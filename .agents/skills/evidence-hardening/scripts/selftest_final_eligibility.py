#!/usr/bin/env python3
"""M4 contract tests for fail-closed final evidence eligibility."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "final_eligibility.py"


def load_module():
    spec = importlib.util.spec_from_file_location("evidence_hardening_final_eligibility", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_packet() -> dict:
    outputs = {
        "A01": {"candidate_id": "A01-v1", "output_ref": "outputs/gallery/a01.png"},
        "A02": {"candidate_id": "A02-v1", "output_ref": "outputs/aplus/a02.png"},
    }
    return {
        "production_freeze": {
            "expected_assets": 2,
            "required_asset_ids": ["A01", "A02"],
            "user_approved_assets": ["A01", "A02"],
            "blocked_assets": [],
            "revision_pending": [],
            "approved_outputs": outputs,
            "set_qa_status": "CLEAR",
            "ready_for_hardening": True,
        },
        "auditor_evidence": {
            "checkpoint": "final",
            "asset_set_gate": {"status": "PASS", "messages": []},
            "assets": {
                "A01": {
                    "output_ref": "outputs/gallery/a01.png",
                    "physical_sha256": "a" * 64,
                    "effective_status": "VERIFIED",
                },
                "A02": {
                    "output_ref": "outputs/aplus/a02.png",
                    "physical_sha256": "b" * 64,
                    "effective_status": "HUMAN_APPROVED",
                },
            },
        },
        "simulator_manifest": {
            "bindings": [
                {"asset_id": "A01", "slot_id": "gallery-1", "output_ref": "outputs/gallery/a01.png", "variation_id": None},
                {"asset_id": "A02", "slot_id": "content:premium-a:module:hero:slot:image", "output_ref": "outputs/aplus/a02.png", "variation_id": None},
            ],
            "pending_assets": [],
            "eligibility": {
                "production_freeze_ready": True,
                "required_asset_set_complete": True,
                "approved_output_matches": True,
                "asset_binding_complete": True,
                "blocking_conflicts": [],
                "hard_verification_status": "PASS",
            },
        },
        "final_artifact": {
            "path": "exports/final.html",
            "sha256": "f" * 64,
        },
        "runtime_evidence": {
            "validator": "browser-runtime",
            "artifact_sha256": "f" * 64,
            "offline": True,
            "network_requests": 0,
            "external_resource_dependencies": 0,
            "viewports": {
                "375": {"horizontal_overflow": False, "broken_images": 0},
                "390": {"horizontal_overflow": False, "broken_images": 0},
                "430": {"horizontal_overflow": False, "broken_images": 0},
            },
        },
    }


def test_complete_exact_packet_passes_final_eligibility() -> None:
    module = load_module()
    result = module.evaluate_final_eligibility(valid_packet())
    assert result["hard_verification_status"] == "PASS", result
    assert result["final_eligible"] is True
    assert result["review_eligible"] is True
    assert result["blocking_conflicts"] == []


def test_manifest_self_declared_pass_cannot_override_binding_mismatch() -> None:
    module = load_module()
    packet = valid_packet()
    packet["simulator_manifest"]["bindings"][0]["output_ref"] = "outputs/gallery/wrong.png"
    result = module.evaluate_final_eligibility(packet)
    assert result["hard_verification_status"] == "FAIL"
    assert result["final_eligible"] is False
    assert "APPROVED_OUTPUT_BINDING_MISMATCH" in result["blocking_conflicts"]


def test_pending_asset_blocks_final_but_review_remains_available() -> None:
    module = load_module()
    packet = valid_packet()
    packet["simulator_manifest"]["pending_assets"] = [{"output_ref": "outputs/gallery/unbound.png"}]
    result = module.evaluate_final_eligibility(packet)
    assert result["hard_verification_status"] == "FAIL"
    assert result["final_eligible"] is False
    assert result["review_eligible"] is True
    assert "PENDING_ASSETS" in result["blocking_conflicts"]


def test_semantic_evidence_gap_is_unverified_not_false_pass() -> None:
    module = load_module()
    packet = valid_packet()
    packet["auditor_evidence"]["assets"]["A02"]["effective_status"] = "HUMAN_REVIEW_REQUIRED"
    result = module.evaluate_final_eligibility(packet)
    assert result["hard_verification_status"] == "UNVERIFIED"
    assert result["final_eligible"] is False
    assert result["checks"]["exact_asset_evidence"] == "UNVERIFIED"


def test_runtime_evidence_must_bind_exact_final_html_hash() -> None:
    module = load_module()
    packet = valid_packet()
    packet["runtime_evidence"]["artifact_sha256"] = "e" * 64
    result = module.evaluate_final_eligibility(packet)
    assert result["hard_verification_status"] == "FAIL"
    assert result["checks"]["final_runtime"] == "FAIL"
    assert "FINAL_ARTIFACT_HASH_MISMATCH" in result["blocking_conflicts"]


def test_mobile_runtime_requires_all_supported_m_first_widths() -> None:
    module = load_module()
    packet = valid_packet()
    packet["runtime_evidence"]["viewports"].pop("430")
    result = module.evaluate_final_eligibility(packet)
    assert result["hard_verification_status"] == "UNVERIFIED"
    assert result["checks"]["final_runtime"] == "UNVERIFIED"
    assert result["final_eligible"] is False


def test_freeze_required_asset_set_cannot_be_shrunk_by_manifest() -> None:
    module = load_module()
    packet = valid_packet()
    packet["simulator_manifest"]["bindings"] = packet["simulator_manifest"]["bindings"][:1]
    result = module.evaluate_final_eligibility(packet)
    assert result["hard_verification_status"] == "FAIL"
    assert "MISSING_REQUIRED_BINDING" in result["blocking_conflicts"]


def main() -> int:
    tests = [(name, value) for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for name, test in sorted(tests):
        test()
    print(f"PASS: {len(tests)} evidence-hardening final eligibility tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
