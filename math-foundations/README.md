# Math foundations

Engineer-useful math for agentic AI systems. Every page here exists because the equation makes you a better engineer — not because it makes the curriculum look rigorous.

> ✅ **All 13 pages authored** (Batch 67). The folder is complete at v1 — every entry in the table below is a live link.

## What lives here

Thirteen short notes, each focused on one piece of theory:

| # | Topic | Connects to |
|---|---|---|
| 01 | [Language model probability — $p(x_t \mid x_{<t})$](./01-language-model-probability.md) | sampling, temperature, top-p |
| 02 | [Embeddings and vector similarity](./02-embeddings-vector-similarity.md) | RAG retrieval |
| 03 | [RAG formulation — $p(y \mid x) = \sum_z p(y \mid x, z)\, p(z \mid x)$](./03-rag-formulation.md) | every RAG decision |
| 04 | [Agents as policies — $\pi_\theta(a_t \mid s_t)$](./04-agents-as-policies.md) | every agent design |
| 05 | [MDP / POMDP intuition](./05-mdp-pomdp.md) | belief state, partial observability |
| 06 | [The ReAct loop, formalized](./06-react-formalization.md) | tool-using agents |
| 07 | [Tool selection as function selection](./07-tool-selection.md) | tool routing |
| 08 | [Planning and search](./08-planning-search.md) | task decomposition |
| 09 | [Memory models](./09-memory-models.md) | short-term, long-term, retrieval |
| 10 | [Multi-agent coordination graphs](./10-multi-agent-coordination.md) | supervisor, hierarchical, swarm |
| 11 | [Evaluation metrics](./11-evaluation-metrics.md) | precision, recall, faithfulness, latency, cost |
| 12 | [Uncertainty and safety](./12-uncertainty-safety.md) | calibration, hallucination |
| 13 | [Context-window optimization](./13-context-window-optimization.md) | constrained selection |

A symbol-and-notation cheat sheet lives in [`notation.md`](./notation.md) (one source of truth for $\pi$, $s$, $a$, $\theta$, $z$, and friends).

## Page template

Every math page follows this format:

1. **The equation** — clean LaTeX, GitHub-flavored MathJax (`$...$` inline, `$$...$$` block).
2. **Mathematical intuition** — what it means, 2–4 sentences of plain language.
3. **Why it matters for engineers** — how it shows up in decisions you make.
4. **Where you'll see it in the code** — direct links to specific labs and concept pages.
5. **Source** — original paper or standard reference. No invented equations.

## How to use this folder

You don't have to read it linearly. Two reasonable approaches:

- **Theory-first.** Read math pages 1–13 before touching the rest of the repo. You'll have a clearer mental model of why things are built the way they are.
- **As-you-go.** Skip math pages until something in a concept or lab surprises you. Then come back. Most concept pages have a *"🧮 Math behind it"* callout that links into the right page here.

Either works. The pages are short enough that skipping won't leave you stranded.

## Prerequisites

- Undergraduate-level probability and linear algebra.
- No reinforcement-learning background required — RL terminology (state, action, policy, reward) is introduced where it comes up.

## See also

- [`glossary/terms.md`](../glossary/terms.md) — short definitions for mathematical terms used here (policy, MDP, POMDP, belief state, embedding, marginalization). The glossary entries link back to these pages for the full treatment.
- [`concepts/`](../concepts/) — the engineering side of every mathematical idea here.

## Contributing

Math pages must cite their sources. We don't accept invented equations or close paraphrases of someone else's formulation without attribution. The full source-citation rules are in [`CONTRIBUTING.md`](../CONTRIBUTING.md#citation-and-source-rules).

> 🟢 Content in this folder is classified **stable** — the math doesn't change.
