#!/usr/bin/env python3
"""Route a regression to on-call, hardened for real volume (Labs 42 + 44).

Lab 42 added severity and provider adapters. Before pointing this at live traffic it
needs three more things so it neither floods on-call nor drops alerts on a transient
blip: retries with backoff (a flaky webhook shouldn't lose a page), rate limiting (a
storm of regressions shouldn't become a storm of pages), and dedup/cooldown (the same
alert shouldn't re-fire every run while you're already on it). Safe no-op default
unchanged - nothing configured means nothing sent.

Usage:
    python notify.py --metric judged_faithfulness --value 0.55 --threshold 0.764 --channel pagerduty
    python notify.py ... --state-file alert_state.json     # persist cooldown across runs
    python notify.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from urllib import request as _request
from urllib.error import URLError

PAGE_FRACTION = 0.10
# Hardening defaults (tune to your tolerance and on-call appetite).
MAX_ALERTS_PER_WINDOW = 5
RATE_WINDOW_S = 3600        # at most 5 sends per hour, per process
COOLDOWN_S = 6 * 3600       # don't re-fire the same (metric, severity) within 6h
RETRIES = 3
BASE_DELAY_S = 1.0


def should_notify(value: float, threshold: float) -> bool:
    """Alert only on a real regression (below threshold). No news is not an alert."""
    return value < threshold


def severity(value: float, threshold: float, page_fraction: float = PAGE_FRACTION) -> str:
    if value >= threshold:
        return "ok"
    return "page" if (threshold - value) > page_fraction * threshold else "warn"


def format_alert(metric: str, value: float, threshold: float, run_url: str | None = None) -> dict:
    sev = severity(value, threshold)
    text = (f"RAG eval regression [{sev.upper()}]: {metric} = {value:.3f} "
            f"(threshold {threshold:.3f}). Investigate before the next release.")
    if run_url:
        text += f" Run: {run_url}"
    return {"text": text, "metric": metric, "value": value, "threshold": threshold, "severity": sev}


def to_slack(payload: dict) -> dict:
    icon = {"page": ":rotating_light:", "warn": ":warning:"}.get(payload["severity"], ":information_source:")
    return {"text": f"{icon} {payload['text']}"}


def to_pagerduty(payload: dict, routing_key: str | None) -> dict:
    return {"routing_key": routing_key or "ROUTING_KEY_UNSET",
            "event_action": "trigger" if payload["severity"] == "page" else "acknowledge",
            "payload": {"summary": payload["text"], "source": "rag-eval",
                        "severity": "critical" if payload["severity"] == "page" else "warning"}}


def to_github_issue(payload: dict) -> dict:
    return {"title": f"[{payload['severity']}] RAG regression: {payload['metric']}",
            "body": payload["text"]}


def route_alert(payload: dict, channel: str, env: dict | None = None) -> dict:
    if channel == "slack":
        return to_slack(payload)
    if channel == "pagerduty":
        return to_pagerduty(payload, (env or {}).get("PAGERDUTY_ROUTING_KEY"))
    if channel == "issue":
        return to_github_issue(payload)
    raise ValueError(f"unknown channel: {channel}")


# ---- hardening layer (Lab 44, item 1) -------------------------------------------------

def dedup_key(payload: dict) -> str:
    """Two alerts collapse to one if they are the same metric at the same severity.
    A value change at the same severity is the same incident, not a new one."""
    return f"{payload['metric']}::{payload['severity']}"


def in_cooldown(key: str, now: float, state: dict, cooldown_s: float = COOLDOWN_S) -> bool:
    """Suppress a re-fire of the same key within the cooldown window."""
    last = state.get("last_sent", {}).get(key)
    return last is not None and (now - last) < cooldown_s


def record_send(key: str, now: float, state: dict) -> dict:
    state.setdefault("last_sent", {})[key] = now
    state.setdefault("window", []).append(now)
    return state


def rate_limited(now: float, state: dict, max_per_window: int = MAX_ALERTS_PER_WINDOW,
                 window_s: float = RATE_WINDOW_S) -> bool:
    """Fixed-window count: block once max sends have happened inside the window."""
    recent = [t for t in state.get("window", []) if now - t < window_s]
    state["window"] = recent
    return len(recent) >= max_per_window


def send_with_retry(fn, retries: int = RETRIES, base_delay: float = BASE_DELAY_S,
                    sleep=time.sleep) -> str:
    """Call fn() with exponential backoff on transient errors. Raises after the last try."""
    last = None
    for attempt in range(retries):
        try:
            return fn()
        except (URLError, OSError, TimeoutError) as e:  # transient delivery failures
            last = e
            if attempt < retries - 1:
                sleep(base_delay * (2 ** attempt))
    raise RuntimeError(f"delivery failed after {retries} attempts: {last}")


def deliver(shaped: dict, payload: dict, url: str | None, state: dict, now: float,
            sleep=time.sleep) -> tuple[str, dict]:
    """Apply cooldown -> rate-limit -> retry around the actual post. Returns (status, state).
    Never raises for control-flow reasons (suppressed/limited); only a true delivery
    failure after retries propagates."""
    key = dedup_key(payload)
    if in_cooldown(key, now, state):
        return f"suppressed (cooldown): {key}", state
    if rate_limited(now, state):
        return "suppressed (rate limit reached)", state
    if not url:
        state = record_send(key, now, state)   # still record, so no-op runs honor cooldown
        return "no endpoint configured - payload printed, not sent", state
    status = send_with_retry(lambda: post(shaped, url), sleep=sleep)  # pragma: no cover
    state = record_send(key, now, state)
    return status, state


def post(shaped: dict, url: str | None) -> str:
    if not url:
        return "no endpoint configured - payload printed, not sent"
    data = json.dumps(shaped).encode()
    req = _request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with _request.urlopen(req, timeout=10) as resp:  # pragma: no cover (network)
        return f"posted ({resp.status})"


def load_state(path: str | None) -> dict:
    if path and os.path.exists(path):
        try:
            return json.load(open(path))
        except Exception:
            return {}
    return {}


def save_state(path: str | None, state: dict) -> None:
    if path:
        with open(path, "w") as f:
            json.dump(state, f)


ENDPOINT_ENV = {"slack": "SLACK_WEBHOOK_URL", "pagerduty": "PAGERDUTY_EVENTS_URL", "issue": None}


def _self_test() -> int:
    # severity + adapters (unchanged from Lab 42)
    assert severity(0.80, 0.764) == "ok" and severity(0.74, 0.764) == "warn" and severity(0.50, 0.764) == "page"
    p = format_alert("judged_faithfulness", 0.50, 0.764)
    assert to_pagerduty(p, "rk")["event_action"] == "trigger"
    assert to_pagerduty(format_alert("m", 0.74, 0.764), "rk")["event_action"] == "acknowledge"

    # dedup/cooldown: same key inside the window is suppressed; outside it is not
    st = {}
    assert not in_cooldown("k", 0.0, st)
    st = record_send("k", 0.0, st)
    assert in_cooldown("k", 100.0, st, cooldown_s=3600)        # still cooling
    assert not in_cooldown("k", 4000.0, st, cooldown_s=3600)   # window passed

    # rate limit: blocks after max sends in the window
    st2 = {"window": [0.0, 1.0, 2.0, 3.0, 4.0]}
    assert rate_limited(5.0, st2, max_per_window=5, window_s=3600)
    assert not rate_limited(5.0, {"window": [0.0]}, max_per_window=5, window_s=3600)

    # retry: a fn that fails twice then succeeds returns; one that always fails raises
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise URLError("boom")
        return "posted (200)"
    assert send_with_retry(flaky, retries=3, sleep=lambda s: None) == "posted (200)" and calls["n"] == 3
    try:
        send_with_retry(lambda: (_ for _ in ()).throw(URLError("x")), retries=2, sleep=lambda s: None)
        raise AssertionError("send_with_retry should have raised RuntimeError")
    except RuntimeError:
        pass

    # deliver: first send records; immediate second is cooldown-suppressed
    state = {}
    s1, state = deliver(to_slack(p), p, None, state, now=0.0, sleep=lambda s: None)
    s2, state = deliver(to_slack(p), p, None, state, now=10.0, sleep=lambda s: None)
    assert s1.startswith("no endpoint") and s2.startswith("suppressed (cooldown)")
    print("self-test: severity/adapters + dedup/cooldown + rate-limit + retry + deliver OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Route a regression to on-call (hardened)")
    ap.add_argument("--metric", default="judged_faithfulness")
    ap.add_argument("--value", type=float)
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--channel", choices=["slack", "pagerduty", "issue"], default="slack")
    ap.add_argument("--state-file", default=None, help="persist cooldown/rate state across runs")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.value is None or args.threshold is None:
        print("provide --value and --threshold (or --self-test)")
        return 1

    if not should_notify(args.value, args.threshold):
        print(f"{args.metric}={args.value:.3f} within band ({args.threshold:.3f}); no alert")
        return 0
    payload = format_alert(args.metric, args.value, args.threshold, os.environ.get("GITHUB_RUN_URL"))
    shaped = route_alert(payload, args.channel, os.environ)
    print(f"severity={payload['severity']} channel={args.channel}")
    print(json.dumps(shaped, indent=2))
    env_key = ENDPOINT_ENV.get(args.channel)
    url = os.environ.get(env_key) if env_key else None
    state = load_state(args.state_file)
    status, state = deliver(shaped, payload, url, state, now=time.time())
    save_state(args.state_file, state)
    print(status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
