# LangGraph — tool snapshot

> 🔴 **Tool snapshot — LangGraph `1.x` series, verified 2026-05-23**
> Source: [LangChain & LangGraph 1.0 announcement (blog, 2025-10-22)](https://blog.langchain.com/langchain-langgraph-1dot0/) · [LangGraph v1 migration guide](https://docs.langchain.com/oss/python/migrate/langgraph-v1) · [Releases on GitHub](https://github.com/langchain-ai/langgraph/releases)

LangGraph is fast-changing. This page is the single source of truth for which LangGraph APIs the labs and concept pages in this repo assume. **When this page goes stale, the labs go stale.** Maintainers: update this page first when LangGraph ships a breaking change, then update downstream content.

## Verified version & pin

The repo pins LangGraph as:

```toml
langgraph = ">=1.0,<2.0"
```

| Item | Status as of 2026-05-23 |
|------|------------------------|
| Latest stable release | `1.2.1` (Apr 2026) |
| GA milestone | `1.0` GA on **2025-10-22** |
| Stability promise | LangChain has publicly committed to **no breaking changes until `2.0`**. Patch (`1.0.x`) and minor (`1.1.x`, `1.2.x`) releases are additive. |
| Python requirement | `>=3.10` (matches our project floor of 3.11) |
| Companion: `langchain` | `1.x` series; `langchain.agents.create_agent` is the recommended high-level entry point as of 1.0 |

If you're reading this more than ~3 months after the verified date, run the **freshness check** at the bottom of this page before trusting the code in the labs.

## What you can rely on (stable APIs)

The labs use this subset of LangGraph, which is part of the `1.0` stability contract:

```python
# Graph construction
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages

# Tool node and routing helpers
from langgraph.prebuilt import ToolNode, tools_condition

# Checkpointing (state persistence)
from langgraph.checkpoint.memory import InMemorySaver

# Human-in-the-loop
from langgraph.types import interrupt, Command

# High-level helper (LangChain 1.x layer that runs on LangGraph)
from langchain.agents import create_agent
```

Notes on each:

- **`StateGraph` and `MessagesState`** — the core graph builder and the prebuilt state schema with a `messages: Annotated[list, add_messages]` field. `MessagesState` is the right starting point for chat-style agents.
- **`add_messages`** — the reducer that appends new messages to the state's `messages` list. Modeling state mutations as reducers (rather than direct assignment) is what makes parallel updates and replay work correctly.
- **`ToolNode`** and **`tools_condition`** — the prebuilt patterns for executing tool calls and conditionally routing to either tool execution or the end state. Use these instead of hand-rolling the tool loop unless you have a specific reason not to.
- **`InMemorySaver`** — the dev/test checkpointer. Replace with `langgraph.checkpoint.postgres.PostgresSaver` or `langgraph.checkpoint.sqlite.SqliteSaver` for production persistence. Note: the older `MemorySaver` name still exists as an alias; new code should use `InMemorySaver`.
- **`interrupt(payload)` and `Command(resume=value)`** — the human-in-the-loop primitives. `interrupt()` pauses graph execution from inside a node and surfaces `payload` to the caller; resuming with `graph.invoke(Command(resume=value), config=...)` makes `value` the return value of `interrupt()` and continues from there. **A checkpointer is required** for interrupts to resume across process restarts.
- **`create_agent`** — the **LangChain 1.x** high-level agent helper that runs on LangGraph. It supersedes `langgraph.prebuilt.create_react_agent` for new code. Use it when you want a fast path to a tool-using agent with middleware support; drop down to raw `StateGraph` when you need custom routing or state shapes.

### Multi-agent surface (added for Path 03 Module 5 labs)

Labs 14 and 15 use these additional primitives, all part of the `1.0` stability contract:

```python
# Multi-agent control flow + parallel dispatch
from langgraph.types import Send, Command
```

- **`Command(goto=..., update=..., graph=...)`** — combined control-flow + state-update return value from a node. The `goto` argument names the next node (or `"__end__"`); the `update` argument is a partial state dict merged via the configured reducers; the optional `graph=Command.PARENT` argument navigates out of a sub-graph to its parent. Replaces the older pattern of returning a state-update dict and using `add_conditional_edges` for routing.
- **`Send(node, state)`** — runtime-determined parallel dispatch. A node that returns `list[Send]` triggers concurrent execution of the named nodes with each `Send`'s state payload. Results merge back into the parent state via reducers. This is the primary parallel-dispatch primitive; it replaces manual `ThreadPoolExecutor` patterns at the graph level.
- **Sub-graph composition** — a compiled `StateGraph` can be passed as a node to a parent `StateGraph` via `parent.add_node("subgraph_node", subgraph_compiled)`. State maps between parent and sub-graph via state-key overlap (matching keys are passed through; differing schemas require explicit mapping). Used for hierarchical multi-agent composition.

Notes for multi-agent specifically:

- **The `langgraph-supervisor` package is no longer recommended for new code.** As of early 2026, the package's own README states: *"We now recommend using the supervisor pattern directly via tools rather than this library for most use cases."* Lab 14 uses the recommended manual supervisor-via-tools pattern with `Command(goto=...)` returns. The `langgraph_supervisor` package can still be installed and used, but is not part of this repo's verified surface.
- **`recursion_limit`** on `invoke()` (and `astream()`) bounds the worst-case number of graph steps. Default is 25. For multi-agent graphs, set this explicitly via `graph.invoke(input, config={"recursion_limit": 40})`. Each supervisor → worker → supervisor cycle is two steps; budget accordingly.
- **Reducers for parallel updates.** When using `Send` to dispatch multiple parallel workers, the state field they update needs a reducer (typically `operator.add` for lists or `add_messages` for message lists). Without a reducer, the last write wins; with one, all parallel updates merge correctly.

## What changed in 1.0 (and what got deprecated)

These are the headline changes that matter for anyone migrating from `0.x` code or following 2024-era tutorials:

### `create_react_agent` → `create_agent`

The single highest-impact change. The `langgraph.prebuilt.create_react_agent` helper still works but is **deprecated** as of LangGraph 1.0 per the [official migration guide](https://docs.langchain.com/oss/python/migrate/langgraph-v1). New code should use:

```python
# Old (still works, deprecated)
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(model, tools=tools)

# New (LangChain 1.0+)
from langchain.agents import create_agent
agent = create_agent(model, tools=tools, system_prompt="...")
```

`create_agent` is built on the LangGraph runtime and adds a middleware system, a cleaner state contract, and provider-agnostic tool wiring. Behavior is broadly equivalent for the simple case; differences appear when you need custom state schemas or per-step interception.

**One gotcha that's caused real migration pain:** `create_agent` drops support for Pydantic models and dataclasses as the agent state schema — everything must be expressed as a `TypedDict` extending `AgentState`. If your codebase passes Pydantic models as state to `create_react_agent`, migration requires reshaping that surface. Field-validated message payloads remain fine; it's the *state container* that has to be a TypedDict.

### Legacy `AgentExecutor` and `initialize_agent` are gone

If you're following a tutorial that uses `initialize_agent(...)` or `AgentExecutor(...)`, the tutorial is from the pre-LangGraph era. These were deprecated in LangChain 0.2 and moved to a `langchain-legacy` package by 1.0. Don't carry them into new code.

### Checkpointer naming

`MemorySaver` (the original name) and `InMemorySaver` (the current preferred name) both still work. The docs and examples have standardized on `InMemorySaver`; prefer the new name in new code.

### `langgraph-checkpoint` is now a separate package

`pip install langgraph` no longer transitively pulls in the database backends — install `langgraph-checkpoint-postgres`, `langgraph-checkpoint-sqlite`, etc. explicitly. `InMemorySaver` is part of the core `langgraph` package and remains zero-config.

### `langgraph-supervisor` helper deprecated for new code

The `langgraph-supervisor` package (which provided `create_supervisor()` as a high-level helper) is no longer recommended by its maintainers for new code. As of early 2026, the package README states the supervisor pattern should be implemented directly via tool calling, not via the `create_supervisor()` helper. The helper still works for existing code; new code should use the manual supervisor pattern that Lab 14 demonstrates. This is consistent with the pattern documented in the [LangGraph multi-agent guide](https://langchain-ai.github.io/langgraph/concepts/multi_agent/).

### `recursion_limit` for multi-agent worst-case bounds

LangGraph's `recursion_limit` config parameter (default: 25) bounds the maximum number of graph steps in a single invocation. For multi-agent graphs where supervisor → worker → supervisor cycles each consume 2 steps, set this explicitly: `graph.invoke(input, config={"recursion_limit": 40})`. Hitting the limit raises `GraphRecursionError`; if you hit it frequently in practice, the cause is almost always a routing loop, not a need for a higher limit.

## Tradeoffs to keep in mind

A few things the marketing material won't tell you, and that the [community](https://forum.langchain.com/) has surfaced post-1.0:

- **Dependency surface is wide.** `langgraph` + `langchain` + `langchain-core` + the provider integration (`langchain-openai` or `langchain-anthropic`) is a meaningful install. The labs deliberately use small environments to make this visible.
- **The TypedDict-only state requirement** for `create_agent` (above) can be a friction point if you're standardizing on Pydantic elsewhere.
- **Multiple ways to do the same thing.** You can build a tool-using agent with raw `StateGraph`, with `create_agent`, or with the older `create_react_agent`. Lab 05 walks through `StateGraph` and `create_agent` so you understand both layers — pick `StateGraph` when you need control, `create_agent` when you don't.
- **Tracing is excellent — if you use LangSmith.** LangGraph's runtime emits rich traces that LangSmith renders well. If you're using a different observability stack (OpenTelemetry, Langfuse, etc.), the integration is workable but less polished. We cover this in Path 06 — Evaluation & Observability.

## Where this snapshot is used

When this page updates, the following content depends on it and may need updates too:

- 🧪 [`labs/05-langgraph-rewrite/`](../../labs/05-langgraph-rewrite/) — the lab that exercises this API surface
- 📖 [`concepts/agents/agents-vs-frameworks.md`](../../concepts/agents/agents-vs-frameworks.md) — references this page for "what LangGraph provides"
- 🧠 [`quizzes/foundations/langgraph-basics.md`](../../quizzes/foundations/langgraph-basics.md) — quiz questions assume the 1.x API
- 🗺 [`learning-paths/01-foundations/README.md`](../../learning-paths/01-foundations/README.md) — Module 6 (LangGraph) references this snapshot

## Freshness check

Before trusting this page as current, verify each of the following from primary sources. If anything is more than a minor version drift, update the page.

1. **Latest stable version.** Check [github.com/langchain-ai/langgraph/releases](https://github.com/langchain-ai/langgraph/releases) for the most recent tagged release. Confirm it's still on the `1.x` line.
2. **Deprecations.** Skim [docs.langchain.com/oss/python/migrate/langgraph-v1](https://docs.langchain.com/oss/python/migrate/langgraph-v1) — if new items have been added to the "deprecated" table, mirror them here.
3. **`create_agent` API.** Confirm [docs.langchain.com/oss/python/langgraph/agents](https://docs.langchain.com/oss/python/langgraph/agents) still describes the same signature and state shape. If the state model contract has changed (e.g., Pydantic support added back), update the gotcha note above.
4. **Interrupt/Command primitives.** Confirm [docs.langchain.com/oss/python/langgraph/interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) still describes `interrupt()` + `Command(resume=...)`. Earlier versions used `interrupt_before` / `interrupt_after` exclusively; both still work but the dynamic form is preferred.

When you update this page, bump the verification date at the top and add a row to the [CHANGELOG](../../CHANGELOG.md) under **Verified Tool Snapshots** in the `[Unreleased]` section.

## Primary sources

The verification claims on this page are anchored to these documents. Anything not from one of these should be treated as community context, not authoritative.

| Source | What it covers |
|---|---|
| [LangChain blog: 1.0 announcement (2025-10-22)](https://blog.langchain.com/langchain-langgraph-1dot0/) | The GA announcement; the "first major release" framing |
| [LangGraph v1 migration guide](https://docs.langchain.com/oss/python/migrate/langgraph-v1) | The canonical deprecation table for `create_react_agent` and friends |
| [docs.langchain.com — Agents](https://docs.langchain.com/oss/python/langgraph/agents) | `create_agent` signature, state model, middleware |
| [docs.langchain.com — Memory](https://docs.langchain.com/oss/python/langgraph/add-memory) | Checkpointer APIs: `InMemorySaver`, `PostgresSaver`, thread_id config |
| [docs.langchain.com — Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) | `interrupt()` and `Command(resume=...)` |
| [github.com/langchain-ai/langgraph/releases](https://github.com/langchain-ai/langgraph/releases) | Release tags, changelogs per release |

When a community blog post contradicts one of these, trust the official doc.
