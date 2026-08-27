from __future__ import annotations

import json
from pathlib import Path

from diagnose_page_context import DIAGNOSES, diagnose_page_context

ROOT = Path(__file__).resolve().parents[4]


def make(issue_code: str) -> dict:
    return diagnose_page_context(
        issue_code,
        observed_problem="Observed issue in Amazon page context",
        root_cause="Structured root cause",
        affected_assets=["G3"],
        preserved_assets=["G1", "G2"],
        exact_change="Change only the affected execution property",
        expected_improvement="Restore page-level clarity without reopening good assets",
    )


def test_issue_codes_map_to_exact_diagnosis_families() -> None:
    expected = {
        "PRODUCT_IDENTITY_ERROR": "ASSET_DEFECT",
        "DUPLICATE_MESSAGE": "MESSAGE_REDUNDANCY",
        "THREE_SAME_COMPOSITION": "VISUAL_REPETITION",
        "DENSITY_RUN": "PAGE_RHYTHM",
        "MOBILE_TEXT_TOO_SMALL": "MOBILE_LEGIBILITY",
        "REGION_ROLE_DUPLICATION": "ROLE_OVERLAP",
        "VISUAL_SYSTEM_DRIFT": "ART_DIRECTION_DRIFT",
        "MISSING_PURCHASE_REASON": "STRATEGY_GAP",
    }
    for issue_code, family in expected.items():
        result = make(issue_code)
        assert result["diagnosis_family"] == family
        assert result["diagnosis_family"] in DIAGNOSES


def test_diagnosis_preserves_smallest_sufficient_rework_fields() -> None:
    result = make("THREE_SAME_COMPOSITION")
    assert result["affected_assets"] == ["G3"]
    assert result["preserved_assets"] == ["G1", "G2"]
    for key in ["observed_problem", "root_cause", "exact_change", "expected_improvement"]:
        assert result[key]


def test_unknown_issue_code_is_rejected() -> None:
    try:
        make("MYSTERY_PROBLEM")
    except ValueError as exc:
        assert "MYSTERY_PROBLEM" in str(exc)
    else:
        raise AssertionError("unknown issue code must fail closed")


def test_affected_and_preserved_assets_cannot_overlap() -> None:
    try:
        diagnose_page_context(
            "THREE_SAME_COMPOSITION",
            observed_problem="repeat",
            root_cause="same composition",
            affected_assets=["G3"],
            preserved_assets=["G3"],
            exact_change="change G3 composition",
            expected_improvement="restore rhythm",
        )
    except ValueError as exc:
        assert "overlap" in str(exc).casefold()
    else:
        raise AssertionError("affected/preserved overlap must fail")


def test_adversarial_manifest_covers_deterministic_and_visual_eval_cases() -> None:
    manifest = json.loads((ROOT / "fixtures" / "adversarial" / "manifest.json").read_text(encoding="utf-8"))
    rows = manifest["cases"]
    ids = {row["id"] for row in rows}
    modes = {row["mode"] for row in rows}
    required = {
        "gallery-three-same-composition",
        "a-plus-repeats-gallery",
        "beautiful-but-unclear-message",
        "japan-scene-unnatural-behavior",
        "proof-without-proof-object",
        "product-identity-drift",
        "comparison-inconsistent-basis",
        "invented-ui",
        "mobile-text-illegible",
    }
    assert required <= ids
    assert {"deterministic", "visual-eval"} <= modes
    for row in rows:
        exact = row.get("expected_diagnosis")
        any_values = row.get("expected_diagnosis_any", [])
        assert (exact in DIAGNOSES) or (isinstance(any_values, list) and any(value in DIAGNOSES for value in any_values))


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} page-context diagnosis tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
