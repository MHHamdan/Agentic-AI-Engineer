# LLM concepts

The vocabulary and mechanics of large language models, explained for engineers: how text is tokenized and embedded, how attention mixes tokens, what the context window holds, how decoding works, and why models hallucinate.

> Batch 01: notes delivered. This area now has its six foundational notes; the runnable companion is [`labs/01-tokenization-and-embeddings/`](../../labs/01-tokenization-and-embeddings/).

## Notes

1. [Tokens and embeddings](./tokens-and-embeddings.md) — text becomes token ids, tokens become vectors; why token counts fill the context window.
2. [Attention, conceptually](./attention.md) — queries, keys, values, and the softmax mix that defines the transformer.
3. [The context window](./context-window.md) — what competes for the budget, and why a bigger window is not a free fix.
4. [Decoding and sampling](./decoding-and-sampling.md) — temperature, top-p, top-k, and the limits of determinism.
5. [Hallucination and knowledge cutoff](./hallucination-and-cutoff.md) — why a frozen model fabricates, and the external fixes.
6. [Fine-tuning vs. retrieval](./fine-tuning-vs-retrieval.md) — a decision guide: change behavior vs. change knowledge.

## Key references

- Attention Is All You Need (transformers) — arXiv:1706.03762.
- Lost in the Middle (context position effects) — arXiv:2307.03172.
- Retrieval-Augmented Generation — arXiv:2005.11401.

See the full list in [`../../references/references.md`](../../references/references.md). All explanations are original; sources are cited, not reproduced ([`STYLE.md`](../../STYLE.md)).
