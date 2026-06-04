# Lab 61 · Reference solution

Complete implementation of [Lab 61](../README.md).

## What this is

- **`evaluate(embedder, noisy_ids, ungrounded_ids)`** — runs the retrieve → read → generate pipeline and returns recall, mean CER, grounding rate, end-to-end accuracy, and a first-failing-stage attribution.
- **Stand-in stages** — `SharedSpaceEmbedder` / `CaptionThenEmbedder`, an OCR `read_text` (corruptible), a `generate` that can be grounded or hallucinate.

## Expected results

- Shared-space: 0.00 accuracy, all failures attributed to retrieval.
- Caption clean: 1.00 accuracy.
- Noisy OCR and ungrounded both 0.75 accuracy — attributed to OCR and grounding respectively.

## Implementation choices

1. **First-failing-stage precedence** retrieval → OCR → grounding; the attribution partitions every query.
2. **Grounded-but-wrong** is an OCR failure (grounding stays 1.00).
3. **Pluggable stages** — swap the stand-ins for a real vision-language stack.

## Running

```bash
cd labs/61-grading-multimodal-rag
python mm_eval.py --self-test
```
