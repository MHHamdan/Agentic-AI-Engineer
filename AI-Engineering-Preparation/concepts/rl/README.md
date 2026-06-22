# Reinforcement learning

The ideas behind how agents learn from outcomes and how models are aligned to human preferences: environments, rewards, policies and values, policy-gradient methods, and RLHF.

> Batch 02: notes delivered. Runnable companion: [`labs/02-rl-from-scratch/`](../../labs/02-rl-from-scratch/).

## Notes

1. [RL primitives](./rl-primitives.md) — agent, environment, reward, policy, value; why value is long-run, not immediate.
2. [Policy gradients and PPO](./policy-gradients.md) — value-based vs. policy-based learning; the advantage; why PPO keeps updates small.
3. [RLHF: from preferences to policy](./rlhf.md) — SFT, a reward model from comparisons, RL optimization, and reward hacking.

## Key references

- Reinforcement Learning: An Introduction (Sutton & Barto, 2nd ed.).
- Proximal Policy Optimization — arXiv:1707.06347.
- Deep RL from Human Preferences — arXiv:1706.03741.
- InstructGPT (RLHF) — arXiv:2203.02155.

See the full list in [`../../references/references.md`](../../references/references.md). All explanations are original; sources are cited, not reproduced ([`STYLE.md`](../../STYLE.md)).
