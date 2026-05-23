# Evaluation

Frameworks, datasets, and scorers for evaluating agentic AI systems. This folder is where the *how do I measure my agent?* question gets answered.

The conceptual side (what faithfulness means, what LLM-as-judge does well and badly) lives in [`concepts/evaluation/`](../concepts/evaluation/). The mathematical treatment of metrics (precision, recall, calibration) lives in [`math-foundations/11-evaluation-metrics.md`](../math-foundations/). This folder is the practical side — actual tooling and workflows.

## Subfolders

| Folder | Covers |
|---|---|
| `frameworks/` | LangSmith, RAGAS, DeepEval, TruLens — versioned snapshots, when to use each |
| `datasets/` | How to build, version, and maintain evaluation datasets |
| `scorers/` | Faithfulness, answer relevance, context relevance, LLM-as-judge, pairwise preference |

## Why this is its own folder

Three reasons evaluation is separated from the rest:

1. **Eval is a discipline.** It deserves room to breathe — datasets, scorers, frameworks, and workflows are distinct topics that interact.
2. **It's how you ship.** Production agents that aren't evaluated aren't actually shipped, they're just deployed.
3. **It's where engineering rigor lives.** Most of what separates a hobby agent from a production one is whether you can measure it.

## Typical workflow

A reasonable end-to-end evaluation workflow:

1. **Instrument** the agent with tracing ([`tools/langsmith/`](../tools/langsmith/) or OpenTelemetry).
2. **Build a dataset** — start with 20 examples, grow to 200 as you find failure modes.
3. **Pick scorers** — reference-based when you have ground truth, reference-free (LLM-as-judge) when you don't.
4. **Calibrate the judge** — sanity-check against human labels on a small holdout.
5. **Run experiments** comparing prompt / model / tool changes.
6. **Track regressions** in CI on every PR that touches the agent.

The labs in the **Evaluation & Observability** learning path walk through each step.

## Contributing

Eval content is in higher demand than supply across the field. Contributions that codify production eval patterns — especially ones that catch failure modes most blogs ignore — are highly welcome.

> 🟡 Eval frameworks are classified **slow-moving**. The underlying ideas (precision, recall, faithfulness) are stable; the specific frameworks evolve quarterly.
