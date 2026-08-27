# Amazon Japan Creative Workflow

`amazon-japan-creative-workflow` is an independent, quality-first workflow for Amazon Japan listing strategy, creative production, creative QA, simulator interoperability, final evidence safeguards, and deterministic distribution.

Normal invocation:

```text
$amazon-japan-creative-workflow
```

## Current status

Current development/release-candidate version: `0.1.1`.

**Important:** the published v0.1.0 `amazon-japan-creative-workflow-0.1.0.skill.zip` is deprecated and unsupported as a reliable multi-Skill installation method. It embedded downstream Skills under a private `internal-skills/` layout that is not the current OpenAI Plugin discovery contract. Do not use that artifact for new installations.

M5.1 replaces it with an official Plugin layout and keeps the Codex project bundle/repository checkout as supported pilot paths. v0.1.1 is not ready for formal publication until the real-agent pressure-eval and live repository-governance gates are satisfied.

## Why this exists

High-quality Amazon creative starts before image generation. The workflow preserves deep Product Truth, offer/claim boundaries, consumer/JTBD/VOC/competitor reasoning, Japan localization, message architecture, Amazon page planning, complete asset planning, Page Visual System, and Evidence Mode, then makes creative quality the Stage 7.5+ center of gravity.

## Stage topology

```text
Stage 0–7     listing-strategy
Stage 7.5–8   creative-production
Stage 8.4     creative-quality
Stage 8.6–9   listing-simulator-bridge
Stage 9.2     creative-quality diagnosis
Stage 9.5     creative-production targeted rework
Stage 10      evidence-hardening + final acceptance
```

M0 established the Router; M1 migrated Stage 0–7 to `listing-strategy`; M2 added `creative-production` and `creative-quality`; M3 added `listing-simulator-bridge`; M4 added fail-closed `evidence-hardening`; M5 added deterministic release packaging; M5.1 hardens distribution/provenance and release readiness.

## Core operating principles

- Deep strategy precedes production.
- Region is not Creative Role; template is not Creative Role.
- One Asset job has one primary shopper task.
- The user should see qualified candidates, not raw first attempts.
- Asset PASS does not imply Set PASS.
- Diagnose before rework; preserve unaffected approved assets.
- The external Amazon Japan Listing Simulator is the only Amazon page renderer.
- Evidence hardening remains fail-closed for Final eligibility, but it is not the creative UX center.
- Caller-authored `PASS` flags never substitute for recomputed exact-output evidence.
- Release provenance is derived from a verified clean Git HEAD; a caller-provided SHA is only a constraint.
- Build artifacts may be automated; merge and formal publication remain explicit user checkpoints.

## Distribution

M5.1 has two primary artifacts:

```text
amazon-japan-creative-workflow-<version>-plugin.zip
amazon-japan-creative-workflow-<version>-codex-bundle.zip
```

The Plugin bundle follows OpenAI's multi-Skill layout:

```text
amazon-japan-creative-workflow/
├── .codex-plugin/plugin.json
└── skills/<skill-name>/...
```

The Codex bundle preserves `.agents/skills/...` for repository/project installation and source review. Both artifacts contain `BUILD_INFO.json`, are reproducible for the same clean Git HEAD, and are validated against the external release manifest plus `SHA256SUMS`.

Legacy `japan-listing-demo` and `listing-hardening` remain repository compatibility source only. The broken legacy `validate_project_state.py` shim is excluded from current release artifacts.

See [`docs/install.md`](docs/install.md) and [`docs/release.md`](docs/release.md).

## Simulator interoperability

M3 exports explicit Asset/Slot/Variation/content binding contracts for the external Amazon Japan Listing Simulator. Unknown media relationships become Pending rather than being guessed from filenames. The included template registry remains **synthetic contract-test data only**; real 43-template registry compatibility is a separate pilot gate.

See [`docs/simulator-integration.md`](docs/simulator-integration.md).

## Final evidence hardening

M4 reconciles Production Freeze, exact physical/semantic evidence, Simulator binding parity, and exact standalone HTML browser-runtime evidence. Only hard-verification `PASS` can set `final_eligible=true`; unresolved evidence remains `UNVERIFIED`.

See [`docs/evidence-hardening.md`](docs/evidence-hardening.md).

## Agent pressure evals

M5.1 defines ten pressure cases for transitions, current-asset approval, ambiguity, evidence gaps, rollback, targeted rework, Simulator Pending, fail-closed hardening, long-context routing, and a cross-Skill Golden Path. Deterministic CI validates the cases but does **not** pretend that fixtures prove real model behavior. Formal v0.1.1 publication requires an actual passing agent-run result bound to the intended release commit.

See [`docs/agent-pressure-evals.md`](docs/agent-pressure-evals.md).

## Baseline and provenance

This repository was created from the exact validated `heymio/japan-listing-demo` v0.3.3 Git tree at commit `67dbb772398af1ff67547b12bb401d96e2a588d8`. It is an independent repository, not a GitHub fork relationship.

## License

MIT. See [`LICENSE`](LICENSE).
