#!/usr/bin/env python3
"""Deterministic whole-set creative QA over structured annotations."""

from __future__ import annotations

from collections import defaultdict


def _require_assets(assets: object) -> list[dict]:
    if not isinstance(assets, list):
        raise ValueError("assets must be an ordered list")
    result: list[dict] = []
    seen: set[str] = set()
    for index, row in enumerate(assets):
        if not isinstance(row, dict):
            raise ValueError(f"assets[{index}] must be a mapping")
        asset_id = row.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id:
            raise ValueError(f"assets[{index}].asset_id must be a non-empty string")
        if asset_id in seen:
            raise ValueError(f"duplicate asset_id: {asset_id}")
        seen.add(asset_id)
        result.append(row)
    return result


def _run_groups(rows: list[dict], key: str, value: object | None = None) -> list[list[str]]:
    groups: list[list[str]] = []
    start = 0
    while start < len(rows):
        current = rows[start].get(key)
        end = start + 1
        while end < len(rows) and rows[end].get(key) == current:
            end += 1
        if end - start >= 3 and (value is None or current == value):
            groups.append([row["asset_id"] for row in rows[start:end]])
        start = end
    return groups


def evaluate_set_quality(region: str, assets: list[dict]) -> dict:
    if not isinstance(region, str) or not region.strip():
        raise ValueError("region must be a non-empty string")
    rows = _require_assets(assets)
    diagnoses: list[str] = []
    affected_groups: list[list[str]] = []
    fail = False
    review = False

    for group in _run_groups(rows, "composition_family"):
        diagnoses.append("VISUAL_REPETITION")
        affected_groups.append(group)
        fail = True

    for group in _run_groups(rows, "shopper_task"):
        diagnoses.append("MESSAGE_REDUNDANCY")
        affected_groups.append(group)
        fail = True

    for group in _run_groups(rows, "information_density", "high"):
        diagnoses.append("PAGE_RHYTHM")
        affected_groups.append(group)
        fail = True

    p0_missing = [row["asset_id"] for row in rows if row.get("priority") == "P0" and row.get("visual_support") is not True]
    if p0_missing:
        diagnoses.append("STRATEGY_GAP")
        affected_groups.append(p0_missing)
        fail = True

    identity_bad = [row["asset_id"] for row in rows if row.get("product_identity_mismatch") is True]
    if identity_bad:
        diagnoses.append("ASSET_DEFECT")
        affected_groups.append(identity_bad)
        fail = True

    by_message_depth: dict[tuple[str, object], list[str]] = defaultdict(list)
    for row in rows:
        message_id = row.get("message_id")
        depth = row.get("message_depth")
        if isinstance(message_id, str) and message_id:
            by_message_depth[(message_id, depth)].append(row["asset_id"])
    for ids in by_message_depth.values():
        if len(ids) >= 2:
            diagnoses.append("MESSAGE_REDUNDANCY")
            affected_groups.append(ids)
            review = True

    # Stable, deterministic ordering with no duplicate diagnosis labels/groups.
    diagnoses = list(dict.fromkeys(diagnoses))
    unique_groups: list[list[str]] = []
    seen_groups: set[tuple[str, ...]] = set()
    for group in affected_groups:
        key = tuple(group)
        if key not in seen_groups:
            seen_groups.add(key)
            unique_groups.append(group)

    status = "FAIL" if fail else "REVIEW" if review else "PASS"
    return {
        "region": region,
        "status": status,
        "diagnoses": diagnoses,
        "affected_asset_groups": unique_groups,
        "evaluation_boundary": "deterministic rules use supplied labels/IDs; semantic visual similarity remains a visual/model or human eval",
    }


def _message_rows(values: object, label: str) -> list[dict]:
    if not isinstance(values, list):
        raise ValueError(f"{label} must be a list")
    result: list[dict] = []
    for index, row in enumerate(values):
        if not isinstance(row, dict):
            raise ValueError(f"{label}[{index}] must be a mapping")
        message_id = row.get("message_id")
        depth = row.get("message_depth")
        if not isinstance(message_id, str) or not message_id:
            raise ValueError(f"{label}[{index}].message_id must be non-empty")
        if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
            raise ValueError(f"{label}[{index}].message_depth must be a non-negative integer")
        result.append({"message_id": message_id, "message_depth": depth})
    return result


def evaluate_cross_region_value(gallery: list[dict], aplus: list[dict]) -> dict:
    gallery_rows = _message_rows(gallery, "gallery")
    aplus_rows = _message_rows(aplus, "aplus")
    gallery_depth: dict[str, int] = {}
    for row in gallery_rows:
        gallery_depth[row["message_id"]] = max(gallery_depth.get(row["message_id"], -1), row["message_depth"])

    incremental = 0
    for row in aplus_rows:
        prior = gallery_depth.get(row["message_id"])
        if prior is None or row["message_depth"] > prior:
            incremental += 1
    ratio = incremental / len(aplus_rows) if aplus_rows else 0.0
    ratio = round(ratio, 4)
    if ratio >= 0.6:
        level = "HIGH"
        status = "PASS"
    elif ratio >= 0.3:
        level = "MEDIUM"
        status = "REVIEW"
    else:
        level = "LOW"
        status = "REVIEW"
    return {
        "status": status,
        "a_plus_incremental_value": level,
        "incremental_ratio": ratio,
        "incremental_count": incremental,
        "a_plus_message_count": len(aplus_rows),
    }
