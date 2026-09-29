---
type: project
description: "This project involves training a custom Large Language Model (LLM) from scratch using a small word-token corpus and extending its knowledge base through targeted corpus additions."
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
# Custom LLM

<!-- wiki:begin src-custom-llm -->
This project involves training Karpathy's nanoGPT from scratch on a small word-token corpus and extending its knowledge base through targeted corpus additions. The author conducted an initial experiment and a subsequent, expanded experiment to diagnose and fix limitations in the model's ability to handle various language extension categories.

## Key details

- The model architecture used was nanoGPT with `n_embd=64`, `n_head=4`, `n_layer=2`, `block_size=48`, `batch_size=32`, and seed 42, running on CPU.
- The second, official expanded result used 8 corpus extension categories, with 8 original text files added to the `corpus/` directory.
- The final expanded model achieved a vocabulary size of 399 types, retaining every training token type.
- The second attempt showed that `extend_corpus` scorable cases rose from 1/24 to 7/24, and correct answers rose from 0/24 to 3/24.
- The model's next-token probabilities shifted from near-uniform noise to a sharp, correct-shaped distribution for prompts like "the customer" after training.
- A key limitation identified was that single-occurrence words in the training split could be lost to the validation set, leading to unscorable cases in certain categories.

## Topics in this project

- [[Model Training]]: The training process used the nanoGPT architecture with specific hyperparameters like learning rate and training steps to build the model.
- [[Corpus Extension]]: The process involved iteratively adding eight distinct categories of text to the original corpus to improve the model's performance on specific evaluation tasks.
- [[Model Evaluation]]: Performance was measured using fixed language suites and scoring based on the model's highest probability assignment for single-word choices.
- [[Token Embeddings]]: The model's internal representation of words is stored in 64-number vectors that are updated during training.

## Sources

- [[Custom LLM README#The runs themselves]] (lines 99–112)
- [[Custom LLM README#How this model actually learns — traced through one real word]] (lines 173–180)
- [[Custom LLM README#One limitation, explained, and what I tried next]] (lines 225–235)

## Related notes

- [[Corpus Extension]]: This note details the process of adding 8 new files to the corpus, which was central to the expanded experiment.
- [[Model Training]]: This note covers the specific training steps, loss curves, and parameter updates for the nanoGPT architecture.
- [[Model Evaluation]]: This note explains how the model's performance was scored using fixed language evaluation cases.
<!-- wiki:end src-custom-llm -->
