# Lab 39 · Reference solution

The complete implementation of [Lab 39: The router's query-data lifecycle](../README.md).

## What this is

The capture → dedup → triage → retrain → measure loop for the Lab 36 router:

- **Distribution-shift detector** — mean `predict_proba` confidence on captured messy queries vs clean eval queries. The drop is label-free evidence that the prototypes never saw these shapes.
- **Dedup** — exact (normalized string) then near-duplicate (embedding cosine > 0.95).
- **Confidence triage** — low-confidence queries go to a human-review queue (uncertainty sampling); high-confidence ones are auto-accepted with the router's label.
- **Merge + retrain + measure** — augment the trainset with reviewed queries, hold out a messy test slice, and compare prototypes-only (A) vs augmented (B).

## Implementation choices

1. **Confidence drop, not accuracy, as the trigger.** It needs no labels, so it runs on live traffic — a sustained sag signals a new round is due.
2. **Uncertainty triage.** Annotator time is the scarce resource; reviewing the low-confidence tail maximizes information per label.
3. **Measure A vs B on a held-out messy slice.** The lab does not assert that augmentation helps — it measures it, and tells you to promote the new model only on a real lift. With semantic embeddings the in-distribution effect is usually positive; the discipline is to verify.
4. **Stratified split** so the messy test set covers all routes.
5. **Re-baseline afterward.** Retraining changes routing accuracy, so the Lab 38 thresholds must be re-derived — the lab says so explicitly.

## A note on the verification

The repo's offline check uses a TF-IDF stand-in for the embedder (no network). TF-IDF keys on content words that survive messy phrasing, so it understates the shift and the augmentation effect can wobble on the tiny test slice. With real sentence-transformer embeddings the confidence drop is sharp and augmentation typically helps — but the lab's stance is to **measure**, which holds regardless of representation.

## What's out of scope

- Real, unlabeled, high-volume logs (this is 36 hand-authored messy queries with gold labels).
- A production review tool and annotator workflow.
- Auto-accept spot-checking (mentioned; not implemented) — important to avoid training the model on its own errors.

## Running

```bash
cd labs/39-router-data-lifecycle
jupyter notebook solution/lab.ipynb
```

Reads Lab 36's `router_trainset.jsonl` and Lab 34's eval set by relative path.

## Next

Re-derive the [Lab 38](../../38-calibrating-the-eval-gate/) baseline after promoting a retrained router; schedule the confidence-drop check on live traffic.
