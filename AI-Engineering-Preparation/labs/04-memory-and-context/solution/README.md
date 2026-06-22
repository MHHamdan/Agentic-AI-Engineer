# Lab 04 · Reference solution

Complete implementation of [Lab 04](../README.md).

## What this is

- **`checkpoints.py`** — a trip planner with rewindable state, durable memory, and checkpoint/rollback (`Planner`, `run_scenario`).
- **`context_budget.py`** — context-window assembly under a token budget by relevance/recency, with compaction (`assemble`).

## Expected results

- A mid-task budget change rolls back to before day 3, keeps days 1–2, recomputes only days 3–5; memory persists.
- Under a 40-word budget: instructions + top-relevance memory kept; stale/low items dropped and compacted; total 40/40.

## Running

```bash
cd labs/04-memory-and-context
python checkpoints.py --self-test
python checkpoints.py --demo
python context_budget.py --self-test
python context_budget.py --demo
```
