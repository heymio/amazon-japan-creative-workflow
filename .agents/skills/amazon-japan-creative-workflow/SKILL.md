---
name: amazon-japan-creative-workflow
description: Quality-first Amazon Japan listing strategy, creative production, creative QA, simulator interoperability, and final evidence safeguards.
---

# Amazon Japan Creative Workflow

## Purpose

Turn product evidence into a Japan-localized Amazon.co.jp creative system whose final standard is not merely workflow completeness, but commercially credible assets that remain strong inside the Amazon Japan Shopping App page context.

Normal invocation:

```text
$amazon-japan-creative-workflow
```

The original `heymio/japan-listing-demo` remains a separate upstream baseline and is not modified by this workflow.

## Stage ownership

The Router is intentionally thin. It owns continuity, checkpoints, transitions, bounded retry routing, and targeted exception return; downstream Skills own the work.

```text
Stage 0–7     listing-strategy
Stage 7.5–8   creative-production
Stage 8.4     creative-quality
Stage 8.6–9   listing-simulator-bridge
Stage 9.2     creative-quality
Stage 9.5     creative-production
Stage 10      evidence-hardening + final user acceptance
```

### Stage 0–7 — Strategy depth is mandatory

`listing-strategy` preserves Product Truth, offer/page boundaries, claim readiness, consumer/JTBD/VOC/competitor reasoning, Japan localization, Amazon channel architecture, Message Architecture, complete asset planning, Page Visual System, and Evidence Mode. Creative quality does not excuse shallow strategy.

### Stage 7.5–8 — Quality-first production

`creative-production` converts one locked creative brief at a time into production candidates using narrow source context, the selected production mode, bounded targeted retry, explicit user approval, candidate history, and Selection Lock.

### Stage 8.4 — Creative quality

`creative-quality` evaluates individual asset quality and whole-set narrative/rhythm. Asset PASS never implies Set PASS.

### Stage 8.6–9 — Simulator bridge

`listing-simulator-bridge` exports explicit simulator bindings/import packs and consumes page-context review results. The external Amazon Japan Listing Simulator is the page renderer; this workflow does not maintain a second Amazon HTML renderer.

### Stage 9.2 / 9.5 — Diagnose before rework

`creative-quality` diagnoses page-context defects. `creative-production` reopens only the smallest sufficient asset scope when the diagnosis is execution-level. Strategy gaps return to Stage 0–7 instead of being patched by prompt improvisation.

### Stage 10 — Evidence safeguards

`evidence-hardening` verifies exact final outputs, required-set completeness, approval/provenance, physical identity, claim/source integrity, and final workflow eligibility. Hardening is a safeguard layer, not the creative UX center.

## Transition commands

Clear advancement wording such as `继续`, `下一步`, `go`, `next`, and clear equivalents advances when the current stage contract is complete.

`先这样` is ambiguous pause wording and **does not advance** a major stage by itself.

`这张先过` accepts and locks the exact **current Asset** candidate only. It does not declare the Production stage complete and does not skip remaining required assets, Set QA, simulator review, or final evidence safeguards.

## User checkpoints

Default checkpoint output stays concise:

```text
Done:
Open:
Next:
```

Use detailed state/audit manifests only for `PARTIAL`, `BLOCKED`, explicit audit requests, or final evidence review.

## Context firewall

Strategy may be deep; generation context stays narrow. Production receives only the current Creative Brief, exact required product/UI/proof sources, current Page Visual System direction, relevant neighbor summaries, and approved visual references. Do not inject full project history, failed attempts, gates, auditor narration, or unrelated evidence into image/video generation context.

## Retry discipline

A candidate may receive at most two autonomous targeted correction attempts after the initial generation. A retry requires a concrete diagnosis and preserves unaffected properties. If the same issue survives the retry budget, escalate from execution problem to creative-direction or strategy diagnosis rather than continuing random prompt churn.

## Exception principle

A downstream Skill must not repair an upstream decision by inference. Return the smallest affected decision to its owning stage using `references/exception-routing.md`, preserve approved unaffected outputs, and resume from the prior point after the upstream contract is repaired.

## Completion principle

The workflow is complete only when strategy is complete, required creative assets are approved, asset quality and whole-set quality pass, simulator page-context quality passes, required evidence safeguards pass, and the user accepts the final set.
