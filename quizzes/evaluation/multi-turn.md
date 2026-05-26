---
quiz_id: multi-turn
title: Multi-turn (threaded) evaluation
path: 06-evaluation-observability
module: 7
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "Your single-turn evaluator scores 0.92 on every turn of an agent's transcripts, but production users complain the bot 'goes in circles' and 'forgets what I said.' What is the most likely diagnosis?"
    options:
      - "The single-turn evaluator is miscalibrated; recalibrate against humans"
      - "The failure modes are between turns, not within turns. Single-turn metrics evaluate one turn in isolation and cannot catch knowledge-retention failures, role drift across the conversation, or completeness failures where every individual answer is fluent but the user's task never gets done. You need conversation-level metrics."
      - "Switch judge models — your current judge is biased toward fluent-sounding answers"
      - "Disable evaluation; rely on production user feedback instead"
    answer: "The failure modes are between turns, not within turns. Single-turn metrics evaluate one turn in isolation and cannot catch knowledge-retention failures, role drift across the conversation, or completeness failures where every individual answer is fluent but the user's task never gets done. You need conversation-level metrics."
  - id: q2
    text: "Which of the four canonical conversation-level metrics is considered the single most important — the one to compute first, every time?"
    options:
      - "Knowledge Retention — agents that re-ask for known facts are unforgivable"
      - "Role Adherence — agents that drift off-task are the highest-risk failures"
      - "Conversation Completeness — if the user's task didn't get done, nothing else matters. The other metrics (Retention, Adherence, Turn Relevancy) are diagnostic when Completeness fails."
      - "Turn Relevancy — every turn must be contextually appropriate or the conversation is broken"
    answer: "Conversation Completeness — if the user's task didn't get done, nothing else matters. The other metrics (Retention, Adherence, Turn Relevancy) are diagnostic when Completeness fails."
  - id: q3
    text: "Three units of evaluation often get confused. Which statement is correct?"
    options:
      - "Turn-level and conversation-level are the same thing"
      - "Turn-level evaluates one response in context; conversation-level evaluates the whole sequence as one unit; trajectory evaluates the path of decisions and tool calls. All three are complementary, not interchangeable — a coding agent can have perfect turn-level scores, perfect conversation-level scores, and still have a poor trajectory (15 tool calls when 3 would have sufficed)."
      - "Trajectory evaluation is a strict subset of conversation-level evaluation"
      - "Single-turn evaluation is obsolete in 2026; only conversation-level matters"
    answer: "Turn-level evaluates one response in context; conversation-level evaluates the whole sequence as one unit; trajectory evaluates the path of decisions and tool calls. All three are complementary, not interchangeable — a coding agent can have perfect turn-level scores, perfect conversation-level scores, and still have a poor trajectory (15 tool calls when 3 would have sufficed)."
  - id: q4
    text: "Trajectory evaluation scales differently from single-turn evaluation. What is the canonical complexity framing?"
    options:
      - "Both are O(n) in the number of test cases"
      - "Trajectory evaluation is O(n × k) where n is the number of test cases and k is the average trajectory length — every tool call is its own evaluation surface, so a coding agent making 15 tool calls per task generates 15 checkpoints to evaluate"
      - "Trajectory evaluation is O(log n) because tool calls are hierarchical"
      - "Trajectory evaluation is O(n²) because each tool call must be compared to every other tool call"
    answer: "Trajectory evaluation is O(n × k) where n is the number of test cases and k is the average trajectory length — every tool call is its own evaluation surface, so a coding agent making 15 tool calls per task generates 15 checkpoints to evaluate"
  - id: q5
    text: "A useful conversation simulation suite covers three persona archetypes. Which one catches role-adherence and security failures specifically?"
    options:
      - "Cooperative — the happy path persona that provides all info upfront and accepts the agent's answers"
      - "Distracted / chaotic — changes topics, forgets context, contradicts itself; catches knowledge-retention failures"
      - "Adversarial — appears polite but probes role boundaries, attempts jailbreaks, asks the agent to violate its role spec under casual cover; catches role-adherence and security failures"
      - "Verbose — produces long, rambling messages; tests token-budget handling"
    answer: "Adversarial — appears polite but probes role boundaries, attempts jailbreaks, asks the agent to violate its role spec under casual cover; catches role-adherence and security failures"
  - id: q6
    text: "What is the cooperative-only trap in conversation simulation?"
    options:
      - "Cooperative personas are too verbose and inflate token costs"
      - "Building a simulation suite of only cooperative users, declaring the agent ready for production, and discovering that real production traffic contains ~30-40% distracted or adversarial users — the failure modes your suite never tested. Every test suite needs at least one adversarial persona, regardless of expected traffic mix."
      - "Cooperative personas don't generate enough diverse conversations to score well on coverage metrics"
      - "The LLM simulating a cooperative user becomes too obedient and matches the agent's outputs verbatim"
    answer: "Building a simulation suite of only cooperative users, declaring the agent ready for production, and discovering that real production traffic contains ~30-40% distracted or adversarial users — the failure modes your suite never tested. Every test suite needs at least one adversarial persona, regardless of expected traffic mix."
  - id: q7
    text: "A 50-turn conversation exceeds your judge model's context window. What is the standard mitigation, and what's its trade-off?"
    options:
      - "Truncate to the last 10 turns; you lose context but the metric still runs"
      - "Switch judge models to a frontier model with larger context — but at higher cost per call"
      - "Sliding-window scoring: score overlapping windows of N turns (e.g., 8 turns with stride 4) and aggregate. Trade-off: per-window scoring is local — a failure where the agent contradicts at turn 47 a fact stated at turn 2 escapes detection if no window includes both turns. The pattern is necessary at scale but it's not free."
      - "Summarize the conversation first, then score the summary"
    answer: "Sliding-window scoring: score overlapping windows of N turns (e.g., 8 turns with stride 4) and aggregate. Trade-off: per-window scoring is local — a failure where the agent contradicts at turn 47 a fact stated at turn 2 escapes detection if no window includes both turns. The pattern is necessary at scale but it's not free."
  - id: q8
    text: "When does conversation simulation supplement, rather than replace, production-trace evaluation?"
    options:
      - "Always — simulation is sufficient on its own; production traces are redundant"
      - "Never — production traces are sufficient on their own; simulation is redundant"
      - "The Sim2Real gap means simulators can't capture lexical diversity, off-task interruptions, domain-specific terminology, or emotional escalation the way real users produce them. Simulation is useful for CI gates and pre-release regression testing; production-trace evaluation (Module 4's online evaluators + Module 5's drift detection) is required for ongoing operations. The two are complementary, not redundant."
      - "Only when you can't afford production-trace evaluation"
    answer: "The Sim2Real gap means simulators can't capture lexical diversity, off-task interruptions, domain-specific terminology, or emotional escalation the way real users produce them. Simulation is useful for CI gates and pre-release regression testing; production-trace evaluation (Module 4's online evaluators + Module 5's drift detection) is required for ongoing operations. The two are complementary, not redundant."
---

# Multi-turn (threaded) evaluation · 🧠 Check your understanding

Calibrate against the [multi-turn evaluation](../../concepts/evaluation/multi-turn-evaluation.md) and [conversation simulation](../../concepts/evaluation/conversation-simulation.md) concept pages plus [Lab 22](../../labs/22-multi-turn-evaluation/). 8 single-select questions covering conversation-level metrics, trajectory evaluation, persona-driven simulation, and the production decision boundary. Passing: 6/8.

---

**1.** Your single-turn evaluator scores 0.92 on every turn of an agent's transcripts, but production users complain the bot "goes in circles" and "forgets what I said." What is the most likely diagnosis?

- (a) The single-turn evaluator is miscalibrated; recalibrate against humans
- (b) The failure modes are between turns, not within turns. Single-turn metrics evaluate one turn in isolation and cannot catch knowledge-retention failures, role drift across the conversation, or completeness failures where every individual answer is fluent but the user's task never gets done. You need conversation-level metrics.
- (c) Switch judge models — your current judge is biased toward fluent-sounding answers
- (d) Disable evaluation; rely on production user feedback instead

<details>
<summary>Answer</summary>

**(b)** — This is the canonical failure mode of single-turn-only evaluation, documented in 2026 production case studies (Confident AI 2026, the voice-AI insurance team at 0.92 faithfulness with chronic complaints). The single-turn metric evaluates one assistant response against one user message; the failure mode is between turns — the agent has the user's email in its context history at turn 4 because it was given at turn 2, but the agent doesn't *use* that context, so it re-asks. Single-turn evals can't see across turn boundaries.

(a) is plausible but doesn't fit — recalibrating a single-turn metric still wouldn't catch between-turn failures. (c) is the wrong dimension. (d) abandons evaluation entirely.

See: [multi-turn-evaluation.md → "The single-turn trap"](../../concepts/evaluation/multi-turn-evaluation.md#the-single-turn-trap).
</details>

---

**2.** Which of the four canonical conversation-level metrics is considered the single most important — the one to compute first, every time?

- (a) Knowledge Retention — agents that re-ask for known facts are unforgivable
- (b) Role Adherence — agents that drift off-task are the highest-risk failures
- (c) Conversation Completeness — if the user's task didn't get done, nothing else matters. The other metrics (Retention, Adherence, Turn Relevancy) are diagnostic when Completeness fails.
- (d) Turn Relevancy — every turn must be contextually appropriate or the conversation is broken

<details>
<summary>Answer</summary>

**(c)** — Conversation Completeness is the single most important multi-turn metric (Confident AI 2026; widely accepted across DeepEval, Langfuse, MLflow, etc.). The reasoning: a conversation can score perfect on Knowledge Retention, Role Adherence, and Turn Relevancy and still completely fail Completeness — the agent acknowledged each user intent politely and never actually delivered on any of them. If the task didn't get done, the conversation failed regardless of how the other metrics look.

The other three metrics are diagnostic: they explain *why* Completeness fails when it fails. Retention failures lead to Completeness failures because the agent loses the context needed to complete. Adherence failures lead to Completeness failures because the agent went off-task. Turn Relevancy failures lead to Completeness failures because the agent kept answering the wrong question.

See: [multi-turn-evaluation.md → "The four canonical conversation-level metrics"](../../concepts/evaluation/multi-turn-evaluation.md#the-four-canonical-conversation-level-metrics).
</details>

---

**3.** Three units of evaluation often get confused. Which statement is correct?

- (a) Turn-level and conversation-level are the same thing
- (b) Turn-level evaluates one response in context; conversation-level evaluates the whole sequence as one unit; trajectory evaluates the path of decisions and tool calls. All three are complementary, not interchangeable — a coding agent can have perfect turn-level scores, perfect conversation-level scores, and still have a poor trajectory (15 tool calls when 3 would have sufficed).
- (c) Trajectory evaluation is a strict subset of conversation-level evaluation
- (d) Single-turn evaluation is obsolete in 2026; only conversation-level matters

<details>
<summary>Answer</summary>

**(b)** — The three units are explicitly distinct dimensions answering different questions. Turn-level: "given this user turn, was the assistant's response correct?" Conversation-level: "across the whole dialogue, did the agent succeed?" Trajectory: "did the agent take the right path of decisions and tool calls?" The coding-agent example makes the distinction concrete — the agent can be locally correct on every turn (turn-level pass), achieve the user's task (conversation-level pass), and burn 12 wasted tool calls along the way (trajectory fail).

(a), (c), (d) all collapse the dimensions incorrectly. Turn-level isn't obsolete — it's just insufficient on its own.

See: [multi-turn-evaluation.md → "Conversation-level vs turn-level vs trajectory metrics"](../../concepts/evaluation/multi-turn-evaluation.md#conversation-level-vs-turn-level-vs-trajectory-metrics).
</details>

---

**4.** Trajectory evaluation scales differently from single-turn evaluation. What is the canonical complexity framing?

- (a) Both are O(n) in the number of test cases
- (b) Trajectory evaluation is O(n × k) where n is the number of test cases and k is the average trajectory length — every tool call is its own evaluation surface, so a coding agent making 15 tool calls per task generates 15 checkpoints to evaluate
- (c) Trajectory evaluation is O(log n) because tool calls are hierarchical
- (d) Trajectory evaluation is O(n²) because each tool call must be compared to every other tool call

<details>
<summary>Answer</summary>

**(b)** — The O(n × k) framing comes from Rane 2026's chapter on agent evaluation and is widely cited. Single-turn evaluation has one evaluation surface per test case: the assistant's response. Trajectory evaluation has *k* evaluation surfaces per test case: one per tool call (or step). For a coding agent making 15 tool calls per task, you have 15 checkpoints — each of which can fail in different ways (wrong tool, wrong arguments, useless intermediate result, redundant call).

The operational implication: trajectory evaluation costs *k* times more in judge calls than turn-level evaluation, which is why teams typically sample trajectories rather than score every tool call exhaustively.

See: [multi-turn-evaluation.md → "Conversation-level vs turn-level vs trajectory metrics"](../../concepts/evaluation/multi-turn-evaluation.md#conversation-level-vs-turn-level-vs-trajectory-metrics).
</details>

---

**5.** A useful conversation simulation suite covers three persona archetypes. Which one catches role-adherence and security failures specifically?

- (a) Cooperative — the happy path persona that provides all info upfront and accepts the agent's answers
- (b) Distracted / chaotic — changes topics, forgets context, contradicts itself; catches knowledge-retention failures
- (c) Adversarial — appears polite but probes role boundaries, attempts jailbreaks, asks the agent to violate its role spec under casual cover; catches role-adherence and security failures
- (d) Verbose — produces long, rambling messages; tests token-budget handling

<details>
<summary>Answer</summary>

**(c)** — Adversarial personas specifically catch role-adherence and security failures. The pattern is "appear polite but probe the agent's limits" — ask out-of-scope questions casually (as if related to the user's main task), reference fake prior conversations, ask the agent to ignore its instructions in friendly tones. A scheduling agent that gives medical advice on turn 3 of an "adversarial scheduling conversation" has a Role Adherence failure.

(a) catches baseline task-completion failures (the easy case). (b) catches knowledge-retention failures (the noisy-but-real-user case). (d) isn't one of the canonical three archetypes — and verbosity is mostly a token-budget concern, not a behavioral one.

See: [conversation-simulation.md → "Three persona archetypes"](../../concepts/evaluation/conversation-simulation.md#three-persona-archetypes).
</details>

---

**6.** What is the cooperative-only trap in conversation simulation?

- (a) Cooperative personas are too verbose and inflate token costs
- (b) Building a simulation suite of only cooperative users, declaring the agent ready for production, and discovering that real production traffic contains ~30-40% distracted or adversarial users — the failure modes your suite never tested. Every test suite needs at least one adversarial persona, regardless of expected traffic mix.
- (c) Cooperative personas don't generate enough diverse conversations to score well on coverage metrics
- (d) The LLM simulating a cooperative user becomes too obedient and matches the agent's outputs verbatim

<details>
<summary>Answer</summary>

**(b)** — The cooperative-only trap is documented across 2026 multi-turn-eval literature (Confident AI 2026; the production-traffic distribution figures from agent observability tools as of 2026). The trap: simulation suites lean cooperative because cooperative scenarios are easier to specify and easier for the agent to handle. The team ships, production traffic is ~60-70% cooperative + 20-30% distracted + 5-10% adversarial, and the 30-40% of non-cooperative traffic surfaces failure modes the suite never tested. The fix isn't to match the production distribution — it's to ensure adversarial coverage exists *at all*. Every test suite needs at least one adversarial persona as a hard rule, not as a percentage of traffic.

See: [conversation-simulation.md → "The cooperative-only trap"](../../concepts/evaluation/conversation-simulation.md#the-cooperative-only-trap).
</details>

---

**7.** A 50-turn conversation exceeds your judge model's context window. What is the standard mitigation, and what's its trade-off?

- (a) Truncate to the last 10 turns; you lose context but the metric still runs
- (b) Switch judge models to a frontier model with larger context — but at higher cost per call
- (c) Sliding-window scoring: score overlapping windows of N turns (e.g., 8 turns with stride 4) and aggregate. Trade-off: per-window scoring is local — a failure where the agent contradicts at turn 47 a fact stated at turn 2 escapes detection if no window includes both turns. The pattern is necessary at scale but it's not free.
- (d) Summarize the conversation first, then score the summary

<details>
<summary>Answer</summary>

**(c)** — Sliding-window scoring is the standard mitigation. Score overlapping windows of N turns and aggregate. The aggregation is typically a mean (sometimes a min, when conservative scoring is wanted).

The trade-off matters: per-window scoring is *local*. A cross-window contradiction (the agent contradicts at turn 47 a fact stated at turn 2) escapes detection if no single window includes both turns. The longer the conversation, the more cross-window failures the pattern misses. The cleaner long-term answer is judge models with larger context — by 2026, frontier judge models handle 32K+ context, which fits a 50-turn conversation directly. Sliding-window is the fallback when context is genuinely insufficient.

(a) loses early-conversation context that may be required. (b) is the cleaner answer but isn't always cost-feasible. (d) summarization introduces its own evaluation problem — was the summary faithful? — and is rarely used in 2026 production.

See: [conversation-simulation.md → "The sliding-window pattern for long conversations"](../../concepts/evaluation/conversation-simulation.md#the-sliding-window-pattern-for-long-conversations).
</details>

---

**8.** When does conversation simulation supplement, rather than replace, production-trace evaluation?

- (a) Always — simulation is sufficient on its own; production traces are redundant
- (b) Never — production traces are sufficient on their own; simulation is redundant
- (c) The Sim2Real gap means simulators can't capture lexical diversity, off-task interruptions, domain-specific terminology, or emotional escalation the way real users produce them. Simulation is useful for CI gates and pre-release regression testing; production-trace evaluation (Module 4's online evaluators + Module 5's drift detection) is required for ongoing operations. The two are complementary, not redundant.
- (d) Only when you can't afford production-trace evaluation

<details>
<summary>Answer</summary>

**(c)** — The Sim2Real gap (term borrowed from robotics; applied to agent simulation by Zhou et al. 2026) is the systematic distance between simulated and production conversations. Simulators capture *types* of behavior the team thought to specify; they can't capture behavior types nobody specified. Real production traffic includes lexical patterns (slang, typos, abbreviations), off-task interruptions (phone calls mid-conversation), domain-specific knowledge references (internal company terminology), and emotional escalation that synthetic personas don't reproduce.

The right pattern is complementary deployment: simulation for CI gates and pre-release regression testing (where reproducibility matters); production-trace evaluation for ongoing operations (where coverage and realism matter). Neither subsumes the other.

(a) and (b) are both extreme positions that aren't operationally defensible. (d) makes simulation a budget-driven choice, which inverts the relationship — simulation is *additionally* required, not a fallback.

See: [conversation-simulation.md → "The Sim2Real gap"](../../concepts/evaluation/conversation-simulation.md#the-sim2real-gap).
</details>

---

✓ **Module 7 complete after this quiz.** With Module 7, **Path 06 v1 is complete** — all seven modules shipped end-to-end.
