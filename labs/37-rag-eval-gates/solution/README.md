# Lab 37 · Reference solution

The complete implementation of [Lab 37: Evaluation gates for RAG](../README.md).

## What this is

Two evaluation artifacts plus the CI wiring:

- **`llm_judge` + `parse_judge`** — a pointwise judge (rubric → `{correct, faithful, score, reason}`) with defensive JSON parsing (handles clean, fenced, embedded, and malformed output).
- **Fixture validation** — adversarial cases where token-presence scoring fails: a correct paraphrase (token says wrong, judge says right), a verbose fabrication (token says right, judge says unfaithful), an abstention (token says wrong, judge says right).
- **`answer_correct_judge`** — same signature as Lab 34's `answer_correct`, so it drops into `run_harness` to upgrade the head-to-head from token-presence to judged scoring.
- **`gate(metrics, thresholds)`** — pure, testable threshold logic.
- **[`eval_gate.py`](../eval_gate.py)** — the CI entrypoint: trains the router, scores routing accuracy on the eval set, applies thresholds, exits non-zero on regression. `--self-test` exercises `gate()` without deps or network.
- **[`rag-eval-gate.yml`](../../../.github/workflows/rag-eval-gate.yml)** — runs the gate on PRs that touch the router, corpus, or eval set.

## Implementation choices

1. **Routing accuracy is the only blocking check.** It's deterministic (classifier only) and free — a stable gate. Judged faithfulness is noisy and costs calls, so it belongs in a nightly informational job, not the blocking path.
2. **Stronger, separate judge model.** Reduces self-preference bias; the judge should not share the generator's blind spots.
3. **Pointwise + rubric.** Cuts the position bias of pairwise judging and constrains verbosity bias.
4. **Defensive parsing always.** Model JSON is untrusted input; `parse_judge` never raises on bad output.
5. **`eval_gate.py` separates pure logic from I/O.** `gate()` and `--self-test` run anywhere; the heavy embedder/sklearn imports live inside `routing_accuracy()` so the smoke test needs neither.

## The design rule

Block CI on cheap deterministic signals (routing accuracy); monitor expensive noisy ones (judged faithfulness) out of band. An LLM-judge blocking gate is flaky and costly; a routing-accuracy gate is neither.

## What's out of scope

- The human-label validation set the judge should be calibrated against (build one before trusting judged metrics).
- Pairwise judging and rubric ensembles (lower variance, higher cost).
- Threshold tuning (the values are illustrative; set yours from a baseline + tolerance band).

## Running

```bash
cd labs/37-rag-eval-gates
python eval_gate.py --self-test     # gate logic, no deps
python eval_gate.py --route-min 0.85  # full routing gate (needs sklearn + sentence-transformers)
jupyter notebook solution/lab.ipynb   # the judge
```

## Next

Add the nightly judged-faithfulness job; calibrate the judge against human labels; set thresholds from a baseline run.
