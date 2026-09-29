"""The retrieval tool: a keyword index over the original sources, searched with BM25.

It only finds evidence; it never calls the model. `wiki search` shows its results
directly, and `ask`/`chat` pass its results to Gemma.

Only files in vault/raw/ are indexed. Generated wiki notes are summaries for
browsing, not evidence, so they are deliberately left out of the index.
"""
import json
import math
import re
from collections import Counter
from dataclasses import dataclass

from . import config
from .chunker import Passage, chunk_file

INDEX_FILE = config.DATA_DIR / "chunks.json"
SOURCE_TYPES = {".md", ".txt"}

STOPWORDS = set("""
a an and are as at be been but by can could did do does for from had has have how i if in into
is it its me my of on or our so than that the their them then there these they this to was
we were what when where which who why will with would you your about after before get got
""".split())


class IndexMissing(Exception):
    pass


# ---------- building the index ----------

def build_index(raw_dir=config.RAW_DIR):
    """Chunk every source in raw_dir and save the passages to data/chunks.json."""
    passages = []
    for path in sorted(raw_dir.rglob("*")):
        if path.suffix.lower() in SOURCE_TYPES and path.is_file():
            source = path.relative_to(config.PROJECT_ROOT).as_posix()
            passages += chunk_file(path.read_text(encoding="utf-8"), source)
    config.DATA_DIR.mkdir(exist_ok=True)
    INDEX_FILE.write_text(json.dumps([p.to_dict() for p in passages], indent=1, ensure_ascii=False))
    return passages


def load_passages():
    if not INDEX_FILE.exists():
        raise IndexMissing("No search index yet. Run: wiki reindex  (or wiki ingest)")
    return [Passage(**d) for d in json.loads(INDEX_FILE.read_text())]


# ---------- tokenizing ----------

def _stem(word):
    """Very light suffix stripping so 'trained'/'training' and 'contacts'/'contact' match."""
    if word[0].isdigit():
        return word
    for suffix in ("ing", "ed", "s"):
        if word.endswith(suffix) and len(word) > len(suffix) + 3:
            return word[: -len(suffix)]
    return word


def tokenize(text):
    words = re.findall(r"[a-z0-9]+(?:\.[0-9]+)*", text.lower())   # keeps numbers like 0.0001 and 492.0
    return [_stem(w) for w in words if w not in STOPWORDS and len(w) > 1]   # drops the "s" in "user's"


# ---------- BM25 search ----------

@dataclass
class Hit:
    passage: Passage
    score: float
    matched: list   # query terms found in this passage


def search(query, k=5, passages=None):
    """Return the top-k passages for the query, best first. Passages with no matching term are skipped.

    BM25 score = sum over query terms of
        idf(term) * tf * (K1 + 1) / (tf + K1 * (1 - B + B * doc_len / avg_len))
    - idf rewards rare terms ("0.0001" beats "model")
    - tf saturates, so repeating a word 20 times doesn't win
    - long passages are normalized so they don't win just by being long
    """
    K1, B = 1.5, 0.75
    passages = passages if passages is not None else load_passages()
    # Each passage is indexed with its document title and section heading, so a table row
    # like "Learning rate | 0.0001" still matches a question that names "Pac-Man DQN".
    docs = [Counter(tokenize(f"{p.title} {p.section} {p.text}")) for p in passages]
    n = len(docs)
    avg_len = sum(sum(d.values()) for d in docs) / n
    terms = list(dict.fromkeys(tokenize(query)))   # unique, keep order

    df = {t: sum(1 for d in docs if t in d) for t in terms}
    idf = {t: math.log((n - df[t] + 0.5) / (df[t] + 0.5) + 1) for t in terms}

    hits = []
    for passage, doc in zip(passages, docs):
        doc_len = sum(doc.values())
        score, matched = 0.0, []
        for t in terms:
            tf = doc.get(t, 0)
            if tf:
                matched.append(t)
                score += idf[t] * tf * (K1 + 1) / (tf + K1 * (1 - B + B * doc_len / avg_len))
        if matched:
            hits.append(Hit(passage, score, matched))
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:k]


def search_sources(query, sources, k=4):
    """Search only the given source files, splitting k between them, so a question about three
    projects gets evidence from all three. Plain BM25 over everything can return passages from
    one project only, because each project's name words score highly in its own passages.
    With no sources given, this is a normal search. (Scores stay per-source, which is fine for ranking.)"""
    if not sources:
        return search(query, k=k)
    passages = load_passages()
    per_source = max(1, k // len(sources))
    hits = []
    for source in sources:
        hits += search(query, k=per_source, passages=[p for p in passages if p.source == source])
    return hits[:max(k, len(sources))]
