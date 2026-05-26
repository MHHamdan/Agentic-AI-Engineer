---
quiz_id: adversarial-red-teaming
title: Adversarial red-teaming at scale
path: 06-evaluation-observability
module: v2-frameworks-and-drift
read_time_min: 10
passing_score: 6
questions:
  - id: q1
    text: "What is the orthogonal question adversarial red-teaming answers, relative to the rest of Path 06?"
    options:
      - "Path 06 covers natural-traffic evaluation; red-teaming covers the same dataset but with more judges"
      - "The rest of Path 06 answers 'is the system performing well on the queries users actually send?'; red-teaming answers 'does the system fail safely on queries adversaries will send?'. The two need the same orchestration substrate but cover orthogonal question spaces"
      - "Red-teaming replaces drift detection as the production monitoring discipline"
      - "Red-teaming is a different discipline that belongs in Path 07, not Path 06"
    answer: "The rest of Path 06 answers 'is the system performing well on the queries users actually send?'; red-teaming answers 'does the system fail safely on queries adversaries will send?'. The two need the same orchestration substrate but cover orthogonal question spaces"
  - id: q2
    text: "The concept page describes Multi-turn Manipulation as a distinct failure category. What is the canonical 2026 multi-turn attack pattern that distinguishes it from single-turn prompt injection?"
    options:
      - "A single fixed template applied uniformly across multiple turns"
      - "The Crescendo pattern — build benign rapport over early turns, pivot to the actual probe in a later turn. Tree-of-Attack-with-Pruning (TAP) is the algorithmic variant where an attacker LLM iteratively refines based on the target's responses across turns. Both require threaded-evaluation infrastructure (Module 7) that single-turn probes don't"
      - "Indirect prompt injection through retrieved documents"
      - "Reward hacking — the agent maximizes the eval signal without genuinely solving the task"
    answer: "The Crescendo pattern — build benign rapport over early turns, pivot to the actual probe in a later turn. Tree-of-Attack-with-Pruning (TAP) is the algorithmic variant where an attacker LLM iteratively refines based on the target's responses across turns. Both require threaded-evaluation infrastructure (Module 7) that single-turn probes don't"
  - id: q3
    text: "In the six-step red-team workflow, where does the judge ensemble (Pattern 3) plug in, and why is single-judge scoring inadequate for this step specifically?"
    options:
      - "Step 1 (seed scenarios) — to validate the threat model categorization"
      - "Step 4 (scoring) — single-judge is inadequate because (a) adversarial scoring is high-stakes — typically an input to a release decision, where Pattern 3's 'When to use' criteria are met; (b) adversarial scoring is high-variance — subtle policy-line cases divide reviewers, never mind LLM judges; (c) the three-way disagreement structure is itself the most useful red-team signal, distinguishing the agent's clear failures from the genuinely ambiguous boundary cases that need human policy clarification"
      - "Step 6 (regression promotion) — to vote on whether a failure should be promoted"
      - "Step 2 (variant generation) — to ensure variants are diverse"
    answer: "Step 4 (scoring) — single-judge is inadequate because (a) adversarial scoring is high-stakes — typically an input to a release decision, where Pattern 3's 'When to use' criteria are met; (b) adversarial scoring is high-variance — subtle policy-line cases divide reviewers, never mind LLM judges; (c) the three-way disagreement structure is itself the most useful red-team signal, distinguishing the agent's clear failures from the genuinely ambiguous boundary cases that need human policy clarification"
  - id: q4
    text: "A unanimous-fail result from the three-judge ensemble is routed where, per Pattern 2's severity classifier extended to adversarial red-teaming?"
    options:
      - "Auto-promoted to the regression set immediately — three judges agreed, no human review needed"
      - "Auto-blocked at the API gateway so the failure can't reach production"
      - "T3 confirmed-failure queue, with auto-paging to on-call if the category is high-severity (e.g., tool misuse, prompt injection, policy boundary probing). Confirmed-fail traces become regression-test candidates, but promotion to the permanent regression set still requires explicit human review and approval — auto-promotion is an anti-pattern"
      - "The trend-tracking sample (T0) for analysis at the next weekly review"
    answer: "T3 confirmed-failure queue, with auto-paging to on-call if the category is high-severity (e.g., tool misuse, prompt injection, policy boundary probing). Confirmed-fail traces become regression-test candidates, but promotion to the permanent regression set still requires explicit human review and approval — auto-promotion is an anti-pattern"
  - id: q5
    text: "Why does the workflow's promotion step (Step 6 — converting confirmed failures into regression tests) require a human-approval gate rather than auto-promoting all unanimous-fail traces?"
    options:
      - "Auto-promotion is slower than human-approval workflows due to API latency"
      - "Unanimous-fail traces include false positives (a judge ensemble can systematically err on the same boundary case, especially when the variant generator over-fits to known attack patterns). The regression set is a curated artifact whose value comes from the human review notes attached to each entry — removing the gate converts the regression set from a curated artifact into a noisy alert log. A growing regression set with reviewer notes is the central success metric of a red-team program; auto-promotion destroys that metric"
      - "Regulatory frameworks (NIST AI RMF, EU AI Act) explicitly forbid automated regression promotion"
      - "Human reviewers are needed only to assign severity tags; the auto-promotion would otherwise be acceptable"
    answer: "Unanimous-fail traces include false positives (a judge ensemble can systematically err on the same boundary case, especially when the variant generator over-fits to known attack patterns). The regression set is a curated artifact whose value comes from the human review notes attached to each entry — removing the gate converts the regression set from a curated artifact into a noisy alert log. A growing regression set with reviewer notes is the central success metric of a red-team program; auto-promotion destroys that metric"
  - id: q6
    text: "The concept page lists four canonical OSS frameworks (DeepTeam, Promptfoo, PyRIT, Garak) as the mid-2026 landscape. Which of these is the strongest fit for CI/CD-integrated regression testing with YAML-defined configurations?"
    options:
      - "DeepTeam — its OWASP_ASI_2026 alignment is the strongest fit for CI"
      - "PyRIT — Microsoft's framework, with multi-modal CI support"
      - "Promptfoo — YAML-defined test configurations make it the closest thing to Jest or Pytest for LLM applications; the `braintrustdata/eval-action` GitHub Action posts PR-diff comments with improvements (🟢) and regressions (🔴) per scorer; 300,000+ developers in 2026"
      - "Garak — NVIDIA's scanner with the strongest CLI for CI scripting"
    answer: "Promptfoo — YAML-defined test configurations make it the closest thing to Jest or Pytest for LLM applications; the `braintrustdata/eval-action` GitHub Action posts PR-diff comments with improvements (🟢) and regressions (🔴) per scorer; 300,000+ developers in 2026"
  - id: q7
    text: "The concept page says coverage against the OWASP Top 10 for LLM Applications v2025 'is not a compliance framework — it is a security reference classification.' What is the correct relationship between OWASP Top 10 coverage and regulatory frameworks like NIST AI RMF and the EU AI Act?"
    options:
      - "OWASP Top 10 compliance fully satisfies all regulatory requirements; no additional evidence is needed"
      - "OWASP Top 10 is a security classification, not a compliance framework. Demonstrating coverage against all ten categories is *strong evidence* of a mature AI security program and satisfies the adversarial testing requirements in NIST AI RMF Measure 2.6 and the cybersecurity measures in the EU AI Act, but the regulatory frameworks require additional governance evidence (risk management plans, audit trails, conformity assessments for high-risk systems) that OWASP coverage alone does not provide"
      - "OWASP Top 10 is independent of regulatory frameworks; they don't overlap"
      - "The EU AI Act explicitly mandates OWASP Top 10 compliance for all LLM applications"
    answer: "OWASP Top 10 is a security classification, not a compliance framework. Demonstrating coverage against all ten categories is *strong evidence* of a mature AI security program and satisfies the adversarial testing requirements in NIST AI RMF Measure 2.6 and the cybersecurity measures in the EU AI Act, but the regulatory frameworks require additional governance evidence (risk management plans, audit trails, conformity assessments for high-risk systems) that OWASP coverage alone does not provide"
  - id: q8
    text: "Which of these is INSIDE the anti-scope of the adversarial red-teaming concept page?"
    options:
      - "Mapping failure categories to OWASP Top 10 entries"
      - "Documenting the canonical six-step workflow"
      - "Treating a unanimous-fail signal as an instruction to auto-deploy a content block, or claiming '100% prevention' for any class of attack. The page is for defenders building eval infrastructure, not for attackers; defensive patterns and threat models with citations are in scope per the repo's SECURITY.md policy; weaponizable exploits with no defensive purpose are not. The anti-scope also rules out treating the eight-category taxonomy as a substitute for domain-specific safety policy — a medical-advice agent and a customer-support agent use the same red-team mechanics but need different policy lines drafted by domain experts"
      - "Listing the four OSS framework options"
    answer: "Treating a unanimous-fail signal as an instruction to auto-deploy a content block, or claiming '100% prevention' for any class of attack. The page is for defenders building eval infrastructure, not for attackers; defensive patterns and threat models with citations are in scope per the repo's SECURITY.md policy; weaponizable exploits with no defensive purpose are not. The anti-scope also rules out treating the eight-category taxonomy as a substitute for domain-specific safety policy — a medical-advice agent and a customer-support agent use the same red-team mechanics but need different policy lines drafted by domain experts"
---

# Adversarial red-teaming at scale — quiz

Eight single-select questions covering the relationship of adversarial red-teaming to the rest of Path 06, the eight failure categories with OWASP Top 10 alignment, the six-step canonical workflow, the role of the judge ensemble, the human-approval gate on regression promotion, the mid-2026 tool landscape, regulatory framework alignment, and the explicit anti-scope.

Read these before attempting the quiz:

- 📖 [Adversarial red-teaming at scale](../../concepts/evaluation/adversarial-red-teaming-at-scale.md) — the concept page (~25 min)
- 🧪 [Lab 24 — Adversarial red-teaming at scale](../../labs/24-adversarial-red-teaming-at-scale/) — the implementation (~90-110 min)
- 📖 [Pattern 3 — Judge ensemble](../../learning-paths/06-evaluation-observability/patterns/03-judge-ensemble.md) — the ensemble scoring mechanism

Passing threshold: 6/8.

---

<details>
<summary><b>Question 1</b> — What's the orthogonal question?</summary>

**Answer**: The rest of Path 06 answers "is the system performing well on the queries users actually send?"; red-teaming answers "does the system fail safely on queries adversaries will send?". The two need the same orchestration substrate but cover orthogonal question spaces.

This framing is the central insight of the concept page. The earlier path treated red-teaming as Path 07 territory; Batch 38 brings the evaluation/observability dimension of red-teaming into Path 06 because it depends on the same eval datasets, judge ensembles, severity routing, and OTel substrate. Path 07 (when authored) will cover the complementary safety-policy authorship dimension.

</details>

<details>
<summary><b>Question 2</b> — Multi-turn manipulation patterns?</summary>

**Answer**: Crescendo and TAP. Crescendo builds benign rapport across early turns then pivots in a later turn; TAP is the algorithmic refinement variant where an attacker LLM iteratively refines based on the target's responses. Both require Module 7's threaded-evaluation infrastructure.

The concept page notes the 2026 industry shift: red-teaming used to mean adversarial prompts against a single model endpoint; in 2026, agents calling tools and MCP servers introduce failure modes that single-prompt scanners miss. Multi-turn manipulation is the canonical example.

</details>

<details>
<summary><b>Question 3</b> — Where does Pattern 3 plug in?</summary>

**Answer**: Step 4 (scoring). Single-judge is inadequate because adversarial scoring is high-stakes, high-variance, and the three-way disagreement structure is the most useful red-team signal — distinguishing the agent's clear failures from genuinely ambiguous boundary cases.

This is the canonical Pattern 3 use case: high-stakes scoring where the judge-ensemble's variance reduction outweighs the 3× cost. The split-verdict bucket specifically is where the ensemble outperforms any single judge — those are the cases that need human policy clarification.

</details>

<details>
<summary><b>Question 4</b> — Routing a unanimous-fail?</summary>

**Answer**: T3 confirmed-failure queue, with auto-paging on high-severity categories. Confirmed-fail traces become *candidates* for the regression set; promotion still requires explicit human review and approval.

This is the most operationally important distinction in the lab: unanimous-fail is a strong signal worth paging on, but it is NOT an instruction to auto-promote to the regression set. The lab's `RegressionSet.promote` requires `human_approved=True` as the explicit gate.

</details>

<details>
<summary><b>Question 5</b> — Why the human-approval gate?</summary>

**Answer**: Unanimous-fail traces include false positives, and the regression set's value comes from the curated human review notes attached to each entry. Auto-promotion converts the regression set from a curated artifact into a noisy alert log.

This is the central anti-pattern the lab models by what it does NOT do. The regression set is the permanent compounding artifact of a red-team program; removing the curation gate destroys its long-term value.

</details>

<details>
<summary><b>Question 6</b> — CI/CD-integrated tool choice?</summary>

**Answer**: Promptfoo. YAML-defined test configurations + `braintrustdata/eval-action` GitHub Action for PR-diff posting + 300,000+ developers in 2026 + the explicit "closest thing to Jest or Pytest for LLM applications" framing per Qaskills' Promptfoo guide.

The four-tool landscape table in the concept page tells you each tool's strongest fit; the CI/CD-integrated regression-testing fit is Promptfoo specifically. DeepTeam is best for OWASP coverage alignment; PyRIT for multi-modal + multi-turn; Garak for LLM provider scanning.

</details>

<details>
<summary><b>Question 7</b> — OWASP Top 10 and regulatory frameworks?</summary>

**Answer**: OWASP Top 10 is a security classification, not a compliance framework. Demonstrating coverage is strong evidence of a mature AI security program and satisfies adversarial testing requirements in NIST AI RMF Measure 2.6 and EU AI Act cybersecurity measures, but the regulatory frameworks require additional governance evidence (risk management plans, audit trails, conformity assessments) that OWASP coverage alone does not provide.

This precision matters in practice. Teams sometimes conflate "covered the OWASP Top 10" with "compliant" — they're related but not the same thing. The concept page Section 6 spells this out explicitly.

</details>

<details>
<summary><b>Question 8</b> — What's anti-scope?</summary>

**Answer**: Treating a unanimous-fail signal as an instruction to auto-deploy a content block, or claiming "100% prevention". Defensive patterns + threat models are in scope per the repo's SECURITY.md policy; weaponizable exploits are not. The taxonomy is not a substitute for domain-specific safety policy.

The concept page's anti-scope section is explicit about these limits. The lab models them by what it deliberately does NOT do: no auto-promotion, no auto-blocking, no "secure" binary verdict in the dashboard.

</details>
