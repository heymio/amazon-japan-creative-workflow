#!/usr/bin/env python3
"""Build deterministic M5.1 release-candidate artifacts from verified Git state.

The builder never creates tags, pushes commits, or publishes a GitHub Release.
The current installable multi-Skill artifact is an OpenAI Plugin bundle, not a
single Skill ZIP with private nested Skill discovery.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
ROUTER_SKILL = "amazon-japan-creative-workflow"
RUNTIME_SKILLS = [
    "amazon-japan-creative-workflow",
    "listing-strategy",
    "creative-production",
    "creative-quality",
    "listing-simulator-bridge",
    "evidence-hardening",
]
SUPPORT_SKILLS = ["listing-evidence-auditor"]
LEGACY_ONLY_SKILLS = {"japan-listing-demo", "listing-hardening"}
PLUGIN_ARTIFACT = "plugin_bundle"
CODEX_ARTIFACT = "codex_bundle"
PRIMARY_ARTIFACT_TYPES = {PLUGIN_ARTIFACT, CODEX_ARTIFACT}
PLUGIN_PREFIX = Path(ROUTER_SKILL)
RELEASE_DOCS = [
    "docs/install.md",
    "docs/provenance.md",
    "docs/simulator-integration.md",
    "docs/evidence-hardening.md",
    "docs/release.md",
    "docs/agent-pressure-evals.md",
    "docs/release-notes-v0.1.1.md",
]
ROOT_METADATA = ["README.md", "VERSION", "LICENSE"]
FORBIDDEN_PRIVATE_MARKERS = (b"/Users/", b"github_pat_", b"ghp_", b"AKIA")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
BROKEN_CURRENT_SHIM = "scripts/validate_project_state.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from package_common import collect_files, reject_symlinks, sha256_file, write_deterministic_zip  # noqa: E402


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _version() -> str:
    value = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(value):
        raise ValueError(f"VERSION must be x.y.z, got {value!r}")
    manifest_text = (SKILLS_ROOT / ROUTER_SKILL / "core" / "manifest.yaml").read_text(encoding="utf-8")
    if f"distribution_version: {value}" not in manifest_text:
        raise ValueError("VERSION and router distribution_version do not match")
    return value


def _normalize_commit(value: str) -> str:
    normalized = value.strip().casefold() if isinstance(value, str) else ""
    if not HEX40.fullmatch(normalized):
        raise ValueError("source commit must be a full 40-character lowercase Git SHA")
    return normalized


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise ValueError(detail)
    return result.stdout.strip()


def verify_git_source(expected_commit: str | None = None, *, repo_root: Path = REPO_ROOT) -> str:
    """Return authoritative clean HEAD, rejecting declaration/tree mismatch."""
    repo_root = Path(repo_root)
    head = _normalize_commit(_git(repo_root, "rev-parse", "--verify", "HEAD"))
    if expected_commit is not None:
        expected = _normalize_commit(expected_commit)
        if expected != head:
            raise ValueError(f"source commit does not match HEAD: expected {expected}, HEAD {head}")
    dirty = _git(repo_root, "status", "--porcelain", "--untracked-files=no")
    if dirty:
        raise ValueError("release source Git tree is dirty; commit or revert tracked changes before packaging")
    return head


def _exclude_runtime(relative: Path) -> bool:
    if relative.name.startswith("selftest_") or relative.name.startswith("selftest-"):
        return True
    if "evals" in relative.parts or "__pycache__" in relative.parts:
        return True
    return relative.suffix == ".pyc"


def _exclude_current_skill_member(skill: str, relative: Path) -> bool:
    if _exclude_runtime(relative):
        return True
    return skill == ROUTER_SKILL and relative.as_posix() == BROKEN_CURRENT_SHIM


def _scan_release_bytes(name: str, data: bytes) -> None:
    path = Path(name)
    if path.name.casefold() in {".env", ".env.local"}:
        raise ValueError(f"forbidden environment file in release: {name}")
    if path.suffix.casefold() in {".js", ".mjs", ".cjs"}:
        raise ValueError(f"executable JavaScript is not part of the workflow release: {name}")
    for marker in FORBIDDEN_PRIVATE_MARKERS:
        if marker in data:
            raise ValueError(f"private/sensitive marker found in release member: {name}")


def _patched_plugin_bytes(skill: str, relative: Path, data: bytes) -> bytes:
    """Patch only packaged Plugin copies for plugin-root shared dependencies."""
    text: str | None = None
    if skill == "listing-simulator-bridge" and relative.as_posix() == "scripts/build_import_pack.py":
        text = data.decode("utf-8")
        old = '''HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))'''
        new = '''HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parents[2]
sys.path.insert(0, str(PLUGIN_ROOT / "runtime-scripts"))'''
        if old not in text:
            raise ValueError("Simulator Bridge package_common path block changed; update Plugin patch")
        text = text.replace(old, new)
    elif skill == "listing-simulator-bridge" and relative.as_posix() == "scripts/validate_contract.py":
        text = data.decode("utf-8")
        old = 'ROOT = Path(__file__).resolve().parents[4]'
        new = 'ROOT = Path(__file__).resolve().parents[3]'
        if old not in text:
            raise ValueError("Simulator Bridge taxonomy path block changed; update Plugin patch")
        text = text.replace(old, new)
    return text.encode("utf-8") if text is not None else data


def _add_file(entries: list[tuple[str, bytes]], name: str, data: bytes) -> None:
    _scan_release_bytes(name, data)
    entries.append((name, data))


def _add_skill_tree(
    entries: list[tuple[str, bytes]],
    skill: str,
    target_root: Path,
    *,
    plugin_mode: bool,
) -> None:
    source_root = SKILLS_ROOT / skill
    if not (source_root / "SKILL.md").is_file():
        raise ValueError(f"missing runtime Skill source: {skill}")
    reject_symlinks(source_root)
    for path in collect_files(source_root):
        relative = path.relative_to(source_root)
        if _exclude_current_skill_member(skill, relative):
            continue
        data = path.read_bytes()
        if plugin_mode:
            data = _patched_plugin_bytes(skill, relative, data)
        _add_file(entries, (target_root / relative).as_posix(), data)


def _add_tree(entries: list[tuple[str, bytes]], source_root: Path, target_root: Path) -> None:
    reject_symlinks(source_root)
    for path in collect_files(source_root, exclude=_exclude_runtime):
        relative = path.relative_to(source_root)
        _add_file(entries, (target_root / relative).as_posix(), path.read_bytes())


def _build_info(artifact_type: str, version: str, source_commit: str) -> bytes:
    return _canonical_json({
        "schema_version": "1.0",
        "distribution": ROUTER_SKILL,
        "artifact_type": artifact_type,
        "version": version,
        "source_commit": source_commit,
        "normal_invocation": "$amazon-japan-creative-workflow",
        "runtime_skills": sorted(RUNTIME_SKILLS),
        "support_skills": sorted(SUPPORT_SKILLS),
    })


def _plugin_manifest(version: str) -> bytes:
    return _canonical_json({
        "name": ROUTER_SKILL,
        "version": version,
        "description": "Quality-first Amazon Japan listing strategy and creative workflow",
        "repository": "https://github.com/heymio/amazon-japan-creative-workflow",
        "license": "MIT",
        "skills": "./skills/",
        "interface": {
            "displayName": "Amazon Japan Creative Workflow",
            "shortDescription": "Japan-localized Amazon listing strategy and creative workflow"
        },
    })


def _plugin_entries(version: str, source_commit: str) -> list[tuple[str, bytes]]:
    entries: list[tuple[str, bytes]] = []
    _add_file(entries, (PLUGIN_PREFIX / ".codex-plugin" / "plugin.json").as_posix(), _plugin_manifest(version))
    for skill in RUNTIME_SKILLS + SUPPORT_SKILLS:
        _add_skill_tree(entries, skill, PLUGIN_PREFIX / "skills" / skill, plugin_mode=True)
    _add_tree(entries, REPO_ROOT / "contracts", PLUGIN_PREFIX / "contracts")
    _add_tree(entries, REPO_ROOT / "profiles", PLUGIN_PREFIX / "profiles")
    _add_file(
        entries,
        (PLUGIN_PREFIX / "runtime-scripts" / "package_common.py").as_posix(),
        (REPO_ROOT / "scripts" / "package_common.py").read_bytes(),
    )
    for relative in ROOT_METADATA + RELEASE_DOCS:
        source = REPO_ROOT / relative
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"missing/unsafe release metadata: {relative}")
        target = PLUGIN_PREFIX / (Path(relative).name if relative in ROOT_METADATA else relative)
        _add_file(entries, target.as_posix(), source.read_bytes())
    _add_file(entries, (PLUGIN_PREFIX / "BUILD_INFO.json").as_posix(), _build_info(PLUGIN_ARTIFACT, version, source_commit))
    return entries


def _codex_bundle_entries(version: str, source_commit: str) -> list[tuple[str, bytes]]:
    entries: list[tuple[str, bytes]] = []
    for skill in RUNTIME_SKILLS + SUPPORT_SKILLS:
        _add_skill_tree(entries, skill, Path(".agents") / "skills" / skill, plugin_mode=False)
    _add_tree(entries, REPO_ROOT / "contracts", Path("contracts"))
    _add_tree(entries, REPO_ROOT / "profiles", Path("profiles"))
    for relative in ROOT_METADATA + RELEASE_DOCS:
        source = REPO_ROOT / relative
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"missing/unsafe release metadata: {relative}")
        _add_file(entries, Path(relative).as_posix(), source.read_bytes())
    _add_file(entries, "scripts/package_common.py", (REPO_ROOT / "scripts" / "package_common.py").read_bytes())
    _add_file(entries, "BUILD_INFO.json", _build_info(CODEX_ARTIFACT, version, source_commit))
    return entries


def _artifact_row(path: Path) -> dict[str, object]:
    with ZipFile(path) as archive:
        members = archive.namelist()
    return {
        "filename": path.name,
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "member_count": len(members),
    }


def build_release(output_dir: Path, source_commit: str | None = None) -> dict[str, object]:
    """Build deterministic Plugin/Codex archives from a verified clean Git HEAD."""
    version = _version()
    authoritative_commit = verify_git_source(source_commit)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plugin = output_dir / f"{ROUTER_SKILL}-{version}-plugin.zip"
    codex_bundle = output_dir / f"{ROUTER_SKILL}-{version}-codex-bundle.zip"
    write_deterministic_zip(plugin, _plugin_entries(version, authoritative_commit))
    write_deterministic_zip(codex_bundle, _codex_bundle_entries(version, authoritative_commit))

    manifest: dict[str, object] = {
        "schema_version": "1.0",
        "distribution": ROUTER_SKILL,
        "version": version,
        "source_commit": authoritative_commit,
        "normal_invocation": "$amazon-japan-creative-workflow",
        "runtime_skills": sorted(RUNTIME_SKILLS),
        "support_skills": sorted(SUPPORT_SKILLS),
        "legacy_compatibility": sorted(LEGACY_ONLY_SKILLS),
        "publication": {"automatic": False, "github_release_created": False},
        "artifacts": {
            PLUGIN_ARTIFACT: _artifact_row(plugin),
            CODEX_ARTIFACT: _artifact_row(codex_bundle),
        },
    }

    manifest_path = output_dir / f"{ROUTER_SKILL}-{version}-release-manifest.json"
    manifest_path.write_bytes(_canonical_json(manifest))
    checksum_lines = []
    for row in manifest["artifacts"].values():  # type: ignore[union-attr]
        checksum_lines.append(f"{row['sha256']}  {row['filename']}")  # type: ignore[index]
    checksum_lines.append(f"{sha256_file(manifest_path)}  {manifest_path.name}")
    (output_dir / "SHA256SUMS").write_text("\n".join(sorted(checksum_lines)) + "\n", encoding="utf-8")
    return manifest


def _default_source_commit() -> str:
    github_sha = os.environ.get("GITHUB_SHA", "").strip().casefold()
    expected = github_sha if HEX40.fullmatch(github_sha) else None
    return verify_git_source(expected)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "dist")
    parser.add_argument("--source-commit", default=None)
    args = parser.parse_args()
    manifest = build_release(args.output_dir, args.source_commit)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
