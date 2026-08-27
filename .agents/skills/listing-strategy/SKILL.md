---
name: listing-strategy
description: Use for Stage 0–7 of an Amazon Japan creative project: product/offer truth, consumer and usage understanding, Japan localization, message architecture, channel/page narrative, and the Complete Asset Set handed to creative production.
---

# Listing Strategy

## Core question

What should we build, for which shopper situation, and why should each planned asset exist?

## Plane boundary

This Skill owns **Stage 0–7 only**. It may be analytically deep, but it does not produce final visual assets, run page-context simulator QA, or perform final delivery hardening.

## Strategic responsibilities

Preserve the full planning depth of the validated v0.3.3 baseline:

- Project Definition and offer/page boundaries;
- source authority, freshness and conflict handling;
- Product Truth and claim readiness;
- Consumer Strategy, JTBD, pains, barriers, benefits and reasons to believe;
- VOC and competitor analysis;
- Japan market and localization reasoning;
- channel capability and frontend-reference planning;
- Message Architecture;
- Gallery, A+, Brand Story / brand-content and video narrative planning;
- module availability, module budget, `CONTENT_COVERAGE`, and `MODULE_FIT_GATE`;
- Complete Asset Set accounting;
- Page Visual System;
- one Evidence Mode per final asset;
- reusable account-level capability evidence when supplied and still valid.

Deep strategy stays upstream. Downstream receives compact, explicit contracts rather than research history.

## Stage 0–3 — Truth and decision boundary

Lock project scope, sources, Product Truth, offer/page boundary, claims, unresolved conflicts and the decisions that materially constrain later creative work. Strategy must not convert an inference or recommendation into a confirmed project fact.

## Stage 4 — User & Usage Understanding

For each important purchase reason model a concrete chain:

```text
User
→ Situation
→ Trigger
→ Friction
→ Desired Outcome
→ Usage Scene
```

The result must be specific enough to become a scene, proof task or objection-handling task. Generic statements such as “smart-home users want convenience” are insufficient.

For `contract_version: "1.0"`, the Creative Strategy Kernel records these fields under `user_usage_understanding`.

## Stage 4.2 — Japan Localization

Use four explicit layers:

```text
Functional Localization
Scene / Behavior Localization
Message / Copy Localization
Visual Localization
```

Japan localization asks whether the product use, environment, shopper behavior, copy framing and visual treatment are plausible in Japanese consumer life. Japanese text or decorative Japan-looking objects alone do not establish localization.

Keep market assumptions evidence-backed. Localization never changes Product Truth, offer scope, measured performance or claim readiness.

## Stage 5 — Message Architecture

Map each major message through:

```text
Feature
→ Shopper Value
→ Usage Situation
→ Proof
→ Creative Expression
```

For `contract_version: "1.0"`, each message-level row carries:

- `message`;
- `user_value`;
- `usage_scene`;
- `proof_object`;
- `desired_takeaway`;
- `visualizable`;
- `amazon_role`;
- `priority`.

Distinguish copy-only information, visual proof, and scene dramatization instead of forcing every message into the same visual pattern.

## Stage 5.5 — Amazon Japan Channel Mapping

Plan against verified platform capability, account capability and current frontend reference evidence. Keep separate:

- platform capability;
- account capability;
- frontend visual evidence;
- brand-controlled regions;
- platform-controlled regions.

Ratings, sponsored blocks, recommendations, purchase controls and other platform-generated regions are not brand creative ownership unless current evidence shows otherwise.

## Stage 6 — Page IA / Shopper Narrative

Design independent reading jobs for:

- Gallery — fast product understanding and fast persuasion;
- A+ — deeper explanation, proof and objection removal;
- Brand Story / brand-content — brand trust, portfolio logic and ecosystem context;
- video — sequence, mechanism, interaction or behavior when motion adds shopper value.

`Message != Module`. Gallery and enhanced-content roles remain separate production requirements even when they cover the same topic.

## Stage 6.5 — Source Asset Intake

Use lightweight Source Asset Intake for fresh projects. A **full project-wide audit is not mandatory** here.

Inventory source assets needed later, such as real product renders/photos, UI sources, packaging, mechanism diagrams, brand assets, visual references and frontend captures.

### Targeted early audit

Use a **targeted early audit** only when inheriting or reusing a **previously approved exact asset**. Do not turn fresh-project Stage 6.5 into full evidence reconciliation before final creative exists.

## Stage 7 — Creative Strategy + Complete Asset Planning

Stage 7 produces four principal artifacts:

1. **Creative Strategy Kernel** — target user/JTBD, tension, promise, purchase reasons, proof principles, Japan implications, visual direction and anti-patterns.
2. **Amazon Page Narrative** — reading/swiping logic across Gallery, A+ and brand content.
3. **Complete Asset Set** — every final required visual role has a stable Asset ID or an explicit blocked dependency.
4. **Page Visual System** — planned variation in scene/composition/tone/product scale/proof form without losing overall brand cohesion.

### Complete Asset Set contract

For `contract_version: "1.0"`, each current Asset ID records:

```text
asset_id
region
slot
shopper_task
primary_message
user_value
usage_scene
proof_object
evidence_mode
creative_role
media_type
variation_id (when applicable)
```

`region != creative_role` and `media_type != creative_role`. An A+ module is a page region/template choice, not a Creative Role.

The nine formal Creative Roles are:

- `HERO_POSITIONING`;
- `DIFFERENTIATOR_PROOF`;
- `MECHANISM_PROOF`;
- `LIFESTYLE_USE_CASE`;
- `COMPARISON_DECISION`;
- `ECOSYSTEM_COMPATIBILITY`;
- `SPEC_INSTALLATION`;
- `OBJECTION_HANDLING`;
- `BRAND_STORY`.

### Completion rule

**Priority proof coverage does not make the Complete Asset Set complete.** P0/differentiator proof is necessary when the strategy calls for it, but every final required role still needs an Asset ID or an explicit `BLOCKED` dependency.

Gallery and enhanced-content assets remain separate production roles unless explicit reuse or derivative intent was planned upstream.

### Parent / Variation planning

When the listing family contains variations, declare stable `variation_id` values once and reference them explicitly from Asset rows. A Parent asset has no `variation_id` (or null). Never infer final Variation assignment from filenames.

### Page Visual System

For each current Asset ID record:

- `visual_role`;
- `scene_family`;
- `composition_family`;
- `tone`;
- `product_scale`;
- `proof_form`;
- optional `neighbor_contrast_note` when adjacent repetition is intentional.

**Same art direction ≠ same composition.** Adjacent assets must not accidentally repeat the same scene/composition/tone/product-scale/proof-form combination merely to preserve brand consistency.

### Evidence Mode

Each current final asset carries exactly one:

- `SOURCE_FAITHFUL` — exact product/pack/offer identity is intrinsic to the role;
- `CREATIVE_MOCK` — lifestyle/atmosphere/spatial representation; generated details do not become Product Truth;
- `PROOF_VISUAL` — factual installation/dimension/interface/mechanism/UI/compatibility proof requiring suitable authoritative evidence.

`source insufficiency != automatic creative rework`. Missing source evidence may reduce entitlement for a Creative Mock, while a Proof Visual may be `BLOCKED` if its proof source is unavailable.

### Scope revisions

If the required set changes after the initial Stage 7 handoff, record a concise `scope_revision` + `scope_delta` rather than silently mutating it. Current production progress always derives from the current authoritative `asset_set`; unrelated approved assets remain untouched.

## Required handoff

Before leaving Stage 7, produce:

- Project Brief;
- Creative Strategy Kernel;
- Amazon Page Narrative;
- Production Handoff;
- Complete Asset Set;
- Page Visual System;
- Evidence Mode per final asset;
- Parent / Variation declaration when applicable.

The Production Handoff carries only the strategy and production decisions needed downstream. It must not carry rejected attempts, full research history, declared final gates or later hardening state.

## Human checkpoints

Do not add a new user approval checkpoint for every Stage 4/5 field. Preserve major-stage checkpoints; use these structures to improve the quality of the recommendation presented at those checkpoints.
