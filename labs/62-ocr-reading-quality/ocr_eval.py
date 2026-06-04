#!/usr/bin/env python3
"""OCR-reading quality: CER, WER, normalization, and why numbers need more (Lab 62).

Lab 61 graded OCR-reading as one axis of multimodal RAG. This lab is about the metric itself,
because scoring read text is subtler than it looks. Character Error Rate (CER) and Word Error Rate
(WER) are edit distances - the standard OCR/ASR metrics - but on the numeric and structured answers
that fill charts and tables they are simultaneously too harsh and too lenient:

  - Too harsh: "$4.2M" vs "4.2 million" is a large CER (different characters) but the same value.
  - Too lenient: "4.2 million" misread as "42 million" is a tiny CER (one deleted '.') but a 10x
    error - exactly the kind of mistake that ruins a financial answer.

So OCR-reading needs two layers: a surface metric (CER/WER, after normalization that removes
cosmetic differences) and a value-aware metric (numeric tolerance) for the answer span. This lab
builds both and shows where each is the right tool.

Everything here is deterministic edit distance and number parsing - exact and offline.

Usage:
    python ocr_eval.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys


def _edit_distance(a: list | str, b: list | str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def cer(reference: str, hypothesis: str) -> float:
    """Character Error Rate: character edit distance / reference length."""
    return _edit_distance(reference, hypothesis) / max(len(reference), 1)


def wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate: word-level edit distance / reference word count."""
    return _edit_distance(reference.split(), hypothesis.split()) / max(len(reference.split()), 1)


def normalize(s: str, *, lower: bool = True, collapse_ws: bool = True) -> str:
    """Remove cosmetic differences before scoring: case and whitespace. Normalization should never
    change content - only formatting - so it lowers CER for typography but not for misreads."""
    if lower:
        s = s.lower()
    if collapse_ws:
        s = re.sub(r"\s+", " ", s.strip())
    return s


_SCALE = {"million": 1e6, "m": 1e6, "billion": 1e9, "b": 1e9, "thousand": 1e3, "k": 1e3}


def extract_number(s: str):
    """Parse the first numeric value in a string, applying magnitude words/suffixes and percent.
    '$4.2M' and '4.2 million' both parse to 4_200_000; '63%' and '63 percent' to 0.63."""
    s = s.lower().replace("$", "").replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    val = float(m.group())
    for unit, mult in _SCALE.items():
        if re.search(rf"\d\s*{unit}\b", s) or re.search(rf"\b{unit}\b", s):
            val *= mult
            break
    if "percent" in s or "%" in s:
        val /= 100
    return val


def numeric_match(reference: str, hypothesis: str, rel_tol: float = 0.01) -> bool:
    """Value-aware match: equal within a relative tolerance, regardless of format."""
    a, b = extract_number(reference), extract_number(hypothesis)
    if a is None or b is None:
        return False
    return abs(a - b) <= rel_tol * max(abs(a), 1e-9)


# (reference, ocr_output, note)
CASES = [
    ("4.2 million", "4.2 million", "clean"),
    ("4.2 million", "4.2  Million", "case + whitespace only"),
    ("4.2 million", "42 million", "misread decimal -> 10x value"),
    ("4.2 million", "$4.2M", "different format, same value"),
    ("63 percent", "63%", "different format, same value"),
    ("retriever reranker generator", "retriever generator", "dropped a word"),
]


def report() -> list[dict]:
    out = []
    for ref, hyp, note in CASES:
        out.append({"ref": ref, "hyp": hyp, "note": note,
                    "cer": cer(ref, hyp), "cer_norm": cer(normalize(ref), normalize(hyp)),
                    "wer": wer(ref, hyp), "exact_norm": normalize(ref) == normalize(hyp),
                    "numeric": numeric_match(ref, hyp)})
    return out


def _self_test() -> int:
    # CER / WER exact on a known dropped-word case: one of three words missing
    assert wer("retriever reranker generator", "retriever generator") == 1 / 3
    assert cer("abc", "abd") == 1 / 3

    rows = {r["note"]: r for r in report()}

    # normalization removes cosmetic differences but not content errors
    ws = rows["case + whitespace only"]
    assert ws["cer"] > 0 and ws["cer_norm"] == 0.0 and ws["exact_norm"]

    # the dangerous case: a misread decimal is a TINY CER but a value error numeric catches
    mis = rows["misread decimal -> 10x value"]
    assert mis["cer_norm"] < 0.15 and mis["numeric"] is False

    # the harsh case: a format difference is a LARGE CER but numerically correct
    fmt = rows["different format, same value"]
    assert fmt["cer_norm"] > 0.5 and fmt["numeric"] is True
    # percent format likewise: large CER, correct value
    assert rows["different format, same value"]["numeric"] is True

    print(f"self-test: WER drops-a-word 1/3; normalization {ws['cer']:.2f}->0.00 for cosmetics; "
          f"misread decimal CER {mis['cer_norm']:.2f} but numeric_match False (10x error hidden by CER); "
          f"format diff CER {fmt['cer_norm']:.2f} but numeric_match True (CER too harsh) OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="OCR-reading quality metrics")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    for r in report():
        print(f"  {r['note']:28} CER {r['cer']:.2f}  CER(norm) {r['cer_norm']:.2f}  "
              f"WER {r['wer']:.2f}  numeric {r['numeric']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
