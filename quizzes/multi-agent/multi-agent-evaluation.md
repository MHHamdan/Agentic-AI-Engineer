---
quiz_id: multi-agent-evaluation
title: Multi-agent evaluation
path: 03-multi-agent-systems
module: 6
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "Why is outcome-only evaluation insufficient for multi-agent systems?"
    options:
      - "Outcome metrics are slower to compute than trajectory metrics"
      - "Multi-agent systems can produce correct answers via broken trajectories that won't generalize"
      - "Outcome metrics require LLM-as-judge and trajectory metrics don't"
      - "Outcome metrics can't be computed in production"
    answer: "Multi-agent systems can produce correct answers via broken trajectories that won't generalize"
  - id: q2
    text: "What does the replay model add compared to live evaluation?"
    options:
      - "It catches behavior that depends on live state (current web content, time-sensitive routing)"
      - "It enables determinism and CI integration, since the recorded trace is fixed"
      - "It removes the need for hand-curated fixtures"
      - "It eliminates the rule-based vs LLM-as-judge trade-off"
    answer: "It enables determinism and CI integration, since the recorded trace is fixed"
  - id: q3
    text: "A trace shows handoff_success_rate=1.0 and routing_accuracy=1.0, but citation_preservation=0.5. What's the most likely diagnosis?"
    options:
      - "The supervisor is routing incorrectly"
      - "The retriever returned no results"
      - "Semantic handoff drift: the structural envelope was preserved but the content was paraphrased away"
      - "The trace fixture has the wrong category annotation"
    answer: "Semantic handoff drift: the structural envelope was preserved but the content was paraphrased away"
  - id: q4
    text: "Which metric pair distinguishes a buggy planner from a buggy execution environment?"
    options:
      - "Handoff success rate and routing accuracy"
      - "Plan validity and plan coverage"
      - "Citation preservation and groundedness"
      - "Replan rate and step cap rate"
    answer: "Plan validity and plan coverage"
  - id: q5
    text: "Why does Lab 16 hand-curate 15 traces rather than generate 1500 synthetically?"
    options:
      - "Synthetic traces are too expensive to generate at scale"
      - "Lab 09's lesson carries over: synthesis bias compounds — your synthesized planner makes the planner mistakes you wrote, not the ones your real planner makes"
      - "Pydantic validation fails on synthetic traces"
      - "The harness can only score 15 traces at a time"
    answer: "Lab 09's lesson carries over: synthesis bias compounds — your synthesized planner makes the planner mistakes you wrote, not the ones your real planner makes"
  - id: q6
    text: "What does category slicing prevent in trajectory-level evaluation?"
    options:
      - "It prevents the LLM-as-judge biases that Zheng et al. (2023) documented"
      - "It prevents the heterogeneous-trace problem where aggregate metrics hide which failure mode is firing"
      - "It removes the need for per-agent breakdown"
      - "It replaces the need for hand-curated trace fixtures"
    answer: "It prevents the heterogeneous-trace problem where aggregate metrics hide which failure mode is firing"
  - id: q7
    text: "When is per-agent evaluation most useful relative to end-to-end evaluation?"
    options:
      - "Per-agent is the default; end-to-end is a stretch metric"
      - "End-to-end says the system has a problem; per-agent says which agent is dragging the metric down. Use per-agent to localize after end-to-end fires"
      - "Per-agent eliminates the need for trajectory metrics"
      - "Per-agent and end-to-end produce identical scores when the system works correctly"
    answer: "End-to-end says the system has a problem; per-agent says which agent is dragging the metric down. Use per-agent to localize after end-to-end fires"
  - id: q8
    text: "Why does the citation_preservation metric canonicalize URLs (strip trailing slashes, fragments, tracking params) before comparison?"
    options:
      - "Production systems require canonical URLs by HTTP standard"
      - "Otherwise the same web page cited as `example.com/x` vs `example.com/x/?utm=foo` shows as a missed citation — false negative that masks real issues"
      - "Canonicalization is a Vertex AI requirement"
      - "Pydantic's URL validators require canonicalization"
    answer: "Otherwise the same web page cited as `example.com/x` vs `example.com/x/?utm=foo` shows as a missed citation — false negative that masks real issues"
---

# Multi-agent evaluation · 🧠 Check your understanding

Calibrate against the [multi-agent evaluation](../../concepts/multi-agent/multi-agent-evaluation.md) and [trajectory-level metrics](../../concepts/multi-agent/trajectory-level-metrics.md) concept pages plus [Lab 16](../../labs/16-multi-agent-evaluation-from-scratch/). 8 single-select questions. Passing: 6/8.

---

**1.** Why is outcome-only evaluation insufficient for multi-agent systems?

- (a) Outcome metrics are slower to compute than trajectory metrics
- (b) Multi-agent systems can produce correct answers via broken trajectories that won't generalize
- (c) Outcome metrics require LLM-as-judge and trajectory metrics don't
- (d) Outcome metrics can't be computed in production

<details>
<summary>Answer</summary>

**(b)** — A multi-agent system can produce the right answer via a lucky-but-broken trajectory (the routing happened to land on the right specialist by accident; the writer faithfully composed prose around a paraphrased-into-uselessness brief). The right outcome from a broken path won't reproduce. Trajectory metrics catch this; outcome metrics by themselves don't. The companion failure (right trajectory, wrong outcome — content drift in transit) is symmetric and motivates needing both tiers.

See: [multi-agent-evaluation.md → "The two tiers"](../../concepts/multi-agent/multi-agent-evaluation.md#the-two-tiers-of-multi-agent-evaluation).
</details>

---

**2.** What does the replay model add compared to live evaluation?

- (a) It catches behavior that depends on live state (current web content, time-sensitive routing)
- (b) It enables determinism and CI integration, since the recorded trace is fixed
- (c) It removes the need for hand-curated fixtures
- (d) It eliminates the rule-based vs LLM-as-judge trade-off

<details>
<summary>Answer</summary>

**(b)** — Replay's strength is exactly opposite to (a): it sacrifices live-state behavior in exchange for determinism, low cost (the same trace can be scored five ways without re-running the system), diagnostic depth (the full trajectory is available for inspection), and CI compatibility (no external service calls during evaluation). Live evaluation catches what replay misses; the two are complements, not substitutes.

See: [multi-agent-evaluation.md → "The replay model"](../../concepts/multi-agent/multi-agent-evaluation.md#the-replay-model).
</details>

---

**3.** A trace shows handoff_success_rate=1.0 and routing_accuracy=1.0, but citation_preservation=0.5. What's the most likely diagnosis?

- (a) The supervisor is routing incorrectly
- (b) The retriever returned no results
- (c) Semantic handoff drift: the structural envelope was preserved but the content was paraphrased away
- (d) The trace fixture has the wrong category annotation

<details>
<summary>Answer</summary>

**(c)** — Handoff success rate is *structural* (envelope well-formed, status="ok", non-empty args). Routing accuracy is the *sequence* of nodes visited. Both can be 1.0 while the content inside the handoff envelope drifted — the researcher's three citations became the writer's two, even though the envelope shape was unchanged. This is the citation-drift failure mode the harness is designed to surface, and exactly why outcome metrics (citation_preservation) need to be paired with trajectory metrics.

See: [trajectory-level-metrics.md → "Handoff success rate"](../../concepts/multi-agent/trajectory-level-metrics.md#1-handoff-success-rate) ("what this hides: semantic handoff drift").
</details>

---

**4.** Which metric pair distinguishes a buggy planner from a buggy execution environment?

- (a) Handoff success rate and routing accuracy
- (b) Plan validity and plan coverage
- (c) Citation preservation and groundedness
- (d) Replan rate and step cap rate

<details>
<summary>Answer</summary>

**(b)** — Plan validity asks "did the planner emit something the validator accepted?" Plan coverage asks "did the validated plan actually execute?" `validity=0.0` localizes the failure to the planner (it never produced a workable plan). `validity=1.0, coverage<1.0` localizes to execution (the plan was good; the tools or the environment broke). Reading them together tells you whether to iterate on the planner prompt or fix tool reliability.

See: [trajectory-level-metrics.md → "Plan validity"](../../concepts/multi-agent/trajectory-level-metrics.md#3-plan-validity) and [Plan coverage](../../concepts/multi-agent/trajectory-level-metrics.md#4-plan-coverage).
</details>

---

**5.** Why does Lab 16 hand-curate 15 traces rather than generate 1500 synthetically?

- (a) Synthetic traces are too expensive to generate at scale
- (b) Lab 09's lesson carries over: synthesis bias compounds — your synthesized planner makes the planner mistakes you wrote, not the ones your real planner makes
- (c) Pydantic validation fails on synthetic traces
- (d) The harness can only score 15 traces at a time

<details>
<summary>Answer</summary>

**(b)** — Same reasoning Lab 09 made for hand-curated eval sets over synthetic generation. When you generate traces, the generator's bias becomes the test set's bias: you catch the failure modes you can imagine and miss the ones the actual planner produces. Hand-curation is slow but each trace is carefully annotated for what it tests. The harness's diagnostic value comes from category coverage (5 categories × 3 source labs) more than from raw trace count.

See: [multi-agent-evaluation.md → "The trace fixture"](../../concepts/multi-agent/multi-agent-evaluation.md#the-trace-fixture) and [Lab 09's eval-set construction](../../concepts/evaluation/eval-set-construction.md).
</details>

---

**6.** What does category slicing prevent in trajectory-level evaluation?

- (a) It prevents the LLM-as-judge biases that Zheng et al. (2023) documented
- (b) It prevents the heterogeneous-trace problem where aggregate metrics hide which failure mode is firing
- (c) It removes the need for per-agent breakdown
- (d) It replaces the need for hand-curated trace fixtures

<details>
<summary>Answer</summary>

**(b)** — Aggregate metrics across heterogeneous traces will lie. `citation_preservation = 0.72` aggregated across happy_path and citation_drift categories tells you nothing about what to fix. The same `0.72` sliced into `happy_path=0.97, citation_drift=0.40` tells you the citation_drift category is doing exactly what it should (surfacing the failure mode it was designed to test) while happy_path runs are mostly clean. Slicing is the discipline; aggregation without slicing produces wrong conclusions.

See: [trajectory-level-metrics.md → "Aggregating and slicing"](../../concepts/multi-agent/trajectory-level-metrics.md#aggregating-and-slicing).
</details>

---

**7.** When is per-agent evaluation most useful relative to end-to-end evaluation?

- (a) Per-agent is the default; end-to-end is a stretch metric
- (b) End-to-end says the system has a problem; per-agent says which agent is dragging the metric down. Use per-agent to localize after end-to-end fires
- (c) Per-agent eliminates the need for trajectory metrics
- (d) Per-agent and end-to-end produce identical scores when the system works correctly

<details>
<summary>Answer</summary>

**(b)** — End-to-end metrics are the headline ("did the system do its job"); per-agent metrics are the diagnostic ("which agent to iterate on"). Most teams default to end-to-end and add per-agent when end-to-end drops. Per-agent is more work to set up (you need per-agent rubrics and per-agent expected outputs in the trace), so it earns its place when you have a specific agent under suspicion.

See: [multi-agent-evaluation.md → "Per-agent vs end-to-end"](../../concepts/multi-agent/multi-agent-evaluation.md#per-agent-vs-end-to-end-evaluation).
</details>

---

**8.** Why does the citation_preservation metric canonicalize URLs (strip trailing slashes, fragments, tracking params) before comparison?

- (a) Production systems require canonical URLs by HTTP standard
- (b) Otherwise the same web page cited as `example.com/x` vs `example.com/x/?utm=foo` shows as a missed citation — false negative that masks real issues
- (c) Canonicalization is a Vertex AI requirement
- (d) Pydantic's URL validators require canonicalization

<details>
<summary>Answer</summary>

**(b)** — URLs in citations come from different places: the researcher's tool returns one canonical form; the writer's prose may repeat the URL in a slightly different form; tracking parameters may get added. Without canonicalization, equality-on-string fails on what are *actually* the same page. The metric becomes pessimistic — reports drops that aren't real drops — and that noise masks the real drops the metric is designed to catch.

See: [trajectory-level-metrics.md → "Citation preservation"](../../concepts/multi-agent/trajectory-level-metrics.md#6-citation-preservation-across-handoffs) and the Lab 16 `_canonicalize_url` implementation.
</details>

---

✓ **Path 03 v1 complete after this module.** Foundations → patterns → framework bridge → evaluation. The path is structurally closed.
