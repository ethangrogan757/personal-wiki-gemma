---
type: concept
description: "The agent uses a convolutional DQN that processes four stacked game screens to infer motion and select the best joystick move."
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
# Deep Q-Network

<!-- wiki:begin src-pacman-dqn -->
## From Pac-Man DQN

Part of the [[Pac-Man DQN]] project.

This project trains a convolutional Deep Q-Network (DQN) on the `ALE/MsPacman-v5` environment. The agent uses four stacked game screens as input to infer motion and selects a joystick move based on the estimated future reward.

### Key details

- The DQN is built to watch four stacked 84×84 grayscale game screens.
- The agent selects one of nine discrete joystick moves: `NOOP, UP, RIGHT, LEFT, DOWN, UPRIGHT, UPLEFT, DOWNRIGHT, DOWNLEFT`.
- The network outputs one estimated future-reward value per move, and the agent chooses the highest-valued move (or a random move with probability equal to exploration).
- The training uses a replay buffer, a target network, and a Huber loss target.
- The reward is the game's own point score, which is clipped to [-1, 1] during training to maintain numerical stability.

### Sources

- [[Pac-Man DQN README#What the agent observes, does, and is rewarded for]] (lines 58–67)

### Related notes

- [[Pac-Man DQN]]: This note describes the overall project, which is a DQN implementation for Ms. Pac-Man.
- [[Learning Rate]]: The learning rate was set to 0.0001, which was chosen based on reference values for the Adam optimizer.
- [[Experience Replay]]: The training process utilizes a replay buffer, which is a key component of the DQN architecture.
<!-- wiki:end src-pacman-dqn -->
