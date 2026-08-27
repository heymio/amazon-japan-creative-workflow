# Amazon Japan Creative Workflow — development install/use

This repository is currently at development version `0.1.0`. The stable packaged distribution and release workflow are rebuilt in M5; until then, use the repository checkout directly rather than the imported v0.3.3 packaging scripts.

## User-facing entry

Invoke only:

```text
$amazon-japan-creative-workflow
```

Current M4 runtime areas:

```text
Stage 0–7       → listing-strategy
Stage 7.5–8     → creative-production
Stage 8.4       → creative-quality
Stage 8.6–9     → listing-simulator-bridge
Stage 9.2       → creative-quality diagnosis
Stage 9.5       → creative-production targeted rework
Stage 10        → evidence-hardening
```

The imported `listing-hardening` remains available only for v0.3.3 Delivery State / legacy Demo compatibility and regression coverage. New projects use `listing-simulator-bridge` as the page-integration layer and `evidence-hardening` as the Final eligibility layer. The external Amazon Japan Listing Simulator is the only intended page renderer.

## Stage 0–7 strategy

`listing-strategy` preserves Product Truth, offer/claim boundaries, consumer/JTBD/VOC/competitor reasoning, Japan localization, message architecture, Amazon IA, complete asset planning, Page Visual System, and Evidence Mode.

For `contract_version: "1.0"`, Stage 4/5 outputs also structure shopper situation/value/proof and assign one of the nine Creative Roles per final asset.

## Creative production

`creative-production` runs one Asset ID at a time from a ready Creative Brief. Default behavior is one strong candidate, not random multi-option generation. It uses provider-agnostic Production Modes, a narrow context firewall, at most two automatic targeted revisions, exact Selection Lock after user approval, and 2–4 asset waves only after 2–3 approved anchors lock the visual language.

Creative approval is not evidence verification.

## Creative quality

`creative-quality` applies:

- Hard Blocker precedence;
- nine-dimension, 100-point diagnostic scoring;
- role-specific minimums;
- deterministic Set QA for structured labels/IDs;
- exact page-context diagnosis families.

Deterministic CI does **not** inspect pixels and claim subjective aesthetics are proven. Semantic scores/observations come from a visual/model evaluator or human review. Final creative acceptance remains human.

## Simulator bridge

`listing-simulator-bridge` validates explicit Asset/Slot/Variation/content bindings, resolves Parent→Variation overrides by semantic keys, and builds deterministic folder or ZIP import packs for the external Amazon Japan Listing Simulator. Unknown media relationships become Pending; filenames are never used to guess slots or variations.

The synthetic registry under the Bridge templates is only for contract tests. Do not treat its IDs as the real Simulator 43-template registry.

## Evidence hardening

`evidence-hardening` recomputes Stage 10 Final eligibility from:

- Production Freeze exact required-set / approved-output state;
- `listing-evidence-auditor` physical SHA-256 + semantic evidence;
- Simulator binding parity and Pending/conflict state;
- exact standalone HTML SHA-256 + browser-runtime evidence.

Final requires `PASS` for Production Freeze, exact asset evidence, Simulator binding, and final runtime. Missing independent/semantic/runtime evidence returns `UNVERIFIED`; deterministic contradictions return `FAIL`. Caller-authored `PASS` fields are never authoritative.

## Current validation

Run:

```bash
python3 scripts/selftest_provenance.py
python3 .agents/skills/amazon-japan-creative-workflow/scripts/selftest_router.py
python3 .agents/skills/listing-strategy/scripts/selftest_strategy.py
python3 .agents/skills/listing-strategy/scripts/selftest_strategy_v010.py
python3 .agents/skills/creative-production/scripts/selftest_creative_brief.py
python3 .agents/skills/creative-production/scripts/selftest_production.py
python3 .agents/skills/creative-production/scripts/selftest_creative_state.py
python3 .agents/skills/creative-quality/scripts/selftest_asset_quality.py
python3 .agents/skills/creative-quality/scripts/selftest_set_quality.py
python3 .agents/skills/creative-quality/scripts/selftest_diagnosis.py
python3 .agents/skills/listing-simulator-bridge/scripts/selftest_contract.py
python3 .agents/skills/listing-simulator-bridge/scripts/selftest_variations.py
python3 .agents/skills/listing-simulator-bridge/scripts/selftest_import_pack.py
python3 .agents/skills/listing-simulator-bridge/scripts/selftest_pack_security.py
python3 .agents/skills/listing-evidence-auditor/scripts/selftest_auditor.py
python3 .agents/skills/listing-hardening/scripts/selftest_hardening.py
python3 .agents/skills/evidence-hardening/scripts/selftest_final_eligibility.py
```

The old v0.3.3 `package_skill.py`, `package_codex_bundle.py`, overlay validation, and embedded Demo distribution remain compatibility/history code until M5 and are not the current development distribution contract.
