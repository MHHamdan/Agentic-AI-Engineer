#!/usr/bin/env python3
"""Production traces and routing (Lab 56).

Labs 51 and 53 ran on hand-built data. In production the eval and cost loops should run on the
same traces the agent already emits. This lab instruments agent steps as OpenTelemetry spans
following the GenAI semantic conventions (gen_ai.* attributes), then reconstructs the steps from
the exported spans and runs the cost loop over them - proving the loop runs on traces, not on a
parallel data structure. Then it replaces Lab 53's hand-set `simple` flag with a learned
classifier that predicts which steps are routable, and measures the routing saving on predicted
labels against the oracle.

Uses the real OpenTelemetry SDK with an in-memory exporter (offline, deterministic) and
scikit-learn for the classifier.

Usage:
    python traces.py --self-test
"""
from __future__ import annotations
import argparse, sys

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

RATES = {"haiku": (1.0, 5.0), "sonnet": (3.0, 15.0), "opus": (5.0, 25.0)}  # per-M (in, out)
GENAI_OP = "gen_ai.chat"


# --------------------------------------------------------------------------------------------
# OpenTelemetry GenAI instrumentation
# --------------------------------------------------------------------------------------------
def make_tracer():
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider.get_tracer("agent.observability"), exporter


def instrument(tracer, sessions: list[dict]) -> None:
    """Emit one GenAI span per agent step, with the gen_ai.* semantic-convention attributes a
    real instrumentation would set, plus the agent-specific fields the loops need."""
    for sess in sessions:
        for step in sess["steps"]:
            with tracer.start_as_current_span(GENAI_OP) as span:
                span.set_attribute("gen_ai.system", "anthropic")
                span.set_attribute("gen_ai.request.model", step["model"])
                span.set_attribute("gen_ai.usage.input_tokens", step["in_tok"])
                span.set_attribute("gen_ai.usage.output_tokens", step["out_tok"])
                span.set_attribute("agent.session_id", sess["id"])
                span.set_attribute("agent.tool", step.get("tool", ""))
                span.set_attribute("agent.duration_s", step["dur_s"])
                span.set_attribute("agent.simple", bool(step.get("simple", False)))


def steps_from_spans(exporter) -> dict:
    """Reconstruct per-session steps from exported spans. This is what an eval/cost loop sees in
    production: it reads the trace store, not the agent's in-memory objects."""
    by_session: dict[str, list[dict]] = {}
    for span in exporter.get_finished_spans():
        a = span.attributes
        by_session.setdefault(a["agent.session_id"], []).append({
            "model": a["gen_ai.request.model"],
            "in_tok": a["gen_ai.usage.input_tokens"],
            "out_tok": a["gen_ai.usage.output_tokens"],
            "tool": a["agent.tool"], "dur_s": a["agent.duration_s"],
            "simple": a["agent.simple"],
        })
    return by_session


def token_cost(steps: list[dict]) -> float:
    total = 0.0
    for s in steps:
        rin, rout = RATES[s["model"]]
        total += s["in_tok"] / 1e6 * rin + s["out_tok"] / 1e6 * rout
    return total


# --------------------------------------------------------------------------------------------
# Learned routing classifier (replaces Lab 53's hand-set `simple` flag)
# --------------------------------------------------------------------------------------------
def routing_eval(sessions: list[dict]) -> dict:
    """Train a classifier to predict which steps are routable (`simple`) from step features, then
    measure the routing saving on predicted labels vs the oracle, and the misroute rate."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import precision_score, recall_score

    steps = [s for sess in sessions for s in sess["steps"]]
    X = [[s["in_tok"], s["out_tok"], 1 if s["tool"] else 0, s["dur_s"]] for s in steps]
    y = [int(s["simple"]) for s in steps]
    n = len(steps); cut = n // 2
    Xtr, ytr, Xte, yte = X[:cut], y[:cut], X[cut:], y[cut:]
    clf = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
    pred = clf.predict(Xte).tolist()
    prec = precision_score(yte, pred, zero_division=0)
    rec = recall_score(yte, pred, zero_division=0)

    test_steps = steps[cut:]
    def cost_with(route_simple: list[int]) -> float:
        total = 0.0
        for s, simple in zip(test_steps, route_simple):
            model = "haiku" if simple else s["model"]
            rin, rout = RATES[model]
            total += s["in_tok"] / 1e6 * rin + s["out_tok"] / 1e6 * rout
        return total
    base = token_cost(test_steps)
    oracle = cost_with(yte)          # route on the true simple flag
    learned = cost_with(pred)        # route on predictions
    return {"precision": prec, "recall": rec,
            "base": base, "oracle_cost": oracle, "learned_cost": learned,
            "oracle_saving": 1 - oracle / base, "learned_saving": 1 - learned / base}


def _synthetic_sessions() -> list[dict]:
    """A handful of sessions whose `simple` steps are separable from features (routine lookups are
    short, no heavy output; planning steps are longer)."""
    sessions = []
    for i in range(12):
        steps = []
        for k in range(6):
            simple = (k % 3 != 0)
            # a few borderline steps look like the other class (a simple step with a long input,
            # a planning step that is short) so the classifier is good but not perfect.
            # a few simple steps carry planning-like features (long input + output, no tool):
            # genuinely hard cases the classifier will misroute, so it is good but not perfect.
            ambiguous = simple and ((i % 3 == 0 and k == 2) or (i % 4 == 1 and k == 4))
            if simple and not ambiguous:
                in_tok, out_tok, tool, dur = 500 + 30 * k, 120, "search", 2
            elif ambiguous:
                in_tok, out_tok, tool, dur = 1600 + 30 * k, 600, "", 7   # looks like planning
            else:
                in_tok, out_tok, tool, dur = 1600 + 30 * k, 600, "", 7
            steps.append({"model": "opus", "in_tok": in_tok, "out_tok": out_tok,
                          "tool": tool, "dur_s": dur, "simple": simple})
        sessions.append({"id": f"s{i:02d}", "steps": steps})
    return sessions


def _self_test() -> int:
    sessions = _synthetic_sessions()
    tracer, exporter = make_tracer()
    instrument(tracer, sessions)

    # 1) the cost loop runs on the EXPORTED spans and matches the source
    recon = steps_from_spans(exporter)
    cost_from_spans = sum(token_cost(steps) for steps in recon.values())
    cost_from_source = sum(token_cost(s["steps"]) for s in sessions)
    assert abs(cost_from_spans - cost_from_source) < 1e-9, (cost_from_spans, cost_from_source)
    n_spans = len(exporter.get_finished_spans())
    assert n_spans == sum(len(s["steps"]) for s in sessions)
    # spans carry the GenAI semantic-convention attributes
    a0 = exporter.get_finished_spans()[0].attributes
    assert a0["gen_ai.system"] == "anthropic" and "gen_ai.usage.input_tokens" in a0

    # 2) the learned router recovers most of the oracle saving
    r = routing_eval(sessions)
    assert r["precision"] >= 0.8 and r["recall"] >= 0.8, r
    # the learned router recovers most of the oracle saving; misroutes leave some on the table,
    # which is exactly why the routing decision needs its own eval rather than being trusted blind
    assert r["learned_saving"] >= 0.7 * r["oracle_saving"], r

    print(f"self-test: {n_spans} GenAI spans exported; cost loop on spans ${cost_from_spans:.2f} == "
          f"source ${cost_from_source:.2f}; routing classifier P{r['precision']:.2f}/R{r['recall']:.2f}, "
          f"learned saving {r['learned_saving']:.0%} of oracle {r['oracle_saving']:.0%} OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="OTel GenAI traces + learned routing")
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return _self_test()
    print("import this module, or run --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
