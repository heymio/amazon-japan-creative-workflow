#!/usr/bin/env python3
"""Regression tests for the v0.1.1 GitHub governance release gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_github_governance.py"
GITHUB_ACTIONS_APP_ID = 15368
REQUIRED_CHECK = "validate"


def load_module():
    spec = importlib.util.spec_from_file_location("check_github_governance", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pull_request_rule(approvals: int = 0) -> dict:
    return {
        "type": "pull_request",
        "parameters": {
            "allowed_merge_methods": ["merge"],
            "dismiss_stale_reviews_on_push": False,
            "require_code_owner_review": False,
            "require_last_push_approval": False,
            "required_approving_review_count": approvals,
            "required_review_thread_resolution": False,
        },
    }


def status_rule(*, context: str = REQUIRED_CHECK, integration_id: int | None = GITHUB_ACTIONS_APP_ID) -> dict:
    row: dict[str, object] = {"context": context}
    if integration_id is not None:
        row["integration_id"] = integration_id
    return {
        "type": "required_status_checks",
        "parameters": {
            "do_not_enforce_on_create": False,
            "required_status_checks": [row],
            "strict_required_status_checks_policy": True,
        },
    }


def full_rules() -> list[dict]:
    return [
        pull_request_rule(),
        status_rule(),
        {"type": "non_fast_forward"},
        {"type": "deletion"},
    ]


def ruleset(rules: list[dict], *, enforcement: str = "active") -> dict:
    return {
        "id": 101,
        "name": "Protect main",
        "target": "branch",
        "enforcement": enforcement,
        "conditions": {
            "ref_name": {
                "include": ["~DEFAULT_BRANCH"],
                "exclude": [],
            }
        },
        "rules": rules,
    }


def assert_fail(result: dict, needle: str) -> None:
    assert result["status"] == "FAIL", result
    reasons = " | ".join(result.get("reasons", []))
    assert needle in reasons, reasons


def test_unprotected_without_ruleset_fails() -> None:
    module = load_module()
    result = module.evaluate({"protected": False}, [])
    assert_fail(result, "no qualifying")


def test_protected_boolean_alone_does_not_pass() -> None:
    module = load_module()
    result = module.evaluate({"protected": True}, [])
    assert_fail(result, "no qualifying")


def test_matching_ruleset_without_required_rules_fails() -> None:
    module = load_module()
    result = module.evaluate({"protected": False}, [ruleset([])])
    assert_fail(result, "missing required rule types")


def test_evaluate_only_ruleset_does_not_pass() -> None:
    module = load_module()
    result = module.evaluate({"protected": False}, [ruleset(full_rules(), enforcement="evaluate")])
    assert_fail(result, "no qualifying")


def test_wrong_required_check_fails() -> None:
    module = load_module()
    rules = [pull_request_rule(), status_rule(context="some-other-check"), {"type": "non_fast_forward"}, {"type": "deletion"}]
    result = module.evaluate({"protected": False}, [ruleset(rules)])
    assert_fail(result, "required status check 'validate'")


def test_required_check_must_be_from_github_actions() -> None:
    module = load_module()
    rules = [pull_request_rule(), status_rule(integration_id=999), {"type": "non_fast_forward"}, {"type": "deletion"}]
    result = module.evaluate({"protected": False}, [ruleset(rules)])
    assert_fail(result, "GitHub Actions app 15368")


def test_missing_force_push_block_fails() -> None:
    module = load_module()
    rules = [pull_request_rule(), status_rule(), {"type": "deletion"}]
    result = module.evaluate({"protected": False}, [ruleset(rules)])
    assert_fail(result, "non_fast_forward")


def test_full_active_ruleset_passes() -> None:
    module = load_module()
    result = module.evaluate({"protected": False}, [ruleset(full_rules())])
    assert result["status"] == "PASS", result
    assert result["qualified_rulesets"] == 1


def main() -> int:
    tests = [(name, value) for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for name, test in sorted(tests):
        test()
    print(f"PASS: {len(tests)} GitHub governance gate tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
