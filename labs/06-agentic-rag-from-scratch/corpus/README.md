# Lab 06 corpus

This folder contains the bundled document corpus that Lab 06's RAG agent retrieves from. It's deliberately small and tightly scoped so the learner can read every document and build intuition for what's retrievable.

## Contents

| File | Topic | ~Tokens |
|------|-------|---------|
| [01-agent-loop.md](./01-agent-loop.md) | The four-phase agent loop and stopping conditions | ~520 |
| [02-tool-design.md](./02-tool-design.md) | Tool design patterns and structured errors | ~560 |
| [03-react-pattern.md](./03-react-pattern.md) | The ReAct pattern (thought-action-observation) | ~530 |
| [04-search-vs-retrieval.md](./04-search-vs-retrieval.md) | Why search and retrieval are different patterns | ~570 |
| [05-embeddings.md](./05-embeddings.md) | What embeddings are and how they behave | ~640 |
| [06-vector-indexes.md](./06-vector-indexes.md) | From numpy to production vector stores | ~660 |
| [07-chunking-strategies.md](./07-chunking-strategies.md) | Chunk size, overlap, boundaries, metadata | ~660 |
| [08-citation-tracking.md](./08-citation-tracking.md) | Why citations must be tracked structurally | ~570 |

Total: 8 documents, ~4,700 tokens, ~24 chunks after splitting at 200 tokens with 20% overlap.

## Why these documents

The corpus covers topics from Foundations (Path 01) so a learner working through Lab 06 can ask questions whose answers they already roughly know. This makes it easy to evaluate retrieval quality: if the agent answers "how does the agent loop work?" with content from `01-agent-loop.md` and cites the right chunks, retrieval is working as expected.

The documents are also deliberately tuned to demonstrate specific retrieval phenomena:

- Some topics are covered in **one document only** (e.g., the ReAct pattern is in `03-react-pattern.md`) — clean retrieval.
- Some topics are covered **across multiple documents** (e.g., chunking shows up in both `07-chunking-strategies.md` and `05-embeddings.md` via the token-limit discussion) — synthesis required.
- Some content **straddles chunk boundaries** at the default chunk size — surfaces the chunking-failure mode discussed in `concepts/rag/chunking-and-indexing.md`.

## Licensing

These documents are original prose written for this curriculum and are licensed under [Creative Commons Attribution 4.0 International (CC-BY-4.0)](../../../LICENSE-CC-BY-4.0), matching the rest of the prose in this repository.

You're welcome to use, modify, and redistribute these documents in your own projects. Attribution is appreciated but enforced lightly — the spirit is "this is shared educational material."

## Modifying the corpus

If you want to experiment with a different corpus:

1. Keep documents under ~1000 tokens each to make chunking behavior visible.
2. Vary the depth of topical coverage so retrieval has something to differentiate.
3. Keep documents text-only (no images, no tables that depend on rendering).
4. If you use external sources, check their licensing and update the LICENSING.md in the lab folder.

The lab notebook reads everything in this folder ending in `.md`. New files are picked up automatically on the next index build.
