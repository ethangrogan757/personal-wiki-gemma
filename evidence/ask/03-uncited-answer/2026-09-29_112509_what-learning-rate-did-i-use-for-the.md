# Ask evidence card

- **Question:** What learning rate did I use for the Pac-Man DQN?
- **Mode:** ask (standalone; no chat history, no persona)
- **Execution:** local, `gemma4:e2b-it-qat` via Ollama at http://localhost:11434
- **Run at:** 2026-09-29 11:25:09
- **Response time:** 10.9s (1435 prompt tokens, 36 output tokens)

## Answer

**Status:** `answered`

The learning rate used for the Pac-Man DQN was 0.0001.

## Citations

- (none)

**Citation check warnings:**
- answered without citing any passage, so the answer is unsupported

## Retrieved passages (exactly as sent to the model)

### [1] `vault/raw/Pac-Man DQN README.md` lines 3–8
Section: Class 3: Training a DQN Agent to Play Ms. Pac-Man · BM25 score 9.65 · matched: learn, pac, man, dqn

```text
This repository is my submission for the Class 3 assignment: train a Deep Q-Network (DQN) on
`ALE/MsPacman-v5` using the provided notebook, choosing three hyperparameters, and reporting what
the agent actually learned.

- Executed notebook: [pacman_dqn.ipynb](pacman_dqn.ipynb) (run in order, outputs saved, final-run version)
- Evidence: [results/](results/) (copied out of the gitignored `pacman_runs/` folder — see [Where things are saved](#where-things-are-saved))
```

### [2] `vault/raw/Pac-Man DQN README.md` lines 12–17
Section: Overview and how to run · BM25 score 9.37 · matched: learn, use, pac, man, dqn

```text
The notebook builds a convolutional DQN that watches four stacked 84×84 grayscale game screens,
picks a joystick move, and learns from a replay buffer, a target network, and a Huber loss target.
No coding is required — you edit three values in Section 1 and choose **Run All**.

- **Google Colab:** open [pacman_dqn.ipynb in Colab](https://colab.research.google.com/github/pepealonso95/pacman-dqn/blob/main/pacman_dqn.ipynb), select a GPU under `Runtime → Change runtime type`, edit Section 1, then `Runtime → Run all`. Packages install automatically.
- **Local Jupyter/VS Code:** use a Python 3.11–3.13 kernel, `pip install -r requirements.txt`, keep [pacman_player.py](pacman_player.py) beside the notebook for the local popup player, edit Section 1, then **Run All**.
```

### [3] `vault/raw/Pac-Man DQN README.md` lines 26–30
Section: My three hyperparameters · BM25 score 9.24 · matched: learn, rate, pac, man, dqn

```text
| Setting | Value | Why I chose it |
|---|---|---|
| **Exploration** | `0.20` | Keeps 20% of post-warm-up training moves random. This is the notebook's own reference value and struck a reasonable balance in a quick 5-episode sanity run I did first — training stayed numerically stable, so I kept it rather than reduce exploration before I had any evidence the agent needed less randomness. |
| **Episodes** | `100` | The notebook's suggested starting point. At the throughput I measured on this machine (~150 decisions/second on Apple Silicon MPS), 100 episodes was ~10 minutes — enough to pass the 25-episode threshold four times over (so periodic GIFs/checkpoints actually get produced) and to accumulate ~14,700 learning updates, versus only 501 in a 5-episode check. |
| **Learning rate** | `0.0001` | The notebook's reference Adam learning rate, tuned to stay stable with the small (5,000-transition) replay buffer and batch size 32 used in this classroom-scale setup. I had no evidence from my sanity run that this needed changing. |
```

### [4] `vault/raw/Pac-Man DQN README.md` lines 134–140
Section: Limitation and next experiment · BM25 score 8.85 · matched: learn, rate, pac, man, dqn

```text
**Next experiment I'd try:** increase **replay capacity** (currently fixed at 5,000 transitions) well
beyond 100 episodes' worth of experience, while keeping exploration, learning rate, and episode count
fixed. A larger buffer would let the agent train on a wider variety of past situations per batch
instead of cycling through recent (and possibly correlated) experience so quickly, which should
reduce the seed-to-seed variance seen above and give the loss more room to decrease as training
progresses. (This single setting isn't one of my three assignment hyperparameters, so I'm proposing
it rather than re-running the experiment.)
```

### [5] `vault/raw/Pac-Man DQN README.md` lines 32–40
Section: My three hyperparameters · BM25 score 7.81 · matched: learn, pac, man, dqn

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

## Assessment

_To fill in: does each claim follow from the cited passage? Is retrieval correct?_
