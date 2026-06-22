# Agent state and memory

Why long-running agents need more than a model call: the difference between state (the current task) and memory (what carries across tasks), the three memory kinds, and the lifecycle that keeps memory from rotting.

> Batch 04: notes delivered. Runnable companion: [`labs/04-memory-and-context/`](../../labs/04-memory-and-context/).

## Notes

1. [State vs. memory](./state-vs-memory.md) — rewindable task state vs. durable carry-across; react fast with state, learn slowly with memory.
2. [Short-term, long-term, and external memory](./memory-types.md) — the three tiers and the RAM/disk analogy.
3. [The memory lifecycle](./memory-lifecycle.md) — create, read, update, delete; consolidation; consistency under change.

## Key references

- MemGPT — arXiv:2310.08560.
- Mem0 — arXiv:2504.19413.
- LangGraph persistence (checkpointers) — official docs.

See the full list in [`../../references/references.md`](../../references/references.md). All explanations are original; sources are cited, not reproduced ([`STYLE.md`](../../STYLE.md)).
