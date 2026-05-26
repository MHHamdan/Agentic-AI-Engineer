# 📖 Concepts · Evaluation

> 🟢 Stable explainers · concepts/evaluation/ covers RAG evaluation as a discipline. This is the *primer* on evaluation that the rest of Path 02 needs; the production-grade treatment (frameworks, observability, drift detection) lives in [Path 06](../../learning-paths/).

The pages here are a four-step progression from "what is RAG evaluation" to "what metrics to compute on what." They're prerequisites for [Lab 09](../../labs/09-evaluating-agentic-rag/) and the synthesis of Path 02's Labs 06-08.

## Current pages

### The primer

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [what-is-rag-evaluation.md](./what-is-rag-evaluation.md) | ~10 min | Orientation: retrieval vs generation, offline vs online, correctness vs groundedness, what evaluation can and can't tell you. |
| 📖 [eval-set-construction.md](./eval-set-construction.md) | ~10 min | The foundation: 30-50 hand-curated queries beat 1000 synthetic ones; expected_chunks/expected_doc, reference answers, category and failure-label tagging. |
| 📖 [retrieval-metrics.md](./retrieval-metrics.md) | ~11 min | Hits@k, recall@k, precision@k, MRR, nDCG@k, mean rank of expected chunk. What each reveals and what it hides. |
| 📖 [answer-quality-metrics.md](./answer-quality-metrics.md) | ~11 min | Faithfulness, groundedness, citation accuracy, answer relevance, refusal quality. Rule-based vs LLM-as-judge; Zheng et al. 2023's documented biases. |

These four pages are prerequisites for [Lab 09: Evaluating agentic RAG](../../labs/09-evaluating-agentic-rag/).

## Path 06 — Production evaluation & observability (✅ v1 complete — all 7 modules shipped)

The pages above (Path 02's RAG-evaluation primer) cover offline evaluation against hand-curated fixture sets. Path 06 extends that mechanism to production: live trace ingestion, drift detection, agent-as-judge calibration, distributed-tracing correlation across parallel sub-agents.

### Module 1 — From harness to production observability (batch 24)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [from-harness-to-production.md](./from-harness-to-production.md) | ~14 min | The framing. Why production is a categorically different problem from the from-scratch harness: live ingestion at scale, distribution drift on metric trends, distributed-tracing correlation across parallel sub-agents. The decision boundary for when to use each. What production tooling absorbs and what stays in the harness. |
| 📖 [observability-three-pillars.md](./observability-three-pillars.md) | ~12 min | Traces, metrics, logs mapped onto agent execution. Why agent traces look different from web-service traces (deeply nested, heavy LLM payloads, parallel sub-agent branches). The OpenTelemetry GenAI semantic conventions as the portable layer. OTel-native vs platform-native instrumentation trade-offs. |

### Module 2 — LangSmith trace ingestion (batch 25)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [langsmith-tracing-shape.md](./langsmith-tracing-shape.md) | ~12 min | The LangSmith data model: Runs, traces, projects. Three tracing methods ranked by automation: env-var auto-trace for LangChain/LangGraph, `@traceable` for custom Python functions, `tracing_v2_enabled` for project scoping. Messages-view vs timeline-view distinction. Adding tags + metadata for filtering. When LangSmith-native helps vs costs lock-in. |
| 📖 [online-vs-offline-evaluation.md](./online-vs-offline-evaluation.md) | ~10 min | The dataset-vs-live-stream distinction; why both matter; the closed loop via annotation queues. `agentevals` package overview (`trajectory.match`, `trajectory.llm`, `graph_trajectory`). How Lab 16's seven from-scratch metrics map onto agentevals — three direct, three custom-evaluator, one set-level. When the from-scratch harness still earns its keep. |

Lab applying these: [🧪 Lab 17 — LangSmith trace ingestion](../../labs/17-langsmith-trace-ingestion/).

Quiz: [🧠 LangSmith trace ingestion](../../quizzes/evaluation/langsmith-ingestion.md) — 8 questions covering Modules 1-2.

### Module 3 — OpenTelemetry portable layer (batch 26)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [opentelemetry-genai-conventions.md](./opentelemetry-genai-conventions.md) | ~14 min | The six layers of GenAI conventions (events, exceptions, metrics, model spans, agent spans, client spans). Core attributes that stabilized (`gen_ai.system`, `gen_ai.request.model`, token usage, tool/agent attributes). The v1.37 transition from per-message events to aggregated `gen_ai.input.messages`/`output.messages` attributes. `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` for new code. Span-kind discipline (CLIENT for LLM calls, INTERNAL for tools/agents). Auto-instrumentation libraries (`OpenAIInstrumentor`, OpenLLMetry covering 8+ frameworks). |
| 📖 [platform-fanout-and-portability.md](./platform-fanout-and-portability.md) | ~10 min | The fanout pattern: one TracerProvider, multiple SpanProcessors, multiple exporters. Three configurations (dev/staging/production). Platform landscape: 6 agent-native platforms + 4 APM tools that ingest OTel. The lock-in cost reframed (instrumentation locks you in, not the platform). Decision boundary for picking Lab 17 vs Lab 18 paths. A concrete migration story across team scale stages. |

Lab applying these: [🧪 Lab 18 — OpenTelemetry portable tracing](../../labs/18-opentelemetry-portable-tracing/).

Quiz: [🧠 OpenTelemetry portable tracing](../../quizzes/evaluation/opentelemetry-portable.md) — 8 questions covering Module 3 + Lab 17 vs Lab 18 trade-offs.

### Module 4 — Online evaluation + tail-based sampling (batch 27)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [online-evaluator-registration.md](./online-evaluator-registration.md) | ~13 min | The shift from offline (Lab 09/16) to online: stored fixture → live trace stream. LangSmith Automations as the canonical mechanism: `(filter, sample_rate, action)` triples with six action types (annotation queue, dataset, webhook, online evaluator, custom code, alert) and their canonical execution order. The cross-rule polling gotcha. The Python SDK polling pattern as the code-side equivalent: `list_runs` + iterate + `create_feedback`. Reference-free evaluators (structural-property checks, LLM-as-judge with criteria-only prompts). LangSmith Engine (May 2026) as the AI layer on top. |
| 📖 [tail-based-sampling.md](./tail-based-sampling.md) | ~12 min | Head-vs-tail distinction: cheap-and-blind vs informed-but-buffered. Where tail sampling lives (the OTel Collector, not the application). Six policy types (`status_code`, `latency`, `numeric_attribute`, `string_attribute`, `probabilistic`, `boolean_attribute`, `composite`). First-match-wins evaluation order. A representative 5-policy production stack with the cost-reduction arithmetic. The load-balancing constraint and the two-tier `loadbalancingexporter` topology that solves it. Memory budget arithmetic (`num_traces ≈ traces/sec × decision_wait × safety_margin`). When tail sampling earns its place vs LangSmith Rules. |

Lab applying these: [🧪 Lab 19 — Online evaluation and tail-based sampling](../../labs/19-online-evaluation-and-sampling/).

Quiz: [🧠 Online evaluation and tail-based sampling](../../quizzes/evaluation/online-evaluation.md) — 8 questions covering Rules (3), tail sampling (3), and the decision boundary (2).

### Module 5 — Drift detection + agent-as-judge calibration (batch 28)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [drift-detection.md](./drift-detection.md) | ~14 min | The three flavors of LLM drift in 2026 (prompt drift, model drift with the GPT-4 Turbo silent-update story, eval-score drift). Why classical ML drift detection doesn't fully map. The four canonical statistical tests (KS-test, PSI, Wasserstein, chi-square) with a decision table. Rolling-window pattern with baseline/reference/current windows. Two-tier alerting thresholds + persistence requirements. Monitoring without labels via proxy signals (confidence distributions, abstain rates, output length histograms). Tool landscape: Evidently, NannyML, whylogs, Phoenix, FutureAGI. |
| 📖 [agent-as-judge-calibration.md](./agent-as-judge-calibration.md) | ~13 min | The Zheng et al. 2023 problem statement three years later. Five named LLM-judge biases (position, verbosity, self-preference, format, calibration drift) with documented magnitudes and mitigations that survive production. Cohen's kappa with Landis & Koch interpretation ranges. The calibration loop: gold set + cadence + kappa-over-time. The 90/10 production split (~59.8% of teams). When NOT to use LLM-as-judge. The Path 06 trust stack assembly. |

Lab applying these: [🧪 Lab 20 — Drift detection and agent-as-judge calibration](../../labs/20-drift-detection-and-calibration/).

Quiz: [🧠 Drift detection and agent-as-judge calibration](../../quizzes/evaluation/drift-and-calibration.md) — 8 questions covering drift flavors (3), calibration mechanism (3), and the trust-stack decision boundary (2).

### Module 6 — Cost attribution + adaptive sampling (batch 29)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [cost-attribution.md](./cost-attribution.md) | ~14 min | The three attribution dimensions (per-tenant, per-user, per-task) and what product question each answers. The four token layers (prompt, tool, memory, response) with distinct optimization levers. The day-one instrumentation rule and the documented ~5x retrofit cost. OTel baggage as the propagation primitive: Python API (`baggage.set_baggage`, `context.attach`), the W3C 4KB total limit, the IDs-only/no-PII/no-secrets/allowlist discipline. The "set baggage early, set span attributes redundantly" pattern. The three-layer enforcement ladder (dashboards → alerts → rate-limit tightening) with 2x/5x baseline thresholds and the incremental-rollout argument. |
| 📖 [adaptive-sampling.md](./adaptive-sampling.md) | ~12 min | Cost-driven policies (`numeric_attribute` on `gen_ai.cost.total_usd`; `string_attribute` on `tenant.tier`). The probabilistic-within-tail pattern. The external control loop with two strategies (rate-inversely-proportional and adaptive-thresholds-on-triggers) and three push mechanisms (file-watching, OPAMP GA in 2026, remote-config endpoint). The two-tier Collector topology (`loadbalancingexporter` + `tailsamplingprocessor`) with the half-trace failure mode that argues for it. Buffer sizing: `num_traces ≈ traces_per_sec × decision_wait × 1.2`. The decision_wait of 30s for agents. |

Lab applying these: [🧪 Lab 21 — Cost attribution and adaptive sampling](../../labs/21-cost-attribution-and-adaptive-sampling/).

Quiz: [🧠 Cost attribution and adaptive sampling](../../quizzes/evaluation/cost-and-sampling.md) — 8 questions covering attribution mechanism (3), sampling mechanism (3), and the production decision boundary (2).

### Module 7 — Multi-turn (threaded) evaluation (batch 30)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [multi-turn-evaluation.md](./multi-turn-evaluation.md) | ~14 min | The single-turn-trap (every individual turn passes; the conversation as a whole fails). The three shifts from 2024 → 2026 that moved multi-turn from optional to required. The four canonical conversation-level metrics (Conversation Completeness, Knowledge Retention, Role Adherence, Turn Relevancy) with operational definitions. The conversation-level vs turn-level vs trajectory distinction with O(n × k) framing. Threads as first-party concept (LangSmith October 2025). The LangChain Deep Agents five-pattern framework. Span-attached scores for CI/production parity. |
| 📖 [conversation-simulation.md](./conversation-simulation.md) | ~11 min | Why simulation: the alternative is weeks of hand-curated test conversations. The three persona archetypes (cooperative, distracted, adversarial) with system-prompt sketches and the failure modes each catches. The 50/30/20 traffic distribution and the cooperative-only trap. The production tools landscape (DeepEval `ConversationSimulator`, MLflow, LivePerson). The sliding-window pattern with the cross-window-contradiction trade-off. The persona-consistency problem and three mitigations. The Sim2Real gap — why simulation supplements rather than replaces production-trace evaluation. |

Lab applying these: [🧪 Lab 22 — Multi-turn (threaded) evaluation](../../labs/22-multi-turn-evaluation/).

Quiz: [🧠 Multi-turn (threaded) evaluation](../../quizzes/evaluation/multi-turn.md) — 8 questions covering conversation metrics (3), trajectory + simulator (3), and the production decision boundary (2).

---

### Path 06 v2 — Frameworks deep dive (batch 36)

| Page | Read time | Covers |
|------|-----------|--------|
| 📖 [evaluation-frameworks-deep-dive.md](./evaluation-frameworks-deep-dive.md) | ~25 min | A practical selection guide across 9 major LLM evaluation/observability frameworks: LangSmith, Braintrust, Langfuse, Arize Phoenix, Laminar, MLflow GenAI evaluation, DeepEval/Confident AI, RAGAS, TruLens. Eleven-dimension comparison table; code-level snippets for the five canonical operations (logging a trace, creating an evaluator, attaching scores, dataset evaluation, online evaluation); decision guide with one "choose X if" rule per tool; Path 06 module mapping; recipes/projects mapping; migration paths. Explicit anti-scope (no "best tool overall" conclusion; no benchmark claims without sources; no pricing claims without time-bounding). Verified mid-2026 from 8 industry comparison posts; pricing/version data carries publication dates.

---

These fifteen pages open [Path 06 — Evaluation & Observability](../../learning-paths/06-evaluation-observability/). The path documents the full production-readiness stack for agentic AI evaluation and observability across seven modules end-to-end: framing → instrumentation × 2 → online evaluation → drift detection + calibration → cost attribution + adaptive sampling → multi-turn evaluation. **Path 06 v1 is complete.** Path 06 v2 has shipped Recipes (Batch 33), Patterns (Batch 34), Projects (Batch 35), and the Frameworks Deep Dive (Batch 36).

## Pending pages (Path 06 v2)

The following are planned for v2 but not yet authored:

- Embedding-space drift detection (the RAG-input-side complement to Module 5's score-side drift).
- Adversarial red-teaming at scale (DeepTeam-style orchestration).

## Where this is used

- 🧪 [Lab 09: Evaluating agentic RAG](../../labs/09-evaluating-agentic-rag/) — implements the metrics from this section from scratch over Labs 06-08's pipeline.
- 🗺 [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/) — Module 11 (this section + Lab 09) closes Path 02 v1.
