# From harness to production observability

> ⏱ ~14 min · 🔴 Advanced · Prerequisites: [Lab 09's RAG eval harness](../../labs/09-evaluating-agentic-rag/) or [Lab 16's multi-agent eval harness](../../labs/16-multi-agent-evaluation-from-scratch/) — at least one. The from-scratch harness is the conceptual baseline this page extends.

You already have a working evaluation harness. Lab 09 gives you the RAG-evaluation version; Lab 16 gives you the multi-agent-trajectory version. Both are hand-curated fixtures + rule-based tier + LLM-as-judge tier + category slicing. Both run offline. Both produce a comparison table.

This page is about what changes when you take the same problem to production. The metric implementations stay; almost everything around them is different. The right mental model is not "scale up Lab 16," it's "the harness is one piece of an operational stack; what are the other pieces."

## What the from-scratch harness gives you

Worth stating clearly because production tooling absorbs a lot of this and you can lose track of what you already had:

- **Metric algorithms.** Lab 09's `recall@k`, Lab 16's `handoff_success_rate`, `citation_preservation` — these are pure functions, framework-agnostic, ~30-100 lines each.
- **Hand-curated fixture set.** 30 queries (Lab 09), 15 traces (Lab 16). The categories — `lexical` / `paraphrase` / `referential` / `compound` / `off-corpus`, or `happy_path` / `tool_failure` / `replan_needed` — encode what each fixture is supposed to test.
- **Aggregation discipline.** The aggregate-then-slice-then-per-agent pattern that prevents an aggregate metric from hiding what's actually failing.
- **Determinism.** Given the fixture set and the metric implementations, the harness produces the same numbers every time. CI can fail builds when a metric regresses below threshold.
- **Diagnostic depth.** When a metric fires, you have the full trajectory or full retrieval result available for inspection. Re-running with more logging isn't needed.

These are not small things. The harness solves the offline-evaluation problem cleanly. The production layer doesn't replace these; it adds operational concerns the harness doesn't address.

## Three things production needs that the harness doesn't provide

### 1. Live trace ingestion at scale

The harness reads from `trace_set.jsonl` — 15 traces, hand-curated. Production reads from a live agent that produces thousands or millions of traces per day. The infrastructure question is no longer "where do I load this file" but "how do I get every agent invocation captured, structured, and queryable, without the instrumentation becoming the bottleneck."

This is what LangSmith / Phoenix / Langfuse / Laminar / Braintrust solve. The trace SDK runs in-process with the agent; spans batch and flush asynchronously to a remote ingestion endpoint; the platform handles storage, indexing, and the dashboard layer. The instrumentation cost is small (low-millisecond overhead per span) but it's not free, and the storage cost at scale is not trivial.

The from-scratch harness avoids this entirely — JSONL files in a repo. Production needs the ingestion infrastructure because the trace volume makes file-based storage untenable and because the team-collaboration concerns (who else can see traces; how do we filter for a specific user complaint; how do we replay a customer's session) need a query layer that JSONL doesn't provide.

### 2. Distribution drift on metric trends over time

The harness reports a single number per metric per run. Production needs the same numbers tracked over time, with detection on distribution shift: "citation_preservation dropped from 0.91 to 0.74 over the last week — is the system regressing or did the world change?"

The detection is not the metric — it's a layer above. Common approaches in 2026:

- **Rolling-window comparisons.** Today's metric distribution vs the last 30 days. Simple, useful as a first cut.
- **Kolmogorov-Smirnov tests.** Statistical test for "are these two distributions different." Good when you have enough data; sensitive to small shifts at high volume.
- **Population Stability Index (PSI).** Standard in classical ML monitoring; works for agent metrics too.
- **Bayesian change-point detection.** When you care about *when* the shift happened, not just *that* it did.

None of these algorithms are in Lab 09 or Lab 16. They live in the production-tooling layer because they need historical state — the harness re-runs against fixtures from scratch every time; production needs to remember what the metric looked like yesterday and last week and last month.

### 3. Distributed-tracing correlation across parallel sub-agents

Lab 16's trace_set has trace IDs but no parent-child correlation across processes. The traces are single-process recordings.

Production multi-agent systems are multi-process. Lab 12's `ThreadPoolExecutor` runs in one process; a production deployment may have the planner on one host, the executors on a worker pool, the synthesizer on a third tier. The trajectory the from-scratch harness sees as a flat list-of-steps is, in production, a DAG of spans across hosts that needs to be reconstructed by the observability layer.

OpenTelemetry's context-propagation primitives are how this works. Every inter-process boundary (every queue message, every HTTP call, every async dispatch) carries the trace context so the ingestion side can stitch spans into a single distributed trace. The platforms know how to do this; the from-scratch harness doesn't have the concept.

A related concern: **parallel sub-agent branches that need correlation.** When two sub-agents run concurrently and one of them poisons shared state, you need the trace context propagated through every message boundary, not just function calls. This is a real production issue — and it's specifically why the [March 2026 DEV community guide](https://dev.to/chunxiaoxx/ai-agent-observability-in-2026-openai-agents-sdk-langsmith-and-opentelemetry-3ale) calls out adding a `span_context` field to every inter-agent payload as the pattern that works.

## What the production layer absorbs

The flip side. Things the production tooling handles by default, that the from-scratch harness made explicit:

- **The trace shape contract.** Lab 16's `TraceStep` / `Trace` pydantic models become the platform's span schema. You stop hand-rolling validators; the SDK enforces shape.
- **Fixture-set construction.** Replaced (or supplemented) by sampling against live traffic. You're no longer hand-curating 15 traces; you're picking 500 from yesterday's production traffic plus the failed/expensive ones via tail-based sampling.
- **The replay loop.** Lab 16's "load fixture, run metric, write to DataFrame" becomes a stream-processing pipeline: trace lands in the platform → registered evaluators fire → metric value gets stored alongside the trace.
- **Storage and querying.** Production has a query layer (SQL or platform-specific DSL). You stop building pandas DataFrames; you ask the platform.
- **Dashboards and alerting.** Built-in to all the production platforms. You stop building Matplotlib plots; you build a dashboard pin or alert rule.

These are real upgrades for production. They're also why production tooling has a learning curve and a vendor-lock-in cost the from-scratch harness doesn't.

## The decision boundary

When to use which:

**Keep the from-scratch harness for**:
- Pre-commit checks: every PR re-runs the harness against the curated fixture set. Failure threshold blocks merge.
- Reproducible regression tests in CI. Determinism matters; the harness has it; live trace ingestion doesn't.
- Rapid metric iteration: changing the `groundedness` threshold from 0.5 to 0.7 is one line; re-running the harness is seconds. Production platforms make this slower because they need to recompute against stored traces.
- Onboarding new contributors: a fresh checkout + `jupyter notebook` reproduces every metric value from the repo. Onboarding to a SaaS platform takes accounts, permissions, network access.

**Add production tooling when**:
- Real users are hitting the system and you can't curate fast enough to keep up with their failure modes. Live traffic is your fixture set.
- You need to debug an incident: "user X had a bad experience at 14:32 yesterday." The harness can't answer this; the trace platform can.
- Metric drift is the question: "are we slowly regressing." Needs historical state the harness doesn't keep.
- Team scale requires shared infrastructure: 5+ engineers iterating on the same agent, all needing to see the same traces, all needing to share evaluators.

**Use both in parallel**, with explicit roles:
- Harness = correctness gate (CI).
- Platform = operational signal (production).

The same metric implementations can run in both. `handoff_success_rate(trace)` is the same function regardless of where `trace` came from — a JSONL line or a LangSmith span object converted to the trace dict shape. This is what makes the Lab 16 design pay off: pure functions are portable.

## What this isn't

A vendor-recommendation document. The 2026 landscape has multiple credible platforms (LangSmith, Braintrust, Langfuse, Phoenix, Laminar, Weave, plus the APM tools — Datadog, New Relic — for the OTel-ingest path). Path 06 covers the categories of choice without picking a winner. Module 2 uses LangSmith because of its `agentevals` integration and the LangChain-native shape Path 03 already used; Module 3 covers the OTel-portable path so you can swap platforms without rewriting instrumentation.

Also not a debugging tutorial. The observability platforms are tools; what you *do* with the traces — diagnose tool selection mistakes, find prompt-drift, localize a hallucination — is the next module's territory.

## Related concepts

- [Observability's three pillars for agents](./observability-three-pillars.md) — the structural companion. Traces, metrics, logs mapped onto agent execution; OpenTelemetry GenAI semantic conventions as the portable layer.
- [Lab 16: multi-agent evaluation harness](../../labs/16-multi-agent-evaluation-from-scratch/) — the from-scratch baseline this page builds on.
- [Lab 09: evaluating agentic RAG](../../labs/09-evaluating-agentic-rag/) — the Path 02 from-scratch baseline.
- [Multi-agent evaluation](../multi-agent/multi-agent-evaluation.md) — the trajectory-vs-outcome framing that Lab 16 implements; carries forward to production.

## References

- LangChain (March 2026), *Introducing End-to-End OpenTelemetry Support in LangSmith* — production trace SDK with native OTel format. [blog.langchain.com](https://blog.langchain.com/end-to-end-opentelemetry-langsmith/).
- Digital Applied (April 2026), *Agent Observability 2026: Evals, Traces, Cost Guide* — the three-platforms-lead-the-category framing; tail-based sampling rationale; multi-dimensional cost attribution as table-stakes for multi-tenant agent products. [digitalapplied.com/blog](https://www.digitalapplied.com/blog/agent-observability-2026-evals-traces-cost-guide).
- DEV Community (April 2026), *AI Agent Observability in 2026: OpenAI Agents SDK, LangSmith, and OpenTelemetry* — the `span_context`-on-every-inter-agent-payload pattern for parallel-branch correlation. [dev.to](https://dev.to/chunxiaoxx/ai-agent-observability-in-2026-openai-agents-sdk-langsmith-and-opentelemetry-3ale).
- LangChain `agentevals` repository — the trajectory eval library Module 2 uses. `create_trajectory_match_evaluator` (deterministic) + `create_trajectory_llm_as_judge` (LLM-judged). [github.com/langchain-ai/agentevals](https://github.com/langchain-ai/agentevals).
- Zheng et al. 2023, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS — the canonical LLM-as-judge bias paper. Required reading before production deployment. [arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685).
