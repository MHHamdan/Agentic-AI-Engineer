# RL objectives

> Mathematical foundation. ~8 min. Anchor: [`labs/02-rl-from-scratch/`](../labs/02-rl-from-scratch/). Supports [RL primitives](../concepts/rl/rl-primitives.md) and [policy gradients](../concepts/rl/policy-gradients.md).

## Why this matters

Reinforcement learning has one quantity it is always trying to maximize — long-run reward — and a few objects that express it. This page defines the return, value, the Bellman relation that Q-learning uses, and the policy-gradient objective, so the lab's two updates have a place to stand.

## Return: the thing being maximized

At time $t$ the agent collects a stream of rewards $r_t, r_{t+1}, \dots$. The **discounted return** weights sooner rewards more heavily:

$$
G_t = \sum_{k=0}^{\infty} \gamma^{k}\, r_{t+k}, \qquad \gamma \in [0, 1).
$$

The discount $\gamma$ sets the horizon — near $0$ the agent is myopic, near $1$ far-sighted — and keeps the sum finite for ongoing tasks.

## Value and action-value

The **state value** under a policy $\pi$ is the expected return from $s$:

$$
V^{\pi}(s) = \mathbb{E}_{\pi}\!\left[\, G_t \mid s_t = s \,\right].
$$

The **action value** fixes the first action too:

$$
Q^{\pi}(s, a) = \mathbb{E}_{\pi}\!\left[\, G_t \mid s_t = s,\, a_t = a \,\right].
$$

This is the table the lab fills in. A greedy policy reads it off directly: $\pi(s) = \arg\max_a Q(s, a)$.

## The Bellman optimality relation

Value is recursive — the value of now is the reward now plus the discounted value of next. For the optimal action-value $Q^{\*}$:

$$
Q^{\*}(s, a) = \mathbb{E}\!\left[\, r + \gamma \max_{a'} Q^{\*}(s', a') \,\right].
$$

Q-learning turns this identity into an update. Each step nudges the current estimate toward the right-hand side:

$$
Q(s, a) \leftarrow Q(s, a) + \alpha\,\big[\, r + \gamma \max_{a'} Q(s', a') - Q(s, a) \,\big].
$$

The bracket is the **temporal-difference error** — how wrong the current estimate was — and $\alpha$ is the learning rate. Repeating it propagates value backward from the goal, which is why the lab's start state ends up with positive value.

## The policy-gradient objective

Policy-based methods parameterize the policy $\pi_\theta$ and maximize the expected return directly:

$$
J(\theta) = \mathbb{E}_{\pi_\theta}\!\left[\, G_t \,\right].
$$

The policy-gradient theorem gives a usable gradient: increase the log-probability of actions in proportion to how much better than a baseline they did,

$$
\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\!\left[\, \nabla_\theta \log \pi_\theta(a \mid s)\; A(s, a) \,\right],
$$

where the **advantage** $A(s, a) = Q(s, a) - V(s)$ measures "better than expected." Subtracting the baseline $V(s)$ leaves the optimum unchanged but cuts the variance of the estimate — the difference between training that converges and training that does not. PPO maximizes a clipped version of this so each update stays close to the previous policy.

## Reward modeling (the RLHF link)

In the lab's preference module there is no environment reward at all; the reward is *learned*. Under Bradley-Terry, the probability that item $i$ is preferred over $j$ is

$$
P(i \succ j) = \sigma\big(r_i - r_j\big), \qquad \sigma(x) = \frac{1}{1 + e^{-x}},
$$

and fitting $r$ by gradient ascent on the preference log-likelihood recovers a scoring consistent with the comparisons. Only differences $r_i - r_j$ are identifiable, so the scores are centered. That learned $r$ is the reward a policy is then optimized against.

## What to remember

- The agent maximizes the discounted return $G_t$; value is its expectation, and $\gamma$ sets the horizon.
- Q-learning is the Bellman optimality relation turned into a TD update: move $Q$ toward $r + \gamma \max Q(s',\cdot)$.
- Policy gradients raise the log-probability of positive-advantage actions; the baseline cuts variance. RLHF replaces the environment reward with one learned from preferences.

## See also

- [`labs/02-rl-from-scratch/`](../labs/02-rl-from-scratch/) — the TD update and the preference fit in code.
- [`concepts/rl/`](../concepts/rl/) — the same ideas in prose.
