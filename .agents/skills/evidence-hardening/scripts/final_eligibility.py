#!/usr/bin/env python3
"""Fail-closed Stage 10 final eligibility reconciliation.

This module does not render Amazon UI and does not perform the physical audit itself.
It reconciles Production Freeze, listing-evidence-auditor results, Simulator bindings,
and exact final-HTML runtime evidence into one hard verification result.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

HEX64 = re.compile(r"^[0-9a-f]{64}$")
FINAL_CONSUMABLE_EVIDENCE = {"VERIFIED", "HUMAN_APPROVED"}
EVIDENCE_FAIL = {"INVALIDATED"}
REQUIRED_MOBILE_WIDTHS = ("375", "390", "430")
CHECK_NAMES = (
    "production_freeze",
    "exact_asset_evidence",
    "simulator_binding",
    "final_runtime",
)


def _nonempty_strings(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def _finish_check(conflicts: list[str], unknowns: list[str], before_conflicts: int, before_unknowns: int) -> str:
    if len(conflicts) > before_conflicts:
        return "FAIL"
    if len(unknowns) > before_unknowns:
        return "UNVERIFIED"
    return "PASS"


def _production_freeze_check(packet: dict[str, Any], conflicts: list[str], unknowns: list[str]) -> tuple[str, list[str], dict[str, dict[str, str]]]:
    before_conflicts = len(conflicts)
    before_unknowns = len(unknowns)
    freeze = packet.get("production_freeze")
    if freeze is None:
        unknowns.append("PRODUCTION_FREEZE_MISSING")
        return "UNVERIFIED", [], {}
    if not isinstance(freeze, dict):
        conflicts.append("PRODUCTION_FREEZE_MALFORMED")
        return "FAIL", [], {}

    required = freeze.get("required_asset_ids")
    required_ids = required if _nonempty_strings(required) else []
    if not required_ids:
        conflicts.append("REQUIRED_ASSET_SET_INVALID")
    elif len(set(required_ids)) != len(required_ids):
        conflicts.append("REQUIRED_ASSET_IDS_DUPLICATED")

    expected = freeze.get("expected_assets")
    if not isinstance(expected, int) or isinstance(expected, bool) or expected != len(required_ids):
        conflicts.append("EXPECTED_ASSET_COUNT_MISMATCH")

    approved = freeze.get("user_approved_assets")
    if not isinstance(approved, list) or any(not isinstance(item, str) or not item for item in approved):
        conflicts.append("USER_APPROVED_ASSET_SET_INVALID")
        approved = []
    if set(approved) != set(required_ids):
        conflicts.append("USER_APPROVED_ASSET_SET_MISMATCH")

    if freeze.get("blocked_assets") not in ([], None):
        conflicts.append("PRODUCTION_FREEZE_HAS_BLOCKED_ASSETS")
    if freeze.get("revision_pending") not in ([], None):
        conflicts.append("PRODUCTION_FREEZE_HAS_PENDING_REVISIONS")
    if freeze.get("set_qa_status") not in {"CLEAR", "USER_ACCEPTED"}:
        conflicts.append("SET_QA_NOT_FINAL")
    if freeze.get("ready_for_hardening") is not True:
        conflicts.append("PRODUCTION_FREEZE_NOT_READY")

    outputs = freeze.get("approved_outputs")
    normalized_outputs: dict[str, dict[str, str]] = {}
    if not isinstance(outputs, dict):
        conflicts.append("APPROVED_OUTPUTS_INVALID")
    else:
        if set(outputs) != set(required_ids):
            conflicts.append("APPROVED_OUTPUT_SET_MISMATCH")
        seen_refs: set[str] = set()
        for asset_id in required_ids:
            row = outputs.get(asset_id)
            if not isinstance(row, dict):
                conflicts.append("APPROVED_OUTPUT_ROW_INVALID")
                continue
            candidate_id = row.get("candidate_id")
            output_ref = row.get("output_ref")
            if not isinstance(candidate_id, str) or not candidate_id:
                conflicts.append("APPROVED_CANDIDATE_ID_MISSING")
                continue
            if not isinstance(output_ref, str) or not output_ref:
                conflicts.append("APPROVED_OUTPUT_REF_MISSING")
                continue
            if output_ref in seen_refs:
                conflicts.append("DUPLICATE_APPROVED_OUTPUT_REF")
            seen_refs.add(output_ref)
            normalized_outputs[asset_id] = {"candidate_id": candidate_id, "output_ref": output_ref}

    return _finish_check(conflicts, unknowns, before_conflicts, before_unknowns), required_ids, normalized_outputs


def _asset_evidence_check(
    packet: dict[str, Any],
    required_ids: list[str],
    approved_outputs: dict[str, dict[str, str]],
    conflicts: list[str],
    unknowns: list[str],
) -> str:
    before_conflicts = len(conflicts)
    before_unknowns = len(unknowns)
    evidence = packet.get("auditor_evidence")
    if evidence is None:
        unknowns.append("AUDITOR_EVIDENCE_MISSING")
        return "UNVERIFIED"
    if not isinstance(evidence, dict):
        conflicts.append("AUDITOR_EVIDENCE_MALFORMED")
        return "FAIL"

    checkpoint = evidence.get("checkpoint")
    if checkpoint not in {"pre-9", "final"}:
        unknowns.append("AUDITOR_CHECKPOINT_UNVERIFIED")

    set_gate = evidence.get("asset_set_gate")
    if not isinstance(set_gate, dict):
        unknowns.append("AUDITOR_ASSET_SET_GATE_MISSING")
    elif set_gate.get("status") == "FAIL":
        conflicts.append("AUDITOR_ASSET_SET_GATE_FAILED")
    elif set_gate.get("status") != "PASS":
        unknowns.append("AUDITOR_ASSET_SET_GATE_UNVERIFIED")

    assets = evidence.get("assets")
    if not isinstance(assets, dict):
        unknowns.append("AUDITOR_ASSET_EVIDENCE_MISSING")
        return _finish_check(conflicts, unknowns, before_conflicts, before_unknowns)

    asset_ids = set(assets)
    required_set = set(required_ids)
    if required_set - asset_ids:
        conflicts.append("AUDITOR_REQUIRED_ASSET_MISSING")
    if asset_ids - required_set:
        conflicts.append("AUDITOR_UNEXPECTED_ASSET")

    for asset_id in required_ids:
        row = assets.get(asset_id)
        if not isinstance(row, dict):
            continue
        expected_ref = approved_outputs.get(asset_id, {}).get("output_ref")
        evidence_ref = row.get("output_ref")
        if evidence_ref is None:
            unknowns.append("AUDITOR_OUTPUT_REF_UNVERIFIED")
        elif evidence_ref != expected_ref:
            conflicts.append("AUDITOR_OUTPUT_REF_MISMATCH")

        sha = row.get("physical_sha256")
        if sha is None:
            unknowns.append("PHYSICAL_SHA256_UNVERIFIED")
        elif not isinstance(sha, str) or not HEX64.fullmatch(sha):
            conflicts.append("PHYSICAL_SHA256_INVALID")

        status = row.get("effective_status")
        if status in FINAL_CONSUMABLE_EVIDENCE:
            pass
        elif status in EVIDENCE_FAIL:
            conflicts.append("ASSET_EVIDENCE_INVALIDATED")
        else:
            unknowns.append("ASSET_SEMANTIC_EVIDENCE_UNVERIFIED")

    return _finish_check(conflicts, unknowns, before_conflicts, before_unknowns)


def _simulator_binding_check(
    packet: dict[str, Any],
    required_ids: list[str],
    approved_outputs: dict[str, dict[str, str]],
    conflicts: list[str],
    unknowns: list[str],
) -> tuple[str, bool]:
    before_conflicts = len(conflicts)
    before_unknowns = len(unknowns)
    manifest = packet.get("simulator_manifest")
    if manifest is None:
        unknowns.append("SIMULATOR_MANIFEST_MISSING")
        return "UNVERIFIED", False
    if not isinstance(manifest, dict):
        conflicts.append("SIMULATOR_MANIFEST_MALFORMED")
        return "FAIL", False

    review_eligible = True
    bindings = manifest.get("bindings")
    if not isinstance(bindings, list):
        conflicts.append("SIMULATOR_BINDINGS_INVALID")
        bindings = []

    bound_ids: set[str] = set()
    for row in bindings:
        if not isinstance(row, dict):
            conflicts.append("SIMULATOR_BINDING_ROW_INVALID")
            continue
        asset_id = row.get("asset_id")
        output_ref = row.get("output_ref")
        slot_id = row.get("slot_id")
        if not isinstance(asset_id, str) or not asset_id:
            conflicts.append("SIMULATOR_BINDING_ASSET_ID_INVALID")
            continue
        if not isinstance(slot_id, str) or not slot_id:
            conflicts.append("SIMULATOR_BINDING_SLOT_ID_INVALID")
        bound_ids.add(asset_id)
        if asset_id not in set(required_ids):
            conflicts.append("UNEXPECTED_BINDING")
            continue
        expected_ref = approved_outputs.get(asset_id, {}).get("output_ref")
        if output_ref != expected_ref:
            conflicts.append("APPROVED_OUTPUT_BINDING_MISMATCH")

    missing = set(required_ids) - bound_ids
    if missing:
        conflicts.append("MISSING_REQUIRED_BINDING")

    pending = manifest.get("pending_assets")
    if not isinstance(pending, list):
        conflicts.append("PENDING_ASSETS_INVALID")
    elif pending:
        conflicts.append("PENDING_ASSETS")

    eligibility = manifest.get("eligibility")
    if not isinstance(eligibility, dict):
        unknowns.append("SIMULATOR_ELIGIBILITY_MISSING")
    else:
        for key in (
            "production_freeze_ready",
            "required_asset_set_complete",
            "approved_output_matches",
            "asset_binding_complete",
        ):
            if eligibility.get(key) is not True:
                conflicts.append(f"SIMULATOR_{key.upper()}_NOT_READY")
        declared_conflicts = eligibility.get("blocking_conflicts")
        if not isinstance(declared_conflicts, list):
            conflicts.append("SIMULATOR_BLOCKING_CONFLICTS_INVALID")
        elif declared_conflicts:
            conflicts.append("SIMULATOR_BLOCKING_CONFLICTS")
        # hard_verification_status is intentionally not trusted here. M4 recomputes it.

    return _finish_check(conflicts, unknowns, before_conflicts, before_unknowns), review_eligible


def _final_runtime_check(packet: dict[str, Any], conflicts: list[str], unknowns: list[str]) -> str:
    before_conflicts = len(conflicts)
    before_unknowns = len(unknowns)
    artifact = packet.get("final_artifact")
    runtime = packet.get("runtime_evidence")
    if artifact is None or runtime is None:
        unknowns.append("FINAL_RUNTIME_EVIDENCE_MISSING")
        return "UNVERIFIED"
    if not isinstance(artifact, dict) or not isinstance(runtime, dict):
        conflicts.append("FINAL_RUNTIME_EVIDENCE_MALFORMED")
        return "FAIL"

    path = artifact.get("path")
    if not isinstance(path, str) or not path or not path.casefold().endswith(".html"):
        conflicts.append("FINAL_ARTIFACT_PATH_INVALID")
    sha = artifact.get("sha256")
    if sha is None:
        unknowns.append("FINAL_ARTIFACT_SHA256_MISSING")
    elif not isinstance(sha, str) or not HEX64.fullmatch(sha):
        conflicts.append("FINAL_ARTIFACT_SHA256_INVALID")

    runtime_sha = runtime.get("artifact_sha256")
    if isinstance(sha, str) and HEX64.fullmatch(sha) and runtime_sha != sha:
        conflicts.append("FINAL_ARTIFACT_HASH_MISMATCH")
    if runtime.get("validator") != "browser-runtime":
        unknowns.append("BROWSER_RUNTIME_VALIDATION_UNVERIFIED")
    if runtime.get("offline") is not True:
        conflicts.append("FINAL_ARTIFACT_NOT_OFFLINE")
    if runtime.get("network_requests") != 0:
        conflicts.append("FINAL_ARTIFACT_NETWORK_DEPENDENCY")
    if runtime.get("external_resource_dependencies") != 0:
        conflicts.append("FINAL_ARTIFACT_EXTERNAL_DEPENDENCY")

    viewports = runtime.get("viewports")
    if not isinstance(viewports, dict):
        unknowns.append("MOBILE_RUNTIME_VIEWPORTS_MISSING")
    else:
        for width in REQUIRED_MOBILE_WIDTHS:
            row = viewports.get(width)
            if row is None:
                unknowns.append(f"MOBILE_RUNTIME_{width}_MISSING")
                continue
            if not isinstance(row, dict):
                conflicts.append(f"MOBILE_RUNTIME_{width}_INVALID")
                continue
            if row.get("horizontal_overflow") is not False:
                conflicts.append(f"MOBILE_RUNTIME_{width}_OVERFLOW")
            if row.get("broken_images") != 0:
                conflicts.append(f"MOBILE_RUNTIME_{width}_BROKEN_IMAGES")

    return _finish_check(conflicts, unknowns, before_conflicts, before_unknowns)


def evaluate_final_eligibility(packet: Any) -> dict[str, Any]:
    """Recompute final eligibility without trusting caller-authored PASS flags."""
    if not isinstance(packet, dict):
        return {
            "schema_version": "1.0",
            "hard_verification_status": "FAIL",
            "review_eligible": False,
            "final_eligible": False,
            "checks": {name: "FAIL" if name == "production_freeze" else "N/A" for name in CHECK_NAMES},
            "blocking_conflicts": ["FINAL_ELIGIBILITY_PACKET_INVALID"],
            "unverified_reasons": [],
        }

    conflicts: list[str] = []
    unknowns: list[str] = []
    checks: dict[str, str] = {}

    freeze_status, required_ids, approved_outputs = _production_freeze_check(packet, conflicts, unknowns)
    checks["production_freeze"] = freeze_status
    checks["exact_asset_evidence"] = _asset_evidence_check(
        packet, required_ids, approved_outputs, conflicts, unknowns
    )
    simulator_status, review_eligible = _simulator_binding_check(
        packet, required_ids, approved_outputs, conflicts, unknowns
    )
    checks["simulator_binding"] = simulator_status
    checks["final_runtime"] = _final_runtime_check(packet, conflicts, unknowns)

    if "FAIL" in checks.values():
        hard_status = "FAIL"
    elif "UNVERIFIED" in checks.values():
        hard_status = "UNVERIFIED"
    else:
        hard_status = "PASS"

    return {
        "schema_version": "1.0",
        "hard_verification_status": hard_status,
        "review_eligible": bool(review_eligible),
        "final_eligible": hard_status == "PASS",
        "checks": checks,
        "blocking_conflicts": list(dict.fromkeys(conflicts)),
        "unverified_reasons": list(dict.fromkeys(unknowns)),
    }


def apply_hard_verification(manifest: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the Simulator manifest carrying the recomputed M4 status."""
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    if not isinstance(result, dict) or result.get("hard_verification_status") not in {"PASS", "UNVERIFIED", "FAIL"}:
        raise ValueError("result must be an evidence-hardening result")
    updated = deepcopy(manifest)
    eligibility = updated.setdefault("eligibility", {})
    if not isinstance(eligibility, dict):
        raise ValueError("manifest eligibility must be an object")
    eligibility["hard_verification_status"] = result["hard_verification_status"]
    existing = eligibility.get("blocking_conflicts")
    if not isinstance(existing, list):
        existing = []
    eligibility["blocking_conflicts"] = list(dict.fromkeys(
        [item for item in existing if isinstance(item, str) and item]
        + [item for item in result.get("blocking_conflicts", []) if isinstance(item, str) and item]
    ))
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="Stage 10 evidence packet JSON")
    parser.add_argument("--json", action="store_true", help="print JSON result")
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result = evaluate_final_eligibility(None)
        result["blocking_conflicts"] = [f"FINAL_ELIGIBILITY_PACKET_READ_ERROR:{exc}"]
    else:
        result = evaluate_final_eligibility(packet)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(result["hard_verification_status"])
        for code in result["blocking_conflicts"]:
            print(f"FAIL: {code}")
        for code in result["unverified_reasons"]:
            print(f"UNVERIFIED: {code}")
    if result["hard_verification_status"] == "PASS":
        return 0
    if result["hard_verification_status"] == "UNVERIFIED":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
