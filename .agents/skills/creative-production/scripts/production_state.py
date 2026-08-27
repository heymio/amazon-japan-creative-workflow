#!/usr/bin/env python3
"""v0.3.3 creative-production state with fail-closed required-set and Freeze bindings."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEGACY_PATH = HERE / "production_state_legacy.py"
SPEC = importlib.util.spec_from_file_location("listing_production_state_legacy", LEGACY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load legacy production state helpers: {LEGACY_PATH}")
_legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_legacy)

ALLOWED_STATUSES = _legacy.ALLOWED_STATUSES
CANDIDATE_STATUSES = _legacy.CANDIDATE_STATUSES
SET_QA_READY_STATUSES = _legacy.SET_QA_READY_STATUSES

add_candidate = _legacy.add_candidate
select_candidate = _legacy.select_candidate
set_creative_status = _legacy.set_creative_status
apply_scope_delta = _legacy.apply_scope_delta


def _copy(value: dict) -> dict:
    return json.loads(json.dumps(value))


def record_auto_revision(ledger: dict, asset_id: str, candidate_id: str, output_ref: str, diagnosis: str) -> dict:
    from cleanup_policy import auto_retry_eligibility

    eligibility = auto_retry_eligibility(diagnosis)
    if eligibility["allowed"] is not True:
        return {"status": "BLOCKED", "reason": "UPSTREAM_STRATEGY_PROBLEM" if eligibility["route"] == "UPSTREAM" else "AUTO_RETRY_NOT_ALLOWED", "ledger": _copy(ledger)}

    row = ledger.get("assets", {}).get(asset_id, {}) if isinstance(ledger, dict) else {}
    count = row.get("auto_revision_count", 0) if isinstance(row, dict) else 0
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("auto_revision_count must be a non-negative integer")
    if count >= 2:
        return {"status": "BLOCKED", "reason": "AUTO_RETRY_BUDGET_EXHAUSTED", "ledger": _copy(ledger)}

    try:
        result = add_candidate(ledger, asset_id, candidate_id, output_ref)
    except ValueError as exc:
        if "reopen" in str(exc).casefold() or "locked" in str(exc).casefold():
            return {"status": "BLOCKED", "reason": "SELECTION_LOCKED", "ledger": _copy(ledger)}
        raise
    asset = result["assets"][asset_id]
    asset["auto_revision_count"] = count + 1
    candidate = asset["candidates"][-1]
    candidate["diagnosis"] = diagnosis
    candidate["generation_kind"] = "AUTO_REVISION"
    return {"status": "RECORDED", "reason": None, "ledger": result}


def approve_candidate(ledger: dict, asset_id: str, candidate_id: str, output_ref: str, approval_ref: str) -> dict:
    if not isinstance(output_ref, str) or not output_ref:
        raise ValueError("output_ref must be a non-empty string")
    row = ledger.get("assets", {}).get(asset_id, {}) if isinstance(ledger, dict) else {}
    candidates = row.get("candidates", []) if isinstance(row, dict) else []
    selected = next((candidate for candidate in candidates if isinstance(candidate, dict) and candidate.get("candidate_id") == candidate_id), None)
    if selected is None:
        raise ValueError(f"candidate_id not found for {asset_id}: {candidate_id}")
    if selected.get("output_ref") != output_ref:
        raise ValueError("output_ref does not match the exact candidate output_ref")
    return select_candidate(ledger, asset_id, candidate_id, approval_ref)


def reopen_asset(ledger: dict, asset_id: str, reason: str, actor: str = "user") -> dict:
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("actor must be a non-empty string")
    result = _legacy.reopen_asset(ledger, asset_id, reason)
    row = result["assets"][asset_id]
    history = row.setdefault("reopen_history", [])
    if not isinstance(history, list):
        raise ValueError("reopen_history must be a list")
    history.append({"reason": reason, "actor": actor})
    return result


def _ordered_unique(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _blocked_ids(handoff: dict) -> set[str]:
    result: set[str] = set()
    for item in handoff.get("blocked_assets", []):
        if isinstance(item, str) and item:
            result.add(item)
        elif isinstance(item, dict):
            asset_id = item.get("asset_id")
            if isinstance(asset_id, str) and asset_id:
                result.add(asset_id)
    return result


def _required_ids(handoff: dict) -> list[str]:
    """Union asset_set, page_plan, and blocked required roles without override semantics."""
    values: list[str] = []
    for item in handoff.get("asset_set", []):
        asset_id = item.get("asset_id") if isinstance(item, dict) else None
        if isinstance(asset_id, str) and asset_id:
            values.append(asset_id)
    page_plan = handoff.get("page_plan") or {}
    if isinstance(page_plan, dict):
        for region in ("gallery", "enhanced_content", "other_required_regions"):
            for asset_id in page_plan.get(region, []):
                if isinstance(asset_id, str) and asset_id:
                    values.append(asset_id)
    values.extend(sorted(_blocked_ids(handoff)))
    return _ordered_unique(values)


def production_progress(handoff: dict, ledger: dict) -> dict:
    required = _required_ids(handoff)
    rows = ledger.get("assets", {}) if isinstance(ledger, dict) else {}
    approved = sum(
        1 for asset_id in required
        if isinstance(rows.get(asset_id), dict) and rows.get(asset_id, {}).get("status") == "USER_APPROVED"
    )
    expected = len(required)
    return {
        "expected": expected,
        "approved": approved,
        "remaining": expected - approved,
        "complete": expected > 0 and expected == approved,
    }


def _set_qa_state(handoff: dict, ledger: dict, required: list[str]) -> tuple[str, bool]:
    # v0.3.3 handoffs require Page Visual System, so absence is no longer a
    # hard-readiness success path.
    if "page_visual_system" not in handoff:
        return "MISSING", False
    return _legacy._set_qa_state(handoff, ledger, required)


def build_production_freeze(handoff: dict, ledger: dict) -> dict:
    required = _required_ids(handoff)
    rows = ledger.get("assets", {}) if isinstance(ledger, dict) else {}
    blocked_from_handoff = _blocked_ids(handoff)
    approved_assets: list[str] = []
    blocked_assets: list[str] = []
    revision_pending: list[str] = []
    approved_outputs: dict[str, dict[str, str]] = {}

    for asset_id in required:
        row = rows.get(asset_id, {}) if isinstance(rows.get(asset_id), dict) else {}
        if asset_id in blocked_from_handoff:
            blocked_assets.append(asset_id)
            continue
        status = row.get("status", "PLANNED")
        if status == "USER_APPROVED":
            candidate_id = row.get("selected_candidate_id")
            output_ref = row.get("current_output_ref")
            if isinstance(candidate_id, str) and candidate_id and isinstance(output_ref, str) and output_ref:
                approved_assets.append(asset_id)
                approved_outputs[asset_id] = {
                    "candidate_id": candidate_id,
                    "output_ref": output_ref,
                }
            else:
                revision_pending.append(asset_id)
        elif status == "BLOCKED":
            blocked_assets.append(asset_id)
        else:
            revision_pending.append(asset_id)

    set_qa_status, set_qa_ready = _set_qa_state(handoff, ledger, required)
    expected = len(required)
    ready = (
        expected > 0
        and len(approved_assets) == expected
        and set(approved_outputs) == set(required)
        and not blocked_assets
        and not revision_pending
        and set_qa_ready
    )
    return {
        "expected_assets": expected,
        "required_asset_ids": list(required),
        "user_approved_assets": approved_assets,
        "blocked_assets": blocked_assets,
        "revision_pending": revision_pending,
        "approved_outputs": approved_outputs,
        "set_qa_status": set_qa_status,
        "ready_for_hardening": ready,
    }
