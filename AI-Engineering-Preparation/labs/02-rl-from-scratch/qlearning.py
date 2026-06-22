#!/usr/bin/env python3
"""Tabular Q-learning from scratch (Lab 02).

Reinforcement learning is learning by trial and reward instead of from labeled examples. An agent in
a state picks an action, the environment returns a reward and a next state, and over many episodes the
agent learns which actions pay off. Q-learning makes this concrete: it learns a table Q[state][action]
estimating the long-run value of each action, and the greedy policy - always take the highest-value
action - converges to optimal.

This builds it on a small deterministic gridworld: start top-left, reach the goal bottom-right, with a
step penalty so shorter paths score higher. No libraries, seeded RNG for reproducibility. It shows the
three things every RL system has - an environment, a reward signal, and a policy derived from learned
values - and that the learned policy takes the optimal six-step path.

References: Sutton & Barto, Reinforcement Learning: An Introduction (2nd ed.); Watkins & Dayan (1992),
Q-learning.

Usage:
    python qlearning.py --self-test
    python qlearning.py --demo
"""
from __future__ import annotations

import argparse
import random
import sys

N = 4                      # 4x4 grid
START = 0                  # top-left
GOAL = N * N - 1           # bottom-right
ACTIONS = ("up", "down", "left", "right")
OPTIMAL_STEPS = 2 * (N - 1)  # Manhattan distance start -> goal


def step(state: int, action: int) -> tuple[int, float, bool]:
    """Deterministic transition. Reward: +10 at the goal, -1 per step otherwise (so shorter is better)."""
    r, c = divmod(state, N)
    if action == 0:
        r = max(0, r - 1)
    elif action == 1:
        r = min(N - 1, r + 1)
    elif action == 2:
        c = max(0, c - 1)
    else:
        c = min(N - 1, c + 1)
    ns = r * N + c
    return ns, (10.0 if ns == GOAL else -1.0), ns == GOAL


def train(seed: int = 0, episodes: int = 500, alpha: float = 0.5, gamma: float = 0.9):
    """Q-learning. The update nudges Q[s][a] toward reward + gamma * max_a' Q[s'][a'] - the Bellman
    target. Exploration is epsilon-greedy with a decaying epsilon, seeded for reproducibility."""
    rng = random.Random(seed)
    Q = [[0.0] * 4 for _ in range(N * N)]
    for ep in range(episodes):
        s = START
        eps = max(0.05, 1.0 - ep / episodes)
        for _ in range(100):
            a = rng.randrange(4) if rng.random() < eps else _argmax(Q[s])
            ns, reward, done = step(s, a)
            Q[s][a] += alpha * (reward + gamma * max(Q[ns]) - Q[s][a])
            s = ns
            if done:
                break
    return Q


def _argmax(row: list[float]) -> int:
    return max(range(len(row)), key=lambda i: row[i])


def greedy_policy(Q) -> list[int]:
    return [_argmax(Q[s]) for s in range(N * N)]


def greedy_path(Q, max_len: int = 50) -> list[int]:
    s = START
    path = [s]
    for _ in range(max_len):
        s, _, done = step(s, _argmax(Q[s]))
        path.append(s)
        if done:
            break
    return path


def render_policy(Q) -> str:
    arrows = {0: "↑", 1: "↓", 2: "←", 3: "→"}
    pol = greedy_policy(Q)
    rows = []
    for r in range(N):
        cells = []
        for c in range(N):
            s = r * N + c
            cells.append("G" if s == GOAL else arrows[pol[s]])
        rows.append(" ".join(cells))
    return "\n".join(rows)


def _self_test() -> int:
    Q = train(seed=0)
    assert greedy_policy(train(seed=0)) == greedy_policy(Q)  # deterministic given the seed

    path = greedy_path(Q)
    assert path[-1] == GOAL, "greedy policy must reach the goal"
    assert len(path) - 1 == OPTIMAL_STEPS, (len(path) - 1, OPTIMAL_STEPS)  # learned the optimal route

    # value sanity: the start's best action has positive value; the goal-adjacent cell values the goal move
    assert max(Q[START]) > 0
    assert Q[GOAL - 1][3] > 0  # moving right into the goal pays

    print(f"self-test: deterministic Q-table; greedy policy reaches goal in {len(path)-1} steps "
          f"(optimal={OPTIMAL_STEPS}); start value {max(Q[START]):.2f} > 0 OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Tabular Q-learning on a gridworld")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    Q = train(seed=0)
    if args.demo:
        print("learned greedy policy:\n" + render_policy(Q))
        print("\noptimal path:", greedy_path(Q))
    else:
        print("path:", greedy_path(Q))
    return 0


if __name__ == "__main__":
    sys.exit(main())
