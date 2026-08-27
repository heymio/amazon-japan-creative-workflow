#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from security import (  # noqa: E402
    validate_project_relative_path,
    validate_source_tree,
    validate_zip_archive,
)


def test_bad_project_relative_paths_are_rejected():
    for value in ["../outside.png", "/" + "Users/example/secret.png", "C:" + r"\Users\example\secret.png", r"\\server\share\x.png"]:
        try:
            validate_project_relative_path(value)
        except ValueError:
            pass
        else:
            raise AssertionError(value)
    assert validate_project_relative_path("outputs/gallery/g1.png") == "outputs/gallery/g1.png"


def test_env_and_executable_javascript_are_rejected():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / ".env.local").write_text("TOKEN=x", encoding="utf-8")
        try:
            validate_source_tree(root)
        except ValueError as exc:
            assert ".env.local" in str(exc)
        else:
            raise AssertionError(".env.local must be rejected")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "assets").mkdir()
        (root / "assets/payload.js").write_text("alert(1)", encoding="utf-8")
        try:
            validate_source_tree(root)
        except ValueError as exc:
            assert "JavaScript" in str(exc)
        else:
            raise AssertionError("JavaScript must be rejected")


def test_symlink_input_is_rejected():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "root"
        root.mkdir()
        outside = Path(directory) / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        (root / "link.txt").symlink_to(outside)
        try:
            validate_source_tree(root)
        except ValueError as exc:
            assert "symlink" in str(exc).casefold()
        else:
            raise AssertionError("symlink must be rejected")


def test_zip_traversal_and_duplicate_normalized_paths_are_rejected():
    with tempfile.TemporaryDirectory() as directory:
        bad = Path(directory) / "bad.zip"
        with zipfile.ZipFile(bad, "w") as archive:
            archive.writestr("../escape.txt", b"x")
        try:
            validate_zip_archive(bad)
        except ValueError as exc:
            assert "unsafe" in str(exc).casefold()
        else:
            raise AssertionError("zip traversal must be rejected")

        dup = Path(directory) / "dup.zip"
        with zipfile.ZipFile(dup, "w") as archive:
            archive.writestr("assets//x.png", b"a")
            archive.writestr("assets/x.png", b"b")
        try:
            validate_zip_archive(dup)
        except ValueError as exc:
            assert "duplicate" in str(exc).casefold()
        else:
            raise AssertionError("normalized duplicates must be rejected")


def test_zip_oversize_and_high_compression_ratio_are_rejected():
    with tempfile.TemporaryDirectory() as directory:
        oversized = Path(directory) / "oversized.zip"
        with zipfile.ZipFile(oversized, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("big.bin", b"x" * 1024)
        try:
            validate_zip_archive(oversized, max_file_size=100)
        except ValueError as exc:
            assert "size" in str(exc).casefold()
        else:
            raise AssertionError("oversized member must be rejected")

        ratio = Path(directory) / "ratio.zip"
        with zipfile.ZipFile(ratio, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("compressible.txt", b"0" * 100000)
        try:
            validate_zip_archive(ratio, max_compression_ratio=5)
        except ValueError as exc:
            assert "compression ratio" in str(exc).casefold()
        else:
            raise AssertionError("suspicious ratio must be rejected")


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"simulator pack-security selftest: PASS ({len(tests)} tests)")
