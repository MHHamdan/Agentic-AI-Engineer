# SOTA RAG patterns (2024-2026)

> 🟡 Slow-moving · ⏱ ~15 min read · 🏷 rag, patterns, sota, agentic-rag

## TL;DR

Canonical RAG (retrieve once, generate once) is the floor, not the ceiling. Between 2023 and 2026 a family of patterns emerged that add a control loop around retrieval: grade what came back, decide whether to retrieve again, route by query difficulty, or build a graph instead of a flat index. This page maps that landscape with citations, says when each pattern earns its added cost, and points at where each one is implemented or discussed in the repo.

The short version: most production systems still run advanced-but-static RAG (hybrid + rerank). The adaptive and agentic patterns below are worth reaching for when static RAG measurably fails on your eval set, not by default. Each added loop adds latency, cost, and failure surface.

> This page describes patterns that span the stable/fast-changing line. The *ideas* are stable; specific framework implementations (LangGraph CRAG templates, LlamaIndex agentic packs) move quarterly and are not pinned here.

---

## The evolution, in one picture

See [`diagrams/rag-bundle.md#9-rag-evolution-timeline`](../../diagrams/rag-bundle.md#9-rag-evolution-timeline) for the colorful version. In text:

Classical IR (BM25) → dense retrieval (DPR) → canonical RAG (Lewis et al.) → advanced RAG (hybrid, rerank, HyDE) → self-reflective RAG (Self-RAG, CRAG) → adaptive and graph RAG → agentic RAG. Each era added a capability the previous one lacked. None fully replaced its predecessor; BM25 is still a strong baseline in 2026.

---

## The baseline: canonical and advanced RAG

Before the SOTA patterns, fix the fundamentals. These are covered in depth elsewhere in the repo:

- **Canonical RAG** - the seven-stage pipeline (ingest / chunk / embed / index / retrieve / generate / cite). See [`what-is-rag.md`](./what-is-rag.md).
- **Hybrid search** - dense + sparse (BM25) fused with reciprocal rank fusion. See [`hybrid-search.md`](./hybrid-search.md).
- **Reranking** - cross-encoder second-stage scoring. See [`reranking.md`](./reranking.md).
- **Query transformation** - HyDE, multi-query expansion, decomposition. See [`query-rewriting.md`](./query-rewriting.md).

A system running hybrid retrieval plus cross-encoder reranking, with a measured eval set, beats most of the fancier patterns below on the median query. Reach for the patterns on this page only when your eval set shows specific failures that static RAG cannot fix.

---

## Pattern 1: Self-RAG (self-reflective retrieval)

**The idea.** The model decides *when* to retrieve and *whether retrieved content is useful*, using special reflection tokens trained into the model. It can retrieve on demand, grade each passage for relevance, and grade its own output for support and usefulness before committing.

**What it adds over static RAG.** Static RAG always retrieves, even when the query needs no external knowledge, and never checks whether what it retrieved was useful. Self-RAG makes both decisions explicit. The reflection tokens (`IsREL` for relevance, `IsSUP` for support, `IsUSE` for usefulness) are emitted as part of generation.

**When it earns its cost.** Mixed workloads where some queries need retrieval and some do not, and where the cost of retrieving-when-unnecessary (latency, distractor chunks) is real. Requires either a model fine-tuned with reflection tokens or a prompt-based approximation.

**Cost and caveats.** The original method requires fine-tuning. Prompt-based approximations exist but lose some of the benefit. Adds at least one extra grading step per retrieval.

**Reference.** Asai et al. (2023), [*Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*](https://arxiv.org/abs/2310.11511), ICLR 2024.

---

## Pattern 2: Corrective RAG (CRAG)

**The idea.** Insert a lightweight retrieval evaluator between retrieval and generation. It scores each retrieved document and classifies the result as correct, incorrect, or ambiguous. Correct documents proceed to generation; incorrect or ambiguous results trigger a corrective action, typically a web search to supplement the static corpus. A decompose-then-recompose step keeps only the load-bearing sentences from retrieved documents.

**What it adds over static RAG.** Static RAG has no mechanism to notice that retrieval failed. CRAG adds one classification layer that catches low-quality retrieval before it pollutes generation, and a fallback (web search) for when the local corpus does not have the answer.

**When it earns its cost.** Corpora that are incomplete or go stale, where the answer is sometimes not in your index and you have a web-search fallback available. The added classifier is one extra model call, so it is among the cheaper SOTA patterns to adopt.

**Cost and caveats.** The corrective action (web search) adds latency and a dependency on an external search API. The retrieval evaluator itself can be wrong; calibrate its threshold on your eval set.

**Reference.** Yan et al. (2024), [*Corrective Retrieval Augmented Generation*](https://arxiv.org/abs/2401.15884).

---

## Pattern 3: Adaptive RAG (query-complexity routing)

**The idea.** A classifier assesses incoming query complexity and routes to the cheapest sufficient strategy: no retrieval for queries the model can answer from parameters, single-step retrieval for simple factual queries, multi-step iterative retrieval for complex multi-hop queries.

**What it adds over static RAG.** Static RAG applies the same (often expensive) retrieval strategy to every query. Adaptive RAG matches effort to difficulty, which bounds average cost while keeping the multi-step machinery available for the queries that need it.

**When it earns its cost.** Workloads with a wide difficulty spread, where applying multi-step retrieval to every query would be wasteful and applying single-step to every query would fail the hard ones. The routing classifier needs training data labeling query complexity.

**Cost and caveats.** The router is a point of failure; a miscalibrated router sends hard queries down the cheap path. Treat router accuracy as its own eval target.

**Reference.** Jeong et al. (2024), [*Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity*](https://arxiv.org/abs/2403.14403), NAACL 2024.

---

## Pattern 4: Agentic RAG

**The idea.** Retrieval becomes a tool the agent chooses to call, rather than a fixed pipeline stage. The agent can reformulate the query, retrieve multiple times, grade results, retrieve from different sources, and critique its own draft before answering. Self-RAG, CRAG, and Adaptive RAG can all be seen as constrained special cases of the general agentic-RAG loop.

**What it adds over static RAG.** Full autonomy over the retrieve-reason-retrieve-again loop. Handles multi-hop questions, questions requiring cross-source synthesis, and questions where the first retrieval reveals what to retrieve next.

**When it earns its cost.** Genuinely multi-step research tasks where a single retrieval cannot surface all the evidence. For single-hop factual lookup, agentic RAG is over-engineering: it adds multiple model calls for no quality gain.

**Cost and caveats.** Most expensive pattern per query (multiple model calls, multiple retrievals). Hardest to make reproducible and to debug. Bound the loop with a maximum-iterations guard or it can spin.

**Where it lives in this repo.** [`patterns/08-agentic-rag.md`](../../patterns/08-agentic-rag.md) is the pattern page; [Lab 06](../../labs/06-agentic-rag-from-scratch/) implements it from scratch; [`retrieval-as-a-tool.md`](./retrieval-as-a-tool.md) is the conceptual framing; [`math-foundations/03-rag-formulation.md`](../../math-foundations/03-rag-formulation.md) has the math.

**References.** Singh et al. (2025), [*Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG*](https://arxiv.org/abs/2501.09136). Asai et al. (2023), Self-RAG (above), is the canonical adaptive-retrieval ancestor.

---

## Pattern 5: Graph RAG

**The idea.** Instead of a flat vector index, build a knowledge graph from the corpus at index time: extract entities and relationships, detect communities of related entities, and summarize each community. At query time, traverse the graph - map-reduce over community summaries for global "what are the themes" questions, or traverse a local subgraph for specific-entity questions.

**What it adds over flat RAG.** Flat vector RAG retrieves chunks independently and struggles with two things: global questions that require synthesizing across the whole corpus ("what are the main themes?") and multi-hop questions that require connecting facts across documents. The graph structure makes both tractable.

**When it earns its cost.** Corpora with rich entity-relationship structure (research literature, legal documents, enterprise knowledge bases) and queries that are global or multi-hop. Not worth it for simple factual lookup over unstructured text.

**Cost and caveats.** Index-time cost is high: entity extraction and community summarization are many LLM calls over the whole corpus. Re-indexing when the corpus changes is expensive. Treat as appropriate for relatively stable corpora.

**References.** Edge et al. (2024), [*From Local to Global: A Graph RAG Approach to Query-Focused Summarization*](https://arxiv.org/abs/2404.16130) (Microsoft Research). Survey: Han et al. (2025), [*Retrieval-Augmented Generation with Graphs (GraphRAG)*](https://arxiv.org/abs/2501.00309).

---

## Pattern 6: Long-context RAG

**The idea.** As model context windows grew to 200K-1M+ tokens, one option is to skip fine-grained retrieval and stuff large amounts of context directly. In practice the useful pattern is a hybrid: retrieve more coarsely (larger chunks, higher k) and rely on the long-context model to find the needle, while still bounding what you send.

**What it adds.** Fewer retrieval-precision failures, since you can afford to include more candidate context. Simpler pipelines for some workloads.

**When it earns its cost.** When retrieval precision is your bottleneck and the cost of larger contexts is acceptable. The decision between long-context and tiered retrieval is itself an engineering tradeoff covered in [`concepts/context/long-context-models.md`](../../concepts/context/long-context-models.md).

**Cost and caveats.** Long contexts cost more per call and exhibit the lost-in-the-middle effect: recall degrades for content in the middle of a long context. More context is not free and does not reliably improve answers. See [`math-foundations/13-context-window-optimization.md`](../../math-foundations/13-context-window-optimization.md).

**Reference.** Liu et al. (2023), [*Lost in the Middle: How Language Models Use Long Contexts*](https://arxiv.org/abs/2307.03172), TACL 2024.

---

## Pattern 7: Multimodal RAG

**The idea.** Retrieve over non-text modalities (images, tables, charts, audio) using multimodal embeddings, then generate with a multimodal model. The retrieval math is the same (vector similarity); the embedding model and the generator change.

**Status: emerging.** Multimodal embedding models and benchmarks are developing quickly. Production patterns are less settled than text RAG. Treat specific model recommendations as fast-moving and verify against current benchmarks.

**When it earns its cost.** Corpora where the answer lives in images, diagrams, or tables that text extraction loses (technical manuals with diagrams, financial reports with charts, slide decks).

**Cost and caveats.** Multimodal embedding quality varies more than text embedding quality. Evaluation tooling is less mature. Budget for more manual validation.

**Reference (requires further validation as the area moves quickly).** The Ragas framework added multimodal faithfulness and relevance metrics, indicating the eval tooling is catching up; see the [Ragas metrics list](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/).

---

## Pattern 8: Structured-data and tool-augmented RAG

**The idea.** Not all knowledge is unstructured text. Structured-data RAG translates a natural-language question into a query against a structured source (SQL database, API, knowledge graph) and grounds the answer in the result. Tool-augmented RAG generalizes this: retrieval is one tool among many (calculator, code interpreter, live API).

**When it earns its cost.** When the ground truth lives in a database or behind an API rather than in a document corpus. A question like "what was our Q3 revenue" should hit the finance database, not a vector index of PDFs.

**Cost and caveats.** Query generation (text-to-SQL) has its own failure modes and needs its own evaluation (execution accuracy, not retrieval recall). Mixing structured and unstructured retrieval requires a router (see Adaptive RAG above).

**Where it lives in this repo.** The tool-augmented framing is [`retrieval-as-a-tool.md`](./retrieval-as-a-tool.md) plus the tool-selection material in [`concepts/tools/`](../../concepts/tools/) and [`math-foundations/07-tool-selection.md`](../../math-foundations/07-tool-selection.md).

---

## Choosing a pattern

A rough decision guide. Start at the top; stop at the first row that matches your measured failure.

| Symptom on your eval set | Reach for | Added cost |
|---|---|---|
| Median query is fine; you have no eval set yet | Build the eval set first | None - this is step zero |
| Retrieval misses relevant chunks | Hybrid search + reranking (not on this page; fundamentals) | Low |
| Retrieval returns junk and the model uses it | CRAG (retrieval evaluator + fallback) | Low-medium |
| Easy and hard queries get the same expensive treatment | Adaptive RAG (complexity routing) | Medium |
| Some queries need no retrieval but always trigger it | Self-RAG (on-demand retrieval) | Medium (fine-tuning or prompt approximation) |
| Multi-hop questions fail; evidence spans documents | Agentic RAG (iterative retrieval) | High |
| Global "what are the themes" questions fail | Graph RAG | High (index-time) |
| Answer lives in images/tables/charts | Multimodal RAG (emerging) | High + less mature tooling |
| Answer lives in a database | Structured-data RAG (text-to-SQL) | Medium + separate eval |

**The meta-point:** every pattern below "hybrid + rerank" adds a control loop, and every control loop adds latency, cost, and a new way to fail. Adopt them in response to measured failures, not in anticipation. The evaluation framework on the next page is how you measure those failures.

---

## Repo cross-references

- [`what-is-rag.md`](./what-is-rag.md) - the canonical pipeline these patterns extend.
- [`retrieval-failure-modes.md`](./retrieval-failure-modes.md) - the diagnostic mental model for deciding which pattern you need.
- [`patterns/08-agentic-rag.md`](../../patterns/08-agentic-rag.md) - the deployable agentic-RAG pattern.
- [`concepts/evaluation/rag-evaluation-framework.md`](../evaluation/rag-evaluation-framework.md) - how to measure whether a pattern helped.
- [`diagrams/rag-bundle.md`](../../diagrams/rag-bundle.md) - the agentic-RAG, graph-RAG, and evolution-timeline diagrams.
- [Lab 06](../../labs/06-agentic-rag-from-scratch/), [Lab 07](../../labs/07-retrieval-strategies-and-reranking/), [Lab 08](../../labs/08-contextual-retrieval-and-query-rewriting/) - hands-on implementations.

## References

- Lewis, P., et al. (2020). [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401). NeurIPS. The canonical RAG formulation all these patterns extend.
- Asai, A., et al. (2023). [*Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*](https://arxiv.org/abs/2310.11511). ICLR 2024. Pattern 1.
- Yan, S., et al. (2024). [*Corrective Retrieval Augmented Generation*](https://arxiv.org/abs/2401.15884). Pattern 2.
- Jeong, S., et al. (2024). [*Adaptive-RAG*](https://arxiv.org/abs/2403.14403). NAACL 2024. Pattern 3.
- Singh, A., et al. (2025). [*Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG*](https://arxiv.org/abs/2501.09136). Pattern 4; broad taxonomy.
- Edge, D., et al. (2024). [*From Local to Global: A Graph RAG Approach to Query-Focused Summarization*](https://arxiv.org/abs/2404.16130). Microsoft Research. Pattern 5.
- Han, H., et al. (2025). [*Retrieval-Augmented Generation with Graphs (GraphRAG)*](https://arxiv.org/abs/2501.00309). GraphRAG survey.
- Liu, N. F., et al. (2023). [*Lost in the Middle: How Language Models Use Long Contexts*](https://arxiv.org/abs/2307.03172). TACL 2024. Pattern 6.
- Brown, A., Roman, M., and Devereux, B. (2025). [*A Systematic Literature Review of Retrieval-Augmented Generation: Techniques, Metrics, and Challenges*](https://arxiv.org/abs/2508.06401). Survey covering 2020 to May 2025; useful map of the whole field.

> 🟡 This page is classified slow-moving. The patterns are stable ideas; specific framework implementations change quarterly. Verify framework-specific details against current docs.
