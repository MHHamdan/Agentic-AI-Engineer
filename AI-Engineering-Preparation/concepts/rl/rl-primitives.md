# RL primitives

> Concept note. ~9 min. Runnable companion: [`labs/02-rl-from-scratch/`](../../labs/02-rl-from-scratch/). Math: [`math-foundations/02`](../../math-foundations/02-rl-objectives.md).

Reinforcement learning is learning from consequences rather than from labeled examples. There is no answer key; there is an environment that responds to actions with rewards, and an agent that must discover which actions pay off. The same vocabulary describes a game-playing agent, a robot, and the alignment step that shapes a language model.

## The cast

- **Agent and environment.** The agent acts; the environment responds. Everything outside the agent's control is the environment.
- **State.** The agent's information about the situation right now.
- **Action.** What the agent can do from a state.
- **Reward.** A scalar the environment returns after an action — the only signal of what is good. Designing it is the hard part.
- **Policy.** The agent's strategy: a mapping from state to action (or to a distribution over actions). This is what is learned.
- **Value.** The expected long-run reward from a state (or state-action pair) under a policy — not the immediate reward, but everything that follows.
- **Return.** The actual cumulative (discounted) reward from a point onward; value is its expectation.

## The one idea that trips people up: value ≠ reward

The reward is immediate; the value is the whole future. A move that scores nothing now can have high value because it leads somewhere good later, and a tempting immediate reward can have low value if it leads to a dead end. A **discount factor** γ between 0 and 1 sets how far ahead the agent looks: near 0 is myopic, near 1 is far-sighted. In the lab's gridworld, the start cell has positive value despite paying step penalties, because the policy from there eventually reaches the goal — value has propagated backward from the reward.

## Tensions that define an algorithm

- **Exploration vs. exploitation.** Exploit what looks best, or explore to find something better? Too much of either fails; epsilon-greedy (mostly exploit, occasionally try a random action) is the simplest balance.
- **On-policy vs. off-policy.** Off-policy methods (like Q-learning) can learn the value of the best policy while behaving more exploratory; on-policy methods learn the value of the policy they actually follow.
- **Model-free vs. model-based.** Model-free agents learn values or policies directly from experience without a model of the environment's dynamics; model-based agents learn (or are given) the dynamics and plan with them.

The lab builds a model-free, off-policy, value-based agent — Q-learning — and watches its greedy policy converge to optimal. Where values become a table the agent fills in, and the policy is just "take the highest-value action."

## What to remember

- RL learns from rewards, not labels: agent, environment, state, action, reward, policy, value.
- Value is long-run expected reward, not the immediate reward; the discount sets the horizon.
- Exploration/exploitation, on/off-policy, and model-free/based are the axes that distinguish methods.

## References

- Sutton, R. & Barto, A. *Reinforcement Learning: An Introduction* (2nd ed.). See [`../../references/references.md`](../../references/references.md).
