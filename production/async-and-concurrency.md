# Async and concurrency for production agents

> 🔴 Advanced · ⏱ ~24 min · 🛠 Verified 2026-05-29 · 📍 Read after [`production/streaming.md`](./streaming.md); pairs with it for Module 3 (Latency and streaming) of [Path 07](../learning-paths/07-production-and-safety/)

## What this page is for

Production agents make 5-30 LLM and tool calls per request. Run them sequentially and a research-pipeline request takes 45 seconds; run them in parallel where independence allows and the same request takes 8-12 seconds. The math compounds across a deployment — per [Zylos Research April 2026](https://zylos.ai/research/2026-04-23-parallel-tool-calling-optimization-ai-agents): "production systems report 3-5x latency reductions and 40-70% cost savings" from parallel tool calling.

The problem: `asyncio.gather()` is the obvious entry point and the wrong default for production. Per [TianPan April 2026](https://tianpan.co/blog/2026-04-09-structured-concurrency-ai-pipelines-parallel-tool-calls): "parallel tool calls are one of the most useful LLM capabilities — but `asyncio.gather()` introduces orphaned tasks, silent failures, and resource leaks that only surface under production load."

This page covers four patterns:

1. **Why `asyncio.gather()` alone isn't enough** — orphaned task problem, silent failure modes
2. **`TaskGroup` and structured concurrency** — Python 3.11+ default for production agent pipelines
3. **Parallel tool calls within a turn** — the per-turn fan-out / fan-in pattern
4. **Multi-agent fan-out at the orchestration layer** — when agents spawn agents

The decision rule: any time the agent runs multiple independent operations (LLM calls, tool calls, sub-agent invocations), use structured concurrency. Sequential is the wrong default — but ad-hoc parallelism with `asyncio.gather()` produces production incidents the test suite never catches.

What this page does **not** cover is in section 6 (Anti-scope).

## Pattern 1 — Why `asyncio.gather()` alone fails in production

`asyncio.gather()` looks like the right abstraction. Pass it a list of coroutines, it runs them concurrently, it returns when all complete. The reality is more nuanced — three production-hostile defaults.

### Failure mode 1 — The orphaned task problem

Per [TianPan April 2026](https://tianpan.co/blog/2026-04-09-structured-concurrency-ai-pipelines-parallel-tool-calls): "tasks created with `asyncio.create_task()` outside a scope boundary have no parent. If the calling coroutine is cancelled — because a request timed out, because the user aborted, because the workflow moved on — the spawned tasks continue running unobserved. They consume LLM API quota, hold HTTP connections, and may execute irreversible tool calls, all with no signal back to anything that could act on the results."

The shape: an agent spawns 5 parallel tool calls; the request times out at 30 seconds; the agent coroutine is cancelled; the 5 tool-call tasks were created with `create_task()` and have no parent scope. They continue running. The LLM bills you for their tokens. Their tool calls may have already triggered side effects.

Production data from multi-agent deployments per the same source: "in a system running 20 concurrent agents, each spawning 3-5 parallel tool calls per turn, orphaned tasks accumulate quickly. Production data shows error rate increases from this pattern at production load."

### Failure mode 2 — Silent partial failures

```python
results = await asyncio.gather(call_a(), call_b(), call_c())
```

If `call_b()` raises an exception, `asyncio.gather()` cancels `call_a()` and `call_c()` immediately and re-raises. The caller sees the exception from `call_b()` but no signal about which of the other calls completed before cancellation. Side effects from already-completed calls happened anyway.

The opposite default:

```python
results = await asyncio.gather(call_a(), call_b(), call_c(), return_exceptions=True)
```

`return_exceptions=True` returns exceptions as values instead of raising. Every result gets returned. No call is cancelled mid-flight. But now the caller has to inspect every result for exception instances, which is easy to miss. Per [dev.to April 2026](https://dev.to/rahulxsingh/parallel-tool-calling-in-llm-agents-complete-guide-with-code-examples-3ilo): "never silently drop failed results because the model expects a result for every tool call it requested."

### Failure mode 3 — No per-task timeout

`asyncio.gather()` runs every call to completion (or until one raises). There's no per-task timeout primitive. If one call hits a rate limit and waits 90 seconds for backoff, your total request latency is 90 seconds — even if the other 4 calls finished in 2 seconds each. The slow tail dominates.

Per [the May 2026 orchestration patterns guide](https://jobsbyculture.com/blog/ai-agent-orchestration-patterns-2026): "uneven task sizing. If Agent A1 finishes in 8 seconds but A3 takes 90 seconds (because it hit a rate limit or got a harder chunk), your total latency is 90 seconds — worse than the overhead of parallelism. Implement time-boxing with graceful degradation: agents that exceed a threshold return partial results, and the reducer handles gaps explicitly."

## Pattern 2 — `TaskGroup` and structured concurrency

Python 3.11+'s `asyncio.TaskGroup` (or `anyio.create_task_group()` for compatibility across event loops) addresses all three failure modes. The structural guarantee: every task spawned inside the `TaskGroup` is awaited before the `async with` block exits. No orphans. Exceptions from any task cancel the others and propagate cleanly.

### The baseline pattern

```python
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def call_with_timeout(coro, timeout: float):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return {"error": "timeout", "partial": None}

async def parallel_research(queries: list[str]) -> list[dict]:
    results = {}
    async with asyncio.TaskGroup() as tg:
        tasks = {
            i: tg.create_task(call_with_timeout(research_one(q), timeout=15.0))
            for i, q in enumerate(queries)
        }
    for i, task in tasks.items():
        results[i] = task.result()
    return [results[i] for i in range(len(queries))]
```

Four properties:

1. **No orphans.** Every task in `tg` is awaited before the `async with` block exits. A timeout on the outer request cancels the `TaskGroup`, which cancels every task inside it cleanly.
2. **Per-task timeout.** The `asyncio.wait_for(..., timeout=15.0)` wrapper bounds individual task latency. A slow tail at 90 seconds becomes a 15-second timeout with explicit `{"error": "timeout"}` result; the rest of the parallel set is not blocked.
3. **Explicit error result.** The wrapper returns a dict instead of raising on timeout. The caller gets a result per input — no missing entries, no silent drops. The agent (or the reducer) can see which queries succeeded.
4. **Result ordering preserved.** The dict keyed by input index keeps result order stable regardless of completion order.

### When to use `anyio.create_task_group()` instead

`asyncio.TaskGroup` is Python 3.11+. For broader compatibility (older Python, or codebases mixing trio + asyncio), `anyio.create_task_group()` provides the same structured-concurrency semantics with the same API surface. Pick `TaskGroup` for Python 3.11+ pure asyncio; pick `anyio` for portability.

### The two-layer rate limiter

Per [TianPan April 2026](https://tianpan.co/blog/2026-04-09-structured-concurrency-ai-pipelines-parallel-tool-calls): "build the two-layer rate limiter before you hit production 429s."

```python
import asyncio
from asyncio import Semaphore

class RateLimiter:
    def __init__(self, max_concurrent: int, max_per_second: float):
        self.concurrent_sem = Semaphore(max_concurrent)
        self.rate_sem = Semaphore(int(max_per_second))
        self.refill_interval = 1.0
        asyncio.create_task(self._refill())

    async def _refill(self):
        while True:
            await asyncio.sleep(self.refill_interval)
            for _ in range(int(self.rate_sem._value)):  # pseudo; use a proper token bucket
                pass

    async def __aenter__(self):
        await self.concurrent_sem.acquire()
        await self.rate_sem.acquire()
        return self

    async def __aexit__(self, *args):
        self.concurrent_sem.release()
```

Layer 1 (concurrency) caps in-flight calls; Layer 2 (rate) caps calls-per-second. Together they prevent both connection-pool exhaustion AND provider-side 429s. In production, both layers matter — concurrency alone lets you burst above the rate limit; rate alone lets you saturate the connection pool with slow calls.

## Pattern 3 — Parallel tool calls within a turn

Modern LLMs (Claude Sonnet 4.6+, GPT-4o, Gemini 1.5 Pro+) return multiple tool calls in a single turn. Per [Zylos Research April 2026](https://zylos.ai/research/2026-04-23-parallel-tool-calling-optimization-ai-agents): "Gemini supports up to 128 functions in a single declaration list, from which the model may select any subset for parallel invocation." When the model requests `[lookup_invoice, check_account_status, fetch_recent_orders]` in one response, executing them sequentially wastes 2-3 seconds; executing them in parallel wins back that time.

### The execution wave pattern

```python
async def execute_tool_calls(tool_calls: list[ToolCall], timeout: float = 10.0) -> list[ToolResult]:
    """Execute a wave of tool calls in parallel, preserving order, with per-call timeout."""
    results: dict[int, ToolResult] = {}

    async def run_one(idx: int, call: ToolCall):
        try:
            result = await asyncio.wait_for(
                call.execute(),
                timeout=timeout,
            )
            results[idx] = ToolResult(call_id=call.id, content=result, success=True)
        except asyncio.TimeoutError:
            results[idx] = ToolResult(
                call_id=call.id,
                content=f"tool timed out after {timeout}s",
                success=False,
            )
        except Exception as e:
            results[idx] = ToolResult(
                call_id=call.id,
                content=f"tool failed: {e}",
                success=False,
            )

    async with asyncio.TaskGroup() as tg:
        for i, call in enumerate(tool_calls):
            tg.create_task(run_one(i, call))

    return [results[i] for i in range(len(tool_calls))]
```

Five properties matter:

1. **Order preserved.** Tool calls return in input order. The LLM's response format expects one result per call_id in the same order it issued them.
2. **Every call gets a result.** Failures return a ToolResult with `success=False` and an error message; no missing entries. Per [dev.to April 2026](https://dev.to/rahulxsingh/parallel-tool-calling-in-llm-agents-complete-guide-with-code-examples-3ilo): "the model expects a result for every tool call it requested."
3. **Per-call timeout.** Slow tools don't block the wave. The tail is bounded.
4. **Errors surface as data.** The LLM sees the error message and can decide how to recover — retry, use a different tool, ask the user. Silent drops break the model's reasoning.
5. **Structured concurrency.** Cancellation at the outer scope (request timeout, user cancel) propagates into the `TaskGroup` and cancels every in-flight tool call.

### Dependency analysis: when calls can't be parallelized

Not every set of tool calls is parallelizable. If `apply_refund(invoice_id, amount)` depends on the output of `lookup_invoice(user_id)`, they have to run sequentially. Per [Salesforce W&D framework (February 2026, cited in Zylos)](https://zylos.ai/research/2026-04-23-parallel-tool-calling-optimization-ai-agents): "parallel tool calling as a scaling dimension" — width (calls per wave) vs depth (sequential waves).

The model usually makes the right call: it returns parallelizable calls together and dependent calls in sequential turns. The pattern in production: trust the model's parallelization decision per turn; execute each wave with `TaskGroup`; sequence waves across turns.

## Pattern 4 — Multi-agent fan-out at the orchestration layer

Module 3's second concern: when agents spawn agents. The fan-out / fan-in pattern (also called scatter-gather or map-reduce in classical concurrency literature) is the production-default multi-agent topology per [the May 2026 orchestration patterns guide](https://jobsbyculture.com/blog/ai-agent-orchestration-patterns-2026).

### The pattern shape

```
                ┌──── specialist A ────┐
                │                       │
supervisor ─────┼──── specialist B ────┼──── reducer ─── final
                │                       │
                └──── specialist C ────┘
```

The supervisor decomposes the task; specialists run in parallel; the reducer merges. The implementation varies by framework:

| Framework | Fan-out primitive | Fan-in primitive |
|---|---|---|
| **LangGraph** | `Send(node, state)` returned from conditional edge | Reducer functions on state schema fields |
| **CrewAI** | `Task(async_execution=True)` | Crew aggregation |
| **OpenAI Agents SDK / Claude Agent SDK** | `asyncio.gather` over `Runner.run` | Application code |
| **Google ADK** | `ParallelAgent` (built-in primitive) | Sub-agent results aggregation |
| **Raw Python** | `TaskGroup` over async runners | Reducer dict / Pydantic model |

The choice of framework is covered in [Path 03's multi-agent frameworks deep dive](../concepts/multi-agent/multi-agent-frameworks-deep-dive.md); the *production-readiness* concerns below apply across all of them.

### The isolation problem

Per [CocoNinja May 2026](https://medium.com/@yashash.gc/parallel-agents-are-just-multithreading-a-new-architecture-for-peer-agent-coordination-079c5340f759): current frameworks "explicitly state that sub-agents run independently with zero automatic sharing of state or conversation history between them. They treat this as a feature." This is correct for genuinely independent tasks (multi-source research with separate source clusters, batch processing with partitioned data). It is incorrect for tasks where mid-execution information from one specialist matters to another.

Three responses:

1. **Decompose to truly independent tasks** when possible. The supervisor's job is to identify the cut points where independence holds.
2. **Add explicit coordination primitives** when independence doesn't hold — a shared state field that all specialists write to, with reducer semantics that merge their contributions. LangGraph's reducer functions on state schema fields are the canonical implementation.
3. **Sequence the dependency.** If specialist B needs specialist A's intermediate output, they can't fan out — they fan out into separate waves with A first.

The right pattern for production is to push as much as possible toward (1) — genuinely independent tasks — because the failure modes of (2) and (3) are harder to reason about.

### Time-boxing fan-out for graceful degradation

```python
async def fan_out_with_partial_results(
    specialists: list[Specialist],
    task: Task,
    total_timeout: float = 60.0,
    per_specialist_timeout: float = 30.0,
) -> dict[str, Any]:
    results = {}
    async with asyncio.timeout(total_timeout):
        async with asyncio.TaskGroup() as tg:
            for spec in specialists:
                tg.create_task(
                    run_specialist(spec, task, per_specialist_timeout, results)
                )
    return results

async def run_specialist(spec, task, timeout, results):
    try:
        results[spec.name] = await asyncio.wait_for(spec.run(task), timeout=timeout)
    except asyncio.TimeoutError:
        results[spec.name] = {"status": "timeout", "partial": spec.get_partial()}
    except Exception as e:
        results[spec.name] = {"status": "error", "error": str(e)}
```

Two timeout layers: per-specialist (30s) bounds each task; total (60s) bounds the whole fan-out. Slow specialists return partial results; failed specialists return error markers; the reducer downstream sees structured success/timeout/error per specialist and decides how to handle gaps.

This matters in production because the alternative — letting one slow specialist make the whole fan-out slow — is exactly the "uneven task sizing" failure mode the [orchestration patterns guide](https://jobsbyculture.com/blog/ai-agent-orchestration-patterns-2026) names as the most common pitfall.

## Operational discipline

Five practices for production async + concurrency:

1. **`TaskGroup` (or `anyio.create_task_group()`) as the only permitted fan-out primitive.** Code-review enforcement: no `asyncio.create_task()` outside a `TaskGroup` scope; no bare `asyncio.gather()` without `return_exceptions=True`. Per [TianPan April 2026](https://tianpan.co/blog/2026-04-09-structured-concurrency-ai-pipelines-parallel-tool-calls): "treat the concurrency model as part of the architecture, not an implementation detail."
2. **Per-call timeout on every external operation.** LLM calls, tool calls, sub-agent invocations all wrapped in `asyncio.wait_for(..., timeout=X)`. The default is "no timeout"; the production default should be "explicit timeout per call."
3. **Two-layer rate limiting** (concurrency + per-second). Per Pattern 2. Caps both connection-pool exhaustion and provider-side 429 cascades.
4. **`return_exceptions=True` (or `TaskGroup` with explicit error capture) on every parallel set.** No silent drops; the LLM needs to see every tool's outcome.
5. **Observability on fan-out spans.** Per Pattern 4: trace the supervisor → specialist invocations as a span tree. The p99 latency of the slow specialist is the latency the user feels; the dashboards have to surface it.

## Anti-patterns

Three async-concurrency moves that produce production incidents:

### Synchronous LLM client in an async event loop

`OpenAI()` (sync) instead of `AsyncOpenAI()` (async) blocks the event loop on the network call. A single sync LLM call in an otherwise async handler degrades the entire process — every concurrent request waits for the sync call to complete. The fix: every LLM client is the async variant; if a library only offers sync, wrap with `asyncio.to_thread()` to run in a thread pool.

### Unbounded concurrency

`asyncio.gather()` over 500 coroutines launches 500 concurrent connections. Most LLM providers return 429 before the 50th. The fix: bound concurrency with a `Semaphore` or process the input in batches with `TaskGroup`.

### Hand-rolled task scheduling

A custom scheduler that distributes work to "workers" using `asyncio.Queue` and `create_task` looks reasonable. It reinvents what `TaskGroup` already provides — minus the orphan handling and the cancellation propagation. The hand-rolled version is buggier than the standard library primitive. Unless there's a specific scheduling requirement the standard primitives don't address, use the standard primitives.

## Anti-scope (what this page does not cover)

- **`multiprocessing` vs `threading` vs `asyncio` for CPU-bound work.** Agent workloads are overwhelmingly I/O-bound (LLM and tool calls are network calls); CPU-bound work belongs in a separate process pool. The decision is well-covered by the [PyCon US 2026 talk on async patterns for AI agents](https://us.pycon.org/2026/schedule/presentation/110/).
- **Distributed agent execution across machines.** Single-process concurrency is what this page covers. Multi-machine durable execution is the Temporal layer covered in [`production/deployment.md`](./deployment.md) Shape 2.
- **GPU-bound concurrency** for self-hosted LLM serving. Tensor parallelism, continuous batching in vLLM — different domain. [`production/deployment.md`](./deployment.md) Shape 4 touches the surface; depth is its own topic.
- **Framework-specific fan-out semantics.** This page covers the production-readiness concerns that apply across frameworks; framework-specific primitives (LangGraph `Send`, CrewAI async tasks, ADK `ParallelAgent`) are covered in [Path 03's frameworks deep dive](../concepts/multi-agent/multi-agent-frameworks-deep-dive.md).
- **Event-loop tuning** (uvloop, pyuv, custom executors). Useful in extreme cases; rarely the bottleneck for agent workloads where LLM calls dominate latency. Skip until profiling says otherwise.

## References

**Structured concurrency for AI pipelines (2026)**:
- [TianPan (April 2026), *Structured Concurrency for AI Pipelines: Why `asyncio.gather()` Isn't Enough*](https://tianpan.co/blog/2026-04-09-structured-concurrency-ai-pipelines-parallel-tool-calls) — orphaned task problem; TaskGroup as the production default; two-layer rate limiter
- [PyCon US 2026, *Don't Block the Loop: Python Async Patterns for AI Agents*](https://us.pycon.org/2026/schedule/presentation/110/) — `asyncio.gather()` vs `TaskGroup`; mixing async and sync code in agent systems

**Parallel tool calling (2026)**:
- [Zylos Research (April 2026), *Parallel Tool Calling and Execution Optimization*](https://zylos.ai/research/2026-04-23-parallel-tool-calling-optimization-ai-agents) — 3-5x latency reduction; 40-70% cost savings; Salesforce W&D framework
- [dev.to / rahulxsingh (April 2026), *Parallel Tool Calling in LLM Agents*](https://dev.to/rahulxsingh/parallel-tool-calling-in-llm-agents-complete-guide-with-code-examples-3ilo) — `return_exceptions=True` pattern; "the model expects a result for every tool call" framing
- [Medium (May 2026), *Parallel Agents Are Just Multithreading: A New Architecture*](https://medium.com/@yashash.gc/parallel-agents-are-just-multithreading-a-new-architecture-for-peer-agent-coordination-079c5340f759) — fan-out/fan-in as scatter-gather; isolation problem with sub-agents
- [Medium, *How to Run Multiple Parallel API Requests to LLM APIs*](https://medium.com/@ghaelen.m/how-to-run-multiple-parallel-api-requests-to-llm-apis-without-freezing-your-cpu-in-python-asyncio-af0da7e240e3) — AsyncOpenAI/AsyncAnthropic/AsyncAzureOpenAI/AsyncAnthropicBedrock client import patterns

**Multi-agent orchestration (2026)**:
- [jobsbyculture (May 2026), *AI Agent Orchestration Patterns 2026*](https://jobsbyculture.com/blog/ai-agent-orchestration-patterns-2026) — six production-proven patterns; uneven task sizing pitfall; LangGraph Send / CrewAI async-execution / raw Python asyncio comparison
- [Microsoft Community Hub (February 2026), *Building a Local Research Desk: Multi-Agent Orchestration*](https://techcommunity.microsoft.com/blog/educatordeveloperblog/building-a-local-research-desk-multi-agent-orchestration/4493965) — `asyncio.gather` for independent sub-agents

**Repo cross-references**:
- [`production/streaming.md`](./streaming.md) — the streaming half of Module 3; parallel tool calls compose with streamed progress events
- [`production/deployment.md`](./deployment.md) — Shape 2 (Temporal-layered) covers cross-machine durable execution that this page's single-process concurrency doesn't address
- [`production/cost-engineering.md`](./cost-engineering.md) — parallel calls are a cost lever (40-70% savings per Zylos Research) and a cost risk (orphaned tasks burn quota)
- [Path 03 v3 Project 2 (Research pipeline)](../learning-paths/03-multi-agent-systems/projects/02-research-pipeline-with-deep-research.md) — production fan-out example
- [Path 03 frameworks deep dive](../concepts/multi-agent/multi-agent-frameworks-deep-dive.md) — framework-specific fan-out primitives
