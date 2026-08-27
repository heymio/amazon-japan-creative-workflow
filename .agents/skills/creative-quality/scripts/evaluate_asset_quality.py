#!/usr/bin/env python3
"""Deterministic decision layer over externally supplied creative-quality scores."""

from __future__ import annotations

from quality_profiles import CREATIVE_ROLES, WEIGHTS, minimums_for_role


def _validate_dimensions(dimensions: dict) -> dict[str, float]:
    if not isinstance(dimensions, dict):
        raise ValueError("dimensions must be a mapping")
    missing = [key for key in WEIGHTS if key not in dimensions]
    extra = [key for key in dimensions if key not in WEIGHTS]
    if missing:
        raise ValueError("missing dimensions: " + ", ".join(missing))
    if extra:
        raise ValueError("unknown dimensions: " + ", ".join(extra))

    result: dict[str, float] = {}
    for key, maximum in WEIGHTS.items():
        value = dimensions[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be numeric")
        if value < 0 or value > maximum:
            raise ValueError(f"{key} must be between 0 and {maximum}")
        result[key] = value
    return result


def _validate_string_list(values: object, label: str) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{label} must be a list of non-empty strings")
    return list(values)


def evaluate_asset_quality(
    creative_role: str,
    dimensions: dict,
    hard_blockers: list[str],
    notes: list[str] | None = None,
) -> dict:
    """Return repeatable triage from semantic scores; never infer aesthetics from pixels."""
    if creative_role not in CREATIVE_ROLES:
        raise ValueError(f"unsupported creative_role: {creative_role}")
    scored = _validate_dimensions(dimensions)
    blockers = _validate_string_list(hard_blockers, "hard_blockers")
    note_values = _validate_string_list(notes, "notes")
    score = sum(scored.values())
    minimums = minimums_for_role(creative_role)

    minimum_failures: list[str] = []
    if score < minimums["total"]:
        minimum_failures.append("total")
    for key, minimum in minimums.items():
        if key == "total":
            continue
        if scored[key] < minimum:
            minimum_failures.append(key)

    if blockers:
        status = "FAIL"
        recommendable = False
    elif score < 80:
        status = "REVISE"
        recommendable = False
    elif score < 85 or minimum_failures:
        status = "REVIEW"
        recommendable = False
    elif score >= 90:
        status = "FINAL_QUALITY"
        recommendable = True
    else:
        status = "PASS"
        recommendable = True

    if isinstance(score, float) and score.is_integer():
        score = int(score)
    return {
        "status": status,
        "hard_blockers": blockers,
        "score": score,
        "dimensions": scored,
        "minimum_failures": minimum_failures,
        "recommendable": recommendable,
        "notes": note_values,
        "evaluation_boundary": "semantic scores are supplied by a visual/model evaluator or human; deterministic CI does not infer subjective aesthetics from pixels",
    }
