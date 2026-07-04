"""Tiny preference-learning demo for RLHF-style reward modeling."""

from __future__ import annotations

import argparse
import math
import sys

TRUE_QUALITY: dict[str, float] = {
    "concise": 1.6,
    "correct": 2.2,
    "verbose": 0.4,
    "unsafe": -1.4,
    "vague": -0.7,
}


def sigmoid(x: float) -> float:
    """Numerically stable sigmoid."""
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)

    z = math.exp(x)
    return z / (1.0 + z)


def make_preferences() -> list[tuple[str, str]]:
    """Create deterministic pairwise preferences from hidden quality scores."""
    items = list(TRUE_QUALITY)
    preferences: list[tuple[str, str]] = []

    for i, left in enumerate(items):
        for right in items[i + 1 :]:
            if TRUE_QUALITY[left] >= TRUE_QUALITY[right]:
                preferences.append((left, right))
            else:
                preferences.append((right, left))

    return preferences


def fit_reward(
    preferences: list[tuple[str, str]],
    epochs: int = 500,
    lr: float = 0.1,
) -> dict[str, float]:
    """Fit a Bradley-Terry reward model from pairwise preferences."""
    items = sorted({item for pair in preferences for item in pair})
    reward = dict.fromkeys(items, 0.0)

    for _ in range(epochs):
        grad = dict.fromkeys(items, 0.0)

        for winner, loser in preferences:
            probability = sigmoid(reward[winner] - reward[loser])
            update = 1.0 - probability
            grad[winner] += update
            grad[loser] -= update

        for item in items:
            reward[item] += lr * grad[item] / max(1, len(preferences))

        mean_reward = sum(reward.values()) / len(reward)
        for item in items:
            reward[item] -= mean_reward

    return reward


def ranking(scores: dict[str, float]) -> list[str]:
    """Return items from best to worst."""
    return sorted(scores, key=scores.get, reverse=True)


def policy_choice(reward: dict[str, float]) -> str:
    """Choose the highest-reward item."""
    return ranking(reward)[0]


def _self_test() -> None:
    preferences = make_preferences()
    reward = fit_reward(preferences)

    assert len(preferences) == 10
    assert policy_choice(reward) == ranking(TRUE_QUALITY)[0]
    assert ranking(reward)[-1] == ranking(TRUE_QUALITY)[-1]

    print("preferences self-test passed")


def _demo() -> None:
    preferences = make_preferences()
    reward = fit_reward(preferences)

    print("Preferences:")
    for winner, loser in preferences:
        print(f"  {winner} > {loser}")

    print("\nLearned reward ranking:", ranking(reward))
    print("True quality ranking:  ", ranking(TRUE_QUALITY))
    print("Policy choice:", policy_choice(reward))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        _self_test()
        return 0

    if args.demo:
        _demo()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
