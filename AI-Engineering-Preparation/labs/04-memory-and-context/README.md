# Lab 04: Memory and context

> 🟢 Foundational · ⏱ ~60–75 min · 📚 Path 03 (Retrieval & memory)

## 🎯 Goal

Build the two disciplines that keep a long-running agent coherent — separating rewindable state from durable memory, and packing a finite context window deliberately — so an agent can take a correction mid-task and stay inside its budget.

By the end you should be able to:

- Separate agent state (the current task) from memory (what carries across tasks).
- Use checkpoint/rollback so a correction re-runs only the affected steps.
- Assemble a context window under a budget by selecting and compressing.
- Explain why a bigger window is not a substitute for selection (context rot).

## 🛠 Modules

| File | What it does |
|---|---|
| `checkpoints.py` | a trip planner with rewindable state, durable memory, and checkpoint/rollback (`Planner`, `run_scenario`, `--self-test`, `--demo`) |
| `context_budget.py` | packs instructions + memory + history into a token budget by relevance/recency, compacting the overflow (`assemble`, `--self-test`, `--demo`) |

## What the numbers say

- Checkpoints: a mid-task budget change rolls back to before the affected day, keeps days 1–2, and recomputes **only days 3–5**; the new budget (memory) survives the rollback.
- Budget: under a 40-word budget, instructions and the two highest-relevance memories are kept, the stale greeting and the low-relevance aside are **dropped and compacted**, total lands at 40/40; a generous budget drops nothing.

## Design choices and tradeoffs

- **State rewinds, memory persists.** Snapshots cover state only; durable preferences live in memory so a rollback does not erase them — "react fast with state, learn slowly with memory."
- **Roll back, do not restart.** Checkpointing the step before each action makes a correction cost only the affected steps.
- **Select then compress.** Instructions are mandatory; everything else competes by priority, and the overflow becomes a short note rather than silently vanishing.

## Common gotchas

- **Conflating state and memory.** Put a durable preference in rewindable state and a rollback erases it; put task progress in memory and corrections corrupt it.
- **Dropping the goal.** Naive truncation removes the oldest messages — often the original instructions; keep instructions mandatory and compress the middle.
- **Trusting a big window.** Models attend unevenly and degrade as context grows (context rot); more tokens is not more signal.

## 🧮 Going deeper

- 📖 [concepts/memory/state-vs-memory.md](../../concepts/memory/state-vs-memory.md) · [memory-lifecycle.md](../../concepts/memory/memory-lifecycle.md)
- 📖 [concepts/context/context-engineering.md](../../concepts/context/context-engineering.md) · [context-rot-and-failure-modes.md](../../concepts/context/context-rot-and-failure-modes.md)

## References

- Packer, C., et al. (2023). *MemGPT.* arXiv:2310.08560.
- Anthropic (2025). *Effective context engineering for AI agents.*
- Hong, K., Troynikov, A., Huber, J. (2025). *Context Rot.* Chroma technical report.
- Liu, N. F., et al. (2023). *Lost in the Middle.* arXiv:2307.03172.
