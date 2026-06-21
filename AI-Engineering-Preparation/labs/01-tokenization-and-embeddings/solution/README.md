# Lab 01 · Reference solution

Complete implementation of [Lab 01](../README.md).

## What this is

- **`bpe.py`** — deterministic byte-pair encoding (`train`, `encode`, `decode`, `build_vocab`).
- **`embeddings.py`** — co-occurrence + PPMI embeddings with cosine similarity (`Embeddings`, `cosine`).

## Expected results

- `newer` → 1 token; unseen `colder` → 5 tokens; round-trip holds.
- PPMI widens the related/unrelated gap from 0.23 to 0.93; nearest to `cat` is `dog`.

## Running

```bash
cd labs/01-tokenization-and-embeddings
python bpe.py --self-test
python embeddings.py --self-test
python bpe.py --encode tokenization
python embeddings.py --nearest cat
```
