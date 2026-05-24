# Changelog

All notable changes to this repository are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), with one repo-specific section added: **Verified Tool Snapshots**.

---

## Versioning policy

This repository is versioned semantically, with content-aware semantics:

- **Major version (X.0.0):** A reorganization that breaks existing links or the learning-path structure. Rare.
- **Minor version (0.X.0):** New content tracks, new learning paths, or substantial expansions to existing sections.
- **Patch version (0.0.X):** Individual concept, lab, recipe, or pattern additions; tool-snapshot updates; bug fixes; typo fixes.

Releases are tagged on `main` as `vX.Y.Z`. The `CHANGELOG.md` is the source of truth for what changed; GitHub release notes link back to it.

Because this is an evolving educational resource and not a software library, we don't promise backwards-compatible URLs across major versions. We do promise to provide migration notes when major reorganizations happen.

---

## Tool snapshot policy

Pages in `tools/` and any code that depends on a specific framework version carry a snapshot date in this form:

```
> 🔴 Tool snapshot — <tool> v<version>, verified YYYY-MM-DD
> Source: <official docs / changelog / spec link>
```

Tool snapshots are tracked separately in the **Verified Tool Snapshots** section of each release. When you update a snapshot:

1. Update the badge on the relevant `tools/<tool>/` page.
2. Add a line to the current `[Unreleased]` section under **Verified Tool Snapshots**.
3. Include a primary-source link in your PR description.

Routine snapshot sweeps happen at minor releases. Individual updates land continuously between releases.

When a tool ships a breaking change (e.g., `langgraph.prebuilt` → `langchain.agents`), the snapshot update is paired with a migration note on the tool page and, if needed, code updates across labs and recipes.

---

## [Unreleased]

### Added

- **Path 02 continuation — contextual retrieval, query rewriting, and retrieval failure modes (Lab 08).**
  - `learning-paths/02-agentic-rag/README.md` — updated. Adds Module 8 (Quality interventions; 3 concept pages), Module 9 (Lab 08), and Module 10 (third quiz). Path time estimate raised from 8-12h to 10-15h. Mermaid flowchart extended again to show the batch-11 → batch-12 progression. Anti-scope refined: contextual retrieval and query expansion moved from "future batches" to "done"; remaining future modules now RAG evaluation primer, framework bridge, and conversational RAG. References list expanded with Anthropic Contextual Retrieval (Sep 2024), HyDE (Gao et al. 2022), Query2doc (Wang et al. 2023), Rewrite-Retrieve-Read (Ma et al. 2023), and Seven Failure Points (Barnett et al. 2024).
  - `concepts/rag/contextual-retrieval.md` — ~11 min concept page on Anthropic's technique (verified via web_fetch of [anthropic.com/engineering/contextual-retrieval](https://www.anthropic.com/engineering/contextual-retrieval), published Sep 19, 2024). Documents the verified prompt template, the two sub-techniques (Contextual Embeddings + Contextual BM25), the headline metrics (5.7% → 3.7% → 2.9% → 1.9% top-20 retrieval failure rate as you add each layer), the ~$1.02/M document-tokens cost claim with prompt caching, when to use vs not, what contextual retrieval is NOT (vs query expansion, RAG-summarization, "give the LLM the whole document", or a substitute for hybrid+rerank), and adjacent techniques (document summary indexing, sentence-window, parent-document). Includes a 🔴 technique-snapshot badge calling out that the metrics are verified-as-of dates.
  - `concepts/rag/query-rewriting.md` — ~10 min concept page on the three patterns from scratch: HyDE (Gao, Ma, Lin, Callan; ACL 2023; arXiv:2212.10496) — generate hypothetical answer and embed THAT; multi-query expansion (Query2doc; Wang et al.; EMNLP 2023; arXiv:2303.07678) — generate 3 rephrasings and RRF-fuse; query decomposition — split compound queries into atomic sub-queries. Each pattern includes when-it-helps, when-it-hurts, and the cost-latency tradeoff. Production patterns section: rewrite-on-fail, cache rewrites, small model for rewrites, show rewrites in research UIs. Adjacent-techniques section: conversational query rewriting, query routing, retrieve-and-edit, self-RAG.
  - `concepts/rag/retrieval-failure-modes.md` — ~11 min synthesis page. Eight failure modes covering the union of Labs 06+07+08: (1) right chunk not in top-50; (2) right chunk at rank 6-15; (3) exact-term queries don't match; (4) paraphrased queries don't match; (5) top-k are redundant; (6) multi-part queries hit wrong parts; (7) wrong synthesis after good retrieval; (8) answer not in corpus. Each mode has symptom/cause/diagnosis/intervention. Includes a 7-step decision tree pseudocode, a failure-mode-to-intervention map table, and a "what's NOT a retrieval failure mode" callout (slow LLM, distrust, latency). Closes with instrumentation guidance — log query + rewrites + top-50 IDs + rerank scores + chunks-read + citations.
  - `concepts/rag/README.md` — updated. New "Quality interventions" subsection added (the three new pages). Resolved batch-12 pending items (contextual-retrieval, query-expansion → query-rewriting). Remaining pending: rag-evaluation.md, conversational-rag.md, framework-bridge-rag.md.
  - `labs/08-contextual-retrieval-and-query-rewriting/README.md` — lab brief (~110-140 min, intermediate). Reuses Lab 06's corpus and chunker entirely; **NO new dependencies** on top of Lab 07. Explicit cost note for index-time LLM calls. Anti-scope: no RAGAS, no production vector stores, no LangChain/LlamaIndex retrievers, no prompt caching in the lab itself (mentioned in concept page), no fine-tuning, no conversational query rewriting, no multi-agent. Common-gotchas list (cost discipline, corpus undersells benefit, HyDE in unfamiliar domains, multi-query latency stacks, score scale shift, agent reads ORIGINAL chunk not augmented).
  - `labs/08-contextual-retrieval-and-query-rewriting/lab.ipynb` — 46-cell notebook (29 md / 17 code) extending Lab 07 with contextual retrieval and three query-rewriting patterns. Step 0 setup. Step 1 recreates Lab 07's full pipeline (chunker, dense+BM25 baseline indexes, hybrid_retrieve helper, RRF, cross-encoder rerank). Step 2 generates context summaries via `llm_complete()` (provider-agnostic), using Anthropic's exact verbatim CONTEXT_PROMPT template, caching to `context_cache.json` keyed by chunk_id. Step 3 builds Contextual BM25 + Contextual Embeddings indexes; side-by-side comparison on EVAL_QUERIES showing 2 improved / 4 unchanged / 0 regressed (small corpus undersells the benefit honestly). Step 4 implements HyDE — `hyde_rewrite()` + demo on a paraphrased query showing the hypothetical answer's vocabulary lift. Step 5 implements multi-query expansion — `multi_query_rewrite()` returns `[original, *3 rephrasings]`, `multi_query_retrieve()` does RRF fusion (k=60). Step 6 implements query decomposition — `decompose_query()` handles the already-atomic case. Step 7 assembles `search_corpus_v3` with `rewrite_mode={None|"hyde"|"multi"|"decompose"}`; rerank uses the ORIGINAL query, not rewrites; agent reads ORIGINAL chunks. Step 8 wires into the Lab 06/07 agent loop unchanged. Step 9 (stretch) walks the failure-modes decision tree against 3 hand-chosen queries, comparing 4 strategies and reporting rank per case. Notebook outputs stripped; sample-output markdown cells throughout. Honest framing that the small lab corpus can't demonstrate Anthropic's headline 35-67% reduction; quote production-scale numbers and let the mechanism speak for itself.
  - `quizzes/agentic-rag/contextual-retrieval-and-query-rewriting.md` — 8 single-select questions: Anthropic technique mechanics (chunk-side, not query-side); why both BM25 AND dense must index augmented chunks; prompt-caching cost optimization with the 5-min TTL math (1.25× write + 0.1× read multipliers); HyDE mechanism inversion; compound-query failure mode; why `read_chunk` returns the ORIGINAL (faithfulness argument); HyDE in unfamiliar domains; the mis-diagnosis trap (failure mode 7 — retrieval succeeded but synthesis failed → not a retrieval problem). All 8 anchors verified via `github-slugger` against actual heading slugs (including em-dash double-hyphen cases). Same YAML+`<details>` + trailing-2-space-hard-break format as prior quizzes.
  - `diagrams/contextual-retrieval-flow.mmd` — Mermaid source for the Lab 08 pipeline showing index-time path (doc → chunker → contextualizer LLM + cache → augmented chunks → Contextual BM25 + Contextual dense indexes) and query-time path (query → optional rewrite → dense + BM25 retrieval over contextual indexes → RRF → cross-encoder rerank on ORIGINAL query → score floor → top-k envelope → agent reads ORIGINAL chunk). 7-class-styled diagram (index_time / query_time / rewrite / retrieval / storage / decision / agent / terminal) matching the diagrammatic vocabulary established in batches 10 and 11.

- **Path 02 continuation — retrieval strategies, hybrid search, and reranking (Lab 07).**
  - `learning-paths/02-agentic-rag/README.md` — updated. Adds Module 5 (Retrieval quality), Module 6 (Lab 07), and Module 7 (retrieval-strategies quiz). Path time estimate raised from 6-9h to 8-12h. Mermaid flowchart extended to show the batch-10 → batch-11 progression. Anti-scope refined: re-ranking + hybrid + retrieval strategies moved from "future batches" to "done"; remaining future modules updated to contextual retrieval, query expansion, framework bridge, RAG evaluation primer. References list expanded with BM25 (Robertson & Zaragoza 2009), RRF (Cormack et al. 2009), MMR (Carbonell & Goldstein 1998), BERT passage re-ranking (Nogueira & Cho 2019), and BEIR (Thakur et al. 2021).
  - `concepts/rag/retrieval-strategies.md` — ~11 min concept page on the four knobs every retriever exposes: `top_k` (with calibration recipe), score floors (with on-corpus vs off-corpus distribution method for picking the threshold), MMR diversification (algorithm laid out with λ semantics — 1.0=pure relevance, 0.7=gentle, 0.5=aggressive), and query construction (the under-appreciated highest-leverage knob). Includes a 7-step practical sequence for improving retrieval, plus an explicit anti-scope list deferring HyDE, contextual retrieval, late-interaction, etc. to later batches.
  - `concepts/rag/hybrid-search.md` — ~10 min concept page on combining dense and BM25 retrieval. Explains BM25 mechanics (TF, IDF, length normalization) and exact failure-mode inversion vs dense; walks through Reciprocal Rank Fusion with the canonical 10-line algorithm and the Cormack `k=60` constant; covers weighted score combination and cascade as alternatives; explicit "when hybrid isn't worth it" section. Includes a production-vector-stores hybrid-support table (Weaviate v1.18+, Qdrant v1.9+, Pinecone sparse-dense, pgvector via SQL, Chroma — no native).
  - `concepts/rag/reranking.md` — ~10 min concept page on cross-encoder reranking. Explains the bi-encoder limit (no query-document interaction signal), what a cross-encoder sees that a bi-encoder can't, the retrieve-then-rerank pipeline, the candidate_k → final_k ratio (5-10×), an alternative-rerankers table (`cross-encoder/ms-marco-MiniLM-L-6-v2` default, plus `MiniLM-L-12`, `bge-reranker-base/large`, Cohere Rerank, Voyage). Includes a wall-time table for the Lab 07 pipeline on CPU. The "candidate set must be wider than final top-k" misconception is the central pedagogical point.
  - `concepts/rag/README.md` — updated. Reorganized into "Foundations" (Module 1) and "Retrieval quality" (Module 5) sections. Resolved batch-10 pending items (retrieval-strategies.md, hybrid-search.md). Remaining pending: contextual-retrieval.md, query-expansion.md, rag-evaluation.md.
  - `labs/07-retrieval-strategies-and-reranking/README.md` — lab brief (~110-140 min, intermediate). Reuses Lab 06's corpus and chunker entirely; the only new dependency is `rank-bm25` (the `sentence-transformers` install from Lab 06 provides `CrossEncoder`). Explicit anti-scope: no RAG eval framework, no production vector stores, no LangChain RAG, no contextual retrieval, no HyDE, no late-interaction, no reranker fine-tuning, no multi-agent retrieval. Common-gotchas list (BM25 tokenization mismatch, reranker download size, score-scale confusion, candidate_k too small, MMR λ confusion, reranking CPU performance).
  - `labs/07-retrieval-strategies-and-reranking/lab.ipynb` — 41-cell notebook (26 md / 15 code) building the production-grade retrieval pipeline step by step. Step 0 sets up the LLM client. Step 1 recreates the Lab 06 baseline (dense index + 6 EVAL_QUERIES tagged `lexical-favorable | both | semantic`). Step 2 adds BM25 via `rank-bm25` with `BM25Okapi(corpus, k1=1.5, b=0.75)` and the same `re.findall(r"\w+", text.lower())` tokenizer for query and corpus. Step 3 implements Reciprocal Rank Fusion from scratch (~10 lines, `k=60`). Step 4 implements MMR from scratch (~15 lines of numpy, `λ=0.7` default), with a demo showing 4× same-doc chunks diversified into 4 different docs. Step 5 loads `cross-encoder/ms-marco-MiniLM-L-6-v2` (~80 MB download) and reranks. Step 6 assembles `search_corpus_v2` — same envelope contract as Lab 06's `search_corpus`, with an added `retrieval_signals` dict per result (dense / bm25 / rerank). Step 7 wires the new pipeline into the Lab 06 agent loop unchanged. Step 8 (stretch) gives a calibration helper sweeping all four variants and reports hits / @top-1 / mean rank. Notebook outputs stripped; sample-output markdown cells throughout.
  - `quizzes/agentic-rag/retrieval-strategies.md` — 8 single-select questions covering: reranker candidate_k too small, BM25 vs dense failure-mode inversion, RRF k=60 robustness, MMR for redundant top-k, bi-encoder vs cross-encoder architecture (precomputation), score-scale non-transfer between cosine and rerank logits, picking the right intervention for a technical-corpus workload, and reasoning about stacked retrieval improvements. Same YAML front-matter + `<details>` reveal + `review:` field format as foundations quizzes.
  - `diagrams/retrieval-pipeline.mmd` — Mermaid source for the Lab 07 pipeline: query → split into dense + BM25 → RRF → optional MMR → cross-encoder rerank → score floor → top-k envelope. Per-stage latency annotations (CPU laptop) on the dotted edges. Same diagrammatic vocabulary (decision diamonds, terminal nodes, retriever/fusion/rerank class styling) as `rag-trajectory.mmd` and `research-agent-trajectory.mmd`.

- **Path 02 opening — Agentic RAG, first batch (Lab 06).**
  - `learning-paths/02-agentic-rag/README.md` — Path 02 entry README, modeled on Path 01's structure. Six numbered items across four modules: conceptual frame (3 concept pages), reference snapshots (2 tool snapshots), the from-scratch lab, and the quiz. Time estimate 6-9 hours for this first batch; the path grows over subsequent batches. Explicit anti-scope section names what's coming in later batches (re-ranking, hybrid search, contextual retrieval, RAG evaluation, framework bridge).
  - `concepts/rag/what-is-rag.md` — ~10 min concept page anchored to Lewis et al. (NeurIPS 2020). Covers the naive-vs-agentic distinction, the three failure modes RAG fixes (staleness, private-blindness, hallucination-under-uncertainty) and the three it doesn't (faithfulness, bad-retrieval propagation, citation hallucination), and "when naive RAG is enough."
  - `concepts/rag/retrieval-as-a-tool.md` — ~9 min concept page making the Lab 03 → Lab 06 transfer explicit. Tabulates which patterns transfer verbatim (loop, repeated-action detection, citation tracking, structured errors, step cap) and which change (low-similarity floor instead of paywalls, chunk-level citations instead of URL-level). Clarifies the common "agentic RAG means choosing whether to retrieve" misconception.
  - `concepts/rag/chunking-and-indexing.md` — ~12 min concept page on the stable retrieval decisions. Chunk size (~200-800 tokens with 512 default), overlap (~10-20%), boundary strategies (fixed / recursive / semantic), metadata schema, what a vector index *is* mechanically (a 2D array + metadata + similarity fn + search algorithm). Includes a 9-item retrieval-quality-knobs ranking and an explicit treatment of the 256-wordpiece foot-gun.
  - `concepts/rag/README.md` — section index for `concepts/rag/`. Lists current pages and forward-references the pending future pages (`retrieval-strategies.md`, `hybrid-search.md`, `contextual-retrieval.md`, `rag-evaluation.md`) so the IA is legible.
  - `tools/embeddings/snapshot-v1.0.md` — 🔴 verified snapshot for `sentence-transformers>=5.0,<6.0` (latest `5.5.1`, 2026-05-20) with `all-MiniLM-L6-v2` as the default (384-dim, 256-wordpiece max, ~80 MB on disk, Apache-2.0) and `text-embedding-3-small` as the production-oriented alternative (1536-dim default, 8192-token context, $0.02/1M tokens, Matryoshka-reducible). Honest tradeoffs on each, the 256-wordpiece foot-gun called out, why MiniLM is the right *pedagogical* default even though it isn't MTEB-SOTA. Excludes ada-002 with deprecation reasoning, considers and rejects mpnet, BGE, voyage, jina, and several others with one-line justifications.
  - `tools/embeddings/README.md` — section index.
  - `tools/vector-stores/snapshot-v1.0.md` — 🔴 survey of the 2026 vector-store landscape: Chroma, pgvector, Qdrant, Weaviate, Pinecone, plus FAISS as honorable mention. A decision aid, not a how-to — each entry covers when to use, when to watch for, the actual API surface, and a primary-source link. The headline lab doesn't use any of these; the page sets up the production paths.
  - `tools/vector-stores/README.md` — section index.
  - `labs/06-agentic-rag-from-scratch/README.md` — lab brief (~100-130 min, intermediate). First Path 02 lab; explicit anti-scope (no production vector store, no LangChain RAG, no re-ranking/hybrid/contextual retrieval, no Ragas, no multi-agent, no LangSmith).
  - `labs/06-agentic-rag-from-scratch/lab.ipynb` — 38-cell notebook (24 md / 14 code) building the entire RAG stack from scratch. Loads and chunks the bundled corpus at `TARGET_TOKENS=160` (deliberately under MiniLM's ~200-token effective cap), embeds with `all-MiniLM-L6-v2` (`normalize_embeddings=True` so cosine = dot product), stacks into a numpy `(n_chunks, 384)` index, exposes `search_corpus(query, top_k)` and `read_chunk(chunk_id)` as agent tools, runs the same agent loop as Lab 03 with chunk-level citation tracking via `_action_hash` repeated-action detection. Three test queries (easy/medium/hard), failure-mode walkthrough (off-corpus empty results, similar-but-not-quite-right retrieval, repeated-action refusal), stretch section swaps in `text-embedding-3-small` in ~15 lines. Notebook outputs stripped; sample-output markdown cells throughout.
  - `labs/06-agentic-rag-from-scratch/corpus/` — bundled Markdown corpus: 8 documents (~4,700 tokens total) covering Path 01 topics (agent loop, tool design, ReAct pattern, search-vs-retrieval, embeddings, vector indexes, chunking strategies, citation tracking). Chunker produces ~55 chunks at 160-token target with ~20% overlap; all chunks stay under MiniLM's 200-token truncation point. Corpus README explains why these specific documents (alignment with Foundations content + tuned to surface specific retrieval phenomena). Documents licensed under CC-BY-4.0 to match the rest of repo prose.
  - `quizzes/agentic-rag/rag-fundamentals.md` — 8 single-select questions on the naive-vs-agentic distinction, the two-tools triage pattern, `normalize_embeddings` semantics, the 256-wordpiece foot-gun, the structural citation property, the similarity-floor design choice, the Lab 03 → Lab 06 transfer, and the "when to upgrade from numpy" decision. Same single-select format with `<details>` reveal and `review:` field anchoring as the foundations quizzes.
  - `diagrams/rag-trajectory.mmd` — Mermaid source for the RAG agent's trajectory: search → triage → read → synthesize → cite, with failure-recovery branches (empty/irrelevant → refine; not_found → next; all-tried → refine) and step-cap escape paths. Companion to Lab 03's `research-agent-trajectory.mmd`; the parallel structure is intentional.

- **Foundations content — multi-step research agent (Lab 03).**
  - `concepts/tools/search-tools.md` — ~9 min concept page on how search tools differ from deterministic ones. Covers the two-tools pattern (`web_search` + `fetch_page`), top-k triage, snippet vs full-page tradeoffs, freshness scoping, attribution and citation tracking, the failure-modes table (empty results, noisy snippets, timeout, paywall, irrelevant pages, rate limit, blocked, redirected), and an explicit "why search is not RAG" comparison. Closes the conceptual gap before Path 02.
  - `tools/search/snapshot-v1.0.md` — 🔴 verified snapshot for the search backends used in Lab 03. Pins `ddgs>=9.0,<10` (verified 2026-05-24, latest `9.14.4`) as the default no-API-key option and `tavily-python>=0.5` as the production-oriented alternative. Documents the `duckduckgo-search` → `ddgs` rename and the metasearch fallback behavior (Bing/Google/Brave/DDG/etc.). Includes the "for educational purposes only" disclaimer flag, Tavily's 1,000/month free tier (verified at time of writing), and a freshness-check protocol with five primary-source verifications.
  - `tools/search/README.md` — section index for the search tools snapshots folder.
  - `labs/03-multi-step-research-agent/README.md` — lab brief (~90–120 min, intermediate). First lab that touches the real internet; explicit anti-scope list (no vector DBs, no embeddings, no multi-agent, no LangSmith, no JS-rendered pages).
  - `labs/03-multi-step-research-agent/lab.ipynb` — 35-cell notebook (23 md / 12 code) building a from-scratch research agent against the real web. Two tools (`web_search` wrapping `ddgs.text(...)` with `DDGSException`/`RatelimitException`/`TimeoutException` handling; `fetch_page` wrapping `requests` + `beautifulsoup4` with HTTP status/timeout/paywall handling). Loop adds `_action_hash`-based repeated-action detection on `(tool_name, args)` and a `citations` list maintained by the loop (not the LLM). Three test queries (easy / medium / hard) followed by an explicit failure-mode walkthrough (empty results, paywall detection, repeated-action refusal). Stretch section demonstrates Tavily backend swap using verified `time_range` parameter. Outputs stripped; sample-output markdown cells after key steps.
  - `quizzes/foundations/multi-step-research-agent.md` — 8 questions on the two-tools pattern, citation-tracking semantics, search failure modes, the `_action_hash` mechanism, the `too_long` structured status, the search-vs-RAG distinction, and when to switch from `ddgs` to a paid backend. Same single-select format with `<details>` reveal and `review:` field anchoring as the other foundations quizzes.
  - `diagrams/research-agent-trajectory.mmd` — Mermaid source for the research-agent trajectory diagram: search → triage → fetch → re-search → synthesize → cite, with explicit failure-recovery branches (empty → refine, blocked → next, all-failed → refine) and step-cap escape paths.

- **Foundations bridge to frameworks — LangGraph rewrite of Lab 01.**
  - `concepts/agents/agents-vs-frameworks.md` — when does a framework pay off? Eight-dimension decision table covering readability, state, debugging, reliability, checkpointing, human approval, maintainability, and learning value. Honest about tradeoffs; explicitly notes that frameworks don't fix tool-design problems.
  - `tools/langgraph/snapshot-v1.0.md` — 🔴 verified tool snapshot for LangGraph `1.x` series, anchored to LangChain's [1.0 announcement (2025-10-22)](https://blog.langchain.com/langchain-langgraph-1dot0/) and the [official migration guide](https://docs.langchain.com/oss/python/migrate/langgraph-v1). Pins the APIs the labs use (`StateGraph`, `MessagesState`, `add_messages`, `ToolNode`, `tools_condition`, `InMemorySaver`, `interrupt`/`Command`, `create_agent`). Documents the `create_react_agent` → `create_agent` migration and the TypedDict-only state requirement gotcha. Includes a freshness check protocol for future updates.
  - `tools/langgraph/README.md` — section index for forthcoming LangGraph pages.
  - `labs/05-langgraph-rewrite/README.md` — lab brief (~90–120 min, intermediate).
  - `labs/05-langgraph-rewrite/lab.ipynb` — 39-cell notebook (25 md / 14 code). Step-by-step rebuild of Lab 01's agent in LangGraph 1.x, then two extensions Lab 01 couldn't do: (a) checkpointing with `InMemorySaver` + thread_id-based resume, (b) human-in-the-loop with `interrupt(...)` + `Command(resume=...)`. Also covers `create_agent` as the high-level alternative, and `.stream(...)` for live trace observation. Outputs stripped; sample-output markdown cells after key steps. Same domain, same queries as Lab 01 — only the wiring changes.
  - `quizzes/foundations/langgraph-basics.md` — 8 questions testing *what LangGraph adds* (state, persistence, interrupts), not API syntax. Includes the key trap question: "what changes about the model?" → nothing.
  - `diagrams/langgraph-state-flow.mmd` — Mermaid source for the LangGraph state flow (model ↔ tools loop with checkpointer overlay).

- **Foundations content — tool design and selection.**
  - `concepts/tools/tool-design.md` — name, description, schema, return contract, executor; patterns (one-tool-per-intent, discriminated unions, pagination); seven common tool-design mistakes mapped to symptom/cause/fix.
  - `concepts/tools/tool-selection.md` — the four selection levers (system prompt, descriptions, history, `tool_choice`); five selection-failure modes; pruning strategies for large toolsets; tool-count guidance table.
  - `concepts/tools/README.md` — section index.
  - `labs/02-tool-design-and-selection/README.md` — lab brief, ~90–120 min, beginner-friendly.
  - `labs/02-tool-design-and-selection/lab.ipynb` — 32-cell notebook (19 md / 13 code) demonstrating the broken-tools → fixed-tools comparison on a mock e-commerce backend. Same agent code, two toolsets, observable behavior difference. Covers strict-mode Pydantic schemas (`ConfigDict(extra="forbid")`), structured errors, destructive-action gates, `tool_choice` (auto/required/none/named), `parallel_tool_calls`, and a stretch router pattern. Notebook outputs stripped; sample outputs in markdown cells.
  - `diagrams/react-loop.mmd` — Mermaid source for the ReAct thought/action/observation diagram (distinct from the general 4-step `agent-loop.mmd`).

- **Foundations quizzes — first batch.**
  - `quizzes/README.md` — quiz hub, format specification (YAML front-matter + `<details>` static rendering), and contribution rules.
  - `quizzes/foundations/agents-basics.md` — 8 questions on `what-is-an-agent.md`.
  - `quizzes/foundations/agent-loop.md` — 8 questions on `agent-loop.md`.
  - `quizzes/foundations/react-pattern.md` — 8 questions on `react-pattern.md`.
  - `quizzes/foundations/tool-design-and-selection.md` — 8 questions on the two tool concept pages and Lab 02.
  - Format: single-select only, 6–8 questions per quiz, difficulty tags (`easy`/`medium`/`hard`), stable per-question IDs (`q1`–`q8`), `review:` field anchoring each question to a specific source section. YAML front-matter as the source of truth; static `<details>` reveal blocks render natively on GitHub. The format is designed to be parseable by a future interactive renderer (deferred sibling project `agentic-ai-engineer-web`) with zero content rewriting.

- **First curriculum content batch — Foundations.**
  - `concepts/agents/what-is-an-agent.md` — foundational concept page; the most-linked page in the repo.
  - `concepts/agents/agent-loop.md` — the four-step perceive/reason/act/observe cycle.
  - `concepts/agents/react-pattern.md` — ReAct prompting pattern with Yao et al. (ICLR 2023) citation.
  - `math-foundations/notation.md` — symbol and convention reference.
  - `math-foundations/04-agents-as-policies.md` — first real math page; $\pi_\theta(a_t \mid s_t)$ framing.
  - `math-foundations/06-react-formalization.md` — ReAct as a specialization of the policy.
  - `labs/01-first-agent-from-scratch/README.md` — lab brief.
  - `labs/01-first-agent-from-scratch/lab.ipynb` — ~150-line ReAct agent in pure Python, provider-agnostic (OpenAI default, Anthropic swap-in). Notebook outputs stripped; sample outputs in markdown cells.
  - `learning-paths/01-foundations/README.md` — curated reading list for the Foundations path.
  - `diagrams/agent-loop.mmd` — Mermaid source for the canonical agent-loop diagram.

- **`SECURITY.md`** — closes the last Community Standards row; private reporting channel via GitHub Security Advisories.

### Changed

- **`.lycheeignore`** — removed `^.*/learning-paths/02-agentic-rag/?$` now that Path 02 has authored content (Batch 10 lands `learning-paths/02-agentic-rag/README.md`). Added forward reference for `labs/06-agentic-rag-from-scratch/solution/` (solution notebooks land in a dedicated future batch covering Labs 01, 02, 03, and 06 together). Updated notes for newly authored content: `concepts/rag/` and `tools/embeddings/`, `tools/vector-stores/` are now resolved.
- **`learning-paths/01-foundations/README.md`** — Module 3 expanded to incorporate Lab 03: inserted `concepts/tools/search-tools.md` + `tools/search/snapshot-v1.0.md` + `labs/03-multi-step-research-agent/` into the Module 3 sequence between Lab 02 and the math module. Module 6 (Quizzes) gains a fifth quiz entry (`multi-step-research-agent.md`). Now 22 numbered items across 6 modules. Flowchart adds two new nodes (S1 = Search tools concept, R = Lab 03) bridging Lab 02 and the math module. Time estimate bumped from 12–18 to 14–20 hours; the "things this path doesn't cover" section now points learners to Path 02 for the RAG counterpart and notes that Lab 03's citation pattern transfers. References gain Lewis et al. (2020) RAG paper as the contrast point for Lab 03's "search is not RAG" framing. Earlier in this Unreleased cycle: expanded from 5 to 6 modules with the framework bridge; before that, from 3 to 5 with the tool-design module.
- **`.lycheeignore`** — added forward reference for `labs/03-multi-step-research-agent/solution/` (solution notebooks land in a dedicated future batch covering Labs 01, 02, 03 together). Updated notes for newly authored content: `concepts/tools/search-tools.md` and `tools/search/` are now resolved and removed from the forward-reference notes. Earlier in this Unreleased cycle: removed forward-reference patterns resolved by batch 8 (`concepts/agents/agents-vs-frameworks.md`, `tools/langgraph/`, `labs/05-langgraph-rewrite/`, `quizzes/foundations/langgraph-basics.md`).
- **`CITATION.cff`** — `date-released` set to actual release date (`2026-05-23`). Passes `cffconvert --validate`.
- **`.lycheeignore`** — removed patterns for content now authored (concept pages, math notes, lab 01, learning-paths/01-foundations; tool concept pages, Lab 02, quizzes). Kept patterns for forthcoming labs (03, 04, 05, …), patterns/, recipes/, projects/, and tools/ pages that haven't been authored yet.
- **`.github/workflows/ci.yml`** — cleaner empty-repo handling, `markdownlint` made informational, lychee uses auto-detected `.lycheeignore` (no broken `--exclude-path` flag); ruff switched from `nbqa` to native notebook support (drops `nbqa` dependency, fixes per-file-ignores not applying to notebooks).
- **`pyproject.toml`** — added `[tool.uv] package = false` and removed empty `[tool.hatch.build.targets.wheel]` block to fix `uv sync` failing on modern Hatchling. Added `I001` to notebook per-file-ignores in `[tool.ruff.lint.per-file-ignores]`.
- **Internal links** in `README.md`, `CONTRIBUTING.md`, `LICENSING.md`, `docs/start-here.md`, `tools/README.md`, `diagrams/README.md` — converted GitHub-relative URLs (`../../issues`, `../../discussions`) to absolute `https://github.com/MHHamdan/Agentic-AI-Engineer/...` URLs; de-linked template placeholder paths to avoid false-positive link errors.

### Fixed

- Two CI failures from the initial v0.1.0 push: `Validate metadata` (placeholder date in `CITATION.cff`) and `Check Markdown links` (49 broken or forward-reference links). All CI jobs now pass.
- CI lint failures from notebook handling: `nbqa ruff` was bypassing per-file-ignores from `pyproject.toml`; switched to native ruff 0.6+ notebook support and added `I001` to notebook per-file-ignores. Fixed 3 real lint issues in `lab.ipynb` (E401 split-import, UP035 `typing.Callable` → `collections.abc.Callable`, F541 unneeded f-prefix), and 1 in Lab 02's `lab.ipynb` (B007 unused tuple-unpack variable `fn` → `_fn`).
- `uv sync` failure: modern Hatchling rejects empty `packages = []` declaration; replaced with canonical `[tool.uv] package = false` virtual-root declaration. `[build-system]` retained for future `pip install -e .` compatibility.
- Lab 01 link bug: `math-foundations/04-agents-as-policies.md` linked to `../../labs/...` when it should have been `../labs/...`.

### Verified Tool Snapshots

- **Anthropic Contextual Retrieval technique** — verified 2026-05-24 against [anthropic.com/engineering/contextual-retrieval](https://www.anthropic.com/engineering/contextual-retrieval) (canonical post, published Sep 19, 2024). The technique uses two sub-techniques (Contextual Embeddings + Contextual BM25) and has these published metrics on Anthropic's internal benchmarks (top-20 retrieval failure rate, lower is better): baseline 5.7% → Contextual Embeddings 3.7% (35% reduction) → +Contextual BM25 2.9% (49% reduction) → +Reranking 1.9% (67% reduction). The verified verbatim prompt template prepends `<document>{{WHOLE_DOCUMENT}}</document>` followed by `<chunk>{{CHUNK_CONTENT}}</chunk>` followed by an instruction to produce a "short succinct context to situate this chunk within the overall document." Resulting context is 50-100 tokens. Cost with prompt caching: ~$1.02 per million document tokens (assuming 800-token chunks, 8K-token documents, 50-token instruction, 100-token context output per chunk). Used in Lab 08. Full snapshot in concept page: [`concepts/rag/contextual-retrieval.md`](./concepts/rag/contextual-retrieval.md).
- **Anthropic prompt caching pricing** — verified 2026-05-24 against [platform.claude.com/docs/en/build-with-claude/prompt-caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching). Multipliers on base input token price: 5-minute cache write = 1.25×; 1-hour cache write = 2.0×; cache read (hit or refresh) = 0.1× (90% discount). Break-even: 1 cache hit for 5-min TTL; 2 cache hits for 1-hour TTL. ZDR-eligible — Anthropic doesn't store raw cache content, only KV representations + cryptographic hashes in memory. Used in Lab 08's concept page to support the cost-question section.
- **HyDE paper** — verified 2026-05-24. Gao, L., Ma, X., Lin, J., & Callan, J. (2022). *Precise Zero-Shot Dense Retrieval without Relevance Labels*. arXiv:2212.10496. Published Dec 20, 2022. Accepted at ACL 2023 (Annual Meeting of the Association for Computational Linguistics). Source paper for HyDE pattern in Lab 08 step 4. The original paper averages 5 hypothetical document embeddings per query to reduce variance.
- **Query2doc paper** — verified 2026-05-24. Wang, L., Yang, N., & Wei, F. (2023). *Query2doc: Query Expansion with Large Language Models*. arXiv:2303.07678. Published Mar 14, 2023 (v1); Oct 11, 2023 (v2). Accepted at EMNLP 2023. Source paper for the multi-query expansion pattern in Lab 08 step 5.
- **Rewrite-Retrieve-Read paper** — verified 2026-05-24. Ma, X., Gong, Y., He, P., Zhao, H., & Duan, N. (2023). *Query Rewriting for Retrieval-Augmented Large Language Models*. arXiv:2305.14283. Formalizes the rewriter-as-preprocessing pattern. Referenced in `concepts/rag/query-rewriting.md` adjacent-techniques section.
- **Seven Failure Points paper** — verified 2026-05-24. Barnett, S., Kurniawan, S., Thudumu, S., Brannelly, Z., & Abdelrazek, M. (2024). *Seven Failure Points When Engineering a Retrieval Augmented Generation System*. arXiv:2401.05856. A field study of real RAG failure modes; complementary to `concepts/rag/retrieval-failure-modes.md` taxonomy (the curriculum's page is 8 modes; this paper is 7).

- `rank-bm25` `>=0.2.2,<0.3` — verified 2026-05-24. Latest: `0.2.2`. Apache-2.0; sole dependency is numpy. Snyk classifies maintenance as "Inactive" (no release in >12 months) but the package is stable, not abandoned — the BM25 algorithm itself hasn't changed and the implementation has held up across ~6.2M downloads/month per pypistats. API confirmed via live `inspect.signature` against installed `0.2.2`: `BM25Okapi(corpus, tokenizer=None, k1=1.5, b=0.75, epsilon=0.25)` with defaults matching Robertson & Walker's standard. `get_scores(query) → np.ndarray`. Used in Lab 07 for the BM25 retrieval step. For production scale (10K+ chunks with high query volume), the path is `bm25s` (Lù 2024, arXiv:2407.03618) which uses scipy-sparse for orders-of-magnitude speedup; for lab-scale work `rank-bm25` is the right call. Source: [pypi.org/project/rank-bm25](https://pypi.org/project/rank-bm25/); [github.com/dorianbrown/rank_bm25](https://github.com/dorianbrown/rank_bm25).
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (model weights) — verified 2026-05-24. 6-layer MiniLM backbone (~22M params, ~80 MB on disk), trained on MS MARCO passage reranking dataset (Nogueira & Cho 2019 lineage). Apache-2.0. Output: raw logits in roughly `[-15, +15]` range (higher = more relevant), or `[0, 1]` if `activation_fn=torch.nn.Sigmoid()` is passed. Throughput per model card: ~1800 docs/sec on V100 GPU; CPU is ~30-50 pairs/second, adequate for ~30-candidate reranking. Loaded via `sentence_transformers.CrossEncoder` (no new package install — `sentence-transformers 5.x` from Lab 06 provides it). The hub has both `L-6` and `L6` aliases pointing to the same weights; Lab 07 uses the canonical `L-6` form. Used in Lab 07 step 5. Source: [huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2); [sbert.net cross-encoder pretrained models](https://www.sbert.net/docs/cross_encoder/pretrained_models.html).
- `sentence-transformers` `CrossEncoder` API — verified 2026-05-24 against installed `5.5.1` via live `inspect.signature`. `CrossEncoder(model_name_or_path, device=None, max_length=None, activation_fn=None, ...)`. `predict(inputs: list[PairInput], batch_size=32, show_progress_bar=None, activation_fn=None, apply_softmax=False, convert_to_numpy=True, ...) → np.ndarray`. Used in Lab 07 alongside the already-snapshotted `SentenceTransformer` bi-encoder API.

- `sentence-transformers` `>=5.0,<6.0` — verified 2026-05-24. Latest: `5.5.1` (May 20, 2026). Production/Stable per PyPI classifiers; Apache-2.0; requires Python `>=3.10`. Maintained by Tom Aarsen (Nils Reimers' successor); the `5.x` line introduced ONNX/OpenVINO backends as alternatives to the default torch backend. `SentenceTransformer.encode()` signature confirmed via live `inspect.signature` against the installed library — returns `np.ndarray` by default (`convert_to_numpy=True`), has `normalize_embeddings: bool = False` parameter (set `True` so cosine similarity reduces to a dot product). Used in Lab 06. Source: [pypi.org/project/sentence-transformers](https://pypi.org/project/sentence-transformers/); [github.com/UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers). Full snapshot: [`tools/embeddings/snapshot-v1.0.md`](./tools/embeddings/snapshot-v1.0.md).
- `sentence-transformers/all-MiniLM-L6-v2` (model weights) — verified 2026-05-24. 384-dim mean-pooled BERT embedding, max sequence length 256 wordpieces (silently truncates beyond), ~80 MB on disk, Apache-2.0. Based on `nreimers/MiniLM-L6-H384-uncased`. The 256-wordpiece truncation point is the single most common foot-gun with this model; Lab 06 chunks at 160 tokens with ~32-token overlap to stay safely under it. Source: [huggingface.co/sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).
- `text-embedding-3-small` (OpenAI, optional alternative for Lab 06) — verified 2026-05-24. 1536-dim default with Matryoshka-style reduction via the `dimensions` parameter, 8192-token context, $0.02/1M tokens standard (50% off via Batch API). Source: [developers.openai.com/api/docs/models/text-embedding-3-small](https://developers.openai.com/api/docs/models/text-embedding-3-small).
- `openai` SDK `2.38.0` — verified 2026-05-24 (released May 21, 2026). `client.embeddings.create(model=..., input=...)` API has been stable across the `1.x` and `2.x` major versions. Used in Lab 06's stretch section for the OpenAI embedding swap.
- Vector store landscape survey — verified 2026-05-24. Chroma, pgvector, Qdrant, Weaviate, Pinecone, plus FAISS as honorable mention. Decision aid only — not pinned to specific versions because each has its own release cadence and the survey would go stale faster than the underlying market consolidates. Full survey: [`tools/vector-stores/snapshot-v1.0.md`](./tools/vector-stores/snapshot-v1.0.md).
- `ddgs` `>=9.0,<10` — verified 2026-05-24. Latest: `9.14.4` (May 15, 2026). Production/Stable per PyPI classifiers; MIT; requires Python `>=3.10`. Renamed from `duckduckgo-search` in 2024 (PyPI page for legacy name now points to the new package). Now a metasearch library aggregating Bing, Brave, DuckDuckGo, Google, Mojeek, Startpage, Yandex, Yahoo, Wikipedia, and Grokipedia with automatic fallback. Result schema: `list[{"title", "href", "body"}]`. Carries an explicit "for educational purposes only" disclaimer. Used as the default search backend in Lab 03. Source: [pypi.org/project/ddgs](https://pypi.org/project/ddgs/); [github.com/deedy5/ddgs](https://github.com/deedy5/ddgs). Full snapshot: [`tools/search/snapshot-v1.0.md`](./tools/search/snapshot-v1.0.md).
- `tavily-python` `>=0.5` — verified 2026-05-24. Tavily's official Python SDK; LLM/RAG-optimized search API. Free tier 1,000 calls/month, no credit card required per Tavily's signup documentation. `client.search(...)` API confirmed via live `inspect.signature` to use `time_range="day"|"week"|"month"|"year"` (not the older `days` integer pattern). Result schema: `response["results"]` is `list[{"title", "url", "content", "score"}]`. Used in Lab 03's stretch section as the production-oriented alternative. Source: [docs.tavily.com/sdk/python/reference](https://docs.tavily.com/sdk/python/reference).
- `beautifulsoup4` `>=4.12` — verified 2026-05-24 (used in Lab 03's `fetch_page` for HTML → text extraction; `html.parser` parser).
- `requests` `>=2.31` — verified 2026-05-24 (used in Lab 03's `fetch_page` for HTTP with timeout, redirect, and User-Agent handling).
- `langgraph` `>=1.0,<2.0` — verified 2026-05-23. Latest: `1.2.1` (Apr 2026). GA on 2025-10-22 with public commitment to no breaking changes until 2.0. Used in Lab 05. Source: [LangChain & LangGraph 1.0 announcement](https://blog.langchain.com/langchain-langgraph-1dot0/); [LangGraph v1 migration guide](https://docs.langchain.com/oss/python/migrate/langgraph-v1); [Releases on GitHub](https://github.com/langchain-ai/langgraph/releases). Full snapshot: [`tools/langgraph/snapshot-v1.0.md`](./tools/langgraph/snapshot-v1.0.md).
- `langchain` `>=1.0,<2.0` — verified 2026-05-23. The `langchain.agents.create_agent` entry point replaces the deprecated `langgraph.prebuilt.create_react_agent`. Used in Lab 05 as the recommended high-level helper.
- `langchain-openai` and `langchain-anthropic` `>=0.2` — verified 2026-05-23. The LangGraph-friendly provider wrappers used in Lab 05.
- `openai` ≥ 1.40 — verified 2026-05-23 (used in Labs 01, 02, and 03; `tool_choice` modes and `parallel_tool_calls` exercised in Lab 02; function-calling with structured-error tool returns in Lab 03).
- `anthropic` ≥ 0.34 — verified 2026-05-23 (used in Labs 01, 02, and 03 as alternative provider).
- `pydantic` ≥ 2.7 — verified 2026-05-23 (used for tool schemas; strict-mode patterns with `ConfigDict(extra="forbid")` and `Literal` types demonstrated in Lab 02).

---

## [0.1.0] — Initial public release

The first public release of the Agentic AI Engineer learning hub. This release establishes the repository's identity, structure, and infrastructure. Content sections are scaffolded but mostly empty — they fill in over subsequent releases.

### Added

- **Root identity.** `README.md` defining mission, audience, and structure. Dual-license declaration (Apache-2.0 for code, CC-BY-4.0 for prose and diagrams).
- **Community infrastructure.**
  - `CONTRIBUTING.md` with content templates for concepts, labs, recipes, and tool-page updates.
  - `CODE_OF_CONDUCT.md` based on the Contributor Covenant.
  - `CITATION.cff` for academic citation.
  - `CHANGELOG.md` (this file) with versioning and tool-snapshot policies.
- **Top-level scaffold.** Empty directories with stub READMEs for:
  - `docs/` — onboarding and FAQ
  - `learning-paths/` — nine curated paths
  - `concepts/` — stable explainers
  - `math-foundations/` — engineer-useful math
  - `labs/` — hands-on guided exercises
  - `recipes/` — copy-paste solutions
  - `patterns/` — architecture patterns
  - `projects/` — Build Challenges and Capstone Projects
  - `examples/` — minimal reference implementations
  - `tools/` — versioned snapshots
  - `evaluation/`, `production/`, `security/`
  - `diagrams/`, `references/`, `glossary/`, `setup/`, `assets/`
- **Onboarding pages.**
  - `docs/start-here.md` — 5-minute repo tour.
  - `setup/README.md` — environment setup.
  - `learning-paths/README.md` — path overview and prerequisite map.
- **License files.** `LICENSE` (Apache-2.0), `LICENSE-CC-BY-4.0` (Creative Commons Attribution 4.0).
- **Environment scaffolding.** `pyproject.toml`, `.env.example`, `.gitignore`.

### Changed

- *(N/A — initial release.)*

### Fixed

- *(N/A — initial release.)*

### Verified Tool Snapshots

The following snapshots were checked against official sources at the time of release. Each `tools/<tool>/` page carries its own verification footer with the source link.

| Tool / Spec | Version / Status | Verified | Primary source |
|---|---|---|---|
| Model Context Protocol | Spec `2025-11-25` (current stable); RC `2026-07-28` announced | 2026-05-23 | [modelcontextprotocol.io/specification/2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25); [MCP blog — RC announcement](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) |
| Agent2Agent (A2A) Protocol | `v1.0` released; Linux Foundation project since June 2025 | 2026-05-23 | [a2a-protocol.org](https://a2a-protocol.org/latest/); [Announcing v1.0](https://a2a-protocol.org/latest/announcing-1.0/) |
| LangGraph | `1.0` GA (Oct 2025); `langgraph.prebuilt` deprecated → `langchain.agents` | 2026-05-23 | [LangGraph 1.0 GA — changelog](https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available) |
| LangChain | `1.0` GA (Oct 2025); introduces `create_agent`, middleware system | 2026-05-23 | [LangChain 1.0 GA — changelog](https://changelog.langchain.com/announcements/langchain-1-0-now-generally-available) |
| LangSmith | Snapshot pending; see `tools/langsmith/` for current verification | — | [changelog.langchain.com](https://changelog.langchain.com/) |
| Google ADK | Snapshot pending; see `tools/google-adk/` | — | [google.github.io/adk-docs](https://google.github.io/adk-docs/) |
| CrewAI | Snapshot pending; see `tools/crewai/` | — | Official repo and docs |
| AutoGen | Snapshot pending; see `tools/autogen/` | — | Official repo and docs |
| OpenAI Agents SDK | Snapshot pending; see `tools/openai-agents-sdk/` | — | Official repo and docs |
| Vector DBs (pgvector, Pinecone, Qdrant, Weaviate, Chroma) | Snapshots pending per page | — | Official docs per tool |

"Snapshot pending" means the tool page exists or is planned but a full verification pass has not yet been completed for this release. Contributions to fill in pending snapshots are welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md#how-to-update-a-tools-page).

---

## How to use this file as a contributor

When you open a PR that changes content meaningfully, add an entry under the appropriate subsection of `[Unreleased]`. Use the past tense and link to the changed pages. Maintainers will move `[Unreleased]` to a numbered release when cutting a tag.

Examples of good entries:

```
### Added
- `recipes/parse-structured-output-safely.md` — Pydantic-based parser with retry on validation failure.
- `concepts/agents/reflection-pattern.md` — explainer on self-correcting agent loops with Reflexion citation.

### Changed
- `tools/langgraph/state-and-checkpoints.md` — rewrote for `langgraph.checkpoint.postgres` API changes.

### Verified Tool Snapshots
- `tools/langgraph/` — bumped to `1.2.x`, verified YYYY-MM-DD. Source: [link].
```

Trivial changes (typo fixes, broken links) don't need changelog entries.
