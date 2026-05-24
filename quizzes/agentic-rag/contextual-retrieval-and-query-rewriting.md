---
quiz_id: agentic-rag-contextual-retrieval-and-query-rewriting
title: "Contextual retrieval, query rewriting, and retrieval failure modes"
source:
  - concepts/rag/contextual-retrieval.md
  - concepts/rag/query-rewriting.md
  - concepts/rag/retrieval-failure-modes.md
  - labs/08-contextual-retrieval-and-query-rewriting/
length_minutes: 10
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "Anthropic's contextual retrieval technique works by augmenting *which* part of the RAG pipeline, with *what* kind of information?"
    options:
      A: "Augments the user's query with synonyms expanded by an LLM, before retrieval runs."
      B: "Augments each chunk with a short (50-100 token) LLM-generated context summary, before indexing into BM25 and the embedder."
      C: "Augments the reranker's training data with hard negatives mined from the corpus."
      D: "Augments the agent loop with a verification step that re-reads each chunk after retrieval."
    answer: B
    explanation: |
      Contextual retrieval is a *corpus-side, index-time* technique.
      For each chunk, an LLM generates a 50-100 token situating
      summary using the full document as context. That summary is
      prepended to the chunk, and the augmented chunk feeds both
      the BM25 index ("Contextual BM25") and the embedder
      ("Contextual Embeddings"). The retrievers don't change; the
      chunks they index do. A describes query expansion. C describes
      reranker training. D describes nothing standard.
    review:
      page: concepts/rag/contextual-retrieval.md
      section: "The mechanism"

  - id: q2
    difficulty: easy
    question: "Why must contextual retrieval index the augmented chunks in *both* the BM25 index and the dense embedding index, rather than just one?"
    options:
      A: "Both indexes share the same backing storage, so updating one would corrupt the other."
      B: "Anthropic's measurements showed that contextual embeddings alone reduce retrieval failure by 35%, but adding contextual BM25 brings it to 49%. The two techniques target overlapping but distinct failure modes (semantic context vs. lexical context), and the gains stack."
      C: "BM25 cannot process raw chunk text; it requires preprocessed summaries."
      D: "The reranker downstream only accepts inputs from BM25 — embeddings alone would not produce a ranked candidate set."
    answer: B
    explanation: |
      Anthropic's published benchmarks: Contextual Embeddings alone
      reduce the top-20 failure rate by 35% (5.7% → 3.7%). Adding
      Contextual BM25 brings it to 49% (5.7% → 2.9%). The two
      indexes carry different signals — BM25 picks up the doc-level
      lexical tokens the summary introduces (proper nouns, codes,
      doc identity), and the embedder picks up the semantic
      anchoring. Skipping either leaves ~⅓ of the improvement on
      the table. The published name even reflects this — the
      technique is "Contextual Retrieval" with two named
      sub-techniques.
    review:
      page: concepts/rag/contextual-retrieval.md
      section: "Why it works"

  - id: q3
    difficulty: medium
    question: "You're indexing a 1M-chunk corpus with contextual retrieval. Naively, you'd make 1M LLM calls, each passing the full document plus the chunk. What's the standard optimization that makes this affordable, and roughly what cost reduction does it produce on long documents?"
    options:
      A: "Generate summaries in parallel batches of 100; reduces cost by ~50% via batch API discounts."
      B: "Truncate documents to 4K tokens before passing them; reduces cost by ~75% by shrinking the per-call input."
      C: "Use prompt caching: load each document into the cache once, then reference it cheaply for every chunk in that document. With Anthropic's 5-min TTL pricing (1.25× write, 0.1× read), a 10-chunk document gets ~80% savings on document tokens versus the uncached baseline."
      D: "Fine-tune a smaller model on the contextualizer task; reduces inference cost by ~90% via model distillation."
    answer: C
    explanation: |
      Prompt caching is the standard optimization Anthropic
      themselves recommend. The math: naive cost per chunk =
      doc_tokens + chunk_tokens + instruction_tokens. With caching,
      the document is paid once at 1.25× (write), then referenced
      at 0.1× (read) for every subsequent chunk in the same
      document. For a 10-chunk document, total document-token cost
      drops from `10 × 1.0×` to `1 × 1.25× + 9 × 0.1×` ≈ 2.15×,
      versus the naive 10.0× — roughly 78-80% savings on document
      tokens. Anthropic's quoted ~$1.02 per million document tokens
      assumes this caching. A, B, and D are all real techniques but
      not the standard one for contextual retrieval.
    review:
      page: concepts/rag/contextual-retrieval.md
      section: "The cost question"

  - id: q4
    difficulty: medium
    question: "HyDE (Hypothetical Document Embeddings, Gao et al. 2022) takes a query and does *what* before retrieval runs?"
    options:
      A: "Translates the query into 5 different languages, retrieves each, and fuses the results."
      B: "Asks an LLM to generate a hypothetical *answer* to the query, then embeds the answer (not the query) and retrieves against that. The bet: answers share vocabulary with the chunks that contain them, in a way questions don't."
      C: "Generates synonyms for each non-stopword token in the query and expands with WordNet."
      D: "Trains a small adapter network on the query distribution to project queries into the document embedding space."
    answer: B
    explanation: |
      HyDE inverts the standard flow. The LLM imagines what an
      answer would look like (using domain vocabulary, statement
      form), then embeds the hypothetical answer for retrieval.
      Chunks containing the real answer are likely to embed near
      the hypothetical answer because they share vocabulary and
      statement form. The original paper averaged embeddings of 5
      hypotheticals to reduce variance. The key risk: if the LLM
      has no domain knowledge, the hypothetical is invented and
      retrieval gets worse, not better. A and C are query expansion
      techniques but not HyDE. D describes an entirely different
      pattern (learned query projection).
    review:
      page: concepts/rag/query-rewriting.md
      section: "Pattern 1: HyDE — Hypothetical Document Embeddings"

  - id: q5
    difficulty: medium
    question: "Your RAG agent's retrieval consistently fails on this query: *\"What's the difference between Lab 06's bi-encoder retrieval and Lab 07's reranking, and how do they interact in the full pipeline?\"* — top-5 chunks are all vaguely relevant but no chunk specifically answers any sub-question. What's the right intervention?"
    options:
      A: "Add MMR diversification — the top-5 are too redundant."
      B: "Switch to contextual retrieval — the chunks need doc-level context."
      C: "Decompose the compound query into atomic sub-questions and retrieve each separately, then union or RRF-fuse the results. Equivalent: trust the agent loop to decompose it through multiple retrieval calls."
      D: "Lower MIN_SIMILARITY so more candidates make it through."
    answer: C
    explanation: |
      This is failure mode 6 (compound query) from the failure-modes
      page. Compound queries compress into a single fuzzy embedding
      that's "about" all sub-questions but specifically about none
      of them. Decomposition addresses this by treating each
      sub-question as its own retrieval target. In Lab 08 you can
      do this explicitly (faster, parallel); in Lab 06's pattern
      the agent naturally does it (slower but more flexible — the
      agent can react to what each sub-query returns). MMR (A) is
      for *redundant* top-k, a different failure mode. Contextual
      retrieval (B) would help if each chunk needed doc context,
      but here the chunks are findable; the *query* is the problem.
      Lowering the floor (D) just admits more low-quality
      candidates.
    review:
      page: concepts/rag/retrieval-failure-modes.md
      section: "Failure mode 6: Multi-part queries hit the wrong parts"

  - id: q6
    difficulty: medium
    question: "Why does Lab 08's `read_chunk` tool return the *original* chunk text (not the augmented chunk-plus-context), even though the augmented version was what got indexed?"
    options:
      A: "The augmented chunk would exceed the LLM's context window."
      B: "The cache stores only original chunks; the augmented version exists only at index time."
      C: "The context summary is a *retrieval aid*, not part of the source of truth. The LLM should reason from the actual document content, not from a summary the LLM itself generated earlier. Passing the augmented chunk would create a subtle self-reference where the model trusts its own earlier paraphrase as if it were original evidence."
      D: "Anthropic's published implementation requires this for legal reasons."
    answer: C
    explanation: |
      This is a faithfulness-preserving design choice. The context
      summary is engineered to help the *retriever* find the right
      chunk — it's a label, not evidence. If the LLM reads the
      augmented chunk and synthesizes from it, the model is now
      reasoning from a paraphrase it generated, which can introduce
      drift, hallucination, or self-confirmation. Lab 06's
      principle "citations track what was *actually read*" extends
      naturally to "the citation source is the original chunk, not
      a summary of it." Anthropic notes optionally passing the
      augmented chunk to generation as a tunable — but only after
      explicitly verifying it doesn't hurt faithfulness on your
      corpus.
    review:
      page: concepts/rag/contextual-retrieval.md
      section: "The mechanism"

  - id: q7
    difficulty: hard
    question: "You add HyDE to your production RAG pipeline. Latency goes up by 800ms (the extra LLM call), and on 20% of queries the retrieval results get *worse*. What's the most likely diagnosis?"
    options:
      A: "Your reranker model is too small; upgrade to bge-reranker-large."
      B: "HyDE is invariably degrading; remove it."
      C: "On some queries the LLM has no relevant domain knowledge, so the hypothetical answer is invented and the embedding lands in a random region of semantic space, pulling retrieval *away* from the right chunks. Mitigations: route only ambiguous/paraphrase-shaped queries through HyDE; fall back to baseline retrieval when the LLM signals low confidence; or measure per-query and disable HyDE for query classes it hurts."
      D: "Your prompt caching isn't enabled; the latency is unrelated to retrieval quality."
    answer: C
    explanation: |
      This is the canonical HyDE failure mode. HyDE only helps when
      the LLM has enough domain knowledge to write a plausible
      answer in the chunk's vocabulary. For unfamiliar domains
      (specialized jargon, internal product names, niche technical
      content) the hypothetical is essentially made up, and its
      embedding goes somewhere unrelated. The fix isn't "always-on
      HyDE" — it's *conditional* HyDE. A common production pattern:
      run baseline retrieval first; if the top-1 score is below a
      confidence threshold, *then* run HyDE and retry. A doesn't
      address the root cause. B is too strong — HyDE genuinely
      helps on 80% of queries in this scenario, just not all. D is
      orthogonal to the quality regression.
    review:
      page: concepts/rag/query-rewriting.md
      section: "When query rewriting hurts more than it helps"

  - id: q8
    difficulty: hard
    question: "Reviewing your RAG system, you find: (a) retrieval surfaces the right chunks consistently at rank 1-3; (b) the agent reads them faithfully via `read_chunk`; (c) yet ~30% of answers are still wrong, contradicting what's actually in the cited chunks. Which intervention from Labs 06-08 fixes this?"
    options:
      A: "Add contextual retrieval — the chunks must be losing context."
      B: "Add a cross-encoder reranker — the ranking is presumably off."
      C: "None of them. This is *not a retrieval failure*. Retrieval is doing its job (right chunks found and read). The problem is faithfulness / groundedness in the answer-generation step. Mitigations are prompt-engineering the agent to stay grounded, switching to a stronger generation model, or — properly — building evaluation tooling (Path 06) to measure and improve faithfulness directly."
      D: "Add HyDE — the query phrasing is misleading the LLM."
    answer: C
    explanation: |
      This is failure mode 7 from the failure-modes page: the
      classic mis-diagnosis trap in production RAG. The symptoms
      look like a retrieval problem ("answers are wrong"), but
      the diagnostic step (inspect the citations against the
      answer) reveals that retrieval succeeded. The problem is
      that the LLM didn't ground its answer in what it read.
      Pouring more engineering into retrieval-side fixes is wasted
      effort. The right intervention is faithfulness/groundedness
      evaluation and prompting — covered in Path 06. The failure
      modes page exists specifically to catch this category of
      mis-diagnosis before the engineering effort gets misallocated.
    review:
      page: concepts/rag/retrieval-failure-modes.md
      section: "Failure mode 7: The agent retrieves something but synthesizes the wrong answer"
---

# Quiz: Contextual retrieval, query rewriting, and retrieval failure modes

> 🟡 Mixed difficulty · ⏱ ~10 minutes · 8 questions, single-select

This quiz checks understanding of the three quality-intervention concept pages and the patterns from Lab 08. Read all three pages and finish at least steps 1-7 of the lab before attempting.

**Format.** Each question shows four options. Click the `<details>` block to reveal the answer and full explanation. Aim for 6/8 to feel solid; below that, the linked review section is the place to revisit.

---

## Q1 — What contextual retrieval augments

Anthropic's contextual retrieval technique works by augmenting *which* part of the RAG pipeline, with *what* kind of information?

A. Augments the user's query with synonyms expanded by an LLM, before retrieval runs.  
B. Augments each chunk with a short (50-100 token) LLM-generated context summary, before indexing into BM25 and the embedder.  
C. Augments the reranker's training data with hard negatives mined from the corpus.  
D. Augments the agent loop with a verification step that re-reads each chunk after retrieval.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

Contextual retrieval is a *corpus-side, index-time* technique. For each chunk, an LLM generates a 50-100 token situating summary using the full document as context. That summary is prepended to the chunk, and the augmented chunk feeds both the BM25 index ("Contextual BM25") and the embedder ("Contextual Embeddings"). The retrievers don't change; the chunks they index do.

A describes query expansion. C describes reranker training. D describes nothing standard.

Review: [`concepts/rag/contextual-retrieval.md` § The mechanism](../../concepts/rag/contextual-retrieval.md#the-mechanism)
</details>

---

## Q2 — Why both BM25 and dense

Why must contextual retrieval index the augmented chunks in *both* the BM25 index and the dense embedding index, rather than just one?

A. Both indexes share the same backing storage, so updating one would corrupt the other.  
B. Anthropic's measurements showed that contextual embeddings alone reduce retrieval failure by 35%, but adding contextual BM25 brings it to 49%. The two techniques target overlapping but distinct failure modes (semantic context vs. lexical context), and the gains stack.  
C. BM25 cannot process raw chunk text; it requires preprocessed summaries.  
D. The reranker downstream only accepts inputs from BM25 — embeddings alone would not produce a ranked candidate set.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

Anthropic's published benchmarks: Contextual Embeddings alone reduce the top-20 failure rate by 35% (5.7% → 3.7%). Adding Contextual BM25 brings it to 49% (5.7% → 2.9%). The two indexes carry different signals — BM25 picks up the doc-level lexical tokens the summary introduces (proper nouns, codes, doc identity), and the embedder picks up the semantic anchoring. Skipping either leaves ~⅓ of the improvement on the table. The published name even reflects this — the technique is "Contextual Retrieval" with two named sub-techniques.

Review: [`concepts/rag/contextual-retrieval.md` § Why it works](../../concepts/rag/contextual-retrieval.md#why-it-works)
</details>

---

## Q3 — Cost optimization

You're indexing a 1M-chunk corpus with contextual retrieval. Naively, you'd make 1M LLM calls, each passing the full document plus the chunk. What's the standard optimization that makes this affordable, and roughly what cost reduction does it produce on long documents?

A. Generate summaries in parallel batches of 100; reduces cost by ~50% via batch API discounts.  
B. Truncate documents to 4K tokens before passing them; reduces cost by ~75% by shrinking the per-call input.  
C. Use prompt caching: load each document into the cache once, then reference it cheaply for every chunk in that document. With Anthropic's 5-min TTL pricing (1.25× write, 0.1× read), a 10-chunk document gets ~80% savings on document tokens versus the uncached baseline.  
D. Fine-tune a smaller model on the contextualizer task; reduces inference cost by ~90% via model distillation.

<details>
<summary>Answer & explanation</summary>

**Answer: C.**

Prompt caching is the standard optimization Anthropic themselves recommend. The math: naive cost per chunk = `doc_tokens + chunk_tokens + instruction_tokens`. With caching, the document is paid once at 1.25× (write), then referenced at 0.1× (read) for every subsequent chunk in the same document. For a 10-chunk document, total document-token cost drops from `10 × 1.0×` to `1 × 1.25× + 9 × 0.1×` ≈ 2.15×, versus the naive 10.0× — roughly 78-80% savings on document tokens.

Anthropic's quoted ~$1.02 per million document tokens assumes this caching. A, B, and D are all real techniques but not the standard one for contextual retrieval.

Review: [`concepts/rag/contextual-retrieval.md` § The cost question](../../concepts/rag/contextual-retrieval.md#the-cost-question)
</details>

---

## Q4 — HyDE mechanics

HyDE (Hypothetical Document Embeddings, Gao et al. 2022) takes a query and does *what* before retrieval runs?

A. Translates the query into 5 different languages, retrieves each, and fuses the results.  
B. Asks an LLM to generate a hypothetical *answer* to the query, then embeds the answer (not the query) and retrieves against that. The bet: answers share vocabulary with the chunks that contain them, in a way questions don't.  
C. Generates synonyms for each non-stopword token in the query and expands with WordNet.  
D. Trains a small adapter network on the query distribution to project queries into the document embedding space.

<details>
<summary>Answer & explanation</summary>

**Answer: B.**

HyDE inverts the standard flow. The LLM imagines what an answer would look like (using domain vocabulary, statement form), then embeds the hypothetical answer for retrieval. Chunks containing the real answer are likely to embed near the hypothetical answer because they share vocabulary and statement form. The original paper averaged embeddings of 5 hypotheticals to reduce variance.

The key risk: if the LLM has no domain knowledge, the hypothetical is invented and retrieval gets worse, not better. A and C are query expansion techniques but not HyDE. D describes an entirely different pattern (learned query projection).

Review: [`concepts/rag/query-rewriting.md` § Pattern 1: HyDE](../../concepts/rag/query-rewriting.md#pattern-1-hyde--hypothetical-document-embeddings)
</details>

---

## Q5 — Compound query failure mode

Your RAG agent's retrieval consistently fails on this query: *"What's the difference between Lab 06's bi-encoder retrieval and Lab 07's reranking, and how do they interact in the full pipeline?"* — top-5 chunks are all vaguely relevant but no chunk specifically answers any sub-question. What's the right intervention?

A. Add MMR diversification — the top-5 are too redundant.  
B. Switch to contextual retrieval — the chunks need doc-level context.  
C. Decompose the compound query into atomic sub-questions and retrieve each separately, then union or RRF-fuse the results. Equivalent: trust the agent loop to decompose it through multiple retrieval calls.  
D. Lower MIN_SIMILARITY so more candidates make it through.

<details>
<summary>Answer & explanation</summary>

**Answer: C.**

This is failure mode 6 (compound query) from the failure-modes page. Compound queries compress into a single fuzzy embedding that's "about" all sub-questions but specifically about none of them. Decomposition addresses this by treating each sub-question as its own retrieval target. In Lab 08 you can do this explicitly (faster, parallel); in Lab 06's pattern the agent naturally does it (slower but more flexible — the agent can react to what each sub-query returns).

MMR (A) is for *redundant* top-k, a different failure mode. Contextual retrieval (B) would help if each chunk needed doc context, but here the chunks are findable; the *query* is the problem. Lowering the floor (D) just admits more low-quality candidates.

Review: [`concepts/rag/retrieval-failure-modes.md` § Failure mode 6](../../concepts/rag/retrieval-failure-modes.md#failure-mode-6-multi-part-queries-hit-the-wrong-parts)
</details>

---

## Q6 — Why `read_chunk` returns the original

Why does Lab 08's `read_chunk` tool return the *original* chunk text (not the augmented chunk-plus-context), even though the augmented version was what got indexed?

A. The augmented chunk would exceed the LLM's context window.  
B. The cache stores only original chunks; the augmented version exists only at index time.  
C. The context summary is a *retrieval aid*, not part of the source of truth. The LLM should reason from the actual document content, not from a summary the LLM itself generated earlier. Passing the augmented chunk would create a subtle self-reference where the model trusts its own earlier paraphrase as if it were original evidence.  
D. Anthropic's published implementation requires this for legal reasons.

<details>
<summary>Answer & explanation</summary>

**Answer: C.**

This is a faithfulness-preserving design choice. The context summary is engineered to help the *retriever* find the right chunk — it's a label, not evidence. If the LLM reads the augmented chunk and synthesizes from it, the model is now reasoning from a paraphrase it generated, which can introduce drift, hallucination, or self-confirmation.

Lab 06's principle "citations track what was *actually read*" extends naturally to "the citation source is the original chunk, not a summary of it." Anthropic notes optionally passing the augmented chunk to generation as a tunable — but only after explicitly verifying it doesn't hurt faithfulness on your corpus.

Review: [`concepts/rag/contextual-retrieval.md` § The mechanism](../../concepts/rag/contextual-retrieval.md#the-mechanism)
</details>

---

## Q7 — HyDE in unfamiliar domains

You add HyDE to your production RAG pipeline. Latency goes up by 800ms (the extra LLM call), and on 20% of queries the retrieval results get *worse*. What's the most likely diagnosis?

A. Your reranker model is too small; upgrade to bge-reranker-large.  
B. HyDE is invariably degrading; remove it.  
C. On some queries the LLM has no relevant domain knowledge, so the hypothetical answer is invented and the embedding lands in a random region of semantic space, pulling retrieval *away* from the right chunks. Mitigations: route only ambiguous/paraphrase-shaped queries through HyDE; fall back to baseline retrieval when the LLM signals low confidence; or measure per-query and disable HyDE for query classes it hurts.  
D. Your prompt caching isn't enabled; the latency is unrelated to retrieval quality.

<details>
<summary>Answer & explanation</summary>

**Answer: C.**

This is the canonical HyDE failure mode. HyDE only helps when the LLM has enough domain knowledge to write a plausible answer in the chunk's vocabulary. For unfamiliar domains (specialized jargon, internal product names, niche technical content) the hypothetical is essentially made up, and its embedding goes somewhere unrelated.

The fix isn't "always-on HyDE" — it's *conditional* HyDE. A common production pattern: run baseline retrieval first; if the top-1 score is below a confidence threshold, *then* run HyDE and retry.

A doesn't address the root cause. B is too strong — HyDE genuinely helps on 80% of queries in this scenario, just not all. D is orthogonal to the quality regression.

Review: [`concepts/rag/query-rewriting.md` § When query rewriting hurts more than it helps](../../concepts/rag/query-rewriting.md#when-query-rewriting-hurts-more-than-it-helps)
</details>

---

## Q8 — Mis-diagnosing a faithfulness problem

Reviewing your RAG system, you find: (a) retrieval surfaces the right chunks consistently at rank 1-3; (b) the agent reads them faithfully via `read_chunk`; (c) yet ~30% of answers are still wrong, contradicting what's actually in the cited chunks. Which intervention from Labs 06-08 fixes this?

A. Add contextual retrieval — the chunks must be losing context.  
B. Add a cross-encoder reranker — the ranking is presumably off.  
C. None of them. This is *not a retrieval failure*. Retrieval is doing its job (right chunks found and read). The problem is faithfulness / groundedness in the answer-generation step. Mitigations are prompt-engineering the agent to stay grounded, switching to a stronger generation model, or — properly — building evaluation tooling (Path 06) to measure and improve faithfulness directly.  
D. Add HyDE — the query phrasing is misleading the LLM.

<details>
<summary>Answer & explanation</summary>

**Answer: C.**

This is failure mode 7 from the failure-modes page: the classic mis-diagnosis trap in production RAG. The symptoms look like a retrieval problem ("answers are wrong"), but the diagnostic step (inspect the citations against the answer) reveals that retrieval succeeded. The problem is that the LLM didn't ground its answer in what it read.

Pouring more engineering into retrieval-side fixes is wasted effort. The right intervention is faithfulness/groundedness evaluation and prompting — covered in Path 06. The failure modes page exists specifically to catch this category of mis-diagnosis before the engineering effort gets misallocated.

Review: [`concepts/rag/retrieval-failure-modes.md` § Failure mode 7](../../concepts/rag/retrieval-failure-modes.md#failure-mode-7-the-agent-retrieves-something-but-synthesizes-the-wrong-answer)
</details>

---

## Scoring

| Score | Interpretation |
|---|---|
| 8/8 | Solid — you've internalized when each intervention helps and which failure mode you have. |
| 6-7/8 | Working knowledge — re-skim the explanation on misses. |
| 4-5/8 | Re-read the three concept pages and walk through step 9 of Lab 08. |
| ≤3/8 | Read the three concept pages in order before re-attempting. |

## Next

- 🧪 [Lab 08](../../labs/08-contextual-retrieval-and-query-rewriting/) — if you haven't finished it, the quiz answers will be much clearer afterwards.
- 📖 [Retrieval failure modes](../../concepts/rag/retrieval-failure-modes.md) — the decision tree this quiz tests.
- 🗺 [Path 02 — Agentic RAG](../../learning-paths/02-agentic-rag/) — full path with prerequisites and ordering.
