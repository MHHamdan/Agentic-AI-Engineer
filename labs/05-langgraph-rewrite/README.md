# Lab 05: LangGraph rewrite of Lab 01

> 🟡 Intermediate · ⏱ ~90–120 min · 📊 Beginner-to-intermediate

## 🎯 Goal

Take the agent you built **from scratch in Lab 01** and rebuild it in **LangGraph**. Use the same domain, the same tools, and the same test queries — so the only thing that changes is *how* the agent is wired together. Then go further than Lab 01 could: add checkpointing, then add a human-in-the-loop approval gate.

By the end you should be able to:

- Map every part of Lab 01's loop to its LangGraph equivalent (`StateGraph`, `MessagesState`, `add_messages`, `ToolNode`, `tools_condition`).
- Explain *why* each framework primitive exists — i.e., what problem in the from-scratch version it solves.
- Add a `checkpointer` to persist state and resume runs.
- Add an `interrupt(...)` node for human approval, and resume with `Command(resume=...)`.
- Decide for your next project whether to use a framework or hand-roll the loop, with concrete tradeoffs in mind (see [`concepts/agents/agents-vs-frameworks.md`](../../concepts/agents/agents-vs-frameworks.md)).

## 📋 Prerequisites

**Read first:**

- 📖 [Agents vs. frameworks](../../concepts/agents/agents-vs-frameworks.md) — the framing this lab depends on
- ⚙️ [LangGraph tool snapshot](../../tools/langgraph/snapshot-v1.0.md) — the verified versions and APIs

**Complete first:**

- 🧪 [Lab 01: First agent from scratch](../../labs/01-first-agent-from-scratch/) — Lab 05 is a *re-build* of Lab 01. If you haven't built Lab 01, this lab will feel like "magic happens here." Don't skip it.
- 🧪 [Lab 02: Tool design and selection](../../labs/02-tool-design-and-selection/) is helpful but not strictly required.

**Setup:**

- Same Python 3.11+ environment as previous labs.
- One additional package: `langgraph >= 1.0, < 2.0`. If `uv sync` from the repo root has already installed it, you're set. Otherwise: `uv add 'langgraph>=1.0,<2.0' 'langchain>=1.0,<2.0' 'langchain-openai>=0.2'` (or `langchain-anthropic`).

## 🛠 Tools and versions

| Library | Version | Verified |
|---|---|---|
| `langgraph` | `>=1.0,<2.0` (latest: 1.2.1 as of 2026-05-23) | 2026-05-23 |
| `langchain` | `>=1.0,<2.0` | 2026-05-23 |
| `langchain-openai` *or* `langchain-anthropic` | `>=0.2` | 2026-05-23 |
| `openai` | `>=1.40` | 2026-05-23 |
| `anthropic` | `>=0.34` | 2026-05-23 |

The full set of pinned APIs and primary-source links lives in [the snapshot page](../../tools/langgraph/snapshot-v1.0.md). If you're running this lab more than ~3 months after the verification date, re-check the snapshot first.

## What you'll build

A LangGraph agent with the same capability as Lab 01:

- One `lookup_customer` tool and one `compute_total` tool over a tiny in-memory dataset.
- A ReAct-style loop: model decides, tool runs, model decides again.
- Same three test queries as Lab 01, so the comparison is concrete.

Then two **extensions** Lab 01 couldn't easily do:

1. **Checkpointing.** Compile the graph with `InMemorySaver`, run, kill the process (simulated), reload from the checkpoint, and continue from exactly where it left off.
2. **Human approval gate.** Add a node that `interrupt()`s before any destructive operation, surfacing the proposed action to the caller. Resume with `Command(resume=...)`.

## Steps

The notebook walks through these in order:

**0. Setup.** Imports, env, the same canned dataset Lab 01 used.

**1. The Lab 01 reference loop.** Reprint the relevant pieces of Lab 01's from-scratch agent. Three test queries. **This is the baseline.**

**2. Tools as LangChain tools.** Wrap the same functions as `@tool`-decorated callables. Show the parallel: the *function* is identical to Lab 01's; only the decoration is new.

**3. The graph.** Build a `StateGraph(MessagesState)` with two nodes (`call_model`, `tools`) and the standard `tools_condition` routing. Run it on the three test queries. Compare the trace to Lab 01's.

**4. What did we gain?** Quick discussion: explicit state, replay-safe reducers, structured node boundaries. Brief — the [`agents-vs-frameworks.md`](../../concepts/agents/agents-vs-frameworks.md) page does this systematically.

**5. Add a checkpointer.** Compile with `InMemorySaver`. Run with a `thread_id`. Inspect the checkpoint. Simulate a "process restart" by building a fresh graph instance and resuming from the same `thread_id`. Confirm the state is recovered.

**6. The `create_agent` shortcut.** Build the same agent with `from langchain.agents import create_agent` — one line instead of a graph definition. Discuss when this is appropriate (most simple cases) and when raw `StateGraph` is better (custom state, custom routing).

**7. Human-in-the-loop.** Add a `human_approval` node that calls `interrupt(...)` before destructive operations. Run a query that triggers it. Resume with approval, run again and resume with rejection. **This is where the framework's value becomes obvious** — building this on top of the Lab 01 loop would require reimplementing the persistence layer.

**8. (Stretch) Streaming intermediate state.** Use `graph.stream(...)` to observe each node's output as it runs. Useful when you want to display the agent's reasoning live in a UI.

## What we *don't* do in this lab

A short anti-scope, to keep the lab honest:

- **No `langgraph-supervisor` or `langgraph-swarm`.** Multi-agent topologies are Path 03. We stay single-agent here.
- **No LangSmith integration.** Tracing is a Path 06 topic.
- **No production-grade checkpointer (Postgres/SQLite).** `InMemorySaver` is enough to demonstrate the *concept* of persistence; production storage is a deployment concern, not a framework concern.
- **No deep custom state schema.** We use the prebuilt `MessagesState`. Custom `TypedDict` states are a footnote.

This is intentional. The headline of the lab is "what does the framework actually add over from-scratch?" — adding more surface area dilutes the answer.

## Common gotchas

A few things that catch people on the first run:

- **Forgot the checkpointer.** `interrupt()` won't work without one. The error message is clear if you read it, but it's easy to miss the first time.
- **`thread_id` matters.** Two invocations with different `thread_id`s are independent runs. Two with the same `thread_id` continue the same run. Mix them up and you'll be confused about what state you're seeing.
- **`MessagesState` is a TypedDict, not a Pydantic model.** If you're used to passing Pydantic models around, you'll be surprised. State *values* can be anything serializable; the state *container* must be a TypedDict in `create_agent`. With raw `StateGraph` you have more flexibility, but `MessagesState` is the friendly default.
- **`create_react_agent` still works** — but it's deprecated as of LangGraph 1.0. Use `langchain.agents.create_agent` in new code. The snapshot page explains the migration.
- **The graph's `compile()` step is what produces a runnable.** Building the graph is just construction; nothing runs until you call `.invoke(...)` or `.stream(...)` on the compiled graph.

## Solution discussion

A reference implementation will land in [`solution/lab.ipynb`](./solution/lab.ipynb) in a follow-up batch. Two design choices worth flagging:

- **We deliberately don't optimize the graph code.** The lab's graph is verbose because it's instructive — every edge is explicit. A real production graph would use `create_agent` for the simple case and only drop down to `StateGraph` for parts that need custom control.
- **The human approval gate is a tool-level interrupt, not a node-level one.** That is, the `interrupt()` call lives inside a tool definition that triggers on destructive arguments, not in a separate "approval" node before tool execution. Both patterns are valid; the tool-level form keeps the graph topology simpler at the cost of putting more logic inside the tool. We discuss the tradeoff in step 7.

## 🧮 Going deeper

- 🧮 [Agents as policies](../../math-foundations/04-agents-as-policies.md) — the framework doesn't change $\pi_\theta$. It changes how you implement $s_{t+1} = f(s_t, a_t, o_t)$.
- 📖 [Tool design](../../concepts/tools/tool-design.md) — the framework also doesn't fix bad tools.

## ✅ Check your understanding

After finishing the lab, take the quiz:

- 🧠 [`quizzes/foundations/langgraph-basics.md`](../../quizzes/foundations/langgraph-basics.md) — 8 questions on what LangGraph adds, not its syntax.

If you score below 6/8, re-read the framework-comparison page and skim the relevant sections of the lab. The questions are designed to test conceptual understanding, not API memorization.

## What comes next

You've now built the same agent twice (from scratch in Lab 01, in LangGraph here). The Foundations path is complete. From here:

- **Lab 03** (forthcoming) — multi-step research agent with a real search backend.
- **Path 02 — Agentic RAG** — retrieval as a tool. The from-scratch and LangGraph patterns both transfer cleanly.
- **Path 03 — Multi-Agent Systems** — when one agent isn't enough. This is where `langgraph-supervisor` and `langgraph-swarm` show up.
- **Path 06 — Evaluation & Observability** — once your agents are doing real work, you need to know what they're doing. LangSmith integrates here.
