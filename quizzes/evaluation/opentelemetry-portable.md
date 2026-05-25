---
quiz_id: opentelemetry-portable-tracing
title: OpenTelemetry portable tracing
path: 06-evaluation-observability
module: 3
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "Why did the OpenTelemetry GenAI Special Interest Group form in April 2024?"
    options:
      - "To replace LangChain's tracing entirely with a new framework"
      - "To standardize attribute names across vendors — pre-2024, every framework shipped its own schema (`model` vs `llm.model` vs `openai.model` meant the same thing but required different queries), making cross-platform debugging awkward and migrations expensive"
      - "To deprecate OpenAI's tracing endpoint"
      - "To require all LLM providers to emit JSON instead of protobuf"
    answer: "To standardize attribute names across vendors — pre-2024, every framework shipped its own schema (`model` vs `llm.model` vs `openai.model` meant the same thing but required different queries), making cross-platform debugging awkward and migrations expensive"
  - id: q2
    text: "Why did v1.37 of the GenAI conventions replace per-message events (`gen_ai.user.message`, `gen_ai.assistant.message`, etc.) with three aggregated attributes (`gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages`)?"
    options:
      - "Aggregated attributes are smaller in payload size than per-message events"
      - "Per-message events flooded multi-turn conversations with fine-grained event records that were painful to query and correlate; aggregated attributes make multi-turn correlation a single query"
      - "OpenTelemetry deprecated events as a telemetry type entirely"
      - "Aggregated attributes are required for use with `OTEL_SEMCONV_STABILITY_OPT_IN`"
    answer: "Per-message events flooded multi-turn conversations with fine-grained event records that were painful to query and correlate; aggregated attributes make multi-turn correlation a single query"
  - id: q3
    text: "You're instrumenting an LLM API call. Which `SpanKind` should you use and why?"
    options:
      - "`SpanKind.INTERNAL` because the OpenAI client library runs in your process"
      - "`SpanKind.CLIENT` because the LLM is an external system you're calling; without this, APMs like Datadog group LLM spans as 'internal database operations' in service maps"
      - "`SpanKind.SERVER` because the LLM call is the request your service serves"
      - "`SpanKind.CONSUMER` because the LLM response is data your service consumes"
    answer: "`SpanKind.CLIENT` because the LLM is an external system you're calling; without this, APMs like Datadog group LLM spans as 'internal database operations' in service maps"
  - id: q4
    text: "How does OTel fanout work — how does the same set of spans land in multiple backends?"
    options:
      - "Each backend requires its own TracerProvider, and the application emits separate sets of spans to each"
      - "One TracerProvider has multiple SpanProcessors (typically `BatchSpanProcessor`) attached, each with its own exporter; every span the provider produces is copied to every processor's exporter"
      - "An external OTel Collector duplicates spans by reading from a shared queue"
      - "Fanout isn't supported in OTel; you must pick a single backend per process"
    answer: "One TracerProvider has multiple SpanProcessors (typically `BatchSpanProcessor`) attached, each with its own exporter; every span the provider produces is copied to every processor's exporter"
  - id: q5
    text: "When does fanout (one set of spans, multiple backends) matter most?"
    options:
      - "Always — single-backend setups should be avoided"
      - "When your team has existing observability infrastructure (corporate Datadog, self-hosted Grafana) and wants agent traces in BOTH the existing APM AND a purpose-built agent platform like LangSmith; or when self-hosted compliance backends (Langfuse, Phoenix) need to run alongside managed ones"
      - "Only when you're debugging — production should always use a single backend"
      - "Never in production; fanout doubles span-ingestion cost without benefit"
    answer: "When your team has existing observability infrastructure (corporate Datadog, self-hosted Grafana) and wants agent traces in BOTH the existing APM AND a purpose-built agent platform like LangSmith; or when self-hosted compliance backends (Langfuse, Phoenix) need to run alongside managed ones"
  - id: q6
    text: "What's the actual lock-in cost when comparing Lab 17's LangSmith-native path against Lab 18's OTel-native path?"
    options:
      - "LangSmith locks you into its platform; OTel doesn't"
      - "The lock-in is in the *instrumentation*, not the *platform*: LangSmith-native `@traceable` decoration must be rewritten when switching backends, while OTel-native instrumentation can target any OTel-compatible platform (including LangSmith via the OTLP `/otel` endpoint) by changing only the exporter configuration"
      - "Both have identical lock-in; the only difference is setup time"
      - "Lock-in cost is a myth — LangSmith provides an export tool for migrating to any platform"
    answer: "The lock-in is in the *instrumentation*, not the *platform*: LangSmith-native `@traceable` decoration must be rewritten when switching backends, while OTel-native instrumentation can target any OTel-compatible platform (including LangSmith via the OTLP `/otel` endpoint) by changing only the exporter configuration"
  - id: q7
    text: "When would you pick Lab 17's LangSmith-native instrumentation over Lab 18's OTel-native instrumentation for a real project?"
    options:
      - "Always — LangSmith-native is the recommended path for all production agents"
      - "Never — OTel-native should be the default since it's portable"
      - "When you're in a single-ecosystem commitment (LangChain/LangGraph-heavy team), iterating quickly, and lock-in cost is acceptable for the setup-time and ecosystem-fit payoff. The setup is two env vars; switching means rewriting — which you don't expect to do for this project."
      - "When you don't have an OpenAI account"
    answer: "When you're in a single-ecosystem commitment (LangChain/LangGraph-heavy team), iterating quickly, and lock-in cost is acceptable for the setup-time and ecosystem-fit payoff. The setup is two env vars; switching means rewriting — which you don't expect to do for this project."
  - id: q8
    text: "What's the hybrid pattern that's increasingly common in 2026?"
    options:
      - "Use Lab 17 for development and Lab 18 for production"
      - "OTel-native instrumentation (for portability) + LangSmith's platform-specific extensions (for the agentevals workflow, dataset management, conversation UI) — gets you portable telemetry data AND the platform-native UI features that depend on that data"
      - "Instrument with both `@traceable` and OTel manual spans on every function to capture maximum data"
      - "Use Langfuse for prompts and LangSmith for traces, in parallel"
    answer: "OTel-native instrumentation (for portability) + LangSmith's platform-specific extensions (for the agentevals workflow, dataset management, conversation UI) — gets you portable telemetry data AND the platform-native UI features that depend on that data"
---

# OpenTelemetry portable tracing · 🧠 Check your understanding

Calibrate against the [OpenTelemetry GenAI semantic conventions](../../concepts/evaluation/opentelemetry-genai-conventions.md) and [platform fanout and portability](../../concepts/evaluation/platform-fanout-and-portability.md) concept pages plus [Lab 18](../../labs/18-opentelemetry-portable-tracing/). 8 single-select questions covering the GenAI conventions, fanout patterns, and the Lab 17 vs Lab 18 trade-off. Passing: 6/8.

---

**1.** Why did the OpenTelemetry GenAI Special Interest Group form in April 2024?

- (a) To replace LangChain's tracing entirely with a new framework
- (b) To standardize attribute names across vendors — pre-2024, every framework shipped its own schema (`model` vs `llm.model` vs `openai.model` meant the same thing but required different queries), making cross-platform debugging awkward and migrations expensive
- (c) To deprecate OpenAI's tracing endpoint
- (d) To require all LLM providers to emit JSON instead of protobuf

<details>
<summary>Answer</summary>

**(b)** — The SIG's charter is to define standardized attribute names and span shapes for GenAI operations. Before, each framework (LangChain, LlamaIndex, OpenAI Agents, CrewAI, …) and each observability platform shipped its own schema. The same concept ("which model was called") had three different attribute names across three vendors. Cross-platform debugging required translation; switching backends meant rewriting instrumentation. The GenAI conventions fix this at the attribute level — same names everywhere.

See: [opentelemetry-genai-conventions.md → "The six layers"](../../concepts/evaluation/opentelemetry-genai-conventions.md#the-six-layers-of-genai-conventions).
</details>

---

**2.** Why did v1.37 of the GenAI conventions replace per-message events (`gen_ai.user.message`, `gen_ai.assistant.message`, etc.) with three aggregated attributes (`gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages`)?

- (a) Aggregated attributes are smaller in payload size than per-message events
- (b) Per-message events flooded multi-turn conversations with fine-grained event records that were painful to query and correlate; aggregated attributes make multi-turn correlation a single query
- (c) OpenTelemetry deprecated events as a telemetry type entirely
- (d) Aggregated attributes are required for use with `OTEL_SEMCONV_STABILITY_OPT_IN`

<details>
<summary>Answer</summary>

**(b)** — Per-message events generated dozens of fine-grained event records per multi-turn conversation. Querying "show me all traces where the user asked X" required full-text scanning across event records, and correlating events to their spans was awkward in some backends. v1.37 collapsed the per-message events into three aggregated attributes on the span (or a single `gen_ai.client.inference.operation.details` event), making multi-turn correlation a single span-attribute query.

Events aren't deprecated overall; only the per-message GenAI events were replaced.

See: [opentelemetry-genai-conventions.md → "The v1.37 transition"](../../concepts/evaluation/opentelemetry-genai-conventions.md#the-v137-transition--per-message-events-to-aggregated-attributes).
</details>

---

**3.** You're instrumenting an LLM API call. Which `SpanKind` should you use and why?

- (a) `SpanKind.INTERNAL` because the OpenAI client library runs in your process
- (b) `SpanKind.CLIENT` because the LLM is an external system you're calling; without this, APMs like Datadog group LLM spans as "internal database operations" in service maps
- (c) `SpanKind.SERVER` because the LLM call is the request your service serves
- (d) `SpanKind.CONSUMER` because the LLM response is data your service consumes

<details>
<summary>Answer</summary>

**(c)** is wrong — SERVER is for *incoming* requests to your service. (a) is wrong because while the SDK runs in-process, the actual LLM call is to an external API. (d) is wrong because CONSUMER is for message-queue/Kafka consumers, not HTTP API responses.

**(b)** — LLM API calls are outgoing requests to external systems. APMs use span kind to build service maps; without `CLIENT`, Datadog groups LLM spans alongside in-process operations like internal database queries. The maketocreate.com source flags this concretely: five minutes of head-scratching when a team forgot it, two minutes to fix.

For tool execution running in-process: `SpanKind.INTERNAL`. For the agent boundary itself (orchestration logic): `SpanKind.INTERNAL`. CLIENT only for outgoing API calls.

See: [opentelemetry-genai-conventions.md → "The span kind discipline"](../../concepts/evaluation/opentelemetry-genai-conventions.md#the-span-kind-discipline--the-cheap-to-get-right-expensive-to-debug-attribute).
</details>

---

**4.** How does OTel fanout work — how does the same set of spans land in multiple backends?

- (a) Each backend requires its own TracerProvider, and the application emits separate sets of spans to each
- (b) One TracerProvider has multiple SpanProcessors (typically `BatchSpanProcessor`) attached, each with its own exporter; every span the provider produces is copied to every processor's exporter
- (c) An external OTel Collector duplicates spans by reading from a shared queue
- (d) Fanout isn't supported in OTel; you must pick a single backend per process

<details>
<summary>Answer</summary>

**(b)** — The fanout pattern is built into the SDK. One `TracerProvider` creates spans; each attached `SpanProcessor` receives every span the provider produces and exports it via its configured exporter. Lab 18 demonstrates three processors: a `SimpleSpanProcessor(ConsoleSpanExporter())` for immediate dev visibility, a `BatchSpanProcessor(OTLPSpanExporter(...))` pointing at LangSmith, and (optionally) a third `BatchSpanProcessor` pointing at Jaeger.

(c) describes a separate pattern that ALSO works — the OTel Collector can receive spans from one source and fan them out to multiple destinations. Both patterns are valid; the in-process fanout is simpler for single-application setups.

See: [platform-fanout-and-portability.md → "The fanout pattern"](../../concepts/evaluation/platform-fanout-and-portability.md#the-fanout-pattern).
</details>

---

**5.** When does fanout (one set of spans, multiple backends) matter most?

- (a) Always — single-backend setups should be avoided
- (b) When your team has existing observability infrastructure (corporate Datadog, self-hosted Grafana) and wants agent traces in BOTH the existing APM AND a purpose-built agent platform like LangSmith; or when self-hosted compliance backends (Langfuse, Phoenix) need to run alongside managed ones
- (c) Only when you're debugging — production should always use a single backend
- (d) Never in production; fanout doubles span-ingestion cost without benefit

<details>
<summary>Answer</summary>

**(b)** — Fanout is a means, not an end. It matters when there's a concrete reason: existing observability infrastructure that already runs on Datadog/Grafana (the SRE team's workflow lives there); compliance requirements that mandate a self-hosted backend (Langfuse/Phoenix) alongside a managed agent-specific UI (LangSmith); or the migration story where you're swapping backends but need overlap during the transition.

Single-backend setups are fine when there's no second consumer. The point of OTel-native instrumentation isn't that you MUST fan out; it's that you CAN fan out without rewriting instrumentation when the need arises.

See: [platform-fanout-and-portability.md → "Three fanout configurations"](../../concepts/evaluation/platform-fanout-and-portability.md#three-fanout-configurations-that-matter-in-2026).
</details>

---

**6.** What's the actual lock-in cost when comparing Lab 17's LangSmith-native path against Lab 18's OTel-native path?

- (a) LangSmith locks you into its platform; OTel doesn't
- (b) The lock-in is in the *instrumentation*, not the *platform*: LangSmith-native `@traceable` decoration must be rewritten when switching backends, while OTel-native instrumentation can target any OTel-compatible platform (including LangSmith via the OTLP `/otel` endpoint) by changing only the exporter configuration
- (c) Both have identical lock-in; the only difference is setup time
- (d) Lock-in cost is a myth — LangSmith provides an export tool for migrating to any platform

<details>
<summary>Answer</summary>

**(b)** — The naive framing ("Platform X locks you in") confuses the platform with the instrumentation. LangSmith itself is fine as a backend; you can target it from OTel-native instrumentation via its OTLP `/otel` endpoint. The lock-in lives in the *decoration*: every `@traceable` call must be rewritten if you change instrumentation patterns, and switching to a different backend requires either rewriting decoration or running parallel instrumentation stacks.

OTel-native instrumentation has higher setup cost but the migration path is one configuration change.

See: [platform-fanout-and-portability.md → "The lock-in cost reframed"](../../concepts/evaluation/platform-fanout-and-portability.md#the-lock-in-cost-reframed).
</details>

---

**7.** When would you pick Lab 17's LangSmith-native instrumentation over Lab 18's OTel-native instrumentation for a real project?

- (a) Always — LangSmith-native is the recommended path for all production agents
- (b) Never — OTel-native should be the default since it's portable
- (c) When you're in a single-ecosystem commitment (LangChain/LangGraph-heavy team), iterating quickly, and lock-in cost is acceptable for the setup-time and ecosystem-fit payoff. The setup is two env vars; switching means rewriting — which you don't expect to do for this project.
- (d) When you don't have an OpenAI account

<details>
<summary>Answer</summary>

**(c)** — Neither path is universally right. Lab 17's LangSmith-native pattern earns its place when (1) your stack is LangChain/LangGraph-heavy so the auto-tracing pays off, (2) you want the platform's purpose-built UI features (messages view, dataset workflow, evaluator registration) that depend on its data shape, (3) the velocity payoff matters more than future flexibility, (4) you're prototyping or have a single-vendor commitment.

Lab 18's OTel-native pattern earns its place when (1) you have existing observability infrastructure on OTel, (2) you expect to switch or add backends, (3) compliance requires self-hosted, (4) cross-team standardization matters.

Most production teams land in one camp or the other. Both are valid for the situations they fit.

See: [platform-fanout-and-portability.md → "When each path is the right pick"](../../concepts/evaluation/platform-fanout-and-portability.md#when-each-path-is-the-right-pick).
</details>

---

**8.** What's the hybrid pattern that's increasingly common in 2026?

- (a) Use Lab 17 for development and Lab 18 for production
- (b) OTel-native instrumentation (for portability) + LangSmith's platform-specific extensions (for the agentevals workflow, dataset management, conversation UI) — gets you portable telemetry data AND the platform-native UI features that depend on that data
- (c) Instrument with both `@traceable` and OTel manual spans on every function to capture maximum data
- (d) Use Langfuse for prompts and LangSmith for traces, in parallel

<details>
<summary>Answer</summary>

**(b)** — The hybrid pattern is OTel-native instrumentation (which gives you portability across backends) combined with platform-native extensions for workflows the platform does well. For LangSmith: instrument via OTel; use LangSmith's UI features (datasets, agentevals registration) on top of those OTel spans. The platform's purpose-built features still work because they operate on the data, not the instrumentation API.

(c) is wasteful — double-instrumentation is exactly what migration aims to avoid. (a) and (d) are real patterns but not the hybrid the concept page identifies; they're different decisions about platform selection.

See: [platform-fanout-and-portability.md → "When each path is the right pick"](../../concepts/evaluation/platform-fanout-and-portability.md#when-each-path-is-the-right-pick).
</details>

---

✓ **Module 3 complete after this quiz.** Modules 4-7 in future batches.
