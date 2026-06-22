# Lab 03 · Reference solution

Complete implementation of [Lab 03](../README.md).

## What this is

- **`rag.py`** — a minimal RAG pipeline: TF-IDF retrieval, grounded extractive answer, citation, abstention (`Retriever`).
- **`ann.py`** — exact vs. IVF approximate nearest-neighbor search and the recall/scan tradeoff (`build_ivf`, `ivf_search`, `evaluate`).

## Expected results

- Distinctive queries ground to the correct source and cite it; out-of-corpus query abstains.
- IVF: nprobe=1 → recall@5 ≈ 0.79 scanning ~13%; nprobe=nlist → recall 1.00, 100% scanned.

## Running

```bash
cd labs/03-rag-and-ann
python rag.py --self-test
python rag.py --query "compress vectors to shrink memory"
python ann.py --self-test
python ann.py --demo
```
