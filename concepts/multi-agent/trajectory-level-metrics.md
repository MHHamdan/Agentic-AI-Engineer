# Trajectory-level metrics

> ⏱ ~12 min · 🟡 Intermediate · Prerequisites: [multi-agent evaluation](./multi-agent-evaluation.md) (the framing), Lab 09 (the harness pattern)

This is the implementation companion to [multi-agent evaluation](./multi-agent-evaluation.md). It covers the specific scoring functions [Lab 16](../../labs/16-multi-agent-evaluation-from-scratch/) implements from scratch — five trajectory metrics, two outcome metrics — with the Python signatures you'll write. Each metric has a "what it reveals / what it hides" line so you know when to reach for which.

## The trace shape Lab 16 assumes

A trace is the recorded execution of one multi-agent run. The shape Lab 16 uses:

```python
@dataclass
class TraceStep:
    """One step in a multi-agent trajectory."""
    node: str          # which agent: "supervisor", "researcher", "writer", ...
    args: dict          # what the agent received
    output: dict        # what the agent returned (or raised)
    status: str         # "ok", "error", "step_cap", "wrong_tool", ...


@dataclass
class Trace:
    """One recorded multi-agent run, end-to-end."""
    id: str                              # "lab10_t01"
    source_lab: str                       # "lab10" | "lab11" | "lab12"
    task: str                             # the user's task
    trajectory: list[TraceStep]
    final_answer: str
    expected_handoffs: list[str]          # golden routing sequence
    expected_citations: list[str]         # golden citation IDs
    category: str                         # "happy_path" | "tool_failure" | ...
```

The five trajectory metrics consume `trace.trajectory` plus `trace.expected_handoffs`. The two outcome metrics consume `trace.final_answer` plus `trace.expected_citations` plus (for groundedness) the cited content. Everything else (per-agent breakdown, category slicing) is bookkeeping over these.

## The five trajectory metrics

### 1. Handoff success rate

```python
def handoff_success_rate(trace: Trace) -> float:
    """Fraction of inter-agent handoffs that delivered the expected payload."""
```

A handoff is one agent emitting a structured envelope that the next agent reads. In Lab 10's pattern, the researcher emits `{findings, citations, status}` and the supervisor passes it to the writer. A successful handoff means the envelope was well-formed (every required field present, types correct, `status` not in `{error, step_cap}`) and the next agent received it intact.

A failed handoff is structural: missing fields, malformed citations list, status indicating upstream failure that the next agent didn't surface. The metric measures the rate of *successful* handoffs, not the count of total handoffs.

**What this reveals**: structural handoff failures. The most common multi-agent bug is "the researcher returned `{status: 'step_cap'}` and the writer composed prose around an empty findings field as if it were real." This metric fires when that happens.

**What this hides**: semantic handoff drift (the envelope was well-formed but the *content* of `findings` got paraphrased into uselessness during transit). That's a content metric, not a structural metric — see citation preservation below.

### 2. Routing accuracy

```python
def routing_accuracy(trace: Trace) -> float:
    """Fraction of supervisor routing decisions that matched the expected route."""
```

For each supervisor step in the trace, check what the supervisor decided next (researcher? writer? END? replan?) against the expected decision from `trace.expected_handoffs`. A 1.0 score means every routing decision was correct; 0.0 means none were.

In Lab 12's plan-and-execute, "routing accuracy" generalizes to "did the planner emit a plan that routes to the right tools for each step." Same concept, different vocabulary.

**What this reveals**: routing bugs. The supervisor calling the writer before the researcher has any findings. The supervisor finalizing without calling either worker. The supervisor looping on the same worker because the LLM keeps emitting the same tool call.

**What this hides**: routing decisions that are correct in isolation but produce a bad trajectory in aggregate. A supervisor that always routes correctly to the researcher but never knows when to stop researching has 1.0 routing accuracy and a step_cap_hit trajectory. Pair this with the step-cap-hit rate to catch that pattern.

### 3. Plan validity

```python
def plan_validity(trace: Trace) -> float:
    """For Lab 12-style trajectories: did the plan pass validate_graph()?

    Returns 1.0 if the planner emitted a valid plan, 0.0 otherwise.
    Returns None for traces without a plan step (Lab 10/11 style).
    """
```

Lab 12's planner emits a structured `Plan` with steps, dependencies, and parallel groups. The plan-and-execute pattern's `validate_graph()` method (Kahn's algorithm + four sanity checks: no cycles, no duplicate IDs, no unknown tools, no parallel-group violations) is the validity test. Either the plan passes or it doesn't.

This is a binary per-trace metric. The aggregate across a trace set tells you the planner's reliability: 0.95 means 1-in-20 plans need a retry-on-validation-failure or a replan.

**What this reveals**: planner reliability. Most planner failures are structural (depends_on a step that doesn't exist; a cycle; a tool that the executor doesn't have). These all show up as validity failures.

**What this hides**: plans that are valid but pointless. A plan with one `web_search` step is valid and trivially executable; whether it's the *right* plan for the user's task is a different question — see "plan coverage" below.

### 4. Plan coverage

```python
def plan_coverage(trace: Trace) -> float:
    """Fraction of plan steps that actually executed with status='ok'.

    Returns None for traces without a plan step.
    """
```

A plan has N steps. The trajectory shows that K of those steps were dispatched, of which J completed with `status="ok"`. Plan coverage is `J / N`. A score of 1.0 means every plan step ran cleanly; a score below 1.0 means some steps failed, were skipped (because their dependencies failed), or were never dispatched at all.

This is distinct from plan validity. A plan can be perfectly valid (passes `validate_graph`) and have 0.4 coverage (the planner asked for 5 steps; 3 of them hit `tool_failure` on a live website; the dispatcher correctly skipped two more that depended on the failed steps).

**What this reveals**: the gap between planning and execution. Low coverage with high validity points at tool failures, retrieval misses, or executor errors — not at the planner. High coverage with low validity is rare and points at a buggy validator.

**What this hides**: which step type is failing. A 0.6 coverage score doesn't tell you whether `web_search` is failing or `fetch_page` is failing. To localize, slice by tool name within the failing steps.

### 5. Replan rate

```python
def replan_rate(trace_set: list[Trace]) -> float:
    """Fraction of trace runs that triggered at least one replan."""
```

This is a trace-set-level metric, not a per-trace metric. It counts how many traces in the set hit the replanner at least once. (You can also report mean replans per trace, which is more diagnostic if the cap is high.)

A healthy replan rate depends on the workload. For Lab 12's pattern with `MAX_REPLANS = 2`, a replan rate below ~10% on a happy-path-dominated set is reasonable; above ~30% suggests the planner is brittle, the tool registry is incomplete, or the user tasks need decomposition before they reach the planner.

**What this reveals**: planner brittleness and execution-environment volatility. If the replan rate climbs over time on the same trace set, either your planner has regressed or the world has shifted under it (sites going down, rate limits, etc.).

**What this hides**: the *quality* of replans. A replan rate of 0.20 with `MAX_REPLANS = 2` and an identical-plan-dedup catching 80% of those replans means most replans converge — the metric looks bad but the system is healthy. Pair with the dedup-fire rate to disambiguate.

## The two outcome metrics

### 6. Citation preservation across handoffs

```python
def citation_preservation(trace: Trace) -> float:
    """Fraction of expected citations that survived from the researcher's
    output through to the final answer's citation list."""
```

Lab 10's researcher emits a list of citations. The writer is supposed to preserve them by reference (inline `[1]`, `[2]` markers + citations listed at the end). Citation preservation measures how many of the researcher's citations actually appear in the final answer's citation list.

The metric is more subtle than it sounds. There are four failure modes:

- **Drop**: a citation in `researcher.output.citations` is missing from `final_answer`. Most common.
- **Duplicate**: same citation listed twice in `final_answer`. Indicates the writer didn't dedup; rare but noisy.
- **Hallucinated**: a citation in `final_answer` that wasn't in `researcher.output.citations`. The writer invented it. Critical.
- **Renumbered**: the same URL appears as `[1]` in the researcher's output and `[3]` in the final answer; the *content* is preserved but the inline references in the prose won't line up unless the writer also renumbers consistently.

Lab 16 computes preservation as `|expected_citations ∩ final_citations| / |expected_citations|`. Hallucinations are caught by a separate `hallucinated_citation_count` companion metric. The metric is intentionally not URL-equality alone — it canonicalizes URLs first (strip trailing slashes, fragment identifiers, common query-param noise) to avoid false negatives.

**What this reveals**: handoff fidelity for the structured payload. The most common Lab 10/13 bug — the writer paraphrasing the researcher's brief into uselessness — shows up here as low preservation with high routing accuracy.

**What this hides**: whether the cited content was actually used. A 1.0 preservation score with a final answer that doesn't mention any of the cited facts is technically a pass. You need groundedness for that.

### 7. Groundedness for final answers

```python
def groundedness(trace: Trace) -> float:
    """Fraction of factual claims in final_answer that are supported by
    the retrieved/researched content the system actually saw."""
```

Lab 09 defines groundedness for single-agent RAG: every claim in the answer must trace to a chunk the retriever returned. Multi-agent groundedness extends this — every claim in the final answer must trace to content the system retrieved or researched (whether via a retriever-worker, a `fetch_page` call, or a tool result).

In Lab 16 we implement two tiers, following Lab 09:

- **Rule-based**: lexical-overlap between the claim and the supporting content. Fast, cheap, conservative (high false-negative rate on paraphrased claims).
- **LLM-as-judge**: a separate LLM call assesses whether each claim is supported. Better recall on paraphrased claims; subject to the Zheng et al. biases; costs $0.50-$1.00 per 50-trace evaluation.

The rule-based version is good enough for regression testing (catch when groundedness drops). The LLM-as-judge version is useful when you need to defend a specific groundedness number externally.

**What this reveals**: hallucination at the synthesis layer. A multi-agent system can have perfect retrieval, perfect handoffs, and still hallucinate in the synthesizer because the synthesizer LLM saw the retrieved content and decided to embellish.

**What this hides**: whether the claims, even if supported, *answer the user's question*. A final answer that's perfectly grounded in retrieved content but discusses a different topic from what the user asked has 1.0 groundedness and 0.0 relevance. Pair with answer-relevance for the full picture; Lab 16 implements relevance as a stretch metric (LLM-as-judge only).

## Aggregating and slicing

The seven metrics give you seven numbers per trace. Across a 15-trace set that's 105 numbers — way too many to read as a flat table.

The discipline Lab 09 taught carries over: slice by category before you do anything else. The same `routing_accuracy = 0.87` means different things depending on whether the 13% failures were on `happy_path` traces (alarming) or `tool_failure` traces (expected — when the tool fails the supervisor sometimes routes oddly).

Lab 16's category set:

| Category | What this slice tests | Healthy-system signature |
|---|---|---|
| `happy_path` | Everything works end-to-end | routing_accuracy ≈ 1.0, plan_validity = 1.0, citation_preservation ≈ 0.95 |
| `tool_failure` | One tool call fails | handoff_success_rate < 1.0 (expected), no plan invalidity, recovery via fallback |
| `replan_needed` | Plan fails partway, must replan | plan_validity = 1.0, plan_coverage drops on first plan + recovers on replan, replan_rate = 1.0 |
| `citation_drift` | Researcher produces citations, writer drops some | citation_preservation drops (this is the failure being tested) |
| `step_cap_hit` | Worker exceeds step budget | handoff carries `status: "step_cap"`, downstream agent surfaces the cap explicitly |

Aggregate metrics across categories will lie — the citation_drift category will drag the headline citation_preservation number down, which looks bad until you slice and see that happy_path runs preserve at 0.97 and only the citation_drift category drops.

## Per-agent slicing

The same metrics can also be computed per-agent. Routing accuracy is intrinsically supervisor-scoped (only the supervisor routes). Handoff success rate becomes per-agent by looking at handoffs *emitted by* each agent. Citation preservation can be split into "researcher → writer preservation" (how much the writer dropped) and "writer → final preservation" (how much made it into the final answer; for Lab 10 these are the same number).

Per-agent slicing is most useful when you have one agent suspected of dragging metrics down. You compute per-agent scores once, identify the worst performer, then iterate on its prompt or its post-processing. Lab 16 demonstrates this for the supervisor and researcher; the pattern generalizes.

## The headline metric

If you need one number to track over time, the right choice depends on the system's purpose:

- Information-retrieval tasks (Lab 10, Lab 13): **citation preservation × groundedness**. The product. Both must be high.
- Multi-step task automation (Lab 12): **plan_validity × plan_coverage**. The product. The plan must be valid and must execute.
- Refinement systems (Lab 11): **groundedness × refinement-effectiveness**. The product. The system must converge.

A single headline metric is misleading on its own but useful as a dashboard summary. Always pair it with a per-category breakdown in the actual report.

## Related concepts

- [Multi-agent evaluation](./multi-agent-evaluation.md) — the framing this page implements.
- [Lab 09's RAG evaluation harness](../../labs/09-evaluating-agentic-rag/) — the precedent. Lab 16 uses the same hand-curated-fixture + rule-based-tier + LLM-as-judge-tier + category-slicing approach.
- [Lab 16 multi-agent evaluation harness](../../labs/16-multi-agent-evaluation-from-scratch/) — where these metrics are implemented from scratch.
- [The four Path 03 patterns](./README.md) — the systems being evaluated.

## References

- Google Cloud Vertex AI, *Agent evaluation* — the `trajectory_exact_match` / `trajectory_precision` / `trajectory_recall` formalization. [cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai).
- LangChain `agentevals` repository — pre-built LLM-as-judge trajectory evaluators. The trace-as-message-list shape that LangGraph produces directly. [github.com/langchain-ai/agentevals](https://github.com/langchain-ai/agentevals).
- AWS, *Evaluating AI agents: Real-world lessons from building agentic systems at Amazon* (Feb 2026) — planning score, communication score, collaboration success rate as named per-agent metrics. [aws.amazon.com/blogs/machine-learning](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/).
- Galileo, *How to Build an Agent Evaluation Framework* (Feb 2026) — argues the "60% on single-run, 25% across 8 runs" reliability gap that trajectory metrics surface but outcome metrics don't. [galileo.ai/blog](https://galileo.ai/blog/agent-evaluation-framework-metrics-rubrics-benchmarks).
- Zheng et al. (2023), *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS — the three documented LLM-as-judge biases (position, verbosity, self-enhancement). [arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685).
