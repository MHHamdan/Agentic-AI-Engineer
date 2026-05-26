# Lab 18 · Reference solution

The polished final implementation of [Lab 18: OpenTelemetry portable tracing](../README.md).

## What this is

A vendor-neutral OTel-instrumented supervisor agent. Same Lab 14-style agent as Lab 17; instrumentation moved from LangSmith-native to OpenTelemetry's GenAI semantic conventions. Fanout exports to LangSmith + console + (optional) Jaeger from a single `TracerProvider`.

- **`TracerProvider` + `Resource`** with `service.name` for backend filtering.
- **`ConsoleSpanExporter`** for inline visibility — spans print to stdout where the reader can see them.
- **Manual `gen_ai.chat` spans** with `SpanKind.CLIENT`, `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.{prompt,completion}_tokens`.
- **`OpenAIInstrumentor`** for auto-instrumentation — every `openai.chat.completions.create()` call becomes a span without manual wrapping.
- **`OTLPSpanExporter` pointing at LangSmith** — same backend as Lab 17, different ingest path.
- **Jaeger as a third backend** (optional, behind a flag) — demonstrates the fanout pattern.
- **`gen_ai.invoke_agent` span** wrapping the supervisor — the convention for agent-level operations.

## How it differs from `../lab.ipynb`

| Lab notebook (25 cells) | Solution (25 cells) |
|---|---|
| Per-step tutorial framing | One-line headers |
| Comparison with Lab 17 distributed across multiple cells | Single side-by-side table at the end |
| Optional Jaeger setup with extended walkthrough | Brief inline comment + run flag |
| Manual span construction shown step-by-step | Single setup cell with the full configured TracerProvider |

## Implementation choices

1. **`SimpleSpanProcessor` over `BatchSpanProcessor` for the lab.** Simple is synchronous — spans flush immediately, which is what you want when you're learning. Production uses Batch for throughput. The trade-off is throughput vs visibility.
2. **Fanout via multiple `SpanProcessor` instances on the same `TracerProvider`.** Each exporter is wrapped in its own processor. Adding a new backend is: `provider.add_span_processor(SimpleSpanProcessor(new_exporter))`. Nothing else changes.
3. **GenAI semantic conventions for attribute names.** `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.prompt_tokens` — these are the names every OTel-aware backend understands. Hand-rolling your own names (`llm.model`, `tokens.input`) means your traces are vendor-specific even though the SDK is portable.
4. **`OpenAIInstrumentor` for the LLM calls; manual spans for the agent-level operations.** The instrumentor handles per-LLM-call instrumentation automatically. The agent-level `gen_ai.invoke_agent` span is something the instrumentor can't auto-create — you mark it manually.
5. **`SpanKind.CLIENT` for LLM calls.** The agent is the client; the LLM (or LLM provider) is the server. This matters for backends that visualize trace dependencies.

## What's deliberately out of scope

- **Per-attribute redaction / PII filtering.** Production deployments redact prompt/completion content via custom span processors before export. Out of scope; concept page references the pattern.
- **OTel Collector deployment.** The lab exports directly to backends (LangSmith, Jaeger). Production deployments route through a Collector for buffering, retry, and policy enforcement (which Lab 19 covers).
- **Logs and metrics signals.** OTel covers traces + logs + metrics; this lab covers only traces. Logs and metrics for LLM observability are emerging — out of scope.
- **Multi-language traces.** OTel is multi-language by design but the lab is Python-only.
- **Trace sampling at the SDK level** (head sampling). Lab 19 handles tail sampling at the Collector level; head sampling is a separate operational concern.

## Running the solution

```bash
cd labs/18-opentelemetry-portable-tracing/solution

# Required
export OPENAI_API_KEY=...
export LANGCHAIN_TRACING_V2=true  # Re-enable LangSmith auto-tracing
export LANGCHAIN_API_KEY=...

# Optional — uncomment the Jaeger block in Step 7 to use this
# docker run -d --name jaeger -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one

jupyter notebook lab.ipynb
```

**Wall-clock**: ~2-4 minutes for the supervisor-agent runs. The OTel SDK overhead is negligible (<10ms per span).

**Cost**: ~$0.02-0.05 at gpt-4o-mini rates for the supervisor-agent LLM calls.

## Next

- Take the [OpenTelemetry portable quiz](../../../quizzes/evaluation/opentelemetry-portable.md).
- Lab 19 builds on this OTel foundation with tail-based sampling at the Collector — the production runtime layer that the SDK feeds.
