"""Split source files into passages that keep their source path, section and line numbers.

Rules:
- A heading (#, ##, ...) always starts a new passage, and each passage remembers
  its heading trail, e.g. "Evidence > Training dashboard".
- Inside a section, paragraphs are packed together up to MAX_CHARS.
- A fenced code block (```) is never split across passages.
- A single paragraph longer than SPLIT_CHARS (usually a long bullet list) is cut
  at line boundaries into pieces of up to MAX_CHARS.
- Line numbers are 1-based and refer to the unchanged file in vault/raw/, so a
  citation can be checked by opening the file at those lines.
"""
import re
from dataclasses import dataclass, asdict

MAX_CHARS = 900     # about 200-250 tokens; five passages fit easily in an 8K context
SPLIT_CHARS = 1500  # paragraphs longer than this get cut at line boundaries
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)")


@dataclass
class Passage:
    id: str          # e.g. "Pac-Man DQN README.md#L24-L31"
    source: str      # path relative to the project root, e.g. "vault/raw/Pac-Man DQN README.md"
    title: str       # the file's first heading, so every passage knows which document it's from
    section: str     # heading trail inside the file
    start_line: int
    end_line: int
    text: str

    def to_dict(self):
        return asdict(self)


def _paragraphs(lines):
    """Yield (heading_trail, start_line, end_line, text) for each paragraph or code block."""
    trail = []            # [(level, title), ...]
    para, start = [], None
    in_fence = False

    def section():
        titles = [t for _, t in trail]
        return " > ".join(titles[1:]) if len(titles) > 1 else (titles[0] if titles else "")

    for n, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        heading = None if in_fence else HEADING.match(line)
        ends_para = heading or (not in_fence and not line.strip())
        if ends_para:
            if para:
                yield section(), start, n - 1, "\n".join(para)
                para, start = [], None
            if heading:
                level = len(heading.group(1))
                trail = [(l, t) for l, t in trail if l < level] + [(level, heading.group(2).strip())]
            continue
        if start is None:
            start = n
        para.append(line)
    if para:
        yield section(), start, len(lines), "\n".join(para)


def _split_long(sec, start, text):
    """Cut an oversized paragraph at line boundaries. Code blocks are left whole."""
    if len(text) <= SPLIT_CHARS or text.lstrip().startswith("```"):
        yield sec, start, start + text.count("\n"), text
        return
    piece, piece_start = [], start
    for n, line in enumerate(text.split("\n"), start=start):
        if piece and len("\n".join(piece + [line])) > MAX_CHARS:
            yield sec, piece_start, n - 1, "\n".join(piece)
            piece, piece_start = [], n
        piece.append(line)
    yield sec, piece_start, piece_start + len(piece) - 1, "\n".join(piece)


def chunk_file(text, source):
    """Return the list of Passages for one file's text."""
    name = source.rsplit("/", 1)[-1]
    first_heading = next((m.group(2) for m in map(HEADING.match, text.splitlines()) if m), None)
    title = first_heading or name.rsplit(".", 1)[0]
    passages = []
    current = None   # [section, start, end, [texts]]

    def close():
        if current:
            sec, s, e, parts = current
            passages.append(Passage(f"{name}#L{s}-L{e}", source, title, sec, s, e, "\n\n".join(parts)))

    pieces = (piece for p in _paragraphs(text.splitlines()) for piece in _split_long(p[0], p[1], p[3]))
    for sec, s, e, para in pieces:
        fits = current and current[0] == sec and len("\n\n".join(current[3])) + len(para) + 2 <= MAX_CHARS
        if fits:
            current[2] = e
            current[3].append(para)
        else:
            close()
            current = [sec, s, e, [para]]
    close()
    return passages
