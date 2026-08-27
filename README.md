# Amazon Japan Creative Workflow

`amazon-japan-creative-workflow` is an independent, quality-first workflow for Amazon Japan listing strategy, creative production, creative QA, simulator interoperability, final evidence safeguards, and deterministic distribution.

Normal invocation:

```text
$amazon-japan-creative-workflow
```

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

M0 established the independent Router; M1 migrated Stage 0–7 to `listing-strategy`; M2 added `creative-production` and `creative-quality`; M3 added `listing-simulator-bridge`; M4 added fail-closed `evidence-hardening`; M5 defines the deterministic packaging and release-candidate contract.

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
- Build artifacts may be automated; merge, tag, and GitHub Release publication are not automatic.

## Simulator interoperability

M3 exports explicit `asset-slot-contract.json` and derived `listing-simulator-manifest.json` contracts for the external Amazon Japan Listing Simulator. Stable Gallery/detail slots are workflow-owned; A+/Brand Story/Shoppable template IDs are registry-owned. Unbound media becomes Pending rather than being guessed from filenames.

Folder and ZIP packs are deterministic and reject path traversal, absolute/local paths, symlinks, `.env` files, executable JavaScript, duplicate normalized ZIP members, oversized entries, and suspicious compression ratios. The included template registry is **synthetic contract-test data only**; real 43-template registry compatibility remains a real-simulator integration gate.

See [`docs/simulator-integration.md`](docs/simulator-integration.md).

## Final evidence hardening

M4 reconciles four independently owned evidence domains before Final delivery:

- Production Freeze exact required-set and approved-output state;
- `listing-evidence-auditor` exact physical/semantic evidence;
- Simulator binding/import parity;
- exact standalone HTML SHA-256 plus offline browser-runtime evidence at 375 / 390 / 430 px.

The result is `PASS`, `UNVERIFIED`, or `FAIL`. Only `PASS` can set `final_eligible=true`. Review mode remains separate and may continue when unresolved evidence or Pending assets still block Final.

Legacy `listing-hardening` remains for v0.3.3 Delivery State compatibility and regression coverage; current Stage 10 routing uses `evidence-hardening`.

See [`docs/evidence-hardening.md`](docs/evidence-hardening.md).

## Packaging and release candidates

M5 has two primary artifacts:

```text
amazon-japan-creative-workflow-<version>.skill.zip
amazon-japan-creative-workflow-<version>-codex-bundle.zip
```

The one-install archive presents one workflow root and embeds the current routed/support Skills. The Codex bundle preserves `.agents/skills/...` for project-level installation and review.

Both artifacts are deterministic, contain `BUILD_INFO.json`, and are bound to an external release manifest plus `SHA256SUMS`. `scripts/validate_release.py` independently recomputes the physical release contract.

Legacy `japan-listing-demo` and `listing-hardening` source remains in this repository for compatibility but is not shipped in the current default M5 release artifacts.

M5 does not automatically create Git tags or GitHub Releases. See [`docs/release.md`](docs/release.md) and [`docs/install.md`](docs/install.md).

## Baseline and provenance

This repository was created from the exact validated `heymio/japan-listing-demo` v0.3.3 Git tree at commit `67dbb772398af1ff67547b12bb401d96e2a588d8`. It is an independent repository, not a GitHub fork relationship, and does not track upstream automatically.

See [`docs/provenance.md`](docs/provenance.md).

## Current version

`0.1.0`

## License

MIT. See [`LICENSE`](LICENSE).
