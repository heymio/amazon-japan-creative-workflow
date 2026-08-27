# Release Candidate Process

M5 defines a deterministic release-candidate build. It does not automatically create Git tags or GitHub Releases.

## Version authority

`VERSION` is the release version source. It must match `distribution_version` in:

`/.agents/skills/amazon-japan-creative-workflow/core/manifest.yaml`

Current development version: `0.1.0`.

## Build

Build from the exact commit intended for release:

```bash
python3 scripts/package_release.py \
  --source-commit <40-character-git-sha> \
  --output-dir dist
```

M5 creates:

```text
amazon-japan-creative-workflow-0.1.0.skill.zip
amazon-japan-creative-workflow-0.1.0-codex-bundle.zip
amazon-japan-creative-workflow-0.1.0-release-manifest.json
SHA256SUMS
```

## Artifact roles

### One-install Skill ZIP

`amazon-japan-creative-workflow-<version>.skill.zip`

Use when one user-facing workflow entry is preferred. The archive root is:

```text
amazon-japan-creative-workflow/
```

The Router remains the only normal invocation. Current routed Skills and `listing-evidence-auditor` are embedded below `internal-skills/`.

Legacy `japan-listing-demo` and `listing-hardening` are not included in this current default artifact.

### Codex bundle

`amazon-japan-creative-workflow-<version>-codex-bundle.zip`

Use for a repository/project installation that preserves:

```text
.agents/skills/<skill-name>/...
contracts/...
profiles/...
```

Extract at the project root. The user-facing invocation remains:

```text
$amazon-japan-creative-workflow
```

## Validation

Validate a built release directory independently:

```bash
python3 scripts/validate_release.py dist
```

The validator recomputes artifact SHA-256 and byte sizes, validates `SHA256SUMS`, checks required members and `BUILD_INFO.json`, rejects unsafe ZIP members/symlinks/repository-only selftests, and scans for selected private/credential markers.

A release candidate is not considered valid solely because `package_release.py` completed.

## Determinism

For the same repository tree, version, and `source_commit`, the two ZIP archives, release manifest, and `SHA256SUMS` must be reproducible byte-for-byte.

Each archive includes `BUILD_INFO.json` binding it to:

- distribution name;
- artifact type;
- version;
- exact source commit;
- normal invocation;
- runtime/support Skill set.

## Publication boundary

The repository may build release candidates in CI, but M5 does not automatically:

- create a Git tag;
- create a GitHub Release;
- upload assets to a public Release;
- merge a release PR;
- publish from a Draft/Open PR head.

Formal publication should use an exact merged `main` commit or an explicitly approved tag only after user confirmation.

The manual `build-release-candidate.yml` workflow has read-only repository permissions and uploads only a GitHub Actions artifact for review.

## Legacy packaging

The imported v0.3.3 scripts, including the old `japan-listing-demo` one-install packager and old `scripts/package_codex_bundle.py`, remain compatibility/history code. They are not the M5 release contract.
