# Path 08 — Mathematical Foundations

> 🟢 → 🔴 (mixed) · ⏱ 6–10 hours (planned, plus reading the cited papers) · 📍 Read alongside the other paths, not in isolation · 📋 **Scaffold — content forthcoming (some math pages already authored)**

> ⚠️ **This path is a scaffold.** The [`math-foundations/`](../../math-foundations/) directory already contains four authored pages — README, notation cheat sheet, agents-as-policies, ReAct formalization. The remaining nine planned pages land in future batches. The "What you can read right now" section below points at those four real, on-disk pages.

## Who this path is for

Engineers who want to understand the math behind agentic AI without reading a textbook. You've seen $\pi_\theta(a_t \mid s_t)$ in an agent paper and skipped past it; you've heard "RAG marginalization" and wondered if it's a real thing; you want to read [Anthropic's research](https://www.anthropic.com/research) and [arXiv papers on agents](https://arxiv.org/list/cs.AI/recent) without getting stuck on notation. This path is one short note per concept — each equation justified by a downstream engineering decision, never math for its own sake.

## What you'll be able to do

When this path is complete, you'll be able to:

- **Read an agentic-AI paper without getting stuck on notation.** The notation cheat sheet at [`math-foundations/notation.md`](../../math-foundations/notation.md) is the one source of truth for $\pi$, $s$, $a$, $\theta$, $z$, and the rest.
- **Reason about retrieval quality formally** — the RAG formulation $p(y \mid x) = \sum_z p(y \mid x, z)\, p(z \mid x)$ makes the chunking-vs-reranking trade-off precise rather than intuitive.
- **Debug agent behavior with the right vocabulary** — when an agent loops or hands off badly, having the MDP / POMDP intuition makes the failure mode visible at the right abstraction level.
- **Connect each math page to specific engineering decisions** — every page in this path has a *"Where you'll see it in the code"* section linking to a concrete lab or concept page. Math here exists because it changes what you build.

## Prerequisites

- **Undergraduate-level probability and linear algebra.** No measure theory, no functional analysis, no PhD-level material.
- **No reinforcement-learning background required** — RL terminology (state, action, policy, reward) is introduced where it comes up.
- **Comfort with mathematical notation in markdown** (`$...$` inline, `$$...$$` block) is helpful for reading but not for using the material.

## Path structure (planned — 4 of 13 pages authored)

This path differs from the other paths: each page is a self-contained short note (~5-10 min), not a multi-module sequence. Read whichever pages help you with whichever paper or lab is in front of you.

| # | Topic | Status |
|---|---|---|
| 01 | **Language model probability** — $p(x_t \mid x_{<t})$, sampling, temperature, top-p | 📋 Planned |
| 02 | **Embeddings and vector similarity** — cosine, dot-product, normalized vs unnormalized; the geometry behind retrieval | 📋 Planned |
| 03 | **RAG formulation** — $p(y \mid x) = \sum_z p(y \mid x, z)\, p(z \mid x)$; chunking, retrieval, marginalization | 📋 Planned |
| 04 | **Agents as policies** — $\pi_\theta(a_t \mid s_t)$; the policy-conditional view of an agent | ✅ Authored — [`04-agents-as-policies.md`](../../math-foundations/04-agents-as-policies.md) |
| 05 | **MDP / POMDP intuition** — belief state, partial observability, why agents-as-MDP-policies matters | 📋 Planned |
| 06 | **The ReAct loop, formalized** — the loop structure of tool-using agents | ✅ Authored — [`06-react-formalization.md`](../../math-foundations/06-react-formalization.md) |
| 07 | **Tool selection as function selection** — the tool-routing decision view | 📋 Planned |
| 08 | **Planning and search** — task decomposition, planning trees, plan-and-execute | 📋 Planned |
| 09 | **Memory models** — short-term, long-term, retrieval-augmented memory architectures | 📋 Planned |
| 10 | **Multi-agent coordination graphs** — supervisor, hierarchical, swarm — the graph-theoretic view | 📋 Planned |
| 11 | **Evaluation metrics** — precision, recall, faithfulness, latency, cost — definitions and pathologies | 📋 Planned |
| 12 | **Uncertainty and safety** — calibration, hallucination, refusal patterns | 📋 Planned |
| 13 | **Context-window optimization** — constrained selection; the formal counterpart to Path 05 | 📋 Planned |

Plus the supporting pages:
- ✅ [`README.md`](../../math-foundations/README.md) — the math-foundations directory landing page
- ✅ [`notation.md`](../../math-foundations/notation.md) — one source of truth for $\pi$, $s$, $a$, $\theta$, $z$, and friends

## What you can read right now

Four real, authored math pages sit in [`math-foundations/`](../../math-foundations/) on disk today:

- 📖 [Math Foundations landing](../../math-foundations/README.md) — the directory introduction; explains the page template (equation → mathematical intuition → why it matters for engineers → where you'll see it in the code → source)
- 📖 [Notation cheat sheet](../../math-foundations/notation.md) — the symbol-and-notation reference; bookmark this and refer back as you read the rest
- 📖 [Page 04 — Agents as policies](../../math-foundations/04-agents-as-policies.md) — $\pi_\theta(a_t \mid s_t)$; the policy-conditional view of an agent; how policy parameters $\theta$ map to system prompt + tools + scaffolding
- 📖 [Page 06 — The ReAct loop, formalized](../../math-foundations/06-react-formalization.md) — the loop structure of tool-using agents; connects to Lab 01's ReAct implementation

These four pages establish the template, the notation, and two of the most-used concepts (policies and ReAct). The remaining nine pages will follow the same shape — short, equation-grounded, with explicit "where this shows up in the code" sections.

## How to use this path

Two reasonable approaches per the math-foundations README:

- **Theory-first.** Read all 13 pages (currently 4) before touching the rest of the repo. You'll have a clearer mental model of why things are built the way they are.
- **As-you-go.** Skip math pages until something in a concept or lab surprises you. Then come back. Most concept pages will eventually have a *"🧮 Math behind it"* callout that links into the right page here.

Either works. The pages are short enough that skipping won't leave you stranded.

## What's not in this path (anti-scope)

When all 13 pages are authored, these remain explicitly out of scope:

- **Deep RL math** — Bellman equations beyond intuition, policy-gradient derivations, actor-critic algorithm proofs. Path 08 stays at the *engineering*-useful level; if you want the full RL machinery, *Sutton & Barto* is the canonical reference.
- **Information-theoretic measures beyond cross-entropy** — KL divergence appears where needed; the rest stays in textbooks.
- **Probabilistic graphical models in generality** — Bayes nets, MRFs, variational inference. Path 08 covers the *agentic* slice: agents-as-policies, RAG-as-marginalization, MDPs-as-environment-models.
- **Embedding-model architecture math** — transformer math, attention derivations, positional encoding. There are excellent textbooks (Goodfellow's *Deep Learning*, Phuong & Hutter's *Formal Algorithms for Transformers*) and we don't re-derive them.
- **Causal inference, statistical learning theory, optimization theory**. Useful background but not directly tested by daily agentic-AI engineering decisions.

## What comes next

Contributions are very welcome. Math pages have stricter rules than other content types per [`CONTRIBUTING.md`](../../CONTRIBUTING.md): every equation must cite its source; no invented equations; no close paraphrases of someone else's formulation without attribution.

The way to help:

1. **Pick one page from the 9 planned.** Each is self-contained.
2. **Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md)** — the source-citation rules in particular.
3. **Use the page template** in [`math-foundations/README.md`](../../math-foundations/README.md) — equation → mathematical intuition → why it matters for engineers → where you'll see it in the code → source.

The natural next-page priorities are Page 01 (LM probability — useful in every later page), Page 02 (embeddings — the most-asked-about), and Page 03 (RAG formulation — most-cited in Path 02 + Path 06 content).

## References

The foundational sources Path 08 builds on:

**Texts** (the references the planned pages will cite):
- Goodfellow, Bengio, Courville (2016), *Deep Learning* — the deep-learning foundation
- Sutton & Barto (2018), *Reinforcement Learning: An Introduction* (2nd ed.) — the canonical RL reference; Page 04 (policies) and Page 05 (MDPs) cite this
- Phuong & Hutter (2022), *Formal Algorithms for Transformers* — the rigorous transformer formalization

**Papers** (foundational results the pages will cite):
- Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — the RAG marginalization formulation Page 03 will build on
- Yao et al. (2022), *ReAct: Synergizing Reasoning and Acting in Language Models* — Page 06's foundational source
- Wei et al. (2022), *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models* — Page 06's adjacent reference

**Standard references**:
- Bishop (2006), *Pattern Recognition and Machine Learning* — probability and statistical foundations
- Wasserman (2004), *All of Statistics* — the most concise statistics reference for working engineers

**Adjacent repo content**:
- [`math-foundations/`](../../math-foundations/) — the directory this path indexes; four pages already authored
- [Path 01 Foundations](../01-foundations/) — Lab 01's ReAct loop is what Page 06 formalizes
- [Path 02 Agentic RAG](../02-agentic-rag/) — Page 03 (RAG formulation) is the math behind it
- [Path 03 Multi-Agent Systems](../03-multi-agent-systems/) — Page 10 (multi-agent coordination graphs) will be the formal companion
- [Path 06 Evaluation & Observability](../06-evaluation-observability/) — Page 11 (evaluation metrics) extends Path 06's measurement vocabulary
