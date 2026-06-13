# Agent state and memory

Why long-running agents need more than a model call: the difference between state (the current task) and memory (what carries across tasks), the three memory kinds, and the lifecycle that keeps memory from rotting.

> Batch 00: area scaffold. The notes below are planned; they land in later batches.

## Planned notes

- State vs. memory.
- Short-term, long-term, and external memory.
- The memory lifecycle: create, update, summarize, delete.
- Checkpointing and rollback.
- Consistency under change: react fast with state, learn slowly with memory.
- Memory failure modes.

## Key references

- MemGPT: Towards LLMs as Operating Systems — arXiv:2310.08560.
- Mem0: production-ready long-term memory — arXiv:2504.19413.
- LangGraph persistence (official docs).

See the full list in [`../../references/references.md`](../../references/references.md). All explanations are original; sources are cited, not reproduced ([`STYLE.md`](../../STYLE.md)).
