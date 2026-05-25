# Lab 16 · Reference solution

The polished final implementation of [Lab 16: Multi-agent evaluation harness from scratch](../README.md).

A reusable evaluation harness over 15 hand-curated multi-agent traces. Five trajectory metrics + two outcome metrics, each implemented as a pure function. Aggregate-then-slice-then-per-agent discipline applied end-to-end.

> 📖 The concept pages that frame this implementation:
> [`multi-agent-evaluation`](../../../concepts/multi-agent/multi-agent-evaluation.md),
> [`trajectory-level-metrics`](../../../concepts/multi-agent/trajectory-level-metrics.md).
> 🧠 Calibrate against the [multi-agent evaluation quiz](../../../quizzes/multi-agent/multi-agent-evaluation.md).
> ⬅️ Builds on the harness pattern from [Lab 09's solution](../../09-evaluating-agentic-rag/solution/README.md) — same hand-curated fixtures + rule-based tier discipline, different unit of analysis (trajectory instead of query/answer pair).

## What this solution implements

The headline path from the parent lab:

- `StrictModel` Pydantic models for `TraceStep` and `Trace` (extra="forbid"). Loud failure on field-drift; the trace_set is a contract.
- Load and validate the 15-trace `trace_set.jsonl` adjacent to the parent lab.
- Five trajectory metrics as standalone pure functions: `handoff_success_rate` (structural-envelope rate), `routing_accuracy` (longest-common-subsequence vs expected handoffs), `plan_validity` (Lab 12 only; reads `plan_valid` flag from final planner step), `plan_coverage` (Lab 12 only; successful executors / plan step count), `replan_rate` (set-level; fraction of Lab 12 traces with >1 planner step).
- Two outcome metrics as standalone pure functions: `citation_preservation` (URL-canonicalized; returns dict with preservation/hallucinated/dropped subscores), `groundedness` (lexical-overlap on content words ≥4 chars, stopwords filtered, threshold 0.5).
- `run_harness(trace_set)` returns a pandas DataFrame with one row per trace, one column per metric.
- Aggregate vs slice-by-category comparison demonstrating the discipline.
- Per-agent breakdown via groupby on the trajectory's node values.
- One synthesis cell closing Path 03 v1.

**Not in this solution** (deliberately): the per-step diagnostic commentary explaining each metric output (parent Steps 2-6 narrative), the LLM-as-judge variant of plan validity (parent Step 9 — optional in the lab, omitted in the canonical harness), the "interesting rows" inspection between metric definitions and the harness run. Those exist for pedagogy; the solution is the mechanism.

## Implementation choices

### Four design decisions worth flagging

**1. Each metric is a pure function with one signature.** `metric_name(trace: Trace) -> float | dict | None`. No globals, no shared state, no class hierarchy. The harness is `for trace in traces: row[metric.name] = metric(trace)`. Side effect: every metric can be moved into a `harness.py` module and unit-tested in isolation without touching the trace loader or the DataFrame builder. The temptation to make `EvaluationHarness` a class with `.run()`, `.aggregate()`, `.slice()` methods is exactly the wrong direction — it couples metric logic to plumbing.

**2. URL canonicalization for citation comparison.** The same web page can appear as `https://example.com/x`, `https://example.com/x/`, `https://example.com/x?utm=foo`, or `https://example.com/x#section-2`. Without canonicalization the metric reads as "missed citation" on what are actually the same page. Canonical form: lowercase scheme + host, strip trailing slash from path (preserve root `/`), strip fragment, strip a denylist of tracking params (`utm_*`, `ref`, `fbclid`, `gclid`). The denylist is small on purpose — overly-aggressive stripping erases content-bearing params (e.g., `?page=2`). Tune per-corpus.

**3. `citation_preservation` returns a dict, not a single number.** Three subscores: `preservation` (fraction of expected citations that appear in final), `hallucinated_count` (citations in final NOT in expected — the critical signal), `dropped_count` (expected citations missing from final — the citation_drift signal). One scalar collapses these into a Schroedinger's metric where 0.5 could mean "half dropped" or "doubled by hallucination" — fundamentally different bugs. The dict resolves the ambiguity at scoring time, not at interpretation time.

**4. Rule-based groundedness is conservative-by-design.** The lexical-overlap check (≥50% of claim's content words appear in supporting content) rejects paraphrased-but-true claims more often than LLM-as-judge does. For regression testing this is the right trade-off: false negatives are cheap (re-check a small flagged set by hand); false positives (saying "grounded" when the answer hallucinated) are expensive. For *grading* you want LLM-as-judge with periodic human calibration — flagged in the concept page, intentionally not built into this solution.

## Common variations that also work

**LLM-as-judge for plan validity.** The parent lab's Step 9 walks through it; the solution omits it because the rule-based version (reading the `plan_valid` flag the validator already set) is sufficient for regression testing. Useful when the validator's logic is suspected of missing semantic issues — the LLM judge can flag "the plan is structurally valid but doesn't actually approach the task."

**Different groundedness thresholds.** Default 0.5. Tighter (0.7) → more false negatives but stronger guarantee on flagged-grounded claims. Looser (0.3) → catches more paraphrased true claims at the cost of accepting some weakly-supported ones. Tune to the trace_set's typical claim-to-content overlap pattern; a non-technical corpus may need a different setting.

**Per-agent metric variants.** Lab 16 implements per-agent breakdown at the *step status* level (counting errors and step-caps per node). A richer variant computes per-agent versions of citation_preservation (researcher → writer fidelity, writer → final fidelity) by splitting the trajectory at handoff points. Useful when you have one agent under suspicion; out of scope for the canonical harness.

**Trace count scaling.** 15 hand-curated traces is enough for diagnostic coverage of 5 categories × 3 source labs. For production replay sets, 50-200 traces is typical. The harness scales — pandas handles the table, the metric functions are O(trajectory length). The bottleneck is *curation*, not computation.

**Production tooling integration.** LangSmith, Phoenix, Galileo, Vertex AI all ship trajectory evaluators. Migration path: keep the metric functions verbatim, swap the trace loader (`trace_set.jsonl` → LangSmith API) and the aggregation backend (pandas DataFrame → production dashboards). The metric algorithms are framework-agnostic.

## Running the solution

```bash
cd labs/16-multi-agent-evaluation-from-scratch/solution
jupyter notebook lab.ipynb
```

Expected wall-clock: **~3 seconds**. Pure-Python computation over 15 traces with 4-11 steps each. No LLM calls in the canonical harness.

Cost: **$0**. No API calls.

If you want to extend with LLM-as-judge, the pattern from the parent's Step 9 transfers verbatim — provider-agnostic ChatModel + JSON-output prompt + retry. Budget ~$0.005-0.01 per judge invocation at gpt-4o-mini rates.
