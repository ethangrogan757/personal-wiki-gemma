---
type: concept
description: "The process involved iteratively adding eight distinct categories of text to the original corpus to improve the model's performance on specific evaluation tasks."
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
# Corpus Extension

<!-- wiki:begin src-custom-llm -->
## From Custom LLM

Part of the [[Custom LLM]] project.

The project involved iteratively extending a custom LLM's training corpus by adding eight distinct categories of text to improve performance on specific evaluation tasks. The author conducted two extension attempts, with the second attempt being the official expanded result, which involved writing original material for all eight categories based on a diagnosis of vocabulary coverage gaps.

### Key details

- The second, official expanded attempt involved adding 8 files in `corpus/`, one per extension category: negation, opposites, spatial relations, categories/analogies, reference, grammar, sequence, and everyday knowledge.
- The author diagnosed the failure of the first attempt (which only included negation and opposites) by comparing the required answer vocabulary against the taught material, leading to the creation of material for all 8 categories.
- The final expanded run resulted in `extend_corpus` scorable cases rising from 1/24 to 7/24, and correct answers rising from 0/24 to 3/24.
- The final model used a vocabulary size of 399 types, compared to 136 types in the starter run, and training steps were fixed at 3,000.
- A limitation identified was that four categories still scored 0/24 scorable, suggesting that the dominant limiter was the random split of single-occurrence words between training and validation sets.

### Sources

- [[Custom LLM README#What I taught it, and why]] (lines 53–59)
- [[Custom LLM README#One limitation, explained, and what I tried next]] (lines 215–223)

### Related notes

- [[Custom LLM]]: This note describes the overall experiment which involved training and extending the custom LLM.
- [[Model Training]]: The corpus extension process is part of the overall model training experiment.
- [[Model Evaluation]]: The performance metrics, including `extend_corpus` scores, are central to evaluating the corpus extension.
<!-- wiki:end src-custom-llm -->
