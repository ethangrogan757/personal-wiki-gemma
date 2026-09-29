---
type: project
description: "This project trains a Deep Q-Network (DQN) agent to play Ms. Pac-Man using a convolutional network."
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
# Pac-Man DQN

<!-- wiki:begin src-pacman-dqn -->
This project trains a convolutional Deep Q-Network (DQN) agent to play Ms. Pac-Man using a provided notebook. The agent learns from a replay buffer, a target network, and a Huber loss target. The training resulted in a mean evaluation score improvement from 492.0 to 692.0, though the gain was not uniform across seeds.

## Key details

- The DQN builds a convolutional network that watches four stacked 84×84 grayscale game screens to infer motion.
- The agent uses 9 discrete joystick moves as actions, and the network outputs an estimated future-reward value per move.
- Three hyperparameters were chosen: Exploration set to `0.20`, Episodes set to `100`, and Learning rate set to `0.0001`.
- The training completed 100 episodes with 59,925 total decisions and 14,732 learning updates in 610.3 s.
- A limitation observed was that the mean training loss increased through training rather than decreasing, and improvement was inconsistent across evaluation seeds.

## Topics in this project

- [[Deep Q-Network]]: The agent uses a convolutional DQN that processes four stacked game screens to infer motion and select the best joystick move.
- [[Experience Replay]]: The agent learns from a replay buffer, which stores past experiences to stabilize learning.
- [[Learning Rate]]: The learning rate was set to 0.0001, matching the reference Adam learning rate for the classroom-scale setup.
- [[Model Evaluation]]: The agent's performance is measured by the raw, unclipped game score across five fixed evaluation seeds.

## Sources

- [[Pac-Man DQN README#Overview and how to run]] (lines 12–17)
- [[Pac-Man DQN README#My three hyperparameters]] (lines 32–40)
- [[Pac-Man DQN README#What the agent observes, does, and is rewarded for]] (lines 58–67)

## Related notes

- [[Deep Q-Network]]: This project utilizes a Deep Q-Network (DQN) architecture for training.
- [[Experience Replay]]: The DQN agent learns from a replay buffer.
- [[Learning Rate]]: The learning rate was set to `0.0001` and was tuned for stability.
<!-- wiki:end src-pacman-dqn -->
