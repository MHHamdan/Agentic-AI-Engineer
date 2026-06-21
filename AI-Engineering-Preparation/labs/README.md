# Labs

Hands-on, runnable exercises. Labs are where the concepts become code.

## Available labs

| # | Lab | Path | What you build |
|---|---|---|---|
| 01 | [Tokenization and embeddings](./01-tokenization-and-embeddings/) | 01 — LLM foundations | byte-pair encoding and count-based PPMI embeddings from scratch; cosine similarity |

## Conventions

- **Runnable and offline-first.** Each lab runs without network access where possible, and ships a deterministic `--self-test`.
- **Standard-library-first.** Extra dependencies are introduced only when a lab needs them, and are stated up front.
- **POSIX-friendly shell.** Create files individually; do not rely on shell-specific brace expansion.
- **Honest stand-ins.** Where a lab simulates a model, judge, or service, it says so and points at what a production version swaps in.
- **House layout.** Each lab is a folder with a `README.md`, a scaffold with `TODO`s, and a `solution/`.

## Planned next labs (by path)

1. Retrieval & memory — a minimal RAG pipeline; an ANN index tradeoff study.
2. Agents — a tool-using agent loop.
3. Evaluation — a small offline eval harness with a golden set.
