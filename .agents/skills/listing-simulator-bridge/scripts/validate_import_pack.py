#!/usr/bin/env python3
"""Validate a built Simulator import folder or ZIP without rendering it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile

from security import validate_project_relative_path, validate_source_tree, validate_zip_archive
from validate_contract import validate_asset_slot_contract, validate_manifest


def _validate_entries(entries: dict[str, bytes]) -> list[str]:
    errors: list[str] = []
    for required in ("listing-simulator-manifest.json", "asset-slot-contract.json"):
        if required not in entries:
            errors.append(f"missing {required}")
    if errors:
        return errors
    try:
        manifest = json.loads(entries["listing-simulator-manifest.json"].decode("utf-8"))
        contract = json.loads(entries["asset-slot-contract.json"].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"invalid contract JSON: {exc}"]
    errors.extend(validate_asset_slot_contract(contract))
    errors.extend(validate_manifest(manifest))
    if isinstance(contract, dict) and isinstance(manifest, dict) and manifest.get("bindings") != contract.get("bindings"):
        errors.append("manifest bindings must exactly match asset-slot contract bindings")
    names = set(entries)
    for binding in contract.get("bindings", []) if isinstance(contract, dict) else []:
        if isinstance(binding, dict):
            try:
                output_ref = validate_project_relative_path(binding.get("output_ref", ""))
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if output_ref not in names:
                errors.append(f"binding references missing media: {output_ref}")
    return errors


def validate_import_pack(path: Path) -> list[str]:
    path = Path(path)
    if path.is_dir():
        files = validate_source_tree(path)
        return _validate_entries({name: file.read_bytes() for name, file in files})
    validate_zip_archive(path)
    with ZipFile(path) as archive:
        entries = {
            validate_project_relative_path(info.filename): archive.read(info)
            for info in archive.infolist() if not info.is_dir()
        }
    return _validate_entries(entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors = validate_import_pack(args.path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Simulator import pack validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
