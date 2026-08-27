#!/usr/bin/env python3
"""Tests for the fail-closed real-agent pressure result validator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "validate_agent_pressure_results.py"
MANIFEST = ROOT / "evals" / "agent-pressure" / "manifest.json"
SHA = "a" * 40


def load():
    spec = importlib.util.spec_from_file_location("m51_agent_results", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture() -> tuple[dict, dict]:
    cases = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = {
        "schema_version": "1.0",
        "source_commit": SHA,
        "model": "real-agent-test-fixture",
        "runner": "fixture-only",
        "cases": [
            {"case_id": row["case_id"], "status": "PASS", "evidence": "observed behavior"}
            for row in cases["cases"]
        ],
    }
    return cases, result


def test_complete_result_passes_contract() -> None:
    module = load()
    cases, result = fixture()
    assert module.validate_results(cases, result, expected_commit=SHA) == []


def test_wrong_commit_fails() -> None:
    module = load()
    cases, result = fixture()
    errors = module.validate_results(cases, result, expected_commit="b" * 40)
    assert any("source_commit" in error for error in errors)


def test_missing_case_fails() -> None:
    module = load()
    cases, result = fixture()
    result["cases"].pop()
    errors = module.validate_results(cases, result, expected_commit=SHA)
    assert any("missing real-agent cases" in error for error in errors)


def test_fail_status_fails() -> None:
    module = load()
    cases, result = fixture()
    result["cases"][0]["status"] = "FAIL"
    errors = module.validate_results(cases, result, expected_commit=SHA)
    assert any("is not PASS" in error for error in errors)


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} real-agent result gate tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
