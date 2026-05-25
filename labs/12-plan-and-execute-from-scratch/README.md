# Lab 12 — Plan-and-execute from scratch

> ⏱ 120-150 min · 🟡 Intermediate · Prerequisites: Lab 10, Lab 11, Path 01 Labs 01-03

Build a plan-and-execute system from scratch. A **planner agent** emits a structured `Plan` (a list of typed `PlanStep`s with `depends_on` and `parallel_group` fields). A **supervisor** resolves dependencies and dispatches steps to a bounded **executor pool** (`ThreadPoolExecutor`, max 3 workers). Failures trigger bounded **replanning** (`MAX_REPLANS = 2`). Everything else — chat client, web tools, action-hash dedup, structured-error envelopes — stays unchanged from Labs 10-11.

No new dependencies beyond stdlib (`concurrent.futures.ThreadPoolExecutor` is built-in).

## What you'll build

```
                    user task
                        │
                        ▼
                ┌───────────────┐
                │   planner     │ ← runs once; emits structured Plan
                └───────────────┘
                        │
                        ▼
            Plan {steps: [{id, tool, args, depends_on,
                           parallel_group}, ...]}
                        │
                        ▼
                ┌───────────────┐
                │  supervisor   │ ← dependency resolver + dispatcher
                │  + executor   │   (NOT an LLM-driven router)
                │      pool     │
                └───────────────┘
                  │  │  │  │
              ┌───┘  │  │  └───┐
              ▼      ▼  ▼      ▼
        executor  executor  executor  ← bounded pool (max 3 concurrent)
              │      │  │      │
              └──────┴──┴──────┘
                       │
                       ▼
                  step results
                       │
              ┌────────┴────────┐
              ▼                 ▼
        all succeeded?    any failed?
              │                 │
        synthesize        replan (≤ MAX_REPLANS=2)
              │                 │
              └────────┬────────┘
                       ▼
                  final answer
                  (or honest partial)
```

Four agents:
- **Planner** — one LLM call per plan. Emits JSON-validated `Plan`.
- **Executor** — one LLM call per step. Runs the step's specified tool with its specified args.
- **Supervisor** — orchestrates planning, dispatch, replanning, finalization. Uses `chat_with_tools` for the orchestration plumbing but the dispatch logic itself is Python.
- **Synthesizer** — final-answer composer (a writer-style agent given the original task + all step results).

## Goal

By the end of the lab you should be able to:

- Design a `Plan` schema with explicit `depends_on` and `parallel_group` fields and explain why each matters.
- Implement a planner agent that emits JSON-validated plans following the five planner-prompt rules.
- Build a dependency-resolving dispatcher using `concurrent.futures.ThreadPoolExecutor` with bounded concurrency.
- Wire bounded replanning (`MAX_REPLANS = 2`) with structured failure-context handoff to the planner.
- Read a trace and distinguish a healthy plan-and-execute trajectory from each of the four failure modes (plan brittleness, execution drift, replanning thrash, plan-execution gap).
- Reason about when plan-and-execute beats supervisor-worker (Lab 10) and generator-critic (Lab 11), and when ReAct is the right call instead.

## Prerequisites

- **Lab 10** — the supervisor-worker pattern. Lab 12's supervisor extends Lab 10's dispatch mechanism; the chat client and tool-calling contract are unchanged.
- **Lab 11** — generator-critic with bounded refinement. Lab 12's bounded replanning uses the same discipline (`MAX_REPLANS` instead of `MAX_REFINEMENT_CYCLES`; honest surfacing at the cap).
- **Lab 03** — `web_search` + `fetch_page`. Reused at the executor level.
- **Concept pages** — at minimum [plan-and-execute](../../concepts/multi-agent/plan-and-execute.md) and [planner-executor pattern](../../concepts/multi-agent/planner-executor-pattern.md). The lab references their failure modes and design rules directly.

## Setup

No new dependencies. `concurrent.futures` is in the Python stdlib. Same `.env` setup as Labs 01-11 (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).

## Structure

Roughly 35-40 cells, output-stripped, sample-output markdown cells throughout. The lab is structured so the deltas from Lab 10/11 are visible at each turn.

- **Step 0**: Setup — same as Lab 10/11.
- **Step 1**: Compact recap of Lab 10/11 machinery (chat client, web tools, action-hash dedup, `StrictModel`). Not a re-derivation — just enough to make the deltas in this lab clear.
- **Step 2**: Define the `PlanStep` and `Plan` Pydantic schemas. `StrictModel(extra="forbid")` so the planner can't emit extra fields. Validation method on `Plan` that checks dependency-graph integrity (no cycles, no references to non-existent step IDs, parallel groups are honestly independent).
- **Step 3**: Build the planner agent. System prompt encodes the five planner-prompt rules. The executor's tool registry is passed in so the planner can only emit steps the executor can actually run (closes the plan-execution gap). Output is parsed and validated against `Plan`; validation errors loop back to the planner with the specific failure context.
- **Step 4**: Build the executor agent. One step at a time. Receives `(step, dependency_outputs)`. Tight anti-improvement prompt: "run the specified tool with the specified arguments; if you can't, return `cannot_execute`."
- **Step 5**: Build the dispatch/concurrency layer. `concurrent.futures.ThreadPoolExecutor(max_workers=MAX_PARALLEL_EXECUTORS)`. Dispatch loop: compute ready steps (all `depends_on` complete), submit them to the pool (parallel groups respected), wait for at least one to complete, repeat.
- **Step 6**: Wire the replanning hook. On executor failure, supervisor invokes planner with `{original_task, partial_plan, failure: {step_id, error, ...}}`. `MAX_REPLANS = 2`. Replan dedup: identical-plan output from the planner triggers escalation rather than a third try.
- **Step 7**: Wire the synthesizer (final-answer composer). Takes the original task + the step-result dict, produces the final answer with citation preservation (when steps produced fetched pages).
- **Step 8**: Run end-to-end on a real task that has both serial and parallel structure. Verbose trace shows: plan emission → dependency resolution → parallel dispatch → result collection → synthesis.
- **Step 9**: Failure-mode walkthrough — each of the four debate-specific failure modes with the mitigation Lab 12 ships:
  - **Plan brittleness** → role-based step descriptions; executor sees actual dependency outputs.
  - **Execution drift** → anti-improvement executor prompt; supervisor reads `cannot_execute` and replans.
  - **Replanning thrash** → `MAX_REPLANS = 2` + identical-plan dedup.
  - **Plan-execution gap** → executor tool registry passed into planner system prompt; planner constrained to available tools.
- **Step 10** (stretch): Comparing plan-and-execute vs. ReAct on the same task. Demonstrate where each pattern's advantages show up empirically — plan-and-execute wins on auditability and parallelism for well-decomposable tasks; ReAct wins on exploratory tasks where each step's result determines what makes sense next.

## What to watch for

Five practical issues:

1. **The planner emits free-text JSON that doesn't validate.** Common at first — the model adds preamble, wraps in markdown fences, or hallucinates a field. The validation-then-retry loop in Step 3 surfaces these errors back to the planner with the specific schema mismatch.

2. **Parallel groups that aren't honest.** The planner puts step B in the same group as step A even though B's `depends_on` includes A. The schema validation in Step 2 catches this (`PlanStep.validate_plan()` checks for parallel-group cycles), but if it slips through, you'll see the supervisor refuse to dispatch — a useful signal that the plan is malformed.

3. **Thread-safety of shared state.** The result dict is read by ready-step computation and written by completed futures. Lab 12 uses a `threading.Lock` around the result dict to keep this safe; if you remove it, you'll occasionally see race conditions where a step claims its dependencies aren't ready when they are.

4. **Cost.** A plan with 8 steps costs ~10-15 LLM calls total: 1 planner + 8 executors + 1 synthesizer + 0-1 replans + 1-2 supervisor coordination calls. At gpt-4o-mini rates, well under $0.10 per run. But replanning thrash can easily double this — watch for tasks where `MAX_REPLANS` consistently fires.

5. **Wall-clock vs sequential timing.** A plan with 4 independent fetches that each take ~2 seconds runs in ~2-3 seconds wall-clock with `max_workers=3` (some serialization at the pool's edge). Sequential takes ~8 seconds. Lab 12 prints both timings in Step 8 so you can verify the parallelism is real.

## Anti-scope

Deliberately out of scope, scoped for future batches:

- **CrewAI, AutoGen, LangGraph multi-agent helpers** — none of them. The lab is `chat_with_tools` + Python stdlib all the way down. Framework bridges come later.
- **Tree-of-Thoughts / MCTS-style plan search** — different shape (search over candidate plans + scoring), different cost, out of scope.
- **Async/asyncio orchestration** — LLM calls are IO-bound; threads work fine; asyncio adds complexity without commensurate benefit for this lab's scale.
- **Distributed execution / message queues** — single-process. Distributed plan-and-execute is a different design problem (state durability, message ordering, partial-failure handling).
- **Persistent plan state across process restarts** — plans are in-memory. LangGraph's checkpointer pattern is one approach; out of scope here.
- **Multi-agent RAG with planning** — composing this with Lab 06-08's retrieval pipeline. Future Path 03 batch.
- **MCP / A2A coverage** — Path 04.
- **Production observability** — Path 06.

## Run-time and cost

Per end-to-end run:

- 1 planner call (emits the plan, ~5-10 seconds for a complex task).
- 1 call per step (executor; in parallel groups, these overlap in wall-clock).
- 0-2 replanner calls (only fires on failures).
- 1 synthesizer call.
- 1-3 supervisor coordination calls.

Total: 8-15 LLM calls, ~$0.05-$0.10 at gpt-4o-mini rates. Wall-clock dominated by `fetch_page` calls (live web; 1-3 seconds each) — and the pool's whole point is to let those overlap. A 4-fetch parallel group runs in ~3-4 seconds wall-clock instead of ~12 sequential.

## Solution

A reference implementation lives in [`solution/lab.ipynb`](./solution/lab.ipynb) with notes in [`solution/README.md`](./solution/README.md). 21 cells vs the lab's 40 — the four-failure-mode walkthrough, the plan-and-execute vs ReAct stretch, and the structured-trace appendix are removed since you've already worked through them; the planner/executor/dispatcher/replanner cycle reads end-to-end. Three implementation choices flagged there:

- **The dispatcher is plain Python, not LLM-driven.** Once the plan exists, dependency resolution and dispatch are mechanical. Wrapping them in an LLM call would add cost and a new failure surface (the LLM mis-resolving dependencies) for no quality gain.
- **The executor receives only `(step, dependency_outputs)`, not the whole plan.** Same discipline as Lab 11's stateless critic. The executor can't see steps it doesn't depend on; this prevents the executor from "helpfully" anticipating future steps.
- **The replanner sees the partial plan and the failure context.** Not the executor's full reasoning; just the structured failure. The replanner is a planner with extra constraints, not a debugger.

## Next

- After completing the lab, take the [plan-and-execute quiz](../../quizzes/multi-agent/plan-and-execute.md).
- Path 03 continues with [Lab 13 (multi-agent RAG)](../13-multi-agent-rag-from-scratch/) and then Module 5's framework bridge in [Lab 14](../14-langgraph-supervisor-bridge/) + [Lab 15](../15-langgraph-plan-execute-bridge/) — Lab 15 specifically re-implements this lab's plan-and-execute pattern using LangGraph's `Send` primitive for parallel dispatch.
- If you've also done Path 02, [Lab 13](../13-multi-agent-rag-from-scratch/) composes Lab 06-08's retrieval pipeline with the supervisor + critic + planner-executor patterns from Labs 10-12.
