# Math foundations

Engineer-useful math for agentic AI systems. Every page exists because the equation makes you a better engineer, not because it makes the curriculum look rigorous.

> Refreshed in Batch 68 with a stronger template, code examples per page, and fully GitHub-compatible LaTeX rendering. Earlier `\;=\;` artifacts have been replaced with clean equations.

## What lives here

Fourteen short notes, each focused on one piece of theory:

| # | Topic | Connects to |
|---|---|---|
| 01 | [Language model probability](./01-language-model-probability.md) | sampling, temperature, top-p, perplexity |
| 02 | [Embeddings and vector similarity](./02-embeddings-vector-similarity.md) | RAG retrieval, semantic search |
| 03 | [RAG formulation](./03-rag-formulation.md) | every RAG decision, top-k, faithfulness |
| 04 | [Agents as policies](./04-agents-as-policies.md) | every agent design, RL framing |
| 05 | [MDP / POMDP intuition](./05-mdp-pomdp.md) | belief state, partial observability |
| 06 | [The ReAct loop, formalized](./06-react-formalization.md) | tool-using agents, the thought-action factor |
| 07 | [Tool selection as function selection](./07-tool-selection.md) | tool routing, tool collision |
| 08 | [Planning and search](./08-planning-search.md) | task decomposition, plan-and-execute |
| 09 | [Memory models](./09-memory-models.md) | short-term, long-term, retrieval-augmented |
| 10 | [Multi-agent coordination graphs](./10-multi-agent-coordination.md) | supervisor, hierarchical, swarm |
| 11 | [Evaluation metrics](./11-evaluation-metrics.md) | precision, recall, faithfulness, calibration |
| 12 | [Uncertainty and safety](./12-uncertainty-safety.md) | entropy, calibration, abstention |
| 13 | [Context-window optimization](./13-context-window-optimization.md) | budget allocation, lost-in-the-middle |
| 14 | [Retrieval and ranking metrics](./14-retrieval-ranking-metrics.md) | precision@k, recall@k, MRR, MAP, NDCG, context precision/recall |

A symbol-and-notation cheat sheet lives in [`notation.md`](./notation.md). One source of truth for `pi`, `s`, `a`, `theta`, `z`, and friends.

## Page template

Every math page follows this structure:

1. **Why this matters for agentic AI** - the engineering motivation in two or three sentences.
2. **The equation** - clean GitHub-rendered LaTeX, with every symbol defined immediately below.
3. **How to read this equation** - a plain-language walkthrough.
4. **Mathematical intuition** - the underlying ideas.
5. **Where this appears in agentic systems** - specific connections to repo content.
6. **Code example** - a minimal, executable Python snippet.
7. **Common mistakes** - failure modes engineers actually run into.
8. **Repo cross-references** - direct links into concepts, labs, and patterns.
9. **Related pages** - what to read next.
10. **References** - papers and textbooks with one-sentence relevance notes.

## How to use this folder

Two reasonable approaches:

- **Theory-first.** Read all 13 pages before touching the rest of the repo. Total reading time around 1.5 to 2 hours. You will have a clearer mental model of why things are built the way they are.
- **As-you-go.** Skip math pages until something in a concept or lab surprises you. Then come back. Most concept pages have a "Math behind it" callout that links into the right page here, and the [glossary](../glossary/terms.md) entries for mathematical terms link to the corresponding pages.

Either works. The pages are short enough that skipping will not leave you stranded.

## GitHub LaTeX rendering

These pages target GitHub-flavored Markdown with KaTeX support. The conventions:

- Inline math: `$...$` for short expressions.
- Display math: `$$...$$` on its own line, with blank lines before and after.
- No `\begin{align}` blocks. Use `aligned` inside a `$$...$$` block only when it renders cleanly across GitHub web and mobile.
- No backslash-spacing around equals signs. Write `a = b`, not `a \;=\; b` (the second form can render visible semicolons depending on the renderer).
- No raw LaTeX packages. KaTeX supports a subset of LaTeX. Stick to standard math symbols.

If you spot a rendering bug, please open an issue. The math layer should be precise enough to be useful and clean enough to read.

## Prerequisites

- Undergraduate-level probability and linear algebra.
- No reinforcement-learning background required. RL terminology (state, action, policy, reward) is introduced where it comes up.

## See also

- [`glossary/terms.md`](../glossary/terms.md) - short definitions for mathematical terms used here. Glossary entries link back to these pages for the full treatment.
- [`concepts/`](../concepts/) - the engineering side of every mathematical idea here.

## Contributing

Math pages have stricter rules than other content types. Every equation must cite its source. We do not accept invented equations or close paraphrases of someone else's formulation without attribution. The full source-citation rules are in [`CONTRIBUTING.md`](../CONTRIBUTING.md#citation-and-source-rules).

When adding a new equation, also add it to [`notation.md`](./notation.md) if it introduces a new symbol.

> Content in this folder is classified **stable**. The math does not change.
