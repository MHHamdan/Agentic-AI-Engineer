# OTel collector for the agent trace pipeline

The runnable piece of "point `eval_service.py` at a real OTLP collector" (suggested-next item 3 from Batch 82). [Lab 56](../../labs/56-production-traces-routing/) exports GenAI spans; `eval_service.py` reads them from a JSONL stand-in. This bundle replaces the stand-in with a real collector and backend.

## Files

- `collector-config.yaml` — OTLP receiver (gRPC 4317 / HTTP 4318), a batch processor, a filter that keeps only `gen_ai.chat` spans, and exporters (debug + an example OTLP backend).
- `docker-compose.yml` — the collector plus an example trace backend (Tempo). `docker compose up`.

## Wiring the agent

Replace the in-memory exporter in `make_tracer()` with the OTLP exporter:

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")))
```

The span shape (the `gen_ai.*` semantic-convention attributes) is unchanged, so `eval_service.py`'s reconstruction logic is unchanged — only its source moves from a JSONL file to a backend query.

## Why a collector and not direct export

The collector decouples the agent from the backend: the agent speaks OTLP and nothing else, while batching, filtering (drop non-GenAI spans to bound cost), sampling, and routing to one or more backends live in the collector config — changeable without redeploying the agent.
