# Lab 62: OCR-reading quality

> 🟡 Intermediate · ⏱ ~55–70 min · 📚 Builds on Lab 61 · Module 28

## 🎯 Goal

Lab 61 graded OCR-reading as one axis. This lab is about the metric itself, because scoring read text is subtler than it looks: Character/Word Error Rate are the standard OCR metrics, but on the numbers that fill charts and tables they are simultaneously too harsh on formatting and too lenient on the digits that carry the meaning.

By the end you should be able to:

- Compute CER and WER and explain when each is the right granularity.
- Normalize away cosmetic differences without masking content errors.
- Add a value-aware numeric match for answer spans, and say why CER alone is insufficient.

## 📋 Prerequisites

- 🧪 [Lab 61](../61-grading-multimodal-rag/) (OCR-reading as an eval axis).
- **Assumed background:** edit distance, and the idea of normalization in text metrics.

**Setup:** Python 3.11+, standard library. Everything is exact edit distance and number parsing.

## 🛠 Module

| Component | Notes |
|---|---|
| `ocr_eval.py` | `cer`, `wer`, `normalize`, `extract_number`, `numeric_match`, `report` (`--self-test`) |

## What the numbers say

| Case | CER (norm) | numeric match |
|---|---|---|
| `4.2 million` vs `4.2  Million` | 0.00 | ✓ |
| `4.2 million` vs `42 million` (misread) | **0.09** | ✗ (10× error) |
| `4.2 million` vs `$4.2M` (format) | **0.73** | ✓ |
| `63 percent` vs `63%` | 0.80 | ✓ |

## Design choices and tradeoffs

- **Two layers.** CER/WER on the read text for legibility; a value-aware match on the answer span for correctness. Neither alone is right for numeric answers.
- **Normalize before scoring, but only formatting.** Case and whitespace are noise; a normalizer that "fixes" content would mask real errors.
- **CER is the wrong score for a single digit.** A misread decimal is one character of CER and a 10× value error — the metric underweights exactly the characters that matter.

## Common gotchas

- **Reporting CER only.** It will pass a 10× misread and fail a correct reformat. Add numeric/structured matching for answer spans.
- **Over-normalizing.** Stripping units or rounding inside the normalizer hides errors you need to see.
- **WER on short answers.** A two-word answer has coarse WER (0, 0.5, 1.0); CER or value match is finer where it counts.

## 🧮 Going deeper

- 📐 [math-foundations/17](../../math-foundations/17-multimodal-eval-metrics.md) — edit distance, CER/WER, and value-aware matching formally.
- 🧪 [Lab 61](../61-grading-multimodal-rag/) — where OCR-reading sits among the three axes.

## What comes next

Extend `extract_number` to currencies, ranges, dates, and units, and add a structured-match metric for table cells, so the answer-span check covers the structured outputs a real corpus contains.
