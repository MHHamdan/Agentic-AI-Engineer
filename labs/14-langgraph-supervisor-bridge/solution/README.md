# Lab 14 · Reference solution

The polished final implementation of [Lab 14: LangGraph supervisor bridge](../README.md).

Rebuilds [Lab 10's supervisor-researcher-writer pattern](../../10-supervisor-worker-from-scratch/solution/README.md) in LangGraph using the manual supervisor-via-tools approach. Same worker contracts, same prompts; the framework absorbs the dispatch plumbing.

> 📖 The concept pages that frame this implementation:
> [`langgraph-multi-agent`](../../../concepts/multi-agent/langgraph-multi-agent.md),
> [`when-frameworks-earn-complexity`](../../../concepts/multi-agent/when-frameworks-earn-complexity.md).
> 🧠 Calibrate against the [framework bridge quiz](../../../quizzes/multi-agent/framework-bridge.md).
> ⬅️ Compare line-by-line against [Lab 10 solution](../../10-supervisor-worker-from-scratch/solution/README.md).

## What this solution implements

The headline path from the parent lab:

- Provider-agnostic chat model via `init_chat_model` (works against OpenAI or Anthropic; same interface throughout Path 03).
- `SupervisorState(MessagesState)` — TypedDict extending `MessagesState`. Adds `findings: str`, `citations: list[dict]`, `brief_status: str`, `final_answer: str`, `last_worker: str`. Pydantic state isn't supported by `create_agent`; the TypedDict is the LangGraph constraint, not a stylistic choice.
- Researcher worker: `create_agent(model, tools=[web_search, fetch_page], prompt=...)` — LangGraph prebuilt provides the agent loop. Web tools include action-hash dedup carried verbatim from Lab 10.
- Writer worker: prompt-only `llm.invoke()` — no tool loop needed. Same prompt + citation discipline as Lab 10.
- Supervisor as a manual node, NOT `create_supervisor()`. Calls an LLM bound to two routing tools (`call_researcher`, `call_writer`); returns `Command(goto=..., update={...})` based on which tool the LLM picked.
- Researcher and writer wrapper nodes that translate state ↔ sub-agent messages.
- Graph wired with `StateGraph(SupervisorState).add_node("supervisor", supervisor_node).add_node("researcher", researcher_node).add_node("writer", writer_node).add_edge(START, "supervisor").compile()`.
- `InMemorySaver` checkpointer for the graph build (resumable runs).
- One end-to-end demonstration via `graph.invoke({"messages": [HumanMessage(content=task)]}, config={"thread_id": "demo", "recursion_limit": 12})`.

**Not in this solution** (deliberately): the Lab 10 baseline recap (parent Step 1), the streaming demonstration (parent Step 11), the `Command.PARENT` swarm building-block (parent Step 12), the line-by-line comparison table against Lab 10 (parent Step 13). Those are pedagogy; the solution is the canonical mechanism.

## Implementation choices

### Five design decisions worth flagging

**1. Manual supervisor via tool-calling, not `create_supervisor()`.** Per LangChain's current upstream guidance and the `langgraph-supervisor` deprecation note. The reason isn't aesthetic — `create_supervisor()` hides the routing logic in a way that makes mid-task customization (add a critic worker, change routing rules, support replanning) far more invasive than rebuilding the supervisor from scratch. The pattern here is the recommended one for new code as of 2026.

**2. State extends `MessagesState`, not Pydantic `StrictModel`.** `create_agent` (LangGraph prebuilt) doesn't support Pydantic state; the TypedDict approach is the framework constraint. Inside the supervisor and worker nodes we're back to `state["messages"]` access patterns. Trade-off vs Lab 10: from-scratch could use Pydantic; the framework couldn't.

**3. Routing tools are stubs.** `call_researcher` and `call_writer` are decorated `@tool` functions that return placeholder strings. They never actually execute as tools — the supervisor node *intercepts* the LLM's tool call to decide where to route. The `@tool` decoration exists so `bind_tools()` knows their schema. If you wired this without the stub tools, you'd have to hand-craft JSON schemas, which is more code.

**4. `recursion_limit=12`.** Maps Lab 10's `SUPERVISOR_MAX_STEPS=6` (supervisor's own loop) plus per-worker step caps (researcher up to 6, writer 1 invocation). LangGraph's `recursion_limit` counts *every* node visit, including the researcher's internal agent-loop steps inside its sub-agent. 12 is empirical; tune up if researcher needs more steps, tune down to surface budget overruns earlier.

**5. Action-hash dedup lives in the researcher's `web_search` / `fetch_page` tools, not in the graph.** Same Lab 10 pattern: dedup is a tool-level concern, not a routing concern. When `create_agent` invokes the tool a second time with identical args, the action-hash returns the cached result without re-hitting the network. The framework doesn't need to know.

## Common variations that also work

**Pydantic-state via a custom graph.** If you skip `create_agent` and roll your own researcher node, you can use Pydantic state throughout. Trade-off: more code, but typed access everywhere. Generally not worth it unless you have a specific Pydantic-validator need.

**Multi-tool supervisor (more than two workers).** Add more `@tool`-decorated stub functions, more `Command(goto=...)` branches in the supervisor node. Lab 11's three-worker (researcher + writer + critic) pattern maps directly — see the parent README for the extension.

**Different checkpointer backends.** `InMemorySaver` is for development. `SqliteSaver` (in `langgraph-checkpoint-sqlite`) for single-process persistence; `PostgresSaver` (in `langgraph-checkpoint-postgres`) for multi-process or production. The graph build code doesn't change — just the checkpointer instance.

**Streaming via `graph.stream(stream_mode="updates")`.** Mentioned in the parent Step 11. Useful for showing intermediate routing decisions in a UI. The solution uses `graph.invoke` for the synchronous case; switching to `stream()` is one line.

## Running the solution

```bash
cd labs/14-langgraph-supervisor-bridge/solution
# Set provider env vars (OPENAI_API_KEY or ANTHROPIC_API_KEY)
jupyter notebook lab.ipynb
```

Expected wall-clock: **15-30 seconds** depending on `web_search` and `fetch_page` latency. Dominated by live web calls in the researcher.

Cost: **~$0.005-0.01** at gpt-4o-mini rates (one supervisor LLM call per routing decision + the researcher's internal agent-loop calls + one writer call).
