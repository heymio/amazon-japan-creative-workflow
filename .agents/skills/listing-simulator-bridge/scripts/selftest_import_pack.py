#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

from build_import_pack import (  # noqa: E402
    build_import_model,
    build_pack_entries,
    derive_eligibility,
    write_import_folder,
    write_import_zip,
)


def test_unbound_media_becomes_pending_without_filename_guess():
    result = build_import_model(
        media=["outputs/gallery/black-gallery-2.png"],
        bindings=[],
    )
    pending = result["pending_assets"]
    assert len(pending) == 1
    assert pending[0]["output_ref"] == "outputs/gallery/black-gallery-2.png"
    assert pending[0].get("slot_id") is None
    assert pending[0].get("variation_id") is None


def test_eligibility_never_upgrades_hard_verification():
    source = {
        "production_freeze_ready": True,
        "required_asset_set_complete": True,
        "approved_output_matches": True,
        "asset_binding_complete": True,
        "blocking_conflicts": [],
        "hard_verification_status": "UNVERIFIED",
    }
    assert derive_eligibility(source)["hard_verification_status"] == "UNVERIFIED"
    source["hard_verification_status"] = "PASS"
    assert derive_eligibility(source)["hard_verification_status"] == "PASS"


def test_pack_marks_binding_incomplete_when_media_is_pending():
    root = ROOT / "fixtures/simulator-import/gallery-a-plus"
    entries = build_pack_entries(root)
    manifest = json.loads(entries["listing-simulator-manifest.json"].decode("utf-8"))
    assert manifest["pending_assets"]
    assert manifest["eligibility"]["asset_binding_complete"] is False


def test_folder_and_zip_are_logically_identical_and_deterministic():
    source = ROOT / "fixtures/simulator-import/parent-only"
    entries = build_pack_entries(source)
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        folder = tmp / "folder"
        zip_a = tmp / "pack-a.zip"
        zip_b = tmp / "pack-b.zip"
        write_import_folder(entries, folder)
        write_import_zip(entries, zip_a)
        write_import_zip(entries, zip_b)
        assert hashlib.sha256(zip_a.read_bytes()).hexdigest() == hashlib.sha256(zip_b.read_bytes()).hexdigest()
        with zipfile.ZipFile(zip_a) as archive:
            zipped = {name: archive.read(name) for name in archive.namelist()}
        folder_data = {
            path.relative_to(folder).as_posix(): path.read_bytes()
            for path in sorted(folder.rglob("*")) if path.is_file()
        }
        assert zipped == folder_data == entries


def test_synthetic_png_media_have_real_png_signature():
    for fixture in ("parent-only", "variation", "gallery-a-plus"):
        for path in sorted((ROOT / "fixtures/simulator-import" / fixture / "outputs").rglob("*.png")):
            assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), path


def test_synthetic_registry_is_explicit_and_covers_four_content_families():
    registry = json.loads((HERE.parent / "templates/template-registry.synthetic.json").read_text(encoding="utf-8"))
    assert registry["synthetic"] is True
    families = {row["content_type"] for row in registry["templates"]}
    assert families == {"basic-a-plus", "premium-a-plus", "brand-story", "shoppable-collections"}
    for row in registry["templates"]:
        assert row["template_id"].startswith("synthetic-")
        assert row["slot_keys"]
        assert row["supported_media_types"]


def test_all_three_public_import_fixtures_build():
    for name in ("parent-only", "variation", "gallery-a-plus"):
        entries = build_pack_entries(ROOT / "fixtures/simulator-import" / name)
        assert "listing-simulator-manifest.json" in entries
        assert "asset-slot-contract.json" in entries


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"simulator import-pack selftest: PASS ({len(tests)} tests)")
