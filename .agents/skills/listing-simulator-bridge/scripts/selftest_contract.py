#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

from validate_contract import (  # noqa: E402
    validate_active_selection,
    validate_asset_slot_contract,
    validate_binding,
    validate_manifest,
    validate_template_binding,
)


def valid_binding(**overrides):
    row = {
        "asset_id": "G1",
        "slot_id": "gallery-1",
        "output_ref": "outputs/gallery/g1.png",
        "variation_id": None,
    }
    row.update(overrides)
    return row


def test_binding_requires_project_relative_output_ref():
    assert "output_ref must be project-root-relative" in validate_binding(
        valid_binding(output_ref="/" + "Users/example/project/g1.png")
    )
    assert "output_ref must be project-root-relative" in validate_binding(
        valid_binding(output_ref="../outside.png")
    )
    assert not validate_binding(valid_binding())


def test_content_slot_must_match_explicit_content_coordinates():
    binding = valid_binding(
        asset_id="A1",
        slot_id="content:premium-a:module:hero-01:slot:image",
        output_ref="outputs/a-plus/a1.png",
        content_id="premium-a",
        module_id="hero-01",
        template_id="synthetic-premium-hero",
        slot_key="image",
    )
    assert not validate_binding(binding)
    bad = dict(binding, slot_id="content:premium-a:module:hero-01:slot:body")
    assert "content slot_id does not match content_id/module_id/slot_key" in validate_binding(bad)


def test_slot_taxonomy_contains_stable_gallery_detail_and_pattern():
    taxonomy = json.loads((ROOT / "profiles/amazon-jp/slot-taxonomy.json").read_text(encoding="utf-8"))
    assert taxonomy["gallery"] == [
        "gallery-1", "gallery-2", "gallery-3", "gallery-4", "gallery-5", "gallery-6",
        "gallery-video-1", "gallery-video-poster-1",
    ]
    assert taxonomy["detail"] == ["detail-gallery-1", "detail-gallery-2", "detail-video-1", "product-document-1"]
    assert taxonomy["content_slot_pattern"] == "content:{content_id}:module:{module_id}:slot:{slot_key}"


def test_template_binding_uses_registry_and_rejects_unknown_slot():
    registry = {
        "templates": [{
            "template_id": "synthetic-premium-hero",
            "content_type": "premium-a-plus",
            "slot_keys": ["image", "headline", "body"],
            "supported_media_types": ["image"],
        }]
    }
    binding = valid_binding(
        asset_id="A1",
        slot_id="content:premium-a:module:hero-01:slot:image",
        output_ref="outputs/a-plus/a1.png",
        content_id="premium-a",
        module_id="hero-01",
        template_id="synthetic-premium-hero",
        slot_key="image",
    )
    assert not validate_template_binding(binding, registry)
    assert "slot_key is not supported by template_id" in validate_template_binding(dict(binding, slot_key="hotspot", slot_id="content:premium-a:module:hero-01:slot:hotspot"), registry)
    assert "template_id not found in registry" in validate_template_binding(dict(binding, template_id="unknown"), registry)


def test_active_selection_rejects_basic_plus_premium_and_brand_plus_shoppable():
    contents = [
        {"content_id": "basic-a", "content_type": "basic-a-plus"},
        {"content_id": "premium-a", "content_type": "premium-a-plus"},
        {"content_id": "brand-a", "content_type": "brand-story"},
        {"content_id": "shop-a", "content_type": "shoppable-collections"},
    ]
    assert not validate_active_selection(
        {"enhanced_description_id": "premium-a", "brand_content_id": "brand-a"}, contents
    )
    assert "Basic A+ and Premium A+ cannot both be active" in validate_active_selection(
        {"basic_a_plus_id": "basic-a", "premium_a_plus_id": "premium-a"}, contents
    )
    assert "Brand Story and Shoppable Collections cannot both be active" in validate_active_selection(
        {"brand_story_id": "brand-a", "shoppable_collections_id": "shop-a"}, contents
    )


def test_unknown_non_template_slot_is_rejected():
    errors = validate_binding(valid_binding(slot_id="gallery-99"))
    assert "slot_id is not in Amazon Japan stable taxonomy" in errors


def test_manifest_binding_variation_must_exist_in_listing_family():
    manifest = {
        "schema_version": "1.0",
        "project": {"market": "JP", "channel": "amazon-jp", "locale": "ja-JP"},
        "contents": [],
        "active_selection": {"enhanced_description_id": None, "brand_content_id": None},
        "bindings": [valid_binding(variation_id="black")],
        "listing_family": {"parent": {"listing_id": "parent"}, "variations": []},
        "eligibility": {
            "production_freeze_ready": False,
            "required_asset_set_complete": False,
            "approved_output_matches": False,
            "asset_binding_complete": True,
            "blocking_conflicts": [],
            "hard_verification_status": "UNVERIFIED",
        },
    }
    assert "binding variation_id is not declared in listing_family" in validate_manifest(manifest)


def test_machine_readable_contracts_and_examples_are_consistent():
    binding_schema = json.loads((ROOT / "contracts/asset-binding.schema.json").read_text(encoding="utf-8"))
    manifest_schema = json.loads((ROOT / "contracts/simulator-manifest.schema.json").read_text(encoding="utf-8"))
    assert binding_schema["required"] == ["asset_id", "slot_id", "output_ref"]
    assert set(manifest_schema["required"]) >= {"schema_version", "project", "bindings", "active_selection", "eligibility"}

    slot_contract = json.loads((ROOT / ".agents/skills/listing-simulator-bridge/templates/asset-slot-contract.example.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / ".agents/skills/listing-simulator-bridge/templates/listing-simulator-manifest.example.json").read_text(encoding="utf-8"))
    assert not validate_asset_slot_contract(slot_contract)
    assert not validate_manifest(manifest)


def test_manifest_requires_explicit_bindings_and_valid_active_selection():
    manifest = {
        "schema_version": "1.0",
        "project": {"market": "JP", "channel": "amazon-jp", "locale": "ja-JP"},
        "contents": [{"content_id": "premium-a", "content_type": "premium-a-plus"}],
        "active_selection": {"enhanced_description_id": "premium-a", "brand_content_id": None},
        "bindings": [valid_binding()],
        "eligibility": {
            "production_freeze_ready": False,
            "required_asset_set_complete": False,
            "approved_output_matches": False,
            "asset_binding_complete": True,
            "blocking_conflicts": [],
            "hard_verification_status": "UNVERIFIED",
        },
    }
    assert not validate_manifest(manifest)
    broken = dict(manifest, bindings=[])
    assert "bindings must be a non-empty list" in validate_manifest(broken)


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"simulator contract selftest: PASS ({len(tests)} tests)")
