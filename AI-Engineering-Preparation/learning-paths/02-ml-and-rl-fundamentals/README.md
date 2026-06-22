# Path 02: ML & RL fundamentals

The systems view of machine learning — how data becomes features, models, and a served prediction — and the reinforcement-learning ideas behind how modern models are aligned. This path connects classical ML system design to the RLHF pipeline.

> Status: **delivered** (Batch 02). Concept notes, a runnable lab, a math page, and a diagram are in place.

## Learning objectives

- Trace the ML lifecycle from raw data through features, training, and serving.
- Explain feature stores, online vs. offline serving, and model/data drift.
- Define the RL primitives: environment, reward, policy, value, on- vs. off-policy.
- Explain policy-gradient methods and how RLHF turns human preferences into a reward signal.

## Modules

| # | Note | Topic |
|---|---|---|
| 1 | [The ML lifecycle](../../concepts/ml-system-design/ml-lifecycle.md) | data → features → training → serving → monitoring |
| 2 | [Feature stores and training/serving skew](../../concepts/ml-system-design/feature-stores.md) | one definition, both paths; point-in-time correctness |
| 3 | [Monitoring, drift, and retraining](../../concepts/ml-system-design/monitoring-and-drift.md) | data vs. concept drift; retrain triggers |
| 4 | [RL primitives](../../concepts/rl/rl-primitives.md) | environment, reward, policy, value |
| 5 | [Policy gradients and PPO](../../concepts/rl/policy-gradients.md) | advantage, stability, PPO |
| 6 | [RLHF: from preferences to policy](../../concepts/rl/rlhf.md) | SFT → reward model → RL; reward hacking |

## Lab

- [`labs/02-rl-from-scratch/`](../../labs/02-rl-from-scratch/) — tabular Q-learning on a gridworld and a Bradley-Terry reward model from preferences; offline, deterministic, with self-tests.

## Math

- [`math-foundations/02-rl-objectives.md`](../../math-foundations/02-rl-objectives.md) — return, value, the Bellman/TD update, policy gradients, preference reward modeling.

## Diagram

- [`diagrams/ml-lifecycle.md`](../../diagrams/ml-lifecycle.md) — data → features → training → serving → monitoring, with the retrain and anti-skew edges.

## Concept areas in this path

- [`concepts/ml-system-design`](../../concepts/ml-system-design/)
- [`concepts/rl`](../../concepts/rl/)

## References

Canonical sources for this path are collected in [`references/references.md`](../../references/references.md). Curriculum sequencing only; all explanations are original. See [`STYLE.md`](../../STYLE.md).
