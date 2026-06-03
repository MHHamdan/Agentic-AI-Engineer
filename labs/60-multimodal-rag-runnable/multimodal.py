#!/usr/bin/env python3
"""Multimodal RAG, runnable (Lab 60).

The Batch 82 concept page (concepts/rag/multimodal-rag.md) argued two architectures and one famous
failure; this lab makes them runnable. A small corpus of "documents" each carry visual content
(what the image looks like) and dense in-image text (a number in a chart, a cell in a table). Two
embedders index them:

  - SharedSpace (CLIP/SigLIP-style): embeds the visual content only. Great for "find the bar
    chart"; blind to the numbers printed inside it - the "CLIP can't read" failure.
  - CaptionThenEmbed: runs a captioner that extracts the visual description AND the in-image text,
    then embeds that. Handles both query kinds, at the cost of an offline captioning pass.

The embedders are deterministic token-overlap stand-ins so the lab runs offline; swap in a real
vision-language embedder and the retrieval/eval code is unchanged. The lab also separates the two
metrics that multimodal eval must not conflate: retrieval (did the right element come back?) and
grounding/reading (did the answer use the number in the image, correctly?).

Usage:
    python multimodal.py --self-test
"""
from __future__ import annotations

import argparse
import math
import re
import sys


def _bag(text: str) -> dict:
    toks = re.findall(r"[a-z0-9]+", text.lower())
    v: dict[str, int] = {}
    for t in toks:
        v[t] = v.get(t, 0) + 1
    return v


def _cosine(u: dict, v: dict) -> float:
    if not u or not v:
        return 0.0
    dot = sum(u[k] * v.get(k, 0) for k in u)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0


# A document carries what it looks like (visual) and the dense text printed inside it (in_image_text).
# NOTE: the visual description and the in-image text use DISJOINT vocabulary on the query-relevant
# terms - the topic words ("revenue", "users", "margin", "offices") appear ONLY in the in-image
# text, so a visual-only embedder genuinely cannot retrieve them. That is the point.
CORPUS = [
    {"id": "fig-rev", "visual": "blue vertical bar chart", "in_image_text": "quarterly revenue Q4 4.2 million dollars", "answer": "4.2 million"},
    {"id": "fig-users", "visual": "green line chart trending upward", "in_image_text": "monthly active users December 1.8 million", "answer": "1.8 million"},
    {"id": "tbl-margin", "visual": "grid table with rows and columns", "in_image_text": "enterprise gross margin 63 percent by segment", "answer": "63 percent"},
    {"id": "diagram-arch", "visual": "boxes connected by arrows", "in_image_text": "retriever reranker generator pipeline", "answer": "retriever, reranker, generator"},
    {"id": "photo-team", "visual": "photograph of people at a whiteboard", "in_image_text": "", "answer": "a team photo"},
    {"id": "map-sites", "visual": "world map with location markers", "in_image_text": "offices Montreal Berlin Singapore cities", "answer": "Montreal, Berlin, Singapore"},
]


class SharedSpaceEmbedder:
    """CLIP/SigLIP-style: embeds the visual content only - cannot read dense in-image text."""
    def encode_doc(self, doc): return _bag(doc["visual"])
    def encode_query(self, q): return _bag(q)
    def similarity(self, a, b): return _cosine(a, b)


class CaptionThenEmbedder:
    """Captions each element (visual description + OCR of in-image text), then embeds that."""
    def encode_doc(self, doc): return _bag(doc["visual"] + " " + doc["in_image_text"])
    def encode_query(self, q): return _bag(q)
    def similarity(self, a, b): return _cosine(a, b)


def retrieve(embedder, query: str):
    qv = embedder.encode_query(query)
    scored = [(embedder.similarity(qv, embedder.encode_doc(d)), d["id"]) for d in CORPUS]
    top_sim, top_id = max(scored)
    return top_id if top_sim > 0 else None      # no signal is a miss, not a lucky tie


# queries split by what they need: visual appearance vs reading the text inside the image
VISUAL_QUERIES = [("blue vertical bar chart", "fig-rev"), ("green line chart upward", "fig-users"),
                  ("boxes connected by arrows", "diagram-arch"), ("photograph of people whiteboard", "photo-team")]
TEXT_IN_IMAGE_QUERIES = [("quarterly revenue", "fig-rev"), ("monthly active users", "fig-users"),
                         ("enterprise gross margin segment", "tbl-margin"), ("offices cities", "map-sites")]


def recall_at_1(embedder, queries) -> float:
    return sum(retrieve(embedder, q) == gold for q, gold in queries) / len(queries)


def grounded_answer(embedder, query: str):
    """Retrieve, then 'read' the answer. The shared-space path only has the visual content, so it
    cannot return the in-image number even when it retrieves the right element; the caption path
    can. This is the retrieval-vs-grounding distinction."""
    top_id = retrieve(embedder, query)
    if top_id is None or isinstance(embedder, SharedSpaceEmbedder):
        return None                      # missed retrieval, or the model never saw the in-image text
    return next(d["answer"] for d in CORPUS if d["id"] == top_id)


def _self_test() -> int:
    shared, caption = SharedSpaceEmbedder(), CaptionThenEmbedder()
    # 1) visual queries: both architectures retrieve well
    assert recall_at_1(shared, VISUAL_QUERIES) >= 0.75
    assert recall_at_1(caption, VISUAL_QUERIES) >= 0.75
    # 2) text-in-image queries: shared space can't read -> low recall; caption-then-embed recovers it
    shared_text = recall_at_1(shared, TEXT_IN_IMAGE_QUERIES)
    caption_text = recall_at_1(caption, TEXT_IN_IMAGE_QUERIES)
    assert caption_text - shared_text >= 0.5, (shared_text, caption_text)
    # 3) grounding is separate from retrieval: even when shared space retrieves the right element,
    #    it cannot return the in-image number; the caption path can
    assert grounded_answer(shared, "what was Q4 revenue") is None
    assert grounded_answer(caption, "what was Q4 revenue") == "4.2 million"

    print(f"self-test: visual queries recall@1 shared {recall_at_1(shared, VISUAL_QUERIES):.2f} / "
          f"caption {recall_at_1(caption, VISUAL_QUERIES):.2f}; text-in-image recall@1 shared "
          f"{shared_text:.2f} (CLIP can't read) vs caption {caption_text:.2f}; grounding separates "
          f"retrieval from reading the number OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Runnable multimodal RAG (stand-in embedders)")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("import SharedSpaceEmbedder / CaptionThenEmbedder, or run --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
