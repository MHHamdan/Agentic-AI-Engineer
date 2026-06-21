# Monitoring, drift, and retraining

> Concept note. ~8 min. Closes the [ML lifecycle](./ml-lifecycle.md) loop.

A model is trained on a snapshot of the world and then deployed into a world that keeps moving. **Monitoring** is how you notice the gap opening, and **drift** is the name for the gap. Without it, a model degrades silently — no error, no alert, just slowly worse decisions.

## Two kinds of drift

- **Data drift (covariate shift).** The inputs change distribution: a new customer segment, a new product, a holiday season. The relationship the model learned may still hold, but it is now operating on data unlike its training set.
- **Concept drift.** The relationship itself changes: the same inputs now map to a different correct output. Fraud patterns adapt, user tastes shift, a competitor changes the market. This is the harder kind, because the model can be confidently wrong on data that looks familiar.

A third issue is **training/serving skew**, which looks like drift in the metrics but is a code bug, not a world change — the features differ between paths from day one (see [feature stores](./feature-stores.md)). Rule that out before assuming the world moved.

## What to watch

You rarely have immediate labels in production, so monitor in layers, from cheapest to most informative:

- **Inputs** — feature distributions vs. the training set; flags data drift without needing labels.
- **Outputs** — the prediction distribution; a sudden shift in the score histogram is an early warning.
- **Operational** — latency, error rates, null/default rates in features (a spike often means an upstream pipeline broke).
- **Outcomes** — the real metric, once labels arrive (delayed, but the ground truth).

## When to retrain

Retraining is not a fixed schedule so much as a triggered response. Common triggers: an input-drift metric crosses a threshold, the outcome metric drops past a floor, or enough new labeled data has accumulated to be worth it. The decision balances cost (retraining and re-validation are not free) against the risk of a stale model. Whatever the trigger, retraining is itself a lifecycle pass — re-evaluate on fresh held-out data and on the slices that matter before promoting the new model, or you risk shipping a regression to fix a drift.

## What to remember

- Data drift changes the inputs; concept drift changes the input-to-output relationship and is harder to catch.
- Monitor inputs and outputs first (no labels needed), operational health next, real outcomes last.
- Retrain on triggers, not faith — and re-validate the retrained model before promoting it.
