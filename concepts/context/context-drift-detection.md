# Context drift detection

> 🟡 Intermediate · ⏱ ~24 min · 🛠 Verified 2026-05-29 · 📍 Module 5 of [Path 05 — Context Engineering](../../learning-paths/05-context-engineering/); read after Modules 1-4 ([`foundations.md`](./foundations.md), [`token-budgets.md`](./token-budgets.md), [`compression-and-summarization.md`](./compression-and-summarization.md), [`../memory/memory-tiers.md`](../memory/memory-tiers.md))

## What this page is for

[`compression-and-summarization.md`](./compression-and-summarization.md) cited the [Zylos Research February 2026](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies) finding: "Nearly 65% of enterprise AI failures in 2025 were attributed to context drift or memory loss during multi-step reasoning — not raw context exhaustion." This page covers the detection side — how to spot drift in production traces before it becomes a quality failure, and what trace-level instrumentation makes the four canonical signals visible.

The detection problem is different from the prevention problem. Prevention is what Modules 2-4 covered (budgets, compression, memory tiers); detection is what happens when those layers don't catch everything. Per [Coralogix April 2026](https://coralogix.com/ai-blog/agentic-ai-observability/): "agent-specific failures like wrong tool selection or drifted retrieval don't show up in HTTP-level metrics" — the signal lives in the agent's own behavior, not in the infrastructure layer.

This page covers:

1. **The four early-warning signals** — re-reads, re-decisions, task reframing, retrieval-precision collapse
2. **The signal hierarchy** — leading vs lagging; which to alert on, which to monitor
3. **Trace-level instrumentation** — where each signal gets measured
4. **Reusing Path 06 v2 Lab 23 infrastructure** — embedding-space drift detection applied at the context-zone level
5. **Detection thresholds and alerting** — when drift goes from observable to actionable
6. Operational discipline, anti-patterns, anti-scope

## The four early-warning signals

Each signal points at a specific failure mode the agent's reasoning loop produces when its context window stops working for it. The signals are observable in trace data; the failure modes that produce them are diagnosable from the same data.

### Signal 1 — Re-reads

The agent reads a file, document, or tool output it already processed in an earlier turn. The trace shows the same tool call (often the same arguments) executed multiple times across turns in the same conversation. The mechanism per [`foundations.md`](./foundations.md) Failure 3: when the context window doesn't surface prior work clearly, the agent's planner concludes the work needs to be redone.

**How it shows up in traces**: the same `read_file(path=...)` or `search_docs(query=...)` call appears in turns N and N+3, with identical arguments and (often) identical results. The agent isn't learning anything new on the second call.

**Instrumentation**: per-conversation deduplication index on tool calls. For each call, compute a hash of (tool_name, normalized_arguments); if the same hash appeared earlier in the same conversation, emit a `tool_call.duplicate` event with the original turn number attached.

**Threshold**: re-read rate above 5% of total tool calls per conversation is a leading indicator that compression or memory-tier surfacing isn't working. Above 15% is acute drift.

### Signal 2 — Re-decisions

The agent re-derives a decision it already made earlier in the conversation. The trace shows the same conclusion being reached multiple times with different reasoning chains, often with subtle inconsistencies between the iterations.

**How it shows up in traces**: structured-output fields (decisions, routing, classifications) get reset and re-derived. The "user wants a refund" classification appears at turn 3, then again at turn 7 with the same input data, and the two derivations don't perfectly agree.

**Instrumentation**: track the agent's structured outputs across turns. For each conversation, compute output stability: how often does the same logical decision get re-derived? Persistent state in [LangGraph checkpointers](../memory/memory-tiers.md) is what should make this unnecessary; re-decisions indicate the persistent state isn't being read.

**Threshold**: any high-stakes decision being re-derived more than once in a conversation is a signal to investigate. For routine decisions, occasional re-derivation is acceptable but bounded — > 3 re-derivations of the same decision is acute.

### Signal 3 — Task reframing

The agent's understanding of the user's task gradually shifts as the conversation progresses. The original task was "fix this bug in the authentication module"; by turn 15, the agent thinks the task is "refactor the entire authentication module." The reframing happens incrementally — no single turn made the change.

**How it shows up in traces**: per-turn task summaries (when instrumented) diverge from the original task framing. The semantic distance between turn-1 task framing and turn-N task framing grows beyond a threshold. Per [Latitude March 2026](https://latitude.so/blog/best-ai-agent-observability-tools-2026-comparison): "session traces as causal trajectories" make this visible — the trajectory drifts away from the starting goal.

**Instrumentation**: extract a one-sentence task framing from each turn (or sample frequently). Compute embedding distance from turn 1's framing. Spike detection on the distance time-series surfaces the reframing.

**Threshold**: cosine distance > 0.3 from original task framing is a yellow flag; > 0.5 is acute. The thresholds need calibration per workload (some tasks legitimately evolve; others shouldn't).

### Signal 4 — Retrieval-precision collapse

Retrieved documents (Zone 2b per [`foundations.md`](./foundations.md)) become less relevant to the agent's queries over the conversation. Early turns retrieve docs with high relevance scores; later turns retrieve docs that are increasingly off-topic. The agent's queries themselves drift — symptom of Signal 3 producing Signal 4.

**How it shows up in traces**: retrieval relevance scores (when emitted by the retriever) trend downward over the conversation. Per [Arize March 2026](https://arize.com/blog/best-ai-observability-tools-for-autonomous-agents-in-2026/): "Galileo Signals engine that scans production traces to automatically identify failure modes, hallucinations, and drift patterns" — the production-mature detector treats this as one of the canonical patterns.

**Instrumentation**: log retriever scores per call. Per-conversation, compute the rolling-average precision (top-K relevance score) trend. Slope < 0 over more than 5 consecutive turns is the warning.

**Threshold**: retrieval precision dropping by > 20% from conversation start is a yellow flag; > 40% is acute and usually correlates with task reframing already underway.

## The signal hierarchy

The four signals aren't independent. They have a causal structure that determines which to alert on and which to monitor:

| Signal | Type | Causes | Lead time |
|---|---|---|---|
| Signal 1 — Re-reads | Leading | Compression failing; memory tier not surfacing prior work | Earliest; appears 5-10 turns before quality failure |
| Signal 2 — Re-decisions | Leading | Persistent state not being read; checkpointer broken | Early; appears 3-7 turns before quality failure |
| Signal 3 — Task reframing | Leading-ish | Compounded effect of 1 + 2; attention dilution | Mid; appears 2-5 turns before quality failure |
| Signal 4 — Retrieval-precision collapse | Lagging | Task reframing (Signal 3) producing off-target queries | Latest; appears at or just before quality failure |

The implication: alert on Signals 1 and 2 (leading); monitor Signals 3 and 4 (lagging — by the time they spike, the failure is imminent or already happened). Per [Coralogix April 2026](https://coralogix.com/ai-blog/agentic-ai-observability/): "Session-level evaluation measures coherence across multi-turn conversations, the right shape for agents that hold long-running context. Trajectory mapping detects recursive patterns and shows which tool call the agent keeps returning to before it loops." Signal 1 is the most visible in trajectory mapping; Signal 2 needs structured-output diffing.

## Trace-level instrumentation

The 2026 production discipline per [Arthur April 2026](https://www.arthur.ai/column/agentic-ai-observability-playbook-2026): "An OpenTelemetry (OTel)-first posture is now table stakes. OTel has emerged as the standard for vendor-neutral observability, and its biggest advantage is portability: you can emit traces once and choose any compatible backend without re-instrumenting your code."

The trace tree per [Coralogix April 2026](https://coralogix.com/ai-blog/agentic-ai-observability/): "the trace tree is the foundation, with a root agent span containing nested LLM, task, tool, retrieval, and workflow spans. Four telemetry categories anchor the monitoring stack."

### What each signal needs at the trace level

| Signal | Required trace attributes | Span types involved |
|---|---|---|
| Signal 1 — Re-reads | `tool.name`, `tool.arguments_hash`, `conversation.id`, `turn.index` | Tool spans |
| Signal 2 — Re-decisions | `agent.decision_type`, `agent.decision_value`, `agent.decision_reasoning_summary`, `conversation.id` | Custom decision spans or LLM-output spans |
| Signal 3 — Task reframing | `agent.task_framing_embedding`, `conversation.id`, `turn.index` | Periodic task-framing spans |
| Signal 4 — Retrieval-precision collapse | `retriever.top_k_scores`, `retriever.query`, `conversation.id`, `turn.index` | Retrieval spans |

The instrumentation is per-span attributes; the detection logic lives in the eval/observability layer (Path 06 territory). Per [Maxim May 2026](https://www.getmaxim.ai/articles/best-ai-observability-platform-in-2026-a-comparison-guide/): "AI observability tracks semantic quality and behavior, including whether the agent understood the query, whether the retrieved context was relevant, whether tool calls produced expected outputs."

### A reference instrumentation snippet

```python
import hashlib
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def call_tool(tool_name: str, arguments: dict, conversation_id: str, turn_index: int):
    args_hash = hashlib.sha256(
        json.dumps(arguments, sort_keys=True).encode()
    ).hexdigest()[:16]

    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("tool.name", tool_name)
        span.set_attribute("tool.arguments_hash", args_hash)
        span.set_attribute("conversation.id", conversation_id)
        span.set_attribute("turn.index", turn_index)

        # Detection logic — caller checks for duplicates across turns
        result = _execute_tool(tool_name, arguments)
        span.set_attribute("tool.success", result.ok)
        return result
```

The `args_hash` is what makes Signal 1 detection cheap — a SQL query on the trace store can count duplicates per conversation without re-processing the full argument payloads.

## Reusing Path 06 v2 Lab 23 infrastructure

[Lab 23 (Embedding-space drift detection)](../../labs/23-embedding-space-drift-detection/) covers four drift scenarios at the RAG-pipeline level: gradual query distribution shift, partial corpus refresh, topic/cluster drift, embedding model/version drift. The mechanics — centroid shift, cosine-distance distribution shift, nearest-neighbor overlap — transfer directly to context drift detection at the conversation level.

### The Lab 23 → Path 05 Module 5 mapping

| Lab 23 detector | Applied to context drift |
|---|---|
| **Centroid shift** | Task-framing embeddings per turn; centroid of the conversation's effective task. Signal 3 detection. |
| **Cosine-distance distribution shift** | Tool-output embeddings per turn; shifts surface when retrieval relevance is degrading. Signal 4 detection. |
| **Nearest-neighbor overlap** | Successive turn task-framings vs the original. Low overlap = reframing. Signal 3 detection. |
| **Per-cluster rate-of-change** | Tool-call clusters per conversation; spike in a cluster's frequency = re-read pattern. Signal 1 detection. |

The transfer is non-obvious because Lab 23 was built for RAG-corpus drift (slow-moving population-level signals) while context drift is conversation-level (fast-moving session-level signals). Same statistics; different time horizons. The detector code from Lab 23's `numpy + scipy.stats + sklearn` foundation runs on conversation traces without modification.

### The drift detector composition

Per [`adversarial-red-teaming-at-scale.md`](../evaluation/adversarial-red-teaming-at-scale.md) Path 06 v2 framing: "the orchestration substrate — eval datasets, judge ensembles, severity routing, regression sets, OTel propagation — is the same; what's distinct is the threat-modeling discipline and the deliberate generation of failure-eliciting inputs." Context drift detection sits in the same orchestration but uses the natural-traffic signal stream rather than red-team probes.

The composition:
- **Lab 20** ([drift-detection-and-calibration](../../labs/20-drift-detection-and-calibration/)): evaluator score drift — output side
- **Lab 23** ([embedding-space-drift-detection](../../labs/23-embedding-space-drift-detection/)): embedding-space drift — input side at RAG-pipeline level
- **Path 05 Module 5** (this page): context drift at the conversation level — input side at session level

Three drift detectors at different scopes; one telemetry substrate.

## Detection thresholds and alerting

The detection thresholds depend on workload baseline. The Path 05 Module 5 discipline is to *establish* baselines per conversation type, then *alert* on deviation rather than on absolute thresholds.

### Baseline establishment

For each conversation type (customer support, research, code assistance, document analysis), compute baseline distributions for each of the four signals:

| Signal | Baseline statistic | Typical window |
|---|---|---|
| Re-reads | Median re-read rate as % of tool calls | Rolling 30-day median |
| Re-decisions | Median re-derivations per high-stakes decision | Rolling 30-day median |
| Task reframing | Median cosine distance from start by conversation-end | Per-conversation-type |
| Retrieval-precision collapse | Median end-vs-start precision ratio | Per-conversation-type |

Per-conversation-type because customer-support agents legitimately re-read tickets they've seen before (the user references prior interactions); research agents legitimately reframe tasks as evidence accumulates. The baseline captures what's normal *for that workload*.

### Alert vs monitor

- **Alert on Signal 1 or Signal 2 deviation > 2σ from baseline** — these are leading indicators with enough lead time to intervene
- **Monitor Signal 3 and Signal 4 on dashboards** — alert only if they trigger together with Signal 1 or 2
- **Auto-escalate when 3+ signals fire on the same conversation** — composite drift is usually irrecoverable; the conversation should be handed off to a fresh session or to a human

The discipline matches the Path 06 v2 severity-routing pattern: leading signals trigger investigation; composite signals trigger intervention.

### What "intervention" looks like

The detection layer doesn't fix drift; it surfaces it. Three intervention shapes:

1. **Force a compaction** — trigger Module 3's anchored iterative summarization regardless of soft-cap status. The fresh compaction state may reset the drift pattern.
2. **Escalate to a fresh session** — the agent hands off the work to a new conversation seeded with the compaction state. The new session starts without the drift accumulated in the old one.
3. **Escalate to a human** — for high-stakes workloads, drifted conversations route to human review per Path 03 Pattern 3 (escalation and fallback).

The choice depends on workload stakes and the available fallback. Per Path 07 v1's [`security/safety-policy.md`](../../security/safety-policy.md), high-stakes categories should default to (3) — human review is the right answer when drift hasn't been preventable.

## Operational discipline

Five practices for sustained drift detection hygiene:

1. **Instrument all four signals from day one of deployment**. Adding instrumentation later is expensive — historical traces don't have the attributes; baselines can't be retroactively computed. The OpenTelemetry attributes named in this page belong in the initial deployment.
2. **Per-conversation-type baselines, refreshed quarterly**. Workloads shift; what was normal in Q1 may not be normal in Q2. The baseline refresh keeps the detector calibrated.
3. **Drift detection metrics in the same dashboard as cost and latency**. Per [Arthur April 2026](https://www.arthur.ai/column/agentic-ai-observability-playbook-2026): "collect the full stack of telemetry: latency, errors, hallucinations, bias, drift, accuracy, cost, and tokens. Then, correlate it to KPIs." Drift in isolation is hard to act on; drift correlated with cost spikes or latency increases tells a complete story.
4. **Use the trace store, not aggregated metrics**. The signals require per-conversation analysis; aggregated metrics hide the conversations where drift is happening. Per [Latitude March 2026](https://latitude.so/blog/best-ai-agent-observability-tools-2026-comparison): "annotation queues that surface prioritized traces for human review based on anomaly signals" — the trace-level granularity is what surfaces individual problem conversations.
5. **Feed drift findings back into the eval set**. Conversations that drifted before quality failure become regression cases for Path 06 v2 Lab 24. The drift detection produces the training data for compression-quality and memory-architecture iteration.

## Anti-patterns

Three drift-detection patterns that look reasonable and aren't:

### Alerting on absolute thresholds

A blanket "alert if re-read rate > 10%" produces false positives for workloads where re-reads are normal (customer support agents re-reading tickets) and false negatives for workloads where 10% is already catastrophic (research agents shouldn't re-read at all). Baseline-relative deviation is the right alerting basis.

### Monitoring only output quality metrics

Faithfulness scores and task success rates are lagging indicators. By the time they drop, the failure has already reached the user. The four context-drift signals are *leading* — they predict the quality drop before it happens. Monitoring only the output side leaves the lead time on the table.

### Treating drift as a model bug

A drifting conversation isn't a bug in the underlying LLM; it's a feedback loop between the model's reasoning and the agent's context architecture. The fix lives in the harness (compression, memory tiers, budgets) not in the model. Per [Coralogix April 2026](https://coralogix.com/ai-blog/agentic-ai-observability/): "agent-specific failures don't show up in HTTP-level metrics" — they don't show up in model-level metrics either.

## Anti-scope

What this page does not cover:

- **Long-context model selection** — when 1M-token models are the right answer vs aggressive compression — that's Module 6 ([`long-context-models.md`](./long-context-models.md)). This page assumes the context architecture is already chosen; Module 6 covers the architecture choice itself.
- **General LLM observability** (cost tracking, latency monitoring, token-counting). [`production/`](../../production/) and Path 06 cover the production-side observability; this page covers the context-engineering-specific signals.
- **RAG-pipeline retrieval evaluation** — answer-quality metrics, retrieval-precision-at-K, faithfulness scoring. [`../evaluation/`](../evaluation/) territory; this page consumes those metrics as Signal 4 inputs.
- **Specific observability product comparisons** — Maxim, Latitude, Langfuse, LangSmith, Arize, Galileo, Braintrust, Coralogix all have different feature sets. Picking is downstream of the four-signal discipline; the discipline transfers across products.
- **Auto-remediation of drift**. Detection ≠ fix. The fix lives in Modules 2-4 (budgets, compression, memory tiers) and in the intervention shapes named above; this page covers detection only.
- **Adversarial drift induction**. An attacker deliberately driving a conversation off-topic is a security concern; that's [`../../security/prompt-injection.md`](../../security/prompt-injection.md) territory, not natural-traffic drift.

## References

**2026 observability platforms and patterns**:
- [Coralogix (April 2026), *Agentic AI Observability: A Practical Guide for 2026*](https://coralogix.com/ai-blog/agentic-ai-observability/) — trace-tree foundation; four telemetry categories; session-level evaluation; trajectory mapping
- [Latitude (March 2026), *Best AI Agent Observability Tools in 2026*](https://latitude.so/blog/best-ai-agent-observability-tools-2026-comparison) — 11-platform comparison; GEPA auto-generated evals; annotation queues for anomaly signals
- [Arize (March 2026), *Best AI Observability Tools for Autonomous Agents in 2026*](https://arize.com/blog/best-ai-observability-tools-for-autonomous-agents-in-2026/) — Luna-2 foundation models; Galileo Signals engine for drift pattern detection; "glass box" approach
- [Maxim (May 2026), *Best AI Observability Platform in 2026: A Comparison Guide*](https://www.getmaxim.ai/articles/best-ai-observability-platform-in-2026-a-comparison-guide/) — Gartner 50%-by-2028 prediction; semantic-quality tracking
- [Maxim (May 2026), *Top 5 AI Agent Monitoring Platforms in 2026*](https://www.getmaxim.ai/articles/top-5-ai-agent-monitoring-platforms-in-2026/) — Galileo Signals; PwC 2025 79% agent adoption stat; multi-step failure root cause
- [Arthur (April 2026), *Agentic AI Observability: A 2026 Playbook*](https://www.arthur.ai/column/agentic-ai-observability-playbook-2026) — OTel-first as table stakes; full telemetry stack correlation with KPIs
- [Braintrust (January 2026), *AI observability tools: A buyer's guide*](https://www.braintrust.dev/articles/best-ai-observability-tools-2026) — BraintrustSpanProcessor OTEL integration; semantic quality vs latency monitoring distinction

**Repo cross-references**:
- [`foundations.md`](./foundations.md) — Module 1; three context zones; Failure 3 (re-reading) is what Signal 1 detects
- [`token-budgets.md`](./token-budgets.md) — Module 2; soft caps that should prevent the drift this page detects when they fire
- [`compression-and-summarization.md`](./compression-and-summarization.md) — Module 3; the 65% context-drift failure rate stat that motivates this page; the anchored iterative pattern that should reduce the rate
- [`../memory/memory-tiers.md`](../memory/memory-tiers.md) — Module 4; the persistent state that Signal 2 detects failing to read from
- [`long-context-models.md`](./long-context-models.md) — Module 6; the next module; covers when long-context models are the right answer to drift vs when tiered architecture is
- [Path 06 v2 — Embedding-space drift detection](../evaluation/embedding-space-drift-detection.md) — the upstream concept this page reuses
- [Lab 23 — Embedding-space drift detection](../../labs/23-embedding-space-drift-detection/) — the operational scaffolding (centroid shift, cosine-distance distribution shift, nearest-neighbor overlap) at the RAG-pipeline level
- [Lab 20 — Drift detection and calibration](../../labs/20-drift-detection-and-calibration/) — score-side drift detector; the output-side complement to this page's input-side detection
- [Path 06 v2 — Adversarial red-teaming at scale](../evaluation/adversarial-red-teaming-at-scale.md) — same telemetry substrate; natural-traffic vs adversarial-probe distinction
- [Path 03 Pattern 3 — Escalation and fallback](../../learning-paths/03-multi-agent-systems/patterns/03-escalation-and-fallback.md) — the escalation pattern drift detection triggers
- [`../../security/prompt-injection.md`](../../security/prompt-injection.md) — adversarial drift induction; security-side complement to natural-traffic drift
