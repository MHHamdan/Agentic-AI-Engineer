---
quiz_id: online-evaluation-and-sampling
title: Online evaluation and tail-based sampling
path: 06-evaluation-observability
module: 4
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "What are the three components of a LangSmith Automation Rule?"
    options:
      - "Source, transformation, and destination"
      - "Filter, sample rate, and action"
      - "Trigger, condition, and webhook"
      - "Dataset, evaluator, and result handler"
    answer: "Filter, sample rate, and action"
  - id: q2
    text: "When multiple LangSmith Automation Rules match the same trace and each has multiple actions, what's the execution order WITHIN a single rule?"
    options:
      - "Webhook → annotation queue → online evaluator → dataset → custom code → alert"
      - "Add to annotation queue → add to dataset → trigger webhook → run online evaluator → run custom code evaluator → trigger alert"
      - "All actions run in parallel; ordering is not guaranteed"
      - "Custom code evaluator → online evaluator → dataset → annotation queue → webhook → alert"
    answer: "Add to annotation queue → add to dataset → trigger webhook → run online evaluator → run custom code evaluator → trigger alert"
  - id: q3
    text: "Why are most online evaluators in production reference-free (no ground-truth comparison)?"
    options:
      - "Reference-free evaluators are faster than reference-comparing ones"
      - "Production traffic doesn't ship with golden answers — there's no curator writing the expected output for each live user interaction; the evaluator has to check structural properties (citation presence, format validity) or use LLM-as-judge with criteria-only prompts"
      - "LangSmith Rules don't support reference-comparing evaluators"
      - "Reference-free evaluators are required for OTel compatibility"
    answer: "Production traffic doesn't ship with golden answers — there's no curator writing the expected output for each live user interaction; the evaluator has to check structural properties (citation presence, format validity) or use LLM-as-judge with criteria-only prompts"
  - id: q4
    text: "What's the core distinction between head-based and tail-based sampling?"
    options:
      - "Head sampling is for HTTP requests; tail sampling is for LLM calls"
      - "Head sampling decides at trace start (cheap, blind to trace contents); tail sampling decides at trace end after buffering all spans (informed by trace contents like errors, latency, attributes)"
      - "Head sampling drops 50% of traces; tail sampling drops 90%"
      - "Head sampling runs in the application; tail sampling runs in the LangSmith UI"
    answer: "Head sampling decides at trace start (cheap, blind to trace contents); tail sampling decides at trace end after buffering all spans (informed by trace contents like errors, latency, attributes)"
  - id: q5
    text: "In a 4-policy `tail_sampling` config with policies in order [errors, high-latency, high-token-usage, 5% baseline], what happens when a trace matches both 'errors' and 'high-token-usage'?"
    options:
      - "Both policies fire and the trace is kept twice (deduplicated downstream)"
      - "The trace is kept only if both policies independently agree"
      - "First-match-wins: the trace is matched by 'errors' (the first matching policy in order) and counted in the errors-policy bucket; the high-token-usage policy is not evaluated"
      - "The trace is dropped because of policy conflict"
    answer: "First-match-wins: the trace is matched by 'errors' (the first matching policy in order) and counted in the errors-policy bucket; the high-token-usage policy is not evaluated"
  - id: q6
    text: "Why must all spans for a given trace reach the same OTel Collector instance for tail sampling to work?"
    options:
      - "OTLP protocol requires it for trace integrity"
      - "Because tail sampling decisions need the complete trace — total latency, every span's status, all attributes — to evaluate policies correctly; if a trace's spans split across multiple Collectors, none has full information and decisions become inconsistent. The fix is the two-tier topology with `loadbalancingexporter` routing spans by trace_id."
      - "To avoid double-counting traces in the kept set"
      - "It's required for LangSmith ingestion compatibility"
    answer: "Because tail sampling decisions need the complete trace — total latency, every span's status, all attributes — to evaluate policies correctly; if a trace's spans split across multiple Collectors, none has full information and decisions become inconsistent. The fix is the two-tier topology with `loadbalancingexporter` routing spans by trace_id."
  - id: q7
    text: "When does Collector tail sampling earn its place in production rather than relying only on LangSmith Automation Rules?"
    options:
      - "When storage and ingestion cost is the binding constraint (high-volume production traffic), when you need vendor-agnostic sampling that applies to every backend in your fanout, or when compliance requires retaining 100% of error traces but not happy-path traces"
      - "Always — Collector tail sampling is the recommended default"
      - "Only when you've stopped using LangSmith entirely"
      - "When you can't write Python evaluator functions"
    answer: "When storage and ingestion cost is the binding constraint (high-volume production traffic), when you need vendor-agnostic sampling that applies to every backend in your fanout, or when compliance requires retaining 100% of error traces but not happy-path traces"
  - id: q8
    text: "How do LangSmith Rules and OTel Collector tail sampling complement each other in a production deployment?"
    options:
      - "They're alternatives; you pick one and never use the other"
      - "Tail sampling runs in development; Rules run in production"
      - "Tail sampling at the Collector reduces what reaches the platform (cuts storage/ingestion cost) — then Rules at the platform decide what to DO with what arrived (run evaluators on samples, route to annotation queue, promote to datasets). Different layers, different concerns, complementary patterns."
      - "Rules generate the data; tail sampling stores it"
    answer: "Tail sampling at the Collector reduces what reaches the platform (cuts storage/ingestion cost) — then Rules at the platform decide what to DO with what arrived (run evaluators on samples, route to annotation queue, promote to datasets). Different layers, different concerns, complementary patterns."
---

# Online evaluation and tail-based sampling · 🧠 Check your understanding

Calibrate against the [online evaluator registration](../../concepts/evaluation/online-evaluator-registration.md) and [tail-based sampling](../../concepts/evaluation/tail-based-sampling.md) concept pages plus [Lab 19](../../labs/19-online-evaluation-and-sampling/). 8 single-select questions covering the platform-side (LangSmith Rules) and Collector-side (OTel tail_sampling) patterns. Passing: 6/8.

---

**1.** What are the three components of a LangSmith Automation Rule?

- (a) Source, transformation, and destination
- (b) Filter, sample rate, and action
- (c) Trigger, condition, and webhook
- (d) Dataset, evaluator, and result handler

<details>
<summary>Answer</summary>

**(b)** — A LangSmith Automation Rule is a `(filter, sample_rate, action)` triple. The filter says which traces match; the sample_rate says what percentage of matching traces the rule fires on; the action says what to do with the trace when the rule fires. Six action types: add to annotation queue, add to dataset, trigger webhook, run online evaluator, run custom code evaluator, trigger alert.

See: [online-evaluator-registration.md → "LangSmith Automations"](../../concepts/evaluation/online-evaluator-registration.md#langsmith-automations--the-canonical-mechanism).
</details>

---

**2.** When multiple LangSmith Automation Rules match the same trace and each has multiple actions, what's the execution order WITHIN a single rule?

- (a) Webhook → annotation queue → online evaluator → dataset → custom code → alert
- (b) Add to annotation queue → add to dataset → trigger webhook → run online evaluator → run custom code evaluator → trigger alert
- (c) All actions run in parallel; ordering is not guaranteed
- (d) Custom code evaluator → online evaluator → dataset → annotation queue → webhook → alert

<details>
<summary>Answer</summary>

**(b)** — The within-rule action order is deterministic per LangChain's docs. Across separate rules, however, ordering is NOT guaranteed — each rule runs on an independent polling schedule, so a webhook in one rule may fire before an evaluator in another rule has scored. If you need cross-rule ordering, express the dependency via filters (e.g., the downstream rule's filter checks `feedback.quality IS NOT NULL` to ensure the upstream rule already wrote feedback).

See: [online-evaluator-registration.md → "LangSmith Automations"](../../concepts/evaluation/online-evaluator-registration.md#langsmith-automations--the-canonical-mechanism).
</details>

---

**3.** Why are most online evaluators in production reference-free (no ground-truth comparison)?

- (a) Reference-free evaluators are faster than reference-comparing ones
- (b) Production traffic doesn't ship with golden answers — there's no curator writing the expected output for each live user interaction; the evaluator has to check structural properties (citation presence, format validity) or use LLM-as-judge with criteria-only prompts
- (c) LangSmith Rules don't support reference-comparing evaluators
- (d) Reference-free evaluators are required for OTel compatibility

<details>
<summary>Answer</summary>

**(b)** — This is the core constraint of online evaluation: live traffic doesn't ship with golden references. Offline evaluators (Lab 09, Lab 16) can compare against curated expected outputs because the curator wrote them. Online evaluators score what production users actually produced, against criteria you can verify without a reference: structural properties (Lab 16's `citation_preservation`, `routing_accuracy`), prompt-conformance checks, or LLM-as-judge with criteria-only prompts.

Reference-free evaluators are faster only as a side effect; they're not chosen for speed. The platform supports both reference-comparing and reference-free; production reality forces most production cases into the latter.

See: [online-evaluator-registration.md → "Reference-free evaluators"](../../concepts/evaluation/online-evaluator-registration.md#reference-free-evaluators-in-practice).
</details>

---

**4.** What's the core distinction between head-based and tail-based sampling?

- (a) Head sampling is for HTTP requests; tail sampling is for LLM calls
- (b) Head sampling decides at trace start (cheap, blind to trace contents); tail sampling decides at trace end after buffering all spans (informed by trace contents like errors, latency, attributes)
- (c) Head sampling drops 50% of traces; tail sampling drops 90%
- (d) Head sampling runs in the application; tail sampling runs in the LangSmith UI

<details>
<summary>Answer</summary>

**(b)** — Head sampling decides at trace start: random percentage, no knowledge of how the trace will turn out. Cheap (no buffering) but blind (90% of errors get dropped along with 90% of happy-path traces). Tail sampling waits until the trace completes, buffers all spans, then inspects them — kept if errors, kept if slow, kept if any policy matches. Informed but requires buffering at the Collector.

(d) is wrong because tail sampling runs at the OTel Collector layer, NOT at the platform (LangSmith). The application emits 100%; the Collector decides.

See: [tail-based-sampling.md → "Head-based vs tail-based"](../../concepts/evaluation/tail-based-sampling.md#head-based-vs-tail-based--the-canonical-distinction).
</details>

---

**5.** In a 4-policy `tail_sampling` config with policies in order [errors, high-latency, high-token-usage, 5% baseline], what happens when a trace matches both 'errors' and 'high-token-usage'?

- (a) Both policies fire and the trace is kept twice (deduplicated downstream)
- (b) The trace is kept only if both policies independently agree
- (c) First-match-wins: the trace is matched by 'errors' (the first matching policy in order) and counted in the errors-policy bucket; the high-token-usage policy is not evaluated
- (d) The trace is dropped because of policy conflict

<details>
<summary>Answer</summary>

**(c)** — Policies are evaluated in declared order; first match wins. The order matters: it's why production configs read errors first (most diagnostic), then latency, then high-cost, then probabilistic baseline last. If you put `probabilistic: 5%` first, all subsequent policies become unreachable — most error traces would already be sampled by the random baseline (or dropped).

See: [tail-based-sampling.md → "Standard policies"](../../concepts/evaluation/tail-based-sampling.md#standard-policies).
</details>

---

**6.** Why must all spans for a given trace reach the same OTel Collector instance for tail sampling to work?

- (a) OTLP protocol requires it for trace integrity
- (b) Because tail sampling decisions need the complete trace — total latency, every span's status, all attributes — to evaluate policies correctly; if a trace's spans split across multiple Collectors, none has full information and decisions become inconsistent. The fix is the two-tier topology with `loadbalancingexporter` routing spans by trace_id.
- (c) To avoid double-counting traces in the kept set
- (d) It's required for LangSmith ingestion compatibility

<details>
<summary>Answer</summary>

**(b)** — Tail sampling needs the whole trace in buffer to evaluate policies: total latency requires the earliest start and latest end span; status_code policy needs to see if ANY span errored; numeric_attribute needs to see the span carrying the high-token-usage attribute. If half a trace's spans go to Collector A and the rest to Collector B, neither can decide correctly. The symptom is "tail sampling looks broken but the config is correct" — surprisingly common in production deployments that scaled before reading the manual.

The fix is the two-tier topology: agent collectors with `loadbalancingexporter` route spans by `trace_id` hash to a specific tail-sampling collector instance, ensuring every span of the same trace lands on the same instance.

See: [tail-based-sampling.md → "The load-balancing constraint"](../../concepts/evaluation/tail-based-sampling.md#the-load-balancing-constraint).
</details>

---

**7.** When does Collector tail sampling earn its place in production rather than relying only on LangSmith Automation Rules?

- (a) When storage and ingestion cost is the binding constraint (high-volume production traffic), when you need vendor-agnostic sampling that applies to every backend in your fanout, or when compliance requires retaining 100% of error traces but not happy-path traces
- (b) Always — Collector tail sampling is the recommended default
- (c) Only when you've stopped using LangSmith entirely
- (d) When you can't write Python evaluator functions

<details>
<summary>Answer</summary>

**(a)** — Tail sampling at the Collector earns its place in three specific situations: (1) high-volume traffic where storage/ingestion fees are the binding constraint and dropping 90% of happy-path traces saves real money, (2) multi-backend fanout where the sampling decision needs to apply uniformly to every downstream backend (Collector tail sampling does; LangSmith Rules only affect LangSmith), (3) compliance scenarios requiring 100% error retention but selective happy-path retention.

At low volume, the Collector adds operational complexity without enough cost savings to justify it; LangSmith Rules alone are sufficient.

See: [tail-based-sampling.md → "When tail sampling earns its place"](../../concepts/evaluation/tail-based-sampling.md#when-tail-sampling-earns-its-place-vs-langsmith-rules).
</details>

---

**8.** How do LangSmith Rules and OTel Collector tail sampling complement each other in a production deployment?

- (a) They're alternatives; you pick one and never use the other
- (b) Tail sampling runs in development; Rules run in production
- (c) Tail sampling at the Collector reduces what reaches the platform (cuts storage/ingestion cost) — then Rules at the platform decide what to DO with what arrived (run evaluators on samples, route to annotation queue, promote to datasets). Different layers, different concerns, complementary patterns.
- (d) Rules generate the data; tail sampling stores it

<details>
<summary>Answer</summary>

**(c)** — The two patterns operate at different layers and address different concerns. Tail sampling at the Collector is about volume control: drop 95% of happy-path traces before they reach the platform; keep 100% of errors and other diagnostic-gold traces. Rules at the platform are about workflow: on the (much smaller) volume that did make it through, run evaluators, route low-quality traces to humans, promote failures to offline datasets for CI regression testing.

Production-scale agent deployments use both. Skipping tail sampling at high volume wastes money on storage. Skipping Rules forfeits the closed-loop production-to-fixture-set workflow that keeps the offline test suite current.

See: [tail-based-sampling.md → "When tail sampling earns its place"](../../concepts/evaluation/tail-based-sampling.md#when-tail-sampling-earns-its-place-vs-langsmith-rules).
</details>

---

✓ **Module 4 complete after this quiz.** Modules 5-7 in future batches.
