# Platform fanout and portability

> ⏱ ~10 min · 🔴 Advanced · Prerequisites: [OpenTelemetry GenAI semantic conventions](./opentelemetry-genai-conventions.md) (the standardization layer this page builds patterns on), [LangSmith tracing shape](./langsmith-tracing-shape.md) (the platform-native counterpart).

OpenTelemetry's standardization is structural: the same set of spans can land in any OTel-compatible backend. This page is the practical companion — how to actually wire that, when fanout (one set of spans, multiple backends) is worth the setup cost, and how the lock-in cost reframes once instrumentation is portable.

This page deliberately reframes a common mistake. Lock-in is usually phrased as "LangSmith locks you in" or "Phoenix locks you in." That's the wrong framing. The lock-in lives in the *instrumentation*, not the *platform*. Platform-native instrumentation is the lock-in; OTel-native instrumentation can target any platform, including the platforms that have native SDKs.

## The fanout pattern

One `TracerProvider`, multiple `SpanProcessor`s, each with its own exporter. The provider creates spans; the processors copy each span to their exporters. Same spans, multiple destinations.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor, SimpleSpanProcessor, ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

# One provider, identifying this process
resource = Resource.create({
    SERVICE_NAME: "my-agent-service",
    "deployment.environment": "production",
})
provider = TracerProvider(resource=resource)

# Multiple exporters attached as separate processors
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="https://api.smith.langchain.com/otel")
))
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="https://otlp.datadoghq.com/v1/otlp")
))
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

trace.set_tracer_provider(provider)
```

Every span the agent emits now lands in three places: LangSmith for the conversation-rendering UI, Datadog for the corporate service-map, and the local console for immediate dev visibility.

`BatchSpanProcessor` for production exporters — it batches spans and flushes asynchronously. `SimpleSpanProcessor` for console output during development — it exports each span immediately so you see it in real time.

## Three fanout configurations that matter in 2026

**Configuration 1 — Dev (console + LangSmith)**:

```
ConsoleSpanExporter → terminal output (immediate visibility)
OTLP → LangSmith /otel endpoint (UI, dataset workflow)
```

Console output during development is non-negotiable. Watching spans print as the agent runs catches bugs (missing attributes, wrong span kind, unexpected nesting) faster than checking the UI. Pair with LangSmith for the UI features.

**Configuration 2 — Staging/CI (LangSmith + APM)**:

```
OTLP → LangSmith (agent-native UI, evaluators)
OTLP → Datadog / Honeycomb / Grafana (unified service+LLM observability)
```

The corporate observability stack typically already exists. Adding LangSmith for agent-specific features (conversation rendering, evaluator registration, dataset workflow) doesn't replace the APM; it complements it. Fanout means one instrumentation maintained, two backends consumed.

**Configuration 3 — Production (multi-backend with collector)**:

```
Application → OpenTelemetry Collector (local agent)
  Collector → OTLP → LangSmith
  Collector → OTLP → Datadog
  Collector → OTLP → self-hosted Langfuse (compliance / data sovereignty)
```

The Collector is a separate process that sits between the application and the backends. It does:
- Buffering (handles back-pressure when one backend is slow).
- Filtering (route different spans to different backends).
- Sampling (tail-based sampling at the collector layer — Module 6 territory).
- Enrichment (add resource attributes the application doesn't have).

For agent observability specifically, LangChain ships [`langsmith-collector-proxy`](https://github.com/langchain-ai/langsmith-collector-proxy) — a specialized collector that filters non-GenAI spans (keeps only `gen_ai.*`, `langsmith.*`, `llm.*`, `ai.*` prefixes). Useful when your fleet emits OTel-everything and you want LangSmith to only see the GenAI subset.

## The platform landscape — what OTel changed

Pre-OTel, choosing an observability platform was choosing instrumentation. Each platform had its own SDK; switching meant rewriting instrumentation.

Post-OTel (and specifically after the LangSmith March 2026 native-OTel-SDK update), choosing a platform is choosing the UI. Instrumentation is portable.

**Platforms that lead in 2026 for agent-native observability**:

| Platform | OTel ingest | License | Where it helps |
|---|---|---|---|
| **LangSmith** | Native ingest at `/otel`; SDK is OTel-native as of March 2026 | Proprietary, self-host on Enterprise | LangChain/LangGraph ecosystem; conversation UI; agentevals workflow |
| **Arize Phoenix** | OTLP ingest; uses OpenInference (closely aligned with OTel GenAI) | Apache 2.0, open-source | Experiment tracking; evaluation-heavy teams |
| **Langfuse** | OTLP ingest | MIT, open-source | Self-host at any scale; prompt management; cost tracking |
| **Laminar** | OTel-native | Apache 2.0, open-source | Agent debugging; transcript view; SQL over traces |
| **Braintrust** | OTLP ingest | Proprietary | Eval-first workflows; regression testing |
| **OpenAI Agents native tracing** | Built-in | OpenAI | Tight OpenAI Agents SDK integration |

**APM tools that ingest GenAI OTel but aren't agent-native**:

| Tool | OTel ingest | Where it helps | What it lacks |
|---|---|---|---|
| **Datadog** | Native gen_ai support since v1.37 | Unified service+LLM observability; APM-mature UX | Conversation rendering; prompt-content search |
| **New Relic** | OTLP | Same | Same |
| **Honeycomb** | OTLP | Flame-graph debugging at scale; high-cardinality queries | Agent-conversation UI |
| **Grafana Tempo / Loki** | OTLP | Self-hosted, full-stack observability with metrics + logs + traces | Purpose-built agent UI |

The APM tools are mature; their service-map and latency-debugging UX is excellent. They're weak for agent debugging because they don't render runs as conversations. The agent-native platforms have purpose-built UIs but typically less mature service-map and APM-style features.

The hybrid pattern in 2026: corporate APM (Datadog or similar) for general service observability and SRE workflows; agent-native platform (LangSmith or Phoenix) for prompt debugging and conversation rendering. Both ingest the same OTel spans.

## The lock-in cost reframed

The naive framing — "Platform X locks you in" — is wrong. The platform doesn't lock you in; the platform-native SDK does. As of 2026:

**Platform-native instrumentation** (LangSmith's `@traceable`, Phoenix's `arize-phoenix-otel`, Langfuse's `@observe`):
- Lower setup cost.
- Tighter feature integration with the platform's purpose-built UI.
- Switching platforms = rewriting instrumentation.
- This is the lock-in.

**OTel-native instrumentation** (using the OpenTelemetry SDK directly with GenAI conventions):
- Higher setup cost up front.
- Some platform-specific UI features may need adaptation.
- Switching platforms = changing the exporter endpoint.
- This is portable.

The misconception: "I'll just use LangSmith's `@traceable` and switch later if needed." Switching means rewriting every decoration. Adding a second backend means double-instrumenting.

The OTel-native approach: instrument once with OTel; pick a backend; switch backends or add a second by changing exporter config. The setup cost is a few extra lines at startup. The portability is everything thereafter.

## When each path is the right pick

The decision boundary cleaner than "always OTel" or "always platform-native":

**Use platform-native instrumentation** (Lab 17 pattern) when:
- You're building inside a single ecosystem with no expectation of switching (a startup committed to LangChain, for example).
- You want the platform's UI features that depend on its data shape (LangSmith's dataset workflow, Phoenix's experiment tracking).
- The setup-time savings matter more than future flexibility.
- You're prototyping; lock-in cost is acceptable for the velocity payoff.

**Use OTel-native instrumentation** (Lab 18 pattern) when:
- You have existing observability infrastructure (corporate Datadog, self-hosted Grafana). Fanout is required, not optional.
- You expect to switch agent-observability platforms as the market shifts.
- Compliance or data-sovereignty requires self-hosted backends (Langfuse / Phoenix); you may need to fanout to a managed backend too for the UX.
- You're scaling from a single agent to many; platform standardization across multiple agent teams is easier with OTel.
- The team has OTel expertise (it's the same conventions you use for any other service).

**Use the hybrid pattern** when:
- You want platform-specific features (agentevals registration in LangSmith, experiment tracking in Phoenix) AND portability.
- OTel-native instrumentation + platform-native extensions for workflows the platform does well.

Most production agents land in one of these categories. Which one depends on team scale, ecosystem commitment, and existing infrastructure — not on which platform is "better."

## A concrete migration story

How a real team navigates the LangSmith-native → multi-backend journey:

**Stage 1 — Early prototyping (Lab 17 pattern)**: One engineer building a Lab 14-style supervisor agent. LangSmith-native `@traceable` everywhere. Setup is two env vars; instrumentation is decorators on the handful of helpers. Fast iteration; no infrastructure to maintain. Lock-in cost: zero, because there's nothing to migrate.

**Stage 2 — Production launch (still Lab 17 pattern)**: The agent ships. LangSmith free tier covers traces. Evaluators run online via the LangSmith UI. Annotation queue feeds back into a Dataset. Everything works.

**Stage 3 — Corporate adoption (Lab 18 pattern needed)**: A second team wants to use the agent infrastructure for a different product. Their observability runs on Datadog. They need agent traces in Datadog for the SRE on-call workflow. The Lab 17 platform-native instrumentation is suddenly a problem.

**Stage 4 — Migration to OTel-native**: Replace `@traceable` decorators with OTel manual spans (or `opentelemetry-instrumentation-langchain` auto-instrumentation). Configure fanout: OTLP → LangSmith + OTLP → Datadog. Both teams get the traces they need. Setup cost: roughly one sprint for a small codebase. Mistake to avoid: trying to maintain both instrumentation styles in parallel; pick one and migrate fully.

**Stage 5 — Multi-backend stable** (Lab 18 pattern matures): The team adds a third backend over time — self-hosted Langfuse for compliance, or Phoenix for experiment tracking — by adding a third processor. No rewrites; only configuration changes.

The lesson: starting with Lab 17 patterns is fine. Migrating to Lab 18 patterns is bounded work. Starting with Lab 18 patterns up front trades setup time for never having to migrate. Pick based on whether you expect Stage 3 to happen.

## What this misses

Things deferred to later modules:

- **Tail-based sampling at the OTel Collector layer.** Module 6. Keep failed/expensive/anomalous traces in full; drop most happy-path traces before they reach the backends.
- **Cost-attribution via OTel baggage.** Module 6. Propagate `tenant_id` / `user_id` through every span without per-span instrumentation.
- **Span-dropping under back-pressure.** When one exporter falls behind, what gets dropped first. Production tuning concern.
- **The OTel Collector deep-dive.** Worth its own page when we get to Module 6's production-scale topics.

## Related concepts

- [OpenTelemetry GenAI semantic conventions](./opentelemetry-genai-conventions.md) — the attribute names that make this fanout work.
- [LangSmith tracing shape](./langsmith-tracing-shape.md) — the platform-native counterpart this page reframes.
- [Lab 18 — OpenTelemetry portable tracing](../../labs/18-opentelemetry-portable-tracing/) — applies the fanout patterns end-to-end against a Lab 14-style agent.

## References

- LangChain blog (March 2026), *Introducing End-to-End OpenTelemetry Support in LangSmith* — the SDK-level OTel pivot that makes LangSmith viable as a fanout target with OTel-native instrumentation. [blog.langchain.com](https://blog.langchain.com/end-to-end-opentelemetry-langsmith/).
- LangChain docs, *Trace with OpenTelemetry* — the LangSmith OTLP endpoint configuration (`OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`). Also covers the self-hosted endpoint path (`/api/v1/otel`). [docs.langchain.com/langsmith](https://docs.langchain.com/langsmith/trace-with-opentelemetry).
- `langsmith-collector-proxy` repository — the GenAI-span-filtering collector pattern. [github.com/langchain-ai/langsmith-collector-proxy](https://github.com/langchain-ai/langsmith-collector-proxy).
- Laminar (April 2026), *Top 6 Agent Observability Platforms (2026)* — head-to-head comparison; LangSmith / Phoenix / Langfuse / Laminar / Weave / Braintrust positioning. [laminar.sh/article](https://laminar.sh/article/2026-04-23-top-6-agent-observability-platforms).
- OpenTelemetry Python docs, *Exporters* — the `OTLPSpanExporter`, `ConsoleSpanExporter`, fanout via multiple processors. [opentelemetry.io/docs/languages/python](https://opentelemetry.io/docs/languages/python/exporters/).
- oneuptime (Feb 2026), *How to Configure OpenTelemetry to Export to a Local Console During Development* — the env-gated dev-vs-prod exporter pattern. [oneuptime.com](https://oneuptime.com/blog/post/2026-02-06-otel-console-exporter-dev-otlp-prod/view).
