#!/usr/bin/env python3
"""Validate built M5 release artifacts without publishing them."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_PRIVATE_MARKERS = (b"/Users/", b"github_pat_", b"ghp_", b"AKIA")
LEGACY_PREFIXES = (
    ".agents/skills/japan-listing-demo/",
    ".agents/skills/listing-hardening/",
    "amazon-japan-creative-workflow/internal-skills/japan-listing-demo/",
    "amazon-japan-creative-workflow/internal-skills/listing-hardening/",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_member_name(name: str) -> bool:
    if not isinstance(name, str) or not name or name.endswith("/"):
        return False
    if "\\" in name or name.startswith("/"):
        return False
    path = PurePosixPath(name)
    return bool(path.parts) and not path.is_absolute() and ".." not in path.parts


def _manifest_path(root: Path) -> Path | None:
    matches = sorted(root.glob("amazon-japan-creative-workflow-*-release-manifest.json"))
    return matches[0] if len(matches) == 1 else None


def _validate_zip(path: Path, artifact_type: str, manifest: dict, errors: list[str]) -> None:
    try:
        with ZipFile(path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                errors.append(f"{path.name}: duplicate ZIP members")
            for info in infos:
                name = info.filename
                if not _safe_member_name(name):
                    errors.append(f"{path.name}: unsafe ZIP member {name!r}")
                    continue
                mode = (info.external_attr >> 16) & 0o170000
                if mode == 0o120000:
                    errors.append(f"{path.name}: symlink member is forbidden: {name}")
                if "selftest_" in name or "__pycache__" in name or name.endswith(".pyc"):
                    errors.append(f"{path.name}: repository-only test/cache leaked: {name}")
                if any(name.startswith(prefix) for prefix in LEGACY_PREFIXES):
                    errors.append(f"{path.name}: legacy-only Skill leaked into current release: {name}")
                data = archive.read(name)
                if any(marker in data for marker in FORBIDDEN_PRIVATE_MARKERS):
                    errors.append(f"{path.name}: private/sensitive marker in {name}")

            build_info_name = (
                "amazon-japan-creative-workflow/BUILD_INFO.json"
                if artifact_type == "one_install_skill"
                else "BUILD_INFO.json"
            )
            if build_info_name not in names:
                errors.append(f"{path.name}: BUILD_INFO.json missing")
            else:
                try:
                    build_info = json.loads(archive.read(build_info_name).decode("utf-8"))
                except (UnicodeError, json.JSONDecodeError) as exc:
                    errors.append(f"{path.name}: invalid BUILD_INFO.json: {exc}")
                else:
                    for field in ["version", "source_commit", "artifact_type", "distribution"]:
                        expected = manifest.get(field) if field in {"version", "source_commit", "distribution"} else artifact_type
                        if build_info.get(field) != expected:
                            errors.append(f"{path.name}: BUILD_INFO {field} mismatch")

            if artifact_type == "one_install_skill":
                required = {
                    "amazon-japan-creative-workflow/SKILL.md",
                    "amazon-japan-creative-workflow/core/manifest.yaml",
                    "amazon-japan-creative-workflow/runtime-scripts/package_common.py",
                }
                for skill in manifest.get("runtime_skills", []):
                    if skill == "amazon-japan-creative-workflow":
                        continue
                    required.add(f"amazon-japan-creative-workflow/internal-skills/{skill}/SKILL.md")
                for skill in manifest.get("support_skills", []):
                    required.add(f"amazon-japan-creative-workflow/internal-skills/{skill}/SKILL.md")
            elif artifact_type == "codex_bundle":
                required = {
                    "BUILD_INFO.json",
                    "README.md",
                    "VERSION",
                    "contracts/final-eligibility.schema.json",
                    "profiles/amazon-jp/slot-taxonomy.json",
                }
                for skill in manifest.get("runtime_skills", []):
                    required.add(f".agents/skills/{skill}/SKILL.md")
                for skill in manifest.get("support_skills", []):
                    required.add(f".agents/skills/{skill}/SKILL.md")
            else:
                errors.append(f"unknown artifact type: {artifact_type}")
                required = set()

            missing = sorted(required - set(names))
            if missing:
                errors.append(f"{path.name}: missing required members: {', '.join(missing)}")
    except (OSError, BadZipFile) as exc:
        errors.append(f"{path.name}: invalid ZIP: {exc}")


def validate_release_dir(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    if not root.is_dir():
        return [f"release directory missing: {root}"]

    manifest_path = _manifest_path(root)
    if manifest_path is None:
        return ["release directory must contain exactly one release manifest"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"invalid release manifest: {exc}"]
    if not isinstance(manifest, dict):
        return ["release manifest root must be an object"]

    if manifest.get("schema_version") != "1.0":
        errors.append("release manifest schema_version must be 1.0")
    if manifest.get("distribution") != "amazon-japan-creative-workflow":
        errors.append("release manifest distribution mismatch")
    version = manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("release manifest version invalid")
    source_commit = manifest.get("source_commit")
    if not isinstance(source_commit, str) or not HEX40.fullmatch(source_commit):
        errors.append("release manifest source_commit invalid")
    if manifest.get("normal_invocation") != "$amazon-japan-creative-workflow":
        errors.append("release manifest normal_invocation mismatch")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {"one_install_skill", "codex_bundle"}:
        errors.append("release manifest artifacts must contain one_install_skill and codex_bundle")
        artifacts = {}

    expected_checksum_lines: list[str] = []
    for artifact_type, row in artifacts.items():
        if not isinstance(row, dict):
            errors.append(f"{artifact_type}: artifact row must be an object")
            continue
        filename = row.get("filename")
        expected_sha = row.get("sha256")
        expected_bytes = row.get("bytes")
        if not isinstance(filename, str) or not filename:
            errors.append(f"{artifact_type}: filename missing")
            continue
        path = root / filename
        if not path.is_file():
            errors.append(f"{artifact_type}: artifact missing: {filename}")
            continue
        actual_sha = _sha256(path)
        if not isinstance(expected_sha, str) or not HEX64.fullmatch(expected_sha):
            errors.append(f"{artifact_type}: sha256 invalid")
        elif actual_sha != expected_sha:
            errors.append(f"{artifact_type}: sha256 mismatch")
        if not isinstance(expected_bytes, int) or isinstance(expected_bytes, bool) or path.stat().st_size != expected_bytes:
            errors.append(f"{artifact_type}: byte size mismatch")
        expected_checksum_lines.append(f"{expected_sha}  {filename}")
        _validate_zip(path, artifact_type, manifest, errors)

    expected_checksum_lines.append(f"{_sha256(manifest_path)}  {manifest_path.name}")
    checksum_path = root / "SHA256SUMS"
    if not checksum_path.is_file():
        errors.append("SHA256SUMS missing")
    else:
        actual_lines = checksum_path.read_text(encoding="utf-8").strip().splitlines()
        if actual_lines != sorted(expected_checksum_lines):
            errors.append("SHA256SUMS content mismatch")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_dir", type=Path)
    args = parser.parse_args()
    errors = validate_release_dir(args.release_dir)
    if errors:
        print("FAIL: release validation")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: release artifacts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
