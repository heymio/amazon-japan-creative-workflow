# Amazon Japan Creative Workflow — development install/use

This repository is currently at development version `0.1.0`. The stable packaged distribution and release workflow are rebuilt in M5; until then, use the repository checkout directly rather than the imported v0.3.3 packaging scripts.

## User-facing entry

Invoke only:

```text
$amazon-japan-creative-workflow
```

Current M2 runtime areas:

```text
Stage 0–7       → listing-strategy
Stage 7.5–8     → creative-production
Stage 8.4       → creative-quality
Stage 9.2       → creative-quality diagnosis
Stage 9.5       → creative-production targeted rework
```

`listing-simulator-bridge` arrives in M3. The imported `listing-hardening` / `listing-evidence-auditor` baseline remains in place until M4 extracts the final `evidence-hardening` Skill. Do not treat the imported v0.3.3 Demo renderer as the new product architecture; the external Amazon Japan Listing Simulator is the only intended page renderer.

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
python3 .agents/skills/listing-evidence-auditor/scripts/selftest_auditor.py
python3 .agents/skills/listing-hardening/scripts/selftest_hardening.py
```

The old v0.3.3 `package_skill.py`, `package_codex_bundle.py`, overlay validation, and embedded Demo distribution remain compatibility/history code until M5 and are not the current development distribution contract.
