# Recipe 1 — LangSmith-native production composition

> 🟡 Slow-moving · ⏱ ~20 min · 🛠 Verified 2026-05-26 · 📍 Read after Modules 2, 4, 5, 7 of Path 06 v1

## When this recipe fits

Your team is already building on LangChain or LangGraph; the agent surfaces are LangChain primitives (chains, agents, graphs). Adding LangSmith costs you near-zero instrumentation effort because the integration is automatic via environment variables. You're OK with proprietary platform coupling because the LLM-eval UX (annotation queues, dataset diffs, replay-against-new-models) earns the vendor commitment for the team. You're typically below 1M traces/month, so LangSmith's per-trace pricing fits the budget.

This is the fastest path from zero to production observability **if** the prerequisites hold. If your stack is not LangChain-rooted, see [Recipe 2](./02-opentelemetry-native.md) (OTel-native). If you need both LangSmith's eval UX and vendor-neutral telemetry for your APM stack, see [Recipe 3](./03-hybrid-langsmith-and-otel.md).

## What you'll have when you're done

- A LangSmith project ingesting every production agent run as a structured trace.
- A LangSmith Dataset versioning your eval set with annotation history.
- Two registered evaluators running automatically on production traffic: one deterministic (e.g., `graph_trajectory_strict_match`), one LLM-as-judge.
- A drift-review dashboard surfacing distribution shifts on evaluator scores week over week.
- An annotation queue routing low-scoring runs to a human reviewer.
- Multi-turn evaluation running on threaded conversations once they're marked complete.
- Trace tags + metadata that let you slice by tenant, user, task type, and model.

## Architecture at a glance

```mermaid
flowchart LR
    App[LangChain / LangGraph<br/>agent code] -->|@traceable<br/>env-var auto-trace| LS[LangSmith<br/>platform]

    LS --> Dash[Project dashboard<br/>traces, threads]
    LS --> DS[Datasets<br/>versioned eval sets]
    LS --> Auto[Automation Rules<br/>online evaluators]
    LS --> Drift[Dataset diff<br/>drift review]
    LS --> AQ[Annotation queue<br/>human calibration]

    Auto --> Scores[Span-attached<br/>scores]
    Scores --> Drift
    Scores --> AQ
    AQ -->|labels| DS

    style App fill:#fff4e6
    style LS fill:#f3e8ff
    style Scores fill:#e6f6ec
```

The whole architecture lives inside LangSmith. Your app emits; LangSmith ingests, evaluates, stores, displays, and routes. No external Collector. No second backend.

## Step-by-step assembly

### Step 1 — Instrument the app (Module 2; Lab 17 patterns)

Three environment variables and you're tracing:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=my-prod-agent
```

LangChain/LangGraph picks them up at import time; every chain, agent, and graph run emits a trace automatically. For custom Python functions outside the LangChain surface (a retriever helper, a tool wrapper), wrap with `@traceable`:

```python
from langsmith import traceable

@traceable(name="retrieve_context", run_type="retriever")
def retrieve_context(query: str, top_k: int = 5) -> list[dict]:
    ...
```

For project scoping (separate `prod`, `staging`, and `eval` traces), use `tracing_v2_enabled` as a context manager around the runs you want isolated.

→ See [`concepts/evaluation/langsmith-tracing-shape.md`](../../../concepts/evaluation/langsmith-tracing-shape.md) and [Lab 17](../../../labs/17-langsmith-trace-ingestion/) for the full surface.

### Step 2 — Define datasets in the LangSmith UI (Modules 2, 4)

A LangSmith Dataset is a versioned, annotated eval set. Three creation paths:
- **Synthetic seed** — generate 20-50 inputs covering your task categories; LangSmith's UI lets you create these manually.
- **Production-derived** — pull 50-100 production traces that you want representative of real traffic; LangSmith's "Add to Dataset" button on any trace handles this.
- **CSV/JSONL upload** — for migrating an existing harness.

Naming convention that survives audits: `<agent-name>-<dataset-purpose>-v<n>`, e.g., `support-bot-regression-v3`, `support-bot-hard-cases-v1`.

Versioning matters more than you'd expect. When your evaluator catches a regression, you need to be able to tell whether the eval set changed or the model changed. LangSmith Datasets are explicit about version pins.

### Step 3 — Register Automation Rules (Module 4 LangSmith path)

Automation Rules are LangSmith's UI-driven online evaluators. The pattern:
- **Trigger**: matches against trace metadata (e.g., `project = my-prod-agent` and `tags contains "billable"`).
- **Sample rate**: typically 5-20% of matching traces (LangSmith pricing scales with evaluation runs; sampling is the cost lever).
- **Evaluator**: either a built-in (`harmfulness`, `relevance`) or a custom one defined in Python and uploaded.

For LangChain-rooted agents, the `agentevals` package gives you ready-made trajectory evaluators (`graph_trajectory_strict_match`, `create_trajectory_llm_as_judge`). These plug directly into Automation Rules.

→ See [`concepts/evaluation/online-evaluator-registration.md`](../../../concepts/evaluation/online-evaluator-registration.md) for the LangSmith Rules vs SDK polling trade-off; [Lab 19](../../../labs/19-online-evaluation-and-sampling/) demonstrates both.

### Step 4 — Drift review via Dataset diffs (Module 5)

LangSmith's Dataset diff view compares evaluator scores between two runs of the same dataset. You typically run the dataset weekly; the diff view highlights:
- Examples that newly fail.
- Examples whose scores moved by more than a threshold.
- Aggregate distribution shift.

This is the LangSmith-native answer to drift detection. It doesn't expose KS-test / PSI / Wasserstein directly the way [Lab 20](../../../labs/20-drift-detection-and-calibration/) does, but it surfaces the same signal: "the distribution moved week over week, and here are the specific examples that drove the move."

For teams that want explicit statistical tests on top, run the weekly Dataset run output through Lab 20's KS / PSI / Wasserstein functions. The Dataset run gives you the score arrays; the stats apply directly.

→ See [`concepts/evaluation/drift-detection.md`](../../../concepts/evaluation/drift-detection.md) for the algorithms.

### Step 5 — Annotation queues for human calibration (Module 5)

The LangSmith annotation queue is the operational form of LLM-as-judge calibration. The pattern:
- Configure the queue to route runs whose evaluator score is below a threshold (or above a different threshold, depending on what you're checking for).
- Domain experts open the queue, see the run alongside its evaluator score, mark agree/disagree, and optionally add a free-text label.
- The labels accumulate as a calibration set for the evaluator.

When agree-rate drops below ~80% (Cohen's κ < 0.6 territory), the LLM-as-judge prompt needs revision or the rubric needs tightening. This is where Lab 20's calibration discipline transfers.

→ See [`concepts/evaluation/agent-as-judge-calibration.md`](../../../concepts/evaluation/agent-as-judge-calibration.md) for the κ math.

### Step 6 — Threads for multi-turn evaluation (Module 7)

LangSmith made threads a first-party concept in October 2025. The pattern:
- Each conversation gets a `thread_id` set as run metadata: `with tracing_v2_enabled(metadata={"thread_id": session_id}): ...`
- Multi-turn Evals run automatically once a thread is marked complete (timeout-based or explicit-signal-based).
- The LLM-as-judge prompt defines the scoring rubric — Conversation Completeness, Knowledge Retention, Role Adherence, Turn Relevancy.

→ See [`concepts/evaluation/multi-turn-evaluation.md`](../../../concepts/evaluation/multi-turn-evaluation.md) and [Lab 22](../../../labs/22-multi-turn-evaluation/).

## Lab-shape vs production-shape

| Module | Lab shape | Production shape (this recipe) |
|---|---|---|
| M2 — Instrumentation | `@traceable` on a few helper functions; `tracing_v2_enabled` for project scoping | Environment variables flip auto-tracing on; `@traceable` only for non-LangChain helpers |
| M4 — Online eval | SDK polling pattern hand-rolled in Python | UI-defined Automation Rules with sample-rate sliders |
| M5 — Drift | KS/PSI/Wasserstein on synthetic streams in a notebook | Weekly Dataset runs + Dataset diff view; statistical tests applied to the score arrays as a follow-up |
| M5 — Calibration | Simulated judge against a 10-example gold set | Annotation queue routing low-score runs to domain experts; agree-rate as the calibration metric |
| M7 — Multi-turn | Three from-scratch metrics on hand-crafted conversations | LangSmith Multi-turn Evals with LLM-as-judge prompt defining all four canonical metrics |

The labs build the math from scratch; production deploys the LangSmith-native abstractions over the same math.

## Hand-off points

Even in a "single-platform" recipe, ownership boundaries matter:

| Artifact | Emitted by | Consumed by | Lives in |
|----------|-----------|-------------|----------|
| Trace data | Agent app | LangSmith ingestion | LangSmith project |
| Evaluator scores | Automation Rules | Dashboard + annotation queue | LangSmith run feedback |
| Annotation labels | Domain experts | Calibration analysis | LangSmith dataset metadata |
| Dataset versions | Eval engineer | Dataset diff view | LangSmith dataset history |
| Thread completion signal | Agent app (explicit) or LangSmith (timeout) | Multi-turn Evals trigger | Thread metadata |

The "Agent app emits" boundary is what stays portable if you outgrow LangSmith later. Everything else is platform-coupled.

## What this recipe doesn't give you

- **Cost attribution beyond LangSmith's built-in trace counts.** If you need per-tenant LLM token cost rolled up with per-tenant infra cost, see Recipe 2 (OTel baggage path).
- **Tail-based sampling.** LangSmith's Automation Rule sample rates are probabilistic only — you can't say "always retain errors, sample everything else at 10%". For policy-based tail sampling, see Recipe 2 or 3.
- **Vendor-neutral telemetry.** If your APM stack needs the same traces (Datadog, Honeycomb, etc.), you're either dual-emitting (Recipe 3) or accepting the duplicate-data tax.
- **Self-hosted deployment.** LangSmith is a managed platform; the self-hosted option exists but is enterprise-tier.
- **Compliance evidence generation** (EU AI Act, NIST AI RMF). LangSmith provides audit trails; turning those into compliance artifacts is organizationally-specific.

## Operational checklist (pre-launch)

- [ ] Three env vars set in production: `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`.
- [ ] Separate projects for `prod`, `staging`, `eval` — never share a project across environments.
- [ ] `LANGCHAIN_API_KEY` rotated quarterly; stored in your secrets manager, not in code or env files committed to git.
- [ ] At least one Dataset created with ≥30 examples covering the agent's task categories.
- [ ] At least one Automation Rule registered with a sample rate ≤ 20% (cost discipline).
- [ ] Annotation queue configured with a low-score threshold; at least one domain reviewer assigned.
- [ ] Trace tags + metadata schema documented in your team's runbook: `tenant_id`, `user_id`, `task_type`, `model_version`.
- [ ] Threads marked complete explicitly (don't rely on the timeout default unless your conversations are short).
- [ ] Cost alert set in LangSmith for monthly trace count exceeding budget.
- [ ] Dataset versioning policy documented: when to bump major, when to bump minor.
- [ ] Replay-against-new-model workflow tested: pin a Dataset, swap the model in your agent config, re-run.
- [ ] Per-evaluator pass rate tracked weekly; alert on > 10 percentage-point drops.
- [ ] Annotation queue agree-rate tracked monthly; trigger LLM-as-judge prompt review if < 80%.

## Cost envelope

Verified 2026-05-26. Re-verify against current LangSmith pricing before committing.

LangSmith pricing (Plus tier, mid-2026): $39/seat/month; trace ingestion included up to plan limit; per-trace overage charges above that. Eval runs counted separately as "API calls".

| Traffic | LangSmith platform | LLM-as-judge | Total /month |
|---------|--------------------|---------------|---------------|
| 10K traces, 10% eval sample, 2 evaluators | $39 (1 seat) | ~$5-15 | $44-54 |
| 100K traces, 10% eval sample, 2 evaluators | $39-78 (1-2 seats) + plan overage | ~$50-150 | $89-228 |
| 1M traces, 5% eval sample, 2 evaluators | Custom Enterprise pricing | ~$250-750 | Custom + LLM |

LLM-as-judge cost dominates at higher volumes — typical mid-2026 budget at 1M traces is ~$500-1500/mo on judge alone if running `gpt-4o-mini` with full evaluator coverage. Drop the sample rate or move to a cheaper judge tier to control.

The Enterprise tier kicks in around 500K-1M traces/month; pricing becomes a negotiation rather than a published rate.

## References + further reading

- [`concepts/evaluation/langsmith-tracing-shape.md`](../../../concepts/evaluation/langsmith-tracing-shape.md) — the LangSmith data model.
- [`concepts/evaluation/online-vs-offline-evaluation.md`](../../../concepts/evaluation/online-vs-offline-evaluation.md) — when online evals earn their place.
- [Lab 17](../../../labs/17-langsmith-trace-ingestion/) — the working instrumentation lab.
- [Lab 19](../../../labs/19-online-evaluation-and-sampling/) — the Rules-vs-SDK-polling comparison.
- [Lab 22](../../../labs/22-multi-turn-evaluation/) — the multi-turn metrics that LangSmith Multi-turn Evals approximate.
- LangChain blog (October 2025), *Improve agent quality with Insights Agent and Multi-turn Evals* — [blog.langchain.com](https://blog.langchain.com/insights-agent-multiturn-evals-langsmith/).
- LangSmith documentation, *Trace with OpenTelemetry* (March 2026) — [docs.langchain.com](https://docs.langchain.com/langsmith/trace-with-opentelemetry) — note that OTel ingestion is the path to migrate later if you outgrow this recipe.
- Digital Applied (April 2026), *Agent Observability Platforms 2026* — [digitalapplied.com/blog](https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026) — the industry-survey data showing LangSmith's positioning.
