# Chat, search and ask mode checks

Model `gemma4:e2b-it-qat`, local Ollama. These are online-machine runs from development (2026-09-29). The required offline rerun is recorded separately.

## Chat: capability questions (no lookup expected)

Transcript: [chat/2026-09-29_113819_transcript.md](chat/2026-09-29_113819_transcript.md), turns 1–2

| Message | Router decision | Result |
|---|---|---|
| "what can we do?" | no notes lookup ✅ | Accurate capabilities: brainstorm, plan, draft/edit, wiki lookups for the 3 named projects. No citations, no refusal ✅ |
| "what can you help me with?" | no notes lookup ✅ | Same capabilities as a list, then asks what to tackle ✅ |

## Chat: draft, then follow-up

Same transcript, turns 3–4

| Message | Router decision | Result |
|---|---|---|
| "Draft a short study plan for reviewing my three class projects…" | lookup in all 3 projects ✅ | 3-week plan labeled as a suggestion, citing one real passage per project [1][2][3] ✅. One misreading: it calls the Networking Tracker's tests "successful and failed test cases", but all 10 tests passed; some test that bad input is *rejected* ⚠️ |
| "make that shorter" | no notes lookup ✅ | Condensed version of the same plan, built from the conversation ✅ |
| "What learning rate did I use for the Pac-Man DQN?" | lookup in Pac-Man DQN only ✅ | "0.0001 [1]" citing Pac-Man DQN README.md:26–30 ✅ |

### Failure found and fixed first

The first run ([chat/01-invented-details/](chat/01-invented-details/)) looked up notes for the study plan, but plain BM25 returned 4 Pac-Man passages and nothing from the other two projects. Gemma filled the gap with **invented details**: "data visualization aspects you implemented" (not in the Networking Tracker README) and "how you fine-tuned" the LLM (the README says it was trained from scratch).

Fixes:
1. The chat router now also names which projects a message is about, and the harness retrieves from each named project (`retrieval.search_sources`). A score-ratio "diversity" rule was tried first and rejected, because the scores didn't separate relevant from irrelevant sources.
2. `persona.md` rule: drafts may only mention project specifics that appear in the passages or conversation, and must otherwise stay generic.

## A chat-only claim isn't evidence in ask

Transcript: [chat/2026-09-29_113858_transcript.md](chat/2026-09-29_113858_transcript.md) · ask card: [ask/2026-09-29_113900_how-much-does-it-cost-per-month-to.md](ask/2026-09-29_113900_how-much-does-it-cost-per-month-to.md)

1. Chat: "Quick note: hosting my Networking Tracker costs $20 a month." → acknowledged, no lookup.
2. Chat: "So how much does hosting my Networking Tracker cost per month?" → looked up notes, then replied "The notes don't specify the exact cost, but you mentioned it is $20 a month." ✅ It keeps the user's claim separate from wiki evidence.
3. Ask (new process, no chat history): same question → **INSUFFICIENT EVIDENCE**, no citations ✅. The chat claim never reached ask mode.

## Search: original passages, no generated answer

See `wiki search` output (no model involved; also works with Ollama unreachable, see Step 5 checks).
