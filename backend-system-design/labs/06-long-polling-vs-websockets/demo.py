"""Runnable lab demo for Long Polling vs WebSockets."""

from __future__ import annotations

from dataclasses import dataclass

TOPIC = "Long Polling vs WebSockets"
FOCUS = "compare long-polling request churn with persistent WebSocket delivery"
BASELINE_STRATEGY = "long_polling"
IMPROVED_STRATEGY = "websocket"
PRIMARY_METRIC = "delivery_latency_ms"


@dataclass(frozen=True)
class ScenarioResult:
    """Stores one strategy result for comparison."""

    strategy: str
    metrics: dict[str, int]


def compare_strategies() -> dict[str, ScenarioResult]:
    """Return baseline and improved results for the lab scenario."""
    baseline = ScenarioResult(
        strategy=BASELINE_STRATEGY,
        metrics={PRIMARY_METRIC: 420, "operations": 10},
    )
    improved = ScenarioResult(
        strategy=IMPROVED_STRATEGY,
        metrics={PRIMARY_METRIC: 95, "operations": 10},
    )
    return {"baseline": baseline, "improved": improved}


def run_demo() -> dict[str, object]:
    """Run the scenario and return a structured summary."""
    results = compare_strategies()
    before = results["baseline"].metrics[PRIMARY_METRIC]
    after = results["improved"].metrics[PRIMARY_METRIC]
    delta = before - after
    return {
        "topic": TOPIC,
        "focus": FOCUS,
        "primary_metric": PRIMARY_METRIC,
        "baseline": results["baseline"],
        "improved": results["improved"],
        "delta": delta,
    }


def main() -> None:
    """Print a concise comparison for command-line use."""
    summary = run_demo()
    baseline = summary["baseline"]
    improved = summary["improved"]
    metric = summary["primary_metric"]

    print(f"{summary['topic']} lab")
    print(f"Focus: {summary['focus']}")
    print(f"Baseline ({baseline.strategy}): {baseline.metrics[metric]} {metric}")
    print(f"Improved ({improved.strategy}): {improved.metrics[metric]} {metric}")
    print(f"Delta: {summary['delta']}")


if __name__ == "__main__":
    main()
