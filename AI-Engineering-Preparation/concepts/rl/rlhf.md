# RLHF: from preferences to policy

> Concept note. ~9 min. Builds on [policy gradients](./policy-gradients.md). Runnable companion: [`labs/02-rl-from-scratch/`](../../labs/02-rl-from-scratch/) (`preferences.py`).

You cannot write a reward function for "be more helpful" or "this answer is better." **Reinforcement learning from human feedback (RLHF)** sidesteps that: instead of specifying the reward, you *learn* it from human comparisons, then optimize a policy against it. It is the alignment step that turned capable base models into usable assistants.

## The three stages

1. **Supervised fine-tuning (SFT).** Start from a pretrained base model and fine-tune it on high-quality example responses, so it reliably follows the instruction format. This is the starting policy.
2. **Reward model from preferences.** Show people pairs of model outputs and ask which is better. Fit a **reward model** that scores an output so that preferred outputs score higher — the Bradley-Terry setup in the lab, where the probability that A is preferred over B is the logistic of their score difference. The labelers never assign numbers; they only compare, and the model recovers a consistent ordering from the comparisons. This is exactly what `preferences.py` does on a toy set: ten "A beats B" judgments, no scores, and it recovers the true ranking.
3. **Policy optimization.** Use RL — typically [PPO](./policy-gradients.md) — to adjust the SFT model so its outputs earn high reward from the reward model. A **KL penalty** ties the policy to the SFT starting point so it improves the reward without drifting into degenerate text that games the score.

```text
base model → SFT → reward model (from pairwise prefs) → RL policy opt (PPO + KL penalty) → aligned model
```

## The central risk: reward hacking

A policy optimizes the reward it is given, not the reward you intended. If the reward model is exploitable — rewarding length, sycophancy, or confident formatting rather than real quality — the policy will find and amplify that flaw, producing outputs that score well and satisfy no one. This is **reward hacking**, and it is the reason RLHF is an engineering discipline rather than a button: the quality of the alignment is capped by the quality of the reward model, which is capped by the quality and coverage of the preference data. The KL penalty limits how far the policy can wander in search of cheap reward, but it does not fix a bad reward model.

Preference-based methods that skip the explicit RL step (optimizing directly on preferences) have become popular alternatives, but the core remains: human comparisons define "better," a learned signal stands in for them at scale, and a policy is moved toward it under a constraint.

## What to remember

- RLHF learns a reward from human comparisons, then optimizes a policy against it — three stages: SFT, reward model, RL.
- The reward model is fit from pairwise preferences (no numeric labels); the lab builds this core from scratch.
- Reward hacking is the central risk: the policy games whatever the reward model actually measures, so alignment is only as good as that model.

## References

- Christiano, P., et al. (2017). *Deep RL from Human Preferences.* arXiv:1706.03741.
- Ouyang, L., et al. (2022). *Training Language Models to Follow Instructions with Human Feedback (InstructGPT).* arXiv:2203.02155. See [`../../references/references.md`](../../references/references.md).
