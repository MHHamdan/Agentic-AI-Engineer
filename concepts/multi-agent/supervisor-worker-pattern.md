# The supervisor-worker pattern

> ⏱ ~10 min · 🟡 Intermediate · Prerequisites: [what is a multi-agent system?](./what-is-a-multi-agent-system.md), Path 01 Foundations

The supervisor-worker pattern is the simplest multi-agent shape that's genuinely useful in production. **One coordinator agent — the supervisor — routes work to specialist worker agents and synthesizes their results.** Workers don't talk to each other directly; the supervisor mediates every handoff.

If you only learn one multi-agent pattern, learn this one. Most production multi-agent systems are either supervisor-worker outright or a thin variation on it.

## The shape

```
                  user task
                      │
                      ▼
              ┌───────────────┐
              │  supervisor   │ ← system prompt, agent loop, dedup, step cap
              └───────────────┘
                  ▲   │   ▲
                  │   │   │
            ┌─────┘   │   └─────┐
            │         │         │
            │         ▼         │
            │  ┌──────────────┐ │
            │  │  worker_A    │ │ ← own prompt, own tools, own loop
            │  └──────────────┘ │
            │                   │
            │   ┌──────────────┐│
            └───│  worker_B    │┘ ← own prompt, own tools, own loop
                └──────────────┘
```

Three properties to internalize:

1. **The supervisor is just an agent.** Same Lab 01 loop. Same `chat_with_tools` machinery. Same step cap, action-hash dedup, structured-error envelope. Nothing exotic.
2. **The supervisor's "tools" are calls to the workers.** Each worker is exposed to the supervisor as a tool with a clear schema. The supervisor selects workers exactly the way it would select any other tool — via the standard tool-calling contract from Lab 02.
3. **Workers don't call each other.** All communication flows through the supervisor. If `worker_A` produces something `worker_B` needs, the supervisor handles the handoff.

That's it. No new framework, no new abstraction, no new failure modes that the single-agent patterns didn't already prepare you for.

## Why this pattern dominates production

Four reasons:

**Clear control flow.** The supervisor is the single point that decides what happens next. You can read its trace top-to-bottom and understand the trajectory. Compare that to a peer-to-peer system where any agent can call any other — you end up with traces that are hard to follow even for the engineer who built them.

**Obvious place to put cross-cutting concerns.** Step caps, retry logic, observability, rate limiting, cost budgeting — all of it goes at the supervisor. You don't have to replicate it across every worker.

**Workers are independently replaceable.** Each worker has a clear contract (its tool schema as seen by the supervisor). You can swap the researcher's implementation, change its model, change its tools, even replace it with a different worker entirely — as long as the schema holds, the supervisor doesn't notice.

**Failure mode locality.** When the trajectory fails, the failure is in one of three places: supervisor (bad routing), specific worker (failed to do its job), or handoff (lost or mangled payload). Three buckets, each with a clear diagnostic path.

## What the supervisor does

Concretely, the supervisor's agent loop:

1. **Receives the user task.** Plain string, just like Lab 01.
2. **Decides which worker(s) to invoke and in what order.** This is the supervisor's system prompt's main job. Often: "if the task needs fresh information, call `researcher` first. Then call `writer` to produce the final answer."
3. **Calls workers via the standard tool contract.** `call_researcher(question="...")` returns `{"findings": ..., "citations": ...}`. The tool-result envelope from Lab 02 applies verbatim.
4. **Collects results.** Each worker's structured output goes into the supervisor's conversation history as a tool result.
5. **Synthesizes the final answer.** Once the supervisor has enough information, it returns the answer to the user (the loop terminates with no further tool call).

That's the entire loop. It's the Lab 01 loop with worker-calling tools instead of arithmetic tools.

## What the workers do

Each worker is itself an agent. It has its own system prompt, its own tool set, its own conversation history, its own agent loop. When called by the supervisor it:

1. **Receives a sub-task** — a structured payload from the supervisor (e.g., `{"question": "..."}`).
2. **Runs its own loop** — same Lab 01 mechanics. The researcher worker uses `web_search` and `fetch_page`; the writer worker uses no tools.
3. **Returns a structured result** — `{"findings": ..., "citations": ...}` for the researcher; `{"answer": ...}` for the writer.

The worker's loop is fully independent of the supervisor's. The worker has its own step cap, its own dedup tracking. When the worker finishes, the result returns to the supervisor and the supervisor's loop continues.

This is the key conceptual move: **a worker is a function from sub-task to structured result, implemented as an internal agent loop**. The supervisor doesn't see the worker's internal trajectory; it just sees the return value.

## Failure modes and mitigations

The patterns from Path 01 transfer directly, with one nuance per failure mode:

**Supervisor never escalates / loops forever.** Same fix as Lab 01: step cap at the supervisor level. Set `SUPERVISOR_MAX_STEPS = 6` (or whatever fits — typically lower than a worker's because the supervisor's job is routing, not deep work).

**Supervisor calls the same worker twice with the same input.** Same fix as Lab 03: action-hash dedup at the supervisor. The dedup signature is `(worker_name, sorted_args_json)` — identical to the single-agent version, just applied to worker-calling tools.

**Wrong worker chosen.** Same fix as Lab 02: tool design. Each worker's "tool description" (the supervisor's view of the worker) needs:
- A clear one-line summary of what the worker does.
- **Negative guidance** — "Use the researcher when X. Do NOT use the researcher when Y; use the writer instead."
- A concrete example input/output if helpful.

**Worker hallucinates capability.** This is the failure mode unique to multi-agent: the supervisor calls a worker for task T, the worker doesn't actually know how to do T but generates something plausible anyway. Mitigation has two parts: a tight worker system prompt ("If the task is outside your scope, return `{\"error\": \"out_of_scope\", \"detail\": \"...\"}`"), and a supervisor that *reads* worker errors instead of treating every worker response as a success.

**Handoff envelope mangles or drops information.** This is the most subtle bug. The supervisor synthesizes a worker's structured result into the next prompt, and somewhere in that re-serialization a citation or fact is lost. Mitigation: handoff payloads are *structured*, not free text, and the supervisor's system prompt explicitly tells it to preserve specific fields ("the citations list must appear in the final answer verbatim").

**Endless ping-pong between supervisor and one worker.** The supervisor calls researcher → reads result → decides it needs more research → calls researcher again → and so on. Mitigation: action-hash dedup + a smaller step cap. Also a clear supervisor prompt that says "if `researcher` returns once with a non-error result, do not call it again unless the user asks a fundamentally different question."

## When supervisor-worker isn't enough

Three situations where the pattern stops carrying its weight:

- **Highly parallel tasks.** If the workers are genuinely independent and there are many of them, a serial supervisor-worker walk wastes wall-clock time. Plan-and-execute (a later Path 03 module) is the natural next pattern: a planner emits a structured plan, multiple executor workers run in parallel, results are aggregated.
- **Iterative refinement.** If the task requires "generate → critique → revise → critique → revise" cycles, agent debate is the natural pattern. A future Path 03 batch covers this.
- **No clear hierarchy.** If the task is symmetric (multiple peer specialists negotiating), swarm or consensus patterns may fit better. Pragmatic note: in production, "no clear hierarchy" is rarer than the marketing suggests. Most tasks *do* have a natural coordinator role; it's just sometimes implicit.

In v1, focus on supervisor-worker. Reach for the others only when you've felt this one bend.

## Related concepts

- The mechanics of how agents pass information: [handoffs and shared state](./handoffs-and-shared-state.md).
- The honest framing of when multi-agent is the right call: [what is a multi-agent system?](./what-is-a-multi-agent-system.md).
- The single-agent loop the supervisor and workers each run: [agent loop](../agents/agent-loop.md).
- The tool-design principles that govern how the supervisor sees its workers: [tool design](../tools/tool-design.md), [tool selection](../tools/tool-selection.md).

## References

- Anthropic 2024, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) — section on orchestrator-workers describes essentially this pattern; recommended reading.
- LangGraph's [multi-agent supervisor docs](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/) — production-grade implementation of the same pattern; useful reference once you've built it from scratch first.
- Hong et al. 2023, "MetaGPT" (arXiv:2308.00352) — role-specialized agents with a coordinator; a more elaborate version of the same idea.
