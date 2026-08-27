# Amazon Japan Creative Workflow

`amazon-japan-creative-workflow` is an independent, quality-first workflow for Amazon Japan listing strategy, creative production, creative QA, simulator interoperability, and final evidence safeguards.

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

M0 established the independent Router; M1 migrated Stage 0–7 to `listing-strategy`; M2 added `creative-production` and `creative-quality`; M3 adds `listing-simulator-bridge` with explicit bindings, Parent/Variation inheritance, Pending-without-guessing behavior, deterministic folder/ZIP import packs, and pack security. Final evidence extraction remains a later milestone.

## Core operating principles

- Deep strategy precedes production.
- Region is not Creative Role; template is not Creative Role.
- One Asset job has one primary shopper task.
- The user should see qualified candidates, not raw first attempts.
- Asset PASS does not imply Set PASS.
- Diagnose before rework; preserve unaffected approved assets.
- The external Amazon Japan Listing Simulator is the only Amazon page renderer.
- Evidence hardening remains fail-closed for final eligibility, but it is not the creative UX center.
- No automatic merge or release.

## Simulator interoperability

M3 exports explicit `asset-slot-contract.json` and derived `listing-simulator-manifest.json` contracts for the external Amazon Japan Listing Simulator. Stable Gallery/detail slots are workflow-owned; A+/Brand Story/Shoppable template IDs are registry-owned. Unbound media becomes Pending rather than being guessed from filenames.

Folder and ZIP packs are deterministic and reject path traversal, absolute/local paths, symlinks, `.env` files, executable JavaScript, duplicate normalized ZIP members, oversized entries, and suspicious compression ratios. The included template registry is **synthetic contract-test data only**; real 43-template registry compatibility is a later real-simulator gate.

See [`docs/simulator-integration.md`](docs/simulator-integration.md).

## Baseline and provenance

This repository was created from the exact validated `heymio/japan-listing-demo` v0.3.3 Git tree at commit `67dbb772398af1ff67547b12bb401d96e2a588d8`. It is an independent repository, not a GitHub fork relationship, and does not track upstream automatically.

See [`docs/provenance.md`](docs/provenance.md).

## Current version

`0.1.0`

## License

MIT. See [`LICENSE`](LICENSE).
