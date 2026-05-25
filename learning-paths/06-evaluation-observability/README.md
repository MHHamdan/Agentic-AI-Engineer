# Path 06 — Evaluation & Observability

> 🔴 Advanced · ⏱ 18-25 hours (Module 1 only — full path estimated ~50h when complete) · 📍 Start here once you've completed at least one of {Path 02, Path 03} · 🚧 Path 06 in progress (Module 1 — opening)

The production layer. Path 02's Lab 09 and Path 03's Lab 16 give you the evaluation *mechanism* — metric implementations, hand-curated fixtures, the aggregate-then-slice-then-per-agent discipline. Path 06 connects that mechanism to the operational reality: live trace ingestion, distributed-tracing correlation across parallel sub-agents, drift detection on metric distributions, alerting on regressions, agent-as-judge calibration against human ground truth, cost attribution across users and tasks and tenants.

Production observability is not a bigger version of the from-scratch harness. It's a categorically different problem with different infrastructure, different cost model, and different failure modes. The from-scratch harness fits in one Python module; the production stack involves trace SDKs, an ingestion API, sampling decisions, time-series storage, drift detectors, alert routing, and a dashboard layer.

## Who this path is for

You've finished Path 02 or Path 03 (ideally both) and have a working agent. You want to ship it — which means measuring it in flight, not just on a hand-curated fixture set.

If you don't have a working agent yet, start with [Path 01 (Foundations)](../01-foundations/) and at least one of [Path 02 (Agentic RAG)](../02-agentic-rag/) or [Path 03 (Multi-Agent Systems)](../03-multi-agent-systems/) first. The production-observability layer is most useful when you have an actual system that's producing actual traces.

## What you'll learn

By the end of Path 06 you should be able to:

- Distinguish offline evaluation (replay harness) from online evaluation (live trace stream) and pick the right tool for each question — they answer different questions and use different infrastructure.
- Map the three observability pillars (traces, metrics, logs) onto agent execution, with the OpenTelemetry GenAI semantic conventions as the portable layer.
- Instrument a multi-agent system end-to-end with LangSmith's native SDK or OpenTelemetry's framework-agnostic SDK; pick between them based on stack and lock-in tolerance.
- Implement tail-based sampling at scale — keep every failed/expensive/anomalous trace in full; sample the happy path aggressively without losing the signal you need when an incident hits.
- Run online evaluation against a live trace stream: register evaluators, alert on metric regressions, route incidents.
- Calibrate LLM-as-judge against periodic human ground truth (the Zheng et al. 2023 biases — position, verbosity, self-enhancement — need ongoing recalibration in production).
- Detect distribution drift on metric trends (KS-test, PSI, or simpler rolling-window comparisons) and distinguish "the world shifted" from "my agent regressed."
- Attribute cost multi-dimensionally — per-user, per-task, per-tenant — via tagging at trace root and propagation through children.
- Extend the Lab 16 harness for multi-turn (threaded) evaluation: trajectory metrics across conversation turns, not just single tasks.

## Prerequisites

Practical prerequisites — what you actually need to have done:

- **Path 01 (Foundations)** — required. The agent-loop vocabulary, tool design, and bounded-execution discipline carry through every Path 06 module.
- **Path 02 (Agentic RAG)** or **Path 03 (Multi-Agent Systems)** — at least one. Both are best. You need a system whose evaluation you care about; the from-scratch harness from Lab 09 (Path 02) or Lab 16 (Path 03) is the conceptual baseline this path builds on.
- **Working API access** — at least one of OpenAI / Anthropic / Google. LangSmith account (free tier sufficient for learning) for the trace-ingestion labs. Optional: a self-hostable observability platform (Langfuse, Phoenix, or Laminar) if you want to avoid vendor accounts.
- **Familiarity with HTTP, JSON, and async Python** — production trace ingestion is async-first by nature; sampling and propagation logic is non-trivial.

## What this path covers

Path 06 ships across multiple batches. Module 1 (this batch) is the opening — framing and concept pages only. Future modules add labs and platform-specific deep-dives.

### Module 1 — From harness to production observability (batch 24, this batch)

The framing. Why production observability is a distinct concern from the from-scratch harness. The three pillars of observability mapped onto agent execution. The platform landscape as of 2026.

**Two concept pages:**

- [📖 From harness to production observability](../../concepts/evaluation/from-harness-to-production.md) — ~14 min. The motivating framing. Three things production needs that the from-scratch harness doesn't provide (live trace ingestion, distribution drift, distributed correlation across parallel sub-agents). The reverse: three things the from-scratch harness gives you that production tooling absorbs by default (metric algorithms, fixture sets, aggregation discipline). The decision boundary: when to keep using the offline harness, when to add production tooling. What this isn't (a vendor-recommendation document; both have a place).
- [📖 Observability's three pillars for agents](../../concepts/evaluation/observability-three-pillars.md) — ~12 min. Traces, metrics, logs — what each pillar means in classical web-service observability and how each maps onto agent execution. Why agent traces look different from web-service traces (deeply nested, heavy LLM payloads, parallel sub-agent branches, multi-turn correlation). The OpenTelemetry GenAI semantic conventions as the portable layer. How LangSmith / Phoenix / Langfuse / Laminar / Braintrust each sit on this layer (or above it). What the OTel-native vs platform-native choice trades.

**One diagram:**

- [Observability layers (`mmd`)](../../diagrams/observability-layers.mmd) — flowchart of the instrumentation → ingestion → processing → consumption flow, mapped onto agent execution.

**No labs in this module.** Module 2 brings the first lab.

### Modules 2-7 — planned, not yet built

These modules will be added in future batches. The plan is sketched here so you can see where Module 1 leads:

- **Module 2 — Trace ingestion with LangSmith.** Instrument a Lab 10/12-style agent end-to-end. Ingest traces. Basic query/explore in the LangSmith UI. First lab.
- **Module 3 — OpenTelemetry as the portable layer.** Same agent, OTel-native instrumentation. Fanout to LangSmith + a generic OTel collector. The vendor-neutral path.
- **Module 4 — Online evaluation.** Register evaluators against a live trace stream. Tail-based sampling. Alert on metric regressions.
- **Module 5 — Drift detection + agent-as-judge calibration.** Periodic human-calibrated judge. Distribution-drift detection (KS-test, PSI, rolling windows).
- **Module 6 — Cost attribution + tail-based sampling at scale.** Multi-dimensional cost (per-user, per-task, per-tenant). Production-scale sampling decisions.
- **Module 7 — Multi-turn (threaded) evaluation.** Extending Lab 16's metric set for conversation-level trajectories.

Each module is ~1-2 batches of work. Path 06 v1 is roughly 6-10 batches end-to-end.

## What's not in this path (anti-scope)

- **General software observability.** Datadog / New Relic / Grafana / Prometheus are mature; this path doesn't reteach them. We assume you can read a flame graph; we focus on what's different about agent traces.
- **Vendor selection guidance.** Path 06 covers LangSmith (because it's the LangChain-native default), OpenTelemetry (because it's the portable layer), and references Langfuse / Phoenix / Laminar / Braintrust by name with concrete trade-offs. The path doesn't pick a winner; it gives you the criteria to pick for your situation.
- **Red-teaming and adversarial evaluation.** Different discipline. [Path 07 (Production & Safety)](../07-production-and-safety/) covers it.
- **Capacity planning, autoscaling, deployment.** Also Path 07 territory.
- **Embedding-drift detection on vector stores.** Path 02 v2 territory (we'd add it as a Lab 09 extension).
- **Multi-tenant data isolation, GDPR/SOC2 compliance.** Production concerns; out of scope for the evaluation-and-observability path proper.

## Module 1 status

| | Status |
|---|---|
| Path landing page (this file) | ✅ shipped (batch 24) |
| `from-harness-to-production.md` | ✅ shipped (batch 24) |
| `observability-three-pillars.md` | ✅ shipped (batch 24) |
| Module 1 diagram | ✅ shipped (batch 24) |
| Module 1 quiz | ⏳ landing alongside Module 2 lab |
| Modules 2-7 | ⏳ future batches |

## How this path connects to what you've built

If you came from **Path 02**: Lab 09 gave you the from-scratch RAG-eval harness. Path 06 connects that mechanism to live trace ingestion, online evaluation, drift detection, and production-grade cost attribution. The metric implementations from Lab 09 mostly carry over verbatim; what changes is *where they run* (offline replay → live trace stream) and *what infrastructure supports them*.

If you came from **Path 03**: Lab 16 gave you the from-scratch multi-agent-trajectory eval harness with seven metrics across two tiers. Path 06 takes the same metric algorithms and shows you how to (a) ingest the traces they consume from a live agent without manually building fixture sets, (b) detect drift on the metric distributions over time, (c) calibrate the LLM-as-judge variants against human ground truth, and (d) correlate spans across parallel sub-agent branches via OpenTelemetry context propagation.

If you came from **both**: the two from-scratch harnesses already share structure (hand-curated fixtures + rule-based tier + LLM-as-judge tier + category slicing). Path 06 abstracts both into a single production-tooling discipline that handles the operational layer the offline harnesses can't address: drift over time, distributed correlation, alerting, and the unification of trace ingestion across heterogeneous agent topologies.

## References

Module 1's concept pages cite specific 2026 sources. The references below are entry points for further reading rather than exhaustive lists:

- **LangChain (March 2026)**, *Introducing End-to-End OpenTelemetry Support in LangSmith* — the SDK-level OTel pivot that makes the portable-instrumentation pattern viable in LangSmith. [blog.langchain.com](https://blog.langchain.com/end-to-end-opentelemetry-langsmith/).
- **LangChain (Oct 2025)**, *Multi-turn evaluations in LangSmith* — the thread-level evaluation pattern (semantic intent, semantic outcome, trajectory). The basis for Path 06's Module 7. [blog.langchain.com](https://blog.langchain.com/insights-agent-multiturn-evals-langsmith/).
- **LangChain `agentevals`** — the production-grade trajectory evaluators (`create_trajectory_match_evaluator` for deterministic matching; `create_trajectory_llm_as_judge` for LLM-judged). [github.com/langchain-ai/agentevals](https://github.com/langchain-ai/agentevals).
- **OpenTelemetry GenAI Semantic Conventions** — the portable instrumentation standard. [opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- **Digital Applied (April 2026)**, *Agent Observability 2026: Evals, Traces, Cost Guide* — the three-platforms-lead-the-category framing (LangSmith / Braintrust / Langfuse), tail-based sampling rationale, multi-dimensional cost attribution patterns. [digitalapplied.com/blog](https://www.digitalapplied.com/blog/agent-observability-2026-evals-traces-cost-guide).
- **Laminar (April 2026)**, *Top 6 Agent Observability Platforms (2026)* — head-to-head platform comparison including Laminar, Langfuse, LangSmith, Phoenix, Weave, Braintrust. [laminar.sh/article](https://laminar.sh/article/2026-04-23-top-6-agent-observability-platforms).
- **Zheng et al. 2023**, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS — the canonical paper on LLM-as-judge biases (position, verbosity, self-enhancement). Required reading before deploying LLM-as-judge in production. [arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685).
