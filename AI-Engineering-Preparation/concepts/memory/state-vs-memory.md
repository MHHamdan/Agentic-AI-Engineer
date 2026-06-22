# State vs. memory

> Concept note. ~8 min. Runnable companion: [`labs/04-memory-and-context/`](../../labs/04-memory-and-context/). Diagram: [`diagrams/agent-state-and-memory.md`](../../diagrams/agent-state-and-memory.md).

A single model call is stateless: it knows only what is in its [context window](../llm/context-window.md). An agent that runs for many steps, or comes back tomorrow, needs to remember things — but "remember" splits into two kinds that behave differently, and conflating them is a frequent, costly bug.

## Two different things

**State** is the agent's picture of the *current task*: the plan, what is done, what is next, the constraints in force right now. It is specific to this run and it must be cheap to **rewind** — when the user changes their mind mid-task, you want to undo the affected work, not restart.

**Memory** is what carries *across tasks*: durable preferences, learned conventions, facts about the user or project, summaries of past sessions. It must **persist** — a correction to the current task should not erase what you know about the user.

The lab makes the split concrete with a trip planner. The itinerary in progress is state; the per-day budget preference is memory. When the user raises the budget mid-plan, the agent rolls back its state to before the affected day and re-plans only the rest, while the budget — memory — survives the rollback untouched.

## Why the distinction matters

Put a durable preference into rewindable state and a rollback silently deletes it. Put task progress into long-lived memory and a later correction corrupts it, because the stale progress now bleeds into the next run. The two need different storage and different lifetimes:

- **State** is short-lived, checkpointed, and rewindable — snapshot it before each step so a correction is cheap.
- **Memory** is long-lived, append-or-update, and survives task boundaries — written deliberately, not as a side effect of the current conversation.

A useful slogan: **react fast with state, learn slowly with memory.** The current task should turn on a dime; durable knowledge should change only when you mean it to.

## What to remember

- State is the rewindable current task; memory is the durable carry-across — they have different lifetimes and storage.
- Checkpoint state so a mid-task correction re-runs only the affected steps instead of restarting.
- Keep durable preferences in memory so corrections to state do not erase them.

## References

- Packer, C., et al. (2023). *MemGPT: Towards LLMs as Operating Systems.* arXiv:2310.08560.
- LangGraph. *Persistence (checkpointers)* — official documentation. See [`../../references/references.md`](../../references/references.md).
