---
name: listing-simulator-bridge
description: Use for Stage 8.6–9 Amazon Japan Listing Simulator interoperability after creative asset/set QA.
---

# Listing Simulator Bridge

## Purpose

Translate approved Amazon Japan creative outputs into explicit, deterministic Simulator import contracts and consume page-context review results. This Skill does **not** render Amazon UI or maintain a second HTML demo implementation.

## Ownership

- Stage 8.6: build explicit bindings and Simulator import pack.
- Stage 9: place the current approved creative set into the external Amazon Japan Listing Simulator for page-context review.
- Stage 9.2 diagnosis belongs to `creative-quality`.
- Stage 9.5 targeted rework belongs to `creative-production`.
- Final physical/evidence eligibility belongs to `evidence-hardening`.

## Binding rules

Every known relationship must be explicit. A normal binding requires:

- `asset_id`
- `slot_id`
- project-root-relative `output_ref`
- optional `variation_id`

Content-region bindings additionally carry `content_id`, `module_id`, registry-owned `template_id`, and `slot_key`. The stable content slot key is:

`content:{content_id}:module:{module_id}:slot:{slot_key}`

Never infer a Variation or slot from a filename when the workflow does not know the relationship. Unknown relationships become Pending.

## Stable non-template slots

Gallery and detail slots come from `profiles/amazon-jp/slot-taxonomy.json`. Concrete A+/Brand Story/Shoppable template IDs are registry-driven, not invented by the workflow.

## Variation inheritance

Resolve parent data with variation overrides using semantic keys:

- Gallery/media: `slot_id`
- specifications: specification key
- content assets: `content_id + module_id + slot_key`

Absent fields inherit. Explicit `null` disables the inherited field. Never merge collection entries by list index.

## Active content

One preview may activate one Basic **or** Premium A+ enhanced-description variant, and one Brand Story **or** Shoppable Collections brand-content variant.

## Eligibility boundary

The bridge carries, but does not manufacture, Review/Final eligibility facts:

- `production_freeze_ready`
- `required_asset_set_complete`
- `approved_output_matches`
- `asset_binding_complete`
- `blocking_conflicts`
- `hard_verification_status`

The bridge never upgrades `UNVERIFIED` or `FAIL` hard verification to `PASS`.

## Registry boundary

M3 may use a clearly labeled synthetic registry for contract tests only. Real Simulator template IDs and the actual 43-template registry are integrated only when supplied from the Simulator project and validated in the real-registry milestone.
