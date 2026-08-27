#!/usr/bin/env python3
"""Validate a real-agent pressure-eval result artifact against the canonical cases."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def validate_results(case_manifest: object, result: object, *, expected_commit: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(case_manifest, dict) or not isinstance(case_manifest.get("cases"), list):
        return ["canonical case manifest is invalid"]
    expected_ids = {
        row.get("case_id")
        for row in case_manifest["cases"]
        if isinstance(row, dict) and isinstance(row.get("case_id"), str) and row.get("case_id")
    }
    if len(expected_ids) != 10:
        errors.append("canonical pressure manifest must contain exactly 10 unique case IDs")

    if not isinstance(result, dict):
        return errors + ["result root must be an object"]
    if result.get("schema_version") != "1.0":
        errors.append("result schema_version must be 1.0")
    source_commit = result.get("source_commit")
    if not isinstance(source_commit, str) or not HEX40.fullmatch(source_commit):
        errors.append("result source_commit must be a full lowercase Git SHA")
    if expected_commit is not None:
        expected = expected_commit.strip().casefold()
        if not HEX40.fullmatch(expected):
            errors.append("expected commit must be a full lowercase Git SHA")
        elif source_commit != expected:
            errors.append("real-agent result source_commit does not match intended release commit")
    for field in ("model", "runner"):
        value = result.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"result {field} must be a non-empty string")

    rows = result.get("cases")
    if not isinstance(rows, list):
        return errors + ["result cases must be a list"]
    seen: set[str] = set()
    for index, row in enumerate(rows):
        label = f"cases[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or case_id not in expected_ids:
            errors.append(f"{label}.case_id is unknown or missing")
            continue
        if case_id in seen:
            errors.append(f"duplicate real-agent result for {case_id}")
        seen.add(case_id)
        if row.get("status") != "PASS":
            errors.append(f"{case_id} is not PASS")
        evidence = row.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(f"{case_id} evidence is missing")
    missing = sorted(expected_ids - seen)
    extra = sorted(seen - expected_ids)
    if missing:
        errors.append("missing real-agent cases: " + ", ".join(missing))
    if extra:
        errors.append("unexpected real-agent cases: " + ", ".join(extra))
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    parser.add_argument("--expected-commit", default=None)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "evals" / "agent-pressure" / "manifest.json",
    )
    args = parser.parse_args()
    try:
        cases = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = json.loads(args.result.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read real-agent eval evidence: {exc}")
        return 1
    errors = validate_results(cases, result, expected_commit=args.expected_commit)
    if errors:
        print("FAIL: real-agent pressure results")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: 10 real-agent pressure results bound to intended commit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
