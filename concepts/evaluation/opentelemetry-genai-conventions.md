# OpenTelemetry GenAI semantic conventions

> ⏱ ~14 min · 🔴 Advanced · Prerequisites: [observability's three pillars](./observability-three-pillars.md) (the framing), [LangSmith tracing shape](./langsmith-tracing-shape.md) (the platform-native counterpart this page contrasts with).

Pre-2024, every observability vendor and every LLM framework shipped a different schema for tracing language-model calls. `model` vs `llm.model` vs `openai.model` — same idea, three different attribute names, three different queries to find the same data. Cross-platform debugging meant translating attribute names by hand; switching backends meant rewriting instrumentation.

OpenTelemetry's GenAI Special Interest Group (SIG) was formed in April 2024 to fix this. The output is a set of **semantic conventions** — standardized attribute names and span shapes for generative AI operations. The same instrumentation now produces traces every OTel-compatible backend understands. This page covers what stabilized, what's still experimental, and the concrete API patterns.

## The six layers of GenAI conventions

OpenTelemetry's GenAI conventions cover six telemetry types:

1. **Model spans** — one span per LLM API call. `gen_ai.system`, `gen_ai.request.model`, token usage, latency. The most mature layer; exited experimental for client spans in early 2026.
2. **Agent spans** — one span per agent invocation. `gen_ai.agent.name`, `gen_ai.agent.description`, `gen_ai.operation.name="invoke_agent"`. Still experimental but stable in practice.
3. **Client spans** — the top-level user-request boundary. Pairs with agent and model spans as nested children.
4. **Events** — chat history and request details, attached either to spans or as separate event records. The structure changed in v1.37 (more below).
5. **Exceptions** — error events with model-specific context (rate limits, content filter, context-window exceeded).
6. **Metrics** — aggregated counters and histograms (token-usage histogram, latency-by-model, error-rate-by-error-kind).

Each layer has its own maturity. Client spans are stable; agent and framework spans are still marked experimental but vendors are already shipping support. Events and metrics are following the same trajectory.

## Core attributes — what stabilized

The attribute set every GenAI-aware backend understands. These names are the actual standard; using them gets you cross-platform portability.

**Model and request**:
- `gen_ai.system` — the LLM provider (e.g., `openai`, `anthropic`, `aws.bedrock`, `gcp.vertex_ai`).
- `gen_ai.request.model` — the model name as requested (e.g., `gpt-4o-mini`, `claude-haiku-4-5`).
- `gen_ai.response.model` — the model name actually used (may differ when the API routes; matters for proxies and load-balancers).
- `gen_ai.request.temperature`, `gen_ai.request.max_tokens`, `gen_ai.request.top_p` — sampling parameters.
- `gen_ai.operation.name` — one of `chat`, `text_completion`, `embeddings`, `invoke_agent`, `execute_tool`.

**Token usage**:
- `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` — the cost-driving counters. Aggregated into the GenAI token-usage histogram metric.

**Tool calls**:
- `gen_ai.tool.name` — the tool function name.
- `gen_ai.tool.call.id` — unique ID linking the tool call to its result.
- `gen_ai.tool.description` — what the tool does (helps when you're debugging "did the agent pick the right tool").

**Agent spans**:
- `gen_ai.agent.name` — the agent's display name.
- `gen_ai.agent.description` — what the agent is for.
- `gen_ai.agent.id` — stable identifier for the agent across invocations.

A LangGraph supervisor agent producing a trace under these conventions looks like:

```
root span: kind=SERVER (top-level request)
├── gen_ai.agent span: kind=INTERNAL (supervisor agent)
│   gen_ai.agent.name=supervisor, gen_ai.operation.name=invoke_agent
│   ├── gen_ai.chat span: kind=CLIENT (supervisor's routing LLM call)
│   │   gen_ai.system=openai, gen_ai.request.model=gpt-4o-mini
│   │   gen_ai.usage.input_tokens=240, gen_ai.usage.output_tokens=45
│   ├── gen_ai.agent span: kind=INTERNAL (researcher agent)
│   │   ├── gen_ai.chat span: kind=CLIENT (researcher's LLM call)
│   │   └── gen_ai.tool span: kind=INTERNAL (web_search execution)
│   │       gen_ai.tool.name=web_search
│   └── gen_ai.agent span: kind=INTERNAL (writer agent)
│       └── gen_ai.chat span: kind=CLIENT (writer's LLM call)
```

Every backend that supports OTel ingests this trace identically. LangSmith renders it as a conversation; Datadog renders it as a service-map; Honeycomb renders it as a flame graph. The underlying data is the same.

## The v1.37 transition — per-message events to aggregated attributes

The v1.37 release of the GenAI conventions was a structural shift worth understanding. The earlier versions emitted one OTel event per message in a conversation — `gen_ai.user.message`, `gen_ai.assistant.message`, `gen_ai.tool.message` events attached to the span. The intent was to capture chat history without duplicating it across the span tree.

In practice this caused problems at production scale:
- Multi-turn conversations produced dozens of fine-grained events per span.
- Querying "show me all traces where the user asked X" required event-level full-text scanning.
- Correlation between events and the spans they belonged to was awkward in some backends.

v1.37 replaced the per-message events with three aggregated attributes on the span:

- `gen_ai.system_instructions` — the system prompt (sometimes large).
- `gen_ai.input.messages` — the conversation history sent to the model.
- `gen_ai.output.messages` — the response messages from the model.

Either set on the span directly or emitted as a single `gen_ai.client.inference.operation.details` event. The shift made multi-turn correlation a single query.

The transition is managed via an environment variable:

```bash
# Default: emit whatever version the instrumentation was emitting (v1.36 or prior)
# (no env var)

# Latest experimental: emit v1.37+ attributes, drop legacy events
OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental
```

For new code in 2026, set `gen_ai_latest_experimental`. For existing systems, the default keeps backward-compatibility until the conventions stabilize. Vendors will progressively switch their default emission as the conventions exit experimental status.

## The span kind discipline — the cheap-to-get-right, expensive-to-debug attribute

OpenTelemetry's `SpanKind` controls how downstream systems group spans. Five values, three relevant for agents:

- **CLIENT** — outgoing request to an external system. **Use for LLM API calls.** Without this, APMs like Datadog group LLM spans as "internal database operations" in service maps. Five minutes of head-scratching, two minutes to fix; getting it right up front is cheap.
- **INTERNAL** — code running inside your service. **Use for tool execution and agent spans.** The agent's local logic isn't a remote call; tool functions running in-process aren't either.
- **SERVER** — incoming request from outside. Use for the top-level user request when your service is a server. For a CLI agent, the root span is usually INTERNAL.

```python
from opentelemetry.trace import SpanKind

# LLM call — CLIENT
with tracer.start_as_current_span("gen_ai.chat", kind=SpanKind.CLIENT) as span:
    span.set_attribute("gen_ai.system", "openai")
    span.set_attribute("gen_ai.request.model", "gpt-4o-mini")
    response = openai_client.chat.completions.create(...)
    span.set_attribute("gen_ai.usage.input_tokens", response.usage.prompt_tokens)
    span.set_attribute("gen_ai.usage.output_tokens", response.usage.completion_tokens)

# Tool execution — INTERNAL
with tracer.start_as_current_span("gen_ai.execute_tool", kind=SpanKind.INTERNAL) as span:
    span.set_attribute("gen_ai.tool.name", "web_search")
    result = web_search(query)

# Agent invocation — INTERNAL
with tracer.start_as_current_span("gen_ai.invoke_agent", kind=SpanKind.INTERNAL) as span:
    span.set_attribute("gen_ai.agent.name", "supervisor")
    span.set_attribute("gen_ai.operation.name", "invoke_agent")
    result = supervisor.invoke(state)
```

The discipline matters because APMs use span kind to build service maps and group operations. Wrong kind = wrong visualization = harder debugging.

## Auto-instrumentation vs manual

Two paths produce the same conventions:

**Auto-instrumentation** — drop in a library that monkey-patches the SDK:

```python
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
OpenAIInstrumentor().instrument()

# From here, every openai.chat.completions.create() call auto-emits
# gen_ai.* attributes with kind=CLIENT. No per-call decoration.
```

The OpenAI Python SDK instrumentation is the most mature (started the project). Other available auto-instrumentors:
- `opentelemetry-instrumentation-anthropic`
- `opentelemetry-instrumentation-langchain` — covers LangChain + LangGraph
- `opentelemetry-instrumentation-cohere`
- `opentelemetry-instrumentation-bedrock`

The OpenLLMetry project (Traceloop, Apache 2.0, 7,100+ GitHub stars as of mid-2026) bundles auto-instrumentors for 8+ frameworks (LangChain, LlamaIndex, LangGraph, Haystack, CrewAI, Langflow, LiteLLM, OpenAI Agents). Now maintained as part of the official OpenTelemetry contrib.

**Manual instrumentation** — wrap calls yourself with the gen_ai attributes. The pattern shown in the span-kind section above. Useful when:
- You're using a provider without an auto-instrumentor.
- You need attributes the auto-instrumentor doesn't capture (custom metadata, request-correlation IDs).
- You're instrumenting non-LLM code that contributes to the agent (custom retrievers, business logic).

The pattern that works in production: auto-instrumentors for the provider SDKs you use; manual spans for the orchestration layer (agents, tools, custom retrievers) where auto-instrumentation doesn't reach.

## What this misses

A few things deliberately out of scope for this page — they belong in [the fanout/portability page](./platform-fanout-and-portability.md):
- How to wire multiple exporters from one TracerProvider.
- The platform landscape (LangSmith vs Phoenix vs Langfuse vs Datadog vs APM tools).
- Migration strategies between platforms via OTel-native instrumentation.

And a few things that are Module 6 territory:
- Tail-based sampling at the OTel Collector layer.
- Span dropping under back-pressure.
- Cost-attribution propagation via OTel baggage.

## Related concepts

- [Platform fanout and portability](./platform-fanout-and-portability.md) — the practical companion: how to use these conventions with multiple backends.
- [LangSmith tracing shape](./langsmith-tracing-shape.md) — the platform-native counterpart. LangSmith ingests both its native format and OTel.
- [Lab 18 — OpenTelemetry portable tracing](../../labs/18-opentelemetry-portable-tracing/) — applies the conventions to a Lab 14-style agent.
- [Lab 17 — LangSmith trace ingestion](../../labs/17-langsmith-trace-ingestion/) — the LangSmith-native counterpart lab.

## References

- OpenTelemetry GenAI semantic conventions (official spec): [opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/). Authoritative source; the six layers each have their own page.
- OpenTelemetry blog (March 2024), *OpenTelemetry for Generative AI* — the SIG kickoff announcement explaining the standardization problem. [opentelemetry.io/blog](https://opentelemetry.io/blog/2024/otel-generative-ai/).
- Greptime (May 2026), *How OpenTelemetry Traces LLM Calls, Agent Reasoning, and MCP Tools* — the six-layer overview; v1.37 transition rationale (per-message events to aggregated attributes); Elastic's 2026 observability report numbers. [greptime.com/blogs](https://www.greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions).
- DEV community (April 2026), *OpenTelemetry GenAI Semantic Conventions* — covers the experimental status as of March 2026, `OTEL_SEMCONV_STABILITY_OPT_IN` env var pattern, vendor-by-vendor support. [dev.to](https://dev.to/x4nent/opentelemetry-genai-semantic-conventions-the-standard-for-llm-observability-1o2a).
- maketocreate.com (May 2026), *OpenTelemetry GenAI: Tracing AI Agents Without Leaking PII* — the span-kind=CLIENT-on-LLM-calls gotcha with the Datadog service-map example. OpenLLMetry library coverage. [maketocreate.com](https://maketocreate.com/opentelemetry-genai-tracing-ai-agents-without-leaking-pii/).
- OpenTelemetry Python documentation, *Getting Started* — the manual-instrumentation patterns, `TracerProvider`, `BatchSpanProcessor`. [opentelemetry.io/docs/languages/python](https://opentelemetry.io/docs/languages/python/exporters/).
