#!/usr/bin/env python3
"""Byte-pair encoding from scratch (Lab 01).

A language model never sees words. It sees token ids. Byte-pair encoding (BPE) is the algorithm that
decides what a token is: start from characters, then repeatedly merge the most frequent adjacent
pair into a new symbol. Common words collapse into one token; rare or unseen words fall back to
smaller pieces. That is why "tokenization tax" is real - an unusual word costs more tokens, hence
more context and more money - and why token counts, not word counts, are what fill the context
window.

This builds BPE end to end: train merges on a tiny corpus, encode and decode, and show that an
unseen word splits into more tokens than a trained one. It is deterministic (ties broken
lexicographically), offline, and standard-library only.

Reference: Sennrich, Haddow, Birch (2016), Neural Machine Translation of Rare Words with Subword
Units, arXiv:1508.07909.

Usage:
    python bpe.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter

END = "</w>"  # marks the end of a word so merges don't cross word boundaries


def _pairs(symbols: list[str]) -> list[tuple[str, str]]:
    return list(zip(symbols[:-1], symbols[1:], strict=False))


def train(corpus_freq: dict[str, int], num_merges: int) -> list[tuple[str, str]]:
    """Learn a merge list from {word: frequency}. Deterministic: at each step take the most frequent
    adjacent pair, breaking ties by lexicographic order of the pair."""
    vocab = {tuple(list(w) + [END]): c for w, c in corpus_freq.items()}
    merges: list[tuple[str, str]] = []
    for _ in range(num_merges):
        counts: Counter = Counter()
        for word, c in vocab.items():
            for p in _pairs(list(word)):
                counts[p] += c
        if not counts:
            break
        best = max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
        merges.append(best)
        vocab = {tuple(_apply_one(list(word), best)): c for word, c in vocab.items()}
    return merges


def _apply_one(symbols: list[str], pair: tuple[str, str]) -> list[str]:
    a, b = pair
    out, i = [], 0
    while i < len(symbols):
        if i < len(symbols) - 1 and symbols[i] == a and symbols[i + 1] == b:
            out.append(a + b)
            i += 2
        else:
            out.append(symbols[i])
            i += 1
    return out


def encode(word: str, merges: list[tuple[str, str]]) -> list[str]:
    """Apply the learned merges in order, greedily, to one word."""
    symbols = list(word) + [END]
    for pair in merges:
        symbols = _apply_one(symbols, pair)
    return symbols


def decode(tokens: list[str]) -> str:
    return "".join(tokens).replace(END, "")


def build_vocab(merges: list[tuple[str, str]], corpus_freq: dict[str, int]) -> dict[str, int]:
    """Assign a stable integer id to every symbol that can appear: base characters + merged units."""
    symbols = {END}
    for w in corpus_freq:
        symbols.update(w)
    for a, b in merges:
        symbols.add(a + b)
    return {s: i for i, s in enumerate(sorted(symbols))}


_CORPUS = {"low": 5, "lower": 2, "lowest": 2, "newer": 6, "wider": 3, "new": 5, "wide": 2}


def _self_test() -> int:
    merges = train(_CORPUS, num_merges=10)
    # deterministic: same corpus + count -> identical merge list
    assert train(_CORPUS, num_merges=10) == merges

    # round-trip for trained words
    for w in _CORPUS:
        assert decode(encode(w, merges)) == w, w

    # a trained word collapses; an unseen word falls back to smaller pieces
    trained = encode("newer", merges)
    unseen = encode("colder", merges)
    assert decode(unseen) == "colder"
    assert len(unseen) > len(trained), (trained, unseen)

    # ids are stable and cover the trained word's symbols. An unseen word may contain characters
    # absent from this tiny corpus (e.g. 'c'); production BPE uses a byte-level base vocabulary of
    # 256 bytes so nothing is ever truly out-of-vocabulary.
    vocab = build_vocab(merges, _CORPUS)
    assert all(tok in vocab for tok in trained)

    print(f"self-test: {len(merges)} deterministic merges; 'newer' -> {len(trained)} token(s), unseen "
          f"'colder' -> {len(unseen)} tokens (rare costs more); round-trip holds; {len(vocab)} ids OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Byte-pair encoding from scratch")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--encode", metavar="WORD")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    merges = train(_CORPUS, num_merges=10)
    if args.encode:
        toks = encode(args.encode, merges)
        print(f"{args.encode!r} -> {toks}  ({len(toks)} tokens)")
    else:
        print("merges:", merges)
    return 0


if __name__ == "__main__":
    sys.exit(main())
