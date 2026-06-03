# Lab 60 · Reference solution

Complete implementation of [Lab 60](../README.md).

## What this is

- **`SharedSpaceEmbedder`** — encodes visual content only (CLIP/SigLIP stand-in).
- **`CaptionThenEmbedder`** — captions visual content + OCR of in-image text, then embeds.
- **`recall_at_1` / `grounded_answer`** — retrieval by query type, and the retrieval-vs-grounding split.

## Expected results

- Visual queries recall@1 1.00 for both; text-in-image recall@1 shared 0.00 vs caption 1.00.
- `grounded_answer(shared, "what was Q4 revenue")` is `None`; the caption path returns the number.

## Implementation choices

1. **Disjoint visual / in-image-text vocabulary** so the "CLIP can't read" failure is genuine.
2. **Zero-signal retrieval is a miss**, not a lucky tie.
3. **Pluggable embedders** — swap the stand-ins for a real vision-language model.

## Running

```bash
cd labs/60-multimodal-rag-runnable
python multimodal.py --self-test
```
