#!/usr/bin/env python3
"""Nugget-based evaluation: coverage and citation for long-form RAG (Lab 64).

By 2026 the standard way to evaluate long-form and report-generation RAG is nugget-based, as in the
TREC RAG track's AutoNuggetizer (Pradeep et al., 2024, arXiv:2411.09607) and Auto-ARGUE (arXiv:
2509.26184): decompose an information need into atomic "nuggets" a good answer should cover, label
how well the answer supports each nugget, and score two orthogonal things -

  - Coverage: of the nuggets that should appear, how many does the answer support? (recall-like)
  - Citation (Sentence-Support Rate): of the answer's sentences, how many are actually supported by
    the evidence they cite? (precision-like)

The TREC 2025 finding that motivates this lab: citation accuracy is becoming a solved problem when
systems add reasonable checks, but nugget coverage is still a work in progress, and the
two are different axes with different fixes. Coverage is mostly a retrieval problem (you did not
retrieve the diverse evidence the nuggets need); citation is mostly a generation problem (you cited
the wrong thing). A single quality score hides which one you have.

Nuggets carry a vital/okay weight (the TREC nugget tradition), and support is labeled Full/Partial/
No for partial credit. The labeler here is a deterministic stand-in; `assign_with_judge` is the
guarded seam for an AutoNuggetizer-style LLM assignment.

Usage:
    python nugget_eval.py --self-test
"""
from __future__ import annotations

import argparse
import sys

# An information need decomposed into nuggets (vital nuggets must be covered; okay nuggets are
# bonus). Entities are from the repo's running corpus.
NUGGETS = [
    {"id": "n1", "text": "Helix Lab leads the Prism Project", "weight": "vital", "terms": ["helix", "prism"]},
    {"id": "n2", "text": "The Prism Project targets retrieval latency", "weight": "vital", "terms": ["prism", "latency"]},
    {"id": "n3", "text": "Dr. Aanya Rao is the principal engineer", "weight": "vital", "terms": ["aanya", "rao", "principal"]},
    {"id": "n4", "text": "Funding comes from the Cascade Consortium", "weight": "okay", "terms": ["cascade", "consortium", "funding"]},
    {"id": "n5", "text": "The project began in 2024", "weight": "okay", "terms": ["2024", "began"]},
]

# Evidence the answer may cite.
DOCS = {
    "d1": "helix lab leads the prism project on retrieval latency",
    "d2": "dr aanya rao is the principal engineer of prism",
    "d3": "the cascade consortium funds the work",
    "d4": "unrelated note about quarterly logistics",
}

_SUPPORT_SCORE = {"full": 1.0, "partial": 0.5, "no": 0.0}
_WEIGHT = {"vital": 1.0, "okay": 0.5}


def support_label(nugget: dict, answer_text: str) -> str:
    """Full / Partial / No support (a deterministic stand-in for AutoNuggetizer's listwise LLM
    assignment): all key terms present -> full, some -> partial, none -> no."""
    present = sum(t in answer_text.lower() for t in nugget["terms"])
    if present == len(nugget["terms"]):
        return "full"
    return "partial" if present else "no"


def assign_with_judge(nugget: dict, answer_text: str, judge=None) -> str:  # pragma: no cover
    """Guarded seam for an LLM judge (AutoNuggetizer-style). `judge(nugget, answer)` should return
    one of full/partial/no. Falls back to the deterministic labeler when no judge is supplied."""
    if judge is None:
        return support_label(nugget, answer_text)
    return judge(nugget, answer_text)


def coverage(answer_text: str, vital_only: bool = False) -> float:
    """Weighted nugget coverage (recall-like). vital_only restricts to the must-have nuggets."""
    items = [n for n in NUGGETS if n["weight"] == "vital" or not vital_only]
    den = sum(_WEIGHT[n["weight"]] for n in items)
    num = sum(_SUPPORT_SCORE[support_label(n, answer_text)] * _WEIGHT[n["weight"]] for n in items)
    return num / den if den else 0.0


def sentence_support_rate(answer: list) -> float:
    """Citation precision: fraction of answer sentences whose cited evidence supports them. `answer`
    is a list of (sentence, [cited_doc_ids]). A sentence is supported if a cited doc contains at
    least half of its content words (a stand-in for an entailment / LLM citation judge)."""
    if not answer:
        return 0.0
    ok = 0
    for sentence, cites in answer:
        words = [w for w in sentence.lower().split() if len(w) > 3]
        need = max(1, len(words) // 2)
        ok += any(sum(w in DOCS.get(c, "") for w in words) >= need for c in cites)
    return ok / len(answer)


def evaluate(answer_text: str, cited_answer: list) -> dict:
    """Both axes plus an attribution: which vital nuggets are missing, which sentences are uncited
    or unsupported."""
    missing = [n["id"] for n in NUGGETS if n["weight"] == "vital" and support_label(n, answer_text) == "no"]
    unsupported = []
    for sentence, cites in cited_answer:
        words = [w for w in sentence.lower().split() if len(w) > 3]
        need = max(1, len(words) // 2)
        if not any(sum(w in DOCS.get(c, "") for w in words) >= need for c in cites):
            unsupported.append(sentence)
    return {"coverage": coverage(answer_text), "vital_coverage": coverage(answer_text, vital_only=True),
            "sentence_support_rate": sentence_support_rate(cited_answer),
            "missing_vital": missing, "unsupported_sentences": unsupported}


# Three answers that separate the two axes (the TREC 2025 lesson made concrete).
ANSWER_CITE_GOOD_MISS = ("helix lab leads the prism project.",
                         [("Helix Lab leads the Prism project.", ["d1"])])
ANSWER_COVER_CITE_BAD = ("helix prism latency. aanya rao principal. cascade consortium funding. began 2024.",
                         [("Helix Lab leads the Prism project on latency.", ["d4"]),
                          ("Aanya Rao is principal engineer.", ["d4"]),
                          ("Cascade Consortium funding began 2024.", ["d4"])])
ANSWER_BALANCED = ("helix prism latency. aanya rao principal. cascade consortium funding. began 2024.",
                   [("Helix Lab leads the Prism project on latency.", ["d1"]),
                    ("Aanya Rao is the principal engineer.", ["d2"]),
                    ("The Cascade Consortium funds it.", ["d3"])])


def _self_test() -> int:
    a = evaluate(*ANSWER_CITE_GOOD_MISS)
    b = evaluate(*ANSWER_COVER_CITE_BAD)
    c = evaluate(*ANSWER_BALANCED)

    # A: cites perfectly but misses vital nuggets - high citation, low coverage
    assert a["sentence_support_rate"] == 1.0 and a["vital_coverage"] < 0.6 and a["missing_vital"]
    # B: covers everything but cites unsupported evidence - high coverage, zero citation
    assert b["vital_coverage"] == 1.0 and b["sentence_support_rate"] == 0.0 and b["unsupported_sentences"]
    # C: both high, nothing missing or unsupported
    assert c["vital_coverage"] == 1.0 and c["sentence_support_rate"] == 1.0
    assert not c["missing_vital"] and not c["unsupported_sentences"]
    # the axes are orthogonal: A and B sit at opposite corners
    assert a["sentence_support_rate"] > b["sentence_support_rate"]
    assert b["vital_coverage"] > a["vital_coverage"]
    # partial credit works: support labels span full/partial/no
    labels = {support_label(n, ANSWER_CITE_GOOD_MISS[0]) for n in NUGGETS}
    assert {"full", "no"} <= labels

    print(f"self-test: cite-good/miss -> coverage {a['vital_coverage']:.2f} SSR {a['sentence_support_rate']:.2f} "
          f"(missing {a['missing_vital']}); cover/cite-bad -> coverage {b['vital_coverage']:.2f} "
          f"SSR {b['sentence_support_rate']:.2f}; balanced -> coverage {c['vital_coverage']:.2f} "
          f"SSR {c['sentence_support_rate']:.2f}. Coverage and citation are orthogonal OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Nugget-based coverage + citation evaluation")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    for name, ans in {"cite-good/miss": ANSWER_CITE_GOOD_MISS, "cover/cite-bad": ANSWER_COVER_CITE_BAD,
                      "balanced": ANSWER_BALANCED}.items():
        r = evaluate(*ans)
        print(f"  {name:16} coverage {r['coverage']:.2f}  vital {r['vital_coverage']:.2f}  "
              f"SSR {r['sentence_support_rate']:.2f}  missing {r['missing_vital']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
