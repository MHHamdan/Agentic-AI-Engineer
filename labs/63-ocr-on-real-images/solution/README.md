# Lab 63 · Reference solution

Complete implementation of [Lab 63](../README.md).

## What this is

- **`images.py`** — deterministic rendering of a text-region corpus + a degradation ladder (clean, noise, blur, small+blur, heavy).
- **`read.py`** — real tesseract OCR (guarded) + CER and value-aware grading + per-stage attribution, with a recorded fixture for determinism.

## Expected results (tesseract 5.3.4)

- Answer accuracy 0.40, mean CER 0.43.
- rev/mgn correct; usr blank (read failure); cnt garble and hvy `94` (numeric misreads).

## Implementation choices

1. **Recorded fixture + `--live`** so grading is deterministic without tesseract and real with it.
2. **Standalone-number parsing** so `Q4` is not read as the value 4.
3. **Two-axis grading** — CER for legibility, numeric match for correctness.

## Running

```bash
cd labs/63-ocr-on-real-images
python images.py --self-test
python read.py --self-test      # deterministic (fixture)
python read.py --live           # real tesseract, if installed
```
