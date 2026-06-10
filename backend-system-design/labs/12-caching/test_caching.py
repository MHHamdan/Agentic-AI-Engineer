"""Tests for the Caching runnable lab."""

import importlib.util
import sys
from pathlib import Path


def load_demo_module():
    """Load this lab's demo module from its file path."""
    module_path = Path(__file__).with_name("demo.py")
    spec = importlib.util.spec_from_file_location(
        "lab_12_caching",
        module_path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_run_demo_identifies_topic():
    """The demo should return the expected topic name."""
    demo = load_demo_module()
    summary = demo.run_demo()
    assert summary["topic"] == "Caching"
    assert summary["primary_metric"] == "database_reads"


def test_improved_strategy_is_not_worse():
    """The improved strategy should reduce the primary cost metric."""
    demo = load_demo_module()
    summary = demo.run_demo()
    metric = summary["primary_metric"]
    baseline_value = summary["baseline"].metrics[metric]
    improved_value = summary["improved"].metrics[metric]
    assert improved_value <= baseline_value


def test_main_prints_summary(capsys):
    """The command-line entry point should print a readable summary."""
    demo = load_demo_module()
    demo.main()
    output = capsys.readouterr().out
    assert "Caching lab" in output
    assert "Delta:" in output


