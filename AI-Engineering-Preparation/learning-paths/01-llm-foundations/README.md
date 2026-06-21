# Path 01: LLM foundations

What a language model actually does, in plain terms: how text becomes tokens, how tokens become vectors, how attention mixes them, and why the model's knowledge is frozen at training time. This path builds the vocabulary the rest of the track assumes.

> Status: **delivered** (Batch 01). Concept notes, a runnable lab, a math page, and a diagram are in place.

## Learning objectives

- Describe tokenization, embeddings, and the attention mechanism without the math getting in the way.
- Explain the context window as a budget and why position affects what the model uses.
- Distinguish decoding settings (temperature, top-p) and their effect on output.
- Name the failure modes — hallucination, staleness — and when fine-tuning vs. retrieval is the right fix.

## Modules

| # | Note | Topic |
|---|---|---|
| 1 | [Tokens and embeddings](../../concepts/llm/tokens-and-embeddings.md) | tokenization (BPE), embeddings, the token budget |
| 2 | [Attention, conceptually](../../concepts/llm/attention.md) | queries/keys/values, multi-head, position |
| 3 | [The context window](../../concepts/llm/context-window.md) | what fills it; lost-in-the-middle |
| 4 | [Decoding and sampling](../../concepts/llm/decoding-and-sampling.md) | temperature, top-p, determinism |
| 5 | [Hallucination and knowledge cutoff](../../concepts/llm/hallucination-and-cutoff.md) | causes and mitigations |
| 6 | [Fine-tuning vs. retrieval](../../concepts/llm/fine-tuning-vs-retrieval.md) | a decision guide |

## Lab

- [`labs/01-tokenization-and-embeddings/`](../../labs/01-tokenization-and-embeddings/) — build byte-pair encoding and count-based PPMI embeddings from scratch; offline, deterministic, with self-tests.

## Math

- [`math-foundations/01-embeddings-and-similarity.md`](../../math-foundations/01-embeddings-and-similarity.md) — vectors, dot product, cosine, PPMI, nearest neighbors.

## Diagram

- [`diagrams/text-to-prediction.md`](../../diagrams/text-to-prediction.md) — text → tokenize → embed → layers → logits → decode.

## Concept areas in this path

- [`concepts/llm`](../../concepts/llm/)

## References

Canonical sources for this path are collected in [`references/references.md`](../../references/references.md). Curriculum sequencing only; all explanations are original. See [`STYLE.md`](../../STYLE.md).
