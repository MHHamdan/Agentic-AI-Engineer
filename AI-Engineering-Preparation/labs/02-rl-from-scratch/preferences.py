#!/usr/bin/env python3
"""Reward modeling from preferences (Lab 02).

How do you train a model toward something you cannot write down a reward function for - "be more
helpful," "this answer is better"? You collect comparisons (A is better than B) and fit a reward
that explains them. This is the engine inside RLHF: a reward model learned from human pairwise
preferences, which a policy is then optimized against.

This builds the reward model from scratch with the Bradley-Terry model: the probability that item i is
preferred over j is the logistic function of their reward difference, sigma(r_i - r_j). Fitting r by
gradient ascent on the preference log-likelihood recovers a scoring that orders items the same way the
preferences do - and a greedy policy then picks the top-scored item. No labeled scores are ever shown
to the learner, only which of two was preferred. Deterministic, offline, standard-library only.

References: Bradley & Terry (1952); Christiano et al. (2017), Deep RL from Human Preferences,
arXiv:1706.03741; Ouyang et al. (2022), InstructGPT, arXiv:2203.02155.

Usage:
    python preferences.py --self-test
    python preferences.py --demo
"""
from __future__ import annotations
import argparse, math, sys

# Latent "true" quality of five candidate answers. The learner never sees these - only comparisons.
TRUE_QUALITY = [0.1, 0.9, 0.5, 0.3, 0.7]


def make_preferences(true_quality: list[float]) -> list[tuple[int, int]]:
    """Every ordered pair (winner, loser) where the higher-quality item wins. Noiseless here so the
    test is deterministic; real preference data is noisy and the same fit still works."""
    n = len(true_quality)
    return [(i, j) for i in range(n) for j in range(n)
            if i != j and true_quality[i] > true_quality[j]]


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def fit_reward(prefs: list[tuple[int, int]], n: int, iters: int = 2000, lr: float = 0.1) -> list[float]:
    """Gradient ascent on the Bradley-Terry log-likelihood. For a preference (i over j), the gradient
    pushes r_i up and r_j down by (1 - sigma(r_i - r_j)) - the model's surprise that i won. Rewards are
    centered each step because only differences are identifiable (a constant shift changes nothing)."""
    r = [0.0] * n
    for _ in range(iters):
        grad = [0.0] * n
        for i, j in prefs:
            err = 1.0 - _sigmoid(r[i] - r[j])
            grad[i] += err
            grad[j] -= err
        for k in range(n):
            r[k] += lr * grad[k] / len(prefs)
        mean = sum(r) / n
        r = [x - mean for x in r]
    return r


def ranking(scores: list[float]) -> list[int]:
    return sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)


def policy_choice(scores: list[float]) -> int:
    """A reward-greedy policy: pick the highest-reward option."""
    return ranking(scores)[0]


def _self_test() -> int:
    prefs = make_preferences(TRUE_QUALITY)
    r = fit_reward(prefs, len(TRUE_QUALITY))
    assert fit_reward(prefs, len(TRUE_QUALITY)) == r  # deterministic

    learned = ranking(r)
    truth = ranking(TRUE_QUALITY)
    assert learned == truth, (learned, truth)  # recovered the true order from comparisons alone

    # the policy picks the genuinely best answer, learned only from "A beats B" signals
    assert policy_choice(r) == truth[0]

    # pairwise consistency: learned reward agrees with every training preference
    agree = sum(1 for i, j in prefs if r[i] > r[j])
    assert agree == len(prefs), (agree, len(prefs))

    print(f"self-test: deterministic fit; recovered true ranking {learned} from {len(prefs)} pairwise "
          f"prefs (no scores shown); policy picks item {policy_choice(r)}; {agree}/{len(prefs)} prefs satisfied")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Reward modeling from pairwise preferences")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    prefs = make_preferences(TRUE_QUALITY)
    r = fit_reward(prefs, len(TRUE_QUALITY))
    if args.demo:
        print("learned reward (centered):", [round(x, 2) for x in r])
        print("learned ranking:", ranking(r), " true ranking:", ranking(TRUE_QUALITY))
        print("policy picks item:", policy_choice(r))
    else:
        print("learned ranking:", ranking(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
