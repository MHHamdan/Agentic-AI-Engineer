# Lab 21 · Reference solution

The polished final implementation of [Lab 21: Cost attribution and adaptive sampling](../README.md).

## What this is

Real OTel SDK with `ConsoleSpanExporter` + `SimpleSpanProcessor` so spans print inline. **Half A** instruments a planner → tool-caller → synthesizer agent with `OTel baggage` carrying tenant/user/task identity; tracks the four token layers as separate counter attributes; rolls up cost across 200 synthetic traces. **Half B** loads a production-realistic Collector YAML with composite policies; implements an external `AdaptiveSamplingController`; walks through the two-tier topology; computes the cost reduction at 1M traces/mo.

- **Baggage propagation primitive** — `baggage.set_baggage` + `context.attach` + `baggage.get_baggage`; demonstrated with an outer_function/inner_function pair where the inner function reads baggage without it being passed as an argument.
- **`request_baggage` context manager** — sets tenant.id / user.id / task.id / tenant.tier at request entry; cleanly detaches on exit.
- **Multi-step agent** — `planner` → `tool_call` × 2 → `synthesizer`; each step its own span; all read baggage and copy values to span attributes.
- **Four token layers** (`prompt`, `tool`, `memory`, `completion`) tracked as separate `gen_ai.usage.{layer}_tokens` attributes.
- **200-trace burn-down** across 5 tenants (weighted 60/20/10/7/3) and 5 task types — surfaces the canonical "acme-corp = 65.1% of spend" pattern.
- **Production Collector YAML** — 5-policy stack: errors → latency → high-cost → enterprise-tier → probabilistic.
- **`simulate_policies(traces, policies)`** — first-match-wins evaluation in Python.
- **`AdaptiveSamplingController` class** — quadratic-falloff sampling rate inversely proportional to remaining budget.
- **Two-tier topology YAMLs** — `loadbalancingexporter` (tier 1) + `tailsamplingprocessor` (tier 2).
- **Cost arithmetic at 1M traces/mo** — 88% ingestion-cost reduction at 12% production retention.

Deterministic via `random.seed(42)`.

## How it differs from `../lab.ipynb`

| Lab notebook (32 cells) | Solution (33 cells) |
|---|---|
| Multi-paragraph intros under every `### Step N` | One-line headers; tables and explanation preserved where they convey signal |
| Step 6's burn-down generation has a walkthrough of the synthesis logic | Same generation; the walkthrough is in the concept page |
| Step 10's `AdaptiveSamplingController` introduced piece by piece | Class defined once; the demo is a single output table |
| Sanity-test cells before each major function | Combined into the call sites that produce real output |

## Implementation choices

1. **`SimpleSpanProcessor` with `ConsoleSpanExporter` for lab visibility.** Spans print to stdout synchronously — the reader sees the propagation work happen. Production uses `BatchSpanProcessor` + `OTLPSpanExporter` for throughput, but neither is visible inline. The lab values visibility over realism here.
2. **The "set baggage early, set span attributes redundantly" pattern.** Baggage propagates implicitly across spans via OTel context; span attributes are the searchable index in the trace store. Both are required: baggage is the mechanism, attributes are the index. The `_add_identity_attributes(span)` helper makes the redundancy explicit.
3. **Quadratic falloff for the sampling rate** rather than linear or step function. At 100% remaining budget the rate is the configured max (10%); at 50% it's 25% of max; at 10% it's 1% of max — clamped to a 1% floor. The shape matches operational intuition: budget pressure should bite hard near the cap, lightly at headroom.
4. **The two-tier topology is shown as YAML, not deployed.** Tier 1 (`loadbalancingexporter` with `routing_key: traceID`) is the constraint that makes tail sampling work at scale; tier 2 runs the policy stack. Deploying it requires Docker + multi-node orchestration; out of scope for a notebook.
5. **`decision_wait=30s` and `num_traces=360000` as the agent-specific defaults** (re-emphasized from Lab 19). Default `decision_wait=10s` is wrong for agents; `num_traces = traces_per_sec × decision_wait × 1.2`.
6. **Token rates are synthetic but realistic.** $3/M for input layers (prompt/tool/memory), $15/M for completion — matches mid-2026 frontier-model cheap-tier pricing. The exact numbers don't matter for the demonstration; the per-layer breakdown does.

## What's deliberately out of scope

- **Prompt-caching cost math** (cached_read vs full pricing). The four-layer breakdown is the foundation; cached-read is a 2026-specific extension. Concept page references it.
- **FinOps tool integration** (Vantage, CloudZero, Apptio). Mentioned in concept pages; not implemented.
- **Usage forecasting** (linear extrapolation, ARIMA). Different discipline.
- **Real Collector deployment.** Docker, multi-node, OPAMP push. Out of scope.
- **Rate-limit infrastructure** (per-tenant Redis token bucket). Mentioned as the Layer-3 enforcement pattern; not implemented.

## Running the solution

```bash
cd labs/21-cost-attribution-and-adaptive-sampling/solution

# No external services needed
pip install opentelemetry-api opentelemetry-sdk pyyaml --break-system-packages

jupyter notebook lab.ipynb
```

**Wall-clock**: ~15-30 seconds. All synchronous; no LLM calls.

**Cost**: $0 — pure synthetic data + local OTel SDK.

## Reading the headline numbers

The canonical demonstration outputs (deterministic via `random.seed(42)`):

```
── Per-tenant burn-down ──
Tenant          Tier         Traces  Cost USD   % of total
acme-corp       enterprise      125    3.9909      65.1%
beta-startup    premium          35    1.1129      18.1%
delta-inc       standard         17    0.4701       7.7%
gamma-co        standard         15    0.4044       6.6%
epsilon-llc     standard          8    0.1558       2.5%

── Heaviest task ──
analysis ($0.058/trace average — long context + reasoning tokens dominate)

── Cost reduction at 1M traces/mo ──
Head-only ingestion:      $23.84/mo
Tail-sampled (12% retention): $2.86/mo
Savings: $20.98/mo (88% reduction)
```

The "one tenant burns 65% of spend" is the canonical pattern cost attribution catches — exactly the signal that justifies the instrumentation work.

## Next

- Take the [cost attribution and sampling quiz](../../../quizzes/evaluation/cost-and-sampling.md).
- Lab 22 closes Path 06 v1 with multi-turn (threaded) evaluation — the trajectory specialization on top of all prior modules.
