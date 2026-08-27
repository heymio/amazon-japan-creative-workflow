#!/usr/bin/env python3
"""Resolve parent listing data with explicit variation overrides."""

from __future__ import annotations

from copy import deepcopy

CONTENT_KEY_FIELDS = ("content_id", "module_id", "slot_key")


def _content_key(row: dict) -> tuple[str, str, str]:
    if not isinstance(row, dict):
        raise ValueError("content_assets entries must be objects")
    values = tuple(row.get(field) for field in CONTENT_KEY_FIELDS)
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError("content_assets entries require content_id/module_id/slot_key")
    return values  # type: ignore[return-value]


def _merge_content_assets(parent: list, child: list) -> list:
    indexed: dict[tuple[str, str, str], dict] = {}
    for row in parent:
        indexed[_content_key(row)] = deepcopy(row)
    for row in child:
        indexed[_content_key(row)] = deepcopy(row)
    return list(indexed.values())


def _merge_value(parent: object, child: object, field: str | None = None) -> object:
    if child is None:
        return None
    if field == "content_assets" and isinstance(parent, list) and isinstance(child, list):
        return _merge_content_assets(parent, child)
    if isinstance(parent, dict) and isinstance(child, dict):
        result = deepcopy(parent)
        for key, value in child.items():
            if key in result:
                result[key] = _merge_value(result[key], value, key)
            else:
                result[key] = deepcopy(value)
        return result
    return deepcopy(child)


def resolve_variation(parent: dict, child: dict) -> dict:
    if not isinstance(parent, dict) or not isinstance(child, dict):
        raise ValueError("parent and child must be objects")
    result = deepcopy(parent)
    for key, value in child.items():
        if key in result:
            result[key] = _merge_value(result[key], value, key)
        else:
            result[key] = deepcopy(value)
    return result
