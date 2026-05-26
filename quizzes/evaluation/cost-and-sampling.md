---
quiz_id: cost-and-sampling
title: Cost attribution and adaptive sampling
path: 06-evaluation-observability
module: 6
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "Which of the following is the canonical reason to instrument cost attribution on day one of an agent's deployment, rather than retrofitting later from logs?"
    options:
      - "Day-one instrumentation produces prettier dashboards"
      - "Retroactive log-tagging misses tool spans, partial traces, and timeout edge cases — building all three attribution dimensions (per-tenant, per-user, per-task) up front costs roughly 5x less than retrofitting them later"
      - "Log volume is too high to query after the fact"
      - "OpenTelemetry doesn't support post-hoc tagging"
    answer: "Retroactive log-tagging misses tool spans, partial traces, and timeout edge cases — building all three attribution dimensions (per-tenant, per-user, per-task) up front costs roughly 5x less than retrofitting them later"
  - id: q2
    text: "Why track the four token layers (prompt, tool, memory, response) as separate span attributes rather than aggregating into 'input' and 'output' counters?"
    options:
      - "OpenAI's API requires the breakdown for billing"
      - "Each layer has different optimization levers (prompt caching for prompt layer, tool-spec compression for tool layer, RAG tuning for memory layer); aggregating to input/output hides which lever to pull"
      - "Total cost is more accurate when you sum four numbers"
      - "The OTel GenAI conventions require it"
    answer: "Each layer has different optimization levers (prompt caching for prompt layer, tool-spec compression for tool layer, RAG tuning for memory layer); aggregating to input/output hides which lever to pull"
  - id: q3
    text: "You set `tenant.id` and `user.id` in OTel baggage at the API gateway. A downstream function reads them with `baggage.get_baggage('tenant.id')` and uses the values, but the trace store has no `tenant.id` field to filter by. What's missing?"
    options:
      - "The W3C Baggage header propagator wasn't registered"
      - "You also need to call `span.set_attribute('tenant.id', tenant_id)` in each span — baggage is the propagation mechanism, but the trace store queries span attributes, not baggage entries. Both are required."
      - "Baggage doesn't work with the OTLP exporter"
      - "Baggage entries expire after 30 seconds"
    answer: "You also need to call `span.set_attribute('tenant.id', tenant_id)` in each span — baggage is the propagation mechanism, but the trace store queries span attributes, not baggage entries. Both are required."
  - id: q4
    text: "Which Collector tail-sampling policy type would you use to keep 100% of traces whose cumulative cost exceeds $0.10?"
    options:
      - "`status_code` with status_codes: [EXPENSIVE]"
      - "`probabilistic` with sampling_percentage: 100"
      - "`numeric_attribute` on `gen_ai.cost.total_usd` with min_value: 0.10"
      - "`latency` with threshold_ms: 1000 (since expensive traces are usually slow)"
    answer: "`numeric_attribute` on `gen_ai.cost.total_usd` with min_value: 0.10"
  - id: q5
    text: "You scale your OTel Collector from one instance to three for capacity. Tail sampling starts producing inconsistent results — some traces are missing error spans, latency policies don't fire reliably. What's the most likely cause?"
    options:
      - "The probabilistic policy is dropping the wrong traces"
      - "Tail sampling requires all spans of a trace to reach the same Collector instance. Without a `loadbalancingexporter` first-tier routing by trace_id, spans of the same trace get distributed across Collectors, leaving each with an incomplete view."
      - "decision_wait is set too high"
      - "The status_code policy was configured incorrectly"
    answer: "Tail sampling requires all spans of a trace to reach the same Collector instance. Without a `loadbalancingexporter` first-tier routing by trace_id, spans of the same trace get distributed across Collectors, leaving each with an incomplete view."
  - id: q6
    text: "How does adaptive sampling tied to cost actually work in practice?"
    options:
      - "The Collector auto-tunes its sampling rates based on built-in cost signals"
      - "An external controller polls per-tenant cost metrics, computes new sampling parameters (e.g., reduced rate for tenants approaching budget), and pushes config updates to the Collector via file write, OPAMP, or remote-config endpoint. The Collector itself reads static YAML."
      - "Sampling rates self-adjust based on trace store backpressure"
      - "OpenTelemetry provides a built-in adaptive sampler that requires no external service"
    answer: "An external controller polls per-tenant cost metrics, computes new sampling parameters (e.g., reduced rate for tenants approaching budget), and pushes config updates to the Collector via file write, OPAMP, or remote-config endpoint. The Collector itself reads static YAML."
  - id: q7
    text: "Your team wants to add ten new identity fields to baggage (org.id, project.id, environment, region, four feature_flag values, etc.). What's the most important constraint to check?"
    options:
      - "OpenTelemetry only supports 5 baggage keys"
      - "The W3C Baggage spec caps total baggage size at 4KB across all entries; ten fields with non-trivial values risk exceeding this and silently truncating propagation. Use IDs only, not full objects, and validate the total at the API gateway."
      - "Baggage doesn't propagate across async boundaries"
      - "The Collector charges per baggage key processed"
    answer: "The W3C Baggage spec caps total baggage size at 4KB across all entries; ten fields with non-trivial values risk exceeding this and silently truncating propagation. Use IDs only, not full objects, and validate the total at the API gateway."
  - id: q8
    text: "Cost attribution dashboards show a single tenant burning 80% of last week's budget. The three-layer enforcement ladder recommends what response — and what response NOT to take?"
    options:
      - "Immediately throttle the tenant; ask questions later"
      - "Layer 1 (dashboards) shows the signal. Layer 2 (alerts) should already have fired at 2x baseline; Layer 3 (rate-limit tightening) automatically reduces budget for over-burn tenants pending human review. Premature Layer-3 deployment without calibration is the classic 'auto-throttled a real customer's legitimate burst' failure mode, so deploy the ladder incrementally."
      - "Disable the tenant's account permanently"
      - "Ignore the signal — cost attribution dashboards are advisory only"
    answer: "Layer 1 (dashboards) shows the signal. Layer 2 (alerts) should already have fired at 2x baseline; Layer 3 (rate-limit tightening) automatically reduces budget for over-burn tenants pending human review. Premature Layer-3 deployment without calibration is the classic 'auto-throttled a real customer's legitimate burst' failure mode, so deploy the ladder incrementally."
---

# Cost attribution and adaptive sampling · 🧠 Check your understanding

Calibrate against the [cost-attribution](../../concepts/evaluation/cost-attribution.md) and [adaptive-sampling](../../concepts/evaluation/adaptive-sampling.md) concept pages plus [Lab 21](../../labs/21-cost-attribution-and-adaptive-sampling/). 8 single-select questions covering attribution mechanics, sampling policies, and the production decision boundary. Passing: 6/8.

---

**1.** Which of the following is the canonical reason to instrument cost attribution on day one of an agent's deployment, rather than retrofitting later from logs?

- (a) Day-one instrumentation produces prettier dashboards
- (b) Retroactive log-tagging misses tool spans, partial traces, and timeout edge cases — building all three attribution dimensions (per-tenant, per-user, per-task) up front costs roughly 5x less than retrofitting them later
- (c) Log volume is too high to query after the fact
- (d) OpenTelemetry doesn't support post-hoc tagging

<details>
<summary>Answer</summary>

**(b)** — The day-one rule is well-documented in 2026 production case studies (Digital Applied's LangFuse rollout: "User-ID and tenant-ID on every span via OTel baggage. Ad-hoc argument passing always loses identity at the first tool boundary"). The 5x retrofit cost comes from the same source. Retroactive joining misses tool spans (which have their own identity context that isn't in the application log), partial traces (timeouts where the trace never completes don't make it to the trace store), and edge cases like async boundaries where the active context isn't propagated.

See: [cost-attribution.md → "The three attribution dimensions"](../../concepts/evaluation/cost-attribution.md#the-three-attribution-dimensions).
</details>

---

**2.** Why track the four token layers (prompt, tool, memory, response) as separate span attributes rather than aggregating into 'input' and 'output' counters?

- (a) OpenAI's API requires the breakdown for billing
- (b) Each layer has different optimization levers (prompt caching for prompt layer, tool-spec compression for tool layer, RAG tuning for memory layer); aggregating to input/output hides which lever to pull
- (c) Total cost is more accurate when you sum four numbers
- (d) The OTel GenAI conventions require it

<details>
<summary>Answer</summary>

**(b)** — The diagnostic value of cost attribution comes from being able to point at which layer is dominating. "Token usage is up 40%" is not actionable; "memory token usage is up 80% on summarization tasks" is. The four layers each have distinct optimization machinery — prompt caching cuts prompt tokens; tool-spec compression cuts tool tokens; RAG-corpus pruning cuts memory tokens. Aggregating into "input" hides which lever to pull.

(a) is false (OpenAI bills on raw input/output). (d) is partly true (the GenAI conventions provide `prompt_tokens` and `completion_tokens`; the four-layer breakdown is an extension that's becoming the convention in 2026 production deployments). (c) is meaningless; the same total comes out either way.

See: [cost-attribution.md → "The four token layers"](../../concepts/evaluation/cost-attribution.md#the-four-token-layers).
</details>

---

**3.** You set `tenant.id` and `user.id` in OTel baggage at the API gateway. A downstream function reads them with `baggage.get_baggage('tenant.id')` and uses the values, but the trace store has no `tenant.id` field to filter by. What's missing?

- (a) The W3C Baggage header propagator wasn't registered
- (b) You also need to call `span.set_attribute('tenant.id', tenant_id)` in each span — baggage is the propagation mechanism, but the trace store queries span attributes, not baggage entries. Both are required.
- (c) Baggage doesn't work with the OTLP exporter
- (d) Baggage entries expire after 30 seconds

<details>
<summary>Answer</summary>

**(b)** — This is the single most common cost-attribution implementation mistake. Baggage is the propagation primitive; it carries values across span boundaries via the implicit OTel context. But the trace store (Tempo, Jaeger, ClickHouse, OpenSearch) indexes span attributes, not baggage entries. To query by `tenant.id`, every span needs a `tenant.id` attribute. The pattern is: read baggage, copy to span attribute. Both are required.

(a) is plausible but would prevent baggage from working at all (the function couldn't read it). (c) is false. (d) is false (baggage entries persist as long as the context is attached).

See: [cost-attribution.md → "OTel baggage — the propagation primitive"](../../concepts/evaluation/cost-attribution.md#otel-baggage--the-propagation-primitive).
</details>

---

**4.** Which Collector tail-sampling policy type would you use to keep 100% of traces whose cumulative cost exceeds $0.10?

- (a) `status_code` with status_codes: [EXPENSIVE]
- (b) `probabilistic` with sampling_percentage: 100
- (c) `numeric_attribute` on `gen_ai.cost.total_usd` with min_value: 0.10
- (d) `latency` with threshold_ms: 1000 (since expensive traces are usually slow)

<details>
<summary>Answer</summary>

**(c)** — `numeric_attribute` is the policy type that compares a numeric span attribute against a threshold. The Collector ships with this in `opentelemetry-collector-contrib`'s `tailsamplingprocessor`. The min_value clamp keeps all traces at or above the threshold.

(a) EXPENSIVE isn't a valid status code; `status_code` matches OK/ERROR/UNSET. (b) probabilistic at 100% would keep everything, not just expensive traces. (d) is the wrong proxy — expensive traces are *correlated* with latency but the correlation isn't tight enough to rely on; e.g., a single expensive reasoning call can finish fast.

See: [adaptive-sampling.md → "Cost-driven policies in the tail sampling processor"](../../concepts/evaluation/adaptive-sampling.md#cost-driven-policies-in-the-tail-sampling-processor).
</details>

---

**5.** You scale your OTel Collector from one instance to three for capacity. Tail sampling starts producing inconsistent results — some traces are missing error spans, latency policies don't fire reliably. What's the most likely cause?

- (a) The probabilistic policy is dropping the wrong traces
- (b) Tail sampling requires all spans of a trace to reach the same Collector instance. Without a `loadbalancingexporter` first-tier routing by trace_id, spans of the same trace get distributed across Collectors, leaving each with an incomplete view.
- (c) decision_wait is set too high
- (d) The status_code policy was configured incorrectly

<details>
<summary>Answer</summary>

**(b)** — This is the canonical "tail sampling at scale" failure mode and the reason the two-tier topology exists. Tail policies inspect attributes across all spans in a trace. If the agent's planner-span lands on Collector A and the synthesizer-error-span lands on Collector B, neither has the full trace. The error policy on B sees the error span and keeps that fragment; A sees no error and probabilistically drops its half. The result is half-traces in the store.

The fix is the two-tier pattern: tier 1 runs `loadbalancingexporter` with `routing_key: traceID`, which hashes trace_id and routes all spans of the same trace to the same tier-2 Collector. The tier-2 Collectors run `tailsamplingprocessor` on their sticky subsets and see complete traces.

See: [adaptive-sampling.md → "The two-tier Collector topology"](../../concepts/evaluation/adaptive-sampling.md#the-two-tier-collector-topology).
</details>

---

**6.** How does adaptive sampling tied to cost actually work in practice?

- (a) The Collector auto-tunes its sampling rates based on built-in cost signals
- (b) An external controller polls per-tenant cost metrics, computes new sampling parameters (e.g., reduced rate for tenants approaching budget), and pushes config updates to the Collector via file write, OPAMP, or remote-config endpoint. The Collector itself reads static YAML.
- (c) Sampling rates self-adjust based on trace store backpressure
- (d) OpenTelemetry provides a built-in adaptive sampler that requires no external service

<details>
<summary>Answer</summary>

**(b)** — The Collector's `tailsamplingprocessor` reads static YAML at startup (and on config reload). "Adaptive" here means an external controller component watches signals (per-tenant cost, latency p95, etc.) and pushes updated configs. The lab demonstrates this with an `AdaptiveSamplingController` class that reads burn rates and emits new rate tables.

Production deployments use one of three push mechanisms: (1) file-watching reload — write new YAML to disk; (2) OPAMP — the OTel control-plane protocol GA in 2026; or (3) sidecar with a remote-config endpoint. The controller logic itself is a small service or sidecar; the math is what the lab shows.

(a) and (d) describe the wishful-thinking version. (c) is the reverse — backpressure should never drive sampling decisions; it should drive batch sizes or buffer sizing.

See: [adaptive-sampling.md → "The external control loop"](../../concepts/evaluation/adaptive-sampling.md#the-external-control-loop).
</details>

---

**7.** Your team wants to add ten new identity fields to baggage (org.id, project.id, environment, region, four feature_flag values, etc.). What's the most important constraint to check?

- (a) OpenTelemetry only supports 5 baggage keys
- (b) The W3C Baggage spec caps total baggage size at 4KB across all entries; ten fields with non-trivial values risk exceeding this and silently truncating propagation. Use IDs only, not full objects, and validate the total at the API gateway.
- (c) Baggage doesn't propagate across async boundaries
- (d) The Collector charges per baggage key processed

<details>
<summary>Answer</summary>

**(b)** — The 4KB limit is the W3C Baggage spec's hard cap. It's *per-request*, summed across all entries, encoded as the `baggage:` HTTP header. Ten fields × ~50 bytes each = 500 bytes; ten fields × ~500 bytes each (e.g., feature-flag arrays, configuration blobs) = 5KB which exceeds the limit. When the header is too long, intermediate proxies may silently truncate it, and downstream services see partial baggage with no indication of the truncation. The discipline: IDs only, no full objects, no PII, no secrets, allowlist at the Collector.

(a) is false (no key-count limit). (c) is false in Python — OTel uses contextvars which are async-safe. (d) is false (Collector cost is per-trace and per-span, not per-baggage-key).

See: [cost-attribution.md → "The four rules of baggage discipline"](../../concepts/evaluation/cost-attribution.md#the-four-rules-of-baggage-discipline).
</details>

---

**8.** Cost attribution dashboards show a single tenant burning 80% of last week's budget. The three-layer enforcement ladder recommends what response — and what response NOT to take?

- (a) Immediately throttle the tenant; ask questions later
- (b) Layer 1 (dashboards) shows the signal. Layer 2 (alerts) should already have fired at 2x baseline; Layer 3 (rate-limit tightening) automatically reduces budget for over-burn tenants pending human review. Premature Layer-3 deployment without calibration is the classic 'auto-throttled a real customer's legitimate burst' failure mode, so deploy the ladder incrementally.
- (c) Disable the tenant's account permanently
- (d) Ignore the signal — cost attribution dashboards are advisory only

<details>
<summary>Answer</summary>

**(b)** — The three-layer ladder is incremental. Layer 1 (dashboards) is the reporting view. Layer 2 (alerts) fires when per-tenant spend exceeds rolling-baseline thresholds (typically 2x warning, 5x critical) and routes to on-call. Layer 3 (rate-limit tightening) is the automated closed-loop response: per-tenant token bucket reduces remaining budget for over-burn tenants pending review. Ship Layer 1 first; add Layer 2 once baseline data exists; add Layer 3 only after the alerting is calibrated against your traffic variance.

(a) is the premature-automation failure mode — you'll auto-throttle a real customer's legitimate burst and lose the deal. (c) is permanent action on a signal that may have an innocent explanation. (d) wastes the signal.

See: [cost-attribution.md → "The three-layer enforcement ladder"](../../concepts/evaluation/cost-attribution.md#the-three-layer-enforcement-ladder).
</details>

---

✓ **Module 6 complete after this quiz.** Module 7 (multi-turn evaluation) in a future batch closes Path 06 v1.
