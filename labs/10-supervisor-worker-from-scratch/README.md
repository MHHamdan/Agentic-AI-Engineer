# Lab 10 — Supervisor-worker from scratch

> ⏱ 100-130 min · 🟡 Intermediate · Prerequisites: Labs 01, 02, 03

Build a three-agent system — supervisor + researcher + writer — using only the agent-loop machinery from Path 01. No frameworks. No multi-agent libraries. The supervisor's "tools" are calls to the worker agents, dispatched through the same `chat_with_tools` contract from Lab 02.

The pedagogical bet: if you can build the supervisor-worker pattern from the bare agent loop, then adopting CrewAI / AutoGen / LangGraph multi-agent later becomes an *informed* engineering choice, not a magic-box dependency.

## What you'll build

A research-and-write pipeline:

```
user task: "Research recent developments in MCP and write a 150-word summary."
                    │
                    ▼
            ┌───────────────┐
            │  supervisor   │  decides who to call, in what order, synthesizes
            └───────────────┘
                ▲           ▲
                │           │
        ┌───────┘           └───────┐
        ▼                           ▼
┌──────────────┐            ┌──────────────┐
│  researcher  │            │   writer     │
│              │            │              │
│ web_search   │            │ no tools     │
│ fetch_page   │            │ prompt only  │
└──────────────┘            └──────────────┘
```

Three agents, each with its own:

- System prompt.
- Tool set.
- Conversation history.
- Agent loop (Lab 01-style, with `MAX_STEPS`, structured errors, and action-hash dedup).

The supervisor sees the workers as two tools: `call_researcher(question)` and `call_writer(brief)`. The internal trajectories of the workers are invisible to the supervisor — it only sees their return values.

## Goal

By the end of the lab you should be able to:

- Implement the supervisor-worker pattern in ~250 lines of Python with no new dependencies.
- Explain why workers' tool schemas (as seen by the supervisor) are the most important design surface in a multi-agent system.
- Compose step caps across agent levels without surprises.
- Pass citations through a worker → supervisor → final-answer handoff without trusting the LLM to preserve them.
- Apply Lab 02's negative-guidance tool descriptions to make the supervisor route correctly.

## Prerequisites

- **Lab 01** — the agent loop. The supervisor *is* a Lab 01 agent loop with worker-calling tools.
- **Lab 02** — tool design. The supervisor's worker-routing accuracy depends almost entirely on the worker tool descriptions following Lab 02's principles.
- **Lab 03** — `web_search` and `fetch_page`. The researcher worker uses these verbatim. Lab 03's citation-tracking-by-the-loop pattern is what we'll extend through the worker → supervisor handoff.
- **Concept pages** — at minimum [supervisor-worker pattern](../../concepts/multi-agent/supervisor-worker-pattern.md) and [handoffs and shared state](../../concepts/multi-agent/handoffs-and-shared-state.md).

## Setup

No new dependencies. Same `.env` setup as Labs 01-03 (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`). The `ddgs`, `requests`, and `bs4` you installed for Lab 03 are still needed for the researcher worker.

## Structure

Roughly 30-35 cells, output-stripped, with sample-output markdown cells:

- **Step 0**: Setup — `.env` autoload, provider selection, the same `chat_with_tools` provider-agnostic client used since Lab 01.
- **Step 1**: The researcher worker — `researcher_agent(question)` runs a Lab 03-style loop with `web_search` + `fetch_page` + citation tracking; returns `{"findings": ..., "citations": [...]}`.
- **Step 2**: The writer worker — `writer_agent(brief)` runs a prompt-only loop (no tools); returns `{"answer": ...}`. The brief includes the researcher's findings *and* citations, with explicit instructions to preserve citation references in the prose.
- **Step 3**: The supervisor — sees the workers as two tools (`call_researcher`, `call_writer`) with strict Pydantic schemas; system prompt makes the decomposition strategy explicit; same action-hash dedup as Lab 03; smaller step cap than the workers because routing is shallower work than research.
- **Step 4**: Run on a real task end-to-end with a verbose trace showing each agent's invocation.
- **Step 5**: Failure-mode walkthrough — what happens when the supervisor calls the researcher twice with the same query (dedup catches it), when the writer over-runs its step cap (partial-result with status flag the supervisor reads), when the supervisor tries to call a non-existent worker (structured error, supervisor sees it and recovers).
- **Step 6** (stretch): Add a third worker — a `critic_agent` that reviews the writer's output for citation preservation and factual grounding; the supervisor's prompt is extended to invoke it before final synthesis.

## What to watch for

The five failure modes that tend to bite in multi-agent code, in rough order:

1. **Citation drops across the handoff.** The researcher returns citations as a structured field; the supervisor synthesizes a final answer that uses the *findings* but forgets the *citations*. Fix lives in the supervisor's system prompt: explicit instruction to preserve the citations list in the final answer, plus a structured payload that doesn't ask the LLM to re-serialize.
2. **Supervisor over-calling the researcher.** The classic loop: supervisor reads findings → decides "I need a bit more" → calls researcher again with a slightly different query → and again. Action-hash dedup helps catch exact repeats; the smaller supervisor step cap is what prevents the drift.
3. **Writer asking for more research.** The writer's prompt should be tight: "If the brief lacks something, return `{\"status\": \"needs_more_research\", \"missing\": [...]}`. Do NOT search yourself." Violating this is the canonical "worker scope creep" bug.
4. **Step cap interaction.** Worker has `WORKER_MAX_STEPS = 8`; supervisor has `SUPERVISOR_MAX_STEPS = 6`. They're independent. A worker hitting *its* step cap returns a partial-result payload with a status flag; the supervisor sees it and decides what to do — it does *not* mean the supervisor terminates.
5. **Wrong worker chosen.** The supervisor uses `call_researcher` when the writer would have sufficed (the question can be answered from the conversation history alone). Mitigation: negative guidance in the `call_researcher` description ("Do NOT use if the answer is already in this conversation; just write directly.").

## Anti-scope

Deliberately out of scope, scoped for future batches:

- **CrewAI / AutoGen / LangGraph multi-agent helpers.** None of them. Lab 10 is `chat_with_tools` and Python all the way down. Framework bridges come later.
- **Parallel worker execution.** Sequential. Async/parallel work is a different design question and adds failure modes that distract from the core pattern.
- **Shared state.** Message-passing only. Shared-state architecture (LangGraph's `StateGraph`) is covered in the framework-bridge module.
- **Multi-agent RAG.** A future Path 03 batch composes the supervisor-worker pattern with Path 02's contextual retrieval pipeline.
- **Production observability.** Logging, tracing, cost tracking — out of scope here; Path 06.
- **Agent debate, plan-and-execute, swarm.** Different multi-agent patterns; different batches.
- **MCP / A2A protocol coverage.** Different problem (cross-process / cross-vendor interop). Path 04.

## Run-time and cost

Roughly 5-10 LLM calls per end-to-end run, depending on how many fetches the researcher does:

- 1-2 supervisor calls (routing + synthesis).
- 2-4 researcher calls (search → optional refine → fetch → maybe a second fetch → final answer).
- 1 writer call (no tools, single-pass synthesis).

At gpt-4o-mini rates, the full lab end-to-end is well under $0.05 to run. Wall-clock is dominated by `fetch_page` calls (live web; 1-3 seconds each).

## Solution

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) with notes in [`solution/README.md`](./solution/README.md). 17 cells vs the lab's 33 — the failure-mode walks, the production-readiness recap, and the structured-trace appendix are removed since you've already worked through them. Two choices flagged there:

- **The supervisor's worker tools use Pydantic schemas with `ConfigDict(extra="forbid")`** — same `StrictModel` pattern from Lab 02. This isn't decorative: in strict tool-calling mode the supervisor can't pass extra fields, which keeps the handoff envelope tight.
- **Workers are plain functions, not classes.** A worker is a function from sub-task to structured result; the agent loop is an implementation detail of that function. Resisting the urge to make workers into objects with `.run()` methods keeps the seam between "tool" and "worker" cleanly thin.

## Next

- After completing the lab, take the [multi-agent fundamentals quiz](../../quizzes/multi-agent/multi-agent-fundamentals.md).
- Path 03 continues with Lab 11 (generator-critic), Lab 12 (plan-and-execute), Lab 13 (multi-agent RAG) — all now shipped — and Module 5's framework bridge in [Lab 14](../14-langgraph-supervisor-bridge/) + [Lab 15](../15-langgraph-plan-execute-bridge/).
- If you came from Path 02 and want to see how multi-agent extends RAG, [Lab 13](../13-multi-agent-rag-from-scratch/) combines Lab 10's pattern with Lab 06-08's retrieval stack.
