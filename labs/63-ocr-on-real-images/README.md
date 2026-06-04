# Lab 63: OCR-reading on real rendered images

> 🔴 Advanced · ⏱ ~75–95 min · 📚 Builds on Lab 62 · Module 29

## 🎯 Goal

Labs 61–62 graded OCR-reading with a stand-in reader. This lab uses a **real** OCR engine (tesseract) on **real** pixels. A deterministic image corpus is rendered across a degradation ladder, read by tesseract, and graded by CER (legibility) and a value-aware answer check (correctness) — so the lesson from Lab 62 holds on real data: a misread digit is a small CER and a catastrophic answer.

By the end you should be able to:

- Render a reproducible image corpus and run a real OCR engine over it.
- Grade reads by CER and a value-aware numeric check, and attribute each failure to a stage.
- Recognize real OCR failure modes (blank reads, garble, digit misreads) and why value-awareness is non-negotiable for numbers.

## 📋 Prerequisites

- 🧪 [Lab 62](../62-ocr-reading-quality/) (CER/WER, normalization, numeric tolerance).
- 📐 [math-foundations/18](../../math-foundations/18-edit-distance-alignment.md) — alignment and the S/I/D error decomposition.
- 📖 [OCR on real images](../../concepts/rag/ocr-on-real-images.md) — the render/scan → preprocess → OCR → grade pipeline.

**Setup:** Python 3.11+, Pillow, numpy. The OCR step needs tesseract + `pytesseract`; without them the lab grades a recorded fixture deterministically, and `--live` runs the real engine when installed.

## 🛠 Modules

| Component | Notes |
|---|---|
| `images.py` | deterministic rendering + degradation ladder (`--self-test`, `--save DIR`) |
| `read.py` | real tesseract OCR + CER/value grading + attribution, with a recorded fixture (`--self-test`, `--live`) |
| `ocr_eval.py` | Lab 62's metrics (re-shipped): `cer`, `normalize`, `extract_number` |

## What the numbers say (tesseract 5.3.4)

| id | degradation | CER | answer read? | OCR output |
|---|---|---|---|---|
| rev | clean | 0.00 | ✓ | `Q4 revenue 4.2 million` |
| usr | sensor noise | 1.00 | ✗ | `` (blank → read failure) |
| mgn | mild blur | 0.00 | ✓ | `Enterprise margin 63 percent` |
| cnt | small + blur | 0.89 | ✗ | `hooey` (garble) |
| hvy | heavy | 0.27 | ✗ | `Arsual revenue 94 bien` (9.4b → 94) |

Answer accuracy 0.40, mean CER 0.43.

## Design choices and tradeoffs

- **Real pixels, real engine.** The failures are tesseract's actual behavior on degraded images, not engineered — which is the point: you cannot predict them, you measure them.
- **Recorded fixture + live mode.** OCR output varies by engine version, so the deterministic self-test grades a captured fixture; `--live` runs the real engine and checks version-stable properties (clean reads perfectly; degradation breaks reads).
- **Value-aware grading.** `read.py` parses standalone numbers (guarding against `Q4` → `4`) and matches the answer value within tolerance — the heavy image's `94` vs `9.4 billion` is caught here, where CER (0.27) would not.

## Common gotchas

- **CER alone passes the worst error.** The 9.4-billion → 94 misread is moderate CER but a ~10⁸ value error; only the numeric check catches it.
- **OCR is layout-dependent.** Real systems crop a region first; feeding a whole chart to `--psm 7` (single line) misreads. Detect/crop, then read.
- **Preprocessing changes everything.** Binarization, deskew, and upscaling can flip a blank read into a correct one — version and preprocess your pipeline as carefully as the model.

## 🧮 Going deeper

- 📐 [math-foundations/18](../../math-foundations/18-edit-distance-alignment.md) — backtrace the alignment to see which characters the engine confuses.
- 🧪 [Lab 61](../61-grading-multimodal-rag/) — where OCR-reading sits among retrieval and grounding.
- 📖 [OCR on real images](../../concepts/rag/ocr-on-real-images.md).

## What comes next

Wire these real reads into the [Lab 61](../61-grading-multimodal-rag/) three-axis grader as the reading stage, so retrieval, OCR-reading, and grounding are all graded on real images.
