from __future__ import annotations

from evaluate_asset_quality import evaluate_asset_quality
from quality_profiles import WEIGHTS


def perfect_dimensions() -> dict:
    return dict(WEIGHTS)


def test_hard_blocker_overrides_perfect_score() -> None:
    result = evaluate_asset_quality(
        creative_role="HERO_POSITIONING",
        dimensions=perfect_dimensions(),
        hard_blockers=["PRODUCT_IDENTITY_ERROR"],
    )
    assert result["status"] == "FAIL"
    assert result["score"] == 100
    assert result["recommendable"] is False


def test_general_asset_under_85_is_not_recommendable() -> None:
    dims = perfect_dimensions()
    dims["message_clarity"] = 4  # total 84
    result = evaluate_asset_quality("ECOSYSTEM_COMPATIBILITY", dims, [])
    assert result["score"] == 84
    assert result["status"] == "REVIEW"
    assert result["recommendable"] is False


def test_general_message_clarity_minimum_is_16() -> None:
    dims = perfect_dimensions()
    dims["message_clarity"] = 15
    result = evaluate_asset_quality("SPEC_INSTALLATION", dims, [])
    assert result["score"] == 95
    assert result["status"] == "REVIEW"
    assert result["recommendable"] is False
    assert "message_clarity" in result["minimum_failures"]


def test_hero_requires_role_specific_minimums() -> None:
    dims = perfect_dimensions()
    dims["message_clarity"] = 17
    result = evaluate_asset_quality("HERO_POSITIONING", dims, [])
    assert result["recommendable"] is False
    assert "message_clarity" in result["minimum_failures"]

    dims = perfect_dimensions()
    dims["product_prominence_fidelity"] = 8
    result = evaluate_asset_quality("HERO_POSITIONING", dims, [])
    assert result["recommendable"] is False
    assert "product_prominence_fidelity" in result["minimum_failures"]


def test_differentiator_proof_requires_strong_visual_proof() -> None:
    dims = perfect_dimensions()
    dims["visual_proof_strength"] = 12
    result = evaluate_asset_quality("DIFFERENTIATOR_PROOF", dims, [])
    assert result["score"] == 97
    assert result["recommendable"] is False
    assert "visual_proof_strength" in result["minimum_failures"]


def test_lifestyle_requires_scene_japan_and_value_thresholds() -> None:
    dims = perfect_dimensions()
    dims["japan_localization"] = 8
    result = evaluate_asset_quality("LIFESTYLE_USE_CASE", dims, [])
    assert result["recommendable"] is False
    assert "japan_localization" in result["minimum_failures"]


def test_qualified_hero_can_be_recommendable() -> None:
    result = evaluate_asset_quality("HERO_POSITIONING", perfect_dimensions(), [], notes=["human/model scored"])
    assert result["status"] == "FINAL_QUALITY"
    assert result["recommendable"] is True
    assert result["notes"] == ["human/model scored"]


def test_dimension_over_maximum_is_rejected() -> None:
    dims = perfect_dimensions()
    dims["mobile_legibility"] = 6
    try:
        evaluate_asset_quality("HERO_POSITIONING", dims, [])
    except ValueError as exc:
        assert "mobile_legibility" in str(exc)
    else:
        raise AssertionError("dimension maximum must be enforced")


def test_missing_dimension_is_rejected() -> None:
    dims = perfect_dimensions()
    dims.pop("commercial_polish")
    try:
        evaluate_asset_quality("HERO_POSITIONING", dims, [])
    except ValueError as exc:
        assert "commercial_polish" in str(exc)
    else:
        raise AssertionError("all nine dimensions are required")


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} asset-quality tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
