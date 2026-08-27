# Amazon Japan Creative Workflow — install/use

Current version: `0.1.0`.

## User-facing entry

Invoke only:

```text
$amazon-japan-creative-workflow
```

Current runtime areas:

```text
Stage 0–7       → listing-strategy
Stage 7.5–8     → creative-production
Stage 8.4       → creative-quality
Stage 8.6–9     → listing-simulator-bridge
Stage 9.2       → creative-quality diagnosis
Stage 9.5       → creative-production targeted rework
Stage 10        → evidence-hardening
```

`listing-evidence-auditor` is a support Skill used for independent exact-file evidence. It is not a separate user-facing workflow.

The imported `listing-hardening` remains available in the repository only for v0.3.3 Delivery State / legacy Demo compatibility and regression coverage. New projects use `listing-simulator-bridge` as the page-integration layer and `evidence-hardening` as the Final eligibility layer. The external Amazon Japan Listing Simulator is the only intended page renderer.

## Installation options

### One-install Skill ZIP

Build or obtain:

```text
amazon-japan-creative-workflow-0.1.0.skill.zip
```

It contains one root Skill, `amazon-japan-creative-workflow`, with current runtime/support Skills embedded internally. Use this form where a single installed workflow entry is preferred.

### Codex project bundle

Build or obtain:

```text
amazon-japan-creative-workflow-0.1.0-codex-bundle.zip
```

Extract it at the project root so the `.agents/skills/` structure is preserved. This form is intended for repository-level use and source review.

Both artifacts carry `BUILD_INFO.json` with exact version/source-commit metadata. Validate physical artifacts against the external release manifest and `SHA256SUMS`.

## Build a release candidate

From the exact source commit:

```bash
python3 scripts/package_release.py \
  --source-commit <40-character-git-sha> \
  --output-dir dist
python3 scripts/validate_release.py dist
```

See `docs/release.md` for the publication boundary. Building a release candidate does not create a GitHub Release or tag.

## Stage 0–7 strategy

`listing-strategy` preserves Product Truth, offer/claim boundaries, consumer/JTBD/VOC/competitor reasoning, Japan localization, message architecture, Amazon IA, complete asset planning, Page Visual System, and Evidence Mode.

For `contract_version: "1.0"`, Stage 4/5 outputs also structure shopper situation/value/proof and assign one of the nine Creative Roles per final asset.

## Creative production

`creative-production` runs one Asset ID at a time from a ready Creative Brief. Default behavior is one strong candidate, not random multi-option generation. It uses provider-agnostic Production Modes, a narrow context firewall, at most two automatic targeted revisions, exact Selection Lock after user approval, and 2–4 asset waves only after 2–3 approved anchors lock the visual language.

Creative approval is not evidence verification.

## Creative quality

`creative-quality` applies Hard Blocker precedence, role-specific thresholds, whole-set QA, and page-context diagnosis. Deterministic CI does not claim subjective pixel aesthetics are proven; semantic visual judgment remains model/human evaluation.

## Simulator bridge

`listing-simulator-bridge` validates explicit Asset/Slot/Variation/content bindings, resolves Parent→Variation overrides by semantic keys, and builds deterministic folder or ZIP import packs for the external Amazon Japan Listing Simulator. Unknown media relationships become Pending; filenames are never used to guess slots or variations.

The synthetic registry under the Bridge templates is only for contract tests. Do not treat its IDs as the real Simulator 43-template registry.

## Evidence hardening

`evidence-hardening` recomputes Stage 10 Final eligibility from Production Freeze, `listing-evidence-auditor`, Simulator binding parity, and exact standalone HTML browser-runtime evidence. Missing independent/semantic/runtime evidence returns `UNVERIFIED`; deterministic contradictions return `FAIL`. Caller-authored `PASS` fields are never authoritative.

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
python3 scripts/selftest_release_packaging.py
```

The old v0.3.3 `package_skill.py`, old `scripts/package_codex_bundle.py`, overlay validation, and embedded legacy Demo distribution remain compatibility/history code and are not the current M5 release contract.
