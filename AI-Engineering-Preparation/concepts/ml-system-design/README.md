# ML system design

The systems view that interview questions and production both demand: how data becomes features, models, and a served prediction, with the stores, serving paths, and monitoring that keep it reliable.

> Batch 02: notes delivered.

## Notes

1. [The ML lifecycle](./ml-lifecycle.md) — data → features → training → serving → monitoring, and the offline/online split where skew hides.
2. [Feature stores and training/serving skew](./feature-stores.md) — one feature definition for both paths; point-in-time correctness.
3. [Monitoring, drift, and retraining](./monitoring-and-drift.md) — data vs. concept drift, what to watch, when to retrain.

## Key references

- Hidden Technical Debt in Machine Learning Systems — NeurIPS 2015.
- Feature-store and serving patterns — see references.

See the full list in [`../../references/references.md`](../../references/references.md). All explanations are original; sources are cited, not reproduced ([`STYLE.md`](../../STYLE.md)).
