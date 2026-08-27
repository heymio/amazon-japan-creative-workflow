#!/usr/bin/env python3
"""Normalize page-context findings into the approved diagnosis taxonomy."""

from __future__ import annotations

DIAGNOSES = {
    "ASSET_DEFECT",
    "MESSAGE_REDUNDANCY",
    "VISUAL_REPETITION",
    "PAGE_RHYTHM",
    "MOBILE_LEGIBILITY",
    "ROLE_OVERLAP",
    "ART_DIRECTION_DRIFT",
    "STRATEGY_GAP",
}

ISSUE_TO_DIAGNOSIS = {
    "PRODUCT_IDENTITY_ERROR": "ASSET_DEFECT",
    "INVENTED_UI": "ASSET_DEFECT",
    "AI_ARTIFACT": "ASSET_DEFECT",
    "UNNATURAL_BEHAVIOR": "ASSET_DEFECT",
    "UNCLEAR_MESSAGE": "ASSET_DEFECT",
    "COMPARISON_INCONSISTENT_BASIS": "STRATEGY_GAP",
    "PROOF_OBJECT_MISSING": "STRATEGY_GAP",
    "MISSING_PURCHASE_REASON": "STRATEGY_GAP",
    "DUPLICATE_MESSAGE": "MESSAGE_REDUNDANCY",
    "THREE_SAME_COMPOSITION": "VISUAL_REPETITION",
    "DENSITY_RUN": "PAGE_RHYTHM",
    "MOBILE_TEXT_TOO_SMALL": "MOBILE_LEGIBILITY",
    "REGION_ROLE_DUPLICATION": "ROLE_OVERLAP",
    "VISUAL_SYSTEM_DRIFT": "ART_DIRECTION_DRIFT",
}


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _ids(values: object, label: str) -> list[str]:
    if not isinstance(values, list):
        raise ValueError(f"{label} must be a list")
    result: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label}[{index}] must be a non-empty Asset ID")
        if value in result:
            raise ValueError(f"duplicate {label} Asset ID: {value}")
        result.append(value)
    return result


def diagnose_page_context(
    issue_code: str,
    *,
    observed_problem: str,
    root_cause: str,
    affected_assets: list[str],
    preserved_assets: list[str],
    exact_change: str,
    expected_improvement: str,
) -> dict:
    issue = _text(issue_code, "issue_code")
    family = ISSUE_TO_DIAGNOSIS.get(issue)
    if family is None:
        raise ValueError(f"unsupported issue_code: {issue}")
    affected = _ids(affected_assets, "affected_assets")
    preserved = _ids(preserved_assets, "preserved_assets")
    overlap = sorted(set(affected) & set(preserved))
    if overlap:
        raise ValueError("affected_assets and preserved_assets overlap: " + ", ".join(overlap))
    return {
        "issue_code": issue,
        "diagnosis_family": family,
        "observed_problem": _text(observed_problem, "observed_problem"),
        "root_cause": _text(root_cause, "root_cause"),
        "affected_assets": affected,
        "preserved_assets": preserved,
        "exact_change": _text(exact_change, "exact_change"),
        "expected_improvement": _text(expected_improvement, "expected_improvement"),
    }
