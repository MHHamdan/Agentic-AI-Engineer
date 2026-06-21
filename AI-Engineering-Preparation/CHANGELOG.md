# Changelog

All notable changes to the AI Engineering Preparation track are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this track is versioned by batch.

## [Unreleased]

### Added
- **📦 Batch 01 — LLM foundations.** Fills in Path 01. Six concept notes under `concepts/llm/`: tokens and embeddings, attention, the context window, decoding and sampling, hallucination and knowledge cutoff, and fine-tuning vs. retrieval. One runnable, offline, deterministic lab — `labs/01-tokenization-and-embeddings/` — building byte-pair encoding (`bpe.py`) and count-based PPMI embeddings (`embeddings.py`) from scratch, each with a `--self-test`, plus a scaffold and solution notebook. One math page (`math-foundations/01-embeddings-and-similarity.md`) covering vectors, dot product, cosine, PPMI, and nearest-neighbor search. One diagram (`diagrams/text-to-prediction.md`) tracing text → tokenize → embed → layers → logits → decode. Navigation, glossary, and counts updated; Path 01 and the `concepts/llm` area page now link the delivered notes and lab.

- **🧱 Batch 00 — scaffold.** Establishes the AI Engineering Preparation sub-folder inside the parent repository: landing README with the learning-path table and repository map, this changelog, the dual-license note, and the writing/style rules. Five learning-path index pages (LLM foundations; ML & RL fundamentals; retrieval & memory; agents, patterns & protocols; evaluation & delivery). Twelve concept-area index pages (llm, rag, vector-db, memory, context, agents, patterns, mcp, multi-agent, rl, eval, ml-system-design). Five project specs (chat-assistant, ml-system-design, travel-agent, incident-response-agent, rag-with-evals). Stubs for labs, math-foundations, diagrams, the glossary, and a seeded canonical references list. No content modules yet — those arrive in later batches.

  Curriculum scope was mapped from a set of external topic guides used only for sequencing; all wording is original and technical claims point to canonical sources (see `references/references.md`).
