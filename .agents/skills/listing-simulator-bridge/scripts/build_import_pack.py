#!/usr/bin/env python3
"""Build deterministic Amazon Japan Listing Simulator folder/ZIP import packs."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from package_common import write_deterministic_zip  # noqa: E402
from security import validate_project_relative_path, validate_source_tree, validate_zip_archive  # noqa: E402
from validate_contract import validate_asset_slot_contract, validate_manifest  # noqa: E402

SUPPORTED_MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm", ".pdf"}
ELIGIBILITY_FIELDS = (
    "production_freeze_ready",
    "required_asset_set_complete",
    "approved_output_matches",
    "asset_binding_complete",
    "blocking_conflicts",
    "hard_verification_status",
)


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def derive_eligibility(source: dict, *, asset_binding_complete: bool | None = None) -> dict:
    source = source if isinstance(source, dict) else {}
    hard_status = source.get("hard_verification_status")
    if hard_status == "PASS":
        normalized_hard = "PASS"
    elif hard_status == "FAIL":
        normalized_hard = "FAIL"
    else:
        normalized_hard = "UNVERIFIED"
    conflicts = source.get("blocking_conflicts")
    if not isinstance(conflicts, list):
        conflicts = []
    result = {
        "production_freeze_ready": source.get("production_freeze_ready") is True,
        "required_asset_set_complete": source.get("required_asset_set_complete") is True,
        "approved_output_matches": source.get("approved_output_matches") is True,
        "asset_binding_complete": source.get("asset_binding_complete") is True,
        "blocking_conflicts": [item for item in conflicts if isinstance(item, str) and item],
        "hard_verification_status": normalized_hard,
    }
    if asset_binding_complete is not None:
        result["asset_binding_complete"] = bool(asset_binding_complete)
    return result


def build_import_model(media: list[str], bindings: list[dict]) -> dict:
    normalized_media: list[str] = []
    for output_ref in media:
        normalized_media.append(validate_project_relative_path(output_ref))
    media_set = set(normalized_media)

    bound_assets: list[dict] = []
    bound_refs: set[str] = set()
    missing_bound_media: list[str] = []
    for binding in bindings if isinstance(bindings, list) else []:
        if not isinstance(binding, dict):
            continue
        output_ref = validate_project_relative_path(binding.get("output_ref", ""))
        bound_refs.add(output_ref)
        if output_ref not in media_set:
            missing_bound_media.append(output_ref)
        bound_assets.append(deepcopy(binding))

    pending_assets = [
        {"output_ref": output_ref, "asset_id": None, "slot_id": None, "variation_id": None}
        for output_ref in normalized_media
        if output_ref not in bound_refs
    ]
    return {
        "bound_assets": bound_assets,
        "pending_assets": pending_assets,
        "missing_bound_media": sorted(set(missing_bound_media)),
    }


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON file: {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path.name}")
    return value


def build_pack_entries(source_root: Path) -> dict[str, bytes]:
    source_root = Path(source_root)
    source_files = validate_source_tree(source_root)
    by_name = {name: path for name, path in source_files}
    for required in ("listing-simulator-manifest.json", "asset-slot-contract.json"):
        if required not in by_name:
            raise ValueError(f"missing required Simulator pack contract: {required}")

    manifest = _load_json(by_name["listing-simulator-manifest.json"])
    slot_contract = _load_json(by_name["asset-slot-contract.json"])
    contract_errors = validate_asset_slot_contract(slot_contract)
    if contract_errors:
        raise ValueError("invalid asset-slot contract: " + "; ".join(contract_errors))
    manifest_errors = validate_manifest(manifest)
    if manifest_errors:
        raise ValueError("invalid Simulator manifest: " + "; ".join(manifest_errors))

    bindings = slot_contract["bindings"]
    if manifest.get("bindings") != bindings:
        raise ValueError("manifest bindings must exactly match asset-slot contract bindings")

    media = [
        name for name, _ in source_files
        if PurePosixPath(name).suffix.casefold() in SUPPORTED_MEDIA_SUFFIXES
    ]
    model = build_import_model(media, bindings)
    if model["missing_bound_media"]:
        raise ValueError("binding references missing media: " + ",".join(model["missing_bound_media"]))

    derived = deepcopy(manifest)
    derived["bindings"] = deepcopy(bindings)
    derived["pending_assets"] = model["pending_assets"]
    derived["eligibility"] = derive_eligibility(
        manifest.get("eligibility", {}),
        asset_binding_complete=not model["pending_assets"] and not model["missing_bound_media"],
    )
    final_errors = validate_manifest(derived)
    if final_errors:
        raise ValueError("derived Simulator manifest is invalid: " + "; ".join(final_errors))

    entries: dict[str, bytes] = {}
    for name, path in source_files:
        if name == "listing-simulator-manifest.json":
            entries[name] = _canonical_json(derived)
        elif name == "asset-slot-contract.json":
            entries[name] = _canonical_json(slot_contract)
        else:
            entries[name] = path.read_bytes()
    return dict(sorted(entries.items()))


def write_import_folder(entries: dict[str, bytes], target: Path) -> None:
    target = Path(target)
    if target.exists():
        if target.is_symlink():
            raise ValueError(f"target folder cannot be a symlink: {target}")
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=False)
    for name, data in sorted(entries.items()):
        normalized = validate_project_relative_path(name)
        path = target / PurePosixPath(normalized)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    validate_source_tree(target)


def write_import_zip(entries: dict[str, bytes], target: Path) -> None:
    safe_entries: list[tuple[str, bytes]] = []
    for name, data in sorted(entries.items()):
        normalized = validate_project_relative_path(name)
        if PurePosixPath(normalized).suffix.casefold() in {".js", ".mjs", ".cjs"}:
            raise ValueError(f"executable JavaScript is not allowed in Simulator pack: {normalized}")
        if PurePosixPath(normalized).name.casefold() in {".env", ".env.local"}:
            raise ValueError(f"forbidden environment file: {normalized}")
        safe_entries.append((normalized, data))
    write_deterministic_zip(Path(target), safe_entries)
    validate_zip_archive(Path(target))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    entries = build_pack_entries(args.source_root)
    if args.output.suffix.casefold() == ".zip":
        write_import_zip(entries, args.output)
    else:
        write_import_folder(entries, args.output)
    print(f"Simulator import pack: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
