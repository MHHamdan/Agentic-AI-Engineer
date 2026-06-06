# Batch 86 — navigation edits

The overlay ships the new content files. Apply these small edits to the existing index files in your repo (they carry the prior batches' content, which this batch leaves untouched).

## `glossary/terms.md` — add (alphabetical)

```
**AutoNuggetizer.** An LLM-based framework (Pradeep et al., 2024) that automatically creates nuggets from an information need and assigns Full/Partial/No support labels to a system answer, refactoring the TREC QA nugget methodology for RAG. → `labs/64-nugget-based-evaluation/`.

**Nugget.** An atomic fact a good answer to an information need should contain; marked vital (must appear) or okay (bonus). Coverage is computed over the nugget set. → `concepts/rag/nugget-evaluation.md`.

**Nugget coverage.** Weighted recall over the nuggets a report should support (Full/Partial/No → partial credit; vital/okay weights). Recall-like and not gameable by writing more. → `labs/64-nugget-based-evaluation/`.

**Sentence-support rate (SSR).** Citation precision: the fraction of a report's sentences whose cited evidence actually supports them. Precision-like and gameable by writing less, so it is reported alongside coverage. → `labs/64-nugget-based-evaluation/`.
```

## `concepts/rag/README.md` — add a row (after `ocr-on-real-images.md`)

```
| 📖 [nugget-evaluation.md](./nugget-evaluation.md) | ~11 min | Nugget-based evaluation for long-form RAG (AutoNuggetizer / Auto-ARGUE): coverage (recall over nuggets) vs citation (sentence-support rate), why they're orthogonal, and the 2026 "citation solved, coverage hard" finding (Lab 64). |
```

## `math-foundations/README.md` — add a row (after row 18)

```
| 19 | [Nugget coverage metrics](./19-nugget-coverage-metrics.md) | coverage as weighted recall, sentence-support rate as precision, harmonic (F-beta) combination, nuggetizer calibration |
```

## `README.md` (landing) — update counts

```
labs: 63 → 64    (Hands-on labs)
math: 18 → 19    (Math foundations)
```

## `learning-paths/02-agentic-rag/README.md` — add after Module 29's through-line

```
## Module 30: Nugget-based evaluation for long-form RAG

Modules 28-29 graded short and multimodal answers. This module covers the 2026 standard for long-form and report-generation RAG, where the query is a paragraph-length information need and "the answer" is a multi-sentence cited report: nugget-based evaluation (AutoNuggetizer / Auto-ARGUE), the method behind the current TREC RAG and RAGTIME tracks.

59. 🧪 **[Lab 64: Nugget-based coverage and citation](../../labs/64-nugget-based-evaluation/)** *(~80-100 min)* - decompose an information need into vital/okay nuggets, label Full/Partial/No support, and score coverage (recall over nuggets) and citation (sentence-support rate) as two orthogonal axes. Three reports land at different corners: cites-well/misses-nuggets, covers-all/cites-wrong, and balanced - so one quality score cannot tell them apart. Concept: [nugget-evaluation.md](../../concepts/rag/nugget-evaluation.md); math: [19](../../math-foundations/19-nugget-coverage-metrics.md).

> 💡 Module 30's through-line: **coverage and citation are different axes with different fixes.** Coverage is recall over the facts a report should contain (mostly a retrieval problem - retrieve diverse evidence); citation is precision over the sentences it wrote (mostly a generation problem - ground each sentence in what it cites). The 2026 TREC result is that citation is largely solved while coverage lags, so report both, summarize with a harmonic combination, and attribute the gap rather than averaging it away.
```

## `CHANGELOG.md` — add at the top of the Unreleased/Added list

```
- **🧪 Nugget-based evaluation for long-form RAG (Batch 86).** Module 30 adds the 2026 standard for evaluating long-form and report-generation RAG: nugget-based coverage and citation, after the TREC RAG track's AutoNuggetizer ([arXiv:2411.09607](https://arxiv.org/abs/2411.09607)) and Auto-ARGUE ([arXiv:2509.26184](https://arxiv.org/abs/2509.26184)). A new lab, a concept note with a pipeline diagram, and a new math-foundations page. The through-line: coverage (recall over the nuggets a report should support) and citation (sentence-support rate) are orthogonal axes with different fixes - the TREC 2025 finding is that citation is largely solved while coverage, a retrieval-diversity problem, still lags.

  - **🧪 [Lab 64: Nugget-based coverage and citation](labs/64-nugget-based-evaluation/)** decomposes an information need into vital/okay nuggets, labels Full/Partial/No support for partial credit, and scores coverage and sentence-support rate separately. Three reports sit at different corners of the coverage×citation grid (cites-well/misses-nuggets at 0.50/1.00, covers-all/cites-wrong at 1.00/0.00, balanced at 1.00/1.00), showing a single quality score cannot tell them apart. The support and citation judges are deterministic stand-ins with a guarded `assign_with_judge` seam for an AutoNuggetizer-style LLM assignment.
  - **📐** New [math-foundations/19: Nugget coverage metrics](math-foundations/19-nugget-coverage-metrics.md) - coverage as weighted recall, sentence-support rate as precision, why a harmonic (F-beta) combination is the right summary (it drives a zero-citation report to 0 where a plain mean reads 0.5), and why coverage is only as trustworthy as the nuggetizer's calibration.
  - **📖** New concept note [nugget-evaluation.md](concepts/rag/nugget-evaluation.md) with a pipeline diagram (need → nuggetize → assign support → score coverage + citation), covering the AutoNuggetizer/Auto-ARGUE method, why the axes are orthogonal, and the TREC 2025/2026 results (citation solved, coverage hard; diverse retrieval and agentic sub-question decomposition as the response).
  - The glossary gains 4 terms (AutoNuggetizer, nugget, nugget coverage, sentence-support rate); Path 02 gains Module 30; the landing page lab count is updated to 64 and math to 19.

  Verified deterministically: `nugget_eval.py --self-test` (cites-well/misses-nuggets → coverage 0.50 / SSR 1.00 with the missing vital nugget identified; covers-all/cites-wrong → 1.00 / 0.00 with the unsupported sentences identified; balanced → 1.00 / 1.00; the two axes are orthogonal and support labels span Full/Partial/No). The solution notebook executes; new-file links resolve. Citations are real and current (AutoNuggetizer, Auto-ARGUE, the TREC RAG and RAGTIME 2025/2026 track overviews). Staged behind a live dependency and documented rather than run here: the AutoNuggetizer-style LLM judge for nugget creation and Full/Partial/No assignment, and the sentence-level citation judge - both are guarded seams over deterministic stand-ins, and the metric design (weighted recall, sentence-support precision, reported separately with attribution) is unchanged with a real judge. Lab data is fictional and grounded in the running corpus; the nugget-evaluation methodology and the "coverage is the hard axis" finding are from the TREC RAG/RAGTIME tracks and are fast-moving - verify the current track guidelines before relying on specifics.
```
