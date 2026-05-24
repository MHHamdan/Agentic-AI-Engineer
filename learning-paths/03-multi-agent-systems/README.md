# 03 · Multi-Agent Systems

> 🟡 Intermediate · ⏱ 6–9 hours (v1 opening) · 📍 Start here once you've completed Path 01 · 🚧 Path 03 in progress (foundations + supervisor-worker)

## Who this is for

You've finished Foundations: you can build an agent loop from scratch (Lab 01), design tools that work (Lab 02), and ship a multi-step research agent (Lab 03). You understand that the agent loop is just `while not done: think → act → observe`, and you've felt the failure modes that come from getting the basics wrong.

This path takes you from "I can build *one* agent" to "I can wire *several* agents together to do something none of them could do alone — and I know the difference between when that's a genuine win and when it's expensive theater."

By the end of Path 03 v1 you should be able to:

- Decide honestly when a task wants a multi-agent system and when it doesn't.
- Reason about coordination cost — every handoff is an extra LLM call, with latency, tokens, and failure-mode implications.
- Implement the **supervisor-worker pattern** from scratch using only the Lab 01 agent-loop machinery. No frameworks.
- Distinguish **message-passing** from **shared-state** architectures and pick the right one for a given task shape.
- Apply the three handoff-hygiene rules that prevent the most common multi-agent bugs.
- Compose step caps, action-hash dedup, and structured-error envelopes *across agent levels* without surprises.
- Carry citations through worker → supervisor handoffs without trusting the LLM to preserve them.

## Prerequisites

**Complete Path 01 — Foundations first.** This is non-negotiable. Lab 10 is structurally a Lab 02 supervisor whose "tools" are calls to Lab 03–style worker agents. The patterns transfer; the conceptual frame only makes sense if you've internalized them.

Minimum:

- Labs 01, 02, 03 finished and understood.
- The [`tool-design`](../../concepts/tools/tool-design.md) and [`tool-selection`](../../concepts/tools/tool-selection.md) concept pages read.
- All five Foundations quizzes passed at 6+/8.

Lab 05 (LangGraph) is helpful but not required. Path 03 stays from-scratch in v1 for the same reason Path 02 did: framework-bridge batches come later, after the mechanism is clear.

Path 02 (Agentic RAG) is **not** a prerequisite for Path 03. The paths are independent — you can do them in either order, or interleave them. A later Path 03 batch will build a multi-agent RAG system that combines them.

## How this path is structured

Path 03 v1 opens with one module: the foundations and the supervisor-worker pattern. Future batches extend it with agent debate, plan-and-execute, multi-agent evaluation, the framework-bridge lab, and multi-agent RAG.

```mermaid
flowchart LR
    A[📖 What is a multi-agent system?] --> B[📖 Supervisor-worker pattern]
    B --> C[📖 Handoffs and shared state]
    C --> L10[🧪 Lab 10: Supervisor-worker from scratch]
    L10 --> Q1[🧠 Multi-agent fundamentals quiz]

    classDef concept fill:#e8f0fe,stroke:#1a73e8
    classDef lab fill:#fef7e0,stroke:#f9ab00
    classDef quiz fill:#e6f4ea,stroke:#137333
    class A,B,C concept
    class L10 lab
    class Q1 quiz
```

## Modules

### Module 1 — Foundations + supervisor-worker (this batch)

**Three concept pages:**

- [📖 What is a multi-agent system?](../../concepts/multi-agent/what-is-a-multi-agent-system.md) — ~10 min. The honest framing: when multi-agent is the wrong call, when it's the right one, why coordination cost is the central tradeoff.
- [📖 The supervisor-worker pattern](../../concepts/multi-agent/supervisor-worker-pattern.md) — ~10 min. The simplest useful multi-agent shape. One coordinator routes work to specialist workers and synthesizes results.
- [📖 Handoffs and shared state](../../concepts/multi-agent/handoffs-and-shared-state.md) — ~9 min. The two architectures; the three handoff-hygiene rules; where things go wrong.

**One lab:**

- [🧪 Lab 10 — Supervisor-worker from scratch](../../labs/10-supervisor-worker-from-scratch/) — ~100-130 min. Build a 3-agent system (supervisor + researcher + writer) using only the Lab 01-03 agent-loop machinery. No new dependencies. The researcher gets Lab 03's `web_search` + `fetch_page`; the writer is prompt-only; the supervisor's "tools" are calls to the workers via the standard tool-dispatch contract from Lab 02.

**One quiz:**

- [🧠 Multi-agent fundamentals](../../quizzes/multi-agent/multi-agent-fundamentals.md) — 8 single-select questions on when to reach for multi-agent, the supervisor-worker mediation property, handoff hygiene, and how the Lab 01-03 patterns compose across levels.

## What's not in this batch (anti-scope)

These are explicitly out of scope for the v1 opening — they're scoped for future Path 03 batches or other paths entirely:

- **Frameworks.** No CrewAI, no AutoGen, no LangGraph multi-agent helpers (`langgraph.prebuilt.create_supervisor`, `AutoGen.GroupChat`, `crewai.Crew`). The headline lab uses only the Path 01 agent loop. Framework-bridge batches come later — the same way Path 02 saved its framework-bridge lab for later.
- **Agent debate, voting, plan-and-execute.** These are different multi-agent patterns with their own tradeoffs and failure modes. Future Path 03 batches will cover each in turn, with the same "from scratch first, framework second" discipline.
- **Tool-protocol coverage.** MCP and A2A are [Path 04](../04-tool-protocols-mcp-a2a/) territory. They're how agents (and their tools) interoperate across processes / vendors; not the same problem as in-process multi-agent coordination.
- **Multi-agent RAG.** A later Path 03 batch will combine Lab 06-08 retrieval with the supervisor-worker pattern.
- **Production observability + evaluation of multi-agent systems.** Same pattern as Path 02: build the mechanism first, evaluate it later (Path 06 territory).

## What comes next

After this batch (Module 1) lands, the planned Path 03 expansion is:

- **Module 2 — Agent debate and critic patterns.** A two-agent loop where one generates and one critiques; iterative refinement. Failure modes specific to debate (sycophancy, infinite agreement, runaway disagreement).
- **Module 3 — Plan-and-execute.** A planner agent emits a structured plan; an executor agent (or pool of them) carries it out. When this beats supervisor-worker and when it doesn't.
- **Module 4 — Multi-agent RAG.** Composing Lab 06-08 retrieval with the supervisor pattern. A retriever-worker + synthesizer-worker + supervisor-as-coordinator.
- **Module 5 — Framework bridge.** Re-implement Lab 10 in LangGraph's multi-agent primitives (`Send`, `Command`, sub-graphs); compare line-by-line; honest discussion of when the framework earns its complexity.
- **Module 6 — Multi-agent evaluation.** Trajectory-level metrics, handoff-success rate, citation-preservation rate; the harness pattern from Lab 09 extended for multi-agent.

Each future batch follows the same shape as v1: concept pages first, lab from-scratch, quiz, then the framework comparison only after the from-scratch version is solid.

## References

The papers and projects that shaped how this path is taught:

- **Wang et al. 2023** — "A Survey on Large Language Model based Autonomous Agents" (arXiv:2308.11432). The taxonomy of agent architectures; useful for honest framing of where multi-agent fits.
- **Wu et al. 2023** — "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" (arXiv:2308.08155). The architecture paper, not the framework. Read for the conversation-driven design philosophy.
- **Hong et al. 2023** — "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework" (arXiv:2308.00352). One of the cleaner examples of role-specialized agents producing useful artifacts.
- **Qian et al. 2023** — "Communicative Agents for Software Development" / ChatDev (arXiv:2307.07924). A multi-agent system that produces working software; useful concrete example of when role specialization pays off.
- **Park et al. 2023** — "Generative Agents: Interactive Simulacra of Human Behavior" (arXiv:2304.03442). The famous Smallville paper; emphasizes how much of "agentic" behavior is really prompt design plus memory plus tools.
- **Anthropic 2024** — ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents). Engineering-grounded essay on agent design; the most-quoted piece of practical advice for production multi-agent work.

These are starting points, not a reading list. The papers are dense and the field moves fast — verify any specific claim against [`tools/frameworks/snapshot-v1.0.md`](../../tools/frameworks/snapshot-v1.0.md) if it exists, or the framework's own docs if it doesn't.
