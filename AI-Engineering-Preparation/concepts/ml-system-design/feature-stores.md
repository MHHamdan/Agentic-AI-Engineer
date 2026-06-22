# Feature stores and training/serving skew

> Concept note. ~8 min. Builds on [the ML lifecycle](./ml-lifecycle.md).

A **feature store** is the system that computes, stores, and serves features so the same feature means the same thing in training and in production. It exists to kill one specific, expensive bug: **training/serving skew**.

## The bug it prevents

Say a feature is "customer's average order value over the last 30 days." In training you compute it with a query over a historical table. In production you must compute it again, live, for one customer, at request time. If the two implementations differ — a different window, a different default for missing values, a different rounding — the model is served inputs that disagree with what it learned on, and accuracy quietly drops. Nothing errors; the numbers just get worse. A feature store fixes this by holding a single feature definition and serving it to both paths.

## Two access patterns

A feature store usually has two halves with different requirements:

- **Offline store** — large historical tables for training and batch scoring; optimized for throughput over a lot of data.
- **Online store** — a low-latency key-value lookup for serving; optimized to return a feature vector for one entity in milliseconds.

The same feature is materialized into both, from one definition, so the training query and the live lookup cannot drift apart.

## Point-in-time correctness

The subtler failure is **leakage through time**. When you build a training row labeled at time *t*, every feature in it must be computed using only data available before *t*. If your join accidentally pulls in a value that was recorded after *t*, the model trains on the future and looks brilliant offline, then collapses in production. "Point-in-time correct" joins — feature values as of the label's timestamp — are the defense, and a core reason to use a feature store rather than ad-hoc queries.

## When you need one

A single model with a handful of static features does not need this machinery. The value shows up when features are reused across models, computed from streaming data, or shared across a team — anywhere the same feature is defined more than once and could drift. The principle survives even without a dedicated product: one definition, used in both paths, computed point-in-time correctly.

## What to remember

- A feature store serves one feature definition to both training and serving, preventing skew.
- Offline (throughput) and online (low-latency) stores hold the same features for different access patterns.
- Point-in-time-correct joins prevent time leakage — features must use only data available before the label.

## References

- See feature-store and serving patterns in [`../../references/references.md`](../../references/references.md).
