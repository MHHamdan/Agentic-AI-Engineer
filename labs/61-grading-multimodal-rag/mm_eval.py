#!/usr/bin/env python3
"""Grading multimodal RAG: retrieval, grounding, and OCR-reading separately (Lab 61).

Lab 60 showed that a shared-space embedder can't retrieve text-in-image queries. This lab is about
what you measure once retrieval works: a multimodal answer can be wrong for three independent
reasons, and a single end-to-end accuracy number cannot tell them apart.

  - Retrieval: did the element that contains the answer come back in the top-k?
  - OCR-reading: was the text inside that element read correctly (the number in the chart)?
  - Grounding: did the generator use the read evidence, or answer from parametric memory?

The decisive case is "grounded but wrong": the OCR misreads 1.8 as 18, the generator faithfully
reports 18, so grounding is perfect and the answer is wrong - the failure is OCR, not grounding.
Conversely a hallucination is grounding, not OCR. This lab computes the three metrics, then
attributes every wrong answer to its FIRST failing stage (retrieval -> OCR -> grounding), so two
runs that both score 0.75 end-to-end are revealed to have different causes.

The embedder/reader/generator are deterministic stand-ins so the lab runs offline; the real
vision-language wiring is sketched in `real_vlm_hint()` and guarded. The metrics and the
attribution are the deliverable and are unchanged for a real model.

Usage:
    python mm_eval.py --self-test
"""
from __future__ import annotations

import argparse
import math
import sys
from collections import Counter


# ---------- string distance + OCR metric ----------
def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(reference: str, hypothesis: str) -> float:
    """Character Error Rate: edit distance normalized by reference length."""
    return levenshtein(reference, hypothesis) / max(len(reference), 1)


def _bag(text: str) -> dict:
    v: dict[str, int] = {}
    for w in text.split():
        v[w] = v.get(w, 0) + 1
    return v


def _cosine(u: dict, v: dict) -> float:
    if not u or not v:
        return 0.0
    dot = sum(u[k] * v.get(k, 0) for k in u)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0


# ---------- corpus: the answer lives in the image's text; visual vocab is disjoint from it ----------
CORPUS = [
    {"id": "rev", "visual": "blue bar chart", "in_image_text": "q4 revenue 4.2 million", "answer": "4.2 million"},
    {"id": "usr", "visual": "green line chart", "in_image_text": "december users 1.8 million", "answer": "1.8 million"},
    {"id": "mgn", "visual": "grid table rows columns", "in_image_text": "enterprise margin 63 percent", "answer": "63 percent"},
    {"id": "map", "visual": "world map with markers", "in_image_text": "offices montreal berlin singapore", "answer": "montreal berlin singapore"},
]
QUERIES = [("q4 revenue", "rev"), ("december users", "usr"),
           ("enterprise margin", "mgn"), ("which offices", "map")]


# ---------- pluggable stand-in stages (swap for a real VLM; see real_vlm_hint) ----------
class SharedSpaceEmbedder:
    def encode_doc(self, d): return _bag(d["visual"])                       # CLIP: visual only
    def encode_query(self, q): return _bag(q)

class CaptionThenEmbedder:
    def encode_doc(self, d): return _bag(d["visual"] + " " + d["in_image_text"])
    def encode_query(self, q): return _bag(q)


def retrieve(embedder, query: str):
    scored = [(_cosine(embedder.encode_query(query), embedder.encode_doc(d)), d) for d in CORPUS]
    sim, best = max(scored, key=lambda x: x[0])
    return best if sim > 0 else None


def read_text(doc, noisy_ids=()) -> str:
    """OCR stand-in. Reads the in-image text; for noisy ids it corrupts the number (a real OCR
    failure: a misread decimal point)."""
    if doc is None:
        return ""
    t = doc["in_image_text"]
    if doc["id"] in noisy_ids:
        t = t.replace("1.8", "18")            # 1.8 million -> 18 million
    return t


def generate(doc, evidence: str, ungrounded_ids=()):
    """Generator stand-in. Returns (answer, grounded). For ungrounded ids it ignores the evidence
    and emits a parametric guess (a hallucination); otherwise it grounds the answer in the evidence
    it was given - which means it faithfully repeats a misread number."""
    if doc is None:
        return "", False
    if doc["id"] in ungrounded_ids:
        return "about half", False
    answer = doc["answer"] if all(tok in evidence for tok in doc["answer"].split()) else evidence
    return answer, True


# ---------- the graded pipeline ----------
def evaluate(embedder, noisy_ids=(), ungrounded_ids=()) -> dict:
    rows = []
    for query, gold_id in QUERIES:
        doc = retrieve(embedder, query)
        retrieval_ok = doc is not None and doc["id"] == gold_id
        gold = next(d for d in CORPUS if d["id"] == gold_id)
        evidence = read_text(doc, noisy_ids)
        ocr = cer(gold["in_image_text"], evidence) if retrieval_ok else 1.0
        answer, grounded = generate(doc, evidence, ungrounded_ids)
        correct = retrieval_ok and answer == gold["answer"]
        # attribute a wrong answer to its first failing stage
        if not retrieval_ok:
            stage = "retrieval"
        elif ocr > 0:
            stage = "ocr"
        elif not grounded:
            stage = "grounding"
        elif not correct:
            stage = "other"
        else:
            stage = "correct"
        rows.append({"query": query, "retrieval_ok": retrieval_ok, "cer": ocr,
                     "grounded": grounded, "answer": answer, "correct": correct, "stage": stage})
    n = len(rows)
    return {"rows": rows, "n": n,
            "recall": sum(r["retrieval_ok"] for r in rows) / n,
            "mean_cer": sum(r["cer"] for r in rows) / n,
            "grounding_rate": sum(r["grounded"] for r in rows) / n,
            "e2e_accuracy": sum(r["correct"] for r in rows) / n,
            "attribution": dict(Counter(r["stage"] for r in rows))}


def real_vlm_hint() -> str:
    return ("Swap the stand-ins for a real vision-language stack and the metrics are unchanged:\n"
            "  embedder  -> a CLIP/SigLIP image-text model (encode_doc on the rendered element)\n"
            "  reader    -> a VLM or OCR engine returning the in-image text\n"
            "  generator -> a VLM answering from the retrieved image + read text\n"
            "Grade recall@k, CER on the read text, grounding (answer entailed by evidence), and "
            "attribute end-to-end errors to the first failing stage exactly as below.")


def _self_test() -> int:
    shared = evaluate(SharedSpaceEmbedder())
    clean = evaluate(CaptionThenEmbedder())
    noisy = evaluate(CaptionThenEmbedder(), noisy_ids=("usr",))
    ungrounded = evaluate(CaptionThenEmbedder(), ungrounded_ids=("mgn",))

    # the attribution partitions every query (correct + failures == n) in all runs
    for r in (shared, clean, noisy, ungrounded):
        assert sum(r["attribution"].values()) == r["n"], r["attribution"]

    # 1) shared space: all failures are retrieval (CLIP can't read the text-in-image queries)
    assert shared["attribution"].get("retrieval") == shared["n"] and shared["e2e_accuracy"] == 0.0
    # 2) caption + clean: everything correct
    assert clean["e2e_accuracy"] == 1.0 and clean["attribution"].get("correct") == clean["n"]
    # 3) grounded-but-wrong: noisy OCR drops accuracy while grounding stays perfect; failure -> ocr
    assert noisy["grounding_rate"] == 1.0 and noisy["e2e_accuracy"] < 1.0
    assert noisy["attribution"].get("ocr") == 1 and noisy["mean_cer"] > 0
    # 4) hallucination: same accuracy as (3) but a DIFFERENT cause -> grounding, with CER clean
    assert ungrounded["e2e_accuracy"] == noisy["e2e_accuracy"]
    assert ungrounded["attribution"].get("grounding") == 1 and ungrounded["mean_cer"] == 0.0

    print(f"self-test: shared-space all-retrieval-failures (acc {shared['e2e_accuracy']:.2f}); caption "
          f"clean acc {clean['e2e_accuracy']:.2f}; noisy-OCR acc {noisy['e2e_accuracy']:.2f} grounding "
          f"{noisy['grounding_rate']:.2f} -> attributed OCR; ungrounded acc {ungrounded['e2e_accuracy']:.2f} "
          f"CER {ungrounded['mean_cer']:.2f} -> attributed GROUNDING. Same accuracy, different cause OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Grade multimodal RAG by stage")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print(real_vlm_hint())
    return 0


if __name__ == "__main__":
    sys.exit(main())
