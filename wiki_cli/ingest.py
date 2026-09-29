"""Ingest: turn the unchanged sources in vault/raw/ into linked, readable wiki notes.

Who decides what:
- Gemma decides WHICH notes a source deserves and WHAT they say (as JSON).
- The code decides filenames, folders, links, source references and duplicates,
  so a small model can't produce broken links or machine-style names.

Flow of `wiki ingest`:
 1. Register each source in data/source_catalog.json (id, path, sha256).
 2. Skip sources unchanged since their last ingest (unless --force), so notes you
    reviewed and corrected aren't overwritten.
 3. PLAN: Gemma reads the whole document and proposes 1 project note + 3-4 topic
    notes. Titles are cleaned by code; a title matching an existing note is merged
    into that note. The plan is saved, and re-ingest reuses it (unless --replan),
    so note names never drift.
 4. WRITE: for each planned note Gemma writes a summary, details and related links.
    The code renders Markdown and replaces only this source's block in the note:
        <!-- wiki:begin src-id --> ... <!-- wiki:end src-id -->
    so re-ingesting updates notes in place instead of duplicating them.
 5. Rebuild vault/index.md and the search index, and save a timing log to evidence/.
"""
import hashlib
import json
import re
import shutil
from datetime import datetime, date

from . import config, llm, retrieval
from .chunker import chunk_file

CATALOG_FILE = config.DATA_DIR / "source_catalog.json"
FOLDERS = {"Projects": "project", "Concepts": "concept", "Tools": "tool"}
SYSTEM = "You write accurate wiki notes from source documents. Reply with JSON only."
# Words that mark a title as "a section of one document" rather than a subject
BAD_TITLE_WORDS = {"readme", "overview", "introduction", "assignment", "part", "section", "notes", "setup",
                   "summary", "observations", "metrics", "selection", "strategy", "details", "experiment"}
MAX_TITLE_WORDS = 4
UNSAFE_HEADING_CHARS = set("#|^[]/:%")

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "project_description": {"type": "string"},
        "topics": {"type": "array", "minItems": 3, "maxItems": 4, "items": {"type": "object", "properties": {
            "title": {"type": "string", "maxLength": 30},
            "folder": {"type": "string", "enum": ["Concepts", "Tools"]},
            "description": {"type": "string"}}, "required": ["title", "folder", "description"]}},
    },
    "required": ["project_description", "topics"],
}


def note_schema(link_targets):
    props = {
        "summary": {"type": "string"},
        "details": {"type": "array", "minItems": 2, "maxItems": 6, "items": {"type": "string"}},
    }
    if link_targets:
        props["related"] = {"type": "array", "maxItems": 3, "items": {"type": "object", "properties": {
            "title": {"type": "string", "enum": sorted(link_targets)},
            "why": {"type": "string"}}, "required": ["title", "why"]}}
    return {"type": "object", "properties": props, "required": list(props)}


# ---------- catalog ----------

def load_catalog():
    if CATALOG_FILE.exists():
        return json.loads(CATALOG_FILE.read_text())
    return {"sources": []}


def save_catalog(catalog):
    CATALOG_FILE.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register(catalog, path):
    """Find or add the catalog entry for a file in vault/raw/. Updates its current hash."""
    raw_path = path.relative_to(config.PROJECT_ROOT).as_posix()
    entry = next((s for s in catalog["sources"] if s["raw_path"] == raw_path), None)
    if entry is None:
        slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
        entry = {"id": f"src-{slug}", "raw_path": raw_path, "original_path": raw_path}
        catalog["sources"].append(entry)
    entry["sha256"] = sha256(path)
    return entry


def registry(catalog):
    """All planned notes: title -> {folder, description, sources: [source ids]}. First plan wins on conflicts."""
    notes = {}
    for src in catalog["sources"]:
        plan = src.get("plan")
        if not plan:
            continue
        entries = [(plan["project"]["title"], "Projects", plan["project"]["description"])]
        entries += [(t["title"], t["folder"], t["description"]) for t in plan["topics"]]
        for title, folder, description in entries:
            info = notes.setdefault(title, {"folder": folder, "description": description, "sources": []})
            info["sources"].append(src["id"])
    return notes


# ---------- titles ----------

def clean_title(raw):
    """Return a short, readable note title, or None if the model's title isn't usable."""
    title = re.sub(r"[\\/:*?\"<>|#^\[\]]", " ", raw)
    title = " ".join(title.split()).strip(" .-")
    words = title.split()
    if not words or len(words) > MAX_TITLE_WORDS or any(w.lower() in BAD_TITLE_WORDS for w in words):
        return None
    if re.search(r"\d{4,}|[0-9a-f]{8,}", title.lower()):   # dates, hashes, IDs
        return None
    return " ".join(w[0].upper() + w[1:] for w in words)


def title_key(title):
    """Comparison key so 'Replay Buffers' and 'replay buffer' count as the same note."""
    return re.sub(r"[^a-z0-9]", "", title.lower()).rstrip("s")


# ---------- talking to Gemma ----------

def ask_json(src_rel, text, task, schema, log, step):
    # The source text comes first and is identical for every call about this source,
    # so Ollama can reuse its processed prefix instead of re-reading 6,000 tokens each time.
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"SOURCE DOCUMENT: {src_rel}\n<<<\n{text}\n>>>\n\n{task}"},
    ]
    reply = llm.chat(messages, temperature=0.2, schema=schema, num_ctx=config.INGEST_NUM_CTX)
    log.append({"source": src_rel, "step": step, "seconds": round(reply.seconds, 1),
                "prompt_tokens": reply.prompt_tokens, "output_tokens": reply.output_tokens})
    print(f"    {step}: {reply.seconds:.1f}s")
    return json.loads(reply.text)


def project_title(entry):
    """Project notes are named by code from the source filename, e.g. 'Pac-Man DQN README.md' -> 'Pac-Man DQN'."""
    return config.PROJECT_ROOT.joinpath(entry["raw_path"]).stem.replace(" README", "")


def plan_source(entry, text, existing_titles, log, rejected=()):
    instructions = (config.PROMPTS_DIR / "ingest-plan.md").read_text()
    existing = "\n".join(f"- {t}" for t in sorted(existing_titles)) or "(none yet)"
    task = f"{instructions}\nTHIS PROJECT: {project_title(entry)}\nEXISTING NOTES:\n{existing}"
    if rejected:
        task += f"\nREJECTED TITLES (not subject names, don't use them): {', '.join(rejected)}"
    raw = ask_json(entry["raw_path"], text, task, PLAN_SCHEMA, log, "plan" + (" retry" if rejected else ""))

    by_key = {title_key(t): t for t in existing_titles}
    project = project_title(entry)
    topics, seen, dropped = [], {title_key(project)}, []
    for t in raw["topics"]:
        title = clean_title(t["title"])
        if not title or title_key(project) in title_key(title):
            print(f"    dropped unusable title: {t['title']!r}")
            dropped.append(t["title"])
            continue
        title = by_key.get(title_key(title), title)   # merge into an existing note
        if title_key(title) in seen:
            continue
        seen.add(title_key(title))
        topics.append({"title": title, "folder": t["folder"], "description": t["description"].strip()})
    if len(topics) < 2 and not rejected:
        return plan_source(entry, text, existing_titles, log, rejected=tuple(dropped))
    return {"project": {"title": project, "description": raw["project_description"].strip()}, "topics": topics}


# ---------- rendering notes ----------

def raw_link(entry, section=None):
    stem = config.PROJECT_ROOT.joinpath(entry["raw_path"]).stem
    heading = section.split(" > ")[-1] if section else None
    if heading and not (set(heading) & UNSAFE_HEADING_CHARS):
        return f"[[{stem}#{heading}]]"
    return f"[[{stem}]]" + (f" ({heading})" if heading else "")


def source_refs(entry, passages, note_text):
    """Point the note at the source sections its facts most likely came from (BM25 over this source only)."""
    hits = retrieval.search(note_text, k=6, passages=passages)
    if not hits:
        return [raw_link(entry)]
    keep = sorted([h for h in hits if h.score >= 0.5 * hits[0].score][:3], key=lambda h: h.passage.start_line)
    refs, seen = [], set()
    for h in keep:
        p = h.passage
        if p.section in seen:
            continue
        seen.add(p.section)
        link = f"{raw_link(entry)} (introduction)" if p.section == p.title else raw_link(entry, p.section)
        refs.append(f"{link} (lines {p.start_line}–{p.end_line})")
    return refs


def render_block(title, is_project, project_title, plan, content, refs):
    lines = []
    h = "##" if is_project else "###"
    if not is_project:
        lines += [f"## From {project_title}", "", f"Part of the [[{project_title}]] project.", ""]
    lines += [content["summary"].strip(), "", f"{h} Key details", ""]
    lines += [f"- {d.strip()}" for d in content["details"]]
    if is_project:
        lines += ["", f"{h} Topics in this project", ""]
        lines += [f"- [[{t['title']}]]: {t['description']}" for t in plan["topics"]]
    lines += ["", f"{h} Sources", ""] + [f"- {r}" for r in refs]
    related = [r for r in content.get("related", []) if r["title"] != title]
    if related:
        lines += ["", f"{h} Related notes", ""] + [f"- [[{r['title']}]]: {r['why'].strip()}" for r in related]
    return "\n".join(lines)


def find_note(title):
    return next(iter(config.WIKI_DIR.rglob(f"{title}.md")), None)


def frontmatter(title, info, catalog):
    by_id = {s["id"]: s for s in catalog["sources"]}
    srcs = [by_id[i] for i in info["sources"] if i in by_id]
    lines = ["---", f"type: {FOLDERS[info['folder']]}", f"description: {json.dumps(info['description'])}", "sources:"]
    lines += [f'  - "{raw_link(s)}"' for s in srcs]
    lines += ["source_ids:"] + [f"  - {s['id']}" for s in srcs]
    lines += ["original_paths:"] + [f"  - {json.dumps(s['original_path'])}" for s in srcs]
    lines += [f"generated_by: {config.MODEL} (local, Ollama)", "reviewed: false", f"updated: {date.today()}", "---", ""]
    return "\n".join(lines)


def block_pattern(source_id):
    sid = re.escape(source_id)
    return re.compile(rf"<!-- wiki:begin {sid} -->.*?<!-- wiki:end {sid} -->", re.S)


def body_of(path):
    """A note's text without frontmatter and first heading (those are regenerated)."""
    if not path or not path.exists():
        return ""
    text = re.sub(r"\A---\n.*?\n---\n", "", path.read_text(), flags=re.S)
    return re.sub(r"\A\s*# .*\n", "", text).strip()


def write_block(title, info, source_id, block, catalog):
    path = find_note(title) or config.WIKI_DIR / info["folder"] / f"{title}.md"
    rest = body_of(path)
    wrapped = f"<!-- wiki:begin {source_id} -->\n{block}\n<!-- wiki:end {source_id} -->"
    pattern = block_pattern(source_id)
    rest = pattern.sub(lambda m: wrapped, rest) if pattern.search(rest) else f"{rest}\n\n{wrapped}".strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{frontmatter(title, info, catalog)}# {title}\n\n{rest}\n")
    return path


def remove_block(title, source_id):
    """Used on --replan: take this source's block out of a note it no longer plans."""
    path = find_note(title)
    if not path:
        return
    rest = block_pattern(source_id).sub("", body_of(path)).strip()
    if rest:
        path.write_text(re.sub(r"(# .*\n\n).*", lambda m: m.group(1) + rest + "\n", path.read_text(), count=1, flags=re.S))
    else:
        path.unlink()
        print(f"    removed empty note: {title}")


def write_source_notes(entry, text, catalog, log):
    notes = registry(catalog)
    plan = entry["plan"]
    project = plan["project"]["title"]
    passages = chunk_file(text, entry["raw_path"])
    instructions = (config.PROMPTS_DIR / "ingest-note.md").read_text()
    written = []
    for item, is_project in [(plan["project"], True)] + [(t, False) for t in plan["topics"]]:
        title = item["title"]
        others = set(notes) - {title}
        kind = ("the PROJECT note: summarize the whole project, what was built and what was found"
                if is_project else f"a TOPIC note, covering only what this document says about {title}")
        task = (f"{instructions}\nNOTE TITLE: {title}\nNOTE TYPE: {kind}\nWHAT IT COVERS: {item['description']}\n"
                f"OTHER NOTES YOU MAY LINK TO: {', '.join(sorted(others))}")
        content = ask_json(entry["raw_path"], text, task, note_schema(others), log, f"note '{title}'")
        refs = source_refs(entry, passages, content["summary"] + " " + " ".join(content["details"]))
        block = render_block(title, is_project, project, plan, content, refs)
        written.append(write_block(title, notes[title], entry["id"], block, catalog))
    return written


# ---------- index.md ----------

def write_index(catalog):
    notes = registry(catalog)
    project_of = {s["id"]: s["plan"]["project"]["title"] for s in catalog["sources"] if s.get("plan")}

    def line(title, info):
        text = f"- [[{title}]]: {info['description']}"
        if info["folder"] != "Projects" and len(info["sources"]) > 1:   # a note shared by several projects
            text += " Shared by " + ", ".join(f"[[{project_of[i]}]]" for i in info["sources"]) + "."
        return text

    lines = ["# Index", "",
             "Personal wiki of my coding-class projects. Start with a project, follow its topic links,",
             "and use each note's **Sources** list to open the original README section it came from.", ""]
    for folder, blurb in [("Projects", "What I built"), ("Concepts", "Ideas and techniques"), ("Tools", "Software and services")]:
        items = sorted((t, i) for t, i in notes.items() if i["folder"] == folder)
        if items:
            lines += [f"## {folder}", "", f"*{blurb}*", ""]
            lines += [line(t, i) for t, i in items]
            lines.append("")
    lines += ["## Original sources", "", "*Unchanged copies in `raw/`. These are the evidence the wiki is built from.*", ""]
    for s in catalog["sources"]:
        if s.get("plan"):
            lines.append(f"- {raw_link(s)}: original of [[{s['plan']['project']['title']}]] (from `{s['original_path']}`)")
    config.INDEX_NOTE.write_text("\n".join(lines) + "\n")


# ---------- entry point ----------

def collect_sources(path):
    """Return files to ingest from a folder or single file. Files outside vault/raw/ are copied in unchanged."""
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    files = [f for f in files if f.suffix.lower() in retrieval.SOURCE_TYPES]
    result = []
    for f in files:
        f = f.resolve()
        if config.RAW_DIR.resolve() not in f.parents:
            target = config.RAW_DIR / f.name
            if target.exists() and target.read_bytes() != f.read_bytes():
                raise SystemExit(f"error: vault/raw/{f.name} already exists with different content; rename one of them.")
            if not target.exists():
                shutil.copy2(f, target)
                print(f"copied {f} -> vault/raw/{f.name} (unchanged)")
            f = target
        result.append(f)
    return result


def run(path, force=False, replan=False):
    files = collect_sources(path)
    if not files:
        raise SystemExit(f"error: no .md or .txt sources found in {path}")
    llm.check_ready()
    catalog = load_catalog()
    log, started = [], datetime.now()

    todo = []
    for f in files:
        entry = register(catalog, f)
        unchanged = entry.get("ingested_sha256") == entry["sha256"] and entry.get("plan")
        if unchanged and not (force or replan):
            print(f"unchanged, skipped: {entry['raw_path']}  (use --force to regenerate its notes)")
            continue
        todo.append((entry, f.read_text(encoding="utf-8")))

    # Phase 1: plan every source first, so notes can link to notes from later sources.
    # On --replan, set the old plans aside first so they can't be offered as "existing notes".
    old_plans = {}
    if replan:
        for entry, _ in todo:
            old_plans[entry["id"]] = entry.pop("plan", None)
    for entry, text in todo:
        print(f"planning {entry['raw_path']}")
        if entry.get("plan"):
            print("    reusing saved plan (stable note names)")
            continue
        others = set(registry({"sources": [s for s in catalog["sources"] if s is not entry]}))
        entry["plan"] = plan_source(entry, text, others, log)
        new_titles = [entry["plan"]["project"]["title"]] + [t["title"] for t in entry["plan"]["topics"]]
        old = old_plans.get(entry["id"])
        old_titles = [old["project"]["title"]] + [t["title"] for t in old["topics"]] if old else []
        for gone in set(old_titles) - set(new_titles):
            remove_block(gone, entry["id"])
        print(f"    notes: {', '.join(new_titles)}")
        save_catalog(catalog)

    # Phase 2: write the notes.
    written = []
    for entry, text in todo:
        print(f"writing notes for {entry['raw_path']}")
        written += write_source_notes(entry, text, catalog, log)
        entry["ingested_sha256"] = entry["sha256"]
        entry["ingested_at"] = datetime.now().isoformat(timespec="seconds")
        save_catalog(catalog)

    save_catalog(catalog)
    write_index(catalog)
    passages = retrieval.build_index()
    elapsed = (datetime.now() - started).total_seconds()
    save_log(log, written, len(passages), elapsed, started)
    return written, elapsed


def save_log(log, written, n_passages, elapsed, started):
    out = [f"# Ingest run {started:%Y-%m-%d %H:%M:%S}", "",
           f"- model: `{config.MODEL}` (local, Ollama), context {config.INGEST_NUM_CTX} tokens, temperature 0.2",
           f"- total time: {elapsed:.1f}s, model calls: {len(log)}",
           f"- notes written: {len(written)}, search index: {n_passages} passages", "",
           "| Source | Step | Seconds | Prompt tokens | Output tokens |", "|---|---|---|---|---|"]
    out += [f"| {e['source']} | {e['step']} | {e['seconds']} | {e['prompt_tokens']} | {e['output_tokens']} |" for e in log]
    out += ["", "## Notes written", ""] + [f"- `{p.relative_to(config.PROJECT_ROOT).as_posix()}`" for p in written]
    path = config.EVIDENCE_DIR / "ingest" / f"{started:%Y-%m-%d_%H%M%S}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 2
    while path.exists():   # two runs in the same second must not overwrite each other
        path = path.with_name(f"{started:%Y-%m-%d_%H%M%S}-{n}.md")
        n += 1
    path.write_text("\n".join(out) + "\n")
    print(f"log saved: {path.relative_to(config.PROJECT_ROOT)}")
