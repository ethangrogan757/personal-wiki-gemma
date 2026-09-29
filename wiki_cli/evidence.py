"""Save each run as a Markdown evidence card so results can be inspected without rerunning the model."""
import re
from datetime import datetime

from . import config


def _card_path(kind, text):
    slug = "-".join(re.findall(r"[a-z0-9]+", text.lower())[:8]) or kind
    folder = config.EVIDENCE_DIR / kind
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{datetime.now():%Y-%m-%d_%H%M%S}_{slug}.md"
    n = 2
    while path.exists():
        path = path.with_name(f"{path.stem}-{n}.md")
        n += 1
    return path


def save_ask_card(result, label=None):
    r = result.reply
    lines = [f"# Ask evidence card{': ' + label if label else ''}", "",
             f"- **Question:** {result.question}",
             "- **Mode:** ask (standalone; no chat history, no persona)",
             f"- **Execution:** local, `{config.MODEL}` via Ollama at {config.OLLAMA_HOST}",
             f"- **Run at:** {datetime.now():%Y-%m-%d %H:%M:%S}",
             f"- **Response time:** {r.seconds:.1f}s ({r.prompt_tokens} prompt tokens, {r.output_tokens} output tokens)", "",
             "## Answer", "", f"**Status:** `{result.status}`", "", result.answer, "",
             "## Citations", ""]
    if result.cited:
        for n in result.cited:
            if 1 <= n <= len(result.hits):
                p = result.hits[n - 1].passage
                lines.append(f"- [{n}] `{p.source}` lines {p.start_line}–{p.end_line} ({p.section})")
            else:
                lines.append(f"- [{n}] **invalid: no such passage**")
    else:
        lines.append("- (none)")
    if result.retry_note:
        lines += ["", f"**Citation retry:** {result.retry_note}"]
    if result.warnings:
        lines += ["", "**Citation check warnings:**"] + [f"- {w}" for w in result.warnings]
    lines += ["", "## Retrieved passages (exactly as sent to the model)", ""]
    for n, hit in enumerate(result.hits, start=1):
        p = hit.passage
        lines += [f"### [{n}] `{p.source}` lines {p.start_line}–{p.end_line}",
                  f"Section: {p.section} · BM25 score {hit.score:.2f} · matched: {', '.join(hit.matched)}", "",
                  "```text", p.text, "```", ""]
    lines += ["## Assessment", "", "_To fill in: does each claim follow from the cited passage? Is retrieval correct?_", ""]
    path = _card_path("ask", result.question)
    path.write_text("\n".join(lines))
    return path


def save_chat_transcript(session, started):
    """Log a chat session for evidence. This is a record for the reader; the assistant never reads it back."""
    lines = ["# Chat transcript", "",
             "- **Mode:** chat (personal assistant, persona from `prompts/persona.md`, conversation memory)",
             f"- **Execution:** local, `{config.MODEL}` via Ollama at {config.OLLAMA_HOST}",
             f"- **Started:** {started:%Y-%m-%d %H:%M:%S}", ""]
    for i, t in enumerate(session.turns, start=1):
        scope = ", ".join(t.projects) or "all projects"
        lookup = (f"looked up notes ({t.decided_by}) in {scope}, search: `{t.query}`" if t.looked_up
                  else f"no notes lookup ({t.decided_by})")
        lines += [f"## Turn {i}", "", f"**You:** {t.user}", "", f"*Harness: {lookup} · {t.seconds:.1f}s*", "",
                  f"**Scout:** {t.reply}", ""]
        if t.hits:
            lines.append("Passages given to the model this turn:")
            for n, h in enumerate(t.hits, start=1):
                p = h.passage
                mark = " **(cited)**" if n in t.cited else ""
                lines.append(f"- [{n}] `{p.source}` lines {p.start_line}–{p.end_line} ({p.section}){mark}")
            lines.append("")
        for w in t.warnings:
            lines.append(f"**Citation check warning:** {w}\n")
    path = _card_path("chat", "transcript")
    path.write_text("\n".join(lines))
    return path


def save_search_card(query, hits):
    lines = ["# Search evidence card", "",
             f"- **Query:** {query}",
             "- **Mode:** search (BM25 keyword search over vault/raw; no model involved, no answer generated)",
             f"- **Run at:** {datetime.now():%Y-%m-%d %H:%M:%S}",
             f"- **Passages returned:** {len(hits)}", ""]
    for n, hit in enumerate(hits, start=1):
        p = hit.passage
        lines += [f"## [{n}] `{p.source}` lines {p.start_line}–{p.end_line}",
                  f"Section: {p.section} · BM25 score {hit.score:.2f} · matched: {', '.join(hit.matched)}", "",
                  "```text", p.text, "```", ""]
    path = _card_path("search", query)
    path.write_text("\n".join(lines))
    return path
