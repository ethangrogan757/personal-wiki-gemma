---
type: concept
description: "The agent's performance is measured by the raw, unclipped game score across five fixed evaluation seeds."
sources:
  - "[[Pac-Man DQN README]]"
  - "[[Custom LLM README]]"
source_ids:
  - src-pacman-dqn
  - src-custom-llm
original_paths:
  - "pacman-dqn/README.md"
  - "Assignment 3/custom-llm/README.md"
generated_by: gemma4:e2b-it-qat (local, Ollama)
reviewed: false
updated: 2026-09-29
---
# Model Evaluation

<!-- wiki:begin src-custom-llm -->
## From Custom LLM

Part of the [[Custom LLM]] project.

The Custom LLM was evaluated on a fixed suite of 48 language cases. Each case gives the model a prompt and 4 single-word choices, and scores 1 only if the model assigns the highest probability to the correct choice. Cases that use a word outside the model's vocabulary are marked unscorable and count as 0, which the author treats as a coverage gap rather than a wrong answer.

### Key details

- The model architecture used was nanoGPT with settings: `n_embd=64`, `n_head=4`, `n_layer=2`, `block_size=48`, `batch_size=32`, `seed 42`, and CPU-only (Colab), using PyTorch 2.11.0+cpu.
- The final expanded run used 3,000 training steps, resulting in a vocabulary size of 399 types and a validation unknown-token rate of 0.28%.
- The final expanded run achieved 26 correct answers out of 48, with 31 cases being scorable, resulting in an accuracy of 83.9% on scorable cases.
- The first attempt at corpus extension (negation + opposites) scored 21 correct out of 48, with 25 cases scorable, yielding an accuracy of 84.0% on scorable cases.
- The model's vocabulary size increased from 136 (starter) to 399 (final expanded), and the training loss for the final run started at 6.0601 and ended at 0.7415 at step 3,000.
- Scoring is based on the model assigning the highest probability to the correct choice; cases using words outside the model's vocabulary are marked unscorable and count as 0.

### Sources

- [[Custom LLM README#The runs themselves]] (lines 99–112)
- [[Custom LLM README]] (Evals: how they're scored, what I found, and how leakage was checked) (lines 246–254)

### Related notes

- [[Corpus Extension]]: The second attempt involved writing material for all 8 extension categories to address category mismatch and single-occurrence word issues.
- [[Custom LLM]]: This note covers the overall experiment, including the architecture, training steps, and final performance metrics.
- [[Learning Rate]]: The training process utilized a learning rate of 0.001, with a warmup and cosine decay schedule.
<!-- wiki:end src-custom-llm -->

<!-- wiki:begin src-pacman-dqn -->
## From Pac-Man DQN

Part of the [[Pac-Man DQN]] project.

This project trains a convolutional Deep Q-Network (DQN) on Ms. Pac-Man using a notebook, measuring performance by the raw, unclipped game score across five fixed evaluation seeds. The agent achieved a mean evaluation score of 692.0 after 100 episodes, showing a ~41% improvement over the untrained baseline.

### Key details

- The agent observes four stacked 84×84 grayscale game screens to infer motion.
- Actions are chosen from 9 discrete joystick moves, and the network outputs an estimated future-reward value per move.
- Rewards are the game's own point score, which is clipped to [-1, 1] during training but reported as the raw, unclipped score.
- The mean evaluation score rose from 492.0 (untrained) to 692.0 (trained).
- The training loss increased through training rather than decreasing, and the raw training score plateaued after roughly episode 10.

### Sources

- [[Pac-Man DQN README#My three hyperparameters]] (lines 32–40)
- [[Pac-Man DQN README#What the agent observes, does, and is rewarded for]] (lines 58–67)

### Related notes

- [[Deep Q-Network]]: This note covers the DQN architecture used in the project.
- [[Model Training]]: This note details the training process and hyperparameter choices made for the DQN.
- [[Pac-Man DQN]]: This note describes the overall project, which involves training the DQN agent on Ms. Pac-Man.
<!-- wiki:end src-pacman-dqn -->
