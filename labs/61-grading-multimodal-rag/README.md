# Lab 61: Grading multimodal RAG — retrieval, grounding, and OCR-reading

> 🔴 Advanced · ⏱ ~80–100 min · 📚 Builds on Lab 60 · Module 28

## 🎯 Goal

[Lab 60](../60-multimodal-rag-runnable/) showed retrieval failing on text-in-image queries. This lab is about what you measure once retrieval works: a multimodal answer can be wrong for three independent reasons — retrieval, OCR-reading, grounding — and a single end-to-end accuracy number cannot tell them apart. You build a grader that reports all three and attributes every wrong answer to its first failing stage.

By the end you should be able to:

- Compute retrieval recall, OCR-reading error (CER), and grounding rate as separate metrics.
- Attribute an end-to-end failure to the stage that caused it.
- Explain why "grounded" and "correct" differ — an answer can be perfectly grounded in misread text.

## 📋 Prerequisites

- 🧪 [Lab 60](../60-multimodal-rag-runnable/) (the two architectures and the "CLIP can't read" failure).
- 📖 [Grounding and OCR-reading](../../concepts/rag/grounding-and-ocr.md) — the failure taxonomy.
- 📐 [math-foundations/17](../../math-foundations/17-multimodal-eval-metrics.md) — the metrics and the decomposition.

**Setup:** Python 3.11+, standard library. The stages are deterministic stand-ins; `real_vlm_hint()` sketches the swap to a real CLIP/SigLIP embedder + VLM reader/generator.

## 🛠 Module

| Component | Notes |
|---|---|
| `mm_eval.py` | `evaluate(embedder, noisy_ids, ungrounded_ids)` → recall, mean CER, grounding rate, e2e accuracy, attribution (`--self-test`) |

## What the numbers say

| Run | recall | mean CER | grounding | e2e acc | attribution |
|---|---|---|---|---|---|
| Shared-space | 0.00 | 1.00 | 0.00 | 0.00 | all retrieval |
| Caption (clean) | 1.00 | 0.00 | 1.00 | 1.00 | all correct |
| Caption + noisy OCR | 1.00 | >0 | 1.00 | 0.75 | **OCR** |
| Caption + ungrounded | 1.00 | 0.00 | 0.75 | 0.75 | **grounding** |

The last two score the same end-to-end; only the attribution shows they are different bugs.

## Design choices and tradeoffs

- **Three metrics, not one.** Retrieval recall, OCR CER, and grounding rate are independent; collapsing them to accuracy hides which stage to fix. The attribution is the actionable output.
- **Grounded ≠ correct.** A generator that faithfully repeats a misread number is perfectly grounded and wrong — so that failure is attributed to OCR, not grounding. A hallucination is the reverse.
- **First-failing-stage attribution.** Retrieval → OCR → grounding is a fixed precedence: you can't grade reading if nothing was retrieved, or grounding if the read text was already wrong.

## Common gotchas

- **Don't average the three into one score.** A weighted blend re-hides the very thing the breakdown exposes.
- **Build eval items whose answer is only in the image**, or you can't separate reading from parametric knowledge.
- **The stand-ins guarantee the failures; a real model grades them.** The 0.75s are engineered to make the point — measure your own stack.

## 🧮 Going deeper

- 📐 [math-foundations/17](../../math-foundations/17-multimodal-eval-metrics.md) — CER/WER, grounding as conditional accuracy, end-to-end decomposition.
- 🧪 [Lab 62](../62-ocr-reading-quality/) — the OCR metric itself, where CER misleads.
- 📖 [Grounding and OCR-reading](../../concepts/rag/grounding-and-ocr.md).

## What comes next

- 🧪 [Lab 62: OCR-reading quality](../62-ocr-reading-quality/) — why CER alone is the wrong score for numbers, and what to add.
