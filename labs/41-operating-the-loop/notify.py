#!/usr/bin/env python3
"""Route a regression to a real on-call channel (Lab 42, item 1).

Lab 41's notifier posted a neutral payload to one generic webhook. Real on-call needs
two more things: (1) provider-shaped payloads (Slack, PagerDuty, GitHub issue), and
(2) severity, so a small dip warns and a large one pages. This keeps the safe no-op
default - with nothing configured it prints and sends nothing, so it is safe to merge.

Usage:
    python notify.py --metric judged_faithfulness --value 0.70 --threshold 0.764 --channel slack
    python notify.py --metric judged_faithfulness --value 0.55 --threshold 0.764 --channel pagerduty
    python notify.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib import request as _request

# How far below threshold (as a fraction of the threshold) escalates warn -> page.
PAGE_FRACTION = 0.10


def should_notify(value: float, threshold: float) -> bool:
    """Alert only on a real regression (below threshold). No news is not an alert."""
    return value < threshold


def severity(value: float, threshold: float, page_fraction: float = PAGE_FRACTION) -> str:
    """Tune your tolerance here: 'ok' at/above threshold, 'warn' just below, 'page' when
    the gap exceeds page_fraction of the threshold. Wire 'page' to a louder channel."""
    if value >= threshold:
        return "ok"
    return "page" if (threshold - value) > page_fraction * threshold else "warn"


def format_alert(metric: str, value: float, threshold: float, run_url: str | None = None) -> dict:
    """Provider-neutral core. The to_* adapters shape it per channel."""
    sev = severity(value, threshold)
    text = (f"RAG eval regression [{sev.upper()}]: {metric} = {value:.3f} "
            f"(threshold {threshold:.3f}). Investigate before the next release.")
    if run_url:
        text += f" Run: {run_url}"
    return {"text": text, "metric": metric, "value": value, "threshold": threshold, "severity": sev}


def to_slack(payload: dict) -> dict:
    """Slack incoming-webhook shape. Emoji by severity."""
    icon = {"page": ":rotating_light:", "warn": ":warning:"}.get(payload["severity"], ":information_source:")
    return {"text": f"{icon} {payload['text']}"}


def to_pagerduty(payload: dict, routing_key: str | None) -> dict:
    """PagerDuty Events API v2 shape. Only 'page' should trigger; others are informational."""
    return {
        "routing_key": routing_key or "ROUTING_KEY_UNSET",
        "event_action": "trigger" if payload["severity"] == "page" else "acknowledge",
        "payload": {"summary": payload["text"], "source": "rag-eval",
                    "severity": "critical" if payload["severity"] == "page" else "warning"},
    }


def to_github_issue(payload: dict) -> dict:
    """GitHub issue shape (for actions/github-script or the REST API)."""
    return {"title": f"[{payload['severity']}] RAG regression: {payload['metric']}",
            "body": payload["text"]}


def route_alert(payload: dict, channel: str, env: dict | None = None) -> dict:
    """Shape the payload for the chosen channel. Pure - returns what WOULD be sent."""
    if channel == "slack":
        return to_slack(payload)
    if channel == "pagerduty":
        return to_pagerduty(payload, (env or {}).get("PAGERDUTY_ROUTING_KEY"))
    if channel == "issue":
        return to_github_issue(payload)
    raise ValueError(f"unknown channel: {channel}")


def post(shaped: dict, url: str | None) -> str:
    """POST to the channel endpoint if configured; otherwise no-op (print only)."""
    if not url:
        return "no endpoint configured - payload printed, not sent"
    data = json.dumps(shaped).encode()
    req = _request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with _request.urlopen(req, timeout=10) as resp:  # pragma: no cover (network)
        return f"posted ({resp.status})"


ENDPOINT_ENV = {"slack": "SLACK_WEBHOOK_URL", "pagerduty": "PAGERDUTY_EVENTS_URL", "issue": None}


def _self_test() -> int:
    assert should_notify(0.70, 0.764) and not should_notify(0.80, 0.764)
    # severity tiers
    assert severity(0.80, 0.764) == "ok"
    assert severity(0.74, 0.764) == "warn"          # just below
    assert severity(0.50, 0.764) == "page"          # far below
    p = format_alert("judged_faithfulness", 0.50, 0.764, "http://run/1")
    assert p["severity"] == "page" and "PAGE" in p["text"]
    # adapters produce the right shapes
    assert "text" in to_slack(p) and to_slack(p)["text"].startswith(":rotating_light:")
    pd = to_pagerduty(p, "rk")
    assert pd["event_action"] == "trigger" and pd["payload"]["severity"] == "critical"
    iss = to_github_issue(p)
    assert iss["title"].startswith("[page]") and iss["body"]
    # a warn does NOT page PagerDuty
    warn = format_alert("m", 0.74, 0.764)
    assert to_pagerduty(warn, "rk")["event_action"] == "acknowledge"
    # routing + safe no-op
    assert route_alert(p, "slack") == to_slack(p)
    assert post(to_slack(p), None).startswith("no endpoint")
    print("self-test: severity + slack/pagerduty/issue adapters + routing + no-op OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Route a nightly regression to on-call")
    ap.add_argument("--metric", default="judged_faithfulness")
    ap.add_argument("--value", type=float)
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--channel", choices=["slack", "pagerduty", "issue"], default="slack")
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
    print(post(shaped, os.environ.get(env_key) if env_key else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
