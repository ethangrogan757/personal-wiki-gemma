"""Check the Obsidian vault the way a reader would: links, headings, names, duplicates.

Problems found:
- a [[link]] whose target file doesn't exist, or matches more than one file
- a [[file#Heading]] link whose heading isn't in that file
- a wiki note whose first heading doesn't match its filename
- a note name that is too long or looks machine-made
- two notes whose names differ only by case, spaces or a plural "s"
"""
import re
from collections import defaultdict

from . import config

LINK = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|[^\]]+)?\]\]")
HEADING = re.compile(r"^#{1,6}\s+(.*\S)", re.M)


def check():
    files = sorted(config.VAULT_DIR.rglob("*.md"))
    by_name = defaultdict(list)
    for f in files:
        by_name[f.stem].append(f)
    problems, links = [], 0

    for f in files:
        rel = f.relative_to(config.VAULT_DIR).as_posix()
        text = f.read_text()
        for target, heading in LINK.findall(text):
            links += 1
            matches = by_name.get(target.strip(), [])
            if not matches:
                problems.append(f"{rel}: broken link [[{target}]]")
            elif len(matches) > 1:
                problems.append(f"{rel}: ambiguous link [[{target}]] matches {len(matches)} files")
            elif heading and heading.strip() not in HEADING.findall(matches[0].read_text()):
                problems.append(f"{rel}: [[{target}#{heading}]] heading not found")

    wiki_notes = [f for f in files if config.WIKI_DIR in f.parents]
    keys = defaultdict(list)
    for f in wiki_notes:
        rel = f.relative_to(config.VAULT_DIR).as_posix()
        body = re.sub(r"\A---\n.*?\n---\n", "", f.read_text(), flags=re.S)
        first = HEADING.search(body)
        if not first or first.group(1) != f.stem:
            problems.append(f"{rel}: first heading doesn't match filename")
        if not 1 <= len(f.stem.split()) <= 6 or re.search(r"\d{4,}|[0-9a-f]{8,}|_", f.stem):
            problems.append(f"{rel}: filename isn't a short readable name")
        keys[re.sub(r"[^a-z0-9]", "", f.stem.lower()).rstrip("s")].append(rel)
    problems += [f"possible duplicates: {', '.join(v)}" for v in keys.values() if len(v) > 1]
    return {"files": len(files), "notes": len(wiki_notes), "links": links, "problems": problems}
