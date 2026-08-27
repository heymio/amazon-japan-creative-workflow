#!/usr/bin/env python3
"""Anchor-first controlled production wave state."""

from __future__ import annotations

import json


def _copy(value: dict) -> dict:
    return json.loads(json.dumps(value))


def _non_empty_ids(values: object) -> list[str] | None:
    if not isinstance(values, list):
        return None
    if any(not isinstance(value, str) or not value for value in values):
        return None
    if len(set(values)) != len(values):
        return None
    return list(values)


def can_lock_visual_language(state: dict, ledger: dict) -> dict:
    anchors = _non_empty_ids(state.get("anchor_asset_ids")) if isinstance(state, dict) else None
    if anchors is None or not 2 <= len(anchors) <= 3:
        return {"allowed": False, "reason": "ANCHOR_COUNT_INVALID"}
    assets = ledger.get("assets", {}) if isinstance(ledger, dict) else {}
    for asset_id in anchors:
        row = assets.get(asset_id)
        if not isinstance(row, dict) or row.get("status") != "USER_APPROVED":
            return {"allowed": False, "reason": "ANCHOR_NOT_APPROVED"}
        if not isinstance(row.get("selected_candidate_id"), str) or not row.get("selected_candidate_id"):
            return {"allowed": False, "reason": "ANCHOR_SELECTION_MISSING"}
        if not isinstance(row.get("current_output_ref"), str) or not row.get("current_output_ref"):
            return {"allowed": False, "reason": "ANCHOR_OUTPUT_MISSING"}
    return {"allowed": True, "reason": None}


def can_start_wave(state: dict, asset_ids: list[str]) -> dict:
    if not isinstance(state, dict) or state.get("visual_language_locked") is not True:
        return {"allowed": False, "reason": "VISUAL_LANGUAGE_NOT_LOCKED"}
    values = _non_empty_ids(asset_ids)
    if values is None:
        return {"allowed": False, "reason": "WAVE_ASSET_IDS_INVALID"}
    if not 2 <= len(values) <= 4:
        return {"allowed": False, "reason": "WAVE_SIZE_OUT_OF_RANGE"}
    if state.get("active_wave"):
        return {"allowed": False, "reason": "WAVE_ALREADY_ACTIVE"}
    return {"allowed": True, "reason": None}


def stop_wave(state: dict, reason: str, affected_assets: list[str]) -> dict:
    if not isinstance(state, dict):
        raise ValueError("state must be a mapping")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reason must be a non-empty string")
    values = _non_empty_ids(affected_assets)
    if values is None:
        raise ValueError("affected_assets must be unique non-empty Asset IDs")
    result = _copy(state)
    result["active_wave"] = []
    history = result.setdefault("wave_stop_history", [])
    if not isinstance(history, list):
        raise ValueError("wave_stop_history must be a list")
    history.append({"reason": reason, "affected_assets": values})
    return result
