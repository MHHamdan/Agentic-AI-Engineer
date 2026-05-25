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

## Multi-agent RAG (batch 18 — Module 4)

- [📖 Multi-agent RAG](./multi-agent-rag.md) — ~10 min. The integrative framing. What changes from single-agent RAG (Lab 06-08): retrieval becomes a coordinated concern, not a single always-on tool call. Three architectural patterns (retriever-as-worker, planner-driven research, critic-on-retrieval) with tradeoffs. When multi-agent RAG earns its place. The four multi-agent-RAG-specific failure modes (citation drift, retrieval skip, retrieval over-call, chunk drift). When self-RAG / CRAG are the right pattern instead.
- [📖 The retriever-as-worker pattern](./retriever-as-worker.md) — ~10 min. The specific pattern Lab 13 implements. The retriever-worker contract (structured chunks envelope). The four retrieval-decision rules. Citation preservation discipline (the canonical multi-agent-RAG bug). Composing with Lab 11's critic on synthesis. Composing with Lab 12's planner for compound queries.

## Framework bridge (batch 20 — Module 5)

- [📖 LangGraph multi-agent: the primitives](./langgraph-multi-agent.md) — ~15 min. Maps LangGraph's five multi-agent primitives (`StateGraph` + `TypedDict` state, `Command(goto=..., update=..., graph=...)`, `Send(node, state)`, sub-graphs, checkpointer) onto from-scratch concepts from Labs 10-13. Each primitive carries a "what you gain / what you trade away" comparison. The three multi-agent topologies LangGraph names (supervisor, swarm, hierarchical). What carries over unchanged from from-scratch: prompts, worker contracts, citation discipline.
- [📖 When frameworks earn complexity](./when-frameworks-earn-complexity.md) — ~10 min. The boundary discussion. Five things from-scratch pays for; five things the framework pays for; a decision table for when each fits. The upstream `langgraph-supervisor` deprecation as evidence that high-level multi-agent helpers age poorly because the underlying patterns evolve faster than the helpers.

## Multi-agent evaluation (batch 22 — Module 6)

- [📖 Multi-agent evaluation](./multi-agent-evaluation.md) — ~13 min. The framing for evaluating multi-agent systems. Trajectory metrics (the path) vs outcome metrics (the answer); why neither alone is sufficient. The replay model (deterministic, cheap, diagnostic, CI-friendly). The trace fixture as the eval contract. Per-agent vs end-to-end evaluation. What this misses (long-running, adversarial, multi-turn, agent-as-judge calibration, production tooling).
- [📖 Trajectory-level metrics](./trajectory-level-metrics.md) — ~12 min. The implementation companion. Seven metrics — five trajectory (handoff success rate, routing accuracy, plan validity, plan coverage, replan rate) and two outcome (citation preservation across handoffs, groundedness) — with Python signatures and per-metric "what this reveals / what this hides" lines. The aggregation-and-slicing discipline carried from Lab 09. The headline metric pattern by system type.

## Production and evaluation (Path 06)

Production-grade multi-agent observability, evaluation, and orchestration are scoped to Path 06 — Evaluation & Observability. The trajectory-level metrics (handoff-success rate, citation-preservation rate, per-worker latency budgets) extend the Lab 09 eval-harness pattern.

## Related sections

- [`concepts/agents/`](../agents/) — single-agent foundations. Read these first if you haven't.
- [`concepts/tools/`](../tools/) — tool-design principles. They still apply at the worker boundary; in fact they apply *harder* because the supervisor's view of each worker is determined by the worker's tool schema.
- [`concepts/evaluation/`](../evaluation/) — eval discipline. Multi-agent systems need *more* eval than single-agent ones, because there are more places things can fail silently.

## Implementation

- [🧪 Lab 10 — Supervisor-worker from scratch](../../labs/10-supervisor-worker-from-scratch/) — implements the supervisor-worker pattern using only the Path 01 agent-loop machinery. No frameworks.
- [🧪 Lab 11 — Generator-critic from scratch](../../labs/11-generator-critic-from-scratch/) — extends Lab 10's supervisor with a critic worker and a bounded refinement loop.
- [🧪 Lab 12 — Plan-and-execute from scratch](../../labs/12-plan-and-execute-from-scratch/) — planner + bounded parallel executor pool + replanning. The from-scratch concurrency dispatcher.
- [🧪 Lab 13 — Multi-agent RAG from scratch](../../labs/13-multi-agent-rag-from-scratch/) — composes Path 02's retrieval pipeline with Lab 10's supervisor pattern.
- [🧪 Lab 14 — LangGraph supervisor bridge](../../labs/14-langgraph-supervisor-bridge/) — rebuilds Lab 10 in LangGraph. Limited but useful framework value-add.
- [🧪 Lab 15 — LangGraph plan-and-execute bridge](../../labs/15-langgraph-plan-execute-bridge/) — rebuilds Lab 12 in LangGraph using `Send`. Strong framework value-add for dynamic parallel dispatch.
- [🧪 Lab 16 — Multi-agent evaluation harness from scratch](../../labs/16-multi-agent-evaluation-from-scratch/) — implements the seven metrics from the concept pages against a hand-curated `trace_set.jsonl` of 15 traces replayed from Labs 10/11/12. Closes Path 03 v1.
