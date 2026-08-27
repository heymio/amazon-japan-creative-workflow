#!/usr/bin/env python3
"""Fail closed on saved GitHub branch/ruleset governance snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _active_rule_applies_to_main(rule: dict[str, Any]) -> bool:
    if rule.get("enforcement") not in {"active", "evaluate"}:
        return False
    conditions = rule.get("conditions")
    if not isinstance(conditions, dict):
        return False
    ref_name = conditions.get("ref_name")
    if not isinstance(ref_name, dict):
        return False
    include = ref_name.get("include")
    if not isinstance(include, list):
        return False
    return any(item in {"~DEFAULT_BRANCH", "refs/heads/main", "main"} for item in include)


def evaluate(branch: object, rulesets: object) -> dict[str, object]:
    reasons: list[str] = []
    protected = isinstance(branch, dict) and branch.get("protected") is True
    applicable_rulesets = []
    if isinstance(rulesets, list):
        applicable_rulesets = [row for row in rulesets if isinstance(row, dict) and _active_rule_applies_to_main(row)]
    elif rulesets is not None:
        reasons.append("rulesets snapshot must be a list")

    if protected:
        status = "PASS"
    elif applicable_rulesets:
        status = "PASS"
    elif isinstance(branch, dict) and isinstance(rulesets, list):
        status = "FAIL"
        reasons.append("main is unprotected and no active matching ruleset was found")
    else:
        status = "UNVERIFIED"
        reasons.append("branch/ruleset evidence is incomplete")

    return {
        "schema_version": "1.0",
        "status": status,
        "main_protected": protected,
        "matching_rulesets": len(applicable_rulesets),
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
