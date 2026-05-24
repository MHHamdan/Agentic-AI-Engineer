---
quiz_id: agentic-rag-rag-fundamentals
title: "RAG fundamentals"
source:
  - concepts/rag/what-is-rag.md
  - concepts/rag/retrieval-as-a-tool.md
  - concepts/rag/chunking-and-indexing.md
  - tools/embeddings/snapshot-v1.0.md
  - labs/06-agentic-rag-from-scratch/
length_minutes: 8
difficulty: mixed
passing_score: 6
total_questions: 8

questions:
  - id: q1
    difficulty: easy
    question: "What's the defining difference between *naive* RAG and *agentic* RAG?"
    options:
      A: "Naive RAG uses a smaller embedding model than agentic RAG."
      B: "Agentic RAG retrieves once and generates once; naive RAG retrieves multiple times."
      C: "Naive RAG is a one-shot pipeline (retrieve → stuff → generate). Agentic RAG is an agent loop where retrieval is a tool the model decides when, what, and how often to call."
      D: "Agentic RAG requires GPU inference; naive RAG runs on CPU."
    answer: C
    explanation: |
      The defining property is *how many times the LLM is invoked* and
      *who decides when to retrieve*. Naive RAG runs one retrieval and
      one LLM call. Agentic RAG runs the LLM repeatedly, with the model
      itself deciding whether to call retrieval again, refine the query,
      or stop. B has the directions reversed. A and D are irrelevant
      distinctions — neither approach is tied to a specific model size
      or hardware.
    review:
      page: concepts/rag/what-is-rag.md
      section: "Naive RAG vs. agentic RAG"

  - id: q2
    difficulty: easy
    question: "Why does Lab 06 split retrieval into TWO tools (`search_corpus` for snippets and `read_chunk` for full text), mirroring Lab 03's `web_search` + `fetch_page`?"
    options:
      A: "OpenAI's function-calling API requires at least two tools."
      B: "It lets the agent triage with cheap snippet retrieval before paying the context cost of full chunks. The agent reads only the chunks worth reading."
      C: "Embeddings can't be computed against full chunks — only against snippets."
      D: "It's a LangChain convention being followed for consistency."
    answer: B
    explanation: |
      Same triage argument as Lab 03's web_search/fetch_page split.
      Snippets are cheap; full chunks consume real context budget. With
      one combined `retrieve_and_return_full_chunks(top_k=5)` tool, every
      retrieval dumps 5 full chunks (≈3000 tokens) into the model's
      context whether or not they're useful. Two tools let the model
      look at the snippets, pick the 1-2 worth reading, and skip the
      rest. The pattern transfers from Lab 03 unchanged. C is factually
      wrong — embeddings work on any text length the model can encode.
    review:
      page: concepts/rag/retrieval-as-a-tool.md
      section: "Why split into two tools (again)"

  - id: q3
    difficulty: medium
    question: "Lab 06 sets `normalize_embeddings=True` when encoding chunks with sentence-transformers. What's the purpose, and what goes wrong if you forget it?"
    options:
      A: "It prevents the model from downloading. Without it, the lab needs internet access."
      B: "Normalized vectors are unit-length, so cosine similarity reduces to a dot product. Without normalization, downstream similarity code must divide by the L2 norms, which is easy to get wrong."
      C: "It quantizes the embeddings to int8, saving 4× storage."
      D: "It forces deterministic output. Without it, the same input produces different embeddings on each call."
    answer: B
    explanation: |
      Normalizing makes every embedding have L2 norm = 1.0. Then
      `cosine(a, b) = (a · b) / (‖a‖ ‖b‖) = a · b`. The lab's retrieval
      step is a single `embeddings @ query_emb` matmul — clean, fast,
      one line. Without normalization the same expression returns dot
      products that *aren't* cosine similarities, and you'd need
      explicit norms in the denominator. The lab's similarity floor
      (`MIN_SIMILARITY = 0.30`) is calibrated against cosine values
      between 0 and 1; if you forget the flag, the floor stops being
      meaningful. C and D are wrong about what the flag does.
    review:
      page: tools/embeddings/snapshot-v1.0.md
      section: "API the labs use"

  - id: q4
    difficulty: medium
    question: "The Lab 06 corpus is chunked at 160 tokens per chunk (with ~20% overlap). Why not chunk at 256 tokens or larger? The chunks would be more self-contained."
    options:
      A: "Larger chunks always retrieve worse."
      B: "`all-MiniLM-L6-v2` silently truncates inputs over 256 *wordpieces* (~200 LLM-tokens). Chunks larger than this get their tails discarded by the embedding model with no error. The lab targets 160 tokens so even with overlap-prepending the chunks stay under 200."
      C: "Larger chunks take longer to embed."
      D: "Tokenization is non-deterministic above 256 tokens."
    answer: B
    explanation: |
      This is the 256-wordpiece foot-gun called out across the
      chunking-and-indexing concept page and the embeddings snapshot.
      MiniLM truncates inputs at 256 wordpieces — ~200 LLM-tokens for
      English. Anything beyond that is *silently* dropped from the
      embedding. The chunker's overlap step prepends ~32 tokens to each
      chunk, so a 160-token target keeps the final chunks comfortably
      under 200. If you change `TARGET_TOKENS` to 256, you'll get chunks
      where the last third has zero influence on the embedding, and
      retrieval quality drops sharply with no warning. A is wrong as a
      blanket claim. C and D are wrong about what changes.
    review:
      page: concepts/rag/chunking-and-indexing.md
      section: "The 256-wordpiece foot-gun (worth repeating)"

  - id: q5
    difficulty: medium
    question: "Lab 06 records citations as `(chunk_id, doc_id, title)` tuples. *When* does the loop add an entry to the citations list?"
    options:
      A: "When `search_corpus` returns a chunk in its top-k results."
      B: "When the LLM mentions the chunk_id in its final answer."
      C: "When `read_chunk` returns `status: ok` for that chunk_id."
      D: "When the model decides — the loop just records what the LLM claims."
    answer: C
    explanation: |
      Citations are recorded *only when `read_chunk` succeeds*. The
      moment that happens, the loop appends `{chunk_id, doc_id, title}`
      to the citations list. The agent cannot cite a chunk it didn't
      actually read in full — the structural property is what makes
      citations trustworthy. Option A would conflate "saw in snippet"
      with "read in full" — meaningless distinction lost. Option B
      would let the model hallucinate citations. Option D abdicates
      provenance to the LLM, which is exactly the failure mode the
      pattern is designed to prevent. This is the Lab 03 citation
      pattern transferred verbatim, just with chunks instead of URLs.
    review:
      page: concepts/rag/retrieval-as-a-tool.md
      section: "Citations get more precise"

  - id: q6
    difficulty: medium
    question: "Lab 06's `search_corpus` enforces a `MIN_SIMILARITY` floor of 0.30 and returns `status: empty` when no chunk crosses it. Why is this preferable to returning the top-k results regardless of score?"
    options:
      A: "It saves embedding compute on the query side."
      B: "Returning low-similarity results would let the agent synthesize confidently from chunks that don't actually match the query — the 'wrong-but-confident retrieval' failure mode. The structured `empty` status surfaces the absence cleanly so the agent can refine its query."
      C: "Cosine similarities below 0.30 are mathematically undefined."
      D: "OpenAI's API rejects similarity scores below 0.30."
    answer: B
    explanation: |
      The point of the floor is to distinguish "we retrieved something
      genuinely relevant" from "we retrieved the *least bad* chunk among
      24 irrelevant ones." Without a floor, an off-corpus query
      ("French Revolution 1789") would still return 5 chunks at scores
      like 0.12 — and the agent might synthesize from them. With a
      structured `empty` status, the agent gets a clean signal to
      either refine the query or surface "I couldn't find this in the
      corpus." The 0.30 number is calibrated for MiniLM; you'd tune it
      for different models or corpora. A is wrong — the cost is in
      computing the dot product, which already happens. C and D are
      fabrications.
    review:
      page: concepts/rag/retrieval-as-a-tool.md
      section: "What changes from Lab 03"

  - id: q7
    difficulty: hard
    question: "A teammate says: 'Lab 06 is just Lab 03 with a vector store. The lab loop is identical; only the I/O changed.' How accurate is this?"
    options:
      A: "Mostly accurate. The agent loop, repeated-action detection, citation tracking, and step cap transfer verbatim. What changes is which failure modes the agent encounters (no paywalls; instead, low-similarity floors and chunk-boundary loss) and the granularity of citations (chunk-level instead of URL-level)."
      B: "Completely wrong. RAG requires a fundamentally different control flow because retrieval is internal to the system."
      C: "Mostly wrong. The agent loop has to be rewritten because vector embeddings can't be tool results."
      D: "Half right. The loop transfers but tool calls work differently because retrieval returns float vectors."
    answer: A
    explanation: |
      The teammate is right. That's the whole pedagogical point of
      placing Lab 06 right after Lab 03 — to make the transfer visible.
      The loop is identical (same `chat_with_tools`, same `_action_hash`
      dedup, same step cap, same structured-error handling, same
      provider-agnostic client). What changes: the I/O layer (numpy
      index + sentence-transformers instead of `ddgs` + `requests`),
      the failure modes the agent sees (low-similarity floor instead of
      paywalls, no rate limits, but chunk-boundary loss is a new
      problem), and the citation granularity (`(chunk_id, doc_id,
      title)` instead of `(url, title)`). B and C are wrong — tool
      results are JSON dicts the way they always were; the embeddings
      are internal to `search_corpus`, the model never sees a float
      vector. D conflates the tool *implementation* with the tool *I/O
      contract*.
    review:
      page: concepts/rag/retrieval-as-a-tool.md
      section: "What stays the same"

  - id: q8
    difficulty: hard
    question: "You're prototyping a RAG system over 50 internal documents. Should you start with Lab 06's numpy index, or reach for Chroma/Pinecone/Qdrant immediately?"
    options:
      A: "Always start with Pinecone. Production-grade infrastructure is the safer default even at prototype scale."
      B: "Never use numpy for retrieval — vector stores have ANN algorithms that are required for correctness."
      C: "Numpy + cosine similarity is correct, fast, and inspectable at this scale. Production vector stores add persistence, network APIs, metadata filtering, and ANN algorithms for billions-of-vectors scale — but the cosine math is identical. Add a vector store when you have a *specific* requirement it solves (persistence across restarts, multi-process access, ANN for millions of chunks), not before."
      D: "Use whichever vector store your team is most familiar with — there are no technical considerations at this scale."
    answer: C
    explanation: |
      At 50 documents (~150-500 chunks), brute-force cosine over a
      numpy array is fast (<1 ms per query), correct, and inspectable.
      Production vector stores add real things — persistence, metadata
      filtering, ANN algorithms, network APIs — but none of those is
      required at this scale, and adopting one adds operational
      complexity. The honest decision rule from the vector-stores
      snapshot: *add infrastructure when you have a specific
      requirement it solves*. Persistence across restarts is the
      cleanest signal. Multi-process access is another. Millions of
      chunks where O(n) becomes too slow is another. None of these
      apply to a 50-document prototype. B is wrong — ANN is for scale,
      not correctness; brute-force is the gold standard at small N.
      A and D abdicate the actual engineering decision.
    review:
      page: tools/vector-stores/snapshot-v1.0.md
      section: "The 2026 vector store landscape, briefly"
---

# 🧠 Quiz · RAG fundamentals

> ⏱ ~8 min · 🎯 Pass: 6/8 · 📖 Sources:
>
> - [`concepts/rag/what-is-rag.md`](../../concepts/rag/what-is-rag.md)
> - [`concepts/rag/retrieval-as-a-tool.md`](../../concepts/rag/retrieval-as-a-tool.md)
> - [`concepts/rag/chunking-and-indexing.md`](../../concepts/rag/chunking-and-indexing.md)
> - [`tools/embeddings/snapshot-v1.0.md`](../../tools/embeddings/snapshot-v1.0.md)
> - [`labs/06-agentic-rag-from-scratch/`](../../labs/06-agentic-rag-from-scratch/)

The questions test the *patterns* of agentic RAG — the search-vs-RAG distinction, citation semantics, the 256-wordpiece foot-gun, when to upgrade from numpy — not the syntax of any specific library. If you understand why each design choice exists, the questions should feel natural.

---

## Question 1 *(easy)*

What's the defining difference between *naive* RAG and *agentic* RAG?

A. Naive RAG uses a smaller embedding model than agentic RAG.  
B. Agentic RAG retrieves once and generates once; naive RAG retrieves multiple times.  
C. Naive RAG is a one-shot pipeline (retrieve → stuff → generate). Agentic RAG is an agent loop where retrieval is a tool the model decides when, what, and how often to call.  
D. Agentic RAG requires GPU inference; naive RAG runs on CPU.

<details>
<summary>Show answer</summary>

**Answer: C** — Agentic RAG is the loop; naive RAG is the pipeline.

The defining property is *how many times the LLM is invoked* and *who decides when to retrieve*. Naive RAG runs one retrieval and one LLM call. Agentic RAG runs the LLM repeatedly, with the model itself deciding whether to call retrieval again, refine the query, or stop. B has the directions reversed. A and D are irrelevant distinctions — neither approach is tied to a specific model size or hardware.

→ Review: [`what-is-rag.md` § "Naive RAG vs. agentic RAG"](../../concepts/rag/what-is-rag.md#naive-rag-vs-agentic-rag)

</details>

---

## Question 2 *(easy)*

Why does Lab 06 split retrieval into TWO tools (`search_corpus` for snippets and `read_chunk` for full text), mirroring Lab 03's `web_search` + `fetch_page`?

A. OpenAI's function-calling API requires at least two tools.  
B. It lets the agent triage with cheap snippet retrieval before paying the context cost of full chunks. The agent reads only the chunks worth reading.  
C. Embeddings can't be computed against full chunks — only against snippets.  
D. It's a LangChain convention being followed for consistency.

<details>
<summary>Show answer</summary>

**Answer: B** — Triage before paying the context cost.

Same triage argument as Lab 03's web_search/fetch_page split. Snippets are cheap; full chunks consume real context budget. With one combined `retrieve_and_return_full_chunks(top_k=5)` tool, every retrieval dumps 5 full chunks (≈3000 tokens) into the model's context whether or not they're useful. Two tools let the model look at the snippets, pick the 1-2 worth reading, and skip the rest. The pattern transfers from Lab 03 unchanged. C is factually wrong — embeddings work on any text length the model can encode.

→ Review: [`retrieval-as-a-tool.md` § "Why split into two tools (again)"](../../concepts/rag/retrieval-as-a-tool.md#why-split-into-two-tools-again)

</details>

---

## Question 3 *(medium)*

Lab 06 sets `normalize_embeddings=True` when encoding chunks with sentence-transformers. What's the purpose, and what goes wrong if you forget it?

A. It prevents the model from downloading. Without it, the lab needs internet access.  
B. Normalized vectors are unit-length, so cosine similarity reduces to a dot product. Without normalization, downstream similarity code must divide by the L2 norms, which is easy to get wrong.  
C. It quantizes the embeddings to int8, saving 4× storage.  
D. It forces deterministic output. Without it, the same input produces different embeddings on each call.

<details>
<summary>Show answer</summary>

**Answer: B** — Unit-norm vectors make cosine = dot product.

Normalizing makes every embedding have L2 norm = 1.0. Then `cosine(a, b) = (a · b) / (‖a‖ ‖b‖) = a · b`. The lab's retrieval step is a single `embeddings @ query_emb` matmul — clean, fast, one line. Without normalization the same expression returns dot products that *aren't* cosine similarities, and you'd need explicit norms in the denominator. The lab's similarity floor (`MIN_SIMILARITY = 0.30`) is calibrated against cosine values between 0 and 1; if you forget the flag, the floor stops being meaningful. C and D are wrong about what the flag does.

→ Review: [`embeddings snapshot` § "API the labs use"](../../tools/embeddings/snapshot-v1.0.md#api-the-labs-use)

</details>

---

## Question 4 *(medium)*

The Lab 06 corpus is chunked at 160 tokens per chunk (with ~20% overlap). Why not chunk at 256 tokens or larger? The chunks would be more self-contained.

A. Larger chunks always retrieve worse.  
B. `all-MiniLM-L6-v2` silently truncates inputs over 256 *wordpieces* (~200 LLM-tokens). Chunks larger than this get their tails discarded by the embedding model with no error. The lab targets 160 tokens so even with overlap-prepending the chunks stay under 200.  
C. Larger chunks take longer to embed.  
D. Tokenization is non-deterministic above 256 tokens.

<details>
<summary>Show answer</summary>

**Answer: B** — The 256-wordpiece foot-gun.

This is the 256-wordpiece foot-gun called out across the chunking-and-indexing concept page and the embeddings snapshot. MiniLM truncates inputs at 256 wordpieces — ~200 LLM-tokens for English. Anything beyond that is *silently* dropped from the embedding. The chunker's overlap step prepends ~32 tokens to each chunk, so a 160-token target keeps the final chunks comfortably under 200. If you change `TARGET_TOKENS` to 256, you'll get chunks where the last third has zero influence on the embedding, and retrieval quality drops sharply with no warning. A is wrong as a blanket claim. C and D are wrong about what changes.

→ Review: [`chunking-and-indexing.md` § "The 256-wordpiece foot-gun (worth repeating)"](../../concepts/rag/chunking-and-indexing.md#the-256-wordpiece-foot-gun-worth-repeating)

</details>

---

## Question 5 *(medium)*

Lab 06 records citations as `(chunk_id, doc_id, title)` tuples. *When* does the loop add an entry to the citations list?

A. When `search_corpus` returns a chunk in its top-k results.  
B. When the LLM mentions the chunk_id in its final answer.  
C. When `read_chunk` returns `status: ok` for that chunk_id.  
D. When the model decides — the loop just records what the LLM claims.

<details>
<summary>Show answer</summary>

**Answer: C** — Read-confirmed only, recorded structurally.

Citations are recorded *only when `read_chunk` succeeds*. The moment that happens, the loop appends `{chunk_id, doc_id, title}` to the citations list. The agent cannot cite a chunk it didn't actually read in full — the structural property is what makes citations trustworthy. Option A would conflate "saw in snippet" with "read in full" — meaningless distinction lost. Option B would let the model hallucinate citations. Option D abdicates provenance to the LLM, which is exactly the failure mode the pattern is designed to prevent. This is the Lab 03 citation pattern transferred verbatim, just with chunks instead of URLs.

→ Review: [`retrieval-as-a-tool.md` § "Citations get more precise"](../../concepts/rag/retrieval-as-a-tool.md#citations-get-more-precise)

</details>

---

## Question 6 *(medium)*

Lab 06's `search_corpus` enforces a `MIN_SIMILARITY` floor of 0.30 and returns `status: empty` when no chunk crosses it. Why is this preferable to returning the top-k results regardless of score?

A. It saves embedding compute on the query side.  
B. Returning low-similarity results would let the agent synthesize confidently from chunks that don't actually match the query — the "wrong-but-confident retrieval" failure mode. The structured `empty` status surfaces the absence cleanly so the agent can refine its query.  
C. Cosine similarities below 0.30 are mathematically undefined.  
D. OpenAI's API rejects similarity scores below 0.30.

<details>
<summary>Show answer</summary>

**Answer: B** — Surface "I couldn't find it" cleanly instead of synthesizing from noise.

The point of the floor is to distinguish "we retrieved something genuinely relevant" from "we retrieved the *least bad* chunk among 24 irrelevant ones." Without a floor, an off-corpus query ("French Revolution 1789") would still return 5 chunks at scores like 0.12 — and the agent might synthesize from them. With a structured `empty` status, the agent gets a clean signal to either refine the query or surface "I couldn't find this in the corpus." The 0.30 number is calibrated for MiniLM; you'd tune it for different models or corpora. A is wrong — the cost is in computing the dot product, which already happens. C and D are fabrications.

→ Review: [`retrieval-as-a-tool.md` § "What changes from Lab 03"](../../concepts/rag/retrieval-as-a-tool.md#what-changes-from-lab-03)

</details>

---

## Question 7 *(hard)*

A teammate says: "Lab 06 is just Lab 03 with a vector store. The lab loop is identical; only the I/O changed." How accurate is this?

A. Mostly accurate. The agent loop, repeated-action detection, citation tracking, and step cap transfer verbatim. What changes is which failure modes the agent encounters (no paywalls; instead, low-similarity floors and chunk-boundary loss) and the granularity of citations (chunk-level instead of URL-level).  
B. Completely wrong. RAG requires a fundamentally different control flow because retrieval is internal to the system.  
C. Mostly wrong. The agent loop has to be rewritten because vector embeddings can't be tool results.  
D. Half right. The loop transfers but tool calls work differently because retrieval returns float vectors.

<details>
<summary>Show answer</summary>

**Answer: A** — The transfer is the pedagogical point.

The teammate is right. That's the whole pedagogical point of placing Lab 06 right after Lab 03 — to make the transfer visible. The loop is identical (same `chat_with_tools`, same `_action_hash` dedup, same step cap, same structured-error handling, same provider-agnostic client). What changes: the I/O layer (numpy index + sentence-transformers instead of `ddgs` + `requests`), the failure modes the agent sees (low-similarity floor instead of paywalls, no rate limits, but chunk-boundary loss is a new problem), and the citation granularity (`(chunk_id, doc_id, title)` instead of `(url, title)`). B and C are wrong — tool results are JSON dicts the way they always were; the embeddings are internal to `search_corpus`, the model never sees a float vector. D conflates the tool *implementation* with the tool *I/O contract*.

→ Review: [`retrieval-as-a-tool.md` § "What stays the same"](../../concepts/rag/retrieval-as-a-tool.md#what-stays-the-same)

</details>

---

## Question 8 *(hard)*

You're prototyping a RAG system over 50 internal documents. Should you start with Lab 06's numpy index, or reach for Chroma/Pinecone/Qdrant immediately?

A. Always start with Pinecone. Production-grade infrastructure is the safer default even at prototype scale.  
B. Never use numpy for retrieval — vector stores have ANN algorithms that are required for correctness.  
C. Numpy + cosine similarity is correct, fast, and inspectable at this scale. Production vector stores add persistence, network APIs, metadata filtering, and ANN algorithms for billions-of-vectors scale — but the cosine math is identical. Add a vector store when you have a *specific* requirement it solves (persistence across restarts, multi-process access, ANN for millions of chunks), not before.  
D. Use whichever vector store your team is most familiar with — there are no technical considerations at this scale.

<details>
<summary>Show answer</summary>

**Answer: C** — Reach for infrastructure when you have a specific requirement.

At 50 documents (~150-500 chunks), brute-force cosine over a numpy array is fast (<1 ms per query), correct, and inspectable. Production vector stores add real things — persistence, metadata filtering, ANN algorithms, network APIs — but none of those is required at this scale, and adopting one adds operational complexity. The honest decision rule from the vector-stores snapshot: *add infrastructure when you have a specific requirement it solves*. Persistence across restarts is the cleanest signal. Multi-process access is another. Millions of chunks where O(n) becomes too slow is another. None of these apply to a 50-document prototype. B is wrong — ANN is for scale, not correctness; brute-force is the gold standard at small N. A and D abdicate the actual engineering decision.

→ Review: [`vector-stores snapshot` § "The 2026 vector store landscape, briefly"](../../tools/vector-stores/snapshot-v1.0.md#the-2026-vector-store-landscape-briefly)

</details>

---

## Scoring

| Score | Meaning |
|---|---|
| 8/8 | You can teach this material. |
| 6–7/8 | Solid grasp. Move on. |
| 4–5/8 | Re-read the three concept pages and re-run Lab 06's failure-mode walkthrough. |
| < 4/8 | Re-do Lab 06 with the concept pages open. The questions map directly to specific sections. |

You've now completed the first practical batch of Path 02. The natural continuations are the *next* Path 02 batch (retrieval strategies, re-ranking, hybrid search, contextual retrieval), Path 03 (Multi-Agent Systems), or Path 06 (Evaluation & Observability).
