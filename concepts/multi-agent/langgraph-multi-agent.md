# LangGraph multi-agent: the primitives

> ⏱ ~15 min · 🟡 Intermediate · Prerequisites: Labs 10-13 (the from-scratch multi-agent labs), [Lab 05](../../labs/05-langgraph-rewrite/) for single-agent LangGraph familiarity

This is the framework-bridge framing page. Labs 10-13 built supervisor-worker, generator-critic, plan-and-execute, and multi-agent RAG from scratch with `chat_with_tools` + structured envelopes + bounded step caps. This page introduces LangGraph's multi-agent primitives, maps each one to a from-scratch concept you already understand, and identifies where the framework changes the implementation and where the from-scratch version is sufficient.

The next page, [when frameworks earn complexity](./when-frameworks-earn-complexity.md), draws the boundary: which problems benefit from LangGraph, and which are well-served by the patterns you already have.

## The primitives, mapped to from-scratch concepts

LangGraph's multi-agent surface area is small. Five primitives carry most of the weight:

| LangGraph primitive | From-scratch analog (Path 03) | What the framework adds |
|---|---|---|
| `StateGraph` + custom `TypedDict` state | The supervisor's `messages: list[dict]` plus side-state (dedup sets, refinement counters) | Schema-checked state with reducers; nodes see only state, not free-form message history |
| `Command(goto=..., update=..., graph=...)` | The supervisor's tool-call dispatch + structured-error envelope return | Combined control-flow + state-update in one return value; cross-graph navigation |
| `Send(node, state)` | Manual `ThreadPoolExecutor.submit(...)` with `as_completed` | Runtime-determined parallel dispatch; LangGraph handles the join + state merge |
| Sub-graphs | Functions calling worker functions (Lab 10's `researcher_agent` inside the supervisor) | First-class hierarchical composition; sub-graph state can be isolated from parent |
| Checkpointer (`InMemorySaver`, `SqliteSaver`, ...) | Nothing — Lab 10-13 don't persist state across runs | State persistence across process restarts; resume-from-crash; time-travel debugging |

The from-scratch labs cover the *patterns* (when to use a supervisor, how a critic refines, how a planner emits a structured plan). LangGraph covers the *plumbing* (how state moves between nodes, how parallel dispatch works, how to persist a multi-step orchestration). The two are complementary; mapping primitives to patterns is what this page is for.

### `StateGraph` and the state schema

The from-scratch supervisor carries state as a `messages` list plus side-state in closures (`seen_actions: set[str]`, `refinement_cycles_used: int`). LangGraph asks you to declare state explicitly:

```python
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages

class SupervisorState(MessagesState):
    """State carried through the supervisor graph.

    Inherits 'messages: Annotated[list, add_messages]' from MessagesState.
    """
    last_worker: str | None  # which worker just finished
    seen_actions: set[str]   # dedup set, carried explicitly
```

What you gain: every node sees the same state shape. The state schema documents what flows through the graph. Reducers like `add_messages` make it easy to append without clobbering. What you trade away: state evolution becomes a schema change. Adding a new field means updating the `TypedDict`, possibly migrating checkpointed state, and updating every node that touches state. For a stable agent, this is a one-time cost. For a rapidly-iterating prototype, the from-scratch pattern (just add another local variable) moves faster.

### `Command` — combined control flow and state update

The from-scratch supervisor returns tool results to the LLM and lets the LLM emit the next decision. LangGraph nodes return `Command` objects that carry both *where to go next* and *what to update in state*:

```python
from langgraph.types import Command
from typing import Literal

def supervisor_node(state: SupervisorState) -> Command[Literal["researcher", "writer", "__end__"]]:
    # ... call LLM, get next-worker decision ...
    if next_worker == "researcher":
        return Command(
            goto="researcher",
            update={"last_worker": "supervisor"},
        )
    return Command(goto="__end__")
```

The `Literal[...]` type annotation tells LangGraph (and the type checker) which nodes this one can route to. The `goto` is the routing decision; the `update` is the state change. Both happen atomically — there's no window where state has been updated but routing hasn't, or vice versa.

What you gain over the from-scratch pattern: routing decisions are visible at the graph level, not buried in tool-call inspection. The `Command(goto=..., graph=Command.PARENT)` form lets a sub-graph node return control to its parent — the building block for hierarchical composition. What you trade away: control-flow that depends on inspecting the full message history (a pattern the from-scratch supervisor uses naturally) becomes harder to express. You end up duplicating state into custom fields that nodes can read directly.

### `Send` — runtime-determined parallel dispatch

This is the primitive that has no clean from-scratch equivalent.

Lab 12's plan-and-execute dispatches steps to a `ThreadPoolExecutor`:

```python
# Lab 12 (from-scratch): manual thread pool, manual completion tracking
with ThreadPoolExecutor(max_workers=MAX_PARALLEL_EXECUTORS) as pool:
    while True:
        ready = _ready_steps(plan, completed, failed_steps, in_flight)
        for step in ready:
            in_flight.add(step.id)
            futures.append(pool.submit(_run_step, step))
        # ... join + merge logic ...
```

The dispatch logic is ~30 lines: tracking `in_flight`, `completed`, `failed`, computing ready steps, joining futures, merging results back into shared state under a `threading.Lock`.

LangGraph's `Send` collapses this:

```python
from langgraph.types import Send

def dispatcher_node(state: PlanState) -> list[Send]:
    """Return one Send per ready step. LangGraph dispatches them in parallel
    and aggregates results back into state via the configured reducer."""
    ready = _ready_steps(state["plan"], state["completed"])
    return [Send("executor", {"step": s, "deps": _deps_for(s, state)})
            for s in ready]
```

The dispatcher node returns a list of `Send` objects. LangGraph runs them concurrently (within a single "superstep") and the results merge back into state via the reducer declared on the state field. The dispatch loop becomes a graph topology declaration.

What you gain: ~30 lines of manual thread-pool plumbing reduces to ~5 lines of `Send` returns. The parallel dispatch is visible in the graph; race conditions are handled by the framework's reducer contract. What you trade away: the bounded-pool concurrency cap (`max_workers=3` in Lab 12) becomes a configuration concern at compile time (`StateGraph.compile()` accepts limits) rather than something visible at the dispatch site. For agents that need fine-grained pool control, you fall back to manual dispatch inside a node anyway.

The `Send` primitive is the strongest single argument for using LangGraph in multi-agent settings. Lab 15 demonstrates it directly.

### Sub-graphs

The from-scratch pattern composes workers as functions called from inside the supervisor's tool-dispatch loop. The supervisor sees only the worker's return envelope. Sub-graphs make this composition first-class:

```python
# Define worker sub-graph
worker_subgraph = StateGraph(WorkerState)
worker_subgraph.add_node("plan", plan_worker)
worker_subgraph.add_node("execute", execute_worker)
# ... edges ...
worker_compiled = worker_subgraph.compile()

# Use as a node in the parent graph
parent = StateGraph(SupervisorState)
parent.add_node("worker_pool", worker_compiled)
```

The worker sub-graph has its own state schema (`WorkerState`). The parent passes state in; the sub-graph runs to completion; the sub-graph's terminal state maps back into the parent's state via configured mapping.

What you gain: hierarchical agents become a topology concern, not a code-organization concern. Each layer can have its own state schema and its own bounded execution. What you trade away: debugging gets harder. A failure in a sub-graph's terminal node surfaces in the parent as a state update; tracing back to the actual failing line means walking through the sub-graph's compile output. Tooling helps (LangSmith, LangGraph Studio); without those, the abstraction can hide as much as it reveals.

### Checkpointer

The from-scratch labs don't persist state. Each run starts fresh; if the process crashes mid-research, the partial progress is lost. The checkpointer changes this:

```python
from langgraph.checkpoint.memory import InMemorySaver

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "user-42-session-7"}}

# Run — state persists under thread_id
graph.invoke({"messages": [...]}, config=config)

# Process dies. Restart. Resume from where we left off:
graph.invoke(None, config=config)  # None = "continue from checkpoint"
```

What you gain: a multi-step orchestration that takes 30 seconds is no longer destroyed by a transient API failure. Human-in-the-loop interruption becomes natural (`interrupt()` pauses; `Command(resume=...)` continues). Time-travel debugging works: you can replay a session from any prior checkpoint and try a different decision. What you trade away: minimal — the checkpointer is opt-in. The `InMemorySaver` is trivial to add. Production checkpointers (`SqliteSaver`, `PostgresSaver`) require infrastructure but the API is the same.

The checkpointer is the second strongest argument for using LangGraph. Lab 14 demonstrates it for the supervisor pattern.

## The three multi-agent topologies LangGraph names

LangGraph's documentation names three multi-agent topologies. Each maps to a different shape of from-scratch coordination:

### Supervisor

A central orchestrator that decides which worker runs next. Each worker returns to the supervisor; the supervisor decides the next step or finalizes. This is what Labs 10/11/13 implement from scratch and what Lab 14 rebuilds in LangGraph.

When it fits: one orchestrator can sensibly own routing decisions. Most multi-agent workloads start here.

### Swarm

No central orchestrator. Agents hand off control directly to each other using `Command(goto=..., graph=Command.PARENT)` returned from handoff tools. The first agent to receive a request handles it or hands off to whichever specialist is appropriate. State is shared via the parent graph's state.

When it fits: routing decisions are simple and local (each agent knows when it should hand off). Saves the supervisor's LLM call on every routing decision. Lab 14 introduces the building blocks (`Command(goto=..., graph=Command.PARENT)` and handoff tools); building a full swarm is left as an extension exercise.

### Hierarchical (supervisor-of-supervisors)

Sub-graphs all the way down. A top-level supervisor routes to mid-level supervisors, each of which manages its own team of workers. The structure is a tree.

When it fits: the workload genuinely decomposes into specialized teams. Overkill for most applications — if you have fewer than ~10 specialist workers, a flat supervisor is simpler. This pattern is introduced conceptually in Lab 14's README but not built; the building block (sub-graph composition via `parent.add_node("team_a", team_a_compiled)`) is the same one used in Lab 15.

## What carries over unchanged from the from-scratch labs

Three things matter as much in LangGraph as they did from scratch:

- **The supervisor's system prompt.** The four retrieval-decision rules from Lab 13, the five planner-prompt rules from Lab 12, the critic's five issue kinds from Lab 11 — none of these change because of the framework. Prompt engineering is the same problem at the framework level as at the from-scratch level.

- **Citation preservation across handoffs.** Lab 13's discipline ("supervisor passes chunks verbatim; synthesizer cites by chunk_id") applies identically in a LangGraph implementation. The state schema makes it slightly easier to enforce (chunks live in a typed field, not in free-form messages), but the discipline is the same.

- **The five planner-prompt rules from Lab 12.** Atomic steps, explicit dependencies, well-formed parallel groups, self-contained descriptions, bounded plans. The planner is an LLM call regardless of framework; the rules apply the same way.

This matters for the framework comparison. If LangGraph made the supervisor's job dramatically easier, you would expect the supervisor's prompt to shrink. It does not. The framework moves the implementation of *plumbing* — state passing, parallel dispatch, persistence. It does not move the implementation of *coordination logic* — that lives in prompts and structured payloads either way.

## When this page's mapping breaks down

Three places where the analogy between primitives and from-scratch concepts becomes loose:

- **`Command(goto=..., graph=Command.PARENT)` for cross-graph navigation.** No from-scratch analog. Used in swarm patterns and in worker sub-graphs that need to escape to the parent.
- **Conditional edges with `add_conditional_edges(...)` and a routing function.** Similar in shape to the from-scratch supervisor's "decide next step" prompt, but lives in code, not in an LLM prompt. Used for deterministic routing decisions (e.g., "if `state['error_count'] > 3`, go to escalation node").
- **The `interrupt()` primitive for human-in-the-loop.** Lab 05 introduces this for the single-agent case. In multi-agent settings it can be placed at any node — useful for approval gates between supervisor decisions and worker dispatch.

These don't have clean from-scratch equivalents because they exist specifically because the framework has a graph topology and state persistence. They're framework-native primitives, not framework versions of from-scratch patterns.

## Related concepts

- The boundary discussion: [when frameworks earn complexity](./when-frameworks-earn-complexity.md).
- The from-scratch baselines: [supervisor-worker pattern](./supervisor-worker-pattern.md), [generator-critic pattern](./generator-critic-pattern.md), [planner-executor pattern](./planner-executor-pattern.md), [retriever-as-worker](./retriever-as-worker.md).
- The single-agent framework bridge for comparison: [agents vs frameworks](../agents/agents-vs-frameworks.md), Path 02's Lab 05.

## References

- LangGraph docs, ["Multi-agent systems"](https://langchain-ai.github.io/langgraph/concepts/multi_agent/) — the official taxonomy of supervisor / swarm / hierarchical.
- LangGraph docs, ["Send API"](https://langchain-ai.github.io/langgraph/how-tos/map-reduce/) — the canonical parallel-dispatch primitive.
- LangGraph docs, ["Subgraphs"](https://langchain-ai.github.io/langgraph/how-tos/subgraph/) — how state passes between parent and sub-graph.
- LangGraph docs, ["Checkpointers"](https://langchain-ai.github.io/langgraph/concepts/persistence/) — state persistence across runs.
- LangChain blog, ["LangChain & LangGraph 1.0"](https://blog.langchain.com/langchain-langgraph-1dot0/) — the 1.0 GA announcement and stability contract.
- [`langgraph-supervisor` package README](https://github.com/langchain-ai/langgraph-supervisor-py) — recommends using the manual supervisor-via-tools pattern (the one Lab 14 demonstrates) rather than the `create_supervisor()` helper for new code.
