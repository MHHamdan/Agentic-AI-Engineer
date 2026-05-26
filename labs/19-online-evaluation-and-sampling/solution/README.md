# Lab 19 · Reference solution

The polished final implementation of [Lab 19: Online evaluation and tail-based sampling](../README.md).

## What this is

Two halves. **Half A** demonstrates LangSmith-side online evaluation: generate synthetic traces, define a reference-free evaluator, score the live trace stream via the SDK polling pattern, audit the resulting feedback. **Half B** simulates the OTel Collector's `tail_sampling` processor: a production-realistic YAML config, the priority-policy stack (errors → latency → probabilistic), and the policy-evaluation logic in Python.

- **Synthetic trace generation** (`client.create_run`) — a 50-trace stream representative of production volume.
- **Reference-free evaluator** — JSON-shape validity check (no human gold set needed).
- **SDK polling pattern** — `client.list_runs` + filter + score + `client.create_feedback`. The lab-side pattern that's portable across LangSmith / Langfuse / Phoenix.
- **The Automation Rule equivalent** — same outcome via the LangSmith UI; documented as a walkthrough.
- **Sample-rate cost arithmetic** — at 1M traces/month, what's the budget impact of scoring 100% vs 10%?
- **Collector YAML** — the priority-policy stack with `decision_wait=30s`, `num_traces=360000`, and the canonical errors / latency / probabilistic order.
- **Policy simulation in Python** — `simulate_policies(traces, policies)` runs the same first-match-wins logic the Collector runs.
- **The load-balancing constraint** — why scaling the Collector to multiple instances requires `loadbalancingexporter` first-tier routing by `traceID`.

## How it differs from `../lab.ipynb`

| Lab notebook (26 cells) | Solution (27 cells) |
|---|---|
| Step-by-step tutorial framing | One-line headers; explanation lives in concept pages |
| Half A and Half B introduced separately with intros | Same two-halves structure, less ceremony |
| Inline UI screenshot placeholders for the Automation Rule | Compact text walkthrough |
| Sanity-test cells for each policy type | Combined into the simulate_policies call site |

## Implementation choices

1. **SDK polling over LangSmith Rules for portability.** The same `client.list_runs` + score pattern works against any LangSmith-API-compatible backend. The Automation Rules path is LangSmith-specific. The solution shows both, leads with the portable one.
2. **Synthetic traces over real agent runs.** The lab is about online evaluation infrastructure, not agent behavior. Synthetic traces with controlled failure modes (3 missing-output, 2 malformed-JSON) make the demo deterministic.
3. **Reference-free evaluator as the canonical online-eval pattern.** Online evaluators run against live production traffic where you don't have a gold answer. The reference-free pattern (JSON-shape validity, schema conformance, output-length sanity) is what works at scale.
4. **The Collector YAML is shown but not deployed.** Production deployment requires Docker + a real OTel pipeline; the notebook simulates the policy logic in Python to show what the Collector does, not how to operate one.
5. **`decision_wait=30s` and `num_traces=360000` as the agent-specific defaults.** The default 10s `decision_wait` is wrong for agents whose traces span 10-30 seconds. The `num_traces` formula: `traces_per_sec × decision_wait × 1.2` (the 1.2 is safety margin).
6. **The probabilistic-within-tail pattern** rather than running a separate probabilistic processor upstream. Putting the probabilistic policy inside the tail_sampling processor ensures errors and high-priority traces aren't dropped randomly before policy evaluation.

## What's deliberately out of scope

- **Real Collector deployment.** Docker, multi-node, load balancer. Out of scope for a notebook.
- **The OTLP-over-HTTP vs OTLP-over-gRPC trade-off.** Both work; the lab uses HTTP for simplicity.
- **Probabilistic head sampling at the SDK level.** A different operational layer; mentioned for context.
- **Adaptive sampling based on cost.** That's Module 6 territory (Lab 21).
- **Annotation queues** as the production-to-fixture loop. Mentioned in the concept page; the lab demonstrates the evaluator pattern but doesn't wire up an annotation queue.

## Running the solution

```bash
cd labs/19-online-evaluation-and-sampling/solution

export LANGCHAIN_API_KEY=...    # Required for Half A
# Half B uses no external services — pure Python policy simulation

jupyter notebook lab.ipynb
```

**Wall-clock**: ~30-60 seconds. Half A creates synthetic LangSmith runs (fast); Half B is pure Python computation.

**Cost**: ~$0 — no LLM calls; the synthetic traces have hand-written outputs.

## Reading the headline result

The Collector-policy simulation on a representative trace stream produces something like:

```
Reason                          Kept
errors                            4
slow-traces                       8
probabilistic-baseline           12
(dropped)                        26
Total retained: 24/50 = 48%
```

At 1M traces/month with this retention rate, ingestion volume drops from ~50 GB/mo to ~24 GB/mo. The headline pattern: **errors and slow traces get 100% retention; the rest gets the probabilistic baseline.** That's what tail-based sampling buys you over head sampling — the high-value-trace coverage doesn't depend on luck.

## Next

- Take the [online evaluation quiz](../../../quizzes/evaluation/online-evaluation.md).
- Lab 20 builds on the score stream this lab produces with drift detection + judge calibration.
