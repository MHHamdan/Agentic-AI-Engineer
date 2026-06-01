# Lab 37: Evaluation gates for RAG

> 🔴 Advanced · ⏱ ~90–120 min · 📚 Builds on Labs 34 and 36

## 🎯 Goal

Build the two pieces of evaluation infrastructure a RAG system needs in CI: an **LLM-as-judge** scorer that drops into [Lab 34](../34-rag-pattern-head-to-head/)'s harness in place of brittle token-presence scoring, and an **eval gate** that wraps the [Lab 36](../36-training-the-router/) router so routing regressions fail the build. The lesson is the split between the two: block CI on a cheap deterministic signal, monitor the expensive noisy one out of band.

By the end you should be able to:

- Write a pointwise LLM judge with a rubric and structured output, and parse it defensively.
- Show where token-presence scoring fails (paraphrase, verbose fabrication, abstention) and where the judge fixes it.
- Name and mitigate the judge's own biases (position, verbosity, self-preference, nondeterminism).
- Build a CI gate that blocks on deterministic routing accuracy and leaves judged faithfulness to a nightly job.

## 📋 Prerequisites

**Read first:**

- 📖 [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — this lab makes its `eval_gate` concept concrete.

**Complete first:**

- 🧪 [Lab 34: Head-to-head evaluation](../34-rag-pattern-head-to-head/) — the judge is the drop-in upgrade to its `answer_correct` scorer.
- 🧪 [Lab 36: Training the router](../36-training-the-router/) — the router this gate wraps; the gate reads its trainset.

**Setup:** Python 3.11+ with the repo environment, `scikit-learn`, `sentence-transformers`, `numpy`, plus `PyYAML` if you want to lint the workflow locally. Your LLM provider key (a stronger model for the judge than for generation, if you can afford it).

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `openai` *or* `anthropic` | from prior labs | Judge + generation |
| `scikit-learn` / `sentence-transformers` | as Lab 36 | The gate trains + scores the router |
| GitHub Actions | — | `.github/workflows/rag-eval-gate.yml` runs the gate on PRs |

## What you'll build

`parse_judge` (defensive JSON parsing) + `llm_judge(query, candidate, reference)` (pointwise rubric → `{correct, faithful, score, reason}`); a validation pass on adversarial fixtures; `answer_correct_judge` — the same signature as Lab 34's `answer_correct`, so it swaps straight into `run_harness`; the pure `gate(metrics, thresholds)` function; and the runnable [`eval_gate.py`](./eval_gate.py) CI entrypoint plus its [workflow](../../.github/workflows/rag-eval-gate.yml).

## How item 4 ("swap Lab 34's scoring") works here

Lab 34 scored answers with `answer_correct` (all expected tokens present). That's deterministic and free but brittle: it marks a correct paraphrase wrong and a verbose fabrication right. This lab's `answer_correct_judge` has the identical signature — `(answer, item) -> bool` — so upgrading Lab 34's head-to-head is a one-line swap inside `run_harness`. The lab demonstrates the difference on the eval set; scoring all four patterns is then just running Lab 34 with the new scorer.

## Steps

1. **Setup** (0): separate judge and generator models.
2. **The judge** (1): rubric + structured output + defensive parse.
3. **Validate on fixtures** (2): the cases token-presence gets wrong.
4. **Drop-in scorer for Lab 34** (3): same signature as `answer_correct`.
5. **Judge caveats** (4): bias and noise before trust.
6. **The gate** (5): pure threshold logic.
7. **The runnable gate** (6): `eval_gate.py`.
8. **Block vs monitor** (7): the design split.

## Design choices and tradeoffs

- **Routing accuracy is the blocking gate; judged faithfulness is not.** Routing accuracy needs only the trained classifier — deterministic, fast, free — so it makes a stable gate. An LLM judge is noisy (run-to-run variance even at temperature 0) and costs a call per item; as a *blocking* gate it makes the build flaky and expensive. Run it nightly, post a trend, alert on regression.
- **Pointwise judging with an explicit rubric.** Reduces the position bias of pairwise judging; the rubric constrains the verbosity bias. Pairwise and rubric ensembles cut variance further at higher cost.
- **A different (stronger) judge model than the generator.** A judge that shares the generator's model family tends to favor its own outputs (self-preference). Separate them.

## Common gotchas

- **The judge is a measurement instrument with error.** Don't report judge-vs-pattern scores until you've reported judge-vs-human agreement on a small labeled set. An uncalibrated judge launders its own bias into your metric.
- **LLM nondeterminism breaks exact-match gates.** If you ever do gate on a judged metric, use a tolerance band, not equality, and pin the judge model version.
- **Models rarely emit clean JSON.** `parse_judge` strips fences, falls back to a regex for the first `{...}`, and defaults safely. Never `json.loads` a raw model response without a fallback.
- **CI cost creep.** An LLM-in-CI gate that runs on every push quietly burns budget. Scope the workflow to the paths that matter (the gate's `on.pull_request.paths`) and keep the blocking job LLM-free.

## 🧮 Going deeper

- 📖 [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md) — the six layers this gate enforces a slice of.
- 📄 Zheng et al. 2023, *Judging LLM-as-a-judge* ([arXiv:2306.05685](https://arxiv.org/abs/2306.05685)) — the judge biases and the MT-Bench validation method.

## What comes next

This closes the production-hardening arc for Path 02's RAG track: Labs 31–33 built the patterns, 34 compared them, 35 routed among them, 36 trained and hardened the router, and 37 gates the whole thing in CI. From here, the natural moves are domain-specific: build the human-label validation set for your judge, set gate thresholds from a baseline run, and add the nightly judged-faithfulness job alongside the blocking routing gate.
