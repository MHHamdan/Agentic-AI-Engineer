# 03 · Multi-Agent Systems

> 🟡 Intermediate · ⏱ 14–19 hours (Modules 1-3) · 📍 Start here once you've completed Path 01 · 🚧 Path 03 in progress (foundations, supervisor-worker, generator-critic, plan-and-execute)

## Who this is for

You've finished Foundations: you can build an agent loop from scratch (Lab 01), design tools that work (Lab 02), and ship a multi-step research agent (Lab 03). You understand that the agent loop is just `while not done: think → act → observe`, and you've felt the failure modes that come from getting the basics wrong.

This path takes you from "I can build *one* agent" to "I can wire *several* agents together to do something none of them could do alone — and I know the difference between when that's a genuine win and when it's expensive theater."

By the end of Path 03 Modules 1-3 you should be able to:

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

## Prerequisites

**Complete Path 01 — Foundations first.** This is non-negotiable. Lab 10 is structurally a Lab 02 supervisor whose "tools" are calls to Lab 03–style worker agents. The patterns transfer; the conceptual frame only makes sense if you've internalized them.

Minimum:

- Labs 01, 02, 03 finished and understood.
- The [`tool-design`](../../concepts/tools/tool-design.md) and [`tool-selection`](../../concepts/tools/tool-selection.md) concept pages read.
- All five Foundations quizzes passed at 6+/8.

Lab 05 (LangGraph) is helpful but not required. Path 03 stays from-scratch in v1 for the same reason Path 02 did: framework-bridge batches come later, after the mechanism is clear.

Path 02 (Agentic RAG) is **not** a prerequisite for Path 03. The paths are independent — you can do them in either order, or interleave them. A later Path 03 batch will build a multi-agent RAG system that combines them.

## How this path is structured

Path 03 v1 opens with Module 1 (foundations and the supervisor-worker pattern); Module 2 extends it with iterative refinement via generator-critic; Module 3 adds plan-and-execute with bounded parallel executor pool. Future batches add multi-agent evaluation, the framework-bridge lab, and multi-agent RAG.

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

    classDef concept fill:#e8f0fe,stroke:#1a73e8
    classDef lab fill:#fef7e0,stroke:#f9ab00
    classDef quiz fill:#e6f4ea,stroke:#137333
    class A,B,C,D,E,F,G concept
    class L10,L11,L12 lab
    class Q1,Q2,Q3 quiz
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

## What's not in this batch (anti-scope)

These are explicitly out of scope for Modules 1-3 — they're scoped for future Path 03 batches or other paths entirely:

- **Frameworks.** No CrewAI, no AutoGen, no LangGraph multi-agent helpers (`langgraph.prebuilt.create_supervisor`, `AutoGen.GroupChat`, `crewai.Crew`, `langgraph.types.Send`). The headline labs use only the Path 01 agent loop. Framework-bridge batches come later — the same way Path 02 saved its framework-bridge lab for later.
- **Swarm, tree-of-thoughts, MCTS-style plan search.** These are different multi-agent patterns or different search strategies. Future Path 03 batches may cover swarm; tree search over plans is out of scope for the educational track.
- **Tool-protocol coverage.** MCP and A2A are [Path 04](../04-tool-protocols-mcp-a2a/) territory. They're how agents (and their tools) interoperate across processes / vendors; not the same problem as in-process multi-agent coordination.
- **Multi-agent RAG.** A later Path 03 batch will combine Lab 06-08 retrieval with the supervisor-worker, generator-critic, and planner-executor patterns.
- **Distributed execution / persistent plan state.** Lab 12 uses thread-based concurrency for IO-bound LLM calls. Distributed execution across processes / machines and durable plan state across restarts are out of scope.
- **Production observability + evaluation of multi-agent systems.** Same pattern as Path 02: build the mechanism first, evaluate it later (Path 06 territory).

## What comes next

After Module 3 (this batch) lands, the planned Path 03 expansion is:

- **Module 4 — Multi-agent RAG.** Composing Lab 06-08 retrieval with the supervisor-worker, generator-critic, and planner-executor patterns. A retriever-worker + synthesizer-worker + critic + supervisor-as-coordinator, with the planner deciding the overall research strategy.
- **Module 5 — Framework bridge.** Re-implement Labs 10-12 in LangGraph's multi-agent primitives (`Send`, `Command`, sub-graphs); compare line-by-line; honest discussion of when the framework earns its complexity.
- **Module 6 — Multi-agent evaluation.** Trajectory-level metrics, handoff-success rate, citation-preservation rate, plan-quality metrics, replan rate; the harness pattern from Lab 09 extended for multi-agent.

Each future batch follows the same shape as v1: concept pages first, lab from-scratch, quiz, then the framework comparison only after the from-scratch version is solid.

## References

The papers and projects that shaped how this path is taught:

- **Wang et al. 2023** — "A Survey on Large Language Model based Autonomous Agents" (arXiv:2308.11432). The taxonomy of agent architectures; useful for honest framing of where multi-agent fits.
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

These are starting points, not a reading list. The papers are dense and the field moves fast — verify any specific claim against [`tools/frameworks/snapshot-v1.0.md`](../../tools/frameworks/snapshot-v1.0.md) if it exists, or the framework's own docs if it doesn't.
