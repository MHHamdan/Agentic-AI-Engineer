#!/usr/bin/env python3
"""A fixed canary set the drift check and nightly job always include (Lab 42, item 4).

Volume-based signals go dark on a quiet day: if little traffic arrives, the drift
window is thin and the nightly eval set may be stale, so a sudden break slips through.
A small fixed canary set - known queries with known routes and reference answers -
gives both jobs a constant heartbeat. If a canary's route flips or its answer breaks,
something regressed regardless of traffic.

Lab 44 grows the set to cover named failure modes (entity confusion, multi-hop
shortcutting, off-corpus overreach, paraphrase brittleness, stale facts, ...) and adds a
corpus-change review: each canary records the corpus docs its answer depends on, so when
the corpus fingerprint changes you know exactly which canaries to revalidate before
trusting them again.

Usage:
    python canary.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CANARIES = HERE / "canary_queries.jsonl"


def load_canaries() -> list[dict]:
    with open(CANARIES) as f:
        return [json.loads(line) for line in f]


def augment_window(window: list[dict], canaries: list[dict]) -> list[dict]:
    """Prepend canaries so the drift window is never empty/quiet. Pure."""
    return [{"query": c["query"]} for c in canaries] + window


def canary_routing_failures(predicted: list[str], canaries: list[dict]) -> list[dict]:
    """Pure: canaries whose predicted route != gold. A non-empty list = a hard break,
    independent of any threshold - these should fail loudly."""
    out = []
    for pred, c in zip(predicted, canaries, strict=False):
        if pred != c["route"]:
            out.append({"query": c["query"], "expected": c["route"], "got": pred})
    return out


def predict_canary_routes() -> list[str]:
    """Route the canary queries with the current model (needs embedder)."""
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression

    with open(HERE.parent / "36-training-the-router" / "router_trainset.jsonl") as f:
        train = [json.loads(line) for line in f]
    cans = load_canaries()
    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    clf = LogisticRegression(max_iter=2000, C=10, class_weight="balanced").fit(
        emb.encode([r["query"] for r in train], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False),
        [r["route"] for r in train])
    return clf.predict(emb.encode([c["query"] for c in cans], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)).tolist()


CORPUS_DIR = HERE.parent / "33-graph-rag-from-scratch" / "corpus"
FINGERPRINT_FILE = HERE / "canary_corpus.fingerprint"


def corpus_fingerprint(corpus_dir: pathlib.Path = CORPUS_DIR) -> str:
    """Stable hash of the corpus contents. A change here means canary answers that depend
    on the corpus may be stale and must be revalidated."""
    h = hashlib.sha256()
    for f in sorted(corpus_dir.glob("*.md")) if corpus_dir.exists() else []:
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def canaries_needing_review(canaries: list[dict], corpus_changed: bool) -> list[dict]:
    """If the corpus changed, every canary with a non-empty corpus_refs must be reviewed
    (its reference answer may no longer match the corpus). Corpus-free canaries (parametric,
    pure off-corpus refusals) are unaffected."""
    if not corpus_changed:
        return []
    return [c for c in canaries if c.get("corpus_refs")]


def review_status(canaries: list[dict], recorded_fp: str | None,
                  current_fp: str | None = None) -> dict:
    """Compare the recorded corpus fingerprint to the current one and list canaries to review."""
    current_fp = current_fp if current_fp is not None else corpus_fingerprint()
    changed = recorded_fp is not None and recorded_fp != current_fp
    return {"corpus_changed": changed, "recorded": recorded_fp, "current": current_fp,
            "to_review": [c["query"] for c in canaries_needing_review(canaries, changed)]}


def _self_test() -> int:
    cans = load_canaries()
    assert len(cans) >= 8 and all("route" in c and "reference" in c for c in cans)
    aug = augment_window([{"query": "live one"}], cans)
    assert len(aug) == len(cans) + 1 and aug[-1]["query"] == "live one"
    # routing-failure detection
    preds = [c["route"] for c in cans]
    preds[0] = "parametric"  # simulate one flip
    fails = canary_routing_failures(preds, cans)
    assert len(fails) == 1 and fails[0]["got"] == "parametric", fails
    assert canary_routing_failures([c["route"] for c in cans], cans) == []
    # failure-mode coverage: the set tags each canary with a named failure mode
    modes = {c.get("failure_mode") for c in cans}
    assert "entity_confusion" in modes and "multihop_shortcut" in modes and "off_corpus_overreach" in modes
    # corpus-change review: a changed fingerprint flags the corpus-dependent canaries
    rs = review_status(cans, recorded_fp="OLDHASH", current_fp="NEWHASH")
    assert rs["corpus_changed"] and len(rs["to_review"]) > 0
    # corpus-free canaries (parametric) are never in the review list
    free = [c["query"] for c in cans if not c.get("corpus_refs")]
    assert all(q not in rs["to_review"] for q in free)
    # unchanged fingerprint -> nothing to review
    assert review_status(cans, recorded_fp="SAME", current_fp="SAME")["to_review"] == []
    print("self-test: load + augment_window + routing-failures + failure-modes + corpus-review OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Canary set helper")
    ap.add_argument("--review", action="store_true", help="check corpus fingerprint for canary review")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.review:
        recorded = FINGERPRINT_FILE.read_text().strip() if FINGERPRINT_FILE.exists() else None
        rs = review_status(load_canaries(), recorded)
        if rs["corpus_changed"]:
            print(f"corpus changed ({rs['recorded']} -> {rs['current']}); revalidate {len(rs['to_review'])} canaries:")
            for q in rs["to_review"]:
                print(f"  - {q}")
            return 2
        print(f"corpus unchanged (fingerprint {rs['current']}); no canary review needed")
        FINGERPRINT_FILE.write_text(rs["current"] + "\n")
        return 0
    fails = canary_routing_failures(predict_canary_routes(), load_canaries())
    if fails:
        print(f"CANARY ROUTING FAILURES ({len(fails)}):")
        for f in fails:
            print(f"  {f['query']!r}: expected {f['expected']}, got {f['got']}")
        return 2
    print(f"all {len(load_canaries())} canaries route correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
