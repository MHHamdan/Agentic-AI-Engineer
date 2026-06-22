# Labs

Hands-on, runnable exercises. Labs are where the concepts become code.

## Available labs

| # | Lab | Path | What you build |
|---|---|---|---|
| 01 | [Tokenization and embeddings](./01-tokenization-and-embeddings/) | 01 — LLM foundations | byte-pair encoding and count-based PPMI embeddings from scratch; cosine similarity |
| 02 | [RL from scratch](./02-rl-from-scratch/) | 02 — ML & RL fundamentals | tabular Q-learning on a gridworld; a Bradley-Terry reward model from preferences (RLHF core) |
| 03 | [RAG and ANN](./03-rag-and-ann/) | 03 — Retrieval & memory | a minimal RAG pipeline (retrieve, ground, cite, abstain); an exact-vs-IVF nearest-neighbor tradeoff study |

## Conventions

- **Runnable and offline-first.** Each lab runs without network access where possible, and ships a deterministic `--self-test`.
- **Standard-library-first.** Extra dependencies are introduced only when a lab needs them, and are stated up front.
- **POSIX-friendly shell.** Create files individually; do not rely on shell-specific brace expansion.
- **Honest stand-ins.** Where a lab simulates a model, judge, or service, it says so and points at what a production version swaps in.
- **House layout.** Each lab is a folder with a `README.md`, a scaffold with `TODO`s, and a `solution/`.

## Planned next labs (by path)

1. Memory & context — a stateful agent with checkpointing.
2. Agents — a tool-using agent loop.
3. Evaluation — a small offline eval harness with a golden set.
