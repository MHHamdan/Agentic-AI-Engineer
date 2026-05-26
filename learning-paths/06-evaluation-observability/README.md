# Path 06 — Evaluation & Observability

> 🔴 Advanced · ⏱ 26-35 hours (Path 06 v1 complete — all 7 modules shipped) · 📍 Start here once you've completed at least one of {Path 02, Path 03} · ✅ Path 06 v1 complete (Modules 1-7 shipped; recipes/patterns/projects remain for v2)

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

Module 1 is concept-only; Module 2 (below) brings the first lab.

### Module 2 — LangSmith trace ingestion (batch 25)

The first Path 06 lab. Takes a Lab 14-style LangGraph supervisor agent (slim version), instruments it with LangSmith's three tracing modes (`@traceable`, env-var auto-trace, `tracing_v2_enabled`), wires two `agentevals` evaluators (deterministic + LLM-judged), runs an offline experiment against a tiny Dataset, and closes with a stretch that bridges Lab 16's from-scratch `routing_accuracy` to the platform-native evaluator format.

**Two concept pages**:

- [📖 LangSmith tracing shape](../../concepts/evaluation/langsmith-tracing-shape.md) — ~12 min. The LangSmith data model (Runs, traces, projects). Three tracing methods ranked by automation: env-var auto-trace for LangChain/LangGraph, `@traceable` for custom Python functions, `tracing_v2_enabled` for project scoping. The messages-view vs timeline-view distinction in the UI. Tags + metadata for filtering. Trade-offs vs OpenTelemetry-native (Module 3 territory).
- [📖 Online vs offline evaluation](../../concepts/evaluation/online-vs-offline-evaluation.md) — ~10 min. The dataset-vs-live-stream distinction; why both matter; the closed loop via annotation queues. `agentevals` package overview with all three evaluator families (`trajectory.match`, `trajectory.llm`, `graph_trajectory`). How Lab 16's seven from-scratch metrics map onto agentevals — three direct, three custom-evaluator, one set-level.

**One lab**:

- [🧪 Lab 17 — LangSmith trace ingestion](../../labs/17-langsmith-trace-ingestion/) — 33 cells, ~80-100 min. Instruments a Lab 14 supervisor agent; runs both deterministic and LLM-judged evaluators; runs one offline experiment; closes with a custom evaluator reusing Lab 16's `routing_accuracy`. Cost per run: ~$0.05-0.20.

**One quiz**:

- [🧠 LangSmith trace ingestion](../../quizzes/evaluation/langsmith-ingestion.md) — 8 single-select questions covering Module 1 framing + Module 2 LangSmith specifics. Passing: 6/8.

### Module 3 — OpenTelemetry portable layer (batch 26)

The vendor-neutral counterpart to Module 2. Same Lab 14 supervisor agent; instrumented with OpenTelemetry's GenAI semantic conventions instead of LangSmith's native SDK. Fanout to LangSmith + console + optional Jaeger demonstrates the portability story end-to-end.

**Two concept pages**:

- [📖 OpenTelemetry GenAI semantic conventions](../../concepts/evaluation/opentelemetry-genai-conventions.md) — ~14 min. The six layers (events, exceptions, metrics, model spans, agent spans, client spans). Core attributes that stabilized (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.tool.name`, `gen_ai.agent.name`). The v1.37 transition from per-message events to aggregated attributes. `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` for new code. Span-kind discipline (CLIENT for LLM calls, INTERNAL for tools/agents). Auto-instrumentation via `OpenAIInstrumentor` / OpenLLMetry vs manual spans.
- [📖 Platform fanout and portability](../../concepts/evaluation/platform-fanout-and-portability.md) — ~10 min. The fanout pattern (one TracerProvider, multiple SpanProcessors, multiple exporters). Three configurations: dev (console + LangSmith), staging (LangSmith + APM), production (collector-based with self-hosted backends). Platform landscape with 6 agent-native platforms + 4 APM tools that ingest GenAI OTel. The lock-in cost reframed: it lives in the instrumentation, not the platform. Decision boundary for picking Lab 17 vs Lab 18 paths. The migration story across team scale.

**One lab**:

- [🧪 Lab 18 — OpenTelemetry portable tracing](../../labs/18-opentelemetry-portable-tracing/) — 25 cells, ~90-110 min. Instruments the same Lab 14 supervisor as Lab 17. Manual `gen_ai.chat` spans with `SpanKind.CLIENT`; auto-instrumentation via `OpenAIInstrumentor`; agent-boundary `gen_ai.invoke_agent` spans. Fanout: console + OTLP→LangSmith + optional OTLP→Jaeger. Closes with Lab 17 vs Lab 18 comparison + decision framework for picking the right path. Cost per run: ~$0.05-0.20.

**One quiz**:

- [🧠 OpenTelemetry portable tracing](../../quizzes/evaluation/opentelemetry-portable.md) — 8 single-select questions covering the GenAI conventions (3), fanout patterns (2), and Lab 17 vs Lab 18 trade-offs (3). Passing: 6/8.

### Module 4 — Online evaluation + tail-based sampling (batch 27)

Third Path 06 lab. The production-runtime layer that sits on top of Modules 2 and 3: register evaluators against the live trace stream (platform-side via LangSmith Rules or code-side via SDK polling); sample intelligently at the Collector layer with the `tail_sampling` processor; close the production-to-fixture loop via annotation queues.

**Two concept pages**:

- [📖 Online evaluator registration](../../concepts/evaluation/online-evaluator-registration.md) — ~13 min. The shift from offline (Lab 09 / 16) to online: stored fixture → live stream. LangSmith Automations as the canonical mechanism: `(filter, sample_rate, action)` triples. Six action types (annotation queue / dataset / webhook / online evaluator / custom code / alert) with their canonical execution order. The cross-rule polling gotcha. The Python SDK polling pattern as the code-side equivalent: `list_runs` + iterate + `create_feedback`. Reference-free evaluators (structural-property checks, LLM-as-judge with criteria-only prompts, heuristic confidence proxies). LangSmith Engine (May 2026) as the AI layer on top.
- [📖 Tail-based sampling](../../concepts/evaluation/tail-based-sampling.md) — ~12 min. Head-vs-tail distinction: cheap-and-blind vs informed-but-buffered. Where tail sampling lives (the OTel Collector, not the application). Six policy types (`status_code`, `latency`, `numeric_attribute`, `string_attribute`, `probabilistic`, `boolean_attribute`, `composite`). First-match-wins evaluation order. A representative 5-policy production stack. The load-balancing constraint (all spans of a trace must reach the same Collector — fixed via two-tier `loadbalancingexporter` topology). Memory budget arithmetic. The complementary relationship with LangSmith Rules.

**One lab**:

- [🧪 Lab 19 — Online evaluation and tail-based sampling](../../labs/19-online-evaluation-and-sampling/) — 26 cells, ~80-100 min. Two halves: Half A wires LangSmith SDK polling (synthetic trace generation via `client.create_run`, reference-free `citation_preservation` evaluator, `create_feedback` feedback round-trip, UI Rule equivalence walkthrough, cost arithmetic). Half B walks through a real `otel-collector-config.yaml` with a 5-policy stack and simulates the policy logic in Python on 1,000 synthetic trace summaries. Closes with the synthesis on when each pattern earns its place. Cost: ~$0.005 (the lab is mostly free; one optional LLM-as-judge variant is the only cost source).

**One quiz**:

- [🧠 Online evaluation and tail-based sampling](../../quizzes/evaluation/online-evaluation.md) — 8 single-select questions covering Rules (3), tail sampling (3), and the decision boundary (2). Passing: 6/8.

### Module 5 — Drift detection + agent-as-judge calibration (batch 28)

Fourth Path 06 lab. The trust-loop closer that sits on top of Module 4: detect when evaluator scores drift over time (KS-test, PSI, Wasserstein, rolling-window monitoring); calibrate LLM-as-judge against periodic human ground truth (Cohen's kappa, five named biases and their mitigations). Without these, drift detection on uncalibrated scores produces alerts you can't act on; with them, the Path 06 trust stack is complete.

**Two concept pages**:

- [📖 Drift detection](../../concepts/evaluation/drift-detection.md) — ~14 min. The three flavors of LLM drift in 2026: prompt drift, model drift (the GPT-4 Turbo silent-update example), eval-score drift. Why classical ML drift detection doesn't fully map (LLM scores are aggregations, not features). The four canonical statistical tests (KS-test, PSI, Wasserstein, chi-square) with decision-table for picking the right one. Rolling-window pattern with baseline/reference/current windows. The alerting problem and two-tier thresholds + persistence requirements. Monitoring without labels via proxy signals. Tool landscape (Evidently, NannyML, whylogs, Phoenix, FutureAGI).
- [📖 Agent-as-judge calibration](../../concepts/evaluation/agent-as-judge-calibration.md) — ~13 min. The five named biases (position, verbosity, self-preference, format, calibration drift) with documented magnitudes from 2025-2026 follow-on work. Mitigations that survive production: permutation averaging for position bias, length-controlled rubrics for verbosity, cross-family judging for self-preference. Cohen's kappa as the agreement metric with Landis & Koch interpretation ranges. The calibration loop: gold set + cadence + kappa-over-time. The 90/10 production split (~59.8% of production AI teams use this). When NOT to use LLM-as-judge. The Path 06 trust stack assembly.

**One lab**:

- [🧪 Lab 20 — Drift detection and agent-as-judge calibration](../../labs/20-drift-detection-and-calibration/) — 34 cells, ~90-110 min. Two halves. Half A simulates 30 days of eval scores with three drift patterns (gradual, abrupt, shape-only) and detects each with KS-test, PSI (hand-coded), and Wasserstein. Rolling-window detector on a 1000-sample stream catches a mid-stream drift event with ~50-sample latency. Half B runs a simulated LLM-as-judge against a 10-example human gold set, measures verbosity bias (κ=0.000 baseline), applies length-controlled mitigation (κ=1.000 after), then visualizes 12 weeks of judge runs with an injected drift event at week 6 detected at week 9. Cost: ~$0 (all local computation).

**One quiz**:

- [🧠 Drift detection and agent-as-judge calibration](../../quizzes/evaluation/drift-and-calibration.md) — 8 single-select questions covering the three drift flavors, statistical-test selection, the five named biases, kappa interpretation, the 90/10 split, and the trust-stack assembly. Passing: 6/8.

### Module 6 — Cost attribution + adaptive sampling (batch 29)

Fifth Path 06 lab. The production-operations closer that ties the prior modules to unit economics: attribute cost to tenants/users/tasks via OTel baggage propagation; then adapt sampling decisions based on per-tenant burn rate. With Module 6 shipped, the Path 06 production stack covers all five operational layers — instrumentation, online evaluation, drift detection, calibration, and cost attribution + adaptive sampling.

**Two concept pages**:

- [📖 Cost attribution](../../concepts/evaluation/cost-attribution.md) — ~14 min. The three attribution dimensions (per-tenant for unit economics, per-user for cohort analysis, per-task for engineering optimization) and what product question each answers. The four token layers (prompt, tool, memory, response) with their distinct optimization levers. The day-one instrumentation rule with the documented ~5x retrofit cost. OTel baggage as the propagation primitive: the W3C 4KB limit, the IDs-only / no-PII / no-secrets discipline, the allowlist pattern. The "set baggage early, set span attributes redundantly" pattern. The three-layer enforcement ladder (dashboards → alerts → rate-limit tightening) with the 2x/5x baseline thresholds and the "auto-throttled real customer's legitimate burst" failure mode that argues for incremental rollout.
- [📖 Adaptive sampling](../../concepts/evaluation/adaptive-sampling.md) — ~12 min. Cost-driven policies in the tail_sampling processor: `numeric_attribute` on `gen_ai.cost.total_usd`; `string_attribute` on tenant.tier. The probabilistic-within-tail pattern. The external control loop: two strategies (sampling-rate-inversely-proportional and adaptive-thresholds-on-policy-triggers) with concrete code. Push mechanisms: file-watching, OPAMP (GA in 2026), remote-config endpoint. The two-tier Collector topology (`loadbalancingexporter` first tier routing by trace_id → `tailsamplingprocessor` second tier) and why it's required at scale. Buffer sizing formula `num_traces = traces_per_sec × decision_wait × 1.2`. The decision_wait of 30s for agents specifically.

**One lab**:

- [🧪 Lab 21 — Cost attribution and adaptive sampling](../../labs/21-cost-attribution-and-adaptive-sampling/) — 32 cells, ~80-100 min. Real OTel SDK with ConsoleSpanExporter so spans print inline. **Half A** instruments a planner → tool-caller → synthesizer agent with baggage set at request entry; demonstrates baggage propagating to every downstream span without explicit argument passing; tracks the four token layers as separate span attributes; rolls up cost over 200 synthetic traces showing the canonical "one tenant burns 65% of spend" pattern. **Half B** loads a production-realistic Collector YAML with composite policies (errors → latency → high-cost → enterprise-tier → probabilistic); simulates the policy evaluation in Python; implements an external `AdaptiveSamplingController` that computes per-tenant sampling rates via quadratic falloff; walks through the two-tier Collector topology with both YAMLs. Synthesis demonstrates 88% ingestion-cost reduction at 1M traces/mo with 12% retention. Cost: ~$0 (all local SDK + computation).

**One quiz**:

- [🧠 Cost attribution and adaptive sampling](../../quizzes/evaluation/cost-and-sampling.md) — 8 single-select questions covering the day-one instrumentation rule, the four token layers, baggage-vs-span-attributes, cost-driven policy types, the two-tier topology constraint, the external control loop, the 4KB baggage limit, and the three-layer enforcement ladder. Passing: 6/8.

### Module 7 — Multi-turn (threaded) evaluation (batch 30)

Sixth and final Path 06 lab. The trajectory specialization that closes Path 06 v1: extend the prior modules' single-trace evaluation patterns to conversation-level (threaded) trajectories. Implements three of the four canonical conversation-level metrics from scratch; builds a minimal `ConversationSimulator` with cooperative / distracted / adversarial personas; demonstrates the single-turn-trap (every individual turn passing while the conversation as a whole fails).

**Two concept pages**:

- [📖 Multi-turn (threaded) evaluation](../../concepts/evaluation/multi-turn-evaluation.md) — ~14 min. The single-turn-trap framing (the voice-AI insurance team at 92% faithfulness with chronic "going in circles" complaints). The three shifts from 2024 → 2026 that moved multi-turn from optional to required. The four canonical conversation-level metrics with operational definitions: Conversation Completeness (the single most important), Knowledge Retention, Role Adherence, Turn Relevancy. The conversation-level vs turn-level vs trajectory distinction (three units of evaluation answering three different questions). The O(n × k) framing for trajectory evaluation. Threads as first-party concept (LangSmith's October 2025 release; the pattern that spread across the tool landscape). The LangChain Deep Agents five-pattern framework for production agent evaluation. The span-attached-scores operational pattern that lets CI and production use the same metric definitions.
- [📖 Conversation simulation](../../concepts/evaluation/conversation-simulation.md) — ~11 min. Why hand-curated test suites don't scale and what simulators solve. The three persona archetypes (cooperative, distracted, adversarial) with system-prompt sketches and the failure modes each catches. The 50/30/20 traffic-distribution argument and the cooperative-only trap as the silent killer of simulation suites. The production tools landscape (DeepEval `ConversationSimulator`, MLflow `ConversationSimulator`, LivePerson enterprise tool). The sliding-window pattern for long conversations (with the cross-window-contradiction trade-off). The persona-consistency problem (LLMs simulating users drift toward generic-helpful behavior past turn 10-12) and three mitigations. The Sim2Real gap and why simulation supplements rather than replaces production-trace evaluation.

**One lab**:

- [🧪 Lab 22 — Multi-turn (threaded) evaluation](../../labs/22-multi-turn-evaluation/) — 29 cells, ~75-95 min. **Half A** implements three of the four canonical conversation-level metrics from scratch (Conversation Completeness with intent extraction + per-intent satisfaction check; Knowledge Retention with fact extraction + re-ask detection; Role Adherence with YAML role-spec + per-turn LLM-as-judge); applies them to three hand-crafted conversations where every individual turn passes a single-turn check but each conversation fails differently (Completeness fail; Retention fail; Adherence fail). **Half B** builds a minimal `ConversationSimulator` class, defines three personas (cooperative, distracted, adversarial), runs them against a small scheduling agent, and scores the resulting conversations. Synthesis assembles the full Path 06 v1 production-readiness stack. Cost: ~$0.02 (uses `gpt-4o-mini` at temperature=0.1 with bounded LLM-as-judge calls; gracefully handles no-API-key mode — all 12 code cells execute, only the call sites skip).

**One quiz**:

- [🧠 Multi-turn (threaded) evaluation](../../quizzes/evaluation/multi-turn.md) — 8 single-select questions covering the single-turn-trap diagnosis, Conversation Completeness as the primary metric, the three-units-of-evaluation distinction, the O(n × k) trajectory complexity, persona archetypes, the cooperative-only trap, the sliding-window pattern, and the Sim2Real gap. Passing: 6/8.

---

## ✅ Path 06 v1 complete

With Module 7 shipped, **Path 06 v1 is structurally complete**. All seven modules ship the full production-readiness stack for agentic AI evaluation and observability:

| Module | Lab | What it ships |
|---|---|---|
| 1 — Framing | (concepts only) | The observability three-pillars; what changes for agents |
| 2 — LangSmith trace ingestion | Lab 17 | Vendor-native instrumentation patterns |
| 3 — OpenTelemetry portable layer | Lab 18 | Vendor-neutral instrumentation; fanout to multiple backends |
| 4 — Online evaluation + tail sampling | Lab 19 | Register evaluators on the live trace stream; tail-based sampling at the Collector |
| 5 — Drift detection + judge calibration | Lab 20 | KS-test / PSI / Wasserstein for score-stream drift; Cohen's kappa for judge calibration |
| 6 — Cost attribution + adaptive sampling | Lab 21 | OTel baggage for cost identity propagation; cost-driven sampling policies |
| 7 — Multi-turn (threaded) evaluation | Lab 22 | Conversation-level metrics; persona-driven simulation |

The full operational picture: instrument → score → monitor for drift → calibrate to humans → attribute cost → sample by cost → evaluate at the conversation level. Each module earns its place; none is redundant.

**What remains for Path 06 v2**:
- **Recipes** — opinionated end-to-end production setups (LangSmith-native recipe; OpenTelemetry recipe; multi-tool integration recipes).
- **Patterns** — cross-cutting patterns (cost-aware retrieval; drift-triggered retraining; judge-ensemble patterns).
- **Projects** — capstone projects that integrate all six labs into a single production-deployable agent observability stack.
- **Lab solutions** — reference solutions for Labs 17-22 (catchup batch).
- **`evaluation-frameworks-deep-dive.md`** — LangSmith vs Braintrust vs Langfuse vs Phoenix vs Laminar at code level.
- **Embedding-space drift detection** — the RAG-input-side complement to Module 5's score-side drift.
- **Adversarial red-teaming at scale** — DeepTeam-style orchestration.

## What's not in this path (anti-scope)

- **General software observability.** Datadog / New Relic / Grafana / Prometheus are mature; this path doesn't reteach them. We assume you can read a flame graph; we focus on what's different about agent traces.
- **Vendor selection guidance.** Path 06 covers LangSmith (because it's the LangChain-native default), OpenTelemetry (because it's the portable layer), and references Langfuse / Phoenix / Laminar / Braintrust by name with concrete trade-offs. The path doesn't pick a winner; it gives you the criteria to pick for your situation.
- **Red-teaming and adversarial evaluation.** Different discipline. [Path 07 (Production & Safety)](../07-production-and-safety/) covers it.
- **Capacity planning, autoscaling, deployment.** Also Path 07 territory.
- **Embedding-drift detection on vector stores.** Path 02 v2 territory (we'd add it as a Lab 09 extension).
- **Multi-tenant data isolation, GDPR/SOC2 compliance.** Production concerns; out of scope for the evaluation-and-observability path proper.

## Module 1-7 status

| | Status |
|---|---|
| Path landing page (this file) | ✅ shipped (batch 24) |
| `from-harness-to-production.md` | ✅ shipped (batch 24) |
| `observability-three-pillars.md` | ✅ shipped (batch 24) |
| Module 1 diagram (`observability-layers.mmd`) | ✅ shipped (batch 24) |
| `langsmith-tracing-shape.md` | ✅ shipped (batch 25) |
| `online-vs-offline-evaluation.md` | ✅ shipped (batch 25) |
| Lab 17 (LangSmith trace ingestion) | ✅ shipped (batch 25) — solution shipped (batch 31) |
| Module 2 quiz (`langsmith-ingestion.md`) | ✅ shipped (batch 25) |
| `opentelemetry-genai-conventions.md` | ✅ shipped (batch 26) |
| `platform-fanout-and-portability.md` | ✅ shipped (batch 26) |
| Lab 18 (OpenTelemetry portable tracing) | ✅ shipped (batch 26) — solution shipped (batch 31) |
| Module 3 quiz (`opentelemetry-portable.md`) | ✅ shipped (batch 26) |
| `online-evaluator-registration.md` | ✅ shipped (batch 27) |
| `tail-based-sampling.md` | ✅ shipped (batch 27) |
| Lab 19 (Online evaluation and sampling) | ✅ shipped (batch 27) — solution shipped (batch 31) |
| Module 4 quiz (`online-evaluation.md`) | ✅ shipped (batch 27) |
| `drift-detection.md` | ✅ shipped (batch 28) |
| `agent-as-judge-calibration.md` | ✅ shipped (batch 28) |
| Lab 20 (Drift detection and calibration) | ✅ shipped (batch 28) — solution shipped (batch 31) |
| Module 5 quiz (`drift-and-calibration.md`) | ✅ shipped (batch 28) |
| `cost-attribution.md` | ✅ shipped (batch 29) |
| `adaptive-sampling.md` | ✅ shipped (batch 29) |
| Lab 21 (Cost attribution and adaptive sampling) | ✅ shipped (batch 29) — solution shipped (batch 31) |
| Module 6 quiz (`cost-and-sampling.md`) | ✅ shipped (batch 29) |
| `multi-turn-evaluation.md` | ✅ shipped (batch 30) |
| `conversation-simulation.md` | ✅ shipped (batch 30) |
| Lab 22 (Multi-turn evaluation) | ✅ shipped (batch 30) — solution shipped (batch 31) |
| Module 7 quiz (`multi-turn.md`) | ✅ shipped (batch 30) |
| **Path 06 v1** | **✅ complete (Modules 1-7 shipped)** |

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
