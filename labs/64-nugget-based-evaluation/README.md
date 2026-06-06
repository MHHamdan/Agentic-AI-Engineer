# Lab 64: Nugget-based coverage and citation for long-form RAG

> 🔴 Advanced · ⏱ ~80–100 min · 📚 Builds on Labs 61–62 · Module 30

## 🎯 Goal

By 2026 the standard way to evaluate long-form and report-generation RAG is **nugget-based**, as in the TREC RAG track's AutoNuggetizer ([Pradeep et al., 2024](https://arxiv.org/abs/2411.09607)) and Auto-ARGUE ([2025](https://arxiv.org/abs/2509.26184)): decompose an information need into atomic nuggets a good answer should cover, label how well the answer supports each, and score two orthogonal axes — coverage (recall over nuggets) and citation (sentence-support rate). The decisive TREC 2025 finding: citation accuracy is largely solved when systems add checks, but nugget coverage is still a work in progress — and they are different bugs.

By the end you should be able to:

- Decompose an information need into vital/okay nuggets and label support (Full/Partial/No).
- Score coverage (recall-like) and sentence-support rate (precision-like) as separate axes.
- Attribute a weak report to coverage (a retrieval problem) or citation (a generation problem).

## 📋 Prerequisites

- 🧪 [Lab 61](../61-grading-multimodal-rag/) (grading retrieval, grounding, and reading separately) and [Lab 62](../62-ocr-reading-quality/).
- 📖 [Nugget-based evaluation](../../concepts/rag/nugget-evaluation.md) — the methodology and the 2026 context.
- 📐 [math-foundations/19](../../math-foundations/19-nugget-coverage-metrics.md) — coverage as weighted recall, citation as precision, and why you report both.

**Setup:** Python 3.11+, standard library. The support labeler and citation judge are deterministic stand-ins; `assign_with_judge` is the guarded seam for an AutoNuggetizer-style LLM assignment.

## 🛠 Module

| Component | Notes |
|---|---|
| `nugget_eval.py` | `coverage`, `sentence_support_rate`, `support_label`, `evaluate`, `assign_with_judge` (`--self-test`) |

## What the numbers say

| Answer | coverage (vital) | sentence-support rate |
|---|---|---|
| Cites well, misses a nugget | 0.50 | 1.00 |
| Covers all, cites wrong doc | 1.00 | 0.00 |
| Balanced | 1.00 | 1.00 |

The first two sit at opposite corners — one quality score cannot tell them apart.

## Design choices and tradeoffs

- **Two orthogonal axes.** Coverage is recall over the nuggets that should appear; sentence-support rate is precision over the answer's citations. A report can be perfect on one and broken on the other, so report both.
- **Different bugs, different fixes.** Low coverage is usually a retrieval problem (you did not retrieve the diverse evidence the nuggets need); low citation is usually a generation problem (you cited the wrong thing). This mirrors the TREC 2025 result.
- **Vital/okay weighting + partial credit.** Vital nuggets must be covered; okay nuggets are bonus; Full/Partial/No support gives partial credit, following the TREC nugget tradition.

## Common gotchas

- **Averaging coverage and citation into one number** re-hides the very thing the split reveals.
- **Nuggetization quality bounds the metric** — bad nuggets make coverage meaningless; in TREC the auto-generated nuggets are calibrated against human-edited ones.
- **Citation precision without coverage is easy to game** — cite only what you are sure of and say little. Coverage is the check against that.

## 🧮 Going deeper

- 📐 [math-foundations/19](../../math-foundations/19-nugget-coverage-metrics.md) — the recall/precision view and a coverage–citation F-style combination.
- 📖 [Nugget-based evaluation](../../concepts/rag/nugget-evaluation.md) — AutoNuggetizer, Auto-ARGUE, and TREC RAGTIME 2026 auto-nuggetization.

## References

- Pradeep, Thakur, Upadhyay, Campos, Craswell, Lin (2024). *Initial Nugget Evaluation Results for the TREC 2024 RAG Track with the AutoNuggetizer Framework.* [arXiv:2411.09607](https://arxiv.org/abs/2411.09607).
- *Auto-ARGUE: LLM-Based Report Generation Evaluation* (2025). [arXiv:2509.26184](https://arxiv.org/abs/2509.26184).
- [TREC RAG](https://trec-rag.github.io/) and [TREC RAGTIME](https://trec-ragtime.github.io/) track sites (2026).

## What comes next

Wire `assign_with_judge` to a real LLM judge and calibrate it against a small set of human-labeled nuggets, then track coverage and citation separately across retrieval changes — the diverse-retrieval problem coverage exposes is where most of the headroom is in 2026.
