---
name: creative-production
description: Use for Stage 7.5–8 and Stage 9.5 quality-first Amazon Japan creative production from an approved Stage 7 asset plan.
---

# Creative Production

## Core question

Turn one approved Stage 7 asset role into one commercially credible candidate while preserving product truth, shopper task, Japan context, and page-level art direction.

## Ownership

This Skill owns Stage 7.5 Creative Brief, Stage 8 candidate production/selection, and Stage 9.5 targeted rework. It does not reinterpret Stage 0–7 strategy, score subjective creative quality as fact, render the Amazon page, or perform final evidence hardening.

## Artifact-first mode

Once production starts, return the requested final artifact first and a concise creative status second. Do not replace the requested asset with project-management narration. Execute **one Asset Packet** / one Asset ID at a time unless a controlled wave has been explicitly unlocked.

Creative status vocabulary remains intentionally small:

`PLANNED` / `READY` / `REVIEW` / `REVISE` / `USER_APPROVED` / `BLOCKED`

**Creative Approval ≠ Evidence Verification.** `USER_APPROVED` records the human creative decision; later Evidence Hardening still owns physical identity and delivery safety.

## Required production sequence

For each Asset ID:

1. validate the Creative Brief;
2. choose a provider-agnostic Production Mode;
3. build the narrow generation/editing context;
4. produce one strong candidate by default;
5. run Creative Quality critique before human review;
6. make at most two automatic targeted revisions for diagnosed execution defects;
7. present only qualified/reviewable candidates to the user;
8. lock the exact selected candidate/output after user approval.

Do not substitute random multi-candidate generation for diagnosis.

## Creative Brief readiness

A production-ready brief requires:

- `asset_id`
- `region`
- `creative_role`
- `shopper_task`
- `primary_message`
- `user_value`
- `usage_scene`
- `proof_object`
- `desired_takeaway`
- `must_show`
- `must_not_show`

A missing proof object, unsupported role, missing authoritative source, or scene that cannot support the shopper value is an upstream/brief problem, not a prompt-retry problem.

## Production Modes

The exact provider-agnostic modes are:

- `SOURCE_COMPOSITE`
- `GENERATIVE_SCENE`
- `PROOF_COMPOSITE`
- `UI_COMPOSITE`
- `DESIGN_LAYOUT`
- `SOURCE_FAITHFUL_EDIT`
- `MOTION_PRODUCTION`

Real product/UI sources remain authoritative. Do not ask an image model to invent product structure or application UI when an authoritative source is required.

## Narrow production context

The normal generation/editing packet contains only:

- current `creative_brief`;
- `product_identity_sources`;
- `ui_sources`;
- current `page_visual_direction`;
- `nearest_neighbors` summaries;
- `japan_scene_constraints`;
- `evidence_mode`.

Reject Delivery State, gate results, full research history, unrelated asset candidates, and other control-plane material from generation context.

**Deep strategy; narrow production context.**

## Candidate policy

Default to one strong candidate. Directional A/B exploration is reserved for genuine creative-direction uncertainty or explicit user request. Automatic revision is targeted to a diagnosed defect and is capped at two revisions per Asset ID.

## Human approval and Selection Lock

Per-asset human approval remains mandatory. After approval, preserve the exact `candidate_id` and `current_output_ref`. Do not silently replace an approved output. Rework after approval requires an explicit reopen event and keeps prior history.

## Anchor-first controlled batching

Do not batch the remaining set before 2–3 designated anchor assets establish and lock the visual language. Once locked, use 2–4 asset waves. Brand language may remain consistent; layout/composition must not become a repeated template.

## Evidence Mode

Continue using `SOURCE_FAITHFUL`, `CREATIVE_MOCK`, or `PROOF_VISUAL` from Strategy. Creative approval is not factual/evidence verification.

## Rework routing

Execution defects may receive targeted revisions. Missing proof, unsupported claim, wrong shopper task, or strategy gap returns upstream instead of spending the retry budget. Page-context rework follows Smallest Sufficient Rework: preserve already-good assets and change only the smallest affected scope.
