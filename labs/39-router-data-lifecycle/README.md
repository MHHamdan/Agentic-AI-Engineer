# Lab 39: The router's query-data lifecycle

> 🔴 Advanced · ⏱ ~90–110 min · 📚 Builds on Lab 36

## 🎯 Goal

[Lab 36](../36-training-the-router/) trained the router on clean prototype queries. Real users type messy ones — lowercase, typos, fragments, `$$`, `??`. This lab closes the loop: capture messy queries, dedup them, triage by confidence to a human-review queue, retrain, and **measure** whether the new round actually helped. The discipline is the point — a second training round is an experiment you verify, not a guaranteed win.

By the end you should be able to:

- Detect distribution shift with a confidence drop on live-style queries.
- Dedup a query stream with exact and near-duplicate (embedding) passes.
- Triage by confidence so human review goes to the highest-value labels (active learning).
- Measure the effect of a retraining round on a held-out slice and decide whether to promote.

## 📋 Prerequisites

**Complete first:**

- 🧪 [Lab 36: Training the router](../36-training-the-router/) — this lab grows the trainset Lab 36 built and reuses its classifier.
- 🧪 [Lab 38: Calibrating the eval gate](../38-calibrating-the-eval-gate/) — after retraining you re-derive its baseline.

**Assumed background:** logistic regression and `predict_proba`, train/test splitting and stratification, active learning (uncertainty sampling), and the data-leakage risks of evaluating on data you trained on.

**Setup:** Python 3.11+ with the repo environment, `scikit-learn`, `sentence-transformers`, `numpy`.

## 🛠 Tools and versions

| Library | Version | Notes |
|---|---|---|
| `scikit-learn` | `>=1.4` | Classifier + metrics |
| `sentence-transformers` | `>=5.0,<6.0` | Query embeddings (features + near-dup) |
| `numpy` | `>=1.26` | Arrays |

## What you'll build / what ships

- `captured_queries.jsonl` — 36 simulated messy log queries with gold labels (the labels a human reviewer would assign).
- A notebook that: shows the confidence drop on messy vs clean; dedups (string + embedding near-dup); triages by confidence into a review queue; merges reviewed labels; retrains; and measures the result on a held-out messy slice.

## How item 4 works here

"Prototypes underrepresent messy phrasing" is not assumed — it's shown: the prototypes-only router's mean confidence collapses on captured messy queries (it sits near its decision boundary because it never saw those shapes). That drop is the trigger for a new round. The round itself is then **measured** on a held-out messy slice before the new model is promoted.

## Steps

1. **Setup** (0).
2. **Prototypes + captured queries** (1).
3. **Distribution shift** (2): the confidence drop.
4. **Dedup** (3): exact then near-duplicate.
5. **Triage** (4): confidence → review queue.
6. **Merge + retrain + measure** (5).
7. **Read it honestly** (6): promote only on a measured lift.

## Design choices and tradeoffs

- **Confidence drop as the shift detector.** It needs no labels — you can run it on live traffic continuously. A sustained sag in mean confidence is your signal that the query distribution has moved and a new round is due.
- **Uncertainty triage for review.** Labeling is the expensive step. Sending the low-confidence tail to human review (rather than a random sample) puts annotator effort where the model learns most per label.
- **Measure before promoting.** Adding data is not automatically an improvement — it can add noise, or the new slice can be too small to resolve an effect. Hold out a messy test set, measure A vs B, and promote only on a real lift. With semantic embeddings the in-distribution augmentation effect is usually positive, but you verify it rather than assume it.

## Common gotchas

- **Leakage in the loop.** If auto-accepted labels (the router's own predictions) dominate the new training data, you train the model on its own beliefs and reinforce its errors. Spot-check auto-accepted labels and weight human-reviewed ones.
- **Tiny test slices lie.** A 15–20 query held-out set can swing several points on noise. Treat the sign of a small delta as indicative; collect more before trusting it, and look per-route, not just in aggregate.
- **Stale gate after retraining.** The model's routing accuracy changes, so the [Lab 38](../38-calibrating-the-eval-gate/) baseline and thresholds must be re-derived — otherwise CI compares the new model against the old reference.
- **Label drift.** Your route taxonomy may need new categories as real queries reveal intents the prototypes never anticipated. Revisit the label set, not just the examples.

## 🧮 Going deeper

- 📖 [SOTA RAG patterns](../../concepts/rag/sota-rag-patterns.md) — the router this feeds.
- 🧪 [Lab 36](../36-training-the-router/) — the classifier and confidence gate this round retrains.

## What comes next

This closes Path 02's RAG arc: patterns (31–33) → comparison (34) → routing (35) → trained, hardened router (36) → CI gate (37) → calibrated gate (38) → fresh router data (39). From here the work is operational and domain-specific: wire real log capture, schedule the confidence-drop check on live traffic, and run the capture → review → retrain → re-baseline loop on a cadence.
