from __future__ import annotations

import argparse
import math

TRUE_QUALITY = {
    "brief-safe": 0.35,
    "detailed-helpful": 0.85,
    "verbose-unclear": 0.20,
    "concise-grounded": 0.95,
    "polite-vague": 0.45,
}


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def make_preferences() -> list[tuple[str, str]]:
    """Create noiseless pairwise preferences from the hidden true quality."""
    items = list(TRUE_QUALITY)
    pairs = []

    for i, left in enumerate(items):
        for right in items[i + 1 :]:
            if TRUE_QUALITY[left] >= TRUE_QUALITY[right]:
                pairs.append((left, right))
            else:
                pairs.append((right, left))

    return pairs


def fit_reward(
    preferences: list[tuple[str, str]],
    epochs: int = 500,
    lr: float = 0.08,
) -> dict[str, float]:
    """Fit a Bradley-Terry reward model from pairwise preferences."""
    items = sorted({item for pair in preferences for item in pair})
    reward = dict.fromkeys(items, 0.0)

    for _ in range(epochs):
        grad = dict.fromkeys(items, 0.0)

        for winner, loser in preferences:
            margin = reward[winner] - reward[loser]
            probability = sigmoid(margin)
            error = 1.0 - probability
            grad[winner] += error
            grad[loser] -= error

        for item in items:
            reward[item] += lr * grad[item]

        mean_reward = sum(reward.values()) / len(reward)
        for item in items:
            reward[item] -= mean_reward

    return reward


def ranking(scores: dict[str, float]) -> list[str]:
    """Return items from best to worst."""
    return sorted(scores, key=scores.get, reverse=True)


def policy_choice(reward: dict[str, float]) -> str:
    """A policy optimized against the reward model chooses the top reward item."""
    return ranking(reward)[0]


def _self_test() -> int:
    prefs = make_preferences()
    reward = fit_reward(prefs)
    learned = ranking(reward)
    truth = ranking(TRUE_QUALITY)

    agree = 0
    for winner, loser in prefs:
        if reward[winner] > reward[loser]:
            agree += 1

    assert learned == truth, (learned, truth)
    assert policy_choice(reward) == truth[0], (policy_choice(reward), truth[0])
    assert agree == len(prefs), (agree, len(prefs))

    print(
        "self-test: deterministic Bradley-Terry reward model recovered "
        f"the true ranking {learned} from {len(prefs)} pairwise preferences; "
        f"policy picks item {policy_choice(reward)}; "
        f"{agree}/{len(prefs)} preferences satisfied"
    )

    return 0


def _demo() -> int:
    prefs = make_preferences()
    reward = fit_reward(prefs)

    print("Learned reward scores:")
    for item in ranking(reward):
        print(f"- {item:18s} {reward[item]: .3f}")

    print("Policy choice:", policy_choice(reward))
    print("True best:", ranking(TRUE_QUALITY)[0])

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Reward modeling from pairwise preferences")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.demo:
        return _demo()

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
