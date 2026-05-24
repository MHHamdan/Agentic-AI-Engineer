# 🔡 Tools · Embedding models

> 🔴 Fast-changing. Pages here carry a verified-as-of date in their header. Embedding models and pricing shift quarterly — treat anything older than ~3 months with caution and run the freshness check.

This folder holds versioned snapshots and notes for the embedding libraries and models used in this repo's RAG labs. Embedding models change behavior, pricing, and SOTA leaderboard position faster than most other tools in the stack.

## Current pages

| Page | What it covers | Verified |
|------|----------------|----------|
| 📌 [snapshot-v1.0.md](./snapshot-v1.0.md) | `sentence-transformers` + `all-MiniLM-L6-v2` (default, no API key) and `text-embedding-3-small` (production-oriented alternative) | 2026-05-24 |

## Where this is used in the curriculum

- 🧪 [Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/) — primary consumer.
- 📖 [Chunking and indexing](../../concepts/rag/chunking-and-indexing.md) — references the 256-wordpiece truncation behavior.
- 🗺 [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/) — Module 1 references this snapshot.

## What's not here (and why)

The snapshot covers the models the curriculum's labs actually use. For a comprehensive comparison of all embedding models, the [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) is the right reference — it's updated continuously by the HF team and contradicts any static survey within months.
