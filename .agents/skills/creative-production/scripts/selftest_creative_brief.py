from __future__ import annotations

import copy

from creative_brief import validate_creative_brief
from production_mode import choose_production_mode
from project_asset_packet import project_generation_context

ROLES = {
    "HERO_POSITIONING",
    "DIFFERENTIATOR_PROOF",
    "MECHANISM_PROOF",
    "LIFESTYLE_USE_CASE",
    "COMPARISON_DECISION",
    "ECOSYSTEM_COMPATIBILITY",
    "SPEC_INSTALLATION",
    "OBJECTION_HANDLING",
    "BRAND_STORY",
}
MODES = {
    "SOURCE_COMPOSITE",
    "GENERATIVE_SCENE",
    "PROOF_COMPOSITE",
    "UI_COMPOSITE",
    "DESIGN_LAYOUT",
    "SOURCE_FAITHFUL_EDIT",
    "MOTION_PRODUCTION",
}


def valid_brief(role: str = "DIFFERENTIATOR_PROOF") -> dict:
    return {
        "asset_id": "G3",
        "region": "gallery",
        "creative_role": role,
        "shopper_task": "Understand the primary differentiator quickly",
        "primary_message": "Wide coverage reduces blind spots",
        "user_value": "See more of the entrance area with less manual adjustment",
        "usage_scene": "Japanese detached-home entrance",
        "proof_object": "Coverage arc anchored to the real product orientation",
        "desired_takeaway": "This product covers more of the area I care about",
        "must_show": ["real product", "coverage relationship"],
        "must_not_show": ["invented UI", "impossible coverage"],
        "media_type": "image",
    }


def valid_ui_brief() -> dict:
    brief = valid_brief("MECHANISM_PROOF")
    brief["proof_object"] = "Real application screen showing the product state"
    brief["requires_ui_source"] = True
    return brief


def test_valid_brief_is_ready() -> None:
    source = valid_brief()
    before = copy.deepcopy(source)
    result = validate_creative_brief(source)
    assert result == {"ready": True, "errors": []}
    assert source == before, "validator must not mutate input"


def test_missing_proof_object_blocks_brief() -> None:
    brief = valid_brief()
    brief["proof_object"] = ""
    result = validate_creative_brief(brief)
    assert result["ready"] is False
    assert "proof_object" in result["errors"]


def test_invalid_role_blocks_brief() -> None:
    brief = valid_brief()
    brief["creative_role"] = "A_PLUS"
    result = validate_creative_brief(brief)
    assert result["ready"] is False
    assert "creative_role" in result["errors"]


def test_must_show_and_must_not_show_are_lists() -> None:
    brief = valid_brief()
    brief["must_show"] = "real product"
    result = validate_creative_brief(brief)
    assert result["ready"] is False
    assert "must_show" in result["errors"]


def test_ui_brief_without_ui_source_is_blocked() -> None:
    result = choose_production_mode(valid_ui_brief(), available_sources={"product": True, "ui": False})
    assert result == {"status": "BLOCKED", "mode": None, "reason": "MISSING_UI_SOURCE"}


def test_ui_brief_with_ui_source_uses_ui_composite() -> None:
    result = choose_production_mode(valid_ui_brief(), available_sources={"product": True, "ui": True})
    assert result == {"status": "READY", "mode": "UI_COMPOSITE", "reason": None}


def test_motion_media_uses_motion_production() -> None:
    brief = valid_brief("LIFESTYLE_USE_CASE")
    brief["media_type"] = "video"
    result = choose_production_mode(brief, available_sources={"product": True, "ui": False})
    assert result["status"] == "READY"
    assert result["mode"] == "MOTION_PRODUCTION"


def test_comparison_role_uses_design_layout() -> None:
    result = choose_production_mode(valid_brief("COMPARISON_DECISION"), available_sources={"product": True})
    assert result["mode"] == "DESIGN_LAYOUT"


def test_proof_role_prefers_proof_composite() -> None:
    result = choose_production_mode(valid_brief("DIFFERENTIATOR_PROOF"), available_sources={"product": True})
    assert result["mode"] == "PROOF_COMPOSITE"


def test_lifestyle_role_uses_generative_scene_when_product_source_exists() -> None:
    result = choose_production_mode(valid_brief("LIFESTYLE_USE_CASE"), available_sources={"product": True})
    assert result["mode"] == "GENERATIVE_SCENE"


def test_missing_product_source_blocks_product_dependent_modes() -> None:
    result = choose_production_mode(valid_brief("HERO_POSITIONING"), available_sources={"product": False})
    assert result == {"status": "BLOCKED", "mode": None, "reason": "MISSING_PRODUCT_SOURCE"}



def valid_generation_packet() -> dict:
    return {
        "creative_brief": valid_brief(),
        "product_identity_sources": ["source:product-render"],
        "ui_sources": [],
        "page_visual_direction": {"composition_family": "proof-led"},
        "nearest_neighbors": [{"asset_id": "G2", "composition_family": "hero"}],
        "japan_scene_constraints": ["realistic Japanese entrance scale"],
        "evidence_mode": "PROOF_VISUAL",
    }


def test_generation_packet_projects_only_the_allowed_context() -> None:
    packet = valid_generation_packet()
    projected = project_generation_context(packet)
    assert projected == packet


def test_generation_packet_rejects_control_plane_keys() -> None:
    packet = valid_generation_packet()
    packet["delivery_state"] = {"stage": 8}
    try:
        project_generation_context(packet)
    except ValueError as exc:
        assert "delivery_state" in str(exc)
    else:
        raise AssertionError("control-plane key must be rejected")


def test_generation_packet_rejects_full_research_history() -> None:
    packet = valid_generation_packet()
    packet["research_history"] = ["unrelated project context"]
    try:
        project_generation_context(packet)
    except ValueError as exc:
        assert "research_history" in str(exc)
    else:
        raise AssertionError("full research history must be rejected")

def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} creative brief / production mode tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
