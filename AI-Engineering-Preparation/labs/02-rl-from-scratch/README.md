# Lab 02: RL from scratch

> 🟢 Foundational · ⏱ ~60–75 min · 📚 Path 02 (ML & RL fundamentals)

## 🎯 Goal

Build the two learning signals behind how modern models are trained and aligned — value-based reinforcement learning and preference-based reward modeling — from scratch, so RLHF stops being a black box.

By the end you should be able to:

- Name the three parts of any RL setup — environment, reward, policy — and point to each in code.
- Explain why a "value" is long-run, not the immediate reward.
- Implement Q-learning and show its greedy policy converging to optimal.
- Implement reward modeling from pairwise preferences (the engine inside RLHF) and explain why comparisons alone recover an ordering.

## 🛠 Modules

| File | What it does |
|---|---|
| `qlearning.py` | tabular Q-learning on a deterministic gridworld: `train`, `greedy_policy`, `greedy_path`, `render_policy` (`--self-test`, `--demo`) |
| `preferences.py` | Bradley-Terry reward model from pairwise preferences: `make_preferences`, `fit_reward`, `ranking`, `policy_choice` (`--self-test`, `--demo`) |

## What the numbers say

- Q-learning: the greedy policy reaches the goal in **6 steps** (the Manhattan optimum); the start state has positive value because the policy from there eventually earns the goal reward.
- Reward model: from **10 pairwise preferences** with no numeric scores, the fit recovers the exact true ranking and the policy picks the genuinely best item.

## Design choices and tradeoffs

- **Value vs. immediate reward.** Q-learning's target is `reward + γ·max Q(next)`, so value propagates backward from the goal; the discount `γ` sets how far-sighted the agent is.
- **Exploration vs. exploitation.** Epsilon-greedy with a decaying epsilon explores early and exploits late; the RNG is seeded so the run is reproducible.
- **Preferences over scores.** People rank more reliably than they score, so RLHF learns from comparisons. Only reward *differences* are identifiable, which is why the fit is centered.

## Common gotchas

- **Tabular does not scale.** A table works because the state space is tiny; real RL approximates Q or the policy with a network.
- **Reward hacking.** A policy optimizes the reward it is given, not the one you meant. A flawed reward model yields a confidently wrong policy — the central risk in RLHF.
- **Determinism.** Seed the RNG and fix iteration counts, or "it learned" becomes unreproducible.

## 🧮 Going deeper

- 📐 [math-foundations/02](../../math-foundations/02-rl-objectives.md) — return, value, and the policy-gradient idea.
- 📖 [concepts/rl/rl-primitives.md](../../concepts/rl/rl-primitives.md) · [policy-gradients.md](../../concepts/rl/policy-gradients.md) · [rlhf.md](../../concepts/rl/rlhf.md).

## References

- Sutton, R. & Barto, A. *Reinforcement Learning: An Introduction* (2nd ed.).
- Watkins, C. & Dayan, P. (1992). *Q-learning.*
- Christiano, P., et al. (2017). *Deep RL from Human Preferences.* arXiv:1706.03741.
- Ouyang, L., et al. (2022). *InstructGPT.* arXiv:2203.02155.
