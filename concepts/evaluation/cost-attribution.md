# Cost attribution via OTel baggage propagation

> ⏱ ~14 min · 🔴 Advanced · Prerequisites: [OpenTelemetry GenAI conventions](./opentelemetry-genai-conventions.md), [Platform fanout and portability](./platform-fanout-and-portability.md). Helpful: Lab 18 (the OTel-instrumented agent pattern this page extends with identity propagation).

Module 3's OTel instrumentation gave you spans. This page is what production-scale operations need on top of spans: every span tagged with the *who* (tenant_id, user_id) and the *what* (task_id), propagated automatically across function and service boundaries, rolled up into per-tenant / per-user / per-task cost reports.

Without this layer, every cost question in production becomes a forensic investigation. With it, the question "which tenant burned 80% of our budget last week" is a SQL query against the trace store.

Three dimensions matter, and they answer different product questions:

- **Per-tenant** — who's burning the budget? B2B unit economics. The single most-referenced view because it determines whether a customer is profitable.
- **Per-user** — which users are heavy? Cohort analysis, abuse detection, free-tier abuse vs paid-tier value.
- **Per-task** — which workflow is expensive? Engineering optimization targets. "Document summarization is 12x more expensive per request than chat" is the kind of signal that drives architectural decisions.

You need all three. Building one and retrofitting the others later costs roughly 5x what building all three up front does (Digital Applied 2026 production case study). The reason: trace identity has to be set at request creation time and propagated through every downstream span; retroactive joining from logs misses tool spans, partial traces, and edge cases like timeouts where the trace never completes.

## The four token layers

Aggregating "input tokens" and "output tokens" hides where spend goes. The four-layer breakdown that surfaces optimization targets:

| Layer | What it counts | Why it matters separately |
|---|---|---|
| **Prompt** | System prompts, few-shot examples, persistent rubric content | Mostly static; high token count per request; cache-friendly |
| **Tool** | Tool descriptions in the schema, tool responses fed back to the model | Grows with tool count and verbose tool outputs |
| **Memory** | Retrieved context, conversation history, RAG documents | The unbounded-growth risk; the layer that runs away |
| **Response** | Model output tokens; reasoning tokens for reasoning-capable models | Inversely correlated with retrieval/prompt quality |

Each layer optimizes differently. Prompt-token explosion calls for prompt caching. Tool-token explosion suggests tool-spec compression or response truncation. Memory-token explosion is the classic RAG-tuning lever. Response-token bloat usually means upstream context is poor.

Setting these as separate span attributes (`gen_ai.usage.prompt_tokens`, `gen_ai.usage.tool_tokens`, `gen_ai.usage.memory_tokens`, `gen_ai.usage.completion_tokens`) is what makes the cost-attribution dashboards diagnostic instead of just totalizing.

## OTel baggage — the propagation primitive

Baggage is the part of the OTel context spec that propagates business identity across span boundaries. It's not a telemetry signal — you don't query a "baggage view." It's a way for context set at the API gateway to travel automatically through every downstream span without being passed explicitly as function arguments.

The Python API:

```python
from opentelemetry import baggage, context, trace

# At request entry (API gateway, web framework middleware)
def handle_request(request):
    tenant_id = request.headers.get("X-Tenant-ID")
    user_id = request.headers.get("X-User-ID")
    task_id = request.headers.get("X-Task-ID", "unknown")

    # Set baggage entries in a new context
    ctx = baggage.set_baggage("tenant.id", tenant_id)
    ctx = baggage.set_baggage("user.id", user_id, context=ctx)
    ctx = baggage.set_baggage("task.id", task_id, context=ctx)

    # Attach the context — now active for the current thread/coroutine
    token = context.attach(ctx)
    try:
        # Downstream calls (including HTTP, gRPC, async tasks) see this baggage
        return run_agent(request)
    finally:
        context.detach(token)


# Anywhere downstream, in any function, in any span:
def call_llm(prompt):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("llm.call") as span:
        # Read baggage that was set at the entry point
        tenant_id = baggage.get_baggage("tenant.id")
        user_id = baggage.get_baggage("user.id")

        # Copy to span attributes for searchability in the trace store
        span.set_attribute("tenant.id", tenant_id or "unknown")
        span.set_attribute("user.id", user_id or "anonymous")
        # ... call the model
```

Two patterns matter here:

**Set baggage early, set span attributes redundantly.** Baggage propagates across span boundaries automatically; span attributes are local to a single span and queryable in the trace store. Both are required. Baggage is the mechanism; span attributes are the index.

**Identity propagates implicitly.** No function in the call chain needs to pass `tenant_id` as an argument. Every span in the trace can read it from the active context. Without this, identity gets lost the moment you cross a boundary (tool call, async task, HTTP request to a downstream service).

## The four rules of baggage discipline

- **IDs only, not full objects.** The W3C Baggage spec caps total baggage size at 4KB across all entries. Use `tenant.id="acme-corp"`, not the full tenant record.
- **No PII.** Baggage propagates over the wire (the `baggage:` HTTP header). Email addresses, names, account numbers don't belong here. Use opaque IDs and join to PII in your own data store when needed.
- **No secrets.** Same reason. Tokens, API keys, session IDs that authenticate other services don't belong in baggage.
- **Allowlist, not blocklist.** Configure your collector to drop unknown baggage keys at the ingest boundary. External callers can set arbitrary baggage; you don't want their stuff leaking into your spans.

## The three-layer enforcement ladder

Cost attribution exists to drive cost decisions. The pattern that works in production:

**Layer 1 — Dashboards.** Per-tenant / per-user / per-task burn-down. Refresh daily. The reporting view that answers "who spent what last week." Tools: any trace store with SQL access (Tempo, ClickHouse, OpenSearch, BigQuery via export). The query pattern is `SELECT tenant.id, SUM(cost.total_usd) GROUP BY tenant.id ORDER BY 2 DESC`.

**Layer 2 — Alerts.** Per-tenant spend vs 7-day rolling baseline. Warning at 2x baseline; critical at 5x. The alert routes to on-call with the tenant_id and the recent traces in payload form, so the responder can investigate without separate context-gathering. The 2x/5x thresholds are conventions; tune per your traffic variance.

**Layer 3 — Rate-limit tightening.** Per-tenant token bucket reduces remaining budget for over-burn tenants automatically until human review. This is the only layer that closes the loop without human action — the others surface signal, this one applies brakes. Implementation typically a Redis-backed token bucket keyed by `tenant.id` with replenishment rate tied to plan tier.

The ladder is incremental. Ship Layer 1 first; add Layer 2 once you have baseline data; add Layer 3 only after you're confident the alerting is calibrated. Premature Layer 3 deployment is the classic "auto-throttled a real customer's legitimate burst traffic and lost the deal" failure mode.

## Pricing-tier propagation

Baggage isn't just for cost reporting. The same propagation primitive carries tier-aware routing decisions:

```python
ctx = baggage.set_baggage("tenant.tier", "enterprise")
ctx = baggage.set_baggage("tenant.id", "acme-corp", context=ctx)
```

Downstream services read `tenant.tier` and apply tier-specific behavior: enterprise tenants might route to a higher-capacity model variant; free-tier tenants might route to cheaper models or get smaller context windows. This is a *propagation* pattern, not a *routing* pattern — the tier comes from the gateway, every downstream service uses the same value, no service makes an independent tier lookup that could go stale.

The reverse is also useful: read `tenant.tier` in your sampling policy so you keep more traces from enterprise tenants than from free-tier. This is one of the bridges between cost attribution (this page) and adaptive sampling (next page).

## What this misses

- **Prompt caching counters.** Cached-read and cached-write tokens have different pricing in 2026 (Anthropic, OpenAI, Google all price them separately). The advanced pattern adds `gen_ai.usage.cache_read_tokens` and `gen_ai.usage.cache_write_tokens` as separate span attributes; the cost computation multiplies each by its provider-specific rate. Out of scope for the lab; mention here.
- **Usage forecasting.** Linear extrapolation, ARIMA, growth-curve fitting on per-tenant usage to predict next month's bill. Different discipline (FinOps + time-series analysis); covered by tools like Vantage, CloudZero, Apptio. Out of scope.
- **The FinOps integration layer.** Pushing aggregated cost data to corporate financial systems. Different operational concern; out of scope.
- **Cost-driven prompt routing.** Choosing models per-request based on remaining budget. Research-frontier; not yet a stable production pattern.

## Related concepts

- [Adaptive sampling](./adaptive-sampling.md) — uses cost attributes from baggage to drive sampling decisions.
- [OpenTelemetry GenAI conventions](./opentelemetry-genai-conventions.md) — the span-attribute schema cost attribution sits on top of.
- [Lab 21 — cost attribution and adaptive sampling](../../labs/21-cost-attribution-and-adaptive-sampling/) — applies these patterns end-to-end.

## References

- Digital Applied (April 2026), *LLM Agent Cost Attribution: Complete Production 2026 Guide* — the three-dimension framing, four token layers, three-layer enforcement ladder, and the day-one instrumentation rule. [digitalapplied.com](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026).
- SoftwareSeni (April 2026), *Token Attribution and Cost Governance for Multi-Tenant LLM Products* — the five-element governance pattern (token layers, identifiers, daily caps, baseline alerts, cached-read counters). [softwareseni.com](https://www.softwareseni.com/token-attribution-and-cost-governance-for-multi-tenant-llm-products-in-production/).
- Portkey (January 2026), *Complete guide to LLM observability for 2026* — user/workspace context, model/provider details, token-and-cost metrics, guardrail signals as the seven observability dimensions. [portkey.ai/blog](https://portkey.ai/blog/the-complete-guide-to-llm-observability/).
- OneUptime (February 2026), *OpenTelemetry baggage for cross-cutting concerns* — the Python baggage API patterns, the 4KB limit, the four discipline rules. [oneuptime.com/blog](https://oneuptime.com/blog/post/2026-02-06-otel-baggage-propagation-business-context/view).
- OneUptime (February 2026), *W3C baggage propagation in OpenTelemetry* — the wire format, the extract/inject mechanics, the cost-attribution use case framing. [oneuptime.com/blog](https://oneuptime.com/blog/post/2026-02-06-w3c-baggage-propagation-opentelemetry/view).
- Digital Applied (May 2026), *Case Study: Agent Observability with LangFuse Rollout 2026* — the "User-ID and tenant-ID on every span via OTel baggage" rule; the 5x retrofit cost. [digitalapplied.com](https://www.digitalapplied.com/blog/case-study-agent-observability-langfuse-rollout-2026).
