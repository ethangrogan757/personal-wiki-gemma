---
type: concept
description: "The model's internal representation of words is stored in 64-number vectors that are updated during training."
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
# Token Embeddings

<!-- wiki:begin src-custom-llm -->
## From Custom LLM

Part of the [[Custom LLM]] project.

The model's internal representation of words is stored in 64-number vectors that are updated during training. These vectors are indexed by token IDs, and their behavior is tracked through parameter updates and changes in next-token probabilities.

### Key details

- Every token is assigned an arbitrary integer ID, and this ID indexes into a lookup table of embeddings, where each token has a 64-number vector.
- Before training, a token's vector starts as small random noise (e.g., the first three numbers for 'customer' were `0.00485, 0.00440, -0.00662`).
- After 3,000 steps, the vector for 'customer' shifted to `-0.01704, -0.00632, -0.01737`, reflecting how the network reads and writes to the representation.
- A single parameter update from this vector showed the first coordinate moving from `0.0048451` to `0.0048351` due to a gradient of `0.0016012` and a learning rate of `1e-05`.
- The shift in next-token probabilities for the prompt 'the customer' went from near-uniform noise to a sharp distribution, with the top guess becoming 'ordered' at 21.2% after training.
- The final expanded run used a vocabulary of 399 types, and the model's internal state is represented by these 64-number vectors.

### Sources

- [[Custom LLM README#How this model actually learns — traced through one real word]] (lines 156–163)

### Related notes

- [[Custom LLM]]: This note details the model's internal representation of words, which is a core component of the Custom LLM experiment.
- [[Model Training]]: The token embeddings are updated during the training process, which is detailed in the Model Training section.
- [[Model Evaluation]]: The final state of the embeddings is assessed through the language evaluation results.
<!-- wiki:end src-custom-llm -->
