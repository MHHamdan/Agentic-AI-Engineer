# Project: Stateful travel agent

Build an agent that plans a multi-step trip: it tracks the current task as state, remembers steady preferences as memory, calls external tools for live data, and stays consistent when the user changes their mind.

> Batch 00: specification. The build arrives in a later batch.

## Objectives

- Separate state (the plan in progress) from memory (lasting preferences).
- Checkpoint progress and roll back only the affected steps on a correction.
- Call external tools and let the system of record win conflicts.
- Keep the context budget small as history grows.

## Planned deliverables

- A runnable agent skeleton with state, memory, and tools.
- A workflow diagram with checkpoints.
- A consistency test: a mid-task preference change.

## Concept areas

[`memory`](../../concepts/memory/), [`context`](../../concepts/context/), [`agents`](../../concepts/agents/)

## References

See [`../../references/references.md`](../../references/references.md). Original work; sources cited, not copied ([`../../STYLE.md`](../../STYLE.md)).
