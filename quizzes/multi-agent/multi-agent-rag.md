---
quiz_id: multi-agent-multi-agent-rag
title: "Multi-agent RAG: when it beats single-agent RAG, the four retrieval-decision rules, the four failure modes, and citation preservation discipline"
source:
  - concepts/multi-agent/multi-agent-rag.md
  - concepts/multi-agent/retriever-as-worker.md
  - labs/13-multi-agent-rag-from-scratch/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "Your application is a customer-support agent over a product manual. Every query is about the manual; every query needs retrieval. You're considering moving from single-agent RAG (Lab 06-08) to multi-agent RAG. Which framing is most accurate?"
    options:
      A: "Always move to multi-agent RAG — the supervisor pattern is strictly better."
      B: "Stay with single-agent RAG. Multi-agent RAG earns its place when deciding-to-retrieve is non-trivial, when multiple retrievals must be composed, or when retrieval precision justifies a critic. If every query needs retrieval and one retrieval per query suffices, the supervisor's routing decision is a no-op and adds pure overhead."
      C: "Move to multi-agent RAG with `MAX_REFINEMENT_CYCLES = 10` to maximize precision."
      D: "Use neither — switch to self-RAG."
    answer: B
    explanation: |
      The decision to retrieve is the value-add of multi-agent RAG.
      For workloads where retrieval is always-on and single, single-
      agent RAG is simpler, cheaper, and equivalent in quality. Adding
      a supervisor whose only job is "always retrieve" wastes an LLM
      call per query for a no-op decision. Option A overstates the
      change. Option C confuses critic refinement (a different layer)
      with retrieval routing, and a 10-cycle cap is replanning thrash
      by design. Option D is from a different problem space — self-
      RAG is training-time intervention; you'd need to fine-tune the
      model, which isn't a deployment choice for off-the-shelf LLMs.
    review:
      page: concepts/multi-agent/multi-agent-rag.md
      section: "When single-agent RAG is enough"

  - id: q2
    difficulty: easy
    question: "Your synthesizer is citing chunks as `[1]`, `[2]`, `[3]` instead of by `chunk_id`. You investigate and find the supervisor is summarizing the retriever's chunks into a 'findings' string before passing them to the synthesizer. What's the failure mode and what's the fix?"
    options:
      A: "Retrieval skip — the supervisor should retrieve more chunks. Fix: lower the retriever's relevance floor."
      B: "Citation drift — the supervisor is paraphrasing chunks into prose, losing the structured `chunk_id` and `source` fields. Fix: structural — supervisor passes the chunks envelope through to the synthesizer VERBATIM; synthesizer is told in its system prompt to cite by `chunk_id`. The supervisor's role is routing, not summarization."
      C: "Chunk drift — the synthesizer is paraphrasing beyond what chunks support. Fix: add Lab 11's critic."
      D: "Retrieval over-call — too many retrievals. Fix: stricter retrieve-skip rules."
    answer: B
    explanation: |
      This is the canonical multi-agent-RAG bug. The supervisor's job
      is to route, not summarize. Every reformatting step is a place
      citations can drop. The structural fix is the supervisor's
      `call_synthesizer` tool taking `chunks: list[dict]` (the raw
      envelope) and the synthesizer's prompt enforcing chunk_id
      citations. Option A is the wrong failure mode entirely — the
      retrieval succeeded; the loss is downstream. Option C is a
      different failure mode (synthesizer inventing claims). Option D
      is unrelated; over-call is about calling retrieve too often,
      not about what happens after.
    review:
      page: concepts/multi-agent/retriever-as-worker.md
      section: "Citation preservation discipline"

  - id: q3
    difficulty: medium
    question: "Lab 13's retriever returns chunks with a `score` field (the cross-encoder rerank score). The supervisor's system prompt explicitly tells the LLM NOT to reason about this score. Why?"
    options:
      A: "Because cross-encoder scores aren't probabilities; they're unbounded logits."
      B: "Because the supervisor doesn't need to evaluate retrieval quality — that's the retriever's job. The retriever already applied the relevance floor; chunks that come back in an `ok` envelope are usable by definition. If chunks aren't usable, the retriever returns `empty`. The supervisor reasoning about `score` would be doing the retriever's work over again, and badly (the LLM doesn't have the cross-encoder's training signal)."
      C: "Because the score field is a security risk."
      D: "Because the score field is randomly noisy and uninformative."
    answer: B
    explanation: |
      The separation of concerns matters. The retriever owns
      retrieval quality (it has the cross-encoder, the BM25 scores,
      the dense cosines, and the relevance floor). The supervisor
      owns routing decisions. Mixing the concerns produces a
      supervisor that "second-guesses" the retriever using a weaker
      signal (LLM judgment of an unbounded logit), which is strictly
      worse than trusting the retriever's envelope. Option A is true
      but doesn't answer "why hide it from the supervisor." Option C
      is invented. Option D is wrong — the score IS informative; it's
      just informative to the retriever, not the supervisor.
    review:
      page: concepts/multi-agent/retriever-as-worker.md
      section: "The retriever-worker contract"

  - id: q4
    difficulty: medium
    question: "You ask your multi-agent RAG system 'What year was Marie Curie born?' (a stable-knowledge question; your corpus is about agentic AI concepts). The supervisor calls `call_retriever` and gets `status='empty'`. What should the supervisor do next?"
    options:
      A: "Retry `call_retriever` with a reworded query like 'Marie Curie birth year' — the original query was too literal."
      B: "Surface 'the corpus doesn't cover this' and (optionally) answer from training data with a disclaimer. Do NOT retry. Rule 3 (one retrieval per distinct factual question) prevents retrieval thrash. The retrieval pipeline already does query rewriting internally; retrying from the supervisor level is doing the same work twice with worse signal."
      C: "Retry up to `MAX_REFINEMENT_CYCLES = 3` times until something comes back."
      D: "Hand off to Lab 12's planner for a multi-retrieval strategy."
    answer: B
    explanation: |
      The retrieve/skip framing matters here. Marie Curie's birth
      year is a stable-knowledge question; Rule 2 says the supervisor
      shouldn't have retrieved in the first place. But assuming it
      did, Rule 3 prevents retrieval thrash: retry with a reworded
      query is the LLM duplicating Lab 08's internal query rewriting
      with weaker signal. The action-hash dedup mechanism enforces
      this at the tool-dispatch level: identical retrieve args return
      `repeated_action`. Option A is the thrash pattern. Option C
      confuses refinement (different layer) with retrieval. Option D
      overengineers — the planner doesn't add anything for a question
      that isn't in the corpus.
    review:
      page: concepts/multi-agent/retriever-as-worker.md
      section: "Rule 3: One retrieval per distinct factual question"

  - id: q5
    difficulty: medium
    question: "Your multi-agent RAG system passes all retrieve/skip diagnostics, but evaluation shows the synthesizer occasionally produces ungrounded claims — claims that cite a real chunk but state things the chunk doesn't actually support. Which composition is the right next move?"
    options:
      A: "Add Lab 12's planner with parallel retrievals — more chunks will fix it."
      B: "Add Lab 11's critic-on-synthesis. The critic reads `(chunks, draft)` and flags every claim against the chunks; ungrounded claims trigger revision via bounded refinement (`MAX_REFINEMENT_CYCLES = 3`). This is the chunk-drift failure mode, and the critic is the structural mitigation."
      C: "Lower the relevance floor — more chunks will give the synthesizer more support."
      D: "Re-train the synthesizer model."
    answer: B
    explanation: |
      Chunk drift is exactly what critic-on-synthesis was designed
      for. The retrieval is fine (the chunks ARE cited; they just
      don't support the cited claims). The synthesizer is generating
      from training-data knowledge alongside the chunks. A critic
      checking every claim against the chunks catches this
      structurally. Option A treats a synthesis problem with more
      retrieval — orthogonal concerns. Option C makes retrieval less
      precise (more chunks, including less-relevant ones) which can
      make chunk drift WORSE because the synthesizer has more
      tempting context to draw from. Option D treats a prompt-design
      problem with model-design machinery; vastly overkill and
      typically infeasible.
    review:
      page: concepts/multi-agent/multi-agent-rag.md
      section: "Chunk drift"

  - id: q6
    difficulty: medium
    question: "Lab 13's retriever auto-detects v2 vs v3: if `context_cache.json` exists from a Lab 08 run, it uses v3 (contextual augmentation); otherwise v2. The detection also verifies that the cached chunk IDs match at least 90% of the rebuilt chunks. Why the 90% check?"
    options:
      A: "Because contextual cache files are large and the 90% threshold saves memory."
      B: "Because if the cached chunks were generated with different chunk parameters (different `TARGET_TOKENS` or `OVERLAP_TOKENS`), the chunk IDs don't match and v3 augmentation silently attaches the wrong context to chunks. The 90% check forces a fallback to v2 with a printed warning rather than producing silently corrupt retrieval."
      C: "Because Lab 08's cache is unreliable; the 90% threshold filters out spurious entries."
      D: "Because the cross-encoder has a 90% accuracy threshold."
    answer: B
    explanation: |
      This is a subtle composition bug that happens in real
      deployments. Lab 08's cache stores `chunk_id → contextual
      description`. If Lab 13 rebuilds chunks with even slightly
      different parameters, the IDs won't match — and a v3 pipeline
      using a stale cache will attach context to the wrong chunks, or
      to no chunks. The retrieval still runs, the answers still come
      back, but precision degrades silently. The 90% check forces
      either (a) consistency (in which case v3 is fine), or (b) fall
      back with a visible warning. Option A is invented. Option C
      misframes the cache as unreliable; the cache itself is fine,
      it's the parameter mismatch that's the issue. Option D
      conflates unrelated systems.
    review:
      page: labs/13-multi-agent-rag-from-scratch/README.md
      section: "What to watch for"

  - id: q7
    difficulty: hard
    question: "Which of the four multi-agent-RAG failure modes is hardest to detect from outside the system (i.e., looking only at the final answer)?"
    options:
      A: "Citation drift — citations are visible in the output."
      B: "Retrieval skip — outputs are sometimes confidently wrong, but you can't see what didn't get retrieved."
      C: "Chunk drift — citations are correct, claims are wrong, and verifying requires reading the chunks alongside the answer. The output looks polished and well-cited; nothing in the prose flags the disconnect."
      D: "Retrieval over-call — extra retrievals are visible in cost and latency."
    answer: C
    explanation: |
      All four failure modes are real, but only chunk drift produces
      outputs that look completely correct. Citations are present and
      point at real chunks; the prose reads naturally; only by
      reading the chunk text alongside the answer can you spot that
      claims aren't supported. Citation drift makes citations look
      wrong (visible). Retrieval skip produces confidently-wrong
      answers but the symptom is detectable via eval (corpus-grounded
      questions getting non-corpus answers). Retrieval over-call is
      visible in cost dashboards. Chunk drift hides in plain sight.
      That's why Lab 11's critic-on-synthesis is the standard
      mitigation: a structural check that doesn't depend on human
      detection.
    review:
      page: concepts/multi-agent/multi-agent-rag.md
      section: "Chunk drift"

  - id: q8
    difficulty: hard
    question: "Your retrieval evaluator wants to add a fallback: when corpus retrieval fails (status='empty'), automatically issue a web search instead. Which pattern best describes this design, and does Lab 13 implement it?"
    options:
      A: "Lab 13 implements this as part of the headline retriever-as-worker pattern."
      B: "This is CRAG (Corrective RAG, Yan et al. 2024) — a retrieval evaluator with corrective fallback. Lab 13 does NOT implement this; the concept page explains where CRAG sits relative to multi-agent RAG and that it solves a different design problem. Building it would be a worthwhile extension on top of Lab 13's pattern but isn't in the headline lab."
      C: "This is self-RAG (Asai et al. 2023), implemented in Lab 13's stretch section."
      D: "This is the planner-driven research pattern from Lab 12, with one fallback step."
    answer: B
    explanation: |
      CRAG is specifically the pattern of evaluating retrieval quality
      and triggering a corrective fallback (often web search). Lab 13
      mentions CRAG in the concept page's "when self-RAG / CRAG are
      the right pattern instead" section as a related-but-different
      design. Self-RAG is the training-time intervention; CRAG is the
      retrieval-evaluator-with-fallback. Lab 13's retriever returns
      `status='empty'` cleanly, which is the building block for CRAG,
      but the corrective fallback itself isn't implemented. Option A
      overstates Lab 13's scope. Option C confuses self-RAG with
      CRAG. Option D conflates planner-driven research (parallel
      retrievals) with corrective fallback (a different control flow).
    review:
      page: concepts/multi-agent/multi-agent-rag.md
      section: "When self-RAG / CRAG are the right pattern instead"
---

# Quiz: Multi-agent RAG

> 🟡 Intermediate · 8 questions · ~10 min · Passing: 6/8

Tests your grasp of when multi-agent RAG beats single-agent RAG, citation preservation across the retriever → supervisor → synthesizer handoff, the four retrieval-decision rules, the four multi-agent-RAG-specific failure modes, composition with Lab 11's critic and Lab 12's planner, and where self-RAG / CRAG fit (and don't) relative to the patterns Lab 13 builds.

If you're below 6/8, the answers point at specific sections of the two concept pages — use them as a re-read guide before Lab 13.

---

## Question 1

Your application is a customer-support agent over a product manual. Every query is about the manual; every query needs retrieval. You're considering moving from single-agent RAG (Lab 06-08) to multi-agent RAG. Which framing is most accurate?

- A. Always move to multi-agent RAG — the supervisor pattern is strictly better.
- B. Stay with single-agent RAG. Multi-agent RAG earns its place when deciding-to-retrieve is non-trivial, when multiple retrievals must be composed, or when retrieval precision justifies a critic. If every query needs retrieval and one retrieval per query suffices, the supervisor's routing decision is a no-op and adds pure overhead.
- C. Move to multi-agent RAG with `MAX_REFINEMENT_CYCLES = 10` to maximize precision.
- D. Use neither — switch to self-RAG.

<details>
<summary>Reveal answer</summary>

**B.**

The decision to retrieve is the value-add of multi-agent RAG. For workloads where retrieval is always-on and single, single-agent RAG is simpler, cheaper, and equivalent in quality. Adding a supervisor whose only job is "always retrieve" wastes an LLM call per query for a no-op decision. Option A overstates the change. Option C confuses critic refinement (a different layer) with retrieval routing, and a 10-cycle cap is replanning thrash by design. Option D is from a different problem space — self-RAG is training-time intervention; you'd need to fine-tune the model.

Review: [`concepts/multi-agent/multi-agent-rag.md`](../../concepts/multi-agent/multi-agent-rag.md#when-single-agent-rag-is-enough) — "When single-agent RAG is enough".

</details>

---

## Question 2

Your synthesizer is citing chunks as `[1]`, `[2]`, `[3]` instead of by `chunk_id`. You investigate and find the supervisor is summarizing the retriever's chunks into a "findings" string before passing them to the synthesizer. What's the failure mode and what's the fix?

- A. Retrieval skip — the supervisor should retrieve more chunks. Fix: lower the retriever's relevance floor.
- B. Citation drift — the supervisor is paraphrasing chunks into prose, losing the structured `chunk_id` and `source` fields. Fix: structural — supervisor passes the chunks envelope through to the synthesizer VERBATIM; synthesizer is told in its system prompt to cite by `chunk_id`. The supervisor's role is routing, not summarization.
- C. Chunk drift — the synthesizer is paraphrasing beyond what chunks support. Fix: add Lab 11's critic.
- D. Retrieval over-call — too many retrievals. Fix: stricter retrieve-skip rules.

<details>
<summary>Reveal answer</summary>

**B.**

This is the canonical multi-agent-RAG bug. The supervisor's job is to route, not summarize. Every reformatting step is a place citations can drop. The structural fix is the supervisor's `call_synthesizer` tool taking `chunks: list[dict]` (the raw envelope) and the synthesizer's prompt enforcing chunk_id citations. Option A is the wrong failure mode entirely — the retrieval succeeded; the loss is downstream. Option C is a different failure mode (synthesizer inventing claims). Option D is unrelated.

Review: [`concepts/multi-agent/retriever-as-worker.md`](../../concepts/multi-agent/retriever-as-worker.md#citation-preservation-discipline) — "Citation preservation discipline".

</details>

---

## Question 3

Lab 13's retriever returns chunks with a `score` field (the cross-encoder rerank score). The supervisor's system prompt explicitly tells the LLM NOT to reason about this score. Why?

- A. Because cross-encoder scores aren't probabilities; they're unbounded logits.
- B. Because the supervisor doesn't need to evaluate retrieval quality — that's the retriever's job. The retriever already applied the relevance floor; chunks that come back in an `ok` envelope are usable by definition. If chunks aren't usable, the retriever returns `empty`. The supervisor reasoning about `score` would be doing the retriever's work over again, and badly (the LLM doesn't have the cross-encoder's training signal).
- C. Because the score field is a security risk.
- D. Because the score field is randomly noisy and uninformative.

<details>
<summary>Reveal answer</summary>

**B.**

The separation of concerns matters. The retriever owns retrieval quality (it has the cross-encoder, the BM25 scores, the dense cosines, and the relevance floor). The supervisor owns routing decisions. Mixing the concerns produces a supervisor that "second-guesses" the retriever using a weaker signal (LLM judgment of an unbounded logit), which is strictly worse than trusting the retriever's envelope. Option A is true but doesn't answer "why hide it from the supervisor." Option C is invented. Option D is wrong — the score IS informative; it's just informative to the retriever, not the supervisor.

Review: [`concepts/multi-agent/retriever-as-worker.md`](../../concepts/multi-agent/retriever-as-worker.md#the-retriever-worker-contract) — "The retriever-worker contract".

</details>

---

## Question 4

You ask your multi-agent RAG system "What year was Marie Curie born?" (a stable-knowledge question; your corpus is about agentic AI concepts). The supervisor calls `call_retriever` and gets `status='empty'`. What should the supervisor do next?

- A. Retry `call_retriever` with a reworded query like "Marie Curie birth year" — the original query was too literal.
- B. Surface "the corpus doesn't cover this" and (optionally) answer from training data with a disclaimer. Do NOT retry. Rule 3 (one retrieval per distinct factual question) prevents retrieval thrash. The retrieval pipeline already does query rewriting internally; retrying from the supervisor level is doing the same work twice with worse signal.
- C. Retry up to `MAX_REFINEMENT_CYCLES = 3` times until something comes back.
- D. Hand off to Lab 12's planner for a multi-retrieval strategy.

<details>
<summary>Reveal answer</summary>

**B.**

The retrieve/skip framing matters here. Marie Curie's birth year is a stable-knowledge question; Rule 2 says the supervisor shouldn't have retrieved in the first place. But assuming it did, Rule 3 prevents retrieval thrash: retry with a reworded query is the LLM duplicating Lab 08's internal query rewriting with weaker signal. The action-hash dedup mechanism enforces this at the tool-dispatch level: identical retrieve args return `repeated_action`. Option A is the thrash pattern. Option C confuses refinement (different layer) with retrieval. Option D overengineers.

Review: [`concepts/multi-agent/retriever-as-worker.md`](../../concepts/multi-agent/retriever-as-worker.md#rule-3-one-retrieval-per-distinct-factual-question) — "Rule 3: One retrieval per distinct factual question".

</details>

---

## Question 5

Your multi-agent RAG system passes all retrieve/skip diagnostics, but evaluation shows the synthesizer occasionally produces ungrounded claims — claims that cite a real chunk but state things the chunk doesn't actually support. Which composition is the right next move?

- A. Add Lab 12's planner with parallel retrievals — more chunks will fix it.
- B. Add Lab 11's critic-on-synthesis. The critic reads `(chunks, draft)` and flags every claim against the chunks; ungrounded claims trigger revision via bounded refinement (`MAX_REFINEMENT_CYCLES = 3`). This is the chunk-drift failure mode, and the critic is the structural mitigation.
- C. Lower the relevance floor — more chunks will give the synthesizer more support.
- D. Re-train the synthesizer model.

<details>
<summary>Reveal answer</summary>

**B.**

Chunk drift is exactly what critic-on-synthesis was designed for. The retrieval is fine (the chunks ARE cited; they just don't support the cited claims). The synthesizer is generating from training-data knowledge alongside the chunks. A critic checking every claim against the chunks catches this structurally. Option A treats a synthesis problem with more retrieval — orthogonal concerns. Option C makes retrieval less precise (more chunks, including less-relevant ones) which can make chunk drift WORSE. Option D is vastly overkill.

Review: [`concepts/multi-agent/multi-agent-rag.md`](../../concepts/multi-agent/multi-agent-rag.md#chunk-drift) — "Chunk drift".

</details>

---

## Question 6

Lab 13's retriever auto-detects v2 vs v3: if `context_cache.json` exists from a Lab 08 run, it uses v3 (contextual augmentation); otherwise v2. The detection also verifies that the cached chunk IDs match at least 90% of the rebuilt chunks. Why the 90% check?

- A. Because contextual cache files are large and the 90% threshold saves memory.
- B. Because if the cached chunks were generated with different chunk parameters (different `TARGET_TOKENS` or `OVERLAP_TOKENS`), the chunk IDs don't match and v3 augmentation silently attaches the wrong context to chunks. The 90% check forces a fallback to v2 with a printed warning rather than producing silently corrupt retrieval.
- C. Because Lab 08's cache is unreliable; the 90% threshold filters out spurious entries.
- D. Because the cross-encoder has a 90% accuracy threshold.

<details>
<summary>Reveal answer</summary>

**B.**

This is a subtle composition bug that happens in real deployments. Lab 08's cache stores `chunk_id → contextual description`. If Lab 13 rebuilds chunks with even slightly different parameters, the IDs won't match — and a v3 pipeline using a stale cache will attach context to the wrong chunks, or to no chunks. The retrieval still runs, the answers still come back, but precision degrades silently. The 90% check forces either (a) consistency, or (b) fall back with a visible warning. Option A is invented. Option C misframes the cache as unreliable. Option D conflates unrelated systems.

Review: [`labs/13-multi-agent-rag-from-scratch/README.md`](../../labs/13-multi-agent-rag-from-scratch/README.md#what-to-watch-for) — "What to watch for".

</details>

---

## Question 7

Which of the four multi-agent-RAG failure modes is hardest to detect from outside the system (i.e., looking only at the final answer)?

- A. Citation drift — citations are visible in the output.
- B. Retrieval skip — outputs are sometimes confidently wrong, but you can't see what didn't get retrieved.
- C. Chunk drift — citations are correct, claims are wrong, and verifying requires reading the chunks alongside the answer. The output looks polished and well-cited; nothing in the prose flags the disconnect.
- D. Retrieval over-call — extra retrievals are visible in cost and latency.

<details>
<summary>Reveal answer</summary>

**C.**

All four failure modes are real, but only chunk drift produces outputs that look completely correct. Citations are present and point at real chunks; the prose reads naturally; only by reading the chunk text alongside the answer can you spot that claims aren't supported. Citation drift makes citations look wrong (visible). Retrieval skip produces confidently-wrong answers but the symptom is detectable via eval. Retrieval over-call is visible in cost dashboards. Chunk drift hides in plain sight. That's why Lab 11's critic-on-synthesis is the standard mitigation: a structural check that doesn't depend on human detection.

Review: [`concepts/multi-agent/multi-agent-rag.md`](../../concepts/multi-agent/multi-agent-rag.md#chunk-drift) — "Chunk drift".

</details>

---

## Question 8

Your retrieval evaluator wants to add a fallback: when corpus retrieval fails (status='empty'), automatically issue a web search instead. Which pattern best describes this design, and does Lab 13 implement it?

- A. Lab 13 implements this as part of the headline retriever-as-worker pattern.
- B. This is CRAG (Corrective RAG, Yan et al. 2024) — a retrieval evaluator with corrective fallback. Lab 13 does NOT implement this; the concept page explains where CRAG sits relative to multi-agent RAG and that it solves a different design problem. Building it would be a worthwhile extension on top of Lab 13's pattern but isn't in the headline lab.
- C. This is self-RAG (Asai et al. 2023), implemented in Lab 13's stretch section.
- D. This is the planner-driven research pattern from Lab 12, with one fallback step.

<details>
<summary>Reveal answer</summary>

**B.**

CRAG is specifically the pattern of evaluating retrieval quality and triggering a corrective fallback (often web search). Lab 13 mentions CRAG in the concept page's "when self-RAG / CRAG are the right pattern instead" section as a related-but-different design. Self-RAG is the training-time intervention; CRAG is the retrieval-evaluator-with-fallback. Lab 13's retriever returns `status='empty'` cleanly, which is the building block for CRAG, but the corrective fallback itself isn't implemented. Option A overstates Lab 13's scope. Option C confuses self-RAG with CRAG. Option D conflates planner-driven research with corrective fallback.

Review: [`concepts/multi-agent/multi-agent-rag.md`](../../concepts/multi-agent/multi-agent-rag.md#when-self-rag--crag-are-the-right-pattern-instead) — "When self-RAG / CRAG are the right pattern instead".

</details>

---

## Scoring

| Score | Interpretation |
|---|---|
| 8/8 | Strong grasp. Move on to Lab 13 (or skip ahead if you've already built it). |
| 6-7/8 | Good. Re-read any concept-page sections flagged in the questions you missed. |
| 4-5/8 | Re-read both concept pages before attempting Lab 13. |
| < 4/8 | Re-do Labs 06-08 and Lab 10 first — Lab 13 composes retrieval with the supervisor pattern, and gaps here usually trace back to weak foundations in one or the other. |
