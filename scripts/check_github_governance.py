#!/usr/bin/env python3
"""Fail closed on GitHub governance evidence for the v0.1.1 release gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_CHECK_CONTEXT = "validate"
GITHUB_ACTIONS_APP_ID = 15368
REQUIRED_RULE_TYPES = {"pull_request", "required_status_checks", "non_fast_forward", "deletion"}


def _active_ruleset_applies_to_main(ruleset: dict[str, Any]) -> bool:
    if ruleset.get("enforcement") != "active":
        return False
    if ruleset.get("target") not in {None, "branch"}:
        return False
    conditions = ruleset.get("conditions")
    if not isinstance(conditions, dict):
        return False
    ref_name = conditions.get("ref_name")
    if not isinstance(ref_name, dict):
        return False
    include = ref_name.get("include")
    if not isinstance(include, list):
        return False
    return any(item in {"~DEFAULT_BRANCH", "refs/heads/main", "main"} for item in include)


def _rule_types(ruleset: dict[str, Any]) -> set[str]:
    rules = ruleset.get("rules")
    if not isinstance(rules, list):
        return set()
    return {row.get("type") for row in rules if isinstance(row, dict) and isinstance(row.get("type"), str)}


def _required_status_rule(ruleset: dict[str, Any]) -> dict[str, Any] | None:
    rules = ruleset.get("rules")
    if not isinstance(rules, list):
        return None
    for row in rules:
        if isinstance(row, dict) and row.get("type") == "required_status_checks":
            return row
    return None


def _status_check_is_qualified(rule: dict[str, Any] | None) -> tuple[bool, str | None]:
    if not isinstance(rule, dict):
        return False, f"required status check '{REQUIRED_CHECK_CONTEXT}' is missing"
    parameters = rule.get("parameters")
    if not isinstance(parameters, dict):
        return False, f"required status check '{REQUIRED_CHECK_CONTEXT}' parameters are missing"
    checks = parameters.get("required_status_checks")
    if not isinstance(checks, list):
        return False, f"required status check '{REQUIRED_CHECK_CONTEXT}' is missing"

    matching = [row for row in checks if isinstance(row, dict) and row.get("context") == REQUIRED_CHECK_CONTEXT]
    if not matching:
        return False, f"required status check '{REQUIRED_CHECK_CONTEXT}' is missing"
    if not any(row.get("integration_id") == GITHUB_ACTIONS_APP_ID for row in matching):
        return False, (
            f"required status check '{REQUIRED_CHECK_CONTEXT}' must be bound to "
            f"GitHub Actions app {GITHUB_ACTIONS_APP_ID}"
        )
    return True, None


def _qualify_ruleset(ruleset: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    present_types = _rule_types(ruleset)
    missing_types = sorted(REQUIRED_RULE_TYPES - present_types)
    if missing_types:
        reasons.append("missing required rule types: " + ", ".join(missing_types))

    status_ok, status_reason = _status_check_is_qualified(_required_status_rule(ruleset))
    if not status_ok and status_reason:
        reasons.append(status_reason)

    return reasons


def evaluate(branch: object, rulesets: object) -> dict[str, object]:
    reasons: list[str] = []
    protected = isinstance(branch, dict) and branch.get("protected") is True

    if not isinstance(branch, dict) or not isinstance(rulesets, list):
        return {
            "schema_version": "1.0",
            "status": "UNVERIFIED",
            "main_protected": protected,
            "matching_rulesets": 0,
            "qualified_rulesets": 0,
            "reasons": ["branch/ruleset evidence is incomplete"],
        }

    applicable = [row for row in rulesets if isinstance(row, dict) and _active_ruleset_applies_to_main(row)]
    qualified = 0
    for row in applicable:
        row_reasons = _qualify_ruleset(row)
        if not row_reasons:
            qualified += 1
            continue
        name = row.get("name") if isinstance(row.get("name"), str) else "<unnamed>"
        reasons.extend([f"ruleset {name!r}: {reason}" for reason in row_reasons])

    if qualified:
        status = "PASS"
    else:
        status = "FAIL"
        if not applicable:
            reasons.append("no qualifying active ruleset applies to main")

    return {
        "schema_version": "1.0",
        "status": status,
        "main_protected": protected,
        "matching_rulesets": len(applicable),
        "qualified_rulesets": qualified,
        "required_check": REQUIRED_CHECK_CONTEXT,
        "required_check_app_id": GITHUB_ACTIONS_APP_ID,
        "required_rule_types": sorted(REQUIRED_RULE_TYPES),
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("branch_json", type=Path)
    parser.add_argument("rulesets_json", type=Path)
    args = parser.parse_args()
    try:
        branch = json.loads(args.branch_json.read_text(encoding="utf-8"))
        rulesets = json.loads(args.rulesets_json.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema_version": "1.0", "status": "UNVERIFIED", "reasons": [str(exc)]}, indent=2))
        return 2
    result = evaluate(branch, rulesets)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else (1 if result["status"] == "FAIL" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
