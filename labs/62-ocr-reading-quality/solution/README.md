# Lab 62 · Reference solution

Complete implementation of [Lab 62](../README.md).

## What this is

- **`cer` / `wer`** — character- and word-level edit-distance error rates.
- **`normalize`** — case + whitespace only (cosmetic, never content).
- **`extract_number` / `numeric_match`** — value-aware match with magnitude/percent parsing and relative tolerance.

## Expected results

- WER drops-one-of-three-words = 1/3; case+whitespace CER 0.18 → 0.00 normalized.
- Misread decimal: CER 0.09 but `numeric_match` False; format difference: CER ~0.7–0.8 but `numeric_match` True.

## Implementation choices

1. **Edit distance for legibility, numeric tolerance for correctness.**
2. **Normalization removes only formatting.**
3. **Relative tolerance** so format-equal numbers match and a misread magnitude does not.

## Running

```bash
cd labs/62-ocr-reading-quality
python ocr_eval.py --self-test
python ocr_eval.py            # the full table
```
