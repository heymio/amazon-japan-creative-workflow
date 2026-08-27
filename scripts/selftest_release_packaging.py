#!/usr/bin/env python3
"""M5 release packaging contract tests.

The tests intentionally exercise the built archives after extraction. They define
what the new distribution must guarantee before implementation exists.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_MODULE = ROOT / "scripts" / "package_release.py"
VALIDATE_MODULE = ROOT / "scripts" / "validate_release.py"
SOURCE_COMMIT = "1" * 40
EXPECTED_VERSION = "0.1.0"
CURRENT_RUNTIME_SKILLS = {
    "amazon-japan-creative-workflow",
    "listing-strategy",
    "creative-production",
    "creative-quality",
    "listing-simulator-bridge",
    "evidence-hardening",
}
SUPPORT_SKILLS = {"listing-evidence-auditor"}
LEGACY_ONLY_SKILLS = {"japan-listing-demo", "listing-hardening"}


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(tmp: Path) -> tuple[object, dict, Path]:
    package = load(PACKAGE_MODULE, "m5_package_release")
    manifest = package.build_release(tmp, SOURCE_COMMIT)
    manifest_path = tmp / f"amazon-japan-creative-workflow-{EXPECTED_VERSION}-release-manifest.json"
    assert manifest_path.is_file()
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest
    return package, manifest, manifest_path


def test_version_sources_are_consistent() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    manifest = (ROOT / ".agents" / "skills" / "amazon-japan-creative-workflow" / "core" / "manifest.yaml").read_text(encoding="utf-8")
    assert version == EXPECTED_VERSION
    assert f"distribution_version: {version}" in manifest


def test_build_creates_two_primary_archives_manifest_and_checksums() -> None:
    with tempfile.TemporaryDirectory() as name:
        out = Path(name)
        _, manifest, manifest_path = build(out)
        assert manifest["schema_version"] == "1.0"
        assert manifest["version"] == EXPECTED_VERSION
        assert manifest["source_commit"] == SOURCE_COMMIT
        assert manifest["normal_invocation"] == "$amazon-japan-creative-workflow"
        assert manifest["runtime_skills"] == sorted(CURRENT_RUNTIME_SKILLS)
        assert manifest["support_skills"] == sorted(SUPPORT_SKILLS)
        assert set(manifest["artifacts"]) == {"one_install_skill", "codex_bundle"}
        assert manifest_path.is_file()
        assert (out / "SHA256SUMS").is_file()
        for row in manifest["artifacts"].values():
            assert (out / row["filename"]).is_file()


def test_release_build_is_deterministic_for_same_source_commit() -> None:
    with tempfile.TemporaryDirectory() as a_name, tempfile.TemporaryDirectory() as b_name:
        a = Path(a_name)
        b = Path(b_name)
        _, manifest_a, _ = build(a)
        _, manifest_b, _ = build(b)
        assert manifest_a == manifest_b
        for key in manifest_a["artifacts"]:
            filename = manifest_a["artifacts"][key]["filename"]
            assert sha256(a / filename) == sha256(b / filename)
        assert (a / "SHA256SUMS").read_bytes() == (b / "SHA256SUMS").read_bytes()


def test_one_install_archive_contains_current_runtime_only() -> None:
    with tempfile.TemporaryDirectory() as name:
        out = Path(name)
        _, manifest, _ = build(out)
        archive_path = out / manifest["artifacts"]["one_install_skill"]["filename"]
        with ZipFile(archive_path) as archive:
            members = set(archive.namelist())
            prefix = "amazon-japan-creative-workflow/"
            assert prefix + "SKILL.md" in members
            assert prefix + "core/manifest.yaml" in members
            assert prefix + "BUILD_INFO.json" in members
            assert prefix + "runtime-scripts/package_common.py" in members
            for skill in (CURRENT_RUNTIME_SKILLS - {"amazon-japan-creative-workflow"}) | SUPPORT_SKILLS:
                assert prefix + f"internal-skills/{skill}/SKILL.md" in members
            for legacy in LEGACY_ONLY_SKILLS:
                assert not any(f"internal-skills/{legacy}/" in member for member in members)
            assert not any("selftest_" in member or "__pycache__" in member or member.endswith(".pyc") for member in members)


def test_codex_bundle_preserves_project_skill_layout_without_legacy_default() -> None:
    with tempfile.TemporaryDirectory() as name:
        out = Path(name)
        _, manifest, _ = build(out)
        archive_path = out / manifest["artifacts"]["codex_bundle"]["filename"]
        with ZipFile(archive_path) as archive:
            members = set(archive.namelist())
            assert "BUILD_INFO.json" in members
            assert "VERSION" in members
            assert "README.md" in members
            assert "contracts/final-eligibility.schema.json" in members
            assert "profiles/amazon-jp/slot-taxonomy.json" in members
            for skill in CURRENT_RUNTIME_SKILLS | SUPPORT_SKILLS:
                assert f".agents/skills/{skill}/SKILL.md" in members
            for legacy in LEGACY_ONLY_SKILLS:
                assert not any(member.startswith(f".agents/skills/{legacy}/") for member in members)
            assert not any("selftest_" in member or "__pycache__" in member or member.endswith(".pyc") for member in members)


def test_manifest_hashes_and_sha256sums_match_physical_artifacts() -> None:
    with tempfile.TemporaryDirectory() as name:
        out = Path(name)
        _, manifest, manifest_path = build(out)
        expected_lines = []
        for row in manifest["artifacts"].values():
            path = out / row["filename"]
            assert row["sha256"] == sha256(path)
            assert row["bytes"] == path.stat().st_size
            expected_lines.append(f"{row['sha256']}  {row['filename']}")
        expected_lines.append(f"{sha256(manifest_path)}  {manifest_path.name}")
        actual = (out / "SHA256SUMS").read_text(encoding="utf-8").strip().splitlines()
        assert actual == sorted(expected_lines)


def test_one_install_embedded_simulator_bridge_can_import_package_common() -> None:
    with tempfile.TemporaryDirectory() as name:
        out = Path(name)
        _, manifest, _ = build(out)
        archive_path = out / manifest["artifacts"]["one_install_skill"]["filename"]
        extract_root = out / "extract"
        with ZipFile(archive_path) as archive:
            archive.extractall(extract_root)
        script = extract_root / "amazon-japan-creative-workflow" / "internal-skills" / "listing-simulator-bridge" / "scripts" / "build_import_pack.py"
        result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "source_root" in result.stdout


def test_release_validator_accepts_clean_build_and_rejects_tampering() -> None:
    validator = load(VALIDATE_MODULE, "m5_validate_release")
    with tempfile.TemporaryDirectory() as name:
        out = Path(name)
        _, manifest, _ = build(out)
        assert validator.validate_release_dir(out) == []
        archive_name = manifest["artifacts"]["codex_bundle"]["filename"]
        with (out / archive_name).open("ab") as handle:
            handle.write(b"tamper")
        errors = validator.validate_release_dir(out)
        assert any("sha256" in error.casefold() for error in errors), errors


def test_release_archives_do_not_contain_forbidden_private_markers() -> None:
    forbidden = [b"/Users/", b"github_pat_", b"ghp_", b"AKIA"]
    with tempfile.TemporaryDirectory() as name:
        out = Path(name)
        _, manifest, _ = build(out)
        for row in manifest["artifacts"].values():
            with ZipFile(out / row["filename"]) as archive:
                for member in archive.namelist():
                    data = archive.read(member)
                    assert not any(marker in data for marker in forbidden), member


def main() -> int:
    tests = [(name, value) for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for name, test in sorted(tests):
        test()
    print(f"PASS: {len(tests)} M5 release packaging tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
