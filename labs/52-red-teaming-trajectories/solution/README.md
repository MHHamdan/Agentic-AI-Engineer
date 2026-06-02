# Lab 52 · Reference solution

The complete implementation of [Lab 52: Red-teaming agent trajectories](../README.md).

## What this is

The fourth observability pillar in code:

- **`redteam_trajectories.jsonl`** — 20 adversarial trajectories, four OWASP Agentic categories × 5 (prompt injection, goal hijacking, excessive agency, tool misuse), grounded in the Batch 71 corpus. Each records the agent's actions and a human gold label per axis.
- **`redteam_score.py`** — `score_trajectory` (deterministic detectors for `tool_selection` / `recovery` / `containment`), `category_pass_rates`, `red_team_gate`, and `scorer_agreement` (scorer vs human gold).

## Expected results

- A defended and an exploited trajectory in each category score as expected.
- Per-category pass rates: excessive agency 60%, the rest 80%.
- Red-team gate (≥ 80% per category): **blocks** on excessive agency.
- Scorer-vs-gold agreement 0.98 — the one miss is a paraphrased leak the keyword detector slips past.

## Implementation choices

1. **Grade the trajectory, not the prompt** — excessive agency and hijacking only appear across steps.
2. **Per-category pass rates** — surface which attack class is weak (excessive agency → least privilege).
3. **Deterministic scorer, validated against humans** — runs in CI, but the 0.98 agreement shows it's a floor, not a ceiling.

## What's out of scope

- Generating trajectories (use garak / PyRIT / AgentDojo); these are a fixed, hand-built set.
- An LLM judge for the subtle paraphrased-leak cases the keyword detector misses.
- Severity grading (axes are 0/1 here).

## Running

```bash
cd labs/52-red-teaming-trajectories
python redteam_score.py --self-test
python redteam_score.py --gate-threshold 0.8   # prints the gate result; exit 1 if blocked
```

## Next

[Lab 53: Cost and latency observability](../../53-cost-latency-observability/).
