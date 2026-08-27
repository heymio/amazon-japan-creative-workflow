# v0.1.0 Release Candidate Notes

Status: release candidate documentation only. No Git tag or GitHub Release has been created by M5.

## Workflow architecture

- M0: independent `amazon-japan-creative-workflow` Router baseline.
- M1: Stage 0–7 `listing-strategy` and versioned strategy/creative contracts.
- M2: quality-first `creative-production` + `creative-quality`, bounded targeted revision, Selection Lock, anchor-first waves, Asset QA and Set QA.
- M3: `listing-simulator-bridge`, explicit Asset/Slot/Variation/content bindings, deterministic Simulator import packs, Pending-without-guessing behavior, and import-pack security.
- M4: fail-closed Stage 10 `evidence-hardening` with exact-output, auditor, Simulator-binding, and runtime evidence reconciliation.
- M5: deterministic release candidate packaging and independent release validation.

## Current default distribution

User-facing invocation:

```text
$amazon-japan-creative-workflow
```

Runtime Skills:

- `amazon-japan-creative-workflow`
- `listing-strategy`
- `creative-production`
- `creative-quality`
- `listing-simulator-bridge`
- `evidence-hardening`

Support Skill:

- `listing-evidence-auditor`

Legacy compatibility source retained in the repository but excluded from the current default release artifacts:

- `japan-listing-demo`
- `listing-hardening`

## Release candidate artifacts

- `amazon-japan-creative-workflow-0.1.0.skill.zip`
- `amazon-japan-creative-workflow-0.1.0-codex-bundle.zip`
- `amazon-japan-creative-workflow-0.1.0-release-manifest.json`
- `SHA256SUMS`

Artifacts are deterministic for the same repository tree, version, and source commit. `BUILD_INFO.json` binds each ZIP to the exact release identity.

## Publication boundary

This release candidate does not automatically create or modify:

- Git tags;
- GitHub Releases;
- release assets on GitHub Releases;
- protected branches;
- merged PR state.

Formal publication remains a separate explicit user-approved action after the release PR is merged and the final `main` commit is revalidated.
