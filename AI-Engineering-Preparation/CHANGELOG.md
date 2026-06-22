# Changelog

All notable changes to the AI Engineering Preparation track are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this track is versioned by batch.

## [Unreleased]

### Added
- **📦 Batch 03 — Retrieval.** Delivers the retrieval half of Path 03. Six concept notes: three under `concepts/rag/` (RAG end-to-end; chunking and retrieval; reranking and citation) and three under `concepts/vector-db/` (similarity and approximate nearest neighbors; HNSW; IVF and quantization). One runnable, offline, deterministic lab — `labs/03-rag-and-ann/` — building a minimal RAG pipeline (`rag.py`: TF-IDF retrieval, grounded answer, citation, abstention) and an exact-vs-IVF nearest-neighbor tradeoff study (`ann.py`: recall vs. vectors scanned), each with a `--self-test`, plus scaffold and solution notebooks. One math page (`math-foundations/03-nearest-neighbor-search.md`) on the k-NN problem, exact cost, recall@k, and the IVF tradeoff. One diagram (`diagrams/rag-pipeline.md`). Navigation, glossary, and counts updated; the `rag` and `vector-db` areas now link the delivered notes and lab. Memory and context engineering complete Path 03 next.

- **📦 Batch 02 — ML & RL fundamentals.** Fills in Path 02. Six concept notes (the ML lifecycle; feature stores and training/serving skew; monitoring, drift, and retraining; RL primitives; policy gradients and PPO; RLHF from preferences to policy), a runnable RL lab (`labs/02-rl-from-scratch/`: Q-learning and a Bradley-Terry reward model), a math page (`math-foundations/02-rl-objectives.md`), and a diagram (`diagrams/ml-lifecycle.md`).

- **📦 Batch 01 — LLM foundations.** Fills in Path 01. Six concept notes under `concepts/llm/`, a runnable tokenization/embeddings lab (`labs/01-tokenization-and-embeddings/`), a math page (`math-foundations/01-embeddings-and-similarity.md`), and a diagram (`diagrams/text-to-prediction.md`).

- **🧱 Batch 00 — scaffold.** Establishes the AI Engineering Preparation sub-folder inside the parent repository: landing README, changelog, dual-license note, and style rules; five learning-path index pages, twelve concept-area index pages, five project specs, and stubs for labs, math-foundations, diagrams, the glossary, and a seeded canonical references list.

  Curriculum scope was mapped from a set of external topic guides used only for sequencing; all wording is original and technical claims point to canonical sources (see `references/references.md`).
