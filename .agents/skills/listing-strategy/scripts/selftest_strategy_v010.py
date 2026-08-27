#!/usr/bin/env python3
"""v0.1 strategy-contract regressions for Amazon Japan Creative Workflow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[2]
SCRIPT_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_strategy_contracts import (  # noqa: E402
    CREATIVE_ROLES,
    validate_creative_strategy,
    validate_production_handoff,
    validate_project_brief,
)


def legacy_v033_handoff() -> str:
    return """production_handoff:
  project:
    market: JP
    channel: amazon-jp
    locale: ja-JP
    product: Example Product
  page_plan:
    gallery:
      - G1
      - G2
    enhanced_content:
      - A1
    other_required_regions: []
  asset_set:
    - asset_id: G1
      role: gallery-native
      slot: G1
      primary_message: Core positioning
      evidence_mode: SOURCE_FAITHFUL
      status: READY
    - asset_id: G2
      role: gallery-native
      slot: G2
      primary_message: Primary proof
      evidence_mode: PROOF_VISUAL
      status: READY
    - asset_id: A1
      role: enhanced-content
      slot: A1
      primary_message: Lifestyle expansion
      evidence_mode: CREATIVE_MOCK
      status: READY
  source_assets:
    - source_id: SRC-P01
      role: real-product-source
      required_by:
        - G1
        - G2
        - A1
  product_invariants:
    - preserve exact product geometry
  creative_strategy_ref: creative-strategy.yaml
  global_visual_direction:
    - product-first commercial hierarchy
  visual_benchmark_refs:
    - BENCH-01
  prohibited:
    - unsupported claims
  blocked_assets: []
  page_visual_system:
    asset_directions:
      - asset_id: G1
        visual_role: hero-positioning
        scene_family: clean-product-stage
        composition_family: centered-hero
        tone: bright-neutral
        product_scale: large
        proof_form: source-faithful-product
      - asset_id: G2
        visual_role: mechanism-proof
        scene_family: technical-detail
        composition_family: close-up-explainer
        tone: neutral-technical
        product_scale: close-up
        proof_form: mechanism
      - asset_id: A1
        visual_role: lifestyle-use
        scene_family: realistic-home
        composition_family: wide-lifestyle
        tone: warm-natural
        product_scale: medium
        proof_form: lifestyle
"""


def v010_handoff(*, creative_role: str = "DIFFERENTIATOR_PROOF", variation_id: str | None = "black") -> str:
    variation_line = "      variation_id: null\n" if variation_id is None else f"      variation_id: {variation_id}\n"
    return f"""contract_version: \"1.0\"
production_handoff:
  project:
    market: JP
    channel: amazon-jp
    locale: ja-JP
    product: Example Product
  listing_family:
    parent_listing_id: parent
    variations:
      - variation_id: black
        label: ブラック
        attributes:
          color: ブラック
  page_plan:
    gallery:
      - G1
    enhanced_content: []
    other_required_regions: []
  asset_set:
    - asset_id: G1
      region: gallery
      slot: gallery-1
      shopper_task: Understand the primary purchase reason
      primary_message: Core differentiator
      user_value: See why the product matters in daily use
      usage_scene: Japanese residential entrance
      proof_object: Direct coverage relationship
      evidence_mode: PROOF_VISUAL
      creative_role: {creative_role}
      media_type: image
{variation_line}  source_assets:
    - source_id: SRC-P01
      role: real-product-source
      required_by:
        - G1
  product_invariants:
    - preserve exact product geometry
  creative_strategy_ref: creative-strategy.yaml
  global_visual_direction:
    - product-first commercial hierarchy
  visual_benchmark_refs: []
  prohibited:
    - unsupported claims
  blocked_assets: []
  page_visual_system:
    asset_directions:
      - asset_id: G1
        visual_role: differentiator-proof
        scene_family: realistic-home
        composition_family: proof-led
        tone: bright-neutral
        product_scale: large
        proof_form: direct-visual-proof
"""


def v010_project_brief(*, duplicate_variation: bool = False) -> str:
    second = ""
    if duplicate_variation:
        second = """    - variation_id: black
      label: ブラック duplicate
      attributes:
        color: ブラック
"""
    return f"""contract_version: \"1.0\"
project:
  id: strategy-v010
  market: JP
  locale: ja-JP
  channel: amazon-jp
  category: project-defined
  product: Example Product
  page_targets:
    - primary-listing
listing_family:
  parent_listing_id: parent
  variations:
    - variation_id: black
      label: ブラック
      attributes:
        color: ブラック
{second}offers:
  - id: single
    page_scope:
      - primary-listing
product_truth:
  confirmed:
    - id: FACT-001
      statement: Confirmed product capability
      source_ref: SRC-001
  conditional: []
  prohibited: []
claim_boundaries:
  consumer_ready:
    - FACT-001
  pending: []
  prohibited: []
consumer_evidence_sources: []
channel_reference:
  primary_reference: REF-001
  capability_status: PARTIAL
  frontend_visual_status: PARTIAL
open_business_decisions: []
"""



def v010_creative_strategy() -> str:
    return """contract_version: \"1.0\"
creative_strategy:
  target_user:
    - evidence-backed primary shopper segment
  core_tension: Primary shopper tension
  core_promise: Core consumer promise
  user_usage_understanding:
    - user: Primary shopper
      situation: Returning home while carrying items
      trigger: Entry action is needed
      friction: Hands are occupied
      desired_outcome: Complete the action with less interruption
      usage_scene: Japanese residential entrance
  primary_purchase_reasons:
    - id: P0-1
      reason: Primary reason to buy
  shopper_barriers: []
  reasons_to_believe:
    - id: RTB-1
      evidence_ref: FACT-001
      statement: Evidence-backed reason to believe
  message_priority:
    p0:
      - P0-1
    p1: []
    p2: []
  message_architecture:
    - message: Primary reason to buy
      user_value: Meaningful user outcome
      usage_scene: Japanese residential entrance
      proof_object: Direct visible evidence
      desired_takeaway: Clear reason to choose
      visualizable: true
      amazon_role: gallery
      priority: P0
  japan_implications:
    - implication: Evidence-backed Japan implication
      evidence_ref: MARKET-001
  proof_principles:
    - principle: Show proof directly
  visual_direction:
    - principle: Product-first hierarchy
  visual_anti_patterns:
    - pattern: Generic lifestyle without proof
"""


def test_v010_creative_strategy_requires_user_usage_model() -> None:
    text = v010_creative_strategy().replace("  user_usage_understanding:\n", "  user_usage_understanding_missing:\n", 1)
    errors = validate_creative_strategy(text)
    assert any("user_usage_understanding" in error for error in errors), errors


def test_v010_message_architecture_requires_proof_object() -> None:
    text = v010_creative_strategy().replace("      proof_object: Direct visible evidence\n", "", 1)
    errors = validate_creative_strategy(text)
    assert any("proof_object" in error for error in errors), errors


def test_v010_creative_strategy_accepts_complete_visualizable_mapping() -> None:
    assert validate_creative_strategy(v010_creative_strategy()) == []

def test_v033_production_handoff_remains_accepted() -> None:
    assert validate_production_handoff(legacy_v033_handoff()) == []


def test_exact_nine_creative_roles_are_exported() -> None:
    assert CREATIVE_ROLES == {
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


def test_new_asset_contract_rejects_unknown_creative_role() -> None:
    errors = validate_production_handoff(v010_handoff(creative_role="A_PLUS"))
    assert any("creative_role" in error for error in errors), errors


def test_new_asset_contract_requires_visualizable_shopper_fields() -> None:
    text = v010_handoff().replace("      shopper_task: Understand the primary purchase reason\n", "")
    text = text.replace("      user_value: See why the product matters in daily use\n", "")
    errors = validate_production_handoff(text)
    assert any("shopper_task" in error for error in errors), errors
    assert any("user_value" in error for error in errors), errors


def test_new_asset_contract_accepts_parent_asset_without_variation_id() -> None:
    assert validate_production_handoff(v010_handoff(variation_id=None)) == []


def test_asset_variation_id_must_reference_declared_variation() -> None:
    errors = validate_production_handoff(v010_handoff(variation_id="white"))
    assert any("variation_id" in error and "white" in error for error in errors), errors


def test_project_brief_rejects_duplicate_variation_ids() -> None:
    errors = validate_project_brief(v010_project_brief(duplicate_variation=True))
    assert any("duplicate" in error and "variation_id" in error for error in errors), errors


def test_public_contract_schemas_are_valid_json_and_forbid_fake_role_a_plus() -> None:
    for relative in ["contracts/creative-brief.schema.json", "contracts/strategy-output.schema.json"]:
        payload = json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))
        assert payload["$schema"].startswith("https://json-schema.org/")
    strategy_schema = json.loads((REPO_ROOT / "contracts/strategy-output.schema.json").read_text(encoding="utf-8"))
    roles = strategy_schema["$defs"]["asset"]["properties"]["creative_role"]["enum"]
    assert "A_PLUS" not in roles
    assert set(roles) == CREATIVE_ROLES


def test_public_role_profile_defines_all_nine_roles_without_private_examples() -> None:
    text = (REPO_ROOT / "profiles/amazon-jp/creative-roles.md").read_text(encoding="utf-8")
    for role in sorted(CREATIVE_ROLES):
        assert f"role: {role}" in text, role


def test_japan_localization_profile_covers_four_layers() -> None:
    text = (REPO_ROOT / "profiles/amazon-jp/localization.md").read_text(encoding="utf-8").casefold()
    for phrase in [
        "functional localization",
        "scene / behavior localization",
        "message / copy localization",
        "visual localization",
    ]:
        assert phrase in text, phrase


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} listing-strategy v0.1 contract tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
