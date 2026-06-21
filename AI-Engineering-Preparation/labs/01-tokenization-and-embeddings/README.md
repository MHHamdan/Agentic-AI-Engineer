# Lab 01: Tokenization and embeddings from scratch

> 🟢 Foundational · ⏱ ~60–75 min · 📚 Path 01 (LLM foundations)

## 🎯 Goal

Build the two operations every LLM starts with — turning text into token ids, and tokens into vectors — from scratch, so the rest of the track rests on something concrete rather than a black box.

By the end you should be able to:

- Implement byte-pair encoding (BPE) and explain why a model counts tokens, not words.
- Explain the "tokenization tax": why a rare or unusual string costs more tokens.
- Build an embedding from co-occurrence counts and use cosine similarity to rank related words.
- Explain why PPMI re-weighting beats raw counts, and how this connects to vector search.

## 🛠 Modules

| File | What it does |
|---|---|
| `bpe.py` | deterministic byte-pair encoding: `train`, `encode`, `decode`, `build_vocab` (`--self-test`, `--encode WORD`) |
| `embeddings.py` | co-occurrence + PPMI embeddings and cosine similarity: `Embeddings`, `cosine` (`--self-test`, `--nearest WORD`) |

## What the numbers say

- BPE: the trained word `newer` → 1 token; the unseen word `colder` → 5 tokens. Token counts, not word counts, fill the context window.
- Embeddings: raw counts give `cos(cat,dog)=0.77`, `cos(cat,car)=0.77` (frequent words dominate); PPMI gives `cos(cat,dog)=1.00`, `cos(cat,car)=0.07` — meaning, not frequency.

## Design choices and tradeoffs

- **Deterministic BPE.** Ties between equally-frequent pairs are broken lexicographically, so the merge list is reproducible — important for a tokenizer, where the ids must be stable.
- **Counts as embeddings.** The distributional hypothesis (words in similar contexts have similar meanings) means co-occurrence rows already are embeddings; you do not need a network to see the idea.
- **PPMI over raw counts.** Raw counts reward ubiquity; PPMI rewards association beyond chance, which is what makes the vectors track meaning.

## Common gotchas

- **Word count ≠ token count.** Budget and cost are in tokens; a document of rare strings is more expensive than its word count suggests.
- **Out-of-vocabulary characters.** This tiny corpus has no byte-level base, so an unseen character has no id; production tokenizers use a 256-byte base so nothing is truly OOV.
- **Cosine, not distance.** Similarity here is the angle between vectors, bounded in [-1, 1]; it is the same operation a vector database runs at scale.

## 🧮 Going deeper

- 📐 [math-foundations/01](../../math-foundations/01-embeddings-and-similarity.md) — vectors, dot product, cosine, and what "nearest" means.
- 📖 [concepts/llm/tokens-and-embeddings.md](../../concepts/llm/tokens-and-embeddings.md).

## References

- Sennrich, Haddow, Birch (2016). *Neural Machine Translation of Rare Words with Subword Units.* arXiv:1508.07909.
- Mikolov et al. (2013). *Efficient Estimation of Word Representations in Vector Space.* arXiv:1301.3781.
- Levy & Goldberg (2014). *Neural Word Embedding as Implicit Matrix Factorization.*
