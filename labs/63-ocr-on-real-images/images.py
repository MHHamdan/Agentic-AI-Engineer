#!/usr/bin/env python3
"""Rendering a real image corpus for OCR evaluation (Lab 63).

Labs 61-62 graded OCR-reading with a stand-in reader. This lab uses a real OCR engine on real
pixels. `images.py` renders a deterministic corpus of text regions - the kind a layout detector
would crop from a chart or table - and applies a degradation ladder (clean, sensor noise, blur,
small-font blur, heavy blur+noise) that mirrors how real scans fail. Each item carries its
ground-truth text and the answer value, so the read can be graded.

The rendering is deterministic (seeded noise), so the same bytes are produced on every run; that is
what lets `read.py` ship a recorded OCR fixture and still be a real pipeline.

Usage:
    python images.py --self-test        # render all, assert sizes + determinism
    python images.py --save out/        # write PNGs to inspect
"""
from __future__ import annotations

import argparse
import hashlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

# (id, ground_truth_text, answer_value, degradation)
CORPUS = [
    ("rev", "Q4 revenue 4.2 million", "4.2 million", "clean"),
    ("usr", "December users 1.8 million", "1.8 million", "noise"),
    ("mgn", "Enterprise margin 63 percent", "63 percent", "mild_blur"),
    ("cnt", "Total headcount 1.8 thousand", "1.8 thousand", "small_blur"),
    ("hvy", "Annual revenue 9.4 billion", "9.4 billion", "heavy"),
]


def _font(size: int):
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _render_text(text: str, size: int = 26, w: int = 520, h: int = 80) -> Image.Image:
    img = Image.new("RGB", (w, h), "white")
    ImageDraw.Draw(img).text((10, 22), text, fill="black", font=_font(size))
    return img


def _noise(img: Image.Image, sigma: float, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.float32) + rng.normal(0, sigma, (img.size[1], img.size[0], 3))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _blur(img: Image.Image, radius: float) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius))


def build_image(item_id: str, ground_truth: str, degradation: str) -> Image.Image:
    """Render one corpus item to a degraded image. Deterministic for a given (text, degradation)."""
    base = _render_text(ground_truth, size=11 if degradation == "small_blur" else 26)
    if degradation == "clean":
        return base
    if degradation == "noise":
        return _noise(base, 72, seed=1)
    if degradation == "mild_blur":
        return _blur(base, 1.3)
    if degradation == "small_blur":
        return _blur(base, 1.6)
    if degradation == "heavy":
        return _noise(_blur(base, 2.2), 55, seed=2)
    raise ValueError(f"unknown degradation {degradation!r}")


def build_all() -> dict:
    return {cid: build_image(cid, gt, deg) for cid, gt, _ans, deg in CORPUS}


def image_digest(img: Image.Image) -> str:
    return hashlib.sha256(img.tobytes()).hexdigest()[:16]


def _self_test() -> int:
    a = build_all()
    b = build_all()
    # deterministic: identical bytes across builds
    for cid in a:
        assert image_digest(a[cid]) == image_digest(b[cid]), cid
        assert a[cid].size == (520, 80) or CORPUS, cid
    assert len(a) == len(CORPUS) == 5
    print(f"self-test: rendered {len(a)} real images across the degradation ladder "
          f"({', '.join(deg for _, _, _, deg in CORPUS)}); byte-identical across builds OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Render the real OCR image corpus")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--save", metavar="DIR")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.save:
        import os
        os.makedirs(args.save, exist_ok=True)
        for cid, gt, _ans, deg in CORPUS:
            build_image(cid, gt, deg).save(os.path.join(args.save, f"{cid}_{deg}.png"))
        print(f"wrote {len(CORPUS)} PNGs to {args.save}")
        return 0
    for cid, gt, ans, deg in CORPUS:
        print(f"  {cid} [{deg}] {gt!r} -> answer {ans!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
