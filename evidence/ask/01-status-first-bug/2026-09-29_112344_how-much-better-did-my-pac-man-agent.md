# Ask evidence card

- **Question:** How much better did my Pac-Man agent get after training?
- **Mode:** ask (standalone; no chat history, no persona)
- **Execution:** local, `gemma4:e2b-it-qat` via Ollama at http://localhost:11434
- **Run at:** 2026-09-29 11:23:44
- **Response time:** 5.5s (1313 prompt tokens, 58 output tokens)

## Answer

**Status:** `insufficient_evidence`

The mean evaluation score rose from 492.0 (untrained) to 692.0 (trained), which is a ~41% improvement [3][4].

## Citations

- [3] `vault/raw/Pac-Man DQN README.md` lines 32–40 (My three hyperparameters)
- [4] `vault/raw/Pac-Man DQN README.md` lines 101–113 (Evidence > Before/after evaluation — all five scores)

## Retrieved passages (exactly as sent to the model)

### [1] `vault/raw/Pac-Man DQN README.md` lines 3–8
Section: Class 3: Training a DQN Agent to Play Ms. Pac-Man · BM25 score 9.14 · matched: pac, man, agent, train

```text
This repository is my submission for the Class 3 assignment: train a Deep Q-Network (DQN) on
`ALE/MsPacman-v5` using the provided notebook, choosing three hyperparameters, and reporting what
the agent actually learned.

- Executed notebook: [pacman_dqn.ipynb](pacman_dqn.ipynb) (run in order, outputs saved, final-run version)
- Evidence: [results/](results/) (copied out of the gitignored `pacman_runs/` folder — see [Where things are saved](#where-things-are-saved))
```

### [2] `vault/raw/Pac-Man DQN README.md` lines 58–67
Section: What the agent observes, does, and is rewarded for · BM25 score 8.87 · matched: pac, man, agent, train

```text
- **Observations:** four consecutive game screens, each converted to 84×84 grayscale and stacked
  together. A single screen shows Pac-Man's position; four in a row let the network infer motion —
  which way the ghosts and Pac-Man are actually moving, not just where they are.
- **Actions:** 9 discrete joystick moves — `NOOP, UP, RIGHT, LEFT, DOWN, UPRIGHT, UPLEFT, DOWNRIGHT, DOWNLEFT`
  (the ALE full action set for Ms. Pac-Man). The network outputs one estimated future-reward value
  per move; the agent takes the highest-valued one (or a random move, with probability = exploration).
- **Reward:** the game's own point score — pellets, power pellets, fruit, and eating frightened ghosts
  all add points, which is exactly what's plotted and reported. During *training only*, rewards are
  clipped to [-1, 1] to keep learning updates numerically stable; every score reported here (baseline,
  trained, all five evaluation games) is the **raw, unclipped** game score.
```

### [3] `vault/raw/Pac-Man DQN README.md` lines 32–40
Section: My three hyperparameters · BM25 score 8.08 · matched: pac, man, agent, train

```text
**Before training, I expected:** a small but real improvement in mean evaluation score, given only
100 episodes (~60k decisions) — nowhere near full DQN-paper scale, but enough for the agent to learn
basic behaviors like avoiding immediate ghost collisions and eating nearby pellets, which are the
kinds of local patterns four stacked frames of Ms. Pac-Man can support.

**What I observed:** mean evaluation score rose from 492.0 (untrained) to 692.0 (trained) — a ~41%
improvement — but the gain was **not uniform across seeds** (4 of 5 seeds improved; one got worse
than baseline). Training loss also *increased* through training rather than decreasing, while the
raw training score plateaued after roughly episode 10. See [Limitation and next experiment](#limitation-and-next-experiment).
```

### [4] `vault/raw/Pac-Man DQN README.md` lines 101–113
Section: Evidence > Before/after evaluation — all five scores · BM25 score 7.52 · matched: pac, man, agent, train

```text
Same 5 fixed seeds, same 5% evaluation exploration, same 3,000-decision cap, before and after
training. The baseline is an **untrained** network (not a random-action agent).

| Seed | Baseline (untrained) score | Trained score |
|---|---|---|
| 101 | 350 | 870 |
| 202 | 500 | 1,140 |
| 303 | 320 | 630 |
| 404 | **800** | **370** |
| 505 | 490 | 450 |
| **Mean** | **492.0** | **692.0** |

Full data: [results/comparison.json](results/comparison.json).
```

### [5] `vault/raw/Pac-Man DQN README.md` lines 157–160
Section: Scope note · BM25 score 7.06 · matched: pac, man, agent, train

```text
This uses the notebook's supplied DQN as-is (no custom architecture). The small replay memory and
fixed evaluation seeds are intentional classroom simplifications, not a benchmark-scale DQN
reproduction — see the [upstream README](https://github.com/pepealonso95/pacman-dqn#how-it-works) for
full environment and algorithm details.
```

## Assessment

_To fill in: does each claim follow from the cited passage? Is retrieval correct?_
