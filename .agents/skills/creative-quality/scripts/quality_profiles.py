#!/usr/bin/env python3
"""Deterministic scoring profile metadata for creative-quality triage."""

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

WEIGHTS = {
    "message_clarity": 20,
    "visual_proof_strength": 15,
    "shopper_value_translation": 15,
    "product_prominence_fidelity": 10,
    "scene_credibility": 10,
    "japan_localization": 10,
    "visual_hierarchy_composition": 10,
    "commercial_polish": 5,
    "mobile_legibility": 5,
}

GENERAL_MINIMUMS = {"total": 85, "message_clarity": 16}

ROLE_MINIMUMS = {
    "HERO_POSITIONING": {
        "total": 88,
        "message_clarity": 18,
        "product_prominence_fidelity": 9,
        "commercial_polish": 4,
    },
    "DIFFERENTIATOR_PROOF": {
        "total": 88,
        "message_clarity": 17,
        "visual_proof_strength": 13,
    },
    "LIFESTYLE_USE_CASE": {
        "total": 85,
        "scene_credibility": 9,
        "japan_localization": 9,
        "shopper_value_translation": 13,
    },
}


def minimums_for_role(creative_role: str) -> dict[str, int]:
    if creative_role not in CREATIVE_ROLES:
        raise ValueError(f"unsupported creative_role: {creative_role}")
    result = dict(GENERAL_MINIMUMS)
    result.update(ROLE_MINIMUMS.get(creative_role, {}))
    return result
