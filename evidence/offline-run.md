# Required offline run (2026-09-29, 12:11–12:16 PDT)

- **Folder:** [runs/2026-09-29_121156-offline/](runs/2026-09-29_121156-offline/): full [terminal.log](runs/2026-09-29_121156-offline/terminal.log) plus every evidence card from the run
- **Network:** Wi-Fi turned off before starting. `curl https://www.google.com` failed on screen, and the script's own check logged `network: offline`. Ollama was quit and reopened while offline, so the model loaded from local disk.
- **Command:** `./tests/run_checks.sh`. Each `wiki` command is a fresh process, so the CLI was restarted for every step.
- **Device:** MacBook Air, Apple M1 (4P + 4E cores), 8 GB unified memory, macOS 14.7.6, 11 GB free disk
- **Model/runtime:** `gemma4:e2b-it-qat` (Gemma 4 E2B, instruction-tuned, QAT, Q4_0, 4.3 GB on disk) on Ollama 0.34.4
- **Recording:** screen recording of the whole run (see README for the link)

## Results

| Check | Result | Time |
|---|---|---|
| `wiki --help`, `wiki status` | ✅ help printed; `model ready: yes` | 1 s |
| **Ingest** (Pac-Man source, `--force`, local Gemma) | ✅ 5 note blocks rewritten in place with the saved plan, same names; `wiki check`: 14 notes, 135 links, no problems | 130 s (first call 81.9 s includes loading the model after the offline Ollama restart) |
| **Test 1** learning rate | ✅ "0.0001 [3]", citing Pac-Man DQN README.md:26–30 | 23.8 s (includes reloading the model at 8K context after ingest's 16K) |
| **Test 2** how much better | ✅ "492.0 → 692.0, ~41% [3][4]", citing lines 32–40 and 101–113 | 5.0 s |
| **Test 3** what stops other users | ✅ "Row Level Security… `auth.user_id() = user_id` [4][2]", citing lines 289–291 and 100–116 | 7.1 s |
| **Test 4** hosting cost | ✅ INSUFFICIENT EVIDENCE, no citations | 5.7 s |
| **Search** "row level security" | ✅ 3 original passages with paths and line ranges, no generated answer | 0 s |
| **Chat** "what can we do?" / "what can you help me with?" | ✅ accurate capabilities, no lookup, no refusal | 5.8 s / 8.2 s |
| **Chat** study plan → "make that shorter" | ✅ plan cites one passage per project and is labeled a suggestion; the shorter version uses the conversation with no lookup | 19.6 s / 9.0 s |
| **Chat** factual question | ✅ "0.0001 [1]", Pac-Man DQN only | 12.5 s |
| **Chat claim → ask** | ✅ ask: INSUFFICIENT EVIDENCE, so the chat claim was not used as evidence. ⚠️ See the chat weakness below | 1.5 s |

**Memory with the model loaded:** 1.8 GB model (100% GPU, 8,192-token context) + 153 MB llama-server process. Ingest runs at a 16,384-token context and measured the same 1.8 GB.

## Review of notes rewritten offline

The forced ingest rewrote the five Pac-Man blocks. New specific claims were checked against `Pac-Man DQN README.md` and all appear there: 59,925 decisions, 14,732 learning updates, 610.3 s, 5,000-transition buffer, batch size 32, plateau after roughly episode 10, `ALE/MsPacman-v5`, the 9 joystick moves. Hand corrections in other sources' blocks and the hand-added Learning Rate section were not touched.

Style weakness (not an error): some topic summaries still open by describing the whole project ("This project trains a convolutional DQN…") instead of the topic.

## Weakness found: chat blurred a user claim with evidence

In the chat-claim check, after looking up notes that don't mention cost, Scout replied: "Based on the info I have, hosting your Networking Tracker costs $20 a month." The online run of the same check answered correctly: "The notes don't specify the exact cost, but you mentioned it is $20 a month."

- **What still held:** ask mode, the required check, answered INSUFFICIENT EVIDENCE. The claim never became source evidence.
- **What went wrong:** chat didn't say the $20 came from the user rather than the wiki, which is what `persona.md` asks for. It's non-deterministic (chat runs at temperature 0.7), and a 2B-effective model doesn't follow that rule reliably.
- **Improvement to try:** don't rely on the persona alone. When a lookup finds nothing relevant, the harness could add an explicit line to that turn ("The notes found don't answer this. If you use something the user said earlier, say it came from them."). Or lower chat temperature on turns that looked up notes.
