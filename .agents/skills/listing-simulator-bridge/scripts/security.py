#!/usr/bin/env python3
"""Security primitives for Simulator import folders and ZIP packs."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
FORBIDDEN_ENV_NAMES = {".env", ".env.local"}
FORBIDDEN_SCRIPT_SUFFIXES = {".js", ".mjs", ".cjs"}
DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024
DEFAULT_MAX_COMPRESSION_RATIO = 200.0


def validate_project_relative_path(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("empty project-relative path")
    text = value.strip()
    if text.startswith(("/", "\\")) or WINDOWS_DRIVE.match(text) or "\\" in text:
        raise ValueError(f"unsafe project-relative path: {value}")
    path = PurePosixPath(text)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"unsafe project-relative path: {value}")
    normalized = path.as_posix()
    if normalized in {"", "."}:
        raise ValueError("empty project-relative path")
    return normalized


def _validate_pack_name(name: str) -> str:
    normalized = validate_project_relative_path(name)
    path = PurePosixPath(normalized)
    if path.name.casefold() in FORBIDDEN_ENV_NAMES:
        raise ValueError(f"forbidden environment file: {normalized}")
    if path.suffix.casefold() in FORBIDDEN_SCRIPT_SUFFIXES:
        raise ValueError(f"executable JavaScript is not allowed in Simulator pack: {normalized}")
    return normalized


def validate_source_tree(root: Path, *, max_file_size: int = DEFAULT_MAX_FILE_SIZE) -> list[tuple[str, Path]]:
    root = Path(root)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"source root must be a directory: {root}")
    if root.is_symlink():
        raise ValueError(f"symlink source root is not allowed: {root}")
    files: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed in Simulator pack input: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        normalized = _validate_pack_name(relative)
        if normalized in seen:
            raise ValueError(f"duplicate normalized path: {normalized}")
        seen.add(normalized)
        size = path.stat().st_size
        if size > max_file_size:
            raise ValueError(f"file size exceeds Simulator pack limit: {normalized}")
        files.append((normalized, path))
    return files


def validate_zip_archive(
    archive_path: Path,
    *,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO,
) -> None:
    archive_path = Path(archive_path)
    with ZipFile(archive_path) as archive:
        seen: set[str] = set()
        for info in archive.infolist():
            if info.is_dir():
                continue
            normalized = _validate_pack_name(info.filename)
            if normalized in seen:
                raise ValueError(f"duplicate normalized ZIP path: {normalized}")
            seen.add(normalized)
            unix_type = (info.external_attr >> 16) & 0o170000
            if unix_type == 0o120000:
                raise ValueError(f"ZIP symlink member is not allowed: {normalized}")
            if info.file_size > max_file_size:
                raise ValueError(f"ZIP member size exceeds limit: {normalized}")
            if info.file_size > 0:
                if info.compress_size <= 0:
                    raise ValueError(f"ZIP member compression ratio is unsafe: {normalized}")
                ratio = info.file_size / info.compress_size
                if ratio > max_compression_ratio:
                    raise ValueError(f"ZIP member compression ratio exceeds limit: {normalized}")
