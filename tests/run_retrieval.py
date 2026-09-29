"""Run the four test questions through retrieval only (no model) and save the results.

    python tests/run_retrieval.py LABEL

Writes evidence/retrieval/<LABEL>.md so retrieval changes can be compared run to run.
Expected passages come from tests/questions.md.
"""
import sys
from datetime import datetime

from wiki_cli import config, retrieval

TESTS = [
    ("What learning rate did I use for the Pac-Man DQN?", ["Pac-Man DQN README.md#L26-"]),
    ("How much better did my Pac-Man agent get after training?", ["Pac-Man DQN README.md#L32-"]),
    ("What stops one user from seeing another user's contacts in my networking tracker?",
     ["Networking Tracker README.md#L118-", "Networking Tracker README.md#L100-"]),
    ("How much does it cost per month to host my Networking Tracker?", []),   # unanswerable
]
K = 5


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "latest"
    out = [f"# Retrieval check: {label}", "",
           f"Run {datetime.now():%Y-%m-%d %H:%M}. BM25 over vault/raw, top {K}, no model involved.", ""]
    for i, (question, expected) in enumerate(TESTS, start=1):
        hits = retrieval.search(question, k=K)
        ids = [h.passage.id for h in hits]
        ranks = [next((r for r, pid in enumerate(ids, 1) if pid.startswith(e)), None) for e in expected]
        if expected:
            verdict = "PASS" if all(ranks) else "FAIL"
            detail = ", ".join(f"{e.rstrip('-')} at rank {r}" if r else f"{e.rstrip('-')} missing" for e, r in zip(expected, ranks))
        else:
            verdict, detail = "n/a (unanswerable)", "no passage is expected to contain the answer"
        out += [f"## Test {i}: {verdict}", "", f"**Question:** {question}", "",
                f"**Query terms:** `{' '.join(retrieval.tokenize(question))}`", "", f"**Expected:** {detail}", "",
                "| Rank | Score | Passage | Section | Matched terms |", "|---|---|---|---|---|"]
        for r, h in enumerate(hits, 1):
            out.append(f"| {r} | {h.score:.2f} | `{h.passage.id}` | {h.passage.section} | {', '.join(h.matched)} |")
        out.append("")
        print(f"Test {i}: {verdict}  ({detail})")
    path = config.EVIDENCE_DIR / "retrieval" / f"{label}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out))
    print(f"saved {path.relative_to(config.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
