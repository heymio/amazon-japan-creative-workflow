---
name: evidence-hardening
description: Use for Stage 10 fail-closed final evidence eligibility after Simulator page-context review and any targeted rework.
---

# Evidence Hardening

## Purpose

Decide whether the exact final Amazon Japan creative set and the exact Simulator export are eligible for Final delivery.

This Skill is a verification layer. It does not create strategy, generate creative, repair assets, choose A+ architecture, render Amazon UI, or maintain a second Simulator implementation.

## Stage ownership

`evidence-hardening` owns Stage 10 final evidence reconciliation and final acceptance support.

It consumes outputs owned elsewhere:

- Production Freeze from `creative-production`;
- exact physical/semantic evidence from `listing-evidence-auditor`;
- explicit bindings and import state from `listing-simulator-bridge`;
- final standalone HTML identity and browser-runtime evidence from the external Simulator/export validation path.

Legacy `listing-hardening` remains only for v0.3.3 Delivery State compatibility and regression coverage. New workflow routing must use `evidence-hardening` for Stage 10.

## Trust boundary

Never trust a caller-authored `PASS` as proof.

In particular:

- `USER_APPROVED` is creative approval, not final evidence verification;
- `asset_id` and filenames are identifiers, not physical identity;
- Simulator `eligibility.hard_verification_status` is an input field to overwrite from recomputed M4 evidence, not an authority;
- Production Freeze `approved_outputs` must reconcile with auditor evidence and Simulator bindings;
- physical SHA-256 and semantic role assurance come from `listing-evidence-auditor`, not from this Skill self-certifying its own output;
- browser/runtime evidence must bind to the exact final HTML SHA-256.

## Required Stage 10 packet

Normal final reconciliation reads:

1. `production_freeze`
   - exact `required_asset_ids`;
   - exact `candidate_id -> output_ref` approved outputs;
   - no blocked/revision-pending assets;
   - set QA final state;
   - `ready_for_hardening: true`.
2. `auditor_evidence`
   - locked required-set gate;
   - real physical SHA-256 evidence;
   - final-consumable `VERIFIED` or `HUMAN_APPROVED` status for every required asset;
   - exact output reference reconciliation.
3. `simulator_manifest`
   - explicit bindings;
   - no Pending assets for Final;
   - no blocking conflicts;
   - required-set and approved-output parity.
4. `final_artifact`
   - exact standalone `.html` path;
   - exact SHA-256.
5. `runtime_evidence`
   - `browser-runtime` validation;
   - exact artifact SHA match;
   - offline execution;
   - zero network/external resource dependencies;
   - 375 / 390 / 430 px mobile checks with no page-level overflow or broken images.

## Review vs Final

Review and Final are separate states.

A project may remain Review-eligible with Pending assets or incomplete semantic evidence so long as the Simulator project itself is structurally available for review. That condition must never be upgraded to Final.

Final requires every Stage 10 check to `PASS`:

- Production Freeze;
- exact asset evidence;
- Simulator binding parity;
- exact final runtime evidence.

Any deterministic contradiction returns `FAIL`. Missing independent/semantic/runtime evidence returns `UNVERIFIED`. Neither state is Final-eligible.

## Machine result

Use `scripts/final_eligibility.py` to recompute:

- `hard_verification_status`: `PASS | UNVERIFIED | FAIL`;
- `review_eligible`;
- `final_eligible`;
- per-domain `checks`;
- `blocking_conflicts`;
- `unverified_reasons`.

`apply_hard_verification()` may copy the recomputed status back into a Simulator manifest. It must never convert an unresolved or failed result into `PASS`.

## Rework boundary

Evidence Hardening diagnoses evidence/identity/contract failures; it does not repair creative.

- execution-level creative defect → Stage 9.5 `creative-production`;
- strategy gap → Stage 0–7 `listing-strategy`;
- binding/import defect → `listing-simulator-bridge`;
- missing independent semantic/physical evidence → `listing-evidence-auditor`.

Preserve unaffected approved assets and use Smallest Sufficient Rework.
