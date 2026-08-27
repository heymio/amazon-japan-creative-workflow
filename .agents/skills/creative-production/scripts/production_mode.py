#!/usr/bin/env python3
"""Provider-agnostic production mode selection."""

from __future__ import annotations

from creative_brief import validate_creative_brief

PRODUCTION_MODES = {
    "SOURCE_COMPOSITE",
    "GENERATIVE_SCENE",
    "PROOF_COMPOSITE",
    "UI_COMPOSITE",
    "DESIGN_LAYOUT",
    "SOURCE_FAITHFUL_EDIT",
    "MOTION_PRODUCTION",
}

DESIGN_ROLES = {"COMPARISON_DECISION", "ECOSYSTEM_COMPATIBILITY", "SPEC_INSTALLATION", "BRAND_STORY"}
PROOF_ROLES = {"DIFFERENTIATOR_PROOF", "MECHANISM_PROOF", "OBJECTION_HANDLING"}


def choose_production_mode(brief: dict, available_sources: dict[str, bool]) -> dict:
    validation = validate_creative_brief(brief)
    if not validation["ready"]:
        return {"status": "BLOCKED", "mode": None, "reason": "CREATIVE_BRIEF_NOT_READY"}

    sources = available_sources if isinstance(available_sources, dict) else {}
    role = brief["creative_role"]

    if brief.get("requires_ui_source"):
        if not sources.get("product", False):
            return {"status": "BLOCKED", "mode": None, "reason": "MISSING_PRODUCT_SOURCE"}
        if not sources.get("ui", False):
            return {"status": "BLOCKED", "mode": None, "reason": "MISSING_UI_SOURCE"}
        return {"status": "READY", "mode": "UI_COMPOSITE", "reason": None}

    if brief.get("source_faithful_edit"):
        if not sources.get("product", False) or not sources.get("source_asset", False):
            return {"status": "BLOCKED", "mode": None, "reason": "MISSING_SOURCE_ASSET"}
        return {"status": "READY", "mode": "SOURCE_FAITHFUL_EDIT", "reason": None}

    if role != "BRAND_STORY" and not sources.get("product", False):
        return {"status": "BLOCKED", "mode": None, "reason": "MISSING_PRODUCT_SOURCE"}

    if brief.get("media_type") in {"video", "motion"}:
        mode = "MOTION_PRODUCTION"
    elif role == "LIFESTYLE_USE_CASE":
        mode = "GENERATIVE_SCENE"
    elif role in PROOF_ROLES:
        mode = "PROOF_COMPOSITE"
    elif role in DESIGN_ROLES:
        mode = "DESIGN_LAYOUT"
    else:
        mode = "SOURCE_COMPOSITE"

    return {"status": "READY", "mode": mode, "reason": None}
