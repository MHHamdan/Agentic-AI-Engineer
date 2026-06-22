# Changelog

All notable changes to the AI Engineering Preparation track are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this track is versioned by batch.

## [Unreleased]

### Added

- **📦 Batch 04 — Memory & context.** Completes Path 03. Six concept notes: three under `concepts/memory/` (state vs. memory; short-term, long-term, and external memory; the memory lifecycle) and three under `concepts/context/` (context engineering; context strategies — retrieval, compaction, note-taking, isolation; context rot and failure modes). One runnable, offline, deterministic lab — `labs/04-memory-and-context/` — building a checkpointed state-vs-memory agent (`checkpoints.py`: rollback re-runs only affected steps, memory persists) and a context-budget assembler (`context_budget.py`: select by priority, compact the overflow), each with a `--self-test`, plus scaffold and solution notebooks. One diagram (`diagrams/agent-state-and-memory.md`). Navigation, glossary, references, and counts updated; Path 03 is now complete.

- **📦 Batch 03 — Retrieval.** Delivered the retrieval half of Path 03: six concept notes (RAG end-to-end; chunking and retrieval; reranking and citation; similarity and ANN; HNSW; IVF and quantization), a RAG-and-ANN lab (`labs/03-rag-and-ann/`), a math page (`math-foundations/03-nearest-neighbor-search.md`), and a diagram (`diagrams/rag-pipeline.md`).

- **📦 Batch 02 — ML & RL fundamentals.** Filled in Path 02: six concept notes (ML lifecycle; feature stores; monitoring/drift; RL primitives; policy gradients; RLHF), an RL lab (`labs/02-rl-from-scratch/`), a math page (`math-foundations/02-rl-objectives.md`), and a diagram (`diagrams/ml-lifecycle.md`).

- **📦 Batch 01 — LLM foundations.** Filled in Path 01: six concept notes under `concepts/llm/`, a tokenization/embeddings lab (`labs/01-tokenization-and-embeddings/`), a math page (`math-foundations/01-embeddings-and-similarity.md`), and a diagram (`diagrams/text-to-prediction.md`).

- **🧱 Batch 00 — scaffold.** Established the AI Engineering Preparation sub-folder inside the parent repository: landing README, changelog, dual-license note, and style rules; five learning-path index pages, twelve concept-area index pages, five project specs, and stubs for labs, math-foundations, diagrams, the glossary, and a seeded canonical references list.

Curriculum scope was mapped from a set of external topic guides used only for sequencing; all wording is original and technical claims point to canonical sources (see `references/references.md`).
