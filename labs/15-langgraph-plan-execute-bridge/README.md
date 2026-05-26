# Lab 15 — LangGraph plan-and-execute bridge

> ⏱ 120-150 min · 🟡 Intermediate · Prerequisites: Lab 12 (the from-scratch baseline this lab rebuilds), Lab 14 (LangGraph supervisor familiarity)

Rebuild [Lab 12's planner-executor pattern](../12-plan-and-execute-from-scratch/) in LangGraph. The strong framework value case. Lab 12 implemented dynamic parallel dispatch with a manual `ThreadPoolExecutor` + completion tracking + `threading.Lock`; LangGraph replaces this with the `Send` primitive — a runtime-determined dispatcher that LangGraph natively supports.

The `Send` primitive is where LangGraph visibly earns its complexity for multi-agent work. The dispatch loop that took ~30 lines in Lab 12 becomes ~5 lines here.

> 📖 The framing pages for this lab:
> [LangGraph multi-agent: the primitives](../../concepts/multi-agent/langgraph-multi-agent.md),
> [when frameworks earn complexity](../../concepts/multi-agent/when-frameworks-earn-complexity.md).
> 🧠 Calibrate against the [framework bridge quiz](../../quizzes/multi-agent/framework-bridge.md).
> ⬅️ Compare line-by-line against [Lab 12 solution](../12-plan-and-execute-from-scratch/solution/README.md).

## What you'll build

A LangGraph plan-and-execute system with the same capability as Lab 12:

- `PlanStep` and `Plan` Pydantic schemas (same as Lab 12 — schemas don't change).
- Planner node that emits a JSON-validated `Plan`. Same five planner-prompt rules as Lab 12.
- Plan validator that runs Kahn's algorithm for cycle detection + four other checks (same as Lab 12).
- Dispatcher node that emits `list[Send]` for ready parallel steps — the framework value-add.
- Executor sub-graph that runs one step with anti-improvement enforcement.
- Synthesizer node that composes the final answer from completed step results.
- Replanner integration that uses `Command(goto="planner")` to drive bounded replanning (`MAX_REPLANS = 2`).
- Checkpointer for plan-state persistence across replan cycles.

Same `MAX_PLAN_STEPS = 8`, `MAX_PARALLEL_EXECUTORS = 3` (mapped to LangGraph's parallel-dispatch model), `EXECUTOR_MAX_STEPS = 4`, `MAX_REPLANS = 2` as Lab 12. The constants don't change because the patterns don't change — only the dispatch mechanism does.

## Goal

By the end of the lab you should be able to:

- Use the `Send` primitive to dispatch a runtime-determined number of parallel sub-graph invocations.
- Recognize when `Send` is the right tool (dynamic parallel dispatch with state merge via reducers) and when it isn't (fine-grained pool control, custom thread-pool sizing per step).
- Build a sub-graph as a node in a parent graph. Pass state in via shared keys; receive state back via the sub-graph's terminal state.
- Compose plan validation, dispatch, and replanning in LangGraph using `Command(goto=...)` for replan navigation.
- Reason about the trade-offs: ~30 lines of manual thread-pool code is replaced by ~5 lines of `Send` returns, but the bounded-concurrency cap becomes implicit rather than explicit at the dispatch site.
- Recognize that the planner's prompt, the plan validation logic, and the synthesizer's prompt all carry over from Lab 12 unchanged. The framework changes the dispatcher and nothing else.

## Prerequisites

- **Lab 12** — the from-scratch plan-and-execute pattern. Lab 15 is a *re-build* of Lab 12's dispatcher. If you haven't built Lab 12, this lab will hide the parts that matter most. Don't skip it.
- **Lab 14** — LangGraph supervisor familiarity. `StateGraph`, `Command`, sub-graphs, checkpointer. Lab 15 assumes you've seen these.
- **Concept pages** — [LangGraph multi-agent: the primitives](../../concepts/multi-agent/langgraph-multi-agent.md) (the `Send` section in particular) and [when frameworks earn complexity](../../concepts/multi-agent/when-frameworks-earn-complexity.md).

## Setup

Same Python 3.11+ environment as Lab 14. No additional packages beyond what Lab 14 installed.

## Tools and versions

Same as Lab 14. See [the snapshot page](../../tools/langgraph/snapshot-v1.0.md) for the full pinned API surface.

## Structure

Roughly 28-32 cells. Output-stripped. Each step pairs a markdown cell explaining the from-scratch → framework mapping with a code cell implementing it.

- **Step 0**: Setup. Same as Lab 14.
- **Step 1**: The Lab 12 baseline (for reference). One paragraph reminder of what we're rebuilding.
- **Step 2**: `PlanStep` and `Plan` Pydantic schemas — unchanged from Lab 12.
- **Step 3**: `Plan.validate_graph()` — unchanged from Lab 12 (Kahn's algorithm + four other checks).
- **Step 4**: State schema. `PlanState(TypedDict)` with `plan`, `completed: Annotated[dict, _merge_results]`, `failed`, `replan_count`. The reducer is what enables parallel updates from `Send`-dispatched executors.
- **Step 5**: Planner node. Same prompt as Lab 12; emits JSON; validates; retries on validation error.
- **Step 6**: Executor sub-graph. One node, anti-improvement enforcement (`tc.name == step.tool`), supports the `cannot_execute` structured signal.
- **Step 7**: Dispatcher node — the framework value-add. Computes ready steps; returns `list[Send]` to launch them in parallel. ~5 lines, replacing Lab 12's ~30 lines of `ThreadPoolExecutor` + `threading.Lock` plumbing.
- **Step 8**: Synthesizer node. Same prompt as Lab 12.
- **Step 9**: Replanner integration. A node that decides between three outcomes: (a) all done → `Command(goto="synthesize")`, (b) failures present + replans remaining → `Command(goto="planner", update={...failure_context...})`, (c) cap fired → `Command(goto="synthesize", update={"status": "partial_after_cap"})`.
- **Step 10**: Wire the graph. `planner → dispatcher → executor (parallel) → replanner → synthesize`. Compile with a checkpointer so multi-replan state persists.
- **Step 11**: Run end-to-end on a compound query that triggers parallel dispatch. Compare wall-clock to a sequential baseline.
- **Step 12**: Line-by-line comparison with Lab 12's solution. What got shorter (the dispatcher), what stayed the same (planner, validator, synthesizer), what changed shape (replanner from a Python loop to a graph edge).

## The line-by-line comparison

The lab's closing step is an explicit comparison of code by section:

| Component | Lab 12 (from-scratch) | Lab 15 (LangGraph) | Net change |
|---|---|---|---|
| Plan/PlanStep schemas | ~30 lines (Pydantic StrictModel) | ~30 lines (unchanged) | No change |
| `validate_graph` | ~50 lines (Kahn + 4 checks) | ~50 lines (unchanged) | No change |
| Planner prompt | ~50 lines (five rules) | ~50 lines (unchanged) | No change |
| Planner retry loop | ~25 lines | ~15 lines (graph edge replaces explicit loop) | Framework wins ~10 lines |
| Executor agent | ~40 lines (anti-improvement, `tc.name == step.tool`) | ~40 lines (sub-graph node, same logic) | No change |
| **Dispatcher** | **~70 lines** (`ThreadPoolExecutor` + `threading.Lock` + `_ready_steps` + completion tracking) | **~10 lines** (`return [Send("executor", ...) for s in ready]`) | **Framework wins ~60 lines** |
| Replanner | ~25 lines (Python loop + `_plan_signature` dedup) | ~20 lines (`Command(goto="planner")` from a node) | Framework wins ~5 lines |
| Synthesizer prompt | ~25 lines | ~25 lines (unchanged) | No change |
| Checkpointer / persistence | Not implemented | ~5 lines (`InMemorySaver`) | Framework adds capability |

The dispatcher is the dominant savings. ~70 lines of manual concurrency code reduces to ~10 lines of `Send` returns. The reducer on the `completed` state field handles the merge that Lab 12 needed `threading.Lock` for.

## What to watch for

Five practical issues:

**1. `Send` payloads must be self-contained.** Each `Send("executor", payload)` carries its own state to the executor sub-graph. The sub-graph sees only what you put in the payload, not the parent's full state. Forgetting to include a step's `depends_on` outputs in the payload is the most common Lab-15 mistake — the executor runs with missing inputs and emits `cannot_execute`.

**2. Reducers on parallel-update fields are required.** The `completed` state field must have a reducer (e.g., `operator.add` for lists or a custom dict-merger for dicts). Without one, parallel `Send` executors clobber each other's updates and only the last write survives. This is a silent bug — your tests pass; production data goes missing.

**3. The bounded-concurrency cap is implicit.** Lab 12 set `MAX_PARALLEL_EXECUTORS = 3` directly on the `ThreadPoolExecutor`. LangGraph's `Send` doesn't have a per-superstep concurrency cap exposed at the dispatch site. If you absolutely need to bound concurrency to N, you batch the `Send` returns yourself (return at most N `Send` objects per superstep). For most workloads this isn't necessary because the LLM provider's rate limits are the real bound.

**4. `Command(goto="planner", update={...})` for replanning.** The replanner is no longer a Python `while` loop — it's a node that returns `Command(goto="planner")` to navigate back. The `update` field carries failure context that the planner reads on its next invocation. This is cleaner topologically but means the planner node must handle "first call" and "replan call" cases in its input parsing.

**5. State debugging is harder for parallel executors.** When five `Send` dispatches run in parallel and one fails, the state snapshot shows the merged result — you don't directly see which executor produced which output without inspecting `graph.stream(...)` events. `astream_events()` with the `on_chain_end` filter is the workaround; LangSmith makes it visual.

## Anti-scope

- **Distributed `Send` dispatch.** `Send` runs in-process; for distributed execution across machines, you'd reach for LangGraph Cloud or a custom worker pool. Out of scope.
- **Lab 13 (multi-agent RAG) framework rewrite.** Composes this lab + retrieval-pipeline-as-node. Mentioned in the concept page as future work.
- **Critic-on-plan or critic-on-synthesis.** The Lab 11 critic pattern is framework-agnostic; you'd add it as a node between dispatcher and synthesizer. Mentioned in the concept page as an extension exercise.
- **Production observability via LangSmith.** Out of scope for the labs; mentioned in the concept page.
- **`langgraph-supervisor` package.** Same as Lab 14 — deprecated for new code; we don't use it.

## Run-time and cost

Per end-to-end run on the demo task:

- 1 planner call (emits the plan; 2-5 seconds)
- 1 executor call per step (plans are typically 3-5 steps)
- 0-2 replanner calls (only on failure)
- 1 synthesizer call

Total: 6-12 LLM calls per task, ~$0.04-$0.08 at gpt-4o-mini rates. Wall-clock dominated by `fetch_page` in executor steps; with `Send` dispatching 3 parallel fetches, a 3-fetch group runs in ~3-4 seconds wall-clock vs ~12 sequentially. Typical end-to-end: 10-25 seconds.

## Solution

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) with notes in [`solution/README.md`](./solution/README.md). 25 cells vs the lab's 32 — the dispatcher transformation walkthrough and the wall-clock parallel-vs-sequential comparison are condensed; the planner → dispatch → executors → replanner → synthesize path reads end-to-end. Two design decisions worth flagging up front:

- **The dispatcher is the only thing that materially changes shape.** Everything else from Lab 12 (planner, validator, executor, synthesizer) ports nearly verbatim. The framework value lives in the dispatcher transformation.
- **The replanner becomes a graph edge, not a Python loop.** This is cleaner topologically but moves the replan-state bookkeeping into the state schema. The plan-signature dedup from Lab 12 lives in a state field; the `Command(goto="planner")` decision uses it.

## Next

- After completing the lab, take the [framework bridge quiz](../../quizzes/multi-agent/framework-bridge.md).
- This concludes Path 03's framework-bridge module. The next planned module (Module 6) extends Lab 09's evaluation harness for multi-agent: trajectory-level metrics, plan-quality scores, replan rate, citation preservation rate.
