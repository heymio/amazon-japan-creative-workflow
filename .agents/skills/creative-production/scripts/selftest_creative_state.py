from __future__ import annotations

from cleanup_policy import auto_retry_eligibility
from production_state import (
    add_candidate,
    approve_candidate,
    build_production_freeze,
    record_auto_revision,
    reopen_asset,
)
from wave_state import can_lock_visual_language, can_start_wave, stop_wave


def ledger_with_asset(asset_id: str) -> dict:
    return {"assets": {asset_id: {"status": "PLANNED", "candidates": [], "auto_revision_count": 0}}}


def approved_asset(asset_id: str, candidate_id: str, output_ref: str) -> dict:
    ledger = add_candidate({}, asset_id, candidate_id, output_ref)
    return approve_candidate(ledger, asset_id, candidate_id, output_ref, "chat:approval")


def handoff(asset_ids: list[str]) -> dict:
    return {
        "asset_set": [{"asset_id": asset_id} for asset_id in asset_ids],
        "page_plan": {"gallery": list(asset_ids), "enhanced_content": [], "other_required_regions": []},
        "page_visual_system": {"asset_directions": [{"asset_id": asset_id} for asset_id in asset_ids]},
    }


def test_third_auto_revision_is_rejected() -> None:
    ledger = ledger_with_asset("G1")
    first = record_auto_revision(ledger, "G1", "G1-v2", "outputs/g1-v2.png", "LOW_PROMINENCE")
    assert first["status"] == "RECORDED"
    second = record_auto_revision(first["ledger"], "G1", "G1-v3", "outputs/g1-v3.png", "LOW_PROMINENCE")
    assert second["status"] == "RECORDED"
    third = record_auto_revision(second["ledger"], "G1", "G1-v4", "outputs/g1-v4.png", "LOW_PROMINENCE")
    assert third["status"] == "BLOCKED"
    assert third["reason"] == "AUTO_RETRY_BUDGET_EXHAUSTED"
    assert third["ledger"]["assets"]["G1"]["auto_revision_count"] == 2


def test_auto_revision_records_diagnosis_on_candidate() -> None:
    result = record_auto_revision(ledger_with_asset("G1"), "G1", "G1-v2", "outputs/g1-v2.png", "LOW_PROMINENCE")
    row = result["ledger"]["assets"]["G1"]
    assert row["auto_revision_count"] == 1
    assert row["candidates"][-1]["diagnosis"] == "LOW_PROMINENCE"
    assert row["candidates"][-1]["generation_kind"] == "AUTO_REVISION"


def test_approved_asset_cannot_be_replaced_without_reopen() -> None:
    ledger = approved_asset("G1", "G1-v2", "outputs/g1-v2.png")
    try:
        add_candidate(ledger, "G1", "G1-v3", "outputs/g1-v3.png")
    except ValueError as exc:
        assert "reopen" in str(exc).casefold()
    else:
        raise AssertionError("approved asset must remain selection-locked")
    assert ledger["assets"]["G1"]["current_output_ref"] == "outputs/g1-v2.png"


def test_approve_candidate_requires_exact_output_ref() -> None:
    ledger = add_candidate({}, "G1", "G1-v2", "outputs/g1-v2.png")
    try:
        approve_candidate(ledger, "G1", "G1-v2", "outputs/other.png", "chat:approval")
    except ValueError as exc:
        assert "output_ref" in str(exc)
    else:
        raise AssertionError("approval must bind exact candidate/output")


def test_reopen_preserves_history_and_actor() -> None:
    ledger = approved_asset("G1", "G1-v2", "outputs/g1-v2.png")
    reopened = reopen_asset(ledger, "G1", "change composition", actor="user")
    row = reopened["assets"]["G1"]
    assert row["status"] == "REVIEW"
    assert row["selected_candidate_id"] == "G1-v2"
    assert row["current_output_ref"] == "outputs/g1-v2.png"
    assert row["reopen_history"][-1] == {"reason": "change composition", "actor": "user"}


def test_batch_cannot_start_before_anchor_lock() -> None:
    state = {"visual_language_locked": False, "anchor_asset_ids": ["G1", "G3"]}
    result = can_start_wave(state, ["G4", "G5"])
    assert result["allowed"] is False
    assert result["reason"] == "VISUAL_LANGUAGE_NOT_LOCKED"


def test_visual_language_requires_two_or_three_approved_anchors() -> None:
    state = {"visual_language_locked": False, "anchor_asset_ids": ["G1", "G3"]}
    ledger = add_candidate({}, "G1", "G1-v1", "outputs/g1.png")
    ledger = approve_candidate(ledger, "G1", "G1-v1", "outputs/g1.png", "chat:g1")
    ledger = add_candidate(ledger, "G3", "G3-v1", "outputs/g3.png")
    ledger = approve_candidate(ledger, "G3", "G3-v1", "outputs/g3.png", "chat:g3")
    ledger["assets"]["G3"]["status"] = "REVIEW"
    assert can_lock_visual_language(state, ledger)["allowed"] is False
    ledger["assets"]["G3"]["status"] = "USER_APPROVED"
    assert can_lock_visual_language(state, ledger)["allowed"] is True
    assert can_lock_visual_language({"anchor_asset_ids": ["G1"]}, ledger)["allowed"] is False
    assert can_lock_visual_language({"anchor_asset_ids": ["G1", "G2", "G3", "G4"]}, ledger)["allowed"] is False


def test_wave_size_is_bounded_to_two_through_four() -> None:
    state = {"visual_language_locked": True}
    assert can_start_wave(state, ["G2"])["allowed"] is False
    assert can_start_wave(state, ["G2", "G4"])["allowed"] is True
    assert can_start_wave(state, ["G2", "G4", "G5", "G6"])["allowed"] is True
    assert can_start_wave(state, ["G2", "G4", "G5", "G6", "A1"])["allowed"] is False


def test_stop_wave_records_reason_and_assets() -> None:
    state = {"visual_language_locked": True, "active_wave": ["G4", "G5"]}
    result = stop_wave(state, "ART_DIRECTION_DRIFT", ["G5"])
    assert result["active_wave"] == []
    assert result["wave_stop_history"][-1] == {"reason": "ART_DIRECTION_DRIFT", "affected_assets": ["G5"]}


def test_upstream_strategy_problems_do_not_consume_auto_retry() -> None:
    for problem in ["MISSING_PROOF_OBJECT", "UNSUPPORTED_CLAIM", "WRONG_SHOPPER_TASK", "STRATEGY_GAP"]:
        result = auto_retry_eligibility(problem)
        assert result["allowed"] is False
        assert result["route"] == "UPSTREAM"
    assert auto_retry_eligibility("LOW_PROMINENCE") == {"allowed": True, "route": "TARGETED_REVISION"}


def test_production_freeze_keeps_exact_candidate_output_binding() -> None:
    ledger = approved_asset("G1", "G1-v2", "outputs/gallery/g1-v2.png")
    ledger["set_qa"] = {
        "status": "CLEAR",
        "reviewed_asset_ids": ["G1"],
        "reviewed_output_refs": {"G1": "outputs/gallery/g1-v2.png"},
        "visual_review_ref": "set-review:1",
    }
    freeze = build_production_freeze(handoff(["G1"]), ledger)
    assert freeze["approved_outputs"] == {
        "G1": {"candidate_id": "G1-v2", "output_ref": "outputs/gallery/g1-v2.png"}
    }
    assert freeze["ready_for_hardening"] is True


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} quality-first production-state tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
