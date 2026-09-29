---
type: concept
description: "The learning rate was set to 0.0001, matching the reference Adam learning rate for the classroom-scale setup."
sources:
  - "[[Pac-Man DQN README]]"
source_ids:
  - src-pacman-dqn
original_paths:
  - "pacman-dqn/README.md"
generated_by: gemma4:e2b-it-qat (local, Ollama)
reviewed: false
updated: 2026-09-29
---
# Learning Rate

<!-- wiki:begin src-pacman-dqn -->
## From Pac-Man DQN

Part of the [[Pac-Man DQN]] project.

The learning rate was set to 0.0001, which was chosen because it matched the reference Adam learning rate for the classroom-scale setup. This setting was kept because there was no evidence from the initial sanity run that it needed changing.

### Key details

- Learning rate: 0.0001
- The learning rate was tuned to stay stable with the small (5,000-transition) replay buffer and batch size 32 used in this classroom-scale setup.
- No evidence from the sanity run suggested this value needed changing.
- The notebook's reference Adam learning rate was used.

### Sources

- [[Pac-Man DQN README#My three hyperparameters]] (lines 26–30)

### Related notes

- [[Deep Q-Network]]: The notebook builds a convolutional DQN that watches four stacked 84×84 grayscale game screens.
- [[Model Training]]: The training process involved accumulating ~14,700 learning updates over 100 episodes.
- [[Pac-Man DQN]]: This document describes the training of a DQN agent to play Ms. Pac-Man.
<!-- wiki:end src-pacman-dqn -->

## From Custom LLM

*Added by hand during review, so re-ingesting won't overwrite it.*

Part of the [[Custom LLM]] project. The nanoGPT training used `LEARNING_RATE = 0.001` for every run, which was the notebook's suggested starting point. The notebook applied its own warmup and cosine decay to that rate, so the effective rate changed during training.

### Key details

- Learning rate: `0.001` for all runs, ten times the Pac-Man DQN's `0.0001`.
- The notebook's warmup and cosine decay schedule scaled the rate over the course of training.
- It was kept fixed across runs (with `CORPUS = "classroom"`), so that the corpus additions were what changed between experiments.

### Sources

- [[Custom LLM README#What I taught it, and why]] (lines 40–42)

### Related notes

- [[Model Training]]: the learning rate is one of the training settings for the nanoGPT runs.
