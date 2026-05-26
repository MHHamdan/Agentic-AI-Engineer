# Online evaluator registration

> ⏱ ~13 min · 🔴 Advanced · Prerequisites: [online vs offline evaluation](./online-vs-offline-evaluation.md) (the dataset-vs-live-stream framing), [LangSmith tracing shape](./langsmith-tracing-shape.md) (the underlying instrumentation), familiarity with at least Lab 17.

Module 2 introduced the online-vs-offline distinction: offline evaluation runs against a stored fixture set; online evaluation scores live traces as they're ingested. That page sketched the mechanism. This page covers the implementation: how online evaluators actually get registered against a production trace stream, what action types fire when an evaluator scores low, and the pure-Python alternative when LangSmith's UI-configured Rules aren't the right fit.

By the end you should be able to (1) read a LangSmith Automation Rule and predict what it does, (2) write the Python-SDK equivalent of any Rule, and (3) pick between the two for a specific situation.

## The shift from offline to online

Offline evaluation in Lab 09 and Lab 16 runs against a fixture file (`eval_set.jsonl`). The harness loads the fixtures, runs the agent against each input, computes metrics. Bounded. Deterministic. CI-friendly.

Online evaluation runs against the live trace stream. Every trace your agent emits — every user interaction in production, every staging run, every CI experiment — is a candidate for scoring. The platform (LangSmith / Phoenix / Langfuse / Braintrust) ingests the trace, evaluates it asynchronously, attaches scores back to the trace as feedback. No fixture file; the stream itself is the input.

The shape of the work changes:

| | Offline | Online |
|---|---|---|
| Where does input come from? | Curated fixture file | Live production traffic |
| Reference output exists? | Yes (the curator wrote it) | Usually no |
| When does the evaluator run? | At experiment time (CI, manual) | Continuously, async, on every (or sampled) trace |
| What does it produce? | A score per fixture; aggregated experiment results | Feedback attached to each trace |
| Cost model | Bounded by fixture-set size | Scales with traffic |

The "reference output exists" row matters most. Offline evaluators can compare actual against expected (`trajectory_match`, `groundedness` with reference). Online evaluators usually can't — production users don't ship with golden answers. Online evaluators are typically **reference-free**: they check structural properties (citation_preservation, format_validity, conformance-to-schema) or use LLM-as-judge with criteria-only prompts.

## LangSmith Automations — the canonical mechanism

LangSmith's online-evaluation surface is **Automations** (also called Rules). The model is straightforward: an Automation is a `(filter, sample_rate, action)` triple that fires on traces matching the filter.

**Filter**: which traces this rule applies to. Examples:
- `metadata.environment == "prod"` — only production traces
- `error == false` — only successful traces (or its inverse for error-only)
- `tags contains "agent-v2"` — only the agent variant you're rolling out
- `feedback.user_score < 3` — only low-feedback traces (chains rules together)

**Sample rate**: percentage of matching traces the rule actually fires on. Common values:
- `100%` — every matching trace (LLM-as-judge on prod is expensive at scale; usually not this)
- `10%` — typical baseline for LLM-as-judge evaluators
- `100%` for error traces, `5%` for successful — encoded via separate rules

**Action**: what happens when the rule fires. Six types, in their canonical execution order:

1. **Add to annotation queue** — route to a human for labeling.
2. **Add to dataset** — promote to the offline fixture set for regression testing.
3. **Trigger webhook** — call an external service (custom evaluator hosted elsewhere, alerting system, ticket creator).
4. **Run online evaluator** — built-in LLM-as-judge, configured via the LangSmith UI. Posts the score back as feedback on the trace.
5. **Run custom code evaluator** — a Python function uploaded to LangSmith. Runs on the platform; same shape as a `client.evaluate(...)` evaluator function.
6. **Trigger alert** — send to Slack, email, webhook.

The action order matters when one rule has multiple actions: the annotation-queue routing happens before the dataset-add, before the webhook fire, before the evaluator runs. Within a single rule this is deterministic.

Across rules it's not. Each rule runs on an independent polling schedule. **A webhook rule may process a trace before an evaluator rule scores it, or vice versa.** If you need ordering — for example, your webhook should fire only after the evaluator has scored — express the dependency via a filter: the downstream rule's filter checks for the upstream rule's output (e.g., `feedback.citation_preservation IS NOT NULL`).

## The closed loop in practice

The pattern that works in production strings several Rule types together to close the production-to-fixture-set loop:

1. **Rule A**: filter = all traces, sample 10%, action = run online evaluator (LLM-as-judge for response quality). Most traces get a quality score; the system has aggregate data.
2. **Rule B**: filter = `feedback.quality < 0.5`, sample 100%, action = add to annotation queue. Low-quality traces get routed to a human reviewer.
3. **Rule C**: filter = `tags contains "annotated-as-failure"`, sample 100%, action = add to dataset. Human-confirmed failures join the offline fixture set.
4. **Offline CI**: runs the agent against the dataset on every PR. Catches the regression deterministically next time someone tries to break it.

The loop is what closes production → fixture → regression test. Online evaluators are the entry point; annotation queues are where ambiguity gets human attention; offline datasets are where the lesson gets locked in.

## The Python SDK polling alternative

Automation Rules are UI-configured. When you'd prefer code:

- You have custom logic that doesn't fit the built-in evaluator types (the rule's evaluator is a function in your existing codebase, not something you want to upload to the platform).
- You're backfilling — scoring a batch of historical traces that pre-date the rule. The Rule fires forward only; backfill needs a one-shot script.
- Your existing infrastructure already does polling (cron jobs, scheduled workers). Code fits the operational model.
- You need atomic ordering — a Python script with explicit sequence guarantees beats N independent polling Rules.

The pattern:

```python
from langsmith import Client

client = Client()

# 1. Fetch recent traces
runs = client.list_runs(
    project_name="my-agent-prod",
    execution_order=1,             # root runs only, not sub-runs
    error=False,
    limit=100,
)

# 2. Run your evaluator
def my_evaluator(run) -> dict:
    output = run.outputs.get("answer", "")
    score = 1.0 if "[" in output and "]" in output else 0.0  # citation present
    return {"key": "citation_present", "score": score}

# 3. Post results back
for run in runs:
    result = my_evaluator(run)
    client.create_feedback(
        run.id,
        key=result["key"],
        score=result["score"],
    )
```

That's the Python equivalent of `Rule: filter=all traces, sample 100%, action=run custom code evaluator`. Same outcome; the LangSmith UI displays the feedback identically. Different operational model.

When to use which:

| Use UI Rules when | Use SDK polling when |
|---|---|
| You don't want to maintain custom infrastructure | You already have a Python worker / cron job |
| Evaluator logic fits the built-in types (LLM-as-judge with a prompt) | Evaluator has logic that's hard to express as a single function |
| You're new to the platform; clicking faster than coding | You're backfilling historical traces |
| Sample rate and filter are simple | Filter or sampling logic is complex (depends on multiple feedback values, requires joining external data) |
| Scaling concerns are the platform's problem | You want explicit control over batching, retries, ordering |

Most production teams use both — UI Rules for the standard online-evaluation patterns (LLM-as-judge on a sample of prod traffic), SDK code for custom logic, ad-hoc analysis, and backfills.

## Reference-free evaluators in practice

The production reality is that online evaluators usually can't compare against a reference. Three patterns that work:

**Structural-property checks** (Lab 16's `citation_preservation`, `routing_accuracy`, `plan_validity` all fit here): the evaluator examines the trace itself for properties that don't require knowing the right answer. "Did the agent emit citation markers?" "Did the trajectory visit the expected node sequence?" "Was a plan emitted and was it well-formed?" Fast, free, deterministic.

**LLM-as-judge with criteria-only prompts**: instead of "compare actual against expected," the prompt says "evaluate whether this response satisfies these criteria: helpfulness, factual grounding, principled refusal of unsafe requests." The judge scores on the criteria, not on similarity-to-reference. The judge can still be biased (Zheng et al. 2023); calibration against periodic human labels is required for production confidence — Module 5's topic.

**Heuristic confidence proxies**: model self-reported confidence scores, retrieval-rank distributions, edit-distance between successive turns. None is ground truth; all correlate weakly with quality and can be aggregated cheaply across millions of traces to detect distribution shifts. Module 5's drift-detection territory.

The shift in mindset: offline evaluators answer "did the agent produce the right answer on this fixture?" Online evaluators answer "does this trace look like the kind of trace I expect, given what I know about good agent behavior?" Different question; different evaluator design.

## LangSmith Engine (May 2026)

The newest addition to LangSmith's online-evaluation surface is **Engine** — an AI layer that sits on top of the online-evaluator results. Engine:

- Clusters failing production traces into named issue buckets (instead of treating each trace as an isolated event).
- Diagnoses likely root causes against the connected codebase.
- Drafts evaluator functions automatically — when a cluster surfaces a pattern, Engine proposes a custom evaluator that would catch it.
- Pulls failing traces into offline datasets — automating the production-to-fixture-set loop Step 3 above.
- Drafts PRs with proposed fixes for review.

Engine is built on the online-evaluator mechanism; understanding the mechanism first is required for using Engine well. The patterns in this page are the substrate Engine operates on. The clustering and PR-drafting are productivity multipliers, not replacements for the underlying discipline.

## What this misses

Deferred to later modules:

- **Tail-based sampling at the Collector layer.** Next concept page — [tail-based sampling](./tail-based-sampling.md). The complement to Rules: Rules operate after ingestion, tail-sampling operates before.
- **Drift detection on metric distributions over time.** Module 5. Online-evaluator scores are the input; trend analysis is the output.
- **Agent-as-judge calibration against periodic human ground truth.** Module 5. Required for trusting LLM-as-judge scores in production.
- **Cost attribution via OTel baggage.** Module 6. Online evaluators that fire on every trace are expensive; baggage propagates cost-relevant tags without per-evaluator instrumentation.

## Related concepts

- [Tail-based sampling](./tail-based-sampling.md) — the OTel-Collector-side complement to LangSmith Rules.
- [Online vs offline evaluation](./online-vs-offline-evaluation.md) — the Module 2 page this builds on.
- [LangSmith tracing shape](./langsmith-tracing-shape.md) — the underlying trace data model these Rules operate on.
- [Lab 19 — online evaluation and sampling](../../labs/19-online-evaluation-and-sampling/) — where the SDK polling pattern is wired against synthetic traces.
- [Lab 17 — LangSmith trace ingestion](../../labs/17-langsmith-trace-ingestion/) — the trace-generation prerequisite.

## References

- LangChain docs, *Set up automation rules* — the canonical reference for Rules; filter syntax, sample rate, action types, ordering semantics. [docs.langchain.com/langsmith/rules](https://docs.langchain.com/langsmith/rules).
- LangChain docs, *LangSmith Evaluation* — the offline-vs-online framing from LangChain itself; the dataset-creation-from-production-traces workflow. [docs.langchain.com/langsmith/evaluation](https://docs.langchain.com/langsmith/evaluation).
- LangChain blog (May 2026), *Introducing LangSmith Engine* — the AI-layer extension on top of online evaluators; clustering, evaluator drafting, automated dataset promotion. [blog.langchain.com](https://www.langchain.com/blog/introducing-langsmith-engine).
- LangSmith Python SDK source — `Client.list_runs`, `Client.create_feedback`, the polling pattern. [github.com/langchain-ai/langsmith-sdk](https://github.com/langchain-ai/langsmith-sdk).
- LangChain docs, *Run rules / Run online evaluations* (observability how-tos) — concrete examples of each action type. [docs.smith.langchain.com](https://docs.smith.langchain.com/observability/how_to_guides/rules).
- Zheng et al. 2023, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS — biases in LLM-as-judge evaluators that motivate Module 5's calibration discussion. [arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685).
