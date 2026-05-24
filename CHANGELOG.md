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
