# Lab 56: Production traces and routing

> 🔴 Advanced · ⏱ ~85–105 min · 📚 Builds on Labs 51, 53 · Module 25

## 🎯 Goal

Labs 51 and 53 ran on hand-built data. In production the eval and cost loops should run on the traces the agent already emits, and the routing decision should be learned, not hand-set. This lab does both: instrument agent steps as OpenTelemetry GenAI spans, run the cost loop over the exported spans, and replace Lab 53's `simple` flag with a learned classifier that has its own eval.

By the end you should be able to:

- Emit GenAI-semantic-convention spans (`gen_ai.*`) for agent steps and export them.
- Reconstruct steps from the trace store and run the cost loop on them — decoupled from the agent.
- Train and evaluate a routing classifier, and reason about the cost of misroutes.

## 📋 Prerequisites

- 🧪 [Lab 53](../53-cost-latency-observability/) (the cost loop and the `simple` flag) and 🧪 [Lab 51](../51-calibrated-multidimensional/) (the eval loop).
- **Assumed background:** OpenTelemetry traces/spans, the GenAI semantic conventions, and basic supervised classification (precision/recall).

**Setup:** Python 3.11+; `opentelemetry-sdk` and `scikit-learn`. Spans export to an in-memory exporter (offline); production points the same instrumentation at an OTLP collector.

## 🛠 Module

| Component | Notes |
|---|---|
| `traces.py` | `make_tracer`/`instrument`/`steps_from_spans` (OTel); `routing_eval` (learned router); `token_cost` (`--self-test`) |

## What the numbers say

| | Result |
|---|---|
| GenAI spans exported | one per step, with `gen_ai.*` attributes |
| Cost loop on spans vs source | identical (the loop runs on traces) |
| Routing classifier | precision 1.00, recall 0.92 |
| Oracle vs learned saving | 33% vs 25% — the gap is misroutes |

## Design choices and tradeoffs

- **Instrument once, query anywhere.** Emitting GenAI-convention spans means the cost loop, the eval loop, and any third-party trace UI all read the same source. The loop reconstructs steps from spans, so it's decoupled from the agent's process — exactly what lets it run in a separate eval service.
- **Semantic conventions, not ad-hoc keys.** Using `gen_ai.usage.input_tokens` (not a custom name) means off-the-shelf tooling understands the spans. Agent-specific fields go under an `agent.*` namespace.
- **A learned router needs its own eval.** Routing on predictions recovers most of the oracle saving, but a misroute either overspends (a hard step sent cheap, then retried) or risks quality (a step that needed the strong model). You measure the routed path; you don't trust the route.

## Common gotchas

- **In-memory exporter is for tests.** Offline here; production uses an OTLP exporter to a collector. The span shape and reconstruction are identical, so the loop code doesn't change.
- **Misroutes are asymmetric.** A false "simple" (routing a hard step cheap) can cost quality, which is worse than the saving — weight the classifier's threshold toward precision on the "simple" class.
- **Retrain on drift.** The router is fit on current traffic; refit it as the workload shifts, like any model.

## 🧮 Going deeper

- 🧪 [Lab 53](../53-cost-latency-observability/) — the cost loop and routing this productionizes.
- 📖 [From stand-ins to production](../../concepts/observability/from-stand-ins-to-production.md) — the trace → eval/cost → gate pipeline.
- OpenTelemetry GenAI semantic conventions.

## What comes next

Wiring the instrumentation to a real OTLP collector and running the eval loop as a separate service that queries the trace backend.
