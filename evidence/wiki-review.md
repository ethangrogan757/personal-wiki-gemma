# Wiki review log

Generated notes were checked against the unchanged originals in `vault/raw/`. Corrections go in the wiki notes, never in the sources.

## Review of ingest run 2 (2026-09-29, `--replan`)

### Facts spot-checked (all correct)

17 specific claims were compared against the source text. All matched exactly:

| Claim in wiki | Source location |
|---|---|
| Final expanded run 26/48 correct, 31 scorable, 83.9% | Custom LLM README.md:261 |
| First attempt 21/48 correct, 25 scorable, 84.0% | Custom LLM README.md:264–265 |
| Training loss 6.0601 → 0.7415 at step 3,000 | Custom LLM README.md:130, 132 |
| Vocabulary 136 → 399 types | Custom LLM README.md:65, 135 |
| Validation unknown-token rate 0.28% | Custom LLM README.md:67 |
| `extend_corpus` scorable 1/24 → 7/24, correct 0/24 → 3/24 | Custom LLM README.md:93–94, 228–229 |
| Learning rate 0.001 with warmup and cosine decay (Custom LLM) | Custom LLM README.md:41–42 |
| 9 discrete joystick moves | Pac-Man DQN README.md:61 |
| Learning rate 0.0001 (Pac-Man) | Pac-Man DQN README.md:30 |
| Mean evaluation score 492.0 → 692.0 (~41%) | Pac-Man DQN README.md:37–38 |
| Replay buffer, target network, Huber loss | Pac-Man DQN README.md:13 |
| RLS policies `auth.user_id() = user_id` on all four operations | Networking Tracker README.md:100–116 |

### Corrections made

1. **Misleading link: `Model Evaluation.md` → `[[Learning Rate]]`**
   - Problem: in the Custom LLM section, the link said the training used "a learning rate of 0.001, with a warmup and cosine decay schedule". That's true according to the source, but the Learning Rate note only covered Pac-Man's 0.0001, so the link pointed to a note that didn't contain the claim.
   - Fix: added a hand-written "From Custom LLM" section to `Learning Rate.md`, sourced from Custom LLM README.md lines 40–42. It sits outside the generated `wiki:begin/end` markers, so `wiki ingest --force` keeps it (verified with a simulated regeneration). Learning Rate is now a real cross-project note.

2. **Off-topic summary: `Model Evaluation.md`, Custom LLM section**
   - Problem: the summary opened with "This document details the training and evaluation of Ethan's custom LLM experiment…". It described the README instead of explaining evaluation.
   - Fix: rewrote it from the "Evals: how they're scored" section (Custom LLM README.md lines 246–252): 48 fixed cases, 4 single-word choices, scored by highest probability, with out-of-vocabulary cases marked unscorable. This edit is inside a generated block, so `--force` on the Custom LLM source would replace it; a normal re-ingest leaves it alone.

3. **Misstated fact: `Row Level Security.md`, Key details** (found while checking the Obsidian screenshots)
   - Problem: the note said Postgres requires `GRANT` statements "before RLS policies can be enforced". The source says something different: RLS only restricts *which rows* a statement can touch and doesn't grant access by itself, so a `GRANT` is needed before the `authenticated` role can run any statement on the table at all (Networking Tracker README.md line 122). The Sources line also cited only lines 100–116, which don't contain the GRANT fact.
   - Fix: reworded the bullet to match line 122 and widened the source range to lines 100–127. The edit is inside the generated block, so `wiki ingest --force` on the Networking Tracker source would replace it.

### Also changed in code during this review

- `vault/index.md`: shared notes now list every project that uses them ("Shared by [[Pac-Man DQN]], [[Custom LLM]]"). Before, the shared Model Evaluation note showed only the Pac-Man description.
