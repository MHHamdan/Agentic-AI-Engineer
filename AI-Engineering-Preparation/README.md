# AI Engineering Preparation

A structured, open preparation hub for **AI engineering** roles and system design — built inside the [Agentic AI Engineer](../) repository as a companion track. It turns the moving pieces of modern LLM and agent systems into a navigable curriculum: learning paths, modular concept notes, runnable labs, capstone projects, diagrams, a glossary, and a curated set of canonical references.

> Status: **Batch 00 — scaffold.** This commit establishes the structure and the curriculum map. Content modules (concept notes, labs, diagrams, projects) land in later batches.

## Learning paths

| # | Path | Scope |
|---|---|---|
| 01 | [LLM foundations](./learning-paths/01-llm-foundations/) | Tokens, embeddings, attention, context windows, decoding, hallucination, and fine-tuning vs. retrieval. |
| 02 | [ML & RL fundamentals](./learning-paths/02-ml-and-rl-fundamentals/) | The ML lifecycle (data → features → training → serving), feature stores, drift; RL primitives, policy gradients, RLHF. |
| 03 | [Retrieval & memory](./learning-paths/03-retrieval-and-memory/) | RAG end-to-end, vector databases / ANN, agent state vs. memory, the memory lifecycle, and context engineering. |
| 04 | [Agents, patterns & protocols](./learning-paths/04-agents-patterns-protocols/) | The agent loop and tool use, agentic design patterns, the Model Context Protocol, and multi-agent coordination. |
| 05 | [Evaluation & delivery](./learning-paths/05-evaluation-and-delivery/) | Offline/online evaluation, LLM-as-judge, regression gates, the AI-assisted coding workflow, and system-design capstones. |

## Repository map

```text
AI-Engineering-Preparation/
├── learning-paths/      # ordered curriculum; one path per cluster
├── concepts/            # modular concept notes, grouped by area (12 areas)
├── labs/                # runnable, self-tested, offline-first exercises
├── projects/            # capstones that tie several areas together (5)
├── math-foundations/    # the math behind embeddings, attention, RL, and eval
├── diagrams/            # reusable Mermaid sources
├── glossary/            # shared vocabulary
└── references/          # canonical papers, standards, and official docs
```

## Counts

| Item | Now | Plan |
|---|---|---|
| Learning paths | 5 | 5 |
| Concept areas | 12 | 12 |
| Concept notes | 0 | grows per batch |
| Labs | 0 | grows per batch |
| Projects (specs) | 5 | 5, then built out |
| Math-foundations pages | 0 | grows per batch |

## Content policy

This track is original educational material. The external articles used to shape the curriculum are treated only as a topic and sequencing guide: no text is copied, and no author names, newsletter names, or personal attributions from them appear anywhere here. Technical claims cite their original sources — papers, standards, official documentation, specifications, and benchmarks. See [`STYLE.md`](./STYLE.md) and [`references/references.md`](./references/references.md).

## How this is built

Development proceeds in numbered **batches**, the same way the parent repository is built. Each content batch ships a coordinated set — concept notes, at least one runnable lab, a diagram, new glossary terms, references, and navigation updates — verified before it is marked done. Batch 00 is the scaffold; see [`CHANGELOG.md`](./CHANGELOG.md) for history.

## License

Dual-licensed: code under Apache-2.0, prose and diagrams under CC-BY-4.0. See [`LICENSE`](./LICENSE).
