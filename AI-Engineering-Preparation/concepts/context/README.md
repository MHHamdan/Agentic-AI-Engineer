# Context engineering

Treating the context window as a working set to be budgeted: what competes for space, how to retrieve only what the current step needs, and how to summarize and drop stale material.

> Batch 04: notes delivered. Runnable companion: [`labs/04-memory-and-context/`](../../labs/04-memory-and-context/) (`context_budget.py`).

## Notes

1. [Context engineering](./context-engineering.md) — designing what the model sees each call; write/select/compress/isolate.
2. [Context strategies](./context-strategies.md) — just-in-time retrieval; compaction vs. summarization; note-taking; sub-agent isolation.
3. [Context rot and failure modes](./context-rot-and-failure-modes.md) — why long contexts degrade, and what to do about it.

## Key references

- Effective context engineering for AI agents — Anthropic (2025).
- Context Rot — Chroma technical report (2025).
- Lost in the Middle — arXiv:2307.03172.

See the full list in [`../../references/references.md`](../../references/references.md). All explanations are original; sources are cited, not reproduced ([`STYLE.md`](../../STYLE.md)).
