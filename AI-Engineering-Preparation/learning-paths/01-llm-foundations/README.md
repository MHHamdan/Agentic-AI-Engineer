# Path 01: LLM foundations

What a language model actually does, in plain terms: how text becomes tokens, how tokens become vectors, how attention mixes them, and why the model's knowledge is frozen at training time. This path builds the vocabulary the rest of the track assumes.

## Learning objectives

- Describe tokenization, embeddings, and the attention mechanism without the math getting in the way.
- Explain the context window as a budget and why position affects what the model uses.
- Distinguish decoding settings (temperature, top-p) and their effect on output.
- Name the failure modes — hallucination, staleness — and when fine-tuning vs. retrieval is the right fix.

## Planned modules

1. Tokens and embeddings: from characters to vectors.
2. Attention and the transformer block, conceptually.
3. The context window: what fills it and why order matters.
4. Decoding and sampling: temperature, top-p, determinism.
5. Hallucination and knowledge cutoff: causes and mitigations.
6. Fine-tuning vs. retrieval: a decision guide.

## Concept areas in this path

- [`concepts/llm`](../../concepts/llm/)

## References

Canonical sources for this path are collected in [`references/references.md`](../../references/references.md). Curriculum sequencing only; all explanations are original. See [`STYLE.md`](../../STYLE.md).
