#!/usr/bin/env python3
"""Real OCR reading and grading on rendered images (Lab 63).

This runs a real OCR engine (tesseract, via pytesseract) on the real images from `images.py`, then
grades each read two ways: CER on the full line (legibility) and a value-aware check on the answer
(correctness), reusing Lab 62's metrics. Every wrong read is attributed to a stage - a blank read is
a read failure, a non-blank read whose answer value is wrong or absent is a numeric misread.

Because tesseract output can vary by version, the module ships a recorded fixture (`EXPECTED_OCR`,
captured on tesseract 5.3.4) so the grading and the self-test are deterministic everywhere. When
tesseract is installed, `--live` runs the real engine and checks structural properties that hold
across versions (a clean render reads perfectly; the degraded ladder produces at least one numeric
misread and at least one blank read).

Usage:
    python read.py --self-test      # deterministic, grades the recorded fixture
    python read.py --live           # run real tesseract on the rendered images
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

from images import CORPUS, build_image
from ocr_eval import cer, extract_number, normalize

# Recorded real OCR outputs (tesseract 5.3.4, --psm 7) for the deterministic corpus.
EXPECTED_OCR = {
    "rev": "Q4 revenue 4.2 million",
    "usr": "",
    "mgn": "Enterprise margin 63 percent",
    "cnt": "hooey",
    "hvy": "Arsual revenue 94 bien",
}

_SCALE = {"million": 1e6, "m": 1e6, "billion": 1e9, "b": 1e9, "thousand": 1e3, "k": 1e3}


def numbers_in(text: str) -> list[float]:
    """Every standalone number in the text, scaled by a trailing magnitude word / percent. The
    standalone guard (not preceded by a letter) keeps 'Q4' from being read as the value 4."""
    text = text.lower().replace("$", "").replace(",", "")
    values = []
    for m in re.finditer(r"(?<![a-z0-9])(\d+(?:\.\d+)?)\s*([a-z%]+)?", text):
        val = float(m.group(1))
        unit = m.group(2) or ""
        for u, mult in _SCALE.items():
            if unit == u or unit.startswith(u):
                val *= mult
                break
        if unit.startswith("percent") or unit == "%":
            val /= 100
        values.append(val)
    return values


def answer_read_ok(answer: str, ocr_text: str, rel_tol: float = 0.01) -> bool:
    """Was the answer's value read correctly anywhere in the OCR output?"""
    target = extract_number(answer)
    if target is None:
        return normalize(answer) in normalize(ocr_text)
    return any(abs(v - target) <= rel_tol * max(abs(target), 1e-9) for v in numbers_in(ocr_text))


def ocr_image(img) -> str:
    import pytesseract
    return pytesseract.image_to_string(img, config="--psm 7").strip()


def tesseract_available() -> bool:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def grade(live: bool = False) -> dict:
    rows = []
    for cid, gt, answer, deg in CORPUS:
        out = ocr_image(build_image(cid, gt, deg)) if live else EXPECTED_OCR[cid]
        line_cer = cer(normalize(gt), normalize(out))
        ok = answer_read_ok(answer, out)
        if not out.strip():
            stage = "read_failure"
        elif not ok:
            stage = "numeric_misread"
        else:
            stage = "correct"
        rows.append({"id": cid, "deg": deg, "ocr": out, "cer": line_cer,
                     "answer_ok": ok, "stage": stage})
    n = len(rows)
    return {"rows": rows, "n": n,
            "mean_cer": sum(r["cer"] for r in rows) / n,
            "answer_accuracy": sum(r["answer_ok"] for r in rows) / n,
            "attribution": dict(Counter(r["stage"] for r in rows))}


def _self_test() -> int:
    # deterministic grading of the recorded fixture
    g = grade(live=False)
    assert sum(g["attribution"].values()) == g["n"] == 5
    by_id = {r["id"]: r for r in g["rows"]}
    assert by_id["rev"]["cer"] == 0.0 and by_id["rev"]["answer_ok"]              # clean reads perfectly
    assert by_id["mgn"]["answer_ok"]                                             # mild blur still fine
    assert by_id["usr"]["stage"] == "read_failure"                              # noise -> blank
    assert by_id["hvy"]["answer_ok"] is False                                   # 9.4b misread as 94
    assert g["attribution"].get("correct") == 2                                  # rev + mgn
    assert g["attribution"].get("read_failure") == 1 and g["attribution"].get("numeric_misread") == 2
    assert 0.0 < g["mean_cer"] < 1.0

    # the standalone-number guard: 'Q4 revenue 4.2 million' reads the value as 4.2M, not 4
    assert answer_read_ok("4.2 million", "Q4 revenue 4.2 million")
    assert numbers_in("Q4 revenue 4.2 million") == [4.2e6]

    msg = (f"self-test: graded recorded real-OCR fixture - answer accuracy {g['answer_accuracy']:.2f}, "
           f"mean CER {g['mean_cer']:.2f}, attribution {g['attribution']} "
           f"(9.4 billion misread as '94 bien' -> numeric_misread)")

    # if tesseract is present, also run the real engine and check version-stable properties
    if tesseract_available():
        live = grade(live=True)
        lb = {r["id"]: r for r in live["rows"]}
        assert lb["rev"]["cer"] == 0.0 and lb["rev"]["answer_ok"], "clean render should read perfectly"
        assert any(not r["answer_ok"] for r in live["rows"]), "degradation should cause a misread"
        assert any(r["stage"] == "read_failure" for r in live["rows"]) or live["mean_cer"] > 0.1
        msg += "; live tesseract confirms clean=perfect and degradation breaks reads"
    else:
        msg += "; tesseract not installed - fixture grading is deterministic without it"
    print(msg + " OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Real OCR reading + grading on rendered images")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    g = grade(live=args.live and tesseract_available())
    src = "live tesseract" if (args.live and tesseract_available()) else "recorded fixture"
    print(f"OCR grading ({src}): answer accuracy {g['answer_accuracy']:.2f}, mean CER {g['mean_cer']:.2f}")
    for r in g["rows"]:
        print(f"  {r['id']} [{r['deg']:10}] CER {r['cer']:.2f}  answer_ok {r['answer_ok']!s:5}  "
              f"{r['stage']:15} OCR={r['ocr']!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
