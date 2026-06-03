# Lab 60: Multimodal RAG, runnable

> 🟡 Intermediate · ⏱ ~65–80 min · 📚 Retrieval science · Module 27

## 🎯 Goal

The [multimodal-RAG concept page](../../concepts/rag/multimodal-rag.md) argued two architectures and one famous failure; this lab makes them runnable. A small corpus where each document has visual content *and* dense in-image text (a number in a chart) is indexed two ways, and the queries split into "what it looks like" vs "what it says".

By the end you should be able to:

- Contrast shared-space (CLIP/SigLIP) and caption-then-embed indexing on the same corpus.
- Reproduce the "CLIP can't read" failure on text-in-image queries.
- Separate retrieval from grounding/OCR as distinct eval metrics.

## 📋 Prerequisites

- 📖 [Multimodal RAG](../../concepts/rag/multimodal-rag.md) — the architectures and the failure modes.
- **Assumed background:** dense retrieval, recall@k, and the idea of a vision-language embedder.

**Setup:** Python 3.11+, standard library. The embedders are deterministic stand-ins; swap in a real vision-language embedder and the retrieval/eval code is unchanged.

## 🛠 Module

| Component | Notes |
|---|---|
| `multimodal.py` | `SharedSpaceEmbedder`, `CaptionThenEmbedder`, `recall_at_1`, `grounded_answer` (`--self-test`) |

## What the numbers say

| Query type | shared-space recall@1 | caption-then-embed recall@1 |
|---|---|---|
| Visual ("blue bar chart") | 1.00 | 1.00 |
| Text-in-image ("quarterly revenue") | 0.00 (can't read) | 1.00 |

## Design choices and tradeoffs

- **Shared-space is blind to printed text.** A CLIP-style embedder encodes appearance, not the numbers inside a chart, so a query whose answer is text-in-image fails — caption-then-embed runs OCR into the index and recovers it, at the cost of an offline captioning pass.
- **Retrieval ≠ grounding.** Even when shared-space retrieves the right figure, it can't return a number it never encoded. The two are separate metrics, and conflating them hides the cause of a wrong answer.
- **A hybrid keeps both indexes.** Shared-space for "looks like", captions for "says" — fused like hybrid text search.

## Common gotchas

- **Build eval items whose answer is only in the image**, or the suite can't tell a model that reads images from one that pattern-matches surrounding text.
- **Captioner errors are silent retrieval errors.** A mis-captioned chart fails retrieval in a way that looks like a retrieval bug; spot-check and version captions.
- **The stand-in guarantees the failure; a real model grades it.** Don't read the 0.00 as a universal constant — measure your own embedder.

## 🧮 Going deeper

- 📖 [Multimodal RAG](../../concepts/rag/multimodal-rag.md) and [RAG evaluation framework](../../concepts/evaluation/rag-evaluation-framework.md).
- 📖 [Lost in the middle](../../concepts/rag/lost-in-the-middle.md) — still applies once you assemble a long multimodal prompt.

## What comes next

Swap the stand-ins for a real vision-language embedder and generator, and grade retrieval, grounding, and OCR-reading separately on a corpus with answers that live only in the images.
