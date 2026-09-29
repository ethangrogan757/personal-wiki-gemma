---
type: concept
description: "The training process used the nanoGPT architecture with specific hyperparameters like learning rate and training steps to build the model."
sources:
  - "[[Custom LLM README]]"
source_ids:
  - src-custom-llm
original_paths:
  - "Assignment 3/custom-llm/README.md"
generated_by: gemma4:e2b-it-qat (local, Ollama)
reviewed: false
updated: 2026-09-29
---
# Model Training

<!-- wiki:begin src-custom-llm -->
## From Custom LLM

Part of the [[Custom LLM]] project.

This project involved training Karpathy's nanoGPT from scratch on a small word-token corpus, followed by two corpus extension attempts. The final expanded run used 3,000 training steps on an 8-category corpus to achieve measurable improvements in evaluation scores.

### Key details

- The architecture used was nanoGPT with settings: `n_embd=64`, `n_head=4`, `n_layer=2`, `block_size=48`, `batch_size=32`, `seed 42`, and CPU-only runtime.
- Training was conducted using `LEARNING_RATE = 0.001` with a warmup and cosine decay schedule.
- The training process involved running `TRAINING_STEPS = 10` for pipeline confirmation and `TRAINING_STEPS = 3000` for real experiments.
- The final expanded run used 3,000 steps, resulting in a vocabulary size of 399 types.
- The final model's validation loss at step 3,000 was 0.9742, which was higher than the training loss of 0.7415, indicating a larger vocabulary needs more steps or repetition to fully close the gap.
- The model's vocabulary size increased from 136 (starter) to 399 (final expanded run).

### Sources

- [[Custom LLM README#What I taught it, and why]] (lines 40–44)
- [[Custom LLM README#The runs themselves]] (lines 99–112)

### Related notes

- [[Corpus Extension]]: The second attempt involved writing material for all 8 extension categories to address a vocabulary-coverage gap.
- [[Learning Rate]]: The training used a learning rate of 0.001, which was the suggested starting point for the notebook.
- [[Model Evaluation]]: The final results show that `extend_corpus` scorable cases rose from 1/24 to 7/24, and correct answers rose from 0/24 to 3/24.
<!-- wiki:end src-custom-llm -->
