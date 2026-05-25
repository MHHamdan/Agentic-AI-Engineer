# Multi-agent evaluation

> ⏱ ~13 min · 🟡 Intermediate · Prerequisites: [Lab 09's RAG evaluation harness](../../labs/09-evaluating-agentic-rag/) (the structural precedent), the four [Path 03 multi-agent patterns](./README.md) (the systems being evaluated)

A multi-agent system produces something you've never had to evaluate before: a *trajectory*. A single-agent system gets a query and returns an answer — you score the answer. A multi-agent system gets a query, makes routing decisions, hands off between specialists, dispatches parallel work, possibly replans on failure, then synthesizes a final answer. You need to score the answer *and* the path that led to it, because the same answer can come from a correct trajectory (which generalizes) or from a lucky-but-broken one (which doesn't).

This page covers the evaluation framing. The next page, [trajectory-level metrics](./trajectory-level-metrics.md), covers the specific scoring functions and how to implement them. Together they prepare you for [Lab 16](../../labs/16-multi-agent-evaluation-from-scratch/), the from-scratch harness.

## The two tiers of multi-agent evaluation

Every multi-agent eval splits into two questions, neither of which subsumes the other:

**Did the system arrive at the right answer?** Outcome metrics. Citation preservation, groundedness, factual correctness, refusal quality. These are the same metrics single-agent systems use, applied to the final response.

**Did the system get there the right way?** Trajectory metrics. Did it route to the correct worker? Did it produce a valid plan? Did its plan steps actually execute? Did handoffs preserve the information they were supposed to carry? Did it replan unnecessarily?

The two tiers measure independent properties. A system can produce the right answer via a broken trajectory (luck or fallback) and a wrong answer via a perfect trajectory (the plan was correct but the world had moved). You need both tiers because each one catches failures the other misses.

For a single-agent system you can often get away with outcome metrics alone — there's only one path, and the answer reflects whether it worked. For multi-agent systems the path matters because the path is the system. Multi-agent failure modes (citation drift across handoffs, replan thrash, routing to the wrong specialist, plan-execution gap) live in the trajectory, not the answer.

## Why outcome metrics aren't enough

Here's a concrete scenario from Lab 11's generator-critic pattern. The system produces a 150-word summary with citations. The output looks fine: claims are mostly correct, citations are present, refusal language is absent. Outcome metrics give it 0.85 groundedness.

What outcome metrics miss: the critic was supposed to fire when the writer produced unsupported claims. In this run, the critic fired three times (consuming budget) on minor stylistic issues while missing one factually unsupported claim that slipped through. The trajectory shows the failure clearly — critic_3 returned `{status: "ok"}` on a draft containing a hallucinated date. Outcome metrics see "0.85 groundedness, ok." Trajectory metrics see "critic accuracy 67%, critic recall on factual errors 0%, budget spent on stylistic issues."

The trajectory tells you what to fix. The outcome tells you whether to ship.

## Why trajectory metrics aren't enough

A symmetric scenario from Lab 10's supervisor-researcher-writer. The supervisor routes correctly: researcher first, then writer. Trajectory metrics score it perfectly — routing accuracy 1.0, handoff success rate 1.0, no replans. But the researcher's final brief was paraphrased so heavily that it lost three of the four claims the user actually asked about. The writer faithfully composed prose around what it received — which was the wrong brief. The final answer is technically grounded in the (sparse) findings, but it doesn't answer the question.

The trajectory looks clean. The answer is wrong. Outcome metrics catch it; trajectory metrics don't.

## The replay model

Multi-agent evaluation works best as **replay**: you run the system once with a trace recorder, then evaluate the recorded trace. The trace contains every routing decision, every tool call, every handoff envelope, every state update. You score it offline without re-running the system.

Replay has four practical advantages over live evaluation:

- **Cost.** Evaluating a 50-trace test set against five different metric implementations costs nothing extra in LLM calls — you score the same recorded trace five ways.
- **Determinism.** The trace is fixed. Two different metric implementations applied to the same trace produce the same score every time. Live LLM calls don't.
- **Diagnostic depth.** When a metric fires, you have the full trajectory to inspect. With live evaluation you have to re-run with more logging.
- **Composability with CI.** Replay is offline — it runs on every PR without hitting external services. You can fail the build when a critical metric drops below threshold.

The trade-off: replay can't catch behavior that depends on live state (current web content, time-sensitive routing). For those you need live evaluation. Most regression-test workloads are well-served by replay; most freshness-and-currency checks need live evaluation. They complement.

## The trace fixture

Lab 16 builds on the same hand-curation discipline as Lab 09. 15-30 traces, hand-annotated, beats 1000 synthesized traces. The reasoning carries over: synthesis bias compounds in trajectories the same way it compounds in queries — your synthesized planner makes the planner mistakes you wrote into the synthesizer, not the ones your real planner makes.

A trace fixture for multi-agent evaluation contains:

- **The user task** — what the system was asked to do.
- **The full trajectory** — every node, every input, every output, in order. For Lab 10's pattern this is roughly: `[supervisor_decision, researcher_call, researcher_tool_calls, researcher_finding, supervisor_decision, writer_call, writer_output]`. For Lab 12's plan-and-execute it's the planner output plus a record of every dispatch and result.
- **Expected handoffs** — the golden routing trajectory. Used to score routing accuracy.
- **Expected citations** — the citation IDs that should appear in the final answer. Used to score citation preservation.
- **Category** — what this trace is supposed to test (happy_path, tool_failure, replan_needed, citation_drift, step_cap_hit, etc.).

The category field is what makes the trace set diagnostic. Aggregate metrics will lie — a 75% trajectory-precision score on a flat trace set tells you nothing about *what's failing*. The same 75% sliced by category might show 95% on happy_path and 30% on replan_needed, which tells you exactly what to fix.

## Per-agent vs end-to-end evaluation

The same trace can be evaluated two ways:

**Per-agent** evaluation scores each agent independently. The researcher gets a "researcher quality" score; the writer gets a "writer quality" score; the supervisor gets a routing-accuracy score. This is useful when an agent is shared across systems (the writer in Lab 10 and Lab 11 is the same writer) or when you're iterating on one agent in isolation.

**End-to-end** evaluation scores the system's final output and trajectory as a single unit. This is what users see; it's what matters for production.

Most teams default to end-to-end and add per-agent only when end-to-end metrics drop and they need to localize the failure. Per-agent is more work to set up (you need per-agent rubrics and per-agent expected outputs in the trace), but it's how you make targeted improvements.

A practical pattern: keep end-to-end metrics as the headline ("did the system do its job"), keep per-agent metrics as the diagnostic ("which agent is dragging the metric down"). Both come from the same recorded trace.

## What this misses

A few things multi-agent evaluation, as Lab 16 builds it, doesn't cover. These belong in Path 06 (Evaluation & Observability) or later modules:

**Long-running agents and online evaluation.** Lab 16 evaluates offline traces. Production systems also need live monitoring — drift detection, distribution shift across days, alerting on metric degradation. That's an observability problem, not an evaluation problem; it overlaps but the tools and methodology differ.

**Adversarial and red-team evaluation.** Lab 16 evaluates against intended tasks. Production systems also need to be probed with adversarial prompts (prompt injection, jailbreaks, social engineering). The Path 03 systems we've built aren't user-facing in a way that warrants this; production deployments are. Path 07 territory.

**Multi-turn (threaded) evaluation.** Lab 16 evaluates single-task trajectories. Production conversational systems also need to evaluate across conversation turns — does the system remember context, recover from errors, accumulate user state coherently? LangSmith's "multi-turn evals" and the emerging "thread-level evaluation" pattern address this. We'd address this in Path 03 v2 or Path 06.

**Agent-as-a-judge calibration.** When using LLM-as-judge for trajectory scoring, the judge itself needs evaluation against human ground truth. The Zheng et al. (2023) biases (position, verbosity, self-enhancement) apply. Lab 16 mentions the issue; calibration is a Path 06 topic.

**Tools that take this to production.** LangSmith, Phoenix, Galileo, DeepEval, and Vertex AI's evaluation service all ship trajectory-evaluation primitives. They're the natural next step after building the from-scratch harness. Path 06 covers them; Lab 16 stays framework-agnostic to make the mechanics visible.

## What the next page covers

[Trajectory-level metrics](./trajectory-level-metrics.md) gets specific about implementation: the seven metrics Lab 16 implements (five trajectory, two outcome), what each one measures, what each one misses, and the Python signatures you'll write in the lab. It's the implementation companion to this framing page.

## Related concepts

- [Lab 09's RAG evaluation harness](../../labs/09-evaluating-agentic-rag/) — the precedent. Same shape (hand-curated fixtures + rule-based tier + LLM-as-judge tier + category slicing) applied to single-agent RAG.
- [Supervisor-worker pattern](./supervisor-worker-pattern.md) — the pattern Lab 10 builds and Lab 16 evaluates traces from.
- [Planner-executor pattern](./planner-executor-pattern.md) — Lab 12's pattern; the plan-validity and plan-coverage metrics in Lab 16 are specific to this.
- [Handoffs and shared state](./handoffs-and-shared-state.md) — the structural concern that handoff-success-rate and citation-preservation metrics target.
- [Generator-critic pattern](./generator-critic-pattern.md) — Lab 11's pattern; the critic-accuracy metric (a per-agent metric) lives here.
- The four [Path 02 evaluation concept pages](../evaluation/) — single-agent RAG evaluation framing; many of the methodological concerns (eval-set construction, the rule-based vs LLM-as-judge trade-off, the discipline of slicing by category) carry over.

## References

- McKinsey QuantumBlack, *Evaluations for the Agentic World* (Jan 2026) — handoffs-per-task, duplicate-work-rate, deadlock detection, invariant violation rate as named multi-agent metrics. [medium.com/quantumblack](https://medium.com/quantumblack/evaluations-for-the-agentic-world-c3c150f0dd5a).
- Google Cloud Vertex AI, *Agent evaluation metrics* — the `trajectory_exact_match` / `trajectory_precision` / `trajectory_recall` formalization. [cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai).
- LangChain, *Multi-turn evaluations in LangSmith* (Oct 2025) — the thread-level evaluation pattern (semantic intent, semantic outcome, trajectory). [blog.langchain.com](https://blog.langchain.com/insights-agent-multiturn-evals-langsmith/).
- LangChain `agentevals` repository — `create_trajectory_llm_as_judge` reference implementation; the message-list format that LangGraph traces naturally produce. [github.com/langchain-ai/agentevals](https://github.com/langchain-ai/agentevals).
- Zheng et al. (2023), *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS — the three documented LLM-as-judge biases (position, verbosity, self-enhancement). [arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685).
- El Filali & Bedar (2026), *Towards More Standardized AI Evaluation: From Models to Agents* — argues that trajectory evaluation is the agentic shift from "how good is the model" to "can we trust the system to behave as intended under change." [arXiv:2602.18029](https://arxiv.org/abs/2602.18029).
