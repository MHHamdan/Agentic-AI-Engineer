# Lab 56 · Reference solution

The complete implementation of [Lab 56: Production traces and routing](../README.md).

## What this is

- **`make_tracer` / `instrument`** — emit one OpenTelemetry span per step with `gen_ai.*` semantic-convention attributes (system, model, input/output tokens) plus `agent.*` fields, via an in-memory exporter.
- **`steps_from_spans`** — reconstruct steps from the exported spans; the cost loop runs on these, matching the source exactly.
- **`routing_eval`** — a logistic-regression classifier predicts the `simple` flag from step features; held-out precision/recall, and routing saving on predictions vs oracle.

## Expected results

- 72 spans exported; cost from spans == cost from source.
- Classifier precision 1.00, recall 0.92; oracle saving 33%, learned saving 25% (the gap is misroutes).

## Implementation choices

1. **GenAI semantic conventions** so off-the-shelf tooling reads the spans.
2. **Loop on the trace store**, decoupled from the agent process.
3. **Learn the routing flag, then eval it** — misroutes are the cost of trusting the route blind.

## What's out of scope

- A real OTLP collector (in-memory exporter here; identical span shape).
- Rich routing features / retraining on drift (four features, one fit).

## Running

```bash
cd labs/56-production-traces-routing
python traces.py --self-test
```
