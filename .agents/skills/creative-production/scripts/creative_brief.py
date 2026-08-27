#!/usr/bin/env python3
"""Fail-closed Creative Brief validation for quality-first production."""

from __future__ import annotations

CREATIVE_ROLES = {
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

SEMANTIC_STRING_FIELDS = (
    "asset_id",
    "region",
    "creative_role",
    "shopper_task",
    "primary_message",
    "user_value",
    "usage_scene",
    "proof_object",
    "desired_takeaway",
)
LIST_FIELDS = ("must_show", "must_not_show")


def validate_creative_brief(brief: dict) -> dict:
    """Return readiness/errors without mutating ``brief``."""
    if not isinstance(brief, dict):
        return {"ready": False, "errors": ["brief"]}

    errors: list[str] = []
    for field in SEMANTIC_STRING_FIELDS:
        value = brief.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(field)

    if brief.get("creative_role") not in CREATIVE_ROLES and "creative_role" not in errors:
        errors.append("creative_role")

    for field in LIST_FIELDS:
        value = brief.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(field)

    return {"ready": not errors, "errors": errors}
