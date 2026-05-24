# Multi-agent · concept index

> Section index for `concepts/multi-agent/`.
> Multi-agent fundamentals and patterns. Foundations for [Path 03](../../learning-paths/03-multi-agent-systems/).

## Foundations (this batch — v1 opening)

- [📖 What is a multi-agent system?](./what-is-a-multi-agent-system.md) — ~10 min. The honest framing: when multi-agent is the right call, when it's the wrong one, why coordination cost is the central tradeoff.
- [📖 The supervisor-worker pattern](./supervisor-worker-pattern.md) — ~10 min. The simplest useful multi-agent shape. One coordinator agent routes work to specialist workers and synthesizes their results.
- [📖 Handoffs and shared state](./handoffs-and-shared-state.md) — ~9 min. The two architectures (message-passing vs. shared-state), the three handoff-hygiene rules, and where things go wrong.

## Patterns (future batches)

These pages will land in future Path 03 batches, each paired with a lab:

- 📖 *Agent debate and critic patterns* (planned) — A generator + critic loop for iterative refinement. Failure modes specific to debate (sycophancy, infinite agreement, runaway disagreement).
- 📖 *Plan-and-execute* (planned) — A planner agent emits a structured plan; one or more executor agents carry it out. When this beats supervisor-worker and when it doesn't.
- 📖 *Multi-agent RAG* (planned) — Composing Path 02 retrieval with the supervisor-worker pattern.

## Production and evaluation (Path 06)

Production-grade multi-agent observability, evaluation, and orchestration are scoped to Path 06 — Evaluation & Observability. The trajectory-level metrics (handoff-success rate, citation-preservation rate, per-worker latency budgets) extend the Lab 09 eval-harness pattern.

## Related sections

- [`concepts/agents/`](../agents/) — single-agent foundations. Read these first if you haven't.
- [`concepts/tools/`](../tools/) — tool-design principles. They still apply at the worker boundary; in fact they apply *harder* because the supervisor's view of each worker is determined by the worker's tool schema.
- [`concepts/evaluation/`](../evaluation/) — eval discipline. Multi-agent systems need *more* eval than single-agent ones, because there are more places things can fail silently.

## Implementation

- [🧪 Lab 10 — Supervisor-worker from scratch](../../labs/10-supervisor-worker-from-scratch/) — the headline lab that implements the supervisor-worker pattern using only the Path 01 agent-loop machinery. No frameworks.
