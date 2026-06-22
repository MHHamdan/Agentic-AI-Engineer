#!/usr/bin/env python3
"""A minimal RAG pipeline from scratch (Lab 03).

Retrieval-augmented generation gives a frozen model fresh, grounded knowledge: instead of answering
from parameters, the system retrieves relevant passages at query time and answers from them, with a
citation. This builds the retrieval half end to end - chunk a corpus, score chunks against a query,
return the best with its source - and adds the two behaviors that separate RAG from a search box:
grounding (the answer comes from a retrieved chunk) and abstention (when nothing is relevant, say so
rather than guess).

The retriever here is lexical: TF-IDF vectors with cosine similarity, after stopword removal. That is
a real retrieval baseline (and the lexical half of hybrid search); a production system would add or
swap in dense embeddings, but the pipeline - chunk, embed, score, ground, cite, abstain - is identical.
The generator is extractive (it returns the retrieved chunk) because the lab is offline; in production
a language model writes the answer from the retrieved context. Deterministic, standard-library only.

References: Lewis et al. (2020), Retrieval-Augmented Generation, arXiv:2005.11401; Robertson & Zaragoza
(2009), BM25 / the probabilistic relevance framework.

Usage:
    python rag.py --self-test
    python rag.py --query "graph index for nearest neighbor search"
"""
from __future__ import annotations

import argparse
import collections
import math
import sys

# A tiny knowledge base. Each entry is a chunk with a source id.
CORPUS = {
    "d1": "HNSW is a graph index for approximate nearest neighbor search over vectors.",
    "d2": "Product quantization compresses vectors to shrink the memory a vector index needs.",
    "d3": "Chunking splits documents into passages before they are embedded for retrieval.",
    "d4": "A reranker reorders retrieved passages with a slower more accurate model.",
    "d5": "Cosine similarity scores how close two embedding vectors are in direction.",
}

STOP = {"a", "an", "the", "is", "are", "was", "were", "of", "for", "to", "in", "on", "and",
        "or", "how", "what", "that", "with", "over", "be", "by", "it", "this", "do", "does"}


def tokenize(text: str) -> list[str]:
    return [w for w in (t.strip(".,").lower() for t in text.split()) if w and w not in STOP]


class Retriever:
    """TF-IDF + cosine. TF rewards terms frequent in a chunk; IDF down-weights terms common across the
    whole corpus, so distinctive words drive the match."""

    def __init__(self, corpus: dict[str, str] = CORPUS):
        self.corpus = corpus
        docs = {d: tokenize(t) for d, t in corpus.items()}
        n = len(docs)
        df = collections.Counter(w for ws in docs.values() for w in set(ws))
        self.idf = {w: math.log((n + 1) / (df[w] + 1)) + 1 for w in df}
        self.vectors = {d: self._vec(ws) for d, ws in docs.items()}

    def _vec(self, words: list[str]) -> dict[str, float]:
        tf = collections.Counter(words)
        return {w: tf[w] * self.idf[w] for w in tf if w in self.idf}

    @staticmethod
    def _cos(a: dict[str, float], b: dict[str, float]) -> float:
        dot = sum(a[w] * b.get(w, 0.0) for w in a)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def retrieve(self, query: str, k: int = 3) -> list[tuple[float, str]]:
        q = self._vec(tokenize(query))
        return sorted(((self._cos(q, self.vectors[d]), d) for d in self.vectors), reverse=True)[:k]

    def answer(self, query: str, threshold: float = 0.08) -> dict:
        """Grounded extractive answer with a citation, or abstain when nothing clears the threshold."""
        top = self.retrieve(query, k=1)[0]
        score, src = top
        if score < threshold:
            return {"answer": "Not enough evidence in the corpus to answer.", "source": None, "score": score}
        return {"answer": self.corpus[src], "source": src, "score": score}


def _self_test() -> int:
    r = Retriever()
    assert Retriever().retrieve("graph index search") == r.retrieve("graph index search")  # deterministic

    # grounding: distinctive queries retrieve and cite the intended chunk
    cases = {"graph index for nearest neighbor search": "d1",
             "what reorders retrieved passages": "d4",
             "compress vectors to shrink memory": "d2"}
    for q, expected in cases.items():
        out = r.answer(q)
        assert out["source"] == expected, (q, out["source"], expected)
        assert out["answer"] == CORPUS[expected]  # the answer is the retrieved chunk, not invented

    # abstention: an out-of-corpus query scores ~0 and is refused rather than answered
    out = r.answer("what is the capital of France")
    assert out["source"] is None and out["score"] < 0.08, out

    print(f"self-test: deterministic TF-IDF retrieval; {len(cases)} queries grounded to the correct "
          f"source and cited; out-of-corpus query abstained (score {out['score']:.2f}) OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Minimal RAG retrieval pipeline")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--query", metavar="TEXT")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    r = Retriever()
    q = args.query or "graph index for nearest neighbor search"
    out = r.answer(q)
    cite = f"  [source: {out['source']}]" if out["source"] else "  [no source — abstained]"
    print(f"Q: {q}\nA: {out['answer']}{cite}  (score {out['score']:.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
