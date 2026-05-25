# Lab 12 · Reference solution

The polished final implementation of [Lab 12: Plan-and-execute from scratch](../README.md).

A planner agent emits a structured `Plan` (typed `PlanStep` list with explicit `depends_on` and `parallel_group`); a supervisor resolves dependencies and dispatches steps to a bounded executor pool (`ThreadPoolExecutor`, `max_workers=3`); failures trigger bounded replanning (`MAX_REPLANS = 2`) with structural plan-signature dedup. No frameworks.

> 📖 The concept pages that frame this implementation:
> [`plan-and-execute`](../../../concepts/multi-agent/plan-and-execute.md),
> [`planner-executor-pattern`](../../../concepts/multi-agent/planner-executor-pattern.md).
> 🧠 Calibrate against the [plan-and-execute quiz](../../../quizzes/multi-agent/plan-and-execute.md).
> ⬅️ Builds on [Lab 10's solution](../../10-supervisor-worker-from-scratch/solution/README.md).

## What this solution implements

The headline path from the parent lab:

- All of Lab 10's machinery (chat client, web tools, action-hash dedup, `StrictModel`) — reused without modification.
- `PlanStep` and `Plan` Pydantic schemas with full graph validation (cycles, duplicate IDs, unknown tools, parallel-group integrity violations).
- Planner agent: emits a JSON-validated `Plan`, with retry loop for malformed output and graph-validation feedback to the planner.
- Executor agent: runs one step at a time with anti-improvement framing (`tc.name == step.tool` enforced; supports `cannot_execute` signal).
- Dependency-resolving dispatcher: pure Python, not LLM-driven. `ThreadPoolExecutor(max_workers=3)`. Action-hash dedup at the pool level.
- Replanning hook: `MAX_REPLANS = 2`. Plan-signature dedup escalates identical-plan replans to `partial_after_cap`.
- Synthesizer: composes the final answer with citation preservation for fetched pages.
- One end-to-end demonstration run.

**Not in this solution** (deliberately): the four-failure-mode walkthrough (parent Step 9), the plan-and-execute vs ReAct comparison (parent Step 10). Those are exploratory cells; the solution is the canonical mechanism.

## Implementation choices

### Six design decisions worth flagging

**1. The dispatcher is pure Python, not LLM-driven.** Once the plan exists, dependency resolution is mechanical: compute ready steps (all `depends_on` satisfied), submit to pool, collect results, repeat. Wrapping this in an LLM call would add cost and a new failure surface (the LLM mis-resolving dependencies) for zero quality gain. The supervisor's "intelligence" lives in the planner role, not the dispatch loop.

**2. The plan signature is computed from structural content only.** `_plan_signature(plan)` hashes `(id, tool, args, sorted depends_on, parallel_group)` for each step — *not* descriptions. A replan that changes only wording but keeps the same steps produces the same signature and triggers escalation to `partial_after_cap`. This is the structural mitigation for replanning thrash: if the planner emits a slightly-reworded but structurally identical plan, the second attempt is rejected without execution.

**3. `Plan.validate_graph()` runs Kahn's algorithm for cycle detection.** Plus four other checks in one pass: duplicate IDs, unknown tools (referenced against the executor's registry), unknown dependency targets, and parallel-group integrity (a step in `parallel_group="A"` cannot depend on another step in `parallel_group="A"`). Each detected error becomes structured feedback to the planner's retry loop. The planner sees its specific error and revises.

**4. The executor is stateless across steps and sees only `(step, dep_outputs)`.** The executor doesn't see the whole plan; it sees the one step it's running plus the resolved outputs of its dependencies. This is the same discipline as Lab 11's stateless critic: it prevents the executor from "helpfully" anticipating future steps. The executor *can* substitute placeholder URLs from dependency outputs — that's not improvement, that's executing the plan as designed.

**5. Anti-improvement is enforced structurally, not just in prompts.** The executor's system prompt says "use the specified tool with the specified arguments." But the `executor_agent` function also validates `tc.name == step.tool` after the LLM emits a tool call. If the LLM deviates, the executor returns a `wrong_tool` error envelope without running anything. Prompt-level guidance + structural check is more robust than prompt alone.

**6. Thread-safety via explicit `threading.Lock`.** The shared `completed` dict is read by ready-step computation and written by completed futures. A lock around both reads and writes prevents the rare-but-real race where a future reports completion before the supervisor's next iteration sees it. Without the lock, you occasionally see "step X isn't ready" when X's dependencies are all done.

## Common variations that also work

**Different pool sizes.** `MAX_PARALLEL_EXECUTORS = 2 or 5`. Three is the sweet spot for LLM API calls — small enough to avoid rate limits, large enough to give meaningful wall-clock savings on tasks with 3-4 independent steps. Pools larger than ~10 tend to produce traces that are hard to debug.

**Different replan policies.** This solution does full replanning (Option A from the concept page): on failure, the planner is invoked again with full task + failure context. An alternative is patch-replanning (Option B): ask the planner to emit just a replacement subgraph. Patch-replanning is harder to get right (subgraph consistency with the unmodified part) but cheaper. Both are valid; full replanning is the easier-to-reason-about default.

**Different validation depths.** The graph validator catches cycles, unknown tools, duplicate IDs, parallel-group violations. Some implementations also validate that each step's `args` matches its tool's schema *at plan time* (not just at execution time). This catches more errors earlier but couples plan validation to tool schemas, making tool updates more invasive. The deferred-arg-validation in this solution is the looser-but-more-modular choice.

## Bugs to watch for

Five things that pass syntax but fail eval:

**1. The planner emits free-text JSON that doesn't validate.** Common at first — the model adds preamble, wraps in markdown fences, or hallucinates a field. The `_strip_code_fences` helper handles common markdown wrapping; the retry loop in `planner_agent` surfaces specific schema mismatches back to the planner. Without the retry loop, occasional planner failures become hard errors.

**2. Parallel groups that aren't practical.** The planner puts step B in `parallel_group="A"` alongside step C, but B's `depends_on` includes C. The graph validator catches this, but if you skip validation, the dispatcher serializes them by accident (B has to wait for C even within the parallel batch) and you get cosmetic parallelism with no wall-clock benefit. Always run `validate_graph` before dispatching.

**3. Race conditions on shared state.** Without the `threading.Lock` around the `completed` dict, you occasionally see a step claim its dependencies aren't ready when they are (the reading thread snapshotted the dict before the writing thread committed). Symptom: same plan, intermittent execution-cap fires. Always use the lock.

**4. Plan signature includes prose descriptions.** If your signature hash includes `step.description`, the dedup never fires (descriptions vary across LLM calls even with `temperature=0`). The hash must use only structural content: `id`, `tool`, `args`, sorted `depends_on`, `parallel_group`. Verify: two plans with same structure + different descriptions should hash to the same value.

**5. The cap fires but the system claims success.** When `MAX_REPLANS` fires, return `status="partial_after_cap"` — not `"ok"`. Downstream code should treat partial differently from clean success. The most dangerous bug here is silently coercing partial to ok; the system claims success when there are unresolved failures.

## Differences from naive implementations

Three things a learner might miss on first pass:

- **The executor's tool registry is passed into the planner's system prompt.** The planner literally sees the executor's tool list as part of its prompt. This closes the plan-execution gap structurally: the planner cannot emit a step using a tool the executor doesn't have, because the planner is told what tools exist and the validator enforces it. Skipping this means the planner occasionally hallucinates `database_query` or similar tools that fail at execution time.

- **Step caps compose multiplicatively in the worst case.** `MAX_PLAN_STEPS = 8` × `EXECUTOR_MAX_STEPS = 4` × `MAX_REPLANS = 2` is technically 64 internal LLM calls. In practice executors usually use 1-2 of their 4 steps (one tool call + finalization), so a typical 4-step plan with 0 replans is ~5-7 LLM calls. The caps bound the worst case, not the typical case.

- **`SUPERVISOR_MAX_STEPS = 12` is higher than Lab 10/11.** The supervisor in Lab 12 makes orchestration calls around planning, dispatching, replanning, and finalization. Lab 10's 6 and Lab 11's 10 don't fit. Step caps must compose with the patterns they enable.

## Cost and timing

Per end-to-end run on the demo task:

- 1 planner call (emits the plan; 2-5 seconds)
- 1 executor call per step (plans are typically 3-5 steps)
- 0-2 replanner calls (only on failure)
- 1 synthesizer call

Total: 6-12 LLM calls per task, ~$0.04-$0.08 at gpt-4o-mini rates. Wall-clock dominated by `fetch_page` in executor steps; the planner and synthesizer are fast (no I/O). With `max_workers=3`, a 4-fetch parallel group runs in ~3-4 seconds wall-clock vs ~12 sequentially. Typical end-to-end: 10-25 seconds.

## Next

After completing this lab, move on to [Lab 13 (multi-agent RAG from scratch)](../../13-multi-agent-rag-from-scratch/) — the integrative lab that composes Path 02's retrieval pipeline with this pattern + Lab 10's supervisor + Lab 11's critic. Lab 13 demonstrates that the patterns from Labs 10-12 compose cleanly when their contracts (structured envelopes, action-hash dedup, step caps with structured errors) are explicit.
