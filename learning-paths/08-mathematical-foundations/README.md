# Path 08 — Mathematical Foundations

> 🟢 → 🔴 (mixed) · ⏱ 6–10 hours of focused reading, plus reading the cited papers · 📍 Read alongside the other paths, not in isolation · ✅ **v1 COMPLETE — all 13 math pages authored** (Batches 53 + 67) · 🔧 **Batch 68 refresh** — every page rewritten with a richer template (Python code examples, "Common mistakes," "Related pages") and clean GitHub-rendered LaTeX

> ✅ **Path 08 v1 is complete and refreshed.** All 13 math pages are authored and live in [`math-foundations/`](../../math-foundations/). The path-opening pair (pages 04 and 06) shipped in Batch 53; the remaining 11 pages (01, 02, 03, 05, 07, 08, 09, 10, 11, 12, 13) shipped in Batch 67 as the closing batch. Batch 68 rewrote every page end-to-end with a richer template, fixed broken LaTeX rendering artifacts, and added executable Python examples per page. Together with [`README.md`](../../math-foundations/README.md) and [`notation.md`](../../math-foundations/notation.md), the path is one of the v1-complete surfaces in the repo.

## Who this path is for

Engineers who want to understand the math behind agentic AI without reading a textbook. You've seen $\pi_\theta(a_t \mid s_t)$ in an agent paper and skipped past it; you've heard "RAG marginalization" and wondered if it's a real thing; you want to read [Anthropic's research](https://www.anthropic.com/research) and [arXiv papers on agents](https://arxiv.org/list/cs.AI/recent) without getting stuck on notation. This path is one short note per concept — each equation justified by a downstream engineering decision, never math for its own sake.

## What you'll be able to do

When this path is complete, you'll be able to:

- **Read an agentic-AI paper without getting stuck on notation.** The notation cheat sheet at [`math-foundations/notation.md`](../../math-foundations/notation.md) is the one source of truth for $\pi$, $s$, $a$, $\theta$, $z$, and the rest.
- **Reason about retrieval quality formally** — the RAG formulation $p(y \mid x) = \sum_z p(y \mid x, z) \, p(z \mid x)$ makes the chunking-vs-reranking trade-off precise rather than intuitive.
- **Debug agent behavior with the right vocabulary** — when an agent loops or hands off badly, having the MDP / POMDP intuition makes the failure mode visible at the right abstraction level.
- **Connect each math page to specific engineering decisions** — every page links to a concrete lab or concept page. Math here exists because it changes what you build.
- **Run a working Python example for each concept** — Batch 68 added a minimal, executable code snippet per page tying the math directly to the OpenAI API, embedding cosines, ReAct loops, MDP runners, knapsack selectors, and so on.

## Prerequisites

- **Undergraduate-level probability and linear algebra.** No measure theory, no functional analysis, no PhD-level material.
- **No reinforcement-learning background required** — RL terminology (state, action, policy, reward) is introduced where it comes up.
- **Comfort with mathematical notation in markdown** (`$...$` inline, `$$...$$` block) is helpful for reading but not for using the material.

## Page template (refreshed in Batch 68)

Every math page follows this expanded structure:

1. **Why this matters for agentic AI** — the engineering motivation in two or three sentences.
2. **The equation** — clean GitHub-rendered LaTeX, with every symbol defined immediately below.
3. **How to read this equation** — a plain-language walkthrough.
4. **Mathematical intuition** — the underlying ideas.
5. **Where this appears in agentic systems** — specific connections to repo content.
6. **Code example** — a minimal, executable Python snippet.
7. **Common mistakes** — failure modes engineers actually run into.
8. **Repo cross-references** — direct links into concepts, labs, and patterns.
9. **Related pages** — what to read next.
10. **References** — papers and textbooks with one-sentence relevance notes.

The Batch 67 template had the first half; Batch 68 added sections 6, 7, 9 (explicit), and tightened section 10. The refresh also removed broken LaTeX spacing artifacts (`\;=\;` patterns that rendered as visible semicolons on GitHub KaTeX) and replaced em-dashes inside `math-foundations/` with ASCII hyphens for consistent rendering across clients.

## Path structure (✅ 13 v1 pages refreshed + page 14 added in the RAG upgrade)

This path differs from the other paths: each page is a self-contained short note (8 to 10 min of reading), not a multi-module sequence. Read whichever pages help you with whichever paper or lab is in front of you.

| # | Topic | Status |
|---|---|---|
| 01 | **Language model probability** — $p(x_t \mid x_{<t})$, sampling, temperature, top-p, perplexity | ✅ Refreshed — [`01-language-model-probability.md`](../../math-foundations/01-language-model-probability.md) |
| 02 | **Embeddings and vector similarity** — cosine, dot-product, normalized vs unnormalized; the geometry behind retrieval | ✅ Refreshed — [`02-embeddings-vector-similarity.md`](../../math-foundations/02-embeddings-vector-similarity.md) |
| 03 | **RAG formulation** — $p(y \mid x) = \sum_z p(y \mid x, z) \, p(z \mid x)$; chunking, retrieval, marginalization | ✅ Refreshed — [`03-rag-formulation.md`](../../math-foundations/03-rag-formulation.md) |
| 04 | **Agents as policies** — $\pi_\theta(a_t \mid s_t)$; the policy-conditional view of an agent | ✅ Refreshed — [`04-agents-as-policies.md`](../../math-foundations/04-agents-as-policies.md) |
| 05 | **MDP / POMDP intuition** — belief state, partial observability, why agents-as-MDP-policies matters | ✅ Refreshed — [`05-mdp-pomdp.md`](../../math-foundations/05-mdp-pomdp.md) |
| 06 | **The ReAct loop, formalized** — the loop structure of tool-using agents | ✅ Refreshed — [`06-react-formalization.md`](../../math-foundations/06-react-formalization.md) |
| 07 | **Tool selection as function selection** — the tool-routing decision view | ✅ Refreshed — [`07-tool-selection.md`](../../math-foundations/07-tool-selection.md) |
| 08 | **Planning and search** — task decomposition, planning trees, plan-and-execute | ✅ Refreshed — [`08-planning-search.md`](../../math-foundations/08-planning-search.md) |
| 09 | **Memory models** — short-term, long-term, retrieval-augmented memory architectures | ✅ Refreshed — [`09-memory-models.md`](../../math-foundations/09-memory-models.md) |
| 10 | **Multi-agent coordination graphs** — supervisor, hierarchical, swarm — the graph-theoretic view | ✅ Refreshed — [`10-multi-agent-coordination.md`](../../math-foundations/10-multi-agent-coordination.md) |
| 11 | **Evaluation metrics** — precision, recall, faithfulness, LLM-as-judge, calibration | ✅ Refreshed — [`11-evaluation-metrics.md`](../../math-foundations/11-evaluation-metrics.md) |
| 12 | **Uncertainty and safety** — entropy, calibration, abstention, HITL routing | ✅ Refreshed — [`12-uncertainty-safety.md`](../../math-foundations/12-uncertainty-safety.md) |
| 13 | **Context-window optimization** — knapsack selection, lost-in-the-middle, reorder | ✅ Refreshed — [`13-context-window-optimization.md`](../../math-foundations/13-context-window-optimization.md) |
| 14 | **Retrieval and ranking metrics** — precision@k, recall@k, MRR, MAP, NDCG, context precision/recall | ✅ Added (RAG upgrade) — [`14-retrieval-ranking-metrics.md`](../../math-foundations/14-retrieval-ranking-metrics.md) |

Plus the supporting pages:
- ✅ [`README.md`](../../math-foundations/README.md) — the math-foundations directory landing page (refreshed)
- ✅ [`notation.md`](../../math-foundations/notation.md) — one source of truth for $\pi$, $s$, $a$, $\theta$, $z$, and friends (refreshed with GitHub KaTeX rendering notes)

## What you can read right now

All 13 math pages plus 2 supporting files are authored, refreshed, and on disk in [`math-foundations/`](../../math-foundations/):

**Foundations + entry points**:
- 📖 [Math Foundations landing](../../math-foundations/README.md) — the directory introduction; explains the page template
- 📖 [Notation cheat sheet](../../math-foundations/notation.md) — the symbol-and-notation reference; bookmark this and refer back as you read the rest

**The 13 content pages** (in numerical order; each 8 to 10 minutes):
- 📖 [Page 01 — Language model probability](../../math-foundations/01-language-model-probability.md)
- 📖 [Page 02 — Embeddings and vector similarity](../../math-foundations/02-embeddings-vector-similarity.md)
- 📖 [Page 03 — RAG formulation as marginalization](../../math-foundations/03-rag-formulation.md)
- 📖 [Page 04 — Agents as policies](../../math-foundations/04-agents-as-policies.md)
- 📖 [Page 05 — MDP / POMDP intuition](../../math-foundations/05-mdp-pomdp.md)
- 📖 [Page 06 — The ReAct loop, formalized](../../math-foundations/06-react-formalization.md)
- 📖 [Page 07 — Tool selection as function selection](../../math-foundations/07-tool-selection.md)
- 📖 [Page 08 — Planning and search](../../math-foundations/08-planning-search.md)
- 📖 [Page 09 — Memory models](../../math-foundations/09-memory-models.md)
- 📖 [Page 10 — Multi-agent coordination graphs](../../math-foundations/10-multi-agent-coordination.md)
- 📖 [Page 11 — Evaluation metrics](../../math-foundations/11-evaluation-metrics.md)
- 📖 [Page 12 — Uncertainty and safety](../../math-foundations/12-uncertainty-safety.md)
- 📖 [Page 13 — Context-window optimization](../../math-foundations/13-context-window-optimization.md)
- 📖 [Page 14 — Retrieval and ranking metrics](../../math-foundations/14-retrieval-ranking-metrics.md) — added in the RAG evaluation upgrade; the IR metrics (precision@k, recall@k, MRR, MAP, NDCG) behind retrieval evaluation

Each page is independently readable; the cross-references between pages let you navigate by curiosity rather than sequence.

## How to use this path

Two reasonable approaches per the math-foundations README:

- **Theory-first.** Read all 13 pages before touching the rest of the repo. You'll have a clearer mental model of why things are built the way they are. Total reading time: around 1.5 to 2 hours for the 13 content pages.
- **As-you-go.** Skip math pages until something in a concept or lab surprises you. Then come back. Most concept pages have a *"🧮 Math behind it"* callout that links into the right page here; the [`glossary/terms.md`](../../glossary/terms.md) entries for mathematical terms also link to the corresponding math pages.

Either works. The pages are short enough that skipping won't leave you stranded.

## What's not in this path (anti-scope)

These remain explicitly out of scope:

- **Deep RL math** — Bellman equations beyond intuition, policy-gradient derivations, actor-critic algorithm proofs. Path 08 stays at the *engineering*-useful level; if you want the full RL machinery, *Sutton & Barto* is the canonical reference.
- **Information-theoretic measures beyond cross-entropy and Shannon entropy** — KL divergence and friends appear where needed; the rest stays in textbooks.
- **Probabilistic graphical models in generality** — Bayes nets, MRFs, variational inference. Path 08 covers the *agentic* slice.
- **Embedding-model architecture math** — transformer math, attention derivations, positional encoding. There are excellent textbooks (Goodfellow's *Deep Learning*, Phuong & Hutter's *Formal Algorithms for Transformers*) and we don't re-derive them.
- **Causal inference, statistical learning theory, optimization theory**. Useful background but not directly tested by daily agentic-AI engineering decisions.

## What comes next

Path 08 v1 is complete and refreshed. Contributions are still welcome — math pages have stricter rules than other content types per [`CONTRIBUTING.md`](../../CONTRIBUTING.md): every equation must cite its source; no invented equations; no close paraphrases of someone else's formulation without attribution.

Directions for continuous improvement:

- **Add worked numerical examples.** The current pages establish the equation, the engineering implications, and one minimal code example. Adding "here's what this looks like with concrete numbers from a real run" would deepen intuition.
- **Add per-framework code references.** "Repo cross-references" currently points at the labs in this repo; a parallel "where you'll see it in LangGraph / CrewAI / Pydantic AI" section would help readers map the math onto whichever framework they're using.
- **Extend the page set with workload-specific pages.** Pages 01 through 14 cover the universal core plus retrieval metrics. Topics like "speculative decoding math," "RLHF objective derivation," or "DPO loss" could become Page 15+ if the community needs them.

Open an issue describing the proposed addition before writing — math pages get more review than other content types because the citation-rigor bar is higher.

## References

The foundational sources Path 08 builds on:

**Texts** (the references the pages cite):
- Goodfellow, Bengio, Courville (2016), *Deep Learning* — the deep-learning foundation
- Sutton & Barto (2018), *Reinforcement Learning: An Introduction* (2nd ed.) — the canonical RL reference; Page 04 (policies) and Page 05 (MDPs) cite this
- Phuong & Hutter (2022), *Formal Algorithms for Transformers* — the rigorous transformer formalization
- Russell & Norvig (2020), *Artificial Intelligence: A Modern Approach* (4th ed.) — the planning and search foundation; Page 08 cites this

**Papers** (foundational results the pages cite):
- Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — the RAG marginalization formulation Page 03 builds on
- Yao et al. (2022), *ReAct: Synergizing Reasoning and Acting in Language Models* — Page 06's foundational source
- Wei et al. (2022), *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models* — Page 06's adjacent reference
- Liu et al. (2023), *Lost in the Middle: How Language Models Use Long Contexts* — Page 13's foundational source for the U-shaped recall finding
- Es et al. (2023), *RAGAS: Automated Evaluation of Retrieval Augmented Generation* — Page 11's source for the faithfulness metric

**Standard references**:
- Bishop (2006), *Pattern Recognition and Machine Learning* — probability and statistical foundations
- Manning, Raghavan, Schutze (2008), *Introduction to Information Retrieval* — Page 11's reference for IR metrics

**Adjacent repo content**:
- [`math-foundations/`](../../math-foundations/) — the directory this path indexes; 13 of 13 pages authored and refreshed
- [Path 01 Foundations](../01-foundations/) — Lab 01's ReAct loop is what Page 06 formalizes
- [Path 02 Agentic RAG](../02-agentic-rag/) — Page 03 (RAG formulation) is the math behind it
- [Path 03 Multi-Agent Systems](../03-multi-agent-systems/) — Page 10 (multi-agent coordination graphs) is the formal companion
- [Path 06 Evaluation & Observability](../06-evaluation-observability/) — Page 11 (evaluation metrics) extends Path 06's measurement vocabulary
- [`glossary/terms.md`](../../glossary/terms.md) — the per-term entry points; mathematical glossary entries link to the corresponding math pages
