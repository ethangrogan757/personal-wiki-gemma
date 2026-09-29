---
type: concept
description: "The agent learns from a replay buffer, which stores past experiences to stabilize learning."
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
# Experience Replay

<!-- wiki:begin src-pacman-dqn -->
## From Pac-Man DQN

Part of the [[Pac-Man DQN]] project.

This project implements a Deep Q-Network (DQN) that learns by utilizing a replay buffer to store past experiences. The agent observes four stacked game screens, selects a joystick move, and learns from this buffer using a target network and a Huber loss target.

### Key details

- The DQN builds a convolutional network that watches four stacked 84×84 grayscale game screens.
- The agent takes one of nine discrete joystick moves, and the network outputs an estimated future-reward value per move.
- The agent learns from a replay buffer, a target network, and a Huber loss target.
- The replay buffer size used in this setup is 5,000 transitions.
- The training process involved 14,732 learning updates over 100 episodes.

### Sources

- [[Pac-Man DQN README#Overview and how to run]] (lines 12–17)
- [[Pac-Man DQN README#My three hyperparameters]] (lines 26–30)
- [[Pac-Man DQN README#What the agent observes, does, and is rewarded for]] (lines 58–67)

### Related notes

- [[Deep Q-Network]]: This note describes the core algorithm used by the project.
- [[Learning Rate]]: The learning rate was set to 0.0001, which was tuned to stay stable with the small replay buffer and batch size used.
- [[Model Training]]: The training process involved 100 episodes and resulted in a mean evaluation score improvement from 492.0 to 692.0.
<!-- wiki:end src-pacman-dqn -->
