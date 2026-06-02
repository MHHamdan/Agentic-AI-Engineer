#!/usr/bin/env python3
"""A fixed canary set the drift check and nightly job always include (Lab 42, item 4).

Volume-based signals go dark on a quiet day: if little traffic arrives, the drift
window is thin and the nightly eval set may be stale, so a sudden break slips through.
A small fixed canary set - known queries with known routes and reference answers -
gives both jobs a constant heartbeat. If a canary's route flips or its answer breaks,
something regressed regardless of traffic.

Lab 44 grows the set to cover named failure modes and adds a corpus-change review keyed on
a single WHOLE-CORPUS fingerprint - which flags every corpus-dependent canary on any change,
even a typo fix in one unrelated doc. Lab 46 keeps a PER-DOCUMENT fingerprint map, so a
change to doc X flags only the canaries whose corpus_refs include X. Same safety, far less
revalidation noise. Lab 48 hashes NORMALIZED content, so a cosmetic reformat (trailing
whitespace, CRLF, an extra blank line) does not count as a change - only content does.

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


MAP_FILE = HERE / "canary_corpus.map.json"


def normalize_corpus_text(raw: bytes) -> str:
    """Format-insensitive view of a document: normalize line endings, strip trailing
    whitespace per line, collapse blank-line runs, and trim leading/trailing blank lines.
    A cosmetic reformat maps to the same string; a content edit does not. This is NOT
    semantic - a reflow that rewraps prose still changes the text (semantic hashing via
    embeddings is out of scope; see the lab)."""
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    out, blanks = [], 0
    for ln in lines:
        if ln == "":
            blanks += 1
            if blanks <= 1:
                out.append("")
        else:
            blanks = 0
            out.append(ln)
    return "\n".join(out).strip("\n") + "\n"


def per_doc_fingerprint(corpus_dir: pathlib.Path = CORPUS_DIR, normalize: bool = True) -> dict:
    """Per-document hashes: {doc_name: sha256[:16]}. With normalize=True (default) a cosmetic
    reformat does not change the hash; pass normalize=False for an exact-bytes fingerprint."""
    out = {}
    for f in sorted(corpus_dir.glob("*.md")) if corpus_dir.exists() else []:
        raw = f.read_bytes()
        data = normalize_corpus_text(raw).encode("utf-8") if normalize else raw
        out[f.name] = hashlib.sha256(data).hexdigest()[:16]
    return out


def changed_docs(old_map: dict, new_map: dict) -> set:
    """Docs that were added, removed, or whose hash changed."""
    changed = set()
    for name in set(old_map) | set(new_map):
        if old_map.get(name) != new_map.get(name):
            changed.add(name)
    return changed


def canaries_for_changed_docs(canaries: list[dict], changed: set) -> list[dict]:
    """Only canaries whose corpus_refs intersect the changed docs need revalidation."""
    if not changed:
        return []
    return [c for c in canaries if set(c.get("corpus_refs", [])) & changed]


def canaries_needing_review(canaries: list[dict], corpus_changed: bool) -> list[dict]:
    """If the corpus changed, every canary with a non-empty corpus_refs must be reviewed
    (its reference answer may no longer match the corpus). Corpus-free canaries (parametric,
    pure off-corpus refusals) are unaffected."""
    if not corpus_changed:
        return []
    return [c for c in canaries if c.get("corpus_refs")]


def review_status(canaries: list[dict], recorded_fp: str | None,
                  current_fp: str | None = None) -> dict:
    """Whole-corpus review (Lab 44): any change flags every corpus-dependent canary."""
    current_fp = current_fp if current_fp is not None else corpus_fingerprint()
    changed = recorded_fp is not None and recorded_fp != current_fp
    return {"corpus_changed": changed, "recorded": recorded_fp, "current": current_fp,
            "to_review": [c["query"] for c in canaries_needing_review(canaries, changed)]}


def review_status_per_doc(canaries: list[dict], old_map: dict, new_map: dict | None = None) -> dict:
    """Per-document review (Lab 46): flag only canaries that depend on a CHANGED doc."""
    new_map = new_map if new_map is not None else per_doc_fingerprint()
    changed = changed_docs(old_map, new_map)
    return {"changed_docs": sorted(changed),
            "to_review": [c["query"] for c in canaries_for_changed_docs(canaries, changed)]}


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
    # per-doc precision: change ONE doc -> only canaries referencing it are flagged
    old_map = {"helix.md": "a", "lattice.md": "b", "beacon.md": "c", "meridian.md": "d",
               "atlas.md": "e", "northgate.md": "f", "cascade.md": "g"}
    new_map = dict(old_map)
    new_map["helix.md"] = "CHANGED"
    pd = review_status_per_doc(cans, old_map, new_map)
    assert pd["changed_docs"] == ["helix.md"]
    flagged = set(pd["to_review"])
    assert flagged and all("helix.md" in c.get("corpus_refs", []) for c in cans if c["query"] in flagged)
    # per-doc flags FEWER than the whole-corpus review (which flags all corpus-dependent)
    whole = [c["query"] for c in cans if c.get("corpus_refs")]
    assert len(pd["to_review"]) < len(whole), (len(pd["to_review"]), len(whole))
    # normalized hashing: a cosmetic reformat does not change the hash; content does
    base = b"# Helix\n\nAanya Rao leads Helix Lab.\n"
    reformat = b"# Helix\r\n\n\nAanya Rao leads Helix Lab.   \n\n"   # CRLF, blank run, trailing ws
    changed = b"# Helix\n\nTomas Vega leads Helix Lab.\n"               # real edit
    def h(blob):
        return hashlib.sha256(normalize_corpus_text(blob).encode()).hexdigest()
    assert h(base) == h(reformat), "reformat should not change the normalized hash"
    assert h(base) != h(changed), "a content edit must change the hash"
    assert hashlib.sha256(base).hexdigest() != hashlib.sha256(reformat).hexdigest()  # raw differs
    print(f"self-test: ... + per-doc review flags {len(pd['to_review'])} vs whole-corpus {len(whole)}; "
          f"normalized hashing ignores reformats OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Canary set helper")
    ap.add_argument("--review", action="store_true", help="check corpus fingerprint for canary review")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.review:
        # Per-document review (Lab 46): flag only canaries depending on a CHANGED doc.
        if MAP_FILE.exists():
            with open(MAP_FILE) as f:
                old_map = json.load(f)
        else:
            old_map = {}
        new_map = per_doc_fingerprint()
        pd = review_status_per_doc(load_canaries(), old_map, new_map)
        if old_map and pd["changed_docs"]:
            print(f"changed docs: {pd['changed_docs']}; revalidate {len(pd['to_review'])} canaries:")
            for q in pd["to_review"]:
                print(f"  - {q}")
            with open(MAP_FILE, "w") as f:
                json.dump(new_map, f, indent=2)
            return 2
        print(f"no corpus-dependent canaries need review ({len(new_map)} docs mapped)")
        with open(MAP_FILE, "w") as f:
                json.dump(new_map, f, indent=2)
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
