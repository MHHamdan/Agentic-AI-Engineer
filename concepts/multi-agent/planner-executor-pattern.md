# The planner-executor pattern

> ⏱ ~10 min · 🟡 Intermediate · Prerequisites: [plan-and-execute](./plan-and-execute.md), [supervisor-worker pattern](./supervisor-worker-pattern.md)

The specific pattern Lab 12 implements: a planner agent emits a structured `Plan` (a list of typed steps with explicit dependencies); a supervisor invokes executor calls in dependency order, parallelizing where the plan allows; failures trigger bounded replanning. Concrete and prescriptive.

## The shape

```
        user task
            │
            ▼
    ┌───────────────┐
    │   planner     │ ← runs once, returns a structured Plan
    └───────────────┘
            │
            ▼
        Plan {steps: [...], depends_on, parallel_group}
            │
            ▼
    ┌───────────────┐
    │  supervisor   │ ← resolves dependencies, dispatches to executor pool
    │  + executor   │
    │      pool     │
    └───────────────┘
            │
       ┌────┴────┬─────────┐
       ▼         ▼         ▼
   executor  executor  executor   ← bounded pool, runs steps when ready
       │         │         │
       └────┬────┴─────────┘
            ▼
       step results
            │
            ▼
      synthesize final answer
       (or replan on failure,
        up to MAX_REPLANS)
```

Three properties:

1. **The planner runs once per plan, not once per step.** The whole trajectory is decided upfront. Replanning is the exception, not the norm.
2. **The supervisor is a dependency resolver and dispatcher**, not a router. It computes which steps are ready (all `depends_on` satisfied) and dispatches them to the executor pool. It does not decide what to do next in any LLM-driven sense — the plan already decided.
3. **The executor pool is bounded and stateless across steps.** Each executor invocation runs one step. No memory of previous steps. Inputs to a step come from the plan + the resolved outputs of its dependencies.

## Plan representation

The plan is a list of typed steps:

```python
class PlanStep(StrictModel):
    id: str                          # "step_1", "step_2", ...
    description: str                 # what the executor should do
    tool: str                        # which tool the executor must use
    args: dict                       # arguments to that tool
    depends_on: list[str]            # IDs of steps whose output this step needs
    parallel_group: str | None       # optional grouping for concurrent execution

class Plan(StrictModel):
    steps: list[PlanStep]
```

`StrictModel` is the Lab 02 pattern (`ConfigDict(extra="forbid")`) — the planner can't emit fields outside this schema. Lab 12 validates the planner's JSON output against `Plan` and surfaces validation errors back to the planner if it produced something malformed.

A few subtleties worth flagging:

- **`tool` is a string, not an enum.** The planner needs to know what tools the executor has — Lab 12 passes the tool registry into the planner's system prompt and validates that each step's `tool` is one the executor actually possesses. This addresses the plan-execution gap failure mode.
- **`args` is `dict`, not a per-tool schema.** Validating args against the tool's schema happens inside the executor, not at plan-time. This keeps the planner schema simple at the cost of pushing some failures from plan-validation time to execution time.
- **`depends_on` is a list of `id`s.** Not "the result of step_1" or anything more elaborate. The executor resolves the dependencies and passes their outputs as part of the step's input.
- **`parallel_group` is optional.** Steps with the same `parallel_group` value can run concurrently (their dependencies permitting). Steps with `None` run alone. This is the safe default — if the planner is uncertain, leaving `parallel_group` as `None` is always correct.

## The five planner-prompt rules

The planner's system prompt is what determines plan quality. Five rules, each preventing a specific failure mode:

### Rule 1: Steps must be atomic

One tool call per step. "Search for X and then read the top result" is two steps. "Compare these three things and decide" is *not* an executor step — it's a synthesis step the supervisor does at the end.

The rule exists because atomic steps are debuggable. If "search and read" is one step and the read fails, did the search fail too? If it's two steps, you know exactly where.

### Rule 2: Dependencies must be explicit

Every step that uses output from another step must declare it in `depends_on`. The supervisor enforces this — a step is not eligible to run until every step in its `depends_on` list has completed successfully.

Implicit dependencies (the planner "knew" step 3 needed step 1's output but didn't list it) produce race conditions when the supervisor parallelizes. Explicit `depends_on` makes the dependency graph machine-readable.

### Rule 3: Parallel groups must be honestly independent

Steps in the same `parallel_group` cannot have transitive dependencies on each other. If step B depends on step A and they're in the same parallel group, the supervisor will detect the cycle and reject the plan.

Cosmetic parallelism — putting steps in the same group because the planner "thought they were independent" — is worse than no parallelism because it produces wrong answers, not just slow ones.

### Rule 4: Step descriptions must be self-contained

The executor sees the step + its dependencies' outputs, not the whole plan. If a step's description says "now do the third thing from the analysis," the executor has no idea what "the analysis" is or what "the third thing" means.

Each step description must read sensibly to someone with no plan context, given the dependency outputs as input.

### Rule 5: Plans must be bounded

`MAX_PLAN_STEPS = 8` in Lab 12. If a task seems to need more steps, the planner should chunk it (emit a plan with the first 8 steps, where the last step's output is "a checklist for the next batch").

Long plans are brittle plans — each step is a chance for the plan to break, and the brittleness compounds. The bound forces decomposition into a tree of shorter plans, which is more debuggable.

## Executor pool concurrency

Lab 12 uses Python's `concurrent.futures.ThreadPoolExecutor` with `max_workers=3`:

```python
MAX_PARALLEL_EXECUTORS = 3

with ThreadPoolExecutor(max_workers=MAX_PARALLEL_EXECUTORS) as pool:
    # dispatch steps whose dependencies are satisfied
    # collect results as futures complete
    ...
```

Three because:
- LLM calls are IO-bound (waiting on HTTP). Threads work fine; no need for asyncio's complexity.
- Three is empirically the sweet spot for tasks with mixed parallel/serial steps. More than three usually triggers rate limits on shared APIs (search, fetch).
- Three is small enough that debugging traces are still readable. Pools of 10+ become hard to follow.

Pool size is a *latency* lever, not a *cost* lever. Three concurrent calls cost the same as three sequential calls — they just finish faster.

The supervisor's dispatch loop:

```
ready_steps = [steps whose depends_on are all completed]
while ready_steps or running_steps:
    for step in ready_steps:
        if step.parallel_group matches running batch:
            submit to pool
    wait for at least one future to complete
    if completed step succeeded:
        store result; recompute ready_steps
    if completed step failed:
        decide: replan or surface
```

## Replanning policy

When an executor returns `{"status": "error"}` or `{"status": "cannot_execute"}`, the supervisor's options are:

**Option A: Replan from scratch.** Invoke the planner again with `{original_task, failure: {step_id, error, ...}}`. The planner emits a new plan. This is what Lab 12 does by default.

**Option B: Patch the plan.** Ask the planner to emit just a replacement subgraph (the failed step + its downstream). Composes the old plan minus the failed branch with the new subgraph. Harder to get right (the patched plan can introduce inconsistencies with the unmodified part).

**Option C: Surface the failure.** Don't replan; return the partial results with the failure context. Lab 12 does this when the replan cap fires.

Lab 12 picks Option A with `MAX_REPLANS = 2`. After two full replans, if execution still fails, the supervisor finalizes with partial results and an honest account of what went wrong. Same discipline as Lab 11's bounded refinement.

The two-replan cap matters: if you get three plans that all fail, the problem is upstream of the planner (wrong tools, ambiguous task, broken executor) and more replans won't fix it. Surfacing the failure is more useful than looping.

## Step-cap composition

Lab 12 has **four** independent step caps, which is one more than Lab 11. The numbers are deliberate:

| Cap | Value | What it bounds |
|---|---:|---|
| `MAX_PLAN_STEPS` | 8 | Steps the planner can emit in one plan |
| `MAX_PARALLEL_EXECUTORS` | 3 | Concurrent executor calls |
| `EXECUTOR_MAX_STEPS` | 4 | Internal loop steps per executor (small because each executor runs one tool call) |
| `MAX_REPLANS` | 2 | Replanning rounds before surfacing failure |
| `SUPERVISOR_MAX_STEPS` | 12 | LLM calls the supervisor itself makes (raised from Lab 11's 10 to accommodate planning + replanning + finalization) |

These compose by escalation through the structured-error envelope, the same way Lab 10 and Lab 11 handled cross-level step caps. An executor hitting its `EXECUTOR_MAX_STEPS` returns a `step_cap` envelope; the supervisor reads it as a failure and decides whether to replan or surface.

## Composing with Lab 10 and Lab 11

Lab 12 reuses heavily:

- The provider-agnostic `chat_with_tools` — unchanged.
- `web_search` and `fetch_page` — Lab 10's web tools, now exposed at the executor level.
- `_action_hash` dedup — applied at the executor pool to prevent the same step from being dispatched twice.
- `StrictModel` — used for `PlanStep` and `Plan`.

What Lab 12 adds:

- The `Plan` schema and the planner agent.
- The dependency-resolving dispatcher (the supervisor's new core).
- The ThreadPoolExecutor-bounded execution pool.
- The replanning hook.

What Lab 12 doesn't add:

- A critic. Plan-and-execute and generator-critic are *independent* patterns; you can compose them (a critic reviews the planner's plan, or the synthesized output, or both), but the headline lab keeps them separate for clarity. The composition is left as a stretch exercise.

## When this pattern stops working

Three signals to drop plan-and-execute and reach for something else:

- **Plans frequently exceed `MAX_PLAN_STEPS`.** The task isn't naturally bounded; ReAct is more natural.
- **Replan rate exceeds ~30% of tasks.** The planner doesn't have enough information upfront; interleaved planning (or supervisor-worker with a critic) is more honest.
- **Parallel groups consistently turn out to be wrong.** The task's dependencies are subtler than the planner can model; sequential execution is safer.

These are observable in eval, not in code. Plan-and-execute is best deployed when you can measure these rates and confirm they're low.

## Related concepts

- The framing of when plan-and-execute earns its place: [plan-and-execute](./plan-and-execute.md).
- The supervisor mechanics this builds on: [supervisor-worker pattern](./supervisor-worker-pattern.md).
- The iterative-refinement alternative: [generator-critic pattern](./generator-critic-pattern.md).
- The structured-payload discipline used for the plan schema: [handoffs and shared state](./handoffs-and-shared-state.md#rule-1-handoffs-carry-structured-payloads-not-free-text).

## References

- Wang et al. 2023, ["Plan-and-Solve Prompting"](https://arxiv.org/abs/2305.04091) — the prompting-level baseline.
- Yao et al. 2023, ["ReAct: Synergizing Reasoning and Acting"](https://arxiv.org/abs/2210.03629) — what to use instead when the plan can't be known upfront.
- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — the "parallelization" pattern in production deployments.
- LangGraph docs, [Plan-and-Execute tutorial](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/) — a production-grade implementation of essentially this pattern, useful reference *after* building the from-scratch version.
