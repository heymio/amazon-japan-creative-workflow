from __future__ import annotations

from evaluate_set_quality import evaluate_cross_region_value, evaluate_set_quality


def row(asset_id: str, **kwargs) -> dict:
    base = {
        "asset_id": asset_id,
        "composition_family": f"composition-{asset_id}",
        "shopper_task": f"task-{asset_id}",
        "message_id": f"M-{asset_id}",
        "message_depth": 1,
        "priority": "P1",
        "visual_support": True,
        "information_density": "medium",
        "product_identity_mismatch": False,
    }
    base.update(kwargs)
    return base


def message(message_id: str, depth: int) -> dict:
    return {"message_id": message_id, "message_depth": depth}


def test_three_consecutive_same_composition_blocks_set() -> None:
    assets = [
        row("G2", composition_family="copy-left-product-right"),
        row("G3", composition_family="copy-left-product-right"),
        row("G4", composition_family="copy-left-product-right"),
    ]
    result = evaluate_set_quality("gallery", assets)
    assert result["status"] == "FAIL"
    assert "VISUAL_REPETITION" in result["diagnoses"]
    assert ["G2", "G3", "G4"] in result["affected_asset_groups"]


def test_three_consecutive_same_shopper_task_is_flagged() -> None:
    assets = [row("G2", shopper_task="prove core difference"), row("G3", shopper_task="prove core difference"), row("G4", shopper_task="prove core difference")]
    result = evaluate_set_quality("gallery", assets)
    assert result["status"] == "FAIL"
    assert "MESSAGE_REDUNDANCY" in result["diagnoses"]


def test_missing_p0_visual_support_blocks_set() -> None:
    assets = [row("G1", priority="P0", visual_support=False)]
    result = evaluate_set_quality("gallery", assets)
    assert result["status"] == "FAIL"
    assert "STRATEGY_GAP" in result["diagnoses"]


def test_product_identity_mismatch_blocks_set() -> None:
    result = evaluate_set_quality("gallery", [row("G1", product_identity_mismatch=True)])
    assert result["status"] == "FAIL"
    assert "ASSET_DEFECT" in result["diagnoses"]


def test_three_consecutive_high_density_assets_flag_page_rhythm() -> None:
    assets = [row("A1", information_density="high"), row("A2", information_density="high"), row("A3", information_density="high")]
    result = evaluate_set_quality("a-plus", assets)
    assert result["status"] == "FAIL"
    assert "PAGE_RHYTHM" in result["diagnoses"]


def test_duplicate_message_id_same_depth_is_flagged() -> None:
    assets = [row("G2", message_id="M1", message_depth=1), row("G3", message_id="M1", message_depth=1)]
    result = evaluate_set_quality("gallery", assets)
    assert result["status"] == "REVIEW"
    assert "MESSAGE_REDUNDANCY" in result["diagnoses"]


def test_clean_set_passes() -> None:
    assets = [
        row("G1", priority="P0", composition_family="hero", shopper_task="position", message_id="M0"),
        row("G2", composition_family="proof", shopper_task="prove", message_id="M1"),
        row("G3", composition_family="lifestyle", shopper_task="translate value", message_id="M2"),
    ]
    result = evaluate_set_quality("gallery", assets)
    assert result["status"] == "PASS"
    assert result["diagnoses"] == []


def test_aplus_reusing_gallery_message_depth_is_low_incremental_value() -> None:
    result = evaluate_cross_region_value(
        gallery=[message("M1", 1), message("M2", 1)],
        aplus=[message("M1", 1), message("M2", 1)],
    )
    assert result["a_plus_incremental_value"] == "LOW"
    assert result["status"] != "PASS"


def test_aplus_new_or_deeper_messages_can_pass_incremental_value() -> None:
    result = evaluate_cross_region_value(
        gallery=[message("M1", 1), message("M2", 1)],
        aplus=[message("M1", 2), message("M3", 1), message("M2", 2)],
    )
    assert result["incremental_ratio"] == 1.0
    assert result["a_plus_incremental_value"] == "HIGH"
    assert result["status"] == "PASS"


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} set-quality tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
