---
quiz_id: embedding-space-drift
title: Embedding-space drift detection
path: 06-evaluation-observability
module: v2-frameworks-and-drift
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "What's the most precise statement of how embedding-space drift differs from the score-side drift that Module 5 covers?"
    options:
      - "Embedding-space drift only matters for RAG systems; score-side drift matters for all LLM systems"
      - "Embedding-space drift is a leading indicator on the input side of the eval pipeline; score-side drift is a lagging indicator on the output side. The two compose — embedding drift propagates through retrieval and generation into score-side drift over time"
      - "Embedding-space drift uses different statistical tests (centroid shift, NN overlap); score-side drift uses KS/PSI/Wasserstein. The tests are the only difference"
      - "Embedding-space drift requires re-embedding the corpus on detection; score-side drift requires recalibrating the judge"
    answer: "Embedding-space drift is a leading indicator on the input side of the eval pipeline; score-side drift is a lagging indicator on the output side. The two compose — embedding drift propagates through retrieval and generation into score-side drift over time"
  - id: q2
    text: "Production RAG systems frequently experience 'silent degradation' — recall drops from 0.92 to 0.74 over weeks with no errors logged. According to the cited mid-2026 production literature, what is the most common root cause?"
    options:
      - "Provider weight updates without changing the model identifier — the LLM silently changes behavior on the same prompts"
      - "Eval set staleness — the golden set no longer represents production queries"
      - "Partial corpus re-embedding — a team re-embeds ~20% of the corpus using a different embedding model version than the 80% already indexed, and the two halves now occupy different regions of embedding space"
      - "Query injection attacks shifting the query distribution into adversarial regions"
    answer: "Partial corpus re-embedding — a team re-embeds ~20% of the corpus using a different embedding model version than the 80% already indexed, and the two halves now occupy different regions of embedding space"
  - id: q3
    text: "You observe that topic populations have shifted measurably between baseline and current windows: one cluster shrunk and another grew, but the overall centroid is roughly stable. Which detector catches this and which one(s) miss it?"
    options:
      - "Centroid shift catches it; cluster-population chi-square misses it"
      - "Cosine-distance distribution shift catches it; everything else misses it"
      - "Cluster-population chi-square catches it; centroid shift misses it because population redistribution can leave the overall centroid roughly stationary"
      - "Only NN overlap catches it because it measures user-felt retrieval changes"
    answer: "Cluster-population chi-square catches it; centroid shift misses it because population redistribution can leave the overall centroid roughly stationary"
  - id: q4
    text: "You want to measure nearest-neighbor overlap between baseline and current versions of a corpus. What's the critical contract that must hold for the metric to be meaningful?"
    options:
      - "The two embedding sets must be drawn from the same statistical distribution"
      - "Row i in baseline_embeddings and row i in current_embeddings must refer to the same logical document — the two arrays are two embedding versions of the same N documents, not two different corpora. Without this contract, doc_id overlap is near zero by construction"
      - "The probe queries must be drawn from a uniform distribution over the embedding space"
      - "The baseline and current sets must have the same L2 norm distribution"
    answer: "Row i in baseline_embeddings and row i in current_embeddings must refer to the same logical document — the two arrays are two embedding versions of the same N documents, not two different corpora. Without this contract, doc_id overlap is near zero by construction"
  - id: q5
    text: "What is the correct way to use UMAP / t-SNE visualizations in an embedding-drift workflow?"
    options:
      - "As the primary alert signal — when UMAP shows separate clusters, fire an alert"
      - "As a diagnostic and communication aid only, not as proof of drift. Dimensionality reduction can fabricate apparent clusters from random noise, and drift patterns existing only in the discarded dimensions will be missed. The statistical tests (centroid, cosine-distance, NN overlap, cluster population) are the authoritative detectors"
      - "As a replacement for clustering-based drift detection — UMAP's local structure preservation makes KMeans unnecessary"
      - "Not at all — UMAP and t-SNE are research tools and have no production use"
    answer: "As a diagnostic and communication aid only, not as proof of drift. Dimensionality reduction can fabricate apparent clusters from random noise, and drift patterns existing only in the discarded dimensions will be missed. The statistical tests (centroid, cosine-distance, NN overlap, cluster population) are the authoritative detectors"
  - id: q6
    text: "A production rolling-window embedding-drift detector fires for two consecutive 24-hour windows. What is the right operational response per the Pattern 2 severity routing this lab implements?"
    options:
      - "Auto-rebuild the index and the embeddings; the drift signal is self-evident proof of degradation"
      - "Classify by number of detectors firing in concert: a single detector firing maps to T1 (annotation queue for investigation); two detectors map to T2 (page eval engineer for next-business-day investigation); three or more map to T3 (page on-call, suspend in-flight experiments, investigate same day). Drift signals are investigation triggers, not remediation instructions"
      - "Wait for score-side drift (Lab 20) to confirm before taking any action — embedding drift alone is not actionable"
      - "Re-embed the entire corpus once and verify the alert clears"
    answer: "Classify by number of detectors firing in concert: a single detector firing maps to T1 (annotation queue for investigation); two detectors map to T2 (page eval engineer for next-business-day investigation); three or more map to T3 (page on-call, suspend in-flight experiments, investigate same day). Drift signals are investigation triggers, not remediation instructions"
  - id: q7
    text: "When tuning the rolling-window detector's alert thresholds, what production-derived rule of thumb does the concept page cite for the user-facing reference signal?"
    options:
      - "Auto-tune via Bayesian optimization against a labeled drift dataset"
      - "A 2-to-5 point Recall@10 drop in rolling-mean over 30 to 90 minutes is the closest user-facing signal — the embedding-side thresholds should fire before the Recall@10 signal would, since embedding drift is the leading indicator. 2σ rolling-mean shifts are the canonical centroid-side trigger; KS p < 0.001 sustained ≥ 24 hours is the canonical distribution-side trigger"
      - "Always use p < 0.05 thresholds — anything stricter produces too many false negatives"
      - "There is no production-derived rule; thresholds are always domain-specific"
    answer: "A 2-to-5 point Recall@10 drop in rolling-mean over 30 to 90 minutes is the closest user-facing signal — the embedding-side thresholds should fire before the Recall@10 signal would, since embedding drift is the leading indicator. 2σ rolling-mean shifts are the canonical centroid-side trigger; KS p < 0.001 sustained ≥ 24 hours is the canonical distribution-side trigger"
  - id: q8
    text: "Which of these is INSIDE the anti-scope of embedding-space drift detection as this page defines it?"
    options:
      - "Monitoring the rolling cosine-distance distribution to baseline"
      - "Treating an embedding-drift event as proof of answer-quality degradation, and auto-rebuilding the index without human review. Embedding drift can fire on legitimate distribution shifts (new tenants, holiday traffic, geographic expansion) that don't degrade quality; the signal is 'investigate', not 'broken'"
      - "Using Reference Dataset Probing to detect embedding-model version drift"
      - "Wiring the drift events into Pattern 2's three-tier severity routing"
    answer: "Treating an embedding-drift event as proof of answer-quality degradation, and auto-rebuilding the index without human review. Embedding drift can fire on legitimate distribution shifts (new tenants, holiday traffic, geographic expansion) that don't degrade quality; the signal is 'investigate', not 'broken'"
---

# Embedding-space drift detection — quiz

Eight single-select questions covering input-side drift concepts, the four detection methods, the rolling-window + severity-routing workflow, and the anti-scope of treating drift as quality-degradation proof.

Read these before attempting the quiz:

- 📖 [Embedding-space drift detection](../../concepts/evaluation/embedding-space-drift-detection.md) — the concept page (~22 min)
- 🧪 [Lab 23 — Embedding-space drift detection](../../labs/23-embedding-space-drift-detection/) — the implementation (~90-110 min)
- 📖 [Drift detection](../../concepts/evaluation/drift-detection.md) — the score-side sibling (Module 5)

Passing threshold: 6/8.

---

<details>
<summary><b>Question 1</b> — How does embedding-space drift differ from score-side drift?</summary>

**Answer**: Embedding-space drift is a leading indicator on the input side of the eval pipeline; score-side drift is a lagging indicator on the output side. The two compose — embedding drift propagates through retrieval and generation into score-side drift over time.

The key framing in the concept page is the causal chain: `embedding drift → retrieval-result drift → answer drift → score-side drift`. When the upstream signal fires but the downstream hasn't, you have lead time to investigate before user-visible degradation surfaces.

</details>

<details>
<summary><b>Question 2</b> — Most common root cause of silent recall degradation?</summary>

**Answer**: Partial corpus re-embedding using a different embedding model version than the 80% already indexed — the two halves now occupy different regions of embedding space, and cross-half retrieval degrades silently because cosine similarity is meaningful only between vectors produced under the same conditions.

Decompressed.io (March 2026) names this as the most common production cause; the concept page Section 3 covers it as the canonical "document corpus drift" failure mode.

</details>

<details>
<summary><b>Question 3</b> — Topic redistribution detection?</summary>

**Answer**: Cluster-population chi-square catches it; centroid shift misses it because population redistribution can leave the overall centroid roughly stationary.

This is the canonical example of why cluster-population testing is needed alongside centroid testing — two detectors that cover complementary failure modes rather than overlapping ones. The lab's Scenario C demonstrates this directly: cosine-distribution and cluster tests fire, but centroid alone doesn't.

</details>

<details>
<summary><b>Question 4</b> — NN overlap contract?</summary>

**Answer**: Row i in baseline_embeddings and row i in current_embeddings must refer to the same logical document — the two arrays are two embedding versions of the same N documents, not two different corpora.

Without this contract, doc_id overlap is near zero by construction (because different documents have unrelated doc_ids). This is the contract Lab 23 documents and asserts in the `nn_overlap` function, and why NN-overlap applies only to scenarios B and D (corpus re-embedding) and not to A and C (population change).

</details>

<details>
<summary><b>Question 5</b> — UMAP / t-SNE role?</summary>

**Answer**: As a diagnostic and communication aid only, not as proof of drift.

Dimensionality reduction can fabricate apparent clusters from random noise; drift patterns existing only in the discarded dimensions will be missed; the choice of hyperparameters significantly affects what the visualization shows. UMAP is often preferred over t-SNE for density-based work because it better preserves global structure, but neither replaces the four statistical tests.

</details>

<details>
<summary><b>Question 6</b> — Operational response to a rolling-window drift alert?</summary>

**Answer**: Classify by number of detectors firing in concert and route to T1/T2/T3 per Pattern 2.

The lab's Step 7 implements exactly this classifier: 1 detector → T1 (annotation queue); 2 → T2 (page eval engineer); 3+ → T3 (page on-call + suspend experiments). The principle is that drift signals are investigation triggers, not remediation instructions — auto-rebuilding the index covers up diagnostic information.

</details>

<details>
<summary><b>Question 7</b> — Threshold tuning rule of thumb?</summary>

**Answer**: The embedding-side thresholds should fire before the Recall@10 signal would, since embedding drift is the leading indicator. 2σ rolling-mean shifts on centroid; KS p < 0.001 sustained ≥ 24 hours on cosine-distance distribution.

The reference signal — 2-to-5 point Recall@10 drop in rolling-mean over 30-90 minutes — comes from FutureAGI (May 2026); the 2σ centroid threshold from Stack Pulsar (April 2026); the p < 0.001 sustained threshold from the Pattern 2 T2 mapping. All three are documented in the concept page's Section 5 production-parameters list.

</details>

<details>
<summary><b>Question 8</b> — What's anti-scope?</summary>

**Answer**: Treating an embedding-drift event as proof of answer-quality degradation, and auto-rebuilding the index without human review.

Embedding drift can fire on legitimate distribution shifts (new tenants, holiday traffic, geographic expansion) that don't degrade quality. The signal is "investigate", not "broken." Auto-rebuild on drift covers up the diagnostic signal and the next failure mode appears without anyone having investigated the first — the same anti-pattern Pattern 2 documents for auto-retraining.

</details>
