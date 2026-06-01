# Lab 43 · Reference solution

The complete implementation of [Lab 43: Tracking annotator drift](../README.md).

## What this is

The over-time extension of Lab 40's agreement measurement:

- **`annotation_rounds.jsonl`** — three rounds of three-annotator binary labels; annotator `a3` drifts (agreement-with-consensus falls round over round) while `a1`/`a2` hold.
- **Per-round agreement-with-consensus** — Cohen's κ between each annotator and that round's majority consensus, giving three trajectories.
- **Drift flag** — an annotator whose agreement drops beyond a tolerance from first to last round is flagged (trajectory, not a single round).
- **Reliability-weighted consensus** — weight each annotator by recent agreement, down-weighting the drifter; recompute the ceiling among the calibrated pair.

## Expected shape of the result

`a3` falls roughly 0.83 → 0.33 → 0.12 (flagged); `a1`/`a2` stay high with normal round-to-round wobble. The latest-round weights down-weight `a3` sharply. The lesson: in a single judge-vs-consensus number, this drift would read as the *model* getting worse — only per-annotator tracking reveals it's the annotator.

## Implementation choices

1. **Consensus-agreement over time as the monitor** (pairwise κ from Lab 40 is the one-time diagnostic).
2. **Flag on trajectory, not a round** — small rounds wobble; drift is a sustained fall.
3. **Down-weight, don't delete** — drift is usually a re-calibration problem.
4. **Recompute the ceiling among calibrated raters** — the old ceiling no longer holds once a rater drifts.

## What's out of scope

- More rounds/items (three rounds of 12 is a teaching size; real drift needs more to call confidently).
- Adjudication or a held-out gold set for weighting (uses a simple linear scheme).
- The re-calibration process itself (shared examples, guideline review).

## Running

```bash
cd labs/43-annotator-drift
jupyter notebook solution/lab.ipynb
```

## Next

Re-measure agreement every round; recompute the Lab 40 ceiling among the calibrated raters before trusting any judged metric.
