# Changelog

All notable changes to the AI Engineering Preparation track are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this track is versioned by batch.

## [Unreleased]

### Added
- **📦 Batch 02 — ML & RL fundamentals.** Fills in Path 02. Six concept notes: three under `concepts/ml-system-design/` (the ML lifecycle; feature stores and training/serving skew; monitoring, drift, and retraining) and three under `concepts/rl/` (RL primitives; policy gradients and PPO; RLHF from preferences to policy). One runnable, offline, deterministic lab — `labs/02-rl-from-scratch/` — building tabular Q-learning on a gridworld (`qlearning.py`) and a Bradley-Terry reward model from pairwise preferences (`preferences.py`), each with a `--self-test`, plus scaffold and solution notebooks. One math page (`math-foundations/02-rl-objectives.md`) covering return, value, the Bellman/TD update, the policy-gradient objective, and preference-based reward modeling. One diagram (`diagrams/ml-lifecycle.md`). Navigation, glossary, and counts updated; Path 02 and both concept areas now link the delivered notes and lab.

- **📦 Batch 01 — LLM foundations.** Fills in Path 01. Six concept notes under `concepts/llm/`: tokens and embeddings, attention, the context window, decoding and sampling, hallucination and knowledge cutoff, and fine-tuning vs. retrieval. One runnable, offline, deterministic lab — `labs/01-tokenization-and-embeddings/` — building byte-pair encoding (`bpe.py`) and count-based PPMI embeddings (`embeddings.py`) from scratch, each with a `--self-test`, plus a scaffold and solution notebook. One math page (`math-foundations/01-embeddings-and-similarity.md`) covering vectors, dot product, cosine, PPMI, and nearest-neighbor search. One diagram (`diagrams/text-to-prediction.md`). Navigation, glossary, and counts updated.

- **🧱 Batch 00 — scaffold.** Establishes the AI Engineering Preparation sub-folder inside the parent repository: landing README with the learning-path table and repository map, this changelog, the dual-license note, and the writing/style rules. Five learning-path index pages, twelve concept-area index pages, five project specs, and stubs for labs, math-foundations, diagrams, the glossary, and a seeded canonical references list.

  Curriculum scope was mapped from a set of external topic guides used only for sequencing; all wording is original and technical claims point to canonical sources (see `references/references.md`).
