from __future__ import annotations

import argparse
import random

N = 4
START = 0
GOAL = N * N - 1
ACTIONS = {
    0: "up",
    1: "down",
    2: "left",
    3: "right",
}
ARROWS = {
    0: "↑",
    1: "↓",
    2: "←",
    3: "→",
}
OPTIMAL_STEPS = 6


def step(state: int, action: int) -> tuple[int, float, bool]:
    """Deterministic transition with +10 at the goal and -1 per step."""
    row, col = divmod(state, N)

    if action == 0:
        row = max(0, row - 1)
    elif action == 1:
        row = min(N - 1, row + 1)
    elif action == 2:
        col = max(0, col - 1)
    else:
        col = min(N - 1, col + 1)

    next_state = row * N + col
    reward = 10.0 if next_state == GOAL else -1.0
    done = next_state == GOAL

    return next_state, reward, done


def _argmax(values: list[float]) -> int:
    best_index = 0
    best_value = values[0]

    for index, value in enumerate(values[1:], start=1):
        if value > best_value:
            best_index = index
            best_value = value

    return best_index


def train(
    episodes: int = 800,
    alpha: float = 0.25,
    gamma: float = 0.92,
    epsilon: float = 0.18,
    seed: int = 7,
) -> list[list[float]]:
    """Train a tiny tabular Q-learning agent on the gridworld."""
    rng = random.Random(seed)
    q_table = [[0.0 for _ in ACTIONS] for _ in range(N * N)]

    for _ in range(episodes):
        state = START

        for _ in range(80):
            if rng.random() < epsilon:
                action = rng.randrange(len(ACTIONS))
            else:
                action = _argmax(q_table[state])

            next_state, reward, done = step(state, action)
            target = reward + gamma * max(q_table[next_state]) * (not done)
            q_table[state][action] += alpha * (target - q_table[state][action])
            state = next_state

            if done:
                break

    return q_table


def greedy_path(q_table: list[list[float]], max_len: int = 50) -> list[int]:
    """Follow the greedy policy from the start state."""
    state = START
    path = [state]

    for _ in range(max_len):
        action = _argmax(q_table[state])
        state, _, done = step(state, action)
        path.append(state)

        if done:
            break

    return path


def render_policy(q_table: list[list[float]]) -> str:
    """Render the greedy policy as arrows."""
    cells = []

    for state in range(N * N):
        if state == GOAL:
            cells.append("G")
        else:
            cells.append(ARROWS[_argmax(q_table[state])])

    rows = [
        " ".join(cells[row * N : (row + 1) * N])
        for row in range(N)
    ]

    return "\n".join(rows)


def _self_test() -> int:
    q_table = train()
    path = greedy_path(q_table)

    assert path[-1] == GOAL, path
    assert len(path) - 1 == OPTIMAL_STEPS, path
    assert max(q_table[START]) > 0.0, q_table[START]
    assert q_table[GOAL - 1][3] > 0.0

    print(
        "self-test: deterministic Q-table recovered a greedy policy "
        f"that reaches the goal in {len(path) - 1} steps "
        f"(optimal={OPTIMAL_STEPS}); start value {max(q_table[START]):.2f} > 0 OK"
    )

    return 0


def _demo() -> int:
    q_table = train()
    path = greedy_path(q_table)

    print("Greedy policy:")
    print(render_policy(q_table))
    print("Path:", path)
    print("Steps:", len(path) - 1)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Tabular Q-learning on a gridworld")
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
