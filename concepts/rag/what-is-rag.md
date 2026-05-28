# What is RAG?

> 🟢 Stable · ⏱ ~10 min read · 🏷 rag, retrieval, foundations

## TL;DR

RAG — Retrieval-Augmented Generation — is a pattern where a language model answers using *retrieved* text from a corpus you control, instead of (or in addition to) what it memorized during training. The 2020 Lewis et al. paper introduced the name; the pattern itself is older, but RAG is the term that stuck.

The pattern shows up in two shapes that often get confused:

- **Naive RAG**: a pipeline. Query → retrieve → stuff retrieved chunks into one prompt → generate one answer. Linear, one-shot.
- **Agentic RAG**: an agent loop. Retrieval is one of the agent's tools; the agent decides *when* to retrieve, *what* to query, and whether to retrieve *again*. Multi-step, just like Lab 03's research agent — but the corpus is yours instead of the open web.

Lab 06 builds the agentic version. This page is about why both shapes exist and when each one is the right reach.

---

## The problem RAG was introduced to solve

By 2020, pre-trained language models — BERT, T5, GPT-2/3 — were known to *store knowledge in their parameters*. You could ask GPT-3 "when did France adopt the metric system?" and it would usually answer correctly because the fact was in its training data.

The problem: that parametric knowledge has three big failure modes.

1. **It's stale.** The model knows nothing past its training cutoff. New facts, recent papers, your company's documents written last week — all invisible.
2. **It's private-blind.** Anything not in the public training corpus (your internal docs, your customer data, your specific domain) is just not there.
3. **It hallucinates under uncertainty.** When the model doesn't know, it doesn't say "I don't know" by default — it generates plausible-sounding output that may be wrong. This is the most-cited reason people reach for RAG.

The 2020 Lewis et al. paper ([*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401), NeurIPS 2020) proposed a fix: augment the model with *non-parametric memory* — a dense vector index over a document collection — that the model queries at inference time. The retrieved passages get conditioned on, and the model generates from both its parametric knowledge and the retrieved evidence. 

The paper showed RAG models produce more specific, diverse, and factual responses than parametric-only baselines on open-domain QA benchmarks. The architecture they proposed (DPR retriever + BART generator, end-to-end trained) is mostly historical now — modern systems use pretrained embedding models and frozen LLMs — but the *pattern* the paper named is what everyone calls RAG today.

## What RAG is, mechanically

In its simplest form, RAG has three moving parts:

```
            ┌────────────┐
question →  │  retrieve  │  → top-k chunks
            └────────────┘            │
                                      ▼
                          ┌────────────────────┐
                          │  generate (LLM)    │  → answer
                          │  prompt: question  │
                          │        + chunks    │
                          └────────────────────┘
```

The retriever queries an *index* — a vector store of embedded text chunks from a *corpus* you've assembled — and returns the top-k chunks most similar to the question. The generator (the LLM) receives the question plus the retrieved chunks in its prompt and produces an answer.

The corpus, the embeddings, the index, the chunk size, the top-k value, the prompt format — all of those are choices the system designer makes. None of them are "RAG" specifically; they're parameters of *a* RAG system.

## Naive RAG vs. agentic RAG

The classic shape — retrieve once, generate once — is what we call **naive RAG** in this curriculum. It's a one-shot pipeline:

```
question → retrieve top 5 chunks → prompt LLM with all 5 → answer
```

It works surprisingly well for simple factual questions where:

- One retrieval is enough.
- The right answer is likely in the top few chunks.
- The question doesn't need iterative refinement.

It fails (or degrades) for questions where:

- The first retrieval misses, and a refined query would have found the answer.
- The answer requires synthesis across multiple parts of the corpus you'd never have retrieved with a single query.
- The chunk-stuffing strategy includes too much irrelevant context, which confuses the model.
- The question is multi-hop ("X was founded by Y, who later worked at Z — what is Z's revenue?") and needs sequential retrievals.

**Agentic RAG** restructures the same pieces into an agent loop. Retrieval is now a *tool* the agent decides to call:

```
question → agent decides → maybe retrieve → maybe read full chunk → maybe retrieve again → synthesize → answer
```

If this looks like [*Lab 03's research agent*](https://github.com/MHHamdan/Agentic-AI-Engineer/blob/main/labs/03-multi-step-research-agent/lab.ipynb) — search the web, decide what to fetch, synthesize across sources — that's exactly the point. **Agentic RAG is the same loop as Lab 03, but the corpus is bounded and yours instead of the open web.**

The Foundations path covered this distinction directly: search ≠ RAG because search queries a corpus you don't control. Now that we're in the corpus-you-control regime, the agent loop is the natural shape because:

- You may want to refine a failed query.
- You may want to retrieve, then read one chunk in full, then retrieve more.
- You may want to surface "I couldn't find this in our docs" rather than synthesizing from the closest-but-irrelevant chunks.
- You absolutely want citations to specific chunks, tracked by the loop and not by the LLM (the Lab 03 pattern transfers directly).

## When naive RAG is enough

Be honest about this. Plenty of production systems are naive RAG and they work fine.

| Question shape | Naive RAG sufficient? |
|---|---|
| "What is our refund policy?" (single answer in single doc) | Yes |
| "What are the steps to deploy?" (procedural, in one doc) | Usually |
| "Compare our pricing tiers" (table in one doc) | Yes |
| "Which features did we ship last quarter?" (across many release notes) | Depends; agentic if questions get specific |
| "Find policy contradictions across our handbooks" | No — needs synthesis across retrievals |
| "Did we ship feature X, and if so, what does our docs say about Y?" | No — multi-hop |

The honest rule: **if one well-chosen retrieval contains the answer, naive RAG is fine.** When you need to iterate, refine, or synthesize across multiple retrievals — agentic RAG.

The cost difference matters: agentic RAG runs the LLM more times per question, costs more per query, and is slower. For the easy half of your traffic, naive is the right efficiency choice. The two patterns coexist in real systems.

## The three failure modes RAG doesn't fix

Worth knowing up front, before you build one:

1. **Hallucination *within* retrieved content.** RAG grounds the model in retrieved chunks, but the model can still misread or misquote them. The chunks reduce the probability of fabrication; they don't eliminate it. Production systems measure this with faithfulness/groundedness metrics (Path 06).
2. **Bad retrievals propagate as confident wrong answers.** If your index returns the wrong top-5 chunks, the model will synthesize from them confidently. *"RAG is only as good as your retriever."* — every production RAG team's first lesson. This is what re-ranking, hybrid search, and contextual retrieval address — covered in later Path 02 batches.
3. **Citation hallucination.** The LLM can claim to be quoting a chunk it didn't actually use. The Lab 03 pattern — *the loop records citations, not the LLM* — transfers directly here and is non-negotiable.

What RAG *does* fix is the staleness, private-blindness, and unverifiable-claim problems that motivated the original paper. Used well, it makes the model's outputs *anchorable* — the user can check the cited source.

## Where the curriculum goes from here

This page sets up Path 02. The other two concept pages in this first batch:

- 📖 **[Retrieval as a tool](./retrieval-as-a-tool.md)** *(~9 min)* — the agentic framing in detail. How `search_corpus` and `read_chunk` map onto Lab 03's `web_search` and `fetch_page`, the patterns that transfer, and the patterns that change.
- 📖 **[Chunking and indexing](./chunking-and-indexing.md)** *(~12 min)* — the stable decisions that govern every RAG system: chunk size, overlap, metadata, indexing strategy. Honest about what matters and what doesn't.

Then 🧪 **[Lab 06: Agentic RAG from scratch](../../labs/06-agentic-rag-from-scratch/)** builds the whole thing against a bundled corpus.

Later Path 02 batches will cover: retrieval strategies (top-k tuning, MMR, re-ranking), contextual retrieval (the Anthropic technique), hybrid search (BM25 + dense fusion), and a framework-bridge lab (the same RAG agent in LangChain).

## See also

- 📖 [Search tools](../tools/search-tools.md) — the Foundations page that introduces the "why search is not RAG" distinction this page builds on.
- 🧪 [Lab 03: Multi-step research agent](../../labs/03-multi-step-research-agent/) — the search-the-open-web analog of Lab 06.
- 📖 [Agents vs. frameworks](../agents/agents-vs-frameworks.md) — the same "do I need the framework?" question reappears for RAG; this page sets the framing.

## References

- Lewis, P. et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS 2020. The paper that named the pattern. Most-cited reference in modern RAG writeups.
- Karpukhin, V. et al. (2020). [*Dense Passage Retrieval for Open-Domain Question Answering*](https://arxiv.org/abs/2004.04906). EMNLP 2020. The dense retrieval mechanism Lewis et al. built on.
- Guu, K. et al. (2020). [*REALM: Retrieval-Augmented Language Model Pre-Training*](https://arxiv.org/abs/2002.08909). ICML 2020. Concurrent paper introducing retrieval-augmented language models from a different angle.
- Gao, Y. et al. (2024). [*Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997). A comprehensive 2024 survey covering naive, advanced, and modular RAG, plus the evaluation landscape.
- Anthropic (2024). [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval). The contextual retrieval technique — covered as its own concept page in a later Path 02 batch.
