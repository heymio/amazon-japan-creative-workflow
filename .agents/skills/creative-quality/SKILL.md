---
name: creative-quality
description: Use for deterministic Creative Quality decision logic and structured semantic QA at Asset, Set, and page-context diagnosis levels.
---

# Creative Quality

## Core question

Does the current creative fulfill its shopper task strongly enough to be recommended for human approval, and does the whole set work as a coherent Amazon Japan page rather than a collection of individually acceptable images?

## Boundary

This Skill does **not** claim that deterministic code can judge aesthetics from pixels. Visual/model evaluators and humans supply semantic observations/scores. Deterministic code then applies the approved Hard Blockers, thresholds, role profiles, repetition rules, and diagnosis taxonomy reproducibly.

## Asset Quality

Nine scored dimensions, maximum total 100:

- Message Clarity — 20
- Visual Proof Strength — 15
- Shopper Value Translation — 15
- Product Prominence & Fidelity — 10
- Scene Credibility — 10
- Japan Localization — 10
- Visual Hierarchy & Composition — 10
- Commercial Polish — 5
- Mobile Legibility — 5

Hard Blockers override any numeric score. General recommendability requires total >=85 and Message Clarity >=16, with stricter role-specific minimums where defined.

Numeric scores are triage/diagnosis aids, not proof of subjective quality. Final creative acceptance remains human.

## Set Quality

Asset PASS does not imply Set PASS. Set QA separately checks narrative progression, message coverage/redundancy, composition rhythm, scene/proof diversity, information-density rhythm, product-scale rhythm, cohesion, and Japan consistency.

## Page-context diagnosis

Simulator review findings are normalized into exact diagnosis families and fed back to Creative Production for Smallest Sufficient Rework. Strategy gaps route upstream; local execution defects remain local.

## Deterministic Set rules

The executable Set layer can deterministically flag:

- three consecutive identical `composition_family` labels;
- three consecutive identical `shopper_task` labels;
- missing visual support for an explicitly `P0` message;
- exact message-ID repetition at the same depth;
- product-identity mismatch flags supplied by hardening;
- three consecutive `high` information-density labels;
- low A+ incremental value when A+ repeats Gallery message IDs at equal depth.

It does not use pixel hashes as a proxy for visual variety.

## Diagnosis taxonomy

Exact page-context diagnosis families:

`ASSET_DEFECT` / `MESSAGE_REDUNDANCY` / `VISUAL_REPETITION` / `PAGE_RHYTHM` / `MOBILE_LEGIBILITY` / `ROLE_OVERLAP` / `ART_DIRECTION_DRIFT` / `STRATEGY_GAP`

Every normalized diagnosis must record the observed problem, root cause, affected assets, preserved assets, exact change, and expected improvement. This is the contract for Smallest Sufficient Rework.
