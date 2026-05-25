# Plan-and-execute

> ⏱ ~10 min · 🟡 Intermediate · Prerequisites: [supervisor-worker pattern](./supervisor-worker-pattern.md), [generator-critic pattern](./generator-critic-pattern.md)

Plan-and-execute is the third coordination pattern in Path 03, after supervisor-worker (Lab 10) and generator-critic (Lab 11). A **planner agent** emits a structured plan upfront; an **executor pool** carries out the plan's steps, sometimes in parallel; a supervisor coordinates and decides what to do when execution diverges from the plan.

This is the pattern where parallel execution first earns its place legitimately. It's also where *replanning* — adjusting course when an executor reports failure — first becomes a real design question. Both turn out to have specific failure modes that don't show up in the simpler patterns.

This page covers the framing. The next page, [planner-executor-pattern](./planner-executor-pattern.md), covers the specific mechanics Lab 12 implements.

## What changes from the prior patterns

In **supervisor-worker** (Lab 10), the supervisor decides what to do *next* at each step. There's no plan; the trajectory emerges from the supervisor's routing decisions one tool call at a time.

In **generator-critic** (Lab 11), the supervisor still decides each step, but a refinement loop adds bounded iteration around the generation step. Still no plan.

In **plan-and-execute**, the planner emits the *whole trajectory* upfront as a structured artifact — a list of steps with dependencies, tool specifications, and (optional) parallel-group annotations. Execution becomes a constraint-satisfaction problem: run each step when its dependencies are ready, parallelize where the plan says it's safe, collect results.

The shift matters because:

- The plan is **auditable** before execution. You can review it, edit it, version it, eval it. A trajectory from supervisor-worker is only inspectable after the fact.
- The plan **declares parallelism**. The supervisor never has to guess what's safe to run concurrently — the planner already decided.
- The plan **separates routing from execution**. Routing logic lives in the planner's prompt; execution logic lives in the executor's prompt. Cleaner blast radius for prompt changes.

## When plan-and-execute beats the alternatives

Three situations:

**1. Tasks with clear upfront decomposition.** Multi-step research that breaks naturally into (a) gather sources, (b) extract structured data from each, (c) cross-reference, (d) synthesize. The decomposition is obvious enough that a competent planner emits a reasonable plan first try. Supervisor-worker would arrive at the same trajectory step-by-step, but the planner gets you there with the plan as an explicit artifact.

**2. Tasks where steps are independent enough to parallelize.** Fetching content from N URLs, running N independent analyses, comparing N alternatives. Supervisor-worker is sequential by construction; plan-and-execute can run independent steps concurrently, with wall-clock savings proportional to the parallelism.

**3. Tasks where the plan itself is the artifact.** "Generate a project plan to migrate the database" — the plan is the deliverable, not just the means to a deliverable. Plan-and-execute makes the plan a first-class artifact you can edit, share, or version-control. Execution is optional.

## When plan-and-execute is the wrong call

Four anti-patterns:

**Single-step tasks.** If the task is one tool call, planning is overhead. Use supervisor-worker (or just a single agent).

**Tasks where each step depends fully on the previous.** If step N strictly needs step (N-1)'s output to even be specified, there's no parallelism to exploit and no upfront-plan to write — the planner is just imagining the trajectory the supervisor would have followed anyway. Use ReAct or supervisor-worker.

**Tasks where the plan can't be known upfront.** Exploratory tasks where each step's result determines what makes sense next. "Find an answer to this question" with no clear decomposition. ReAct is built for this — interleaved think-act-think-act with no commitment to a plan. Plan-and-execute would emit a brittle plan that doesn't survive contact with reality.

**Tasks where the cost of replanning approaches the cost of the original plan.** If failures are frequent and full re-plans are expensive, you spend more time planning than executing. Supervisor-worker degrades more gracefully because each decision is independent.

A useful heuristic: **can a competent human write a checklist for this task before starting it?** If yes, plan-and-execute is plausible. If no — if the human would say "depends on what I find" — it's ReAct territory.

## Plan-first vs interleaved planning

**Plan-first** (what Lab 12 does): the planner emits the entire plan upfront. The executor runs the whole plan unless something fails. If something fails, the planner is invoked again with the failure context to revise.

**Interleaved planning**: the planner emits the next step, the executor runs it, the planner sees the result and emits the next step. This is just ReAct with a fancier system prompt — the planner is now playing the role of "supervisor reasoning about what to do next." It loses the auditability advantage (the plan never exists as a complete artifact) and the parallelism advantage (steps come one at a time).

Production systems often blend both: an initial plan-first pass, then per-step interleaved adjustment when execution surfaces information the planner couldn't have known. Lab 12 stays plan-first with bounded replanning for clarity; the blended pattern is a natural extension once you've built the simple one.

## The parallelism trade-off

Plan-and-execute is the first pattern where parallel execution is on the table. It's also where the cost of parallelism is most visible.

**What you gain**: wall-clock savings proportional to how much of the plan is genuinely independent. A plan with 4 independent fetches that each take 2 seconds runs in ~2 seconds wall-clock with a pool of 4, vs ~8 seconds sequentially.

**What you pay**:
- **Coordination complexity**. Tracking which steps are ready, which are running, which have failed.
- **Resource contention**. Three threads hammering a search API may trigger rate limits the single-threaded version wouldn't.
- **Debugging difficulty**. A failed step now sits inside a parallel batch; the trace shows the batch boundary, not the linear sequence.
- **Cost**. Parallel LLM calls are concurrent, not free — you still pay for each one. Pool size is a latency control, not a cost control.

A useful framing: parallelism is a wall-clock optimization, not a quality optimization. If your task isn't latency-sensitive, sequential plan-and-execute gives you most of the pattern's benefits (auditable plan, separated routing/execution) without the coordination cost.

## Four failure modes specific to plan-and-execute

These don't appear in supervisor-worker or generator-critic. They're emergent properties of committing to a plan upfront.

### Plan brittleness

The planner emits a plan that doesn't survive contact with reality. Common mechanism: the planner *guesses* what a tool result will look like and writes downstream steps that depend on the guess. When the actual result differs, the downstream steps break.

Example: planner says "Step 1: search the web for X. Step 2: fetch the third result and extract the author's name." But the search returns only two results, or the third result is a video with no author. Step 2 fails not because the executor did something wrong, but because the plan made an assumption that didn't hold.

Mitigation: planner-prompt rule that downstream steps must reference dependency outputs by *role*, not by *specific structure* the planner has imagined. Step 2 should be "extract the author's name from each fetched page," not "extract the author's name from the third result." When the executor receives the step, it sees the actual upstream results and can adapt.

### Execution drift

The executor "improves" a step beyond what the plan specified, breaking downstream steps. Common mechanism: the executor decides a different tool or different arguments would be better, and uses them. The result doesn't match what the downstream steps expect.

Example: plan says "Step 1: web_search('rust async'). Step 2: fetch the top result." Executor decides web_search is the wrong tool, calls a different tool, returns a different shape of result. Step 2 now can't parse the input.

Mitigation: tight executor prompt with explicit anti-improvement framing. "Run exactly the tool the step specifies, with exactly the arguments. If you can't, return `cannot_execute` with the reason. Do not substitute tools." The supervisor reads `cannot_execute` and either replans or surfaces.

### Replanning thrash

Every executor failure triggers a full re-plan. The new plan often has the same flaw. The system never converges.

This is the plan-and-execute version of generator-critic's runaway disagreement. Same fix: hard cap on replans (`MAX_REPLANS = 2` in Lab 12). When the cap fires, the supervisor surfaces the partial results and the latest failure, not a forced approval.

### Plan-execution gap

The plan looks reasonable to a human reading it, but the executor can't actually do the steps. Common mechanism: the planner specifies tools the executor doesn't have, or grants the executor capabilities it lacks.

Example: planner emits "Step 3: use the database query tool to find all users in region X." The executor has `web_search` and `fetch_page`. No database tool. Plan looks great; can't run.

Mitigation: planner-prompt includes the executor's actual tool list. The planner is constrained to steps the executor can run. Lab 12 enforces this by passing the executor's tool registry into the planner's system prompt.

## Related concepts

- The pattern this composes with: [supervisor-worker pattern](./supervisor-worker-pattern.md).
- The iterative refinement that's an alternative to upfront planning: [generator-critic pattern](./generator-critic-pattern.md).
- The general framing of when multi-agent earns its place: [what is a multi-agent system?](./what-is-a-multi-agent-system.md).
- The structured-payload discipline that plan representation follows: [handoffs and shared state](./handoffs-and-shared-state.md#rule-1-handoffs-carry-structured-payloads-not-free-text).
- The next page covers Lab 12's specific mechanics: [planner-executor pattern](./planner-executor-pattern.md).

## References

- Wang et al. 2023, ["Plan-and-Solve Prompting"](https://arxiv.org/abs/2305.04091) — the plan-then-execute prompting baseline; useful for understanding where the pattern came from at the prompting level (one model, two stages) before it generalized to multi-agent.
- Yao et al. 2023, ["ReAct: Synergizing Reasoning and Acting"](https://arxiv.org/abs/2210.03629) — the interleaved-planning alternative; required reading for understanding when plan-first is wrong.
- Xu et al. 2024, ["AgentBench"](https://arxiv.org/abs/2308.03688) — empirical eval of agentic patterns; useful for understanding where plan-and-execute outperforms ReAct and vice versa.
- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — the "orchestrator-workers" section frames the supervisor's role; the "parallelization" section discusses when concurrent execution earns its place.
- Shinn et al. 2023, ["Reflexion"](https://arxiv.org/abs/2303.11366) — relevant when thinking about replanning policy; their reflection mechanism is conceptually adjacent.
