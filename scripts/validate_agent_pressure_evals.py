#!/usr/bin/env python3
"""Validate M5.1 agent pressure eval definitions without pretending to run an agent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_CATEGORIES = {
    "transition",
    "asset-lock",
    "evidence",
    "rollback",
    "rework",
    "simulator",
    "hardening",
    "context-firewall",
    "golden-path",
}
ALLOWED_ROUTES = {
    "current-stage-owner",
    "listing-strategy",
    "creative-production",
    "creative-quality",
    "listing-simulator-bridge",
    "evidence-hardening",
}


def validate_manifest(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be an object"]
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    cases = data.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases must be a list"]
    if len(cases) != 10:
        errors.append("M5.1 requires exactly 10 pressure cases")
    ids: set[str] = set()
    categories: set[str] = set()
    for index, case in enumerate(cases):
        label = f"case[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{label}.case_id missing")
        elif case_id in ids:
            errors.append(f"duplicate case_id: {case_id}")
        else:
            ids.add(case_id)
        category = case.get("category")
        if not isinstance(category, str) or not category:
            errors.append(f"{label}.category missing")
        else:
            categories.add(category)
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{label}.prompt missing")
        if "real_agent_passed" in case:
            errors.append(f"{label} must not embed real-agent result state")
        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{label}.expected must be an object")
            continue
        route = expected.get("route")
        if route not in ALLOWED_ROUTES:
            errors.append(f"{label}.expected.route invalid: {route!r}")
        if not isinstance(expected.get("advance"), bool):
            errors.append(f"{label}.expected.advance must be boolean")
        if not isinstance(expected.get("requires_current_contract_complete"), bool):
            errors.append(f"{label}.expected.requires_current_contract_complete must be boolean")
        for field in ("must_preserve", "must_not_claim"):
            value = expected.get(field)
            if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
                errors.append(f"{label}.expected.{field} must be a string list")
    missing_categories = sorted(REQUIRED_CATEGORIES - categories)
    if missing_categories:
        errors.append("missing pressure categories: " + ", ".join(missing_categories))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "evals" / "agent-pressure" / "manifest.json",
    )
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read pressure eval manifest: {exc}")
        return 1
    errors = validate_manifest(data)
    if errors:
        print("FAIL: agent pressure eval definitions")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: 10 M5.1 agent pressure eval definitions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
