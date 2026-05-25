# Multi-agent · concept index

> Section index for `concepts/multi-agent/`.
> Multi-agent fundamentals and patterns. Foundations for [Path 03](../../learning-paths/03-multi-agent-systems/).

## Foundations (batch 15 — v1 opening)

- [📖 What is a multi-agent system?](./what-is-a-multi-agent-system.md) — ~10 min. The honest framing: when multi-agent is the right call, when it's the wrong one, why coordination cost is the central tradeoff.
- [📖 The supervisor-worker pattern](./supervisor-worker-pattern.md) — ~10 min. The simplest useful multi-agent shape. One coordinator agent routes work to specialist workers and synthesizes their results.
- [📖 Handoffs and shared state](./handoffs-and-shared-state.md) — ~9 min. The two architectures (message-passing vs. shared-state), the three handoff-hygiene rules, and where things go wrong.

## Iterative refinement (batch 16 — Module 2)

- [📖 Agent debate and critics](./agent-debate-and-critics.md) — ~10 min. The framing of iterative-refinement-via-critique. Self-critique vs. separate-critic vs. multi-agent debate. The four debate-specific failure modes (sycophancy, infinite agreement, runaway disagreement, critique drift).
- [📖 The generator-critic pattern](./generator-critic-pattern.md) — ~10 min. The specific pattern Lab 11 implements. Critic prompt design rules. Bounded refinement. Sycophancy detection and mitigation.

## Plan-and-execute (batch 17 — Module 3)

- [📖 Plan-and-execute](./plan-and-execute.md) — ~10 min. The framing: when plan-first beats supervisor-worker and ReAct. Plan-first vs. interleaved planning. The parallelism trade-off. The four failure modes specific to plan-and-execute (plan brittleness, execution drift, replanning thrash, plan-execution gap).
- [📖 The planner-executor pattern](./planner-executor-pattern.md) — ~10 min. The specific pattern Lab 12 implements. The `Plan` and `PlanStep` schemas. The five planner-prompt design rules. Executor pool concurrency (`MAX_PARALLEL_EXECUTORS = 3`). Replanning policy (`MAX_REPLANS = 2`). Four-cap composition.

## Patterns (future batches)

These pages will land in future Path 03 batches, each paired with a lab:

- 📖 *Multi-agent RAG* (planned) — Composing Path 02 retrieval with the supervisor-worker, generator-critic, and planner-executor patterns.

## Production and evaluation (Path 06)

Production-grade multi-agent observability, evaluation, and orchestration are scoped to Path 06 — Evaluation & Observability. The trajectory-level metrics (handoff-success rate, citation-preservation rate, per-worker latency budgets) extend the Lab 09 eval-harness pattern.

## Related sections

- [`concepts/agents/`](../agents/) — single-agent foundations. Read these first if you haven't.
- [`concepts/tools/`](../tools/) — tool-design principles. They still apply at the worker boundary; in fact they apply *harder* because the supervisor's view of each worker is determined by the worker's tool schema.
- [`concepts/evaluation/`](../evaluation/) — eval discipline. Multi-agent systems need *more* eval than single-agent ones, because there are more places things can fail silently.

## Implementation

- [🧪 Lab 10 — Supervisor-worker from scratch](../../labs/10-supervisor-worker-from-scratch/) — the headline lab that implements the supervisor-worker pattern using only the Path 01 agent-loop machinery. No frameworks.
