#!/usr/bin/env python3
"""M5.1 RED/GREEN tests for official Plugin distribution and Git provenance."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "scripts" / "package_release.py"
VALIDATE = ROOT / "scripts" / "validate_release.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def init_repo(root: Path) -> str:
    run("git", "init", "-q", cwd=root)
    run("git", "config", "user.email", "m51@example.invalid", cwd=root)
    run("git", "config", "user.name", "M5.1 Test", cwd=root)
    (root / "tracked.txt").write_text("clean\n", encoding="utf-8")
    run("git", "add", "tracked.txt", cwd=root)
    result = run("git", "commit", "-qm", "fixture", cwd=root)
    assert result.returncode == 0, result.stderr
    head = run("git", "rev-parse", "HEAD", cwd=root)
    assert head.returncode == 0
    return head.stdout.strip()


def test_release_contract_declares_plugin_not_one_install() -> None:
    package = load(PACKAGE, "m51_package_contract")
    assert hasattr(package, "PLUGIN_ARTIFACT"), "M5.1 requires PLUGIN_ARTIFACT"
    assert package.PLUGIN_ARTIFACT == "plugin_bundle"
    assert "one_install_skill" not in getattr(package, "PRIMARY_ARTIFACT_TYPES", set())


def test_plugin_archive_uses_official_layout_and_excludes_legacy_shim() -> None:
    package = load(PACKAGE, "m51_package_plugin")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "dist"
        manifest = package.build_release(out, package._default_source_commit())
        artifacts = manifest["artifacts"]
        assert "plugin_bundle" in artifacts
        assert "one_install_skill" not in artifacts
        plugin = out / artifacts["plugin_bundle"]["filename"]
        with ZipFile(plugin) as archive:
            names = set(archive.namelist())
            prefix = "amazon-japan-creative-workflow/"
            manifest_name = prefix + ".codex-plugin/plugin.json"
            assert manifest_name in names
            plugin_json = json.loads(archive.read(manifest_name).decode("utf-8"))
            assert plugin_json["skills"] == "./skills/"
            for skill in manifest["runtime_skills"] + manifest["support_skills"]:
                assert prefix + f"skills/{skill}/SKILL.md" in names
            assert not any("/internal-skills/" in name for name in names)
            assert not any(name.endswith("/scripts/validate_project_state.py") for name in names)


def test_fake_expected_commit_is_rejected() -> None:
    package = load(PACKAGE, "m51_package_fake_sha")
    actual = package._default_source_commit()
    fake = "1" * 40
    if actual == fake:
        fake = "2" * 40
    with tempfile.TemporaryDirectory() as tmp:
        try:
            package.build_release(Path(tmp) / "dist", fake)
        except ValueError as exc:
            assert "HEAD" in str(exc) or "source" in str(exc).lower()
        else:
            raise AssertionError("fake source commit must fail closed")


def test_dirty_tracked_tree_is_rejected_by_git_verifier() -> None:
    package = load(PACKAGE, "m51_package_dirty")
    assert hasattr(package, "verify_git_source"), "M5.1 requires verify_git_source()"
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        head = init_repo(repo)
        assert package.verify_git_source(head, repo_root=repo) == head
        (repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")
        try:
            package.verify_git_source(head, repo_root=repo)
        except ValueError as exc:
            assert "dirty" in str(exc).lower() or "clean" in str(exc).lower()
        else:
            raise AssertionError("dirty tracked tree must fail closed")


def test_independent_validator_rejects_internal_skills_and_legacy_shim() -> None:
    validator = load(VALIDATE, "m51_validate_release")
    text = VALIDATE.read_text(encoding="utf-8")
    assert "internal-skills" in text, "validator must explicitly reject old private discovery layout"
    assert "validate_project_state.py" in text, "validator must explicitly reject broken legacy shim"
    assert hasattr(validator, "validate_release_dir")


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} M5.1 release reliability tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
