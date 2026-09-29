# Ask mode: iterations and fixes

All runs: `gemma4:e2b-it-qat`, local Ollama, temperature 0.1, top 5 BM25 passages, same four questions from `tests/questions.md`. Earlier results are kept in subfolders of `evidence/ask/`.

| Run | Change | T1 (0.0001) | T2 (492→692) | T3 (RLS) | T4 (hosting cost) |
|---|---|---|---|---|---|
| [01](ask/01-status-first-bug/) | JSON `{status, answer}`, status an enum | answer ✅, cited ✅, **status ❌** | answer ✅, **status ❌** | answer ✅, **status ❌** | refused ✅ |
| [02](ask/02-status-last-bug/) | answer first, status second | answer ✅, cited ✅, **status ❌** | **status ❌** | **status ❌** | refused ✅ |
| [03](ask/03-uncited-answer/) | yes/no field `answer_found_in_passages` | status ✅, **no citation ❌** (caught by checker) | ✅ | ✅ | ✅ |
| current (`evidence/ask/*.md`) | harness retries once when an answer has no citations | ✅ | ✅ | ✅ | ✅ |

## Failure 1: every answer labeled "insufficient evidence" (runs 01–02)

- **Symptom:** correct, cited answers came back with `status: "insufficient_evidence"`.
- **Diagnosis:** the same prompt was sent with three output formats. The answer text was correct in all three. Only the two-choice text field was wrong. A boolean field judged correctly. My best explanation is that the prompt names the label `insufficient_evidence` explicitly, which primes a small model toward it. I didn't prove this.
- **Fix:** replaced the enum with `answer_found_in_passages: true/false`. The harness also now flags a contradiction (claims insufficient evidence but cites passages) as a warning.

## Failure 2: correct answer with no citation (run 03)

- **Symptom:** T1 answered "0.0001" with no `[n]`. The code's citation check flagged it as unsupported. The same question was cited correctly in runs 01, 02 and the current run, so the model's citation habit isn't reliable at this size.
- **Fix:** citations are enforced by the harness. If an answer claims support but cites no valid passage, the harness asks once more with a reminder and records the retry in the evidence card. Tested with a simulated uncited answer: one retry, reminder sent, cited answer kept.

## Still-open observations

- T3 cites passage [4] (testing checklist, L289–291) and [2] (SQL policies, L100–116), but not [1] (L118–120), which states the claim most directly. Both cited passages do support the claims, so the citations are valid, just not the best available.
- T4's refusal is correct, but it doesn't "name what the passages do cover" as `wiki-instructions.md` asks.
- The model sees only the passages, so answers are only as good as retrieval. See `evidence/retrieval/` for the retrieval-only runs.
