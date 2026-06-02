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


def _release(state: dict, key: str, claimed_at: float) -> dict:
    """Undo a claim: drop the cooldown marker and the window entry it added. Used when a
    delivery fails after retries, so the slot is free for the next attempt."""
    state.get("last_sent", {}).pop(key, None)
    window = state.get("window", [])
    if claimed_at in window:
        window.remove(claimed_at)
    return state


class StateStore:
    def try_claim(self, key, now, cooldown_s, max_per_window, window_s) -> bool:
        """Atomically: return True and record the send iff a send is allowed; else False.
        Exactly one of N concurrent callers for the same key gets True."""
        raise NotImplementedError

    def release(self, key, claimed_at, window_s) -> None:
        """Free a slot claimed at `claimed_at` (call when delivery ultimately failed)."""
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

    def release(self, key, claimed_at, window_s) -> None:
        with self._lock:
            _release(self._state, key, claimed_at)


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

    def release(self, key, claimed_at, window_s) -> None:
        with open(self.path, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                try:
                    state = json.load(f)
                except Exception:
                    state = {}
                _release(state, key, claimed_at)
                f.seek(0)
                f.truncate()
                json.dump(state, f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)


# ---- distributed backend (Lab 48, item 1) ---------------------------------------------

# One atomic round-trip: check cooldown (last-send value vs now) AND the sliding window,
# and record both only if allowed. Redis runs Lua single-threaded, so this is the claim's
# atomicity across every worker, serverless or multi-region - no read-then-write race.
# KEYS[1] = per-key cooldown; KEYS[2] = GLOBAL window (max N alerts total per window).
# ARGV: now_ms, cooldown_ms, max, window_ms, member (unique "now:key" for the window).
CLAIM_LUA = """
local last = redis.call('GET', KEYS[1])
local now = tonumber(ARGV[1])
local cd  = tonumber(ARGV[2])
local maxn = tonumber(ARGV[3])
local win = tonumber(ARGV[4])
if last and (now - tonumber(last)) < cd then return 0 end
redis.call('ZREMRANGEBYSCORE', KEYS[2], 0, now - win)
if redis.call('ZCARD', KEYS[2]) >= maxn then return 0 end
redis.call('SET', KEYS[1], now, 'PX', cd)
redis.call('ZADD', KEYS[2], now, ARGV[5])
redis.call('PEXPIRE', KEYS[2], win)
return 1
"""
RELEASE_LUA = """
redis.call('DEL', KEYS[1])
redis.call('ZREM', KEYS[2], ARGV[1])
return 1
"""


class RedisStore(StateStore):
    """Shared across any number of workers via Redis. The claim is one atomic Lua call, so
    serverless and multi-region workers share one view of 'already paged'. `client` is a
    redis-py client (or the FakeRedis below for tests). A SQL backend is the same shape:
    one transaction doing `SELECT ... FOR UPDATE` then the conditional insert."""
    def __init__(self, client, namespace: str = "alertstate"):
        self.client = client
        self.ns = namespace

    def _keys(self, key: str):
        return (f"{self.ns}:cd:{key}", f"{self.ns}:win")     # cooldown per key, window global

    def try_claim(self, key, now, cooldown_s, max_per_window, window_s) -> bool:
        cd, win = self._keys(key)
        now_ms = int(now * 1000)
        member = f"{now_ms}:{key}"
        res = self.client.eval(CLAIM_LUA, 2, cd, win, now_ms,
                               int(cooldown_s * 1000), int(max_per_window), int(window_s * 1000), member)
        return int(res) == 1

    def release(self, key, claimed_at, window_s) -> None:
        cd, win = self._keys(key)
        member = f"{int(claimed_at * 1000)}:{key}"
        self.client.eval(RELEASE_LUA, 2, cd, win, member)


class FakeRedis:
    """Minimal in-process Redis for tests and the notebook demo - implements only the
    commands the two scripts use, executed single-threaded (mirroring real Redis). NOT for
    production; install `redis` and pass a real client there."""
    def __init__(self):
        self.kv = {}     # key -> (value, expire_at_ms or None)
        self.z = {}      # key -> {member: score}
        self._now = 0

    def _alive(self, k):
        v = self.kv.get(k)
        if v is None:
            return None
        val, exp = v
        if exp is not None and exp <= self._now:
            self.kv.pop(k, None)
            return None
        return val

    def eval(self, script, numkeys, *args):
        keys = [str(a) for a in args[:numkeys]]
        argv = [str(a) for a in args[numkeys:]]
        if "ZADD" in script and "PEXPIRE" in script:          # CLAIM
            cd_key, win_key = keys
            now, cd, maxn, win = (int(argv[0]), int(argv[1]), int(argv[2]), int(argv[3]))
            member = argv[4]
            self._now = now
            last = self._alive(cd_key)
            if last is not None and (now - int(last)) < cd:
                return 0
            z = self.z.setdefault(win_key, {})
            for m in [m for m, s in z.items() if s <= now - win]:
                z.pop(m, None)
            if len(z) >= maxn:
                return 0
            self.kv[cd_key] = (str(now), now + cd)
            z[member] = now
            return 1
        else:                                                  # RELEASE
            cd_key, win_key = keys
            self.kv.pop(cd_key, None)
            self.z.get(win_key, {}).pop(argv[0], None)
            return 1


def make_store(spec: str):
    """Build a store from a spec: 'memory', 'file:/path', or 'redis://...'."""
    if spec == "memory":
        return InMemoryStore()
    if spec.startswith("file:"):
        return FileLockStore(spec[len("file:"):])
    if spec.startswith("redis://"):
        import redis  # type: ignore
        return RedisStore(redis.Redis.from_url(spec))
    raise ValueError(f"unknown store spec: {spec!r}")


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
    # release frees a slot: claim, release, claim again succeeds inside the same cooldown
    s3 = InMemoryStore()
    assert s3.try_claim("k", 0.0, 3600, 5, 3600) is True
    assert s3.try_claim("k", 1.0, 3600, 5, 3600) is False     # cooled down
    s3.release("k", 0.0, 3600)                                 # delivery failed -> free it
    assert s3.try_claim("k", 2.0, 3600, 5, 3600) is True       # slot is free again

    # RedisStore over the FakeRedis: atomic claim + release, same semantics
    rs = RedisStore(FakeRedis())
    assert rs.try_claim("k", 0.0, 3600, 5, 3600) is True
    assert rs.try_claim("k", 1.0, 3600, 5, 3600) is False     # cooldown
    rs.release("k", 0.0, 3600)
    assert rs.try_claim("k", 2.0, 3600, 5, 3600) is True      # released
    # rate limit on the FakeRedis sliding window
    rs2 = RedisStore(FakeRedis())
    for i in range(5):
        assert rs2.try_claim(f"k{i}", float(i), 0, 5, 3600) is True
    assert rs2.try_claim("k5", 5.0, 0, 5, 3600) is False
    print(f"self-test: in-memory cooldown/rate-limit + release OK; naive races ({naive_wins} wins), "
          f"FileLockStore atomic ({locked_wins} win); RedisStore(FakeRedis) claim+release+ratelimit OK")
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
