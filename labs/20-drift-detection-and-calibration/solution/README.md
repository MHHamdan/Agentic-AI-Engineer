# Lab 20 · Reference solution

The polished final implementation of [Lab 20: Drift detection and agent-as-judge calibration](../README.md).

## What this is

Two halves. **Half A** demonstrates three drift-detection algorithms (Kolmogorov-Smirnov, Population Stability Index, Wasserstein distance) on three drift patterns (gradual, abrupt, shape-only); a rolling-window stream detector with ~50-sample latency. **Half B** measures and mitigates verbosity bias in an LLM-as-judge via Cohen's kappa; a 12-week calibration drift simulation detects an injected drift event at week 6.

- **Three drift patterns** as synthetic score streams: gradual (slow mean shift), abrupt (sharp change at midpoint), shape-only (same mean, different variance).
- **KS-test** (`scipy.stats.ks_2samp`) — sensitive to any distributional change.
- **PSI from scratch** (~15 LOC) — production-favorite for its interpretability (0.1 / 0.25 thresholds).
- **Wasserstein distance** (`scipy.stats.wasserstein_distance`) — the earth-mover metric; sensitive to mean shifts, less so to shape-only drift.
- **Test selection table** — which test catches which scenario; surfaces the trade-offs.
- **Rolling-window detector** — KS-test on a 1000-sample stream with a mid-stream drift event; the detector flags drift ~50 samples after onset.
- **10-example human gold set** — the calibration anchor.
- **Simulated LLM judge with controlled biases** — length-correlated bias gets κ=0.000 at baseline.
- **Length-controlled mitigation** — the actual lever; κ jumps from 0.000 → 1.000.
- **12-week recalibration loop** — judge drifts at week 6; detector flags at week 9.

## How it differs from `../lab.ipynb`

| Lab notebook (34 cells) | Solution (35 cells) |
|---|---|
| Per-step tutorial framing under each `### Step N` | One-line headers; explanation in concept pages |
| Each drift algorithm introduced separately | Same step structure; less prose between |
| Week-by-week walkthrough of the 12-week simulation | Single condensed run with the final week-9-detection result |
| Sanity-test cells for each metric | Combined into Step 6's summary table |

## Implementation choices

1. **PSI implemented from scratch** rather than via a library. Two reasons: (1) keeps the binning math visible (10 bins; equal-width; clip values to baseline range); (2) avoids a dependency for a 15-line function. The 0.1 / 0.25 thresholds are the production convention.
2. **Three drift patterns chosen to expose which test misses what.** Gradual drift is caught by KS and Wasserstein but not strongly by PSI at small magnitudes. Abrupt drift is caught by all three. Shape-only drift (same mean, different variance) is caught by KS but missed by Wasserstein. The combination is what the comparison table makes visible.
3. **Rolling-window over per-sample-test** for the stream detector. The trade-off: per-sample tests have very high false-positive rates with small samples; rolling windows have detection latency (~window_size / 2 samples). Production deployments converge on rolling windows; the ~50-sample latency is acceptable for most score streams.
4. **The 10-example human gold set as the calibration anchor, not a 100-example set.** 10 is the smallest set that still produces statistically meaningful kappa. Production calibration uses 50-200 examples per quarter; the lab uses 10 to show the pattern.
5. **Length-controlled mitigation as the canonical bias-removal lever.** The simulated judge has length-correlated bias (`score ∝ len(answer)`); the mitigation normalizes by length before scoring. Other mitigations exist (rubric refinement, judge-ensemble, calibration constants) — length normalization is the simplest example.
6. **The 12-week simulation injects drift at week 6 and detects at week 9.** The 3-week detection delay is a deliberate design choice — production teams want low false-positive rates more than they want immediate detection. The window-size lever moves the trade-off.

## What's deliberately out of scope

- **Continuous-time drift detection** (CUSUM, EWMA). Mentioned in the concept page; out of scope.
- **Multivariate drift detection** (joint distribution shifts). Single-score drift is the practical concern; multivariate is more theoretical.
- **Concept drift vs covariate drift distinction**. Mentioned in concept pages; the lab focuses on score-distribution drift specifically.
- **Real LLM-as-judge calls.** Half B uses a simulated judge with controlled biases — exactly what's needed to demonstrate calibration. Real judges (gpt-4o, claude-haiku) would add cost without changing the pedagogy.
- **The full κ interpretation table** beyond the lab's `interpret_kappa` thresholds. Mentioned in concept page references (Landis & Koch 1977).

## Running the solution

```bash
cd labs/20-drift-detection-and-calibration/solution

# No API keys required — pure Python + scipy
jupyter notebook lab.ipynb
```

**Wall-clock**: ~30-60 seconds. Pure computation; the rolling-window detector is the slowest part at ~5 seconds.

**Cost**: $0 — no LLM calls.

## Reading the headline results

**Drift detection comparison** (representative output):

```
Scenario              KS statistic   p-value   PSI    Wasserstein
gradual_drift         0.18           0.001     0.07   0.04
abrupt_drift          0.34           0.000     0.31   0.12
shape_only_drift      0.16           0.005     0.04   0.01
```

KS catches all three with statistical significance. PSI's `0.07` for gradual and `0.04` for shape-only are below the 0.1 "noteworthy" threshold — illustrating that PSI is conservative; you need substantial drift before it fires.

**Calibration recovery via length control**:

```
Judge variant                        Cohen's κ
length_correlated_baseline           0.000      (no agreement)
length_controlled                    1.000      (perfect agreement on this gold set)
```

The lever isn't subtle — the synthetic bias is fully removed by the mitigation. Real-world bias removal is less complete; the pattern is the lever exists and that you can measure its effect.

## Next

- Take the [drift detection and calibration quiz](../../../quizzes/evaluation/drift-and-calibration.md).
- Lab 21 builds on the trust stack with cost attribution — the unit-economics layer that ties Modules 4-5 to dollars.
