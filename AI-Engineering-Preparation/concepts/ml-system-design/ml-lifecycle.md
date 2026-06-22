# The ML lifecycle

> Concept note. ~9 min. Diagram: [`diagrams/ml-lifecycle.md`](../../diagrams/ml-lifecycle.md).

A model is a small part of a machine-learning system. The interview question "design X" and the production reality are the same question: how does raw data become a feature, a trained model, and a served prediction that stays correct over time? The lifecycle is the loop that answers it.

## The stages

1. **Problem framing.** Turn a vague goal ("reduce churn") into a measurable learning problem: the target, the unit of prediction, the label, and the metric that defines success. Most failures are decided here, before any model exists.
2. **Data.** Collect, clean, and label. Decide what is a training example, how labels are obtained (explicit, implicit, human), and how fresh the data must be.
3. **Features.** Transform raw data into model inputs — aggregations, encodings, embeddings. This is where most predictive signal and most subtle bugs live (see [feature stores](./feature-stores.md)).
4. **Training.** Fit the model offline on historical data, tune, and select. The output is an artifact plus a record of exactly how it was produced.
5. **Evaluation.** Measure on held-out data against the framing metric, and against slices that matter (per segment, not just the average), before anything ships.
6. **Serving.** Expose the model for predictions — **batch** (precompute and store) or **online** (compute per request under a latency budget). The serving path has different constraints from training.
7. **Monitoring.** Watch inputs and outputs in production and decide when to retrain (see [monitoring and drift](./monitoring-and-drift.md)).

```text
data → features → training → evaluation → serving → monitoring
                     ↑__________________________________|   (retrain when signals say so)
```

## The split that causes most bugs

Training is **offline**: batch access to history, latency measured in hours, the full label available. Serving is often **online**: one example at a time, latency in milliseconds, and only the data available *at request time*. A feature trivial to compute over a historical table — "average order value over the last 30 days" — must be computed identically, from the same definition, in the live path. When the two diverge, you get **training/serving skew**: the model was trained on features it never actually sees in production. Keeping the two consistent is the job of a [feature store](./feature-stores.md), and the reason it exists.

## Designing under constraints

A system-design answer is mostly about the non-model parts: where labels come from, how features stay consistent, batch vs. online serving, how to handle scale and latency, and how to detect and recover from drift. State the metric, walk the data path, name the skew and drift risks, and say how you would monitor — that is the shape of a strong design.

## What to remember

- The model is one stage; framing, data, features, serving, and monitoring decide whether it works.
- Training is offline and serving is often online, with different data and latency — the gap between them is where skew hides.
- Design the loop, not just the model: define the metric, keep features consistent, and plan for drift.

## References

- Sculley, D., et al. (2015). *Hidden Technical Debt in Machine Learning Systems.* NeurIPS. See [`../../references/references.md`](../../references/references.md).
