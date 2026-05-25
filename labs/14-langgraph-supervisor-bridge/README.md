# Lab 14 — LangGraph supervisor bridge

> ⏱ 120-150 min · 🟡 Intermediate · Prerequisites: Lab 10 (the from-scratch baseline this lab rebuilds), Lab 05 (single-agent LangGraph familiarity)

Rebuild [Lab 10's supervisor-worker pattern](../10-supervisor-worker-from-scratch/) in LangGraph. Same task domain (research + write), same worker contracts (researcher + writer), same step caps — so the comparison is direct. Then go further than Lab 10 could: add a checkpointer for crash-resume; stream intermediate state; demonstrate `Command(goto=..., graph=Command.PARENT)` as the handoff primitive that enables swarm patterns.

The goal isn't to oversell LangGraph. The from-scratch supervisor pattern is already strong; this lab shows where the framework adds limited but useful structure (graph state, routing visibility, checkpointing, streaming) and where the from-scratch version is sufficient (prompt engineering, worker contracts, citation discipline).

> 📖 The framing pages for this lab:
> [LangGraph multi-agent: the primitives](../../concepts/multi-agent/langgraph-multi-agent.md),
> [when frameworks earn complexity](../../concepts/multi-agent/when-frameworks-earn-complexity.md).
> 🧠 Calibrate against the [framework bridge quiz](../../quizzes/multi-agent/framework-bridge.md).
> ⬅️ Compare line-by-line against [Lab 10 solution](../10-supervisor-worker-from-scratch/solution/README.md).

## What you'll build

A LangGraph supervisor with the same capability as Lab 10:

- One `researcher` worker (using `create_agent` with `web_search` + `fetch_page` tools — the same tools as Lab 10).
- One `writer` worker (no tools; one LLM call composing prose from the researcher's brief).
- A `supervisor` node that calls these workers via handoff tools, using `Command(goto=...)` to route.
- The same task: "research X and write a 150-word summary."
- The same step caps (mapped onto LangGraph's `recursion_limit`).

Then three extensions Lab 10 couldn't easily do:

1. **Checkpointing.** Compile the graph with `InMemorySaver`. Run, kill the process (simulated), reload from the checkpoint, continue from exactly where it stopped.
2. **Streaming.** Use `graph.stream(...)` to observe state transitions as they happen — which node is running, what state was just updated, which worker is next.
3. **Handoff tool primitive.** Demonstrate the `Command(goto=..., graph=Command.PARENT)` pattern. This is the building block for swarm topology (no central supervisor; agents hand off directly to each other). The lab introduces the primitive; building a full swarm is left as an extension exercise.

## Goal

By the end of the lab you should be able to:

- Map every part of Lab 10's supervisor loop to its LangGraph equivalent: `chat_with_tools` → `create_agent`; structured-error envelopes → `Command(goto=..., update=...)`; `_action_hash` dedup → state field; `SUPERVISOR_MAX_STEPS` → `recursion_limit`.
- Explain *why* each framework primitive exists by reference to a from-scratch concept it replaces (or doesn't).
- Add a checkpointer to persist multi-agent state across a process restart.
- Stream intermediate state and read the resulting events.
- Decide for your next multi-agent project where LangGraph helps and where the from-scratch supervisor is sufficient.
- Recognize that the supervisor's system prompt does not shrink under LangGraph. Prompt engineering remains the dominant cost regardless of framework.

## Prerequisites

- **Lab 10** — the from-scratch supervisor-worker pattern. Lab 14 is a *re-build*. If you haven't built Lab 10, the framework abstractions here will hide too much to follow. Don't skip it.
- **Lab 05** — single-agent LangGraph familiarity. `StateGraph`, `MessagesState`, `add_messages`, `interrupt()`, `Command`. Lab 14 assumes you've seen these.
- **Concept pages** — at minimum [LangGraph multi-agent: the primitives](../../concepts/multi-agent/langgraph-multi-agent.md). The lab references the primitive-to-pattern mapping directly.

## Setup

Same Python 3.11+ environment as previous labs. Two additional packages beyond what Lab 10 used:

```bash
uv add 'langgraph>=1.0,<2.0' 'langchain>=1.0,<2.0' 'langchain-openai>=0.2'
# or 'langchain-anthropic>=0.2' if PROVIDER=anthropic
```

If `uv sync` from the repo root has already installed these (Lab 05's setup), you're set.

## Tools and versions

| Library | Version | Verified |
|---|---|---|
| `langgraph` | `>=1.0,<2.0` (latest: 1.2.1 as of 2026-05-23) | 2026-05-23 |
| `langchain` | `>=1.0,<2.0` | 2026-05-23 |
| `langchain-openai` *or* `langchain-anthropic` | `>=0.2` | 2026-05-23 |
| `ddgs` | (already installed from Lab 03) | — |
| `requests`, `beautifulsoup4` | (already installed from Lab 03) | — |

The full set of pinned APIs and primary-source links lives in [the snapshot page](../../tools/langgraph/snapshot-v1.0.md). If you're running this lab more than ~3 months after the verification date, re-check the snapshot first.

## Structure

Roughly 28-32 cells. Output-stripped. Each step pairs a markdown cell explaining the from-scratch → framework mapping with a code cell implementing it.

- **Step 0**: Setup. Provider config + corpus check.
- **Step 1**: The Lab 10 baseline (for reference). One paragraph reminder of what we're rebuilding.
- **Step 2**: Define the state schema. `SupervisorState(MessagesState)` with extra fields for worker-output payloads (findings + citations).
- **Step 3**: Build the researcher worker as a `create_agent` call. Same `web_search` and `fetch_page` tools as Lab 10. The agent's internal tool-call loop is a sub-graph — LangGraph handles it.
- **Step 4**: Build the writer worker as a `create_agent` call with zero tools. Composes prose from `findings + citations`.
- **Step 5**: Build the supervisor node — manual tool-calling supervisor pattern (the one LangChain currently recommends). System prompt names the workers and the workflow. Returns `Command(goto="researcher" | "writer" | "__end__", update={...})`.
- **Step 6**: Wire the graph. `StateGraph(SupervisorState)`, add the three nodes (`supervisor`, `researcher`, `writer`), edges from each worker back to `supervisor`, entry point at `supervisor`. Compile.
- **Step 7**: Run end-to-end on the same task Lab 10 used. Compare the output to Lab 10's solution.
- **Step 8**: Compile with a checkpointer (`InMemorySaver`). Run with a `thread_id`. Demonstrate resume-from-interruption by simulating a process crash and continuing.
- **Step 9**: Stream the graph's execution. Use `graph.stream(...)` and print each state transition.
- **Step 10**: Demonstrate the `Command(goto=..., graph=Command.PARENT)` primitive in a small example. This is what swarm topology uses for direct agent-to-agent handoff. Building a full swarm is mentioned as an extension exercise.
- **Step 11**: Line-by-line comparison with Lab 10's solution. What got shorter, what stayed the same, what got longer.

## The line-by-line comparison

The lab's closing step is an explicit comparison of code by section:

| Component | Lab 10 (from-scratch) | Lab 14 (LangGraph) | Net change |
|---|---|---|---|
| Chat client | ~50 lines (`chat_with_tools` for two providers) | 0 lines (uses `create_agent`) | Framework wins ~50 lines |
| Researcher worker | ~80 lines (manual tool loop) | ~10 lines (`create_agent` call) | Framework wins ~70 lines |
| Writer worker | ~25 lines (manual LLM call) | ~10 lines (`create_agent` with no tools) | Framework wins ~15 lines |
| Supervisor system prompt | ~30 lines | ~30 lines | No change |
| Supervisor loop | ~70 lines (manual dispatch + action-hash + step-cap) | ~40 lines (`Command(goto=...)` returns) | Framework wins ~30 lines |
| Worker schemas | ~20 lines (Pydantic `StrictModel`) | ~20 lines (TypedDict state fields) | No change |
| Crash-resume support | Not implemented | ~5 lines (`InMemorySaver`) | Framework adds capability |
| Streaming support | Not implemented | ~5 lines (`graph.stream()`) | Framework adds capability |

The pattern is consistent: the framework wins where the from-scratch version was implementing infrastructure (chat client, tool loop, dispatch glue). The framework breaks even or adds lines where the work is genuinely the supervisor's logic (system prompt, worker contracts). Two capabilities (crash-resume, streaming) are added by the framework that the from-scratch version didn't have.

## What to watch for

Five practical issues:

**1. The supervisor's system prompt does not shrink.** This is the most surprising finding for learners who expect LangGraph to "do more for you." Routing decisions are still LLM decisions; the LLM needs the same instructions whether the routing is implemented via tool calls or via `Command(goto=...)` returns. If your supervisor prompt got shorter, you probably moved logic out of the prompt and into hardcoded graph edges — which works for deterministic routing but loses flexibility.

**2. Worker prompts also do not change.** The researcher's job is "search, fetch, summarize, return JSON envelope." The writer's job is "compose 150 words with citations." Neither changes because of the framework. Prompt engineering is the same problem at the framework level.

**3. The `recursion_limit` config replaces `SUPERVISOR_MAX_STEPS`.** Default is 25. Each supervisor → worker → supervisor cycle is 2 graph steps. For Lab 10's `SUPERVISOR_MAX_STEPS=6` equivalent, you want `recursion_limit=12`. Setting it explicitly is better than relying on the default; setting it too high invites routing loops.

**4. State schema changes are migrations.** Adding a field to `SupervisorState` means: update the TypedDict, update every node that touches state, possibly migrate existing checkpointed state. In the from-scratch version, adding a tracking variable was a local change. This is a real cost of the framework that doesn't show up in line counts.

**5. The `create_agent` helper hides the worker's tool loop.** This is the framework's biggest abstraction-vs-transparency trade-off in this lab. You no longer see `web_search` being called, then `fetch_page`, then `web_search` again. You see only the worker's final return. For most production cases this is fine; for debugging unexpected worker behavior, you'll reach for `astream_events()` or LangSmith tracing.

## Anti-scope

Deliberately out of scope, scoped for future batches or other paths:

- **`langgraph-supervisor` package usage.** Per [the upstream deprecation note](https://github.com/langchain-ai/langgraph-supervisor-py), new code should use the manual supervisor pattern this lab demonstrates, not the `create_supervisor()` helper.
- **A full swarm implementation.** The `Command(goto=..., graph=Command.PARENT)` building block is shown; the full swarm topology with multiple specialist agents handing off directly is left as an extension exercise.
- **Hierarchical supervisor-of-supervisors.** Mentioned in the concept page; not built. Lab 15 demonstrates the building block (sub-graph as a node in a parent graph).
- **Lab 11 (critic) framework rewrite.** The critic pattern is framework-agnostic: a node that takes `(brief, draft)` and returns `{status, issues}` is the same in LangGraph as in Lab 11. No new framework primitives to demonstrate. Mentioned in the concept page as an extension exercise.
- **Lab 13 (multi-agent RAG) framework rewrite.** This would be Lab 14 + retrieval-pipeline-as-node — mostly a composition exercise. Mentioned in the concept page as future work; not in this batch.
- **LangSmith integration.** Out of scope for the labs (you'd need API keys + an account). Mentioned in the concept page as one of the operational concerns that frameworks can address.
- **LangGraph Studio / Platform / Cloud.** Out of scope.
- **Production deployment patterns.** Path 06 territory.

## Run-time and cost

Per end-to-end run on the demo task:

- 1-2 supervisor calls (routing decisions)
- 2-5 researcher tool calls (one `web_search` + 1-3 `fetch_page` calls, handled inside `create_agent`)
- 1 writer call
- Total: ~5-8 LLM calls per task, ~$0.03-$0.06 at gpt-4o-mini rates.

Wall-clock dominated by `fetch_page` (live web). Typical end-to-end: 10-15 seconds. Checkpointer adds negligible overhead. Streaming adds slight latency but improves perceived responsiveness.

## Solution

A reference implementation will land in `solution/lab.ipynb` in a follow-up batch. Two design decisions worth flagging up front:

- **The supervisor is a manual node, not `create_supervisor()`.** Per the upstream recommendation. This keeps the supervisor's logic visible and editable.
- **The state schema is a `TypedDict` extending `MessagesState`.** Per the `create_agent` constraint (Pydantic state isn't supported there). The extra fields (`findings`, `citations`, `brief_status`) live alongside the inherited `messages` field.

## Next

- After completing the lab, take the [framework bridge quiz](../../quizzes/multi-agent/framework-bridge.md).
- [Lab 15](../15-langgraph-plan-execute-bridge/) rebuilds Lab 12's plan-and-execute in LangGraph using the `Send` primitive — the stronger framework value case.
- The follow-up solutions batch will provide reference implementations for both Lab 14 and Lab 15.
