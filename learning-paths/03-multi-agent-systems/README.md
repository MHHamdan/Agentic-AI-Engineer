# 03 · Multi-Agent Systems

> 🟡 Intermediate · ⏱ 23–30 hours (Modules 1-6) · 📍 Start here once you've completed Path 01 (recommended: also Path 02 for Modules 4 and 6) · ✅ Path 03 v1 complete (foundations, supervisor-worker, generator-critic, plan-and-execute, multi-agent RAG, framework bridge, evaluation)

## Who this is for

You've finished Foundations: you can build an agent loop from scratch (Lab 01), design tools that work (Lab 02), and ship a multi-step research agent (Lab 03). You understand that the agent loop is just `while not done: think → act → observe`, and you've felt the failure modes that come from getting the basics wrong.

This path takes you from "I can build *one* agent" to "I can wire *several* agents together to do something none of them could do alone — and I know the difference between when that's a genuine win and when it's expensive theater."

By the end of Path 03 Modules 1-6 you should be able to:

- Decide honestly when a task wants a multi-agent system and when it doesn't.
- Reason about coordination cost — every handoff is an extra LLM call, with latency, tokens, and failure-mode implications.
- Implement the **supervisor-worker pattern** from scratch using only the Lab 01 agent-loop machinery. No frameworks.
- Distinguish **message-passing** from **shared-state** architectures and pick the right one for a given task shape.
- Apply the three handoff-hygiene rules that prevent the most common multi-agent bugs.
- Compose step caps, action-hash dedup, and structured-error envelopes *across agent levels* without surprises.
- Carry citations through worker → supervisor handoffs without trusting the LLM to preserve them.
- Add a **critic** to the supervisor's loop to enable bounded iterative refinement, without falling into sycophancy.
- Diagnose sycophancy with the obvious-bad-draft test and apply the four critic-prompt rules to prevent it.
- Bound refinement with `MAX_REFINEMENT_CYCLES` and handle the cap honestly (surface partial results, not forced approvals).
- Recognize the four debate-specific failure modes (sycophancy, infinite agreement, runaway disagreement, critique drift) and the mitigation each requires.
- Implement the **plan-and-execute pattern**: a planner agent emits a structured `Plan` (typed `PlanStep` list with explicit `depends_on` and `parallel_group` fields); the supervisor resolves dependencies and dispatches steps to a bounded executor pool.
- Apply the five planner-prompt rules (atomic steps, explicit dependencies, honest parallel groups, self-contained descriptions, bounded plans) and explain why each prevents a specific failure mode.
- Wire bounded executor-pool concurrency (`ThreadPoolExecutor(max_workers=3)`) and reason about parallelism as a wall-clock optimization rather than a cost or quality optimization.
- Handle replanning with `MAX_REPLANS = 2` — invoke the planner with failure context, finalize honestly when the cap fires.
- Recognize the four plan-and-execute-specific failure modes (plan brittleness, execution drift, replanning thrash, plan-execution gap) and the mitigation each requires.
- Compose Path 02's retrieval pipeline (Labs 06-08) with the supervisor-worker pattern: wrap retrieval as a single worker the supervisor can call, with structured `{status, chunks}` envelope.
- Apply the four retrieval-decision rules (retrieve when corpus-grounded, skip for stable-knowledge, one retrieval per distinct factual question, pass chunks verbatim) and explain why each prevents a specific failure mode.
- Recognize the four multi-agent-RAG-specific failure modes (citation drift, retrieval skip, retrieval over-call, chunk drift) and the mitigation each requires.
- Preserve citations across the retrieval → supervisor → synthesis handoff without trusting the LLM to track them by hand.
- Decide honestly when multi-agent RAG beats single-agent RAG (when deciding-to-retrieve is non-trivial, when multiple retrievals must be composed, when precision justifies a critic) — and when it doesn't.
- Rebuild from-scratch multi-agent patterns in LangGraph (`StateGraph`, `Command`, `Send`, sub-graphs, checkpointer) and run line-by-line comparisons against the from-scratch baselines — the pedagogical payoff of having both implementations.
- Explain when framework adoption earns its complexity (durable checkpointer, observable execution via streaming, `Send`-based dynamic parallel dispatch, reducer-based parallel-update semantics) and when it doesn't.
- Implement seven trajectory and outcome metrics from scratch — handoff success rate, routing accuracy, plan validity, plan coverage, replan rate, citation preservation, groundedness — and explain what each reveals and what each hides.
- Apply the aggregate-then-slice-then-per-agent discipline carried from Lab 09 to multi-agent trajectories; localize a failing aggregate to a specific failure category and a specific agent.
- Reason about the replay-vs-live evaluation trade-off, the rule-based-vs-LLM-as-judge trade-off, and the per-agent-vs-end-to-end trade-off.
- Recognize that the from-scratch eval harness is the conceptual foundation; production tooling (LangSmith / Phoenix / Galileo / Vertex AI) layers on top.

## Prerequisites

**Complete Path 01 — Foundations first.** This is non-negotiable. Lab 10 is structurally a Lab 02 supervisor whose "tools" are calls to Lab 03–style worker agents. The patterns transfer; the conceptual frame only makes sense if you've internalized them.

Minimum:

- Labs 01, 02, 03 finished and understood.
- The [`tool-design`](../../concepts/tools/tool-design.md) and [`tool-selection`](../../concepts/tools/tool-selection.md) concept pages read.
- All five Foundations quizzes passed at 6+/8.

Lab 05 (LangGraph single-agent) is helpful for Modules 1-4 and **required** for Module 5 — Labs 14/15 assume you've seen `StateGraph`, `MessagesState`, `add_messages`, `Command`, and `interrupt()`. If you haven't built Lab 05, do that first before attempting Module 5.

Path 02 (Agentic RAG) is recommended for Module 4. Modules 1-3 are independent of Path 02; you can do them in any order. Module 4 (multi-agent RAG) explicitly composes Labs 06-08 with the multi-agent patterns from Labs 10-12 — if you haven't built the retrieval pipeline, the Module 4 lab still runs (it builds chunks inline from Lab 06's corpus), but the conceptual framing assumes you understand what dense + BM25 + RRF + cross-encoder rerank is doing inside the retriever.

## How this path is structured

Path 03 v1 opens with Module 1 (foundations and the supervisor-worker pattern); Module 2 extends it with iterative refinement via generator-critic; Module 3 adds plan-and-execute with bounded parallel executor pool; Module 4 composes Path 02's retrieval pipeline with these coordination patterns as multi-agent RAG; Module 5 (framework bridge) rebuilds Labs 10 and 12 in LangGraph and provides line-by-line comparisons against the from-scratch baselines. Future batches add multi-agent evaluation.

```mermaid
flowchart LR
    A[📖 What is a multi-agent system?] --> B[📖 Supervisor-worker pattern]
    B --> C[📖 Handoffs and shared state]
    C --> L10[🧪 Lab 10: Supervisor-worker from scratch]
    L10 --> Q1[🧠 Multi-agent fundamentals quiz]
    Q1 --> D[📖 Agent debate and critics]
    D --> E[📖 Generator-critic pattern]
    E --> L11[🧪 Lab 11: Generator-critic from scratch]
    L11 --> Q2[🧠 Agent debate and critics quiz]
    Q2 --> F[📖 Plan-and-execute]
    F --> G[📖 Planner-executor pattern]
    G --> L12[🧪 Lab 12: Plan-and-execute from scratch]
    L12 --> Q3[🧠 Plan-and-execute quiz]
    Q3 --> H[📖 Multi-agent RAG]
    H --> I[📖 Retriever-as-worker pattern]
    I --> L13[🧪 Lab 13: Multi-agent RAG from scratch]
    L13 --> Q4[🧠 Multi-agent RAG quiz]
    Q4 --> J[📖 LangGraph multi-agent primitives]
    J --> K[📖 When frameworks earn complexity]
    K --> L14[🧪 Lab 14: LangGraph supervisor bridge]
    L14 --> L15[🧪 Lab 15: LangGraph plan-execute bridge]
    L15 --> Q5[🧠 Framework bridge quiz]

    classDef concept fill:#e8f0fe,stroke:#1a73e8
    classDef lab fill:#fef7e0,stroke:#f9ab00
    classDef quiz fill:#e6f4ea,stroke:#137333
    class A,B,C,D,E,F,G,H,I,J,K concept
    class L10,L11,L12,L13,L14,L15 lab
    class Q1,Q2,Q3,Q4,Q5 quiz
```

## Modules

### Module 1 — Foundations + supervisor-worker (batch 15)

**Three concept pages:**

- [📖 What is a multi-agent system?](../../concepts/multi-agent/what-is-a-multi-agent-system.md) — ~10 min. The honest framing: when multi-agent is the wrong call, when it's the right one, why coordination cost is the central tradeoff.
- [📖 The supervisor-worker pattern](../../concepts/multi-agent/supervisor-worker-pattern.md) — ~10 min. The simplest useful multi-agent shape. One coordinator routes work to specialist workers and synthesizes results.
- [📖 Handoffs and shared state](../../concepts/multi-agent/handoffs-and-shared-state.md) — ~9 min. The two architectures; the three handoff-hygiene rules; where things go wrong.

**One lab:**

- [🧪 Lab 10 — Supervisor-worker from scratch](../../labs/10-supervisor-worker-from-scratch/) — ~100-130 min. Build a 3-agent system (supervisor + researcher + writer) using only the Lab 01-03 agent-loop machinery. No new dependencies. The researcher gets Lab 03's `web_search` + `fetch_page`; the writer is prompt-only; the supervisor's "tools" are calls to the workers via the standard tool-dispatch contract from Lab 02.

**One quiz:**

- [🧠 Multi-agent fundamentals](../../quizzes/multi-agent/multi-agent-fundamentals.md) — 8 single-select questions on when to reach for multi-agent, the supervisor-worker mediation property, handoff hygiene, and how the Lab 01-03 patterns compose across levels.

### Module 2 — Iterative refinement: generator-critic (batch 16)

**Two concept pages:**

- [📖 Agent debate and critics](../../concepts/multi-agent/agent-debate-and-critics.md) — ~10 min. The framing of iterative-refinement-via-critique. Self-critique vs. separate-critic vs. multi-agent debate. The four debate-specific failure modes (sycophancy, infinite agreement, runaway disagreement, critique drift).
- [📖 The generator-critic pattern](../../concepts/multi-agent/generator-critic-pattern.md) — ~10 min. The specific pattern Lab 11 implements. The four critic-prompt-design rules. Bounded refinement (`MAX_REFINEMENT_CYCLES = 3`). Sycophancy detection and mitigation.

**One lab:**

- [🧪 Lab 11 — Generator-critic from scratch](../../labs/11-generator-critic-from-scratch/) — ~110-140 min. Extend Lab 10's supervisor with a critic worker. The supervisor's loop adds a bounded refinement cycle: writer → critic → if-approve-finalize-else-refine-with-issues. Includes the sycophancy diagnostic test and the four-failure-mode walkthrough. No new dependencies — pure composition of Lab 10's machinery plus one new worker.

**One quiz:**

- [🧠 Agent debate and critics](../../quizzes/multi-agent/agent-debate-and-critics.md) — 8 single-select questions on when generator-critic earns its place, sycophancy detection, critic prompt design, bounded refinement, and self-critique vs. separate-critic tradeoffs.

### Module 3 — Plan-and-execute (batch 17)

**Two concept pages:**

- [📖 Plan-and-execute](../../concepts/multi-agent/plan-and-execute.md) — ~10 min. The framing: when plan-first beats supervisor-worker and ReAct. Plan-first vs. interleaved planning. The parallelism trade-off (wall-clock optimization, not a cost or quality optimization). The four plan-and-execute-specific failure modes (plan brittleness, execution drift, replanning thrash, plan-execution gap).
- [📖 The planner-executor pattern](../../concepts/multi-agent/planner-executor-pattern.md) — ~10 min. The specific pattern Lab 12 implements. `Plan` and `PlanStep` Pydantic schemas with `depends_on` + `parallel_group` fields. The five planner-prompt design rules. Executor pool concurrency (`ThreadPoolExecutor`, `MAX_PARALLEL_EXECUTORS = 3`). Replanning policy (`MAX_REPLANS = 2`). Four-cap composition with Lab 10/11's caps.

**One lab:**

- [🧪 Lab 12 — Plan-and-execute from scratch](../../labs/12-plan-and-execute-from-scratch/) — ~120-150 min. Build a planner-executor system with bounded parallel execution and bounded replanning. Reuses Lab 10's `web_search` + `fetch_page` at the executor level. New components: `PlanStep` and `Plan` schemas (Lab 02's `StrictModel` pattern), planner agent emitting JSON-validated plans, executor agent running one step at a time, dependency-resolving dispatcher with `concurrent.futures.ThreadPoolExecutor`, replanning hook with failure-context handoff. Includes the four-failure-mode walkthrough and a stretch comparison of plan-and-execute vs. ReAct on the same task.

**One quiz:**

- [🧠 Plan-and-execute](../../quizzes/multi-agent/plan-and-execute.md) — 8 single-select questions on when plan-and-execute beats supervisor-worker / ReAct, plan brittleness, parallel groups honesty, replanning policy, dependencies vs. parallel groups, plan-execution gap, and how the pattern composes with Lab 10's machinery.

### Module 4 — Multi-agent RAG (batch 18)

The integrative module. Composes Path 02's retrieval pipeline (Labs 06-08) with the multi-agent coordination patterns from Labs 10-12.

**Two concept pages:**

- [📖 Multi-agent RAG](../../concepts/multi-agent/multi-agent-rag.md) — ~10 min. The framing: what changes from single-agent RAG (retrieval becomes a coordinated concern). Three architectural patterns (retriever-as-worker, planner-driven research, critic-on-retrieval) with tradeoffs. When multi-agent RAG earns its place over single-agent RAG (deciding-to-retrieve is non-trivial, multiple retrievals must be composed, precision justifies a critic). The four multi-agent-RAG-specific failure modes (citation drift, retrieval skip, retrieval over-call, chunk drift). When self-RAG / CRAG are the right pattern instead.
- [📖 The retriever-as-worker pattern](../../concepts/multi-agent/retriever-as-worker.md) — ~10 min. The specific pattern Lab 13 implements. The retriever-worker contract (structured `{status, chunks: [{id, text, source, score}, ...]}` envelope). The four retrieval-decision rules (retrieve when corpus-grounded, skip for stable-knowledge, one retrieval per distinct factual question, pass chunks verbatim). Citation preservation discipline. Composing with Lab 11's critic on synthesis. Composing with Lab 12's planner for compound queries.

**One lab:**

- [🧪 Lab 13 — Multi-agent RAG from scratch](../../labs/13-multi-agent-rag-from-scratch/) — ~130-160 min. Wrap Lab 06-08's retrieval pipeline as a single worker the supervisor calls. Auto-detects v2 (Lab 07: dense + BM25 + RRF + rerank) vs v3 (Lab 08: + contextual augmentation) based on whether the context cache is available. Includes the retrieve/skip diagnostic, the four-failure-mode walkthrough, an optional Lab 11 critic-on-synthesis stretch, and an optional Lab 12 planner-driven parallel-retrieval stretch.

**One quiz:**

- [🧠 Multi-agent RAG](../../quizzes/multi-agent/multi-agent-rag.md) — 8 single-select questions on when multi-agent RAG beats single-agent RAG, citation preservation across handoffs, the four retrieval-decision rules, the four multi-agent-RAG-specific failure modes, composing with Lab 11's critic, and when CRAG / self-RAG are the right alternative.

### Module 5 — Framework bridge (batch 20)

The framework comparison module. Rebuilds Lab 10 (supervisor-worker) and Lab 12 (plan-and-execute) in LangGraph, providing line-by-line comparisons against the from-scratch baselines. The pedagogical payoff of Path 03's "from-scratch first" approach: with working code on both sides, framework-adoption trade-offs become concrete rather than abstract.

**Two concept pages:**

- [📖 LangGraph multi-agent: the primitives](../../concepts/multi-agent/langgraph-multi-agent.md) — ~15 min. Maps LangGraph's five multi-agent primitives (`StateGraph` + `TypedDict` state, `Command(goto=..., update=..., graph=...)`, `Send(node, state)`, sub-graphs, checkpointer) onto from-scratch concepts. Each primitive carries a "what you gain / what you trade away" comparison. The three multi-agent topologies LangGraph names (supervisor, swarm, hierarchical). What carries over unchanged from from-scratch: prompts, worker contracts, citation discipline.
- [📖 When frameworks earn complexity](../../concepts/multi-agent/when-frameworks-earn-complexity.md) — ~10 min. The boundary discussion. Five things from-scratch pays for; five things the framework pays for; a decision table for when each fits. The upstream `langgraph-supervisor` deprecation as evidence that high-level multi-agent helpers age poorly because the underlying patterns evolve faster than the helpers.

**Two labs:**

- [🧪 Lab 14 — LangGraph supervisor bridge](../../labs/14-langgraph-supervisor-bridge/) — ~120-150 min. Rebuilds Lab 10's supervisor-worker in LangGraph using the manual supervisor-via-tools pattern (the one LangChain currently recommends, NOT the deprecated `create_supervisor()` helper). Adds checkpointer for crash-resume, streaming for observable execution, and demonstrates `Command(goto=..., graph=Command.PARENT)` as the swarm-topology building block. Closes with a line-by-line comparison showing where the framework adds limited but useful structure.
- [🧪 Lab 15 — LangGraph plan-and-execute bridge](../../labs/15-langgraph-plan-execute-bridge/) — ~120-150 min. Rebuilds Lab 12's plan-and-execute in LangGraph using the `Send` primitive. The dispatcher transformation: ~70 lines of manual `ThreadPoolExecutor` + `threading.Lock` becomes ~10 lines of `Send` returns plus a reducer on the `completed` state field. The strong framework value case for multi-agent.

**One quiz:**

- [🧠 Framework bridge](../../quizzes/multi-agent/framework-bridge.md) — 8 single-select questions covering `Command` semantics, `Send` vs `ThreadPoolExecutor`, the `langgraph-supervisor` deprecation reasoning, what the checkpointer adds, supervisor vs swarm trade-offs, reducer-on-parallel-update-fields, when migration isn't worth it, and what the framework comparison actually demonstrates.

### Module 6 — Multi-agent evaluation (batch 22)

The evaluation module. Closes Path 03 v1. Extends Lab 09's RAG-evaluation harness pattern (hand-curated fixtures + rule-based tier + LLM-as-judge tier + category slicing) for multi-agent trajectories. Same discipline, different unit of analysis — a recorded trajectory instead of a single query/answer pair.

**Two concept pages:**

- [📖 Multi-agent evaluation](../../concepts/multi-agent/multi-agent-evaluation.md) — ~13 min. The framing. Trajectory metrics (the path) vs outcome metrics (the answer); why neither alone is sufficient. The replay model (deterministic, cheap, diagnostic, CI-friendly). The trace fixture as the eval contract. Per-agent vs end-to-end evaluation. What this misses (long-running, adversarial, multi-turn, agent-as-judge calibration, production tooling).
- [📖 Trajectory-level metrics](../../concepts/multi-agent/trajectory-level-metrics.md) — ~12 min. The implementation companion. Seven metrics — five trajectory (handoff success rate, routing accuracy, plan validity, plan coverage, replan rate) and two outcome (citation preservation across handoffs, groundedness) — with Python signatures and per-metric "what this reveals / what this hides" lines. The aggregation-and-slicing discipline from Lab 09. The headline metric pattern by system type (IR tasks, automation tasks, refinement tasks).

**One lab:**

- [🧪 Lab 16 — Multi-agent evaluation harness from scratch](../../labs/16-multi-agent-evaluation-from-scratch/) — ~100-130 min. Build the from-scratch evaluation harness for the seven metrics. Consumes `trace_set.jsonl` — 15 hand-curated traces (5 each from Labs 10/11/12, across 5 failure categories). Implements each metric as a standalone function. Demonstrates the aggregate-then-slice-then-per-agent diagnostic discipline. Optional LLM-as-judge variant for plan validity. Closes with the synthesis: what the harness reveals, what it hides, what production tooling (LangSmith / Phoenix / Vertex AI) adds on top.

**One quiz:**

- [🧠 Multi-agent evaluation](../../quizzes/multi-agent/multi-agent-evaluation.md) — 8 single-select questions covering: outcome-only vs trajectory-plus-outcome evaluation, the replay model's trade-offs, semantic handoff drift, plan validity vs plan coverage, hand-curated vs synthetic fixtures, category slicing as discipline, per-agent vs end-to-end usage, and URL canonicalization for citation preservation.

## What's not in this batch (anti-scope)

These are explicitly out of scope for Modules 1-5 — they're scoped for future Path 03 batches or other paths entirely:

- **CrewAI and AutoGen framework counterparts.** Module 5 covers the LangGraph framework bridge; CrewAI and AutoGen are different frameworks with different trade-offs. A different batch may cover them; not in scope here.
- **`langgraph-supervisor` package usage.** Per [the upstream deprecation note](https://github.com/langchain-ai/langgraph-supervisor-py), new code should use the manual supervisor-via-tools pattern (Lab 14 demonstrates). The `create_supervisor()` helper is not part of the verified surface in this path.
- **LangGraph Cloud / Platform / Studio.** Out of scope. Production deployment is Path 06 territory.
- **Distributed `Send` dispatch across machines.** `Send` (Lab 15) runs in-process. Cross-machine parallelism would require LangGraph Cloud or a custom worker pool.
- **Swarm and hierarchical topologies built out as full labs.** Lab 14 introduces the building blocks (`Command(goto=..., graph=Command.PARENT)` and sub-graph composition); building full implementations is left as extension exercises.
- **Swarm, tree-of-thoughts, MCTS-style plan search.** These are different multi-agent patterns or different search strategies. Future Path 03 batches may cover swarm; tree search over plans is out of scope for the educational track.
- **Self-RAG / CRAG / GraphRAG.** These are different multi-agent RAG patterns with their own design tradeoffs (training-time intervention for Self-RAG; retrieval-evaluator-with-fallback for CRAG; graph-structured retrieval for GraphRAG). The framing page explains when each is the right call; the labs don't implement them.
- **New retrieval techniques.** Lab 13 *composes* the retrieval from Labs 06-08; it doesn't invent new retrieval. Distributed retrieval, vector DB integrations (Qdrant, Pinecone, Weaviate), and federated multi-corpus search are out of scope.
- **Tool-protocol coverage.** MCP and A2A are [Path 04](../04-tool-protocols-mcp-a2a/) territory. They're how agents (and their tools) interoperate across processes / vendors; not the same problem as in-process multi-agent coordination.
- **Distributed execution / persistent plan state.** Lab 12 uses thread-based concurrency for IO-bound LLM calls. Distributed execution across processes / machines and durable plan state across restarts are out of scope.
- **Production observability + evaluation of multi-agent systems.** Module 6 (this batch) brings trajectory-level metrics into Path 03 as a from-scratch harness. Production tooling (LangSmith, Phoenix, Galileo, Vertex AI's evaluation service) is Path 06 territory.

## What comes next

Path 03 v1 closes with this batch. Modules 1-6 cover foundations, the four multi-agent patterns (supervisor-worker, generator-critic, plan-and-execute, multi-agent RAG), the framework bridge, and evaluation. The path is structurally complete.

The planned follow-ups:

- **Solutions for Labs 14, 15, and 16.** Reference implementations in the same pattern as the Labs 01-13 solutions (batches 14 and 21).
- **Path 06 — Evaluation & Observability.** Production-grade evaluation infrastructure. LangSmith depth, OpenTelemetry-based trace ingestion, drift detection, agent-as-judge calibration against human ground truth, online evaluation. Lab 16's from-scratch harness is the conceptual foundation; Path 06 layers tooling on top.
- **Path 03 v2 (possible).** Extensions identified during v1: multi-turn (threaded) evaluation, Lab 13 (multi-agent RAG) framework-bridge variant, Lab 11 (critic) framework-bridge variant, adversarial / red-team evaluation patterns.

Each future batch follows the same shape as v1: concept pages first, lab from-scratch, quiz; framework comparisons come after the from-scratch version is solid.

## References

The papers and projects that shaped how this path is taught:

- **Wang et al. 2023** — "A Survey on Large Language Model based Autonomous Agents" (arXiv:2308.11432). The taxonomy of agent architectures; useful framing of where multi-agent fits.
- **Wu et al. 2023** — "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" (arXiv:2308.08155). The architecture paper, not the framework. Read for the conversation-driven design philosophy.
- **Hong et al. 2023** — "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework" (arXiv:2308.00352). One of the cleaner examples of role-specialized agents producing useful artifacts.
- **Qian et al. 2023** — "Communicative Agents for Software Development" / ChatDev (arXiv:2307.07924). A multi-agent system that produces working software; useful concrete example of when role specialization pays off.
- **Park et al. 2023** — "Generative Agents: Interactive Simulacra of Human Behavior" (arXiv:2304.03442). The famous Smallville paper; emphasizes how much of "agentic" behavior is really prompt design plus memory plus tools.
- **Anthropic 2024** — ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents). Engineering-grounded essay on agent design; the most-quoted piece of practical advice for production multi-agent work. The "evaluator-optimizer" section describes the generator-critic pattern Lab 11 implements.
- **Madaan et al. 2023** — ["Self-Refine: Iterative Refinement with Self-Feedback"](https://arxiv.org/abs/2303.17651). The canonical paper on iterative-refinement-via-critique. Reports gains across diverse tasks; the empirical baseline for generator-critic claims.
- **Sharma et al. 2023** — ["Towards Understanding Sycophancy in Language Models"](https://arxiv.org/abs/2310.13548). The canonical sycophancy paper. Required reading for anyone building critics.
- **Saunders et al. 2022** — ["Self-critiquing models for assisting human evaluators"](https://arxiv.org/abs/2206.05802). Foundational work on critique-quality; the critic-as-eval-assistant framing.
- **Wang et al. 2023 (Plan-and-Solve)** — ["Plan-and-Solve Prompting"](https://arxiv.org/abs/2305.04091). The prompting-level baseline for plan-then-execute; useful for understanding the pattern's pedigree before it generalized to multi-agent.
- **Yao et al. 2023 (ReAct)** — ["ReAct: Synergizing Reasoning and Acting"](https://arxiv.org/abs/2210.03629). The interleaved-planning alternative to plan-first; required reading for understanding when plan-and-execute is the wrong call.
- **Xu et al. 2024 (AgentBench)** — ["AgentBench: Evaluating LLMs as Agents"](https://arxiv.org/abs/2308.03688). Empirical benchmarks across agentic patterns; useful for understanding where plan-and-execute outperforms ReAct and vice versa.
- **Lewis et al. 2020 (RAG)** — ["Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"](https://arxiv.org/abs/2005.11401). The original RAG paper. Useful as the baseline single-agent pattern Module 4 extends.
- **Asai et al. 2023 (Self-RAG)** — ["Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection"](https://arxiv.org/abs/2310.11511). Training-time approach to retrieval-aware models; conceptually adjacent to multi-agent RAG but a different design problem.
- **Yan et al. 2024 (CRAG)** — ["Corrective Retrieval Augmented Generation"](https://arxiv.org/abs/2401.15884). Retrieval evaluator + fallback design; the pattern multi-agent RAG with critic-on-retrieval approximates.
- **Zheng et al. 2023** — ["Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"](https://arxiv.org/abs/2306.05685), NeurIPS. The canonical paper on LLM-as-judge biases (position, verbosity, self-enhancement); required reading before deploying LLM-as-judge for trajectory or outcome scoring (Module 6).
- **El Filali & Bedar 2026** — ["Towards More Standardized AI Evaluation: From Models to Agents"](https://arxiv.org/abs/2602.18029). Argues the model-to-agent evaluation shift: from "how good is the model" to "can we trust the system under change." Frames Module 6's why.
- **McKinsey QuantumBlack 2026** — ["Evaluations for the Agentic World"](https://medium.com/quantumblack/evaluations-for-the-agentic-world-c3c150f0dd5a). Industry framing of multi-agent metric vocabulary (handoffs-per-task, duplicate-work-rate, deadlock detection); useful complement to Module 6's from-scratch implementations.
- **LangChain `agentevals`** — [github.com/langchain-ai/agentevals](https://github.com/langchain-ai/agentevals). Production-reference trajectory evaluators; the message-list trace format LangGraph produces. Path 06 will cover the integration; Module 6 is the conceptual prerequisite.

These are starting points, not a reading list. The papers are dense and the field moves fast — verify any specific claim against [`tools/frameworks/snapshot-v1.0.md`](../../tools/frameworks/snapshot-v1.0.md) if it exists, or the framework's own docs if it doesn't.
