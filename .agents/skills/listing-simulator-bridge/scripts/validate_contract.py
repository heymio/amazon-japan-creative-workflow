#!/usr/bin/env python3
"""Fail-closed contracts for Amazon Japan Listing Simulator interoperability."""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath

REQUIRED_BINDING_FIELDS = ("asset_id", "slot_id", "output_ref")
OPTIONAL_BINDING_FIELDS = ("variation_id", "content_id", "module_id", "template_id", "slot_key")
ELIGIBILITY_KEYS = {
    "production_freeze_ready",
    "required_asset_set_complete",
    "approved_output_matches",
    "asset_binding_complete",
    "blocking_conflicts",
    "hard_verification_status",
}
CONTENT_TYPES = {"basic-a-plus", "premium-a-plus", "brand-story", "shoppable-collections"}
WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
ROOT = Path(__file__).resolve().parents[4]
_TAXONOMY = json.loads((ROOT / "profiles/amazon-jp/slot-taxonomy.json").read_text(encoding="utf-8"))
STABLE_NON_TEMPLATE_SLOTS = set(_TAXONOMY["gallery"]) | set(_TAXONOMY["detail"])


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_project_relative(value: object) -> bool:
    if not _nonempty_string(value):
        return False
    text = value.strip()
    if text.startswith(("/", "\\")) or WINDOWS_DRIVE.match(text):
        return False
    if "\\" in text:
        return False
    path = PurePosixPath(text)
    return bool(path.parts) and not path.is_absolute() and ".." not in path.parts and "." not in path.parts


def expected_content_slot(binding: dict) -> str | None:
    values = [binding.get("content_id"), binding.get("module_id"), binding.get("slot_key")]
    if not all(_nonempty_string(value) for value in values):
        return None
    return f"content:{values[0]}:module:{values[1]}:slot:{values[2]}"


def validate_binding(binding: dict) -> list[str]:
    if not isinstance(binding, dict):
        return ["binding must be an object"]
    errors: list[str] = []
    for field in REQUIRED_BINDING_FIELDS:
        if not _nonempty_string(binding.get(field)):
            errors.append(f"{field} must be a non-empty string")

    if "output_ref" not in errors and not _is_project_relative(binding.get("output_ref")):
        errors.append("output_ref must be project-root-relative")

    variation_id = binding.get("variation_id")
    if variation_id is not None and not _nonempty_string(variation_id):
        errors.append("variation_id must be null or a non-empty string")

    content_fields = ("content_id", "module_id", "template_id", "slot_key")
    present = [field for field in content_fields if binding.get(field) is not None]
    if present and len(present) != len(content_fields):
        errors.append("content bindings require content_id/module_id/template_id/slot_key together")
    elif len(present) == len(content_fields):
        if any(not _nonempty_string(binding.get(field)) for field in content_fields):
            errors.append("content binding coordinates must be non-empty strings")
        else:
            expected = expected_content_slot(binding)
            if binding.get("slot_id") != expected:
                errors.append("content slot_id does not match content_id/module_id/slot_key")
    elif _nonempty_string(binding.get("slot_id")) and binding.get("slot_id") not in STABLE_NON_TEMPLATE_SLOTS:
        errors.append("slot_id is not in Amazon Japan stable taxonomy")

    return errors


def _template_index(registry: dict) -> dict[str, dict]:
    if not isinstance(registry, dict) or not isinstance(registry.get("templates"), list):
        return {}
    result: dict[str, dict] = {}
    for row in registry["templates"]:
        if isinstance(row, dict) and _nonempty_string(row.get("template_id")):
            result[row["template_id"]] = row
    return result


def _media_type(output_ref: str) -> str | None:
    suffix = PurePosixPath(output_ref).suffix.casefold()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return "image"
    if suffix in {".mp4", ".webm"}:
        return "video"
    if suffix == ".pdf":
        return "document"
    return None


def validate_template_binding(binding: dict, registry: dict) -> list[str]:
    errors = validate_binding(binding)
    if errors:
        return errors
    template_id = binding.get("template_id")
    if template_id is None:
        return []
    template = _template_index(registry).get(template_id)
    if template is None:
        return ["template_id not found in registry"]
    slot_keys = template.get("slot_keys")
    if not isinstance(slot_keys, list) or binding.get("slot_key") not in slot_keys:
        errors.append("slot_key is not supported by template_id")
    media_type = _media_type(binding["output_ref"])
    supported = template.get("supported_media_types")
    if media_type and isinstance(supported, list) and media_type not in supported:
        errors.append("output_ref media type is not supported by template_id")
    return errors


def _content_index(contents: object) -> dict[str, str]:
    if not isinstance(contents, list):
        return {}
    result: dict[str, str] = {}
    for row in contents:
        if not isinstance(row, dict):
            continue
        content_id = row.get("content_id")
        content_type = row.get("content_type")
        if _nonempty_string(content_id) and content_type in CONTENT_TYPES:
            result[content_id] = content_type
    return result


def validate_active_selection(selection: dict, contents: object) -> list[str]:
    if not isinstance(selection, dict):
        return ["active_selection must be an object"]
    errors: list[str] = []
    if selection.get("basic_a_plus_id") and selection.get("premium_a_plus_id"):
        errors.append("Basic A+ and Premium A+ cannot both be active")
    if selection.get("brand_story_id") and selection.get("shoppable_collections_id"):
        errors.append("Brand Story and Shoppable Collections cannot both be active")

    index = _content_index(contents)
    enhanced_id = selection.get("enhanced_description_id")
    brand_id = selection.get("brand_content_id")
    if enhanced_id is not None:
        if not _nonempty_string(enhanced_id) or index.get(enhanced_id) not in {"basic-a-plus", "premium-a-plus"}:
            errors.append("enhanced_description_id must reference Basic A+ or Premium A+")
    if brand_id is not None:
        if not _nonempty_string(brand_id) or index.get(brand_id) not in {"brand-story", "shoppable-collections"}:
            errors.append("brand_content_id must reference Brand Story or Shoppable Collections")
    return errors


def validate_eligibility(eligibility: dict) -> list[str]:
    if not isinstance(eligibility, dict):
        return ["eligibility must be an object"]
    errors: list[str] = []
    missing = sorted(ELIGIBILITY_KEYS - set(eligibility))
    if missing:
        errors.append(f"eligibility missing keys: {','.join(missing)}")
        return errors
    for field in (
        "production_freeze_ready",
        "required_asset_set_complete",
        "approved_output_matches",
        "asset_binding_complete",
    ):
        if not isinstance(eligibility.get(field), bool):
            errors.append(f"{field} must be boolean")
    conflicts = eligibility.get("blocking_conflicts")
    if not isinstance(conflicts, list) or any(not _nonempty_string(item) for item in conflicts):
        errors.append("blocking_conflicts must be a list of non-empty strings")
    if eligibility.get("hard_verification_status") not in {"PASS", "UNVERIFIED", "FAIL"}:
        errors.append("hard_verification_status must be PASS, UNVERIFIED, or FAIL")
    return errors


def validate_manifest(manifest: dict) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]
    errors: list[str] = []
    if manifest.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    project = manifest.get("project")
    if not isinstance(project, dict):
        errors.append("project must be an object")
    else:
        if project.get("market") != "JP":
            errors.append("project.market must be JP")
        if project.get("channel") != "amazon-jp":
            errors.append("project.channel must be amazon-jp")
        if not _nonempty_string(project.get("locale")):
            errors.append("project.locale must be a non-empty string")

    contents = manifest.get("contents", [])
    if not isinstance(contents, list):
        errors.append("contents must be a list")
    else:
        seen: set[str] = set()
        for row in contents:
            if not isinstance(row, dict) or not _nonempty_string(row.get("content_id")) or row.get("content_type") not in CONTENT_TYPES:
                errors.append("each content row requires content_id and supported content_type")
                continue
            if row["content_id"] in seen:
                errors.append("content_id values must be unique")
            seen.add(row["content_id"])

    errors.extend(validate_active_selection(manifest.get("active_selection", {}), contents))

    declared_variations: set[str] = set()
    listing_family = manifest.get("listing_family")
    if listing_family is not None:
        if not isinstance(listing_family, dict):
            errors.append("listing_family must be an object or null")
        else:
            variations = listing_family.get("variations", [])
            if not isinstance(variations, list):
                errors.append("listing_family.variations must be a list")
            else:
                for row in variations:
                    variation_id = row.get("variation_id") if isinstance(row, dict) else None
                    if not _nonempty_string(variation_id):
                        errors.append("each variation requires variation_id")
                    elif variation_id in declared_variations:
                        errors.append("listing_family variation_id values must be unique")
                    else:
                        declared_variations.add(variation_id)

    bindings = manifest.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        errors.append("bindings must be a non-empty list")
    else:
        seen_slots: set[tuple[object, object]] = set()
        for binding in bindings:
            errors.extend(validate_binding(binding))
            if isinstance(binding, dict):
                variation_id = binding.get("variation_id")
                if variation_id is not None and variation_id not in declared_variations:
                    errors.append("binding variation_id is not declared in listing_family")
                key = (variation_id, binding.get("slot_id"))
                if key in seen_slots:
                    errors.append("binding slot_id must be unique within variation")
                seen_slots.add(key)
    errors.extend(validate_eligibility(manifest.get("eligibility")))
    return errors


def validate_asset_slot_contract(contract: dict, registry: dict | None = None) -> list[str]:
    if not isinstance(contract, dict):
        return ["asset-slot contract must be an object"]
    errors: list[str] = []
    if contract.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    bindings = contract.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        errors.append("bindings must be a non-empty list")
        return errors
    seen_slots: set[tuple[object, object]] = set()
    for binding in bindings:
        if registry is None:
            errors.extend(validate_binding(binding))
        else:
            errors.extend(validate_template_binding(binding, registry))
        if isinstance(binding, dict):
            key = (binding.get("variation_id"), binding.get("slot_id"))
            if key in seen_slots:
                errors.append("binding slot_id must be unique within variation")
            seen_slots.add(key)
    return errors
