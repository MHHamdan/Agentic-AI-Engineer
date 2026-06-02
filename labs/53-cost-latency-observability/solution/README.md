# Lab 53 · Reference solution

The complete implementation of [Lab 53: Cost and latency observability](../README.md).

## What this is

- **`sessions.jsonl`** — 40 synthetic session traces (36 normal, 4 runaway loops). Each step records model, input/output tokens, the re-sent history portion, a tool call, duration, and a `simple` flag.
- **`cost.py`** — `session_cost` (tokens + runtime + tool calls), `cost_summary` (mean / p50 / p90 / p99 / max), `detect_runaways` (repeated tool-call signature), `resent_context_fraction`, `with_caching`, `route_cheaper`.

## Expected results

- mean ~$0.50 but p99 ~$4.91 (≈10× the mean).
- Runaways `r00`–`r03` flagged (one query repeated 45–60×).
- Re-sent context ~61% (normal) / ~90% (overall); caching ~54% off; routing ~47% off the routine bill.
- Budget gate: mean and p90 within a $1 budget, p99 breaches.

## Implementation choices

1. **Cost across three dimensions** (tokens, runtime, tools) in one accounting.
2. **Own the tail** — surface p90/p99, gate on p99.
3. **Two controls** — routing for routine spend, loop detection for runaways.

## What's out of scope

- OpenTelemetry GenAI instrumentation (synthetic traces here; live capture on the roadmap).
- A learned `simple`-step classifier for routing (the flag is given).
- Realistic TTL/write-premium caching (modeled as a flat multiplier).

## Running

```bash
cd labs/53-cost-latency-observability
python cost.py --self-test
python cost.py            # prints the cost summary
```

## Next

OpenTelemetry GenAI span instrumentation and a learned routing classifier.
