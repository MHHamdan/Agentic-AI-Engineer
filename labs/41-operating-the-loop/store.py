#!/usr/bin/env python3
"""Shared alert state so many workers share one view of 'already paged' (Lab 46, item 1).

Lab 44 kept cooldown + rate-limit state in a per-process dict (and a local JSON file). That
is fine for one nightly job, but the moment two workers - two CI runs, two replicas of a
service - evaluate the same regression at once, each has its own view and BOTH page. The
bug is structural: the check ('in cooldown?') and the record ('mark sent') are two steps,
and a second worker can slip between them.

The fix is an ATOMIC claim: one operation that checks the cooldown / rate limit AND records
the send under a lock, returning True for exactly one caller. This module provides a small
StateStore interface with two backends - an in-memory one (single process, the Lab 44
behavior) and a file-lock one (shared across processes on a shared filesystem, a stand-in
for the Redis/DB you'd use in production). `naive_claim` is the racy version, kept only to
demonstrate the bug.

Usage:
    python store.py --self-test
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
import threading
import time


def _free(state: dict, key: str, now: float, cooldown_s: float,
          max_per_window: int, window_s: float) -> bool:
    """Pure predicate: is a send for `key` allowed given current state?"""
    last = state.get("last_sent", {}).get(key)
    if last is not None and (now - last) < cooldown_s:
        return False
    recent = [t for t in state.get("window", []) if now - t < window_s]
    return len(recent) < max_per_window


def _record(state: dict, key: str, now: float, window_s: float) -> dict:
    state.setdefault("last_sent", {})[key] = now
    window = [t for t in state.get("window", []) if now - t < window_s]
    window.append(now)
    state["window"] = window
    return state


class StateStore:
    def try_claim(self, key, now, cooldown_s, max_per_window, window_s) -> bool:
        """Atomically: return True and record the send iff a send is allowed; else False.
        Exactly one of N concurrent callers for the same key gets True."""
        raise NotImplementedError


class InMemoryStore(StateStore):
    """Single-process. Thread-safe within a process, but NOT shared across processes -
    two workers each get their own InMemoryStore and will both page. The Lab 44 default."""
    def __init__(self):
        self._state = {}
        self._lock = threading.Lock()

    def try_claim(self, key, now, cooldown_s, max_per_window, window_s) -> bool:
        with self._lock:
            if not _free(self._state, key, now, cooldown_s, max_per_window, window_s):
                return False
            _record(self._state, key, now, window_s)
            return True


class FileLockStore(StateStore):
    """Shared across processes on a shared filesystem. The whole read-check-write runs
    under an exclusive flock, so the claim is atomic between workers. Stand-in for a real
    shared store (Redis SETNX / a DB row lock) you'd use in production."""
    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump({}, f)

    def try_claim(self, key, now, cooldown_s, max_per_window, window_s) -> bool:
        with open(self.path, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)            # held across the whole critical section
            try:
                try:
                    state = json.load(f)
                except Exception:
                    state = {}
                if not _free(state, key, now, cooldown_s, max_per_window, window_s):
                    return False
                _record(state, key, now, window_s)
                f.seek(0)
                f.truncate()
                json.dump(state, f)
                return True
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)


def naive_claim(path: str, key: str, now: float, cooldown_s: float,
                max_per_window: int, window_s: float, barrier=None) -> bool:
    """The BUGGY version: check, then (later) record, with no lock. Two workers both read
    'free' and both claim. Kept only to demonstrate the race the FileLockStore fixes."""
    with open(path) as f:
        try:
            state = json.load(f)
        except Exception:
            state = {}
    allowed = _free(state, key, now, cooldown_s, max_per_window, window_s)
    if barrier is not None:
        barrier.wait()      # force both workers to finish the check before either writes
    if not allowed:
        return False
    _record(state, key, now, window_s)
    with open(path, "w") as f:
        json.dump(state, f)
    return True


def _race(claim_fn):
    """Run two 'workers' that try to claim the same fresh key at once; count successes."""
    wins = []
    barrier = threading.Barrier(2)
    def worker():
        wins.append(claim_fn(barrier))
    ts = [threading.Thread(target=worker) for _ in range(2)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return sum(1 for w in wins if w)


def _self_test() -> int:
    # in-memory: a second claim for the same key inside cooldown is refused
    s = InMemoryStore()
    assert s.try_claim("k", 0.0, 3600, 5, 3600) is True
    assert s.try_claim("k", 10.0, 3600, 5, 3600) is False     # cooldown
    assert s.try_claim("k", 4000.0, 3600, 5, 3600) is True    # window passed
    # rate limit: 5 distinct keys allowed, 6th blocked within the window
    s2 = InMemoryStore()
    for i in range(5):
        assert s2.try_claim(f"k{i}", float(i), 0, 5, 3600) is True
    assert s2.try_claim("k5", 5.0, 0, 5, 3600) is False

    d = tempfile.mkdtemp()
    # the naive (unlocked) claim RACES: both workers win for the same fresh key
    npath = os.path.join(d, "naive.json")
    with open(npath, "w") as f:
        f.write("{}")
    naive_wins = _race(lambda b: naive_claim(npath, "k", 0.0, 3600, 5, 3600, barrier=b))
    assert naive_wins == 2, f"expected the bug (2 wins), got {naive_wins}"
    # the file-lock store does NOT race: exactly one worker wins
    lpath = os.path.join(d, "locked.json")
    store = FileLockStore(lpath)
    locked_wins = _race(lambda b: store.try_claim("k", 0.0, 3600, 5, 3600))
    assert locked_wins == 1, f"expected atomic claim (1 win), got {locked_wins}"
    print(f"self-test: in-memory cooldown/rate-limit OK; naive races ({naive_wins} wins), "
          f"FileLockStore atomic ({locked_wins} win)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Shared alert state store")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("import this module; or run --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
