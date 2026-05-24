---
quiz_id: agentic-rag-retrieval-strategies
title: "Retrieval strategies, hybrid search, and reranking"
source:
  - concepts/rag/retrieval-strategies.md
  - concepts/rag/hybrid-search.md
  - concepts/rag/reranking.md
  - labs/07-retrieval-strategies-and-reranking/
length_minutes: 9
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "Your RAG pipeline has a cross-encoder reranker at the end. Your bi-encoder retrieves `top_k=5` candidates and the reranker picks `top_k=5` from those. Why is the answer quality barely better than the bi-encoder alone?"
    options:
      A: "Cross-encoders are worse than bi-encoders on small candidate sets; you should use a larger reranker model."
      B: "The reranker can only reorder candidates it's given. With `candidate_k=5` and `final_k=5`, the reranker has nothing to reach for outside the bi-encoder's choices. Standard practice is `candidate_k=30-50` for `final_k=5`."
      C: "Cross-encoders need a minimum batch size of 32 to produce meaningful scores."
      D: "Reranking only helps when the bi-encoder uses a smaller model than the reranker."
    answer: B
    explanation: |
      Reranking is a *precision* improvement on a fixed *recall* set.
      Whatever the bi-encoder missed at the candidate stage is invisible
      to the reranker. The standard ratio is roughly 5-10× more
      candidates than the final top-k. With `candidate_k=5, final_k=5`
      you've made the reranker run for nothing — its only job is to
      reorder the five candidates the bi-encoder already chose.
    review:
      page: concepts/rag/reranking.md
      section: "A common misconception"

  - id: q2
    difficulty: easy
    question: "Which retrieval failure mode is BM25 *worst* at handling, and dense retrieval (e.g. MiniLM bi-encoder) *best* at handling?"
    options:
      A: "Queries with rare technical terms or exact codes — BM25 misses these because they're rare."
      B: "Paraphrased queries — the query uses different words than the chunk does, but the meaning matches. BM25 can't see the semantic match; a bi-encoder can."
      C: "Short queries — BM25 needs at least 10-15 query tokens to score meaningfully."
      D: "Queries against very large corpora — BM25 scales poorly past 10K documents."
    answer: B
    explanation: |
      BM25 sees tokens, not meaning. If the query uses synonyms the
      chunk doesn't ("automobile" vs "car", "send messages between
      agents" vs "A2A protocols"), BM25 finds zero match. Dense
      retrieval embeds both into roughly the same semantic
      neighborhood and finds the connection.
      A is the opposite of true — BM25 is *strongest* on rare-term
      queries because rare terms get high IDF. C and D are mostly false:
      BM25 handles short queries fine and scales to hundreds of
      millions of documents in real search engines (Elasticsearch).
    review:
      page: concepts/rag/hybrid-search.md
      section: "What BM25 actually does"

  - id: q3
    difficulty: medium
    question: "Reciprocal Rank Fusion (RRF) uses the formula `score(c) = Σ 1 / (k + rank_i(c))` summed over each retriever's rank for chunk `c`. Why is the constant `k=60` such a robust default?"
    options:
      A: "The Cormack et al. (2009) paper showed `k=60` empirically across many retrieval benchmarks. The denominator damps the contribution of low-ranked chunks (rank 100's contribution is `1/160 ≈ 0.006`) so a single retriever's tail doesn't dominate, while keeping enough sensitivity at the top of the ranking. Tuning `k` rarely pays for the effort."
      B: "`k=60` corresponds to the maximum context length most LLMs support, so the formula naturally normalizes for prompt-window constraints."
      C: "The value 60 is computed from the harmonic mean of all retrievers' precision-at-10 scores."
      D: "RRF was originally designed for 60-document candidate sets, and the constant matches that."
    answer: A
    explanation: |
      `k=60` is from the original RRF paper (Cormack, Clarke & Büttcher,
      SIGIR 2009). It's robust because of two properties:
      (1) the denominator dampens low-rank tails — a chunk at rank 100
      contributes only `1/(60+100) ≈ 0.006` — so noise doesn't
      accumulate; (2) the top-of-ranking gradient is meaningful —
      rank 1 contributes `1/61 ≈ 0.016`, rank 5 contributes `1/65 ≈ 0.0154`.
      The constant has held up across many corpora; tuning it is
      one of the lowest-yield interventions in retrieval. B, C, and D
      are fabrications.
    review:
      page: concepts/rag/hybrid-search.md
      section: "How to combine them"

  - id: q4
    difficulty: medium
    question: "Your top-5 retrieval for the query 'what is the agent loop' returns five chunks all from `01-agent-loop.md` — different chunks of the same document. What's the right fix, and what's the wrong fix?"
    options:
      A: "Right: lower MIN_SIMILARITY to admit more chunks. Wrong: add a reranker."
      B: "Right: switch to BM25. Wrong: use MMR diversification."
      C: "Right: add MMR diversification (e.g. `λ=0.7`) so the top-k balances relevance against redundancy with already-selected chunks. Wrong: just lower `top_k` to 1 (you lose context the agent could use)."
      D: "Right: increase `top_k` to 20. Wrong: anything involving reranking — rerankers can't diversify."
    answer: C
    explanation: |
      This is the textbook MMR case — a broad query maps to one cluster
      of similar chunks. MMR (Carbonell & Goldstein, 1998) penalizes
      candidates similar to already-selected ones. `λ=0.7` is a gentle
      default that keeps the top-1 unchanged but spreads the next
      few across different documents. Lowering `top_k=1` "fixes" the
      redundancy by losing the diversity you actually wanted. A is
      wrong because lowering the similarity floor is unrelated.
    review:
      page: concepts/rag/retrieval-strategies.md
      section: "Knob 3 — MMR (Maximal Marginal Relevance)"

  - id: q5
    difficulty: medium
    question: "Why is a cross-encoder unsuitable as a *primary retriever* (used directly over the whole corpus) but well-suited as a *reranker* (used on a small candidate set)?"
    options:
      A: "Cross-encoders are trained on different data than bi-encoders, so they only work on documents matching their training distribution."
      B: "Bi-encoders embed query and chunk independently and can precompute the chunk side; retrieval is a fast dot-product over the index. Cross-encoders require a full forward pass per (query, chunk) pair with no precomputation possible, which is fine for 30 candidates but intractable for 100K."
      C: "Cross-encoders only return binary relevance scores, so they can't produce a fine-grained ranking."
      D: "Cross-encoders can't handle documents longer than 128 tokens."
    answer: B
    explanation: |
      The architectural difference is precomputation. A bi-encoder
      embeds each chunk once at index time; query-time is a single
      query embedding plus a dot product against the index — O(N)
      cheap operations. A cross-encoder takes (query, chunk) jointly
      and runs the full transformer — every pair requires its own
      forward pass, no chunk-side caching possible. At 50ms per pair
      on CPU, 100K chunks = 5000 seconds per query. 30 candidates =
      1.5 seconds. The cross-encoder pays for its precision with this
      cost, which is why the retrieve-then-rerank cascade exists.
      C and D are false; A misrepresents the issue.
    review:
      page: concepts/rag/reranking.md
      section: "What a cross-encoder does differently"

  - id: q6
    difficulty: medium
    question: "Lab 06 used `MIN_SIMILARITY=0.30` against normalized MiniLM cosines. Lab 07's `search_corpus_v2` sets `MIN_SIMILARITY=0.0` against cross-encoder *logits*. Why doesn't the same floor value transfer between them?"
    options:
      A: "0.30 was a typo in Lab 06; both should have been 0.0."
      B: "Score scales are model- and architecture-specific. Cosine of normalized embeddings lives in `[-1, 1]` with sensible hits clustering around `0.3-0.8`. Cross-encoder logits are unbounded and typically span roughly `[-15, +15]` — different scale entirely. A floor calibrated for one says nothing about the other."
      C: "Lab 06 floored on similarity; Lab 07 floored on rerank rank position, not score."
      D: "Cross-encoders don't need a floor because they never produce false positives."
    answer: B
    explanation: |
      This is a common gotcha when bolting on a new retrieval stage.
      Cosine similarity ∈ [-1, 1]; sensible matches are 0.3-0.8.
      Cross-encoder logits ∈ roughly [-15, +15]; positive ≈ relevant,
      negative ≈ irrelevant. RRF scores ∈ ~[0, 0.033]. The floor
      must be calibrated for whatever score the pipeline returns. The
      lab notes this explicitly and uses 0.0 as a default-for-logits
      starting point — you should re-calibrate it on your own corpus
      using the on-corpus vs off-corpus distribution method.
    review:
      page: concepts/rag/retrieval-strategies.md
      section: "Knob 2 — score floors"

  - id: q7
    difficulty: hard
    question: "You're building a RAG system for an internal codebase wiki — lots of technical terms (function names, error codes, API endpoints). The bi-encoder retrieval is missing exact-match queries while finding good results on conceptual queries. Cost is the constraint: only one new retrieval intervention. Which gives the best return?"
    options:
      A: "Add a cross-encoder reranker on top of the existing bi-encoder."
      B: "Switch the bi-encoder to a larger embedding model (e.g. `bge-large` instead of MiniLM)."
      C: "Add BM25 alongside the bi-encoder and fuse via RRF — hybrid search. Bi-encoder still handles the conceptual queries; BM25 catches the proper-noun and exact-term queries dense retrieval is fuzzy on. The two retrievers' failure modes are inverses, so the combined system has access to both winners."
      D: "Add MMR diversification with `λ=0.5`."
    answer: C
    explanation: |
      This is exactly the workload hybrid search exists for. The
      symptom (good on conceptual, weak on exact-match) names BM25 as
      the missing piece. Reranking (A) would tighten the precision
      *within* whatever the bi-encoder already returned — but if the
      right chunk isn't in the bi-encoder's top-30, no reranker can
      surface it. A larger bi-encoder (B) improves cosines uniformly
      but doesn't solve the architectural fuzzy-match weakness on
      proper nouns. MMR (D) is unrelated. Real-world studies (BEIR,
      Sciavolino et al. 2021) consistently show hybrid retrieval
      lifts technical-corpus quality by 5-15% over dense alone.
    review:
      page: concepts/rag/hybrid-search.md
      section: "Why combine BM25 and dense?"

  - id: q8
    difficulty: hard
    question: "Your validation set shows the bi-encoder finds the correct chunk in its top-50 for 95% of queries, but the correct chunk's average rank is ~12. Adding a reranker brings the average rank to ~2. Then you swap the bi-encoder for a larger embedding model; the correct chunk is now in top-50 for 97% of queries, with average rank ~8 *without* the reranker. Should you keep the reranker?"
    options:
      A: "No — the larger bi-encoder made the reranker redundant. Drop it to save compute."
      B: "Yes — but only if your latency budget allows. The bi-encoder upgrade improved *recall* (95% → 97% in top-50) and *moved good chunks closer to the top* (rank 12 → rank 8), but the cross-encoder is doing different work: it adds query-document interaction signal that pure embedding similarity can't capture. Rerank latency and recall improvement are orthogonal; you'd verify by running both with the reranker on and measuring whether rank-2 holds or improves."
      C: "No — recall above 95% indicates retrieval is saturated, and reranker overhead becomes pure cost."
      D: "Yes — rerankers always strictly improve quality; never remove one once added."
    answer: B
    explanation: |
      The two interventions improve different things. The bi-encoder
      upgrade improved recall (more correct chunks reach the candidate
      set) and moved them closer to the top. The reranker exploits a
      different signal — query-document interactions a bi-encoder
      cannot see. Even after the upgrade, the cross-encoder's mean
      rank of ~2 on the prior setup tells you the interaction signal
      was worth ~6 positions; that signal hasn't gone away. Run the
      full pipeline (upgraded bi-encoder + reranker) and measure. If
      it lands at rank 1.5 you keep the reranker; if it lands at the
      same rank ~8 with no improvement, you drop it. Don't reason from
      first principles when you can run the measurement. D is also
      wrong — rerankers don't *always* improve; on already-near-perfect
      retrieval (small focused corpora) they can be no-ops.
    review:
      page: concepts/rag/reranking.md
      section: "When reranking helps the most"
---

# Quiz: Retrieval strategies, hybrid search, and reranking

> 🟡 Mixed difficulty · ⏱ ~9 minutes · 8 questions, single-select

This quiz checks understanding of the three retrieval-quality concept pages and the patterns from Lab 07. Read all three concept pages and finish at least steps 1-7 of the lab before attempting.

**Format.** Each question shows four options. Click the `<details>` block to reveal the answer and full explanation. Aim for 6/8 to feel solid; below that, the linked review section is the place to revisit.

---

## Q1 — Reranker `candidate_k`

Your RAG pipeline has a cross-encoder reranker at the end. Your bi-encoder retrieves `top_k=5` candidates and the reranker picks `top_k=5` from those. Why is the answer quality barely better than the bi-encoder alone?

A. Cross-encoders are worse than bi-encoders on small candidate sets; you should use a larger reranker model.  
B. The reranker can only reorder candidates it's given. With `candidate_k=5` and `final_k=5`, the reranker has nothing to reach for outside the bi-encoder's choices. Standard practice is `candidate_k=30-50` for `final_k=5`.  
C. Cross-encoders need a minimum batch size of 32 to produce meaningful scores.  
D. Reranking only helps when the bi-encoder uses a smaller model than the reranker.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

Reranking is a *precision* improvement on a fixed *recall* set. Whatever the bi-encoder missed at the candidate stage is invisible to the reranker. The standard ratio is roughly 5-10× more candidates than the final top-k. With `candidate_k=5, final_k=5` you've made the reranker run for nothing — its only job is to reorder the five candidates the bi-encoder already chose.

Review: [`concepts/rag/reranking.md` § A common misconception](../../concepts/rag/reranking.md#a-common-misconception)
</details>

---

## Q2 — Where BM25 and dense disagree

Which retrieval failure mode is BM25 *worst* at handling, and dense retrieval (e.g. MiniLM bi-encoder) *best* at handling?

A. Queries with rare technical terms or exact codes — BM25 misses these because they're rare.  
B. Paraphrased queries — the query uses different words than the chunk does, but the meaning matches. BM25 can't see the semantic match; a bi-encoder can.  
C. Short queries — BM25 needs at least 10-15 query tokens to score meaningfully.  
D. Queries against very large corpora — BM25 scales poorly past 10K documents.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

BM25 sees tokens, not meaning. If the query uses synonyms the chunk doesn't ("automobile" vs "car", "send messages between agents" vs "A2A protocols"), BM25 finds zero match. Dense retrieval embeds both into roughly the same semantic neighborhood and finds the connection.

A is the opposite of true — BM25 is *strongest* on rare-term queries because rare terms get high IDF. C and D are mostly false: BM25 handles short queries fine and scales to hundreds of millions of documents in real search engines (Elasticsearch).

Review: [`concepts/rag/hybrid-search.md` § What BM25 actually does](../../concepts/rag/hybrid-search.md#what-bm25-actually-does)
</details>

---

## Q3 — Why `k=60` in RRF

Reciprocal Rank Fusion (RRF) uses the formula `score(c) = Σ 1 / (k + rank_i(c))` summed over each retriever's rank for chunk `c`. Why is the constant `k=60` such a robust default?

A. The Cormack et al. (2009) paper showed `k=60` empirically across many retrieval benchmarks. The denominator damps the contribution of low-ranked chunks (rank 100's contribution is `1/160 ≈ 0.006`) so a single retriever's tail doesn't dominate, while keeping enough sensitivity at the top of the ranking. Tuning `k` rarely pays for the effort.  
B. `k=60` corresponds to the maximum context length most LLMs support, so the formula naturally normalizes for prompt-window constraints.  
C. The value 60 is computed from the harmonic mean of all retrievers' precision-at-10 scores.  
D. RRF was originally designed for 60-document candidate sets, and the constant matches that.

<details>
<summary>Answer & explanation</summary>

**Answer: A.**

`k=60` is from the original RRF paper (Cormack, Clarke & Büttcher, SIGIR 2009). It's robust because of two properties:

1. The denominator dampens low-rank tails — a chunk at rank 100 contributes only `1/(60+100) ≈ 0.006` — so noise doesn't accumulate.
2. The top-of-ranking gradient is meaningful — rank 1 contributes `1/61 ≈ 0.0164`, rank 5 contributes `1/65 ≈ 0.0154`.

The constant has held up across many corpora; tuning it is one of the lowest-yield interventions in retrieval. B, C, and D are fabrications.

Review: [`concepts/rag/hybrid-search.md` § How to combine them](../../concepts/rag/hybrid-search.md#how-to-combine-them)
</details>

---

## Q4 — When top-5 fills with near-duplicates

Your top-5 retrieval for the query "what is the agent loop" returns five chunks all from `01-agent-loop.md` — different chunks of the same document. What's the right fix, and what's the wrong fix?

A. Right: lower MIN_SIMILARITY to admit more chunks. Wrong: add a reranker.  
B. Right: switch to BM25. Wrong: use MMR diversification.  
C. Right: add MMR diversification (e.g. `λ=0.7`) so the top-k balances relevance against redundancy with already-selected chunks. Wrong: just lower `top_k` to 1 (you lose context the agent could use).  
D. Right: increase `top_k` to 20. Wrong: anything involving reranking — rerankers can't diversify.

<details>
<summary>Answer & explanation</summary>

**Answer: C.**

This is the textbook MMR case — a broad query maps to one cluster of similar chunks. MMR (Carbonell & Goldstein, 1998) penalizes candidates similar to already-selected ones. `λ=0.7` is a gentle default that keeps the top-1 unchanged but spreads the next few across different documents. Lowering `top_k=1` "fixes" the redundancy by losing the diversity you actually wanted. A is wrong because lowering the similarity floor is unrelated.

Review: [`concepts/rag/retrieval-strategies.md` § Knob 3 — MMR](../../concepts/rag/retrieval-strategies.md#knob-3--mmr-maximal-marginal-relevance)
</details>

---

## Q5 — Bi-encoder vs cross-encoder architecture

Why is a cross-encoder unsuitable as a *primary retriever* (used directly over the whole corpus) but well-suited as a *reranker* (used on a small candidate set)?

A. Cross-encoders are trained on different data than bi-encoders, so they only work on documents matching their training distribution.  
B. Bi-encoders embed query and chunk independently and can precompute the chunk side; retrieval is a fast dot-product over the index. Cross-encoders require a full forward pass per (query, chunk) pair with no precomputation possible, which is fine for 30 candidates but intractable for 100K.  
C. Cross-encoders only return binary relevance scores, so they can't produce a fine-grained ranking.  
D. Cross-encoders can't handle documents longer than 128 tokens.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

The architectural difference is precomputation. A bi-encoder embeds each chunk once at index time; query-time is a single query embedding plus a dot product against the index — O(N) cheap operations. A cross-encoder takes (query, chunk) jointly and runs the full transformer — every pair requires its own forward pass, no chunk-side caching possible.

At 50ms per pair on CPU, 100K chunks = 5000 seconds per query. 30 candidates = 1.5 seconds. The cross-encoder pays for its precision with this cost, which is why the retrieve-then-rerank cascade exists.

C and D are false; A misrepresents the issue.

Review: [`concepts/rag/reranking.md` § What a cross-encoder does differently](../../concepts/rag/reranking.md#what-a-cross-encoder-does-differently)
</details>

---

## Q6 — Score scales don't transfer

Lab 06 used `MIN_SIMILARITY=0.30` against normalized MiniLM cosines. Lab 07's `search_corpus_v2` sets `MIN_SIMILARITY=0.0` against cross-encoder *logits*. Why doesn't the same floor value transfer between them?

A. 0.30 was a typo in Lab 06; both should have been 0.0.  
B. Score scales are model- and architecture-specific. Cosine of normalized embeddings lives in `[-1, 1]` with sensible hits clustering around `0.3-0.8`. Cross-encoder logits are unbounded and typically span roughly `[-15, +15]` — different scale entirely. A floor calibrated for one says nothing about the other.  
C. Lab 06 floored on similarity; Lab 07 floored on rerank rank position, not score.  
D. Cross-encoders don't need a floor because they never produce false positives.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

This is a common gotcha when bolting on a new retrieval stage. Cosine similarity ∈ [-1, 1]; sensible matches are 0.3-0.8. Cross-encoder logits ∈ roughly [-15, +15]; positive ≈ relevant, negative ≈ irrelevant. RRF scores ∈ ~[0, 0.033]. The floor must be calibrated for whatever score the pipeline returns. The lab notes this explicitly and uses 0.0 as a default-for-logits starting point — you should re-calibrate it on your own corpus using the on-corpus vs off-corpus distribution method.

Review: [`concepts/rag/retrieval-strategies.md` § Knob 2 — score floors](../../concepts/rag/retrieval-strategies.md#knob-2--score-floors)
</details>

---

## Q7 — Picking the right intervention for a workload

You're building a RAG system for an internal codebase wiki — lots of technical terms (function names, error codes, API endpoints). The bi-encoder retrieval is missing exact-match queries while finding good results on conceptual queries. Cost is the constraint: only one new retrieval intervention. Which gives the best return?

A. Add a cross-encoder reranker on top of the existing bi-encoder.  
B. Switch the bi-encoder to a larger embedding model (e.g. `bge-large` instead of MiniLM).  
C. Add BM25 alongside the bi-encoder and fuse via RRF — hybrid search. Bi-encoder still handles the conceptual queries; BM25 catches the proper-noun and exact-term queries dense retrieval is fuzzy on. The two retrievers' failure modes are inverses, so the combined system has access to both winners.  
D. Add MMR diversification with `λ=0.5`.

<details>
<summary>Answer & explanation</summary>

**Answer: C.**

This is exactly the workload hybrid search exists for. The symptom (good on conceptual, weak on exact-match) names BM25 as the missing piece.

Reranking (A) would tighten the precision *within* whatever the bi-encoder already returned — but if the right chunk isn't in the bi-encoder's top-30, no reranker can surface it. A larger bi-encoder (B) improves cosines uniformly but doesn't solve the architectural fuzzy-match weakness on proper nouns. MMR (D) is unrelated.

Real-world studies (BEIR, Sciavolino et al. 2021) consistently show hybrid retrieval lifts technical-corpus quality by 5-15% over dense alone.

Review: [`concepts/rag/hybrid-search.md` § Why combine BM25 and dense?](../../concepts/rag/hybrid-search.md#why-combine-bm25-and-dense)
</details>

---

## Q8 — Reasoning about stacked improvements

Your validation set shows the bi-encoder finds the correct chunk in its top-50 for 95% of queries, but the correct chunk's average rank is ~12. Adding a reranker brings the average rank to ~2. Then you swap the bi-encoder for a larger embedding model; the correct chunk is now in top-50 for 97% of queries, with average rank ~8 *without* the reranker. Should you keep the reranker?

A. No — the larger bi-encoder made the reranker redundant. Drop it to save compute.  
B. Yes — but only if your latency budget allows. The bi-encoder upgrade improved *recall* (95% → 97% in top-50) and *moved good chunks closer to the top* (rank 12 → rank 8), but the cross-encoder is doing different work: it adds query-document interaction signal that pure embedding similarity can't capture. Rerank latency and recall improvement are orthogonal; you'd verify by running both with the reranker on and measuring whether rank-2 holds or improves.  
C. No — recall above 95% indicates retrieval is saturated, and reranker overhead becomes pure cost.  
D. Yes — rerankers always strictly improve quality; never remove one once added.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

The two interventions improve different things. The bi-encoder upgrade improved recall (more correct chunks reach the candidate set) and moved them closer to the top. The reranker exploits a different signal — query-document interactions a bi-encoder cannot see.

Even after the upgrade, the cross-encoder's mean rank of ~2 on the prior setup tells you the interaction signal was worth ~6 positions; that signal hasn't gone away. Run the full pipeline (upgraded bi-encoder + reranker) and measure. If it lands at rank 1.5 you keep the reranker; if it lands at the same rank ~8 with no improvement, you drop it. Don't reason from first principles when you can run the measurement.

D is also wrong — rerankers don't *always* improve; on already-near-perfect retrieval (small focused corpora) they can be no-ops.

Review: [`concepts/rag/reranking.md` § When reranking helps the most](../../concepts/rag/reranking.md#when-reranking-helps-the-most)
</details>

---

## Scoring

| Score | Interpretation |
|---|---|
| 8/8 | Solid — you've internalized when each intervention helps and why. |
| 6-7/8 | Working knowledge — re-skim the explanation on misses. |
| 4-5/8 | Re-read the concept pages and re-run step 7 of Lab 07. |
| ≤3/8 | Read the three concept pages in order before re-attempting. |

## Next

- 🧪 [Lab 07](../../labs/07-retrieval-strategies-and-reranking/) — if you haven't finished it, the quiz answers will be much clearer afterwards.
- 🗺 [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/) — full path with prerequisites and ordering.
- 🧮 [Math foundations — agents as policies](../../math-foundations/04-agents-as-policies.md) — the framing under all this.
