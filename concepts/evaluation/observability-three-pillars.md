# Observability's three pillars for agents

> ⏱ ~12 min · 🔴 Advanced · Prerequisites: [from-harness-to-production](./from-harness-to-production.md) (the motivating framing) · Helpful background: any prior exposure to web-service observability (Datadog / Grafana / OpenTelemetry traces) makes the analogies land faster.

Classical web-service observability rests on three pillars: **traces** (the path a request took through your system), **metrics** (the numbers you track over time), and **logs** (the structured records of discrete events). The vocabulary is well-established; the tools are mature.

Agent observability is the same three pillars applied to a different execution model. The infrastructure carries over; the data shape and the questions you ask it don't. This page is about what's the same, what's different, and how the OpenTelemetry GenAI semantic conventions give you a portable instrumentation layer that all the named platforms (LangSmith, Phoenix, Langfuse, Laminar, Braintrust) sit on top of.

## The classical three pillars in 30 seconds

If you're rusty on the terms:

- **Traces** answer "what did this request do?" — a tree of spans showing every function/service call, with timing, parents, and child relationships. The unit of analysis is one user request.
- **Metrics** answer "how is the system behaving over time?" — counters, gauges, histograms. Aggregated; cheap to query; bad for diagnosing a specific incident, good for trends and alerting.
- **Logs** answer "what happened at this exact moment?" — discrete events with a timestamp, level, message, and structured fields. The fallback when traces and metrics don't have the information.

The three are complementary. A latency alert (metric) fires; you find the trace for a slow request; you read the logs from the slow span. Production observability without all three has blind spots.

## What an agent trace looks like

A traditional web service trace has a predictable shape: request in, a handful of database queries, maybe a cache hit, response out. Most spans are short (sub-millisecond to hundreds of milliseconds). Latency lives in the database calls; the rest is overhead.

An agent trace looks structurally different in three ways:

**Deeply nested.** A single user query can produce dozens of spans across nested function calls: the agent's `chat_with_tools` loop runs N iterations; each iteration includes an LLM call (one span) plus tool calls (more spans) plus parsing (more spans). A multi-agent system with three workers can produce 50-200 spans per task. The trace tree gets wide and deep fast.

**Heavy LLM payloads.** Each LLM span carries the full prompt + response. A 4k-token system prompt + 8k tokens of accumulated message history + 2k tokens of response is ~14k tokens of payload per call. Across dozens of calls per trace, this is megabytes per agent run. The ingestion side has to handle this gracefully; the storage cost is non-trivial; the UI has to render conversations, not flame graphs.

**Parallel sub-agent branches.** Lab 12's plan-and-execute pattern dispatches 3-5 concurrent executor sub-agents. Lab 15's LangGraph version uses `Send` to fan them out. Each sub-agent produces its own span subtree. Stitching these back into a coherent parent-child DAG requires explicit context propagation — and getting it wrong gives you orphan spans that look unrelated when they're really part of the same task.

The Datadog / New Relic / Grafana world handles the first concern (deep trees) and the third concern (parallel branches, via OpenTelemetry context propagation) acceptably well. The second concern (heavy LLM payloads, conversation rendering, natural-language signal extraction over LLM content) is where the agent-native platforms (LangSmith, Phoenix, etc.) earn their place — they render traces as conversations, not as flame graphs, and let you query into prompt content directly.

## What an agent metric looks like

The classical metrics (request count, p99 latency, error rate) carry over directly. You also need agent-specific metrics:

**Per-trajectory**: handoff success rate, routing accuracy, plan validity, plan coverage, replan rate, citation preservation, groundedness — every metric Lab 16 implements, computed over each individual trace.

**Per-cohort**: the same metrics aggregated by category, by user, by tenant, by deployed agent version. The aggregation discipline from the from-scratch harness applies; the platform's storage and query layer is what makes the cohorts queryable.

**Per-time-window**: rolling-window comparisons (last 24h vs prior 24h), distribution-drift indicators (KS-test p-value, PSI), regression detectors. The historical state required is what platforms provide that the offline harness can't.

**Cost and latency**: aggregated token usage and dollar spend, p50/p95/p99 trace duration, time-in-LLM-call vs time-in-tool-call. These are the production economics; cost attribution at the trace-root level is how multi-tenant agent products meter customers.

The right metric mix depends on what the agent is for. A user-facing chat agent cares about latency and groundedness; a batch research agent cares about cost-per-task and plan validity. Pick the metrics that map to your actual quality concerns; don't track everything.

## What an agent log looks like

Logs are the third pillar and the one that ages best. An agent log entry is a discrete event with structured fields. Common log targets:

- **Tool call errors** — `tool_name`, `args`, `error_kind`, `error_detail`, `trace_id`. These are the raw failure signal; metrics aggregate them; logs preserve the per-event detail.
- **Routing decisions** — when the supervisor picks worker A over worker B, log it with `available_workers`, `chosen_worker`, `reason`. Lets you audit routing post-hoc.
- **Step-cap events** — `step_cap` (the worker exceeded its budget) is a graceful failure; log it with `cap_value`, `steps_used`, `last_node`. Helps you tune caps based on actual budget consumption.
- **Plan rejections** — when `validate_graph()` rejects a plan, log the structured errors plus the rejected plan. Lets you see what the planner is producing wrong and how often.

The temptation is to log the full LLM prompt and response on every call. Don't — that's what traces are for; logs lose the structural relationship. Logs are for the discrete events that the trace tree doesn't surface well.

## The OpenTelemetry GenAI semantic conventions

The portable instrumentation layer. OpenTelemetry's standard semantic conventions for GenAI cover what every observability platform agrees on:

- **Model invocations**: `gen_ai.system`, `gen_ai.request.model`, `gen_ai.request.temperature`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, etc. Standardized attribute names; every OTel-compatible backend understands them.
- **Embeddings**: similar shape, with `gen_ai.embeddings.model` and dimensions.
- **Tool calls**: `gen_ai.tool.name`, `gen_ai.tool.call.id`, arguments, results.
- **Agent spans**: `gen_ai.agent.name`, `gen_ai.agent.description`, `gen_ai.agent.id` — the agent-execution-specific layer.
- **Conversation context**: thread IDs, session IDs, the multi-turn glue.

Instrumenting your agent with these attributes makes the trace portable. LangSmith ingests it. Phoenix ingests it. Langfuse ingests it. The APM tools (Datadog, New Relic) can ingest it but won't render it as a conversation — they treat it as a generic span with attributes.

The portable-instrumentation discipline is what the [LangSmith March 2026 SDK update](https://blog.langchain.com/end-to-end-opentelemetry-langsmith/) made viable end-to-end: previously LangSmith ingested OTel but used a proprietary client SDK; the March update added native OTel support in the SDK itself. The practical result: an agent instrumented with the OTel GenAI conventions can fanout traces to LangSmith *and* a generic OTel collector at the same time, without rewriting the instrumentation.

## OTel-native vs platform-native — what trades

Both paths are viable in 2026. The choice is about lock-in, ecosystem fit, and what your team already has.

**Platform-native instrumentation** (LangSmith's `@traceable` decorator, Phoenix's `arize-phoenix-otel`, Langfuse's `@observe`):

- *Where it helps*: smallest setup cost; rich UI features (LLM-specific renderings, eval registration, dashboard pinning) that depend on the platform's data shape; tight integration with platform-specific features (LangSmith's `agentevals` package, Phoenix's experiment tracking).
- *What it trades*: switching platforms means rewriting instrumentation. Cross-platform fanout (e.g., to a corporate Datadog + LangSmith) requires double-instrumentation or platform-specific bridges.

**OTel-native instrumentation** (using the OpenTelemetry SDK directly with GenAI conventions):

- *Where it helps*: vendor-neutral; fanout to multiple backends; integration with non-agent observability (your APM, your service mesh, your existing OTel collector); future-proofs against platform churn.
- *What it trades*: more code to write up front; less of the platform's purpose-built UI affordances work out of the box (agent-conversation rendering, eval registration may need adaptation); slightly higher per-span overhead per LangChain's docs.

The hybrid pattern, increasingly common in 2026: OTel-native instrumentation for the agent's own spans + platform-specific extensions for the eval-registration and dashboard layer. You get portability for the data and platform-specific UX for the workflows the platform does well.

## Picking the right pillar for the question

A practical guide for which pillar answers which question:

| Question | Pillar | Example |
|---|---|---|
| What went wrong in this specific run? | **Trace** | "User X complained at 14:32; show me the full trajectory." |
| Is the system regressing over time? | **Metric** | "citation_preservation has dropped from 0.91 → 0.74 over 7 days." |
| What exactly happened at this moment? | **Log** | "The retriever returned status='error' — what was the underlying exception?" |
| Why did the supervisor route to the writer here? | **Trace** | The supervisor's `reasoning` field surfaces in the LLM-call span. |
| Are we spending too much on tool calls? | **Metric** | Cost per trace, aggregated by tool, over time. |
| Did the user retry an action with different args? | **Trace + Log** | Trace shows the loop; logs show the args. |

The pillars are complements, not competitors. Production stacks have all three because each one is the wrong tool for some questions.

## What this misses

A few things this page deliberately doesn't cover — they belong in later modules:

- **Specific OTel instrumentation code.** Module 3's first lab walks through it.
- **Tail-based sampling decisions.** Module 6 covers this. The short version: keep every failed/expensive/anomalous trace in full; sample the happy path aggressively.
- **Multi-turn (threaded) evaluation.** The single-task focus of this page extends naturally to threads, but the metric set changes (semantic intent across turns, semantic outcome, cross-turn trajectory). Module 7.
- **Cost attribution across multi-tenant deployments.** Path 07 + Module 6 of Path 06 territory. The pattern: tag at trace root with `tenant_id` / `user_id`; propagate through children; aggregate by tag dimension.

## Related concepts

- [From harness to production observability](./from-harness-to-production.md) — the motivating framing this page implements.
- [Lab 16: multi-agent evaluation harness](../../labs/16-multi-agent-evaluation-from-scratch/) — the from-scratch baseline.
- [Trajectory-level metrics](../multi-agent/trajectory-level-metrics.md) — the metric algorithms that the production layer ingests live trace data into.
- [Observability layers diagram](../../diagrams/observability-layers.mmd) — visual companion: instrumentation → ingestion → processing → consumption.

## References

- OpenTelemetry, *Generative AI Semantic Conventions* — the standardized attribute names for GenAI spans. [opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- LangChain (March 2026), *Introducing End-to-End OpenTelemetry Support in LangSmith* — the SDK-level OTel pivot. [blog.langchain.com](https://blog.langchain.com/end-to-end-opentelemetry-langsmith/).
- Laminar (April 2026), *Top 6 Agent Observability Platforms (2026)* — head-to-head: LangSmith, Phoenix, Langfuse, Laminar, Weave, Braintrust. Useful for the platform landscape. [laminar.sh/article](https://laminar.sh/article/2026-04-23-top-6-agent-observability-platforms).
- Digital Applied (April 2026), *Agent Observability 2026: Evals, Traces, Cost Guide* — three observability layers, OTel as portable, cost attribution patterns. [digitalapplied.com/blog](https://www.digitalapplied.com/blog/agent-observability-2026-evals-traces-cost-guide).
- LangChain `agentevals` repository — production trajectory evaluators. The trace-as-message-list shape that LangGraph produces directly is the wire format. [github.com/langchain-ai/agentevals](https://github.com/langchain-ai/agentevals).
