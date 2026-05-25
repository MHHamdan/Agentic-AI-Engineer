# Lab 15 · Reference solution

The polished final implementation of [Lab 15: LangGraph plan-and-execute bridge](../README.md).

Rebuilds [Lab 12's plan-and-execute pattern](../../12-plan-and-execute-from-scratch/solution/README.md) in LangGraph using the `Send` primitive for dynamic parallel dispatch. The strong framework value case: Lab 12's ~70-line manual `ThreadPoolExecutor` + `threading.Lock` dispatcher collapses to ~10 lines of `Send` list-returns plus a reducer.

> 📖 The concept pages that frame this implementation:
> [`langgraph-multi-agent`](../../../concepts/multi-agent/langgraph-multi-agent.md),
> [`when-frameworks-earn-complexity`](../../../concepts/multi-agent/when-frameworks-earn-complexity.md).
> 🧠 Calibrate against the [framework bridge quiz](../../../quizzes/multi-agent/framework-bridge.md).
> ⬅️ Compare line-by-line against [Lab 12 solution](../../12-plan-and-execute-from-scratch/solution/README.md).

## What this solution implements

The headline path from the parent lab:

- Provider-agnostic chat model setup. Same pattern as Lab 14.
- `PlanStep` and `Plan` Pydantic `StrictModel` schemas with `id`, `description`, `tool`, `args`, `depends_on`, `parallel_group` fields — carried verbatim from Lab 12.
- `validate_graph(plan, available_tools)` returns a list of validation errors (cycles via Kahn's algorithm, duplicate IDs, unknown tools, parallel-group violations, unknown deps, self-deps). Identical to Lab 12.
- `PlanState(TypedDict)` with `task`, `plan`, `completed` (Annotated with `_merge_results` reducer), `failed`, `replan_count`, `final_answer`, `status`. The reducer is the framework primitive for handling parallel updates.
- Planner node: emits a `Plan` via Pydantic-validated JSON, validation-then-retry loop on parse failure.
- Executor node: receives a single step + its dependency outputs (not the whole plan; same discipline as Lab 12). `tc.name == step["tool"]` validation prevents the executor from deviating from the planned tool.
- Dispatcher node: returns `[Send("executor", {"step": s, "deps": deps}) for s in ready_steps]`. The framework dispatches each `Send` as a parallel sub-graph invocation; results merge into `state["completed"]` via the reducer.
- Replanner node: routes to `synthesize` if execution is complete, or back to `planner` with failure context if replanning is needed.
- Synthesizer: composes the final answer with citation preservation.
- Graph wired with `StateGraph(PlanState)` + `add_conditional_edges("planner", dispatcher_node, ["executor"])` so the dispatcher's `Send` list-return becomes the next batch of executor invocations.
- One end-to-end demonstration run on a research-and-summarize task.

**Not in this solution** (deliberately): the Lab 12 baseline recap (parent Step 1), plan-signature dedup with `MAX_REPLANS=2` (parent Step 8), the four-failure-mode walkthrough (parent Step 11), the line-by-line comparison table against Lab 12 (parent Step 12). Plan-signature dedup is a Lab 12-specific stretch; the canonical headline path doesn't need it.

## Implementation choices

### Five design decisions worth flagging

**1. The dispatcher transformation is the framework's payoff.** Lab 12's manual `ThreadPoolExecutor(max_workers=3)` + `threading.Lock` + completion tracking ran ~70 lines. The LangGraph version is `return [Send("executor", payload) for s in ready]` — ~10 lines including the ready-step computation. The framework handles dispatch, parallelism, and result merging via the reducer on `completed`. This is the strong value case for `Send`.

**2. The `_merge_results` reducer is non-negotiable.** Without `Annotated[dict, _merge_results]` on `completed`, parallel executor updates would clobber each other (last-write-wins on the whole dict, not per step_id). The reducer merges per-step results so 3 concurrent executors can update without conflict. This is the LangGraph idiom for any state field touched by parallel `Send` invocations.

**3. The executor receives only `{"step": s, "deps": deps_dict}`, not the whole plan.** Same discipline as Lab 12: the executor sees what it needs to execute its step, nothing more. Prevents the executor from "helpfully" anticipating future steps or short-circuiting the dispatcher. The `Send` payload makes this enforceable — it's literally what the executor sees as its state input.

**4. Validation-then-retry stays in the planner node.** The Pydantic-validate + `validate_graph` + retry-on-error loop is the same code from Lab 12. The framework doesn't change *what* validation does — only *where* the planner sits in the graph. If you wanted retry-as-graph-edge (a recursive edge back to `planner`), you could; the in-node retry is simpler and works well for the bounded retry case.

**5. Plan-signature dedup omitted in canonical solution.** Lab 12 uses a `plan_signature_history` to escalate identical-plan replans to `partial_after_cap` — preventing replanning thrash. This is a Lab 12-specific protection that's most valuable when replans are common. The canonical Lab 15 solution sticks to the headline path: planner → dispatch → executors → replanner → synthesize. Adding dedup is a 5-line extension; see Lab 12's solution for the pattern.

## Common variations that also work

**Replanner-as-graph-edge.** Instead of a `replanner_node` that returns `Command(goto="planner" | "synthesize")`, you can wire `add_conditional_edges("replanner", lambda s: "planner" if needs_replan(s) else "synthesize", ["planner", "synthesize"])`. Same behavior, slightly more graph-native. The node-with-Command approach reads more linearly; pick by team preference.

**Streaming the dispatcher's parallel executions.** `graph.stream(stream_mode="updates")` surfaces each executor's completion as a separate update. Useful for showing parallel progress in a UI. The solution uses `invoke` for synchronous demonstration.

**Larger `max_workers` via `Send`.** Lab 12's `MAX_PARALLEL_EXECUTORS = 3` is hardcoded in `ThreadPoolExecutor`. LangGraph's `Send` parallelism is bounded only by the event loop and the LLM provider's rate limits. Empirically, 5-10 concurrent executors is fine for LLM-bound work; beyond that, rate limits dominate and the gain flattens.

**Async-throughout via `graph.ainvoke`.** All LangGraph primitives support async. For high-throughput batch evaluation, async is the path. The synchronous solution is for clarity.

**With the `langgraph-checkpoint-sqlite` checkpointer.** `InMemorySaver` is for development. `SqliteSaver` survives process restarts; useful when plans take minutes to execute and you want crash recovery.

## Running the solution

```bash
cd labs/15-langgraph-plan-execute-bridge/solution
# Set provider env vars (OPENAI_API_KEY or ANTHROPIC_API_KEY)
jupyter notebook lab.ipynb
```

Expected wall-clock: **20-40 seconds** end-to-end, dominated by parallel `fetch_page` calls (3 concurrent, ~1-3 seconds each) and a small number of LLM calls (planner, executors, synthesizer).

Cost: **~$0.005-0.015** at gpt-4o-mini rates (planner + 3-4 executor steps + synthesizer).
