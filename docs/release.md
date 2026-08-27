# Release Candidate Process

M5.1 defines the deterministic release-candidate build and its non-deterministic publication gates. It does not automatically merge or publish v0.1.1.

## Version authority

`VERSION` is the release version source and must match `distribution_version` in `.agents/skills/amazon-japan-creative-workflow/core/manifest.yaml`.

Current development/release-candidate version: `0.1.1`.

## Build from verified Git state

The release builder derives the authoritative source commit from the current clean Git HEAD. A supplied `--source-commit` must equal HEAD.

```bash
python3 scripts/package_release.py \
  --source-commit "$(git rev-parse HEAD)" \
  --output-dir dist
python3 scripts/validate_release.py dist
```

The build fails when:

- HEAD cannot be resolved to a full Git SHA;
- the supplied SHA differs from HEAD;
- tracked files are dirty;
- version sources disagree;
- a release member violates the security/distribution contract.

## M5.1 artifacts

```text
amazon-japan-creative-workflow-0.1.1-plugin.zip
amazon-japan-creative-workflow-0.1.1-codex-bundle.zip
amazon-japan-creative-workflow-0.1.1-release-manifest.json
SHA256SUMS
```

### Plugin bundle

The current multi-Skill installable artifact follows the OpenAI Plugin contract:

```text
amazon-japan-creative-workflow/
├── .codex-plugin/plugin.json
└── skills/<skill-name>/...
```

`plugin.json` sets `"skills": "./skills/"`. The old private `internal-skills/` discovery layout is forbidden in current artifacts.

### Codex bundle

The Codex bundle preserves `.agents/skills/<skill-name>/...` and is intended for repository/project installation and source review.

## v0.1.0 disposition

The published v0.1.0 `.skill.zip` is deprecated and unsupported for new multi-Skill installation because its nested Skills were not packaged as an official Plugin. v0.1.0 also used declaration-only source SHA binding. Do not use those properties as evidence of production-ready distribution.

## Independent physical validation

`scripts/validate_release.py` recomputes artifact SHA-256 and byte sizes, validates `SHA256SUMS`, checks required members and `BUILD_INFO.json`, verifies the Plugin manifest, rejects `internal-skills/`, rejects the broken `validate_project_state.py` compatibility shim, rejects legacy-only Skills, unsafe ZIP members/symlinks/repository-only selftests, and selected private/credential markers.

The independent validator validates the physical release directory and its internal provenance metadata. Authentic Git provenance is established by the packager's clean-HEAD verification before artifacts are created.

## Determinism

For the same clean repository tree, version, and verified HEAD, both ZIP archives, the release manifest, and `SHA256SUMS` must be byte-for-byte reproducible.

## Agent-eval publication gate

Deterministic tests do not prove model behavior. Formal v0.1.1 publication requires a real-agent run result covering all ten cases in `evals/agent-pressure/manifest.json`, bound to the intended release commit, with every case `PASS`.

See `docs/agent-pressure-evals.md`.

## Repository-governance publication gate

Formal v0.1.1 publication also requires an explicit live check of `main` protection/ruleset state. A green CI run by itself is not branch protection.

See `docs/main-protection-required.md`.

## Publication boundary

The repository may build release candidates in CI. Formal publication must use an exact merged `main` commit and requires explicit user confirmation after:

1. deterministic full CI passes;
2. Plugin/Codex release artifacts pass independent validation;
3. real-agent pressure evals pass;
4. live governance state is reviewed and meets policy.

No Draft/Open PR head may be published as v0.1.1.

## Legacy packaging

Imported v0.3.3 packagers remain repository compatibility/history code. They are not the M5.1 release contract.
