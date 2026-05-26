# Tail-based sampling for agent traces

> ⏱ ~12 min · 🔴 Advanced · Prerequisites: [OpenTelemetry GenAI semantic conventions](./opentelemetry-genai-conventions.md) (the trace shape we're sampling on), [platform fanout and portability](./platform-fanout-and-portability.md) (the OTel Collector positioning).

Lab 17 and Lab 18 emit 100% of agent traces. That's fine for a course lab. In production, where one agent might emit millions of traces per day across thousands of users, ingesting and storing 100% is wasteful — the happy-path traces dominate, the diagnostic gold (errors, slow runs, expensive runs) is buried, and your observability bill is mostly paying for data nobody queries.

Tail-based sampling is the discipline that fixes this. Keep 100% of error traces in full; keep 100% of high-latency traces; keep 100% of high-token-usage traces; keep a 5% probabilistic sample of the rest. Storage costs drop by an order of magnitude; diagnostic depth on the cases that matter stays intact.

This page covers the mechanism (where it lives, how policies are evaluated), the operational constraints (the load-balancing requirement that surprises teams at scale), and the decision boundary against LangSmith Rules from the previous page.

## Head-based vs tail-based — the canonical distinction

There are two places to make a sampling decision.

**Head-based sampling**: decide at trace start. The application either emits all spans for the trace or emits nothing. Random decision, typically a percentage. Cheap (no buffering). Blind — you don't know yet whether the trace will be interesting.

```python
# Head-based sampling at the SDK layer
sampler = TraceIdRatioBased(rate=0.10)  # keep 10% of traces, decided at trace start
```

If a trace turns out to error at step 5 of 10, head sampling has already decided whether to keep it before step 1 ran. 90% of errors get dropped along with 90% of happy-path traces. Diagnostic value: low.

**Tail-based sampling**: decide at trace end. Buffer all spans for a trace; once the trace completes (or a timeout elapses), inspect its contents — span statuses, attributes, total duration — and decide whether to keep, drop, or sample. Informed. More expensive (requires buffering).

```yaml
# Tail-based sampling in the OTel Collector
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors                # Keep 100% of error traces
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: high-latency          # Keep 100% of slow traces
        type: latency
        latency: { threshold_ms: 30000 }
      - name: baseline              # 5% of the rest
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

Same 10% net sampling rate; vastly different diagnostic value. Errors are 100% retained. Slow traces are 100% retained. Happy-path traces get a 5% representative sample.

Head sampling is fine for low-volume systems where storage isn't the binding constraint. Tail sampling is the production discipline at agent-trace scale, where errors and slow traces are rare and storage is expensive.

## Where tail sampling lives

Tail sampling **doesn't live in the application**. The application emits 100% of spans; the OTel Collector decides what to forward downstream. This is critical because:

- The application doesn't know yet which traces will error or be slow when it emits the first span.
- Buffering all spans in the application's memory would couple instrumentation to evaluation logic, making the application heavier.
- Sampling decisions should apply uniformly across backends — if you fan out to LangSmith and Datadog, both should see the same sampled subset.

The Collector sits between the application and the backends. The standard topology:

```
Application (emits 100%) → OTel Collector (tail_sampling processor) → Backends (LangSmith, Datadog, etc.)
```

The `tailsamplingprocessor` is shipped in `opentelemetry-collector-contrib`. It's a separate process, typically deployed as a sidecar (per-pod) or as a daemonset (per-node). Configuration is YAML.

## Standard policies

The `tail_sampling` processor supports several policy types. The ones that matter for agent traces:

**`status_code`** — sample based on whether the trace has any error spans. Standard usage: keep 100% of traces with at least one `ERROR` status.

**`latency`** — sample based on the trace's total duration (earliest start to latest end). Standard usage: keep 100% of traces over a threshold (e.g., 30 seconds).

**`numeric_attribute`** — sample based on a numeric attribute matching a range. For agent traces specifically: keep 100% of traces where `gen_ai.usage.input_tokens > 5000` (these are the expensive runs you want to inspect), or where `gen_ai.usage.output_tokens > 2000` (long generations that may indicate a runaway).

**`string_attribute`** — sample based on a string attribute matching a value or pattern. Useful for keeping all traces from specific users (debug accounts, beta-tester cohorts).

**`probabilistic`** — random sampling at a configured percentage. Standard baseline: 5-10% of everything that didn't already match a higher-priority policy.

**`boolean_attribute`** — keep traces where a boolean attribute is true. Common for keeping traces flagged by upstream classifiers.

**`composite`** — combine multiple policies with AND/OR. For complex conditions like "errors OR (long-latency AND high-token-usage)".

Policies are evaluated in declared order. **First match wins.** This is why the policy stack reads top-down from most diagnostic to least: errors first, then latency, then expensive runs, then baseline.

## A production policy stack

A representative configuration for a Lab 18-style agent in production:

```yaml
processors:
  tail_sampling:
    # Wait 10 seconds for late spans before deciding. Longer is safer; uses more memory.
    decision_wait: 10s
    # Memory budget: traces/sec × decision_wait × safety_margin
    # At 100 traces/sec, decision_wait=10s, safety_margin=2x: 2000 traces in memory
    num_traces: 2000
    expected_new_traces_per_sec: 100
    policies:
      # ──── KEEP 100% ────
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]

      - name: high-latency
        type: latency
        latency:
          threshold_ms: 30000

      - name: high-token-usage
        type: numeric_attribute
        numeric_attribute:
          key: gen_ai.usage.input_tokens
          min_value: 5000

      - name: debug-users
        type: string_attribute
        string_attribute:
          key: user.id
          values: [debug-1, debug-2, beta-cohort-a]

      # ──── BASELINE: 5% of everything else ────
      - name: baseline-sample
        type: probabilistic
        probabilistic:
          sampling_percentage: 5
```

At 100 traces/sec with an error rate of 0.5%, a high-latency rate of 0.3%, a high-token-usage rate of 1%, and a debug-user fraction of 0.1%, the net retention is approximately:

```
0.5% + 0.3% + 1.0% + 0.1% + 5% × (1 - 0.019) = 6.8% retained, 93.2% dropped
```

Storage cost drops by ~14x. Diagnostic depth on errors stays at 100%. The probabilistic baseline retains enough happy-path traces to compute aggregate metrics (volume, mean latency, mean tokens/trace) for the dashboard.

## The load-balancing constraint

The constraint that surprises teams at production scale: **all spans for a given trace must reach the same Collector instance.** Tail sampling needs to see the whole trace to evaluate latency, look at the status of every span, check whether any span has the high-token-usage attribute. If half the trace's spans go to Collector A and the other half to Collector B, neither can make an informed decision.

In a single-instance Collector deployment, this is automatic. At scale, when you need multiple Collectors for throughput, the problem appears. The fix is the **two-tier topology**:

```
Application → Agent Collector (per-pod / per-host) → Tail-sampling Collector layer
                                                                  ↓
                                              Routed by trace_id via loadbalancingexporter
                                                                  ↓
                                                      Tail-sampling Collector pool → Backends
```

The agent collectors are the receivers; they use the `loadbalancingexporter` (also in `opentelemetry-collector-contrib`) to route each span to a specific tail-sampling collector based on the span's `trace_id`. Hashing on `trace_id` ensures every span of the same trace lands on the same downstream collector. The tail-sampling collectors then have full traces in their buffers and can decide correctly.

If you skip this and run multiple tail-sampling collectors directly behind a generic load balancer (round-robin, least-connections), traces get split across instances and sampling decisions are wrong. **Failure mode**: high-latency traces appear sometimes-kept-sometimes-dropped randomly; errors get partially captured (some error spans kept, other spans of the same trace missing). Debugging this is awful — the symptom is "the tail sampling looks broken but the config is correct."

## Memory budget

The Collector buffers complete traces in memory while waiting for late spans. The memory budget needs to accommodate:

```
num_traces ≈ expected_new_traces_per_sec × decision_wait × safety_margin
```

At 100 traces/sec, `decision_wait=10s`, `safety_margin=2x`: 2000 traces. If a single trace averages 50 KB, that's 100 MB. Manageable.

At 10,000 traces/sec, `decision_wait=10s`, `safety_margin=2x`: 200,000 traces. At 50 KB each, that's 10 GB. Now the Collector needs significant memory; you may want to scale horizontally with the load-balancer-plus-tail-sampling two-tier topology, with each tail-sampling instance handling a slice of trace_id space.

The `decision_wait` knob is the lever for memory-vs-completeness. Shorter waits use less memory but risk missing late spans. Longer waits use more memory but capture more complete traces. 10 seconds is the conventional default; agent traces with long-running tool calls may need 30-60 seconds.

## When tail sampling earns its place vs LangSmith Rules

Both are "sample intelligently in production." They operate at different layers and trade off differently.

| | LangSmith Automation Rules | OTel Collector tail sampling |
|---|---|---|
| **Layer** | Platform (after ingestion) | Collector (before ingestion) |
| **What you save** | UI processing time, evaluator cost on uninteresting traces | Network egress, ingestion fees, storage cost |
| **Granularity** | Per-trace, after the trace is in LangSmith | Per-trace, in-flight |
| **Configurability** | LangSmith UI; six action types | YAML config; multiple policy types; first-match-wins |
| **Vendor scope** | LangSmith only | Vendor-neutral; applies to every backend the Collector exports to |
| **Buffering required?** | No (LangSmith already has the trace) | Yes (Collector buffers full traces) |
| **Best for** | "Run online evaluator only on 10% of traces"; "route errors to annotation queue"; "promote failures to dataset" | "Drop 95% of happy-path traces before they hit storage"; "keep all errors and high-cost traces" |

The patterns complement each other. Tail sampling at the Collector reduces what reaches the platform; Rules at the platform decide what to do with what arrived. Production-scale agent observability uses both:

1. Collector tail-samples to keep `errors + high-latency + high-cost + 5% baseline`.
2. Sampled traces reach LangSmith (and Datadog, and whatever else is downstream).
3. LangSmith Rules fire on what's now a manageable volume: 10% of incoming traces get LLM-as-judge evaluation, errors get routed to annotation queue.

Doing both is the production pattern. Skipping tail sampling means paying for trace storage you don't need. Skipping Rules means accumulating low-quality traces in the platform without any automated triage. Doing one without the other works at small scale; both are needed at production scale.

## When you don't need tail sampling

Three cases where 100% retention is fine:

- **Development and CI traffic.** Volume is bounded; storage cost is negligible; you want every trace for debugging. Skip tail sampling; route everything to LangSmith.
- **Low-volume production.** If you're at 10 traces/minute, the math doesn't justify the operational cost of a Collector deployment. Keep everything; revisit when you hit 10 traces/second.
- **Compliance scenarios** where you must retain 100% of traces for a regulated period. Tail sampling is incompatible with "retain everything." Use longer-term cold storage instead.

For everything else — most production agent deployments — tail sampling at the Collector is the right starting point. The 5-10x storage savings pay for the operational complexity quickly.

## What this misses

Out of scope for this page; covered later:

- **Cost-attribution propagation via OTel baggage.** Module 6. Required for "keep all traces from tenant X" patterns that depend on context flowing through the trace.
- **Adaptive sampling.** Where the sample rate adjusts dynamically based on observed error rate or quality scores. Module 6.
- **Drift detection on the sampled subset.** Module 5. When tail sampling biases the distribution, naive drift detection on the sampled subset can be misleading.

## Related concepts

- [Online evaluator registration](./online-evaluator-registration.md) — the platform-side complement.
- [Platform fanout and portability](./platform-fanout-and-portability.md) — where the OTel Collector sits in the topology.
- [OpenTelemetry GenAI semantic conventions](./opentelemetry-genai-conventions.md) — the `gen_ai.*` attributes tail sampling policies operate on.
- [Lab 19 — online evaluation and sampling](../../labs/19-online-evaluation-and-sampling/) — the lab applies these patterns end-to-end against synthetic trace streams.

## References

- OpenTelemetry collector-contrib, *tailsamplingprocessor* README — the canonical reference for policy types, configuration knobs, scaling guidance. [github.com/open-telemetry/opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor).
- Grafana docs (2026), *Tail sampling* — applied guide with policy examples and Grafana Alloy alternative. [grafana.com/docs/opentelemetry/collector/sampling/tail](https://grafana.com/docs/opentelemetry/collector/sampling/tail/).
- oneuptime (January 2026), *How to Configure the Tail Sampling Processor in the OpenTelemetry Collector* — production-config example with memory-budget arithmetic, error-status policies. [oneuptime.com](https://oneuptime.com/blog/post/2026-02-06-tail-sampling-processor-opentelemetry-collector/view).
- oneuptime (February 2026), *How to Use Tail-Based Trace Sampling Using OpenTelemetry Collector Load Balancing* — the two-tier topology with `loadbalancingexporter` for multi-instance deployments. [oneuptime.com](https://oneuptime.com/blog/post/2026-02-09-tail-based-trace-sampling-otel/view).
- OpenTelemetry docs, *Tail-based sampling* — head-vs-tail decision rationale, language-level alternatives (some SDKs ship in-process tail samplers as previews). [opentelemetry.io/docs](https://opentelemetry.io/docs/languages/dotnet/traces/tail-based-sampling/).
