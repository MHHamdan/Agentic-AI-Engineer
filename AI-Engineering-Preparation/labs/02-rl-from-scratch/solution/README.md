# Lab 02 · Reference solution

Complete implementation of [Lab 02](../README.md).

## What this is

- **`qlearning.py`** — tabular Q-learning on a gridworld (`train`, `greedy_policy`, `greedy_path`, `render_policy`).
- **`preferences.py`** — Bradley-Terry reward model from pairwise preferences (`make_preferences`, `fit_reward`, `ranking`, `policy_choice`).

## Expected results

- Greedy policy reaches the goal in 6 steps (optimal); start value > 0.
- From 10 pairwise preferences (no scores), the learned ranking equals the true ranking and the policy picks the best item.

## Running

```bash
cd labs/02-rl-from-scratch
python qlearning.py --self-test
python qlearning.py --demo
python preferences.py --self-test
python preferences.py --demo
```
