#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from variation_resolver import resolve_variation  # noqa: E402


def test_gallery_variation_overrides_by_slot_id():
    parent = {"gallery": {"gallery-1": "G1", "gallery-2": "G2"}}
    child = {"variation_id": "black", "gallery": {"gallery-2": "G2-BLACK"}}
    resolved = resolve_variation(parent, child)
    assert resolved["gallery"] == {"gallery-1": "G1", "gallery-2": "G2-BLACK"}


def test_specifications_merge_by_spec_key():
    parent = {"specifications": {"size": "10", "weight": "2"}}
    child = {"specifications": {"weight": "3", "color": "black"}}
    assert resolve_variation(parent, child)["specifications"] == {"size": "10", "weight": "3", "color": "black"}


def test_content_assets_merge_by_content_module_slot_key():
    parent = {
        "content_assets": [
            {"content_id": "premium-a", "module_id": "hero", "slot_key": "image", "asset_id": "A1"},
            {"content_id": "premium-a", "module_id": "hero", "slot_key": "headline", "value": "Parent"},
        ]
    }
    child = {
        "variation_id": "black",
        "content_assets": [
            {"content_id": "premium-a", "module_id": "hero", "slot_key": "image", "asset_id": "A1-BLACK"}
        ],
    }
    resolved = resolve_variation(parent, child)
    indexed = {(x["content_id"], x["module_id"], x["slot_key"]): x for x in resolved["content_assets"]}
    assert indexed[("premium-a", "hero", "image")]["asset_id"] == "A1-BLACK"
    assert indexed[("premium-a", "hero", "headline")]["value"] == "Parent"


def test_absent_field_inherits_but_explicit_null_disables():
    parent = {"brand_content_id": "brand-a", "enhanced_description_id": "premium-a"}
    assert resolve_variation(parent, {})["brand_content_id"] == "brand-a"
    assert resolve_variation(parent, {"brand_content_id": None})["brand_content_id"] is None


def test_offer_dict_inherits_and_overrides_fields():
    parent = {"offer": {"price": "12980", "stock": "in-stock", "coupon": None}}
    child = {"offer": {"price": "13980"}}
    assert resolve_variation(parent, child)["offer"] == {"price": "13980", "stock": "in-stock", "coupon": None}


def test_content_collection_is_not_merged_by_list_index():
    parent = {"content_assets": [{"content_id": "x", "module_id": "m1", "slot_key": "image", "asset_id": "A1"}]}
    child = {"content_assets": [{"content_id": "x", "module_id": "m2", "slot_key": "image", "asset_id": "A2"}]}
    result = resolve_variation(parent, child)["content_assets"]
    assert len(result) == 2


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"variation resolver selftest: PASS ({len(tests)} tests)")
