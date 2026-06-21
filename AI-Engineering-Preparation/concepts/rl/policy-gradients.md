# Policy gradients and PPO

> Concept note. ~8 min. Builds on [RL primitives](./rl-primitives.md). Math: [`math-foundations/02`](../../math-foundations/02-rl-objectives.md).

There are two ways to learn to act. **Value-based** methods (like the Q-learning in the lab) learn the value of actions and act greedily on them. **Policy-based** methods skip the value table and adjust the policy directly. The second family is what trains large models with RL, so it is worth the intuition.

## The policy-gradient idea

Represent the policy as a parameterized, probabilistic thing — given a state, it outputs a distribution over actions — and tune the parameters so that actions leading to high return become more likely. The recipe: run the policy, observe the returns, and push up the probability of the actions that did better than expected while pushing down the ones that did worse. "Better than expected" is the key phrase: you compare each action's return to a baseline (often the state's value), and the difference — the **advantage** — tells you which way to nudge. Subtracting the baseline does not change what is optimal, but it cuts the noise in the estimate, which is what makes training stable enough to work.

Policy-based methods handle continuous and very large action spaces gracefully (you never enumerate actions to take a max), and they can learn genuinely stochastic policies. The cost is high variance and sensitivity — a step too large can collapse the policy.

## Why PPO

Plain policy gradients are fragile: one oversized update can move the policy so far that the data you just collected no longer describes it, and learning diverges. **Proximal Policy Optimization (PPO)** is the workhorse fix. The intuition is a leash: improve the policy, but clip the update so the new policy cannot move too far from the old one in a single step. That clipped objective trades a little speed for a lot of stability, which is why PPO became the default for hard RL problems — including the policy-optimization stage of [RLHF](./rlhf.md). You do not need its equations to use the idea: take improving steps, but small, bounded ones.

## What to remember

- Value-based methods learn values and act greedily; policy-based methods adjust the policy directly and scale to large/continuous actions.
- Policy gradients push up actions with positive advantage (return above a baseline); the baseline cuts variance.
- PPO keeps each update close to the previous policy (a clip/leash), trading speed for the stability that makes RL on large models practical.

## References

- Schulman, J., et al. (2017). *Proximal Policy Optimization Algorithms.* arXiv:1707.06347. See [`../../references/references.md`](../../references/references.md).
