# Amazon Japan Creative Workflow — install/use

Current development/release-candidate version: `0.1.1`.

## User-facing entry

Invoke only:

```text
$amazon-japan-creative-workflow
```

Runtime ownership remains:

```text
Stage 0–7       → listing-strategy
Stage 7.5–8     → creative-production
Stage 8.4       → creative-quality
Stage 8.6–9     → listing-simulator-bridge
Stage 9.2       → creative-quality diagnosis
Stage 9.5       → creative-production targeted rework
Stage 10        → evidence-hardening
```

`listing-evidence-auditor` is a support Skill. `listing-hardening` remains repository-only compatibility source for v0.3.3 and is not part of the current default distribution.

## v0.1.0 warning

Do **not** use `amazon-japan-creative-workflow-0.1.0.skill.zip` for new multi-Skill installations. That artifact embedded downstream Skills under `internal-skills/`, which is not the current OpenAI Plugin discovery layout.

For v0.1.0 pilot work, prefer the Codex bundle or repository checkout and treat release provenance as affected by the v0.1.0 declaration-only SHA issue.

## M5.1 installation options

### Plugin bundle — primary multi-Skill installable form

Build or obtain:

```text
amazon-japan-creative-workflow-0.1.1-plugin.zip
```

The archive contains:

```text
amazon-japan-creative-workflow/
├── .codex-plugin/plugin.json
├── skills/<skill-name>/...
├── contracts/...
├── profiles/...
└── BUILD_INFO.json
```

The Plugin manifest points at `./skills/`, so ChatGPT/Codex plugin installation can discover the related Skill group as one installable experience.

### Codex project bundle

Build or obtain:

```text
amazon-japan-creative-workflow-0.1.1-codex-bundle.zip
```

Extract it at the project root so `.agents/skills/` is preserved. This remains the recommended repository-level pilot path and the easiest form for source inspection.

### Repository checkout

The repository itself remains the source of truth for development and pilot work.

## Build a release candidate

The builder requires a clean tracked Git tree and derives provenance from the actual current HEAD. An optional `--source-commit` is a constraint that must equal HEAD; it is not trusted as the source of truth.

```bash
python3 scripts/package_release.py \
  --source-commit "$(git rev-parse HEAD)" \
  --output-dir dist
python3 scripts/validate_release.py dist
```

The build fails if the expected SHA differs from HEAD or tracked files are dirty.

## Pilot release readiness

A green deterministic build is necessary but not sufficient for v0.1.1 publication. The hard publication gates are:

- live GitHub `main` protection/ruleset review must PASS;
- explicit user publication approval.

The ten-case real-agent pressure eval remains a recommended post-release/pilot validation before describing the workflow as production-ready. It is not a v0.1.1 publication blocker, and missing real-agent evidence must remain visible as `UNVERIFIED` rather than being represented as PASS.

See `docs/agent-pressure-evals.md`, `docs/main-protection-required.md`, and `docs/release.md`.

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
python3 scripts/selftest_release_reliability.py
python3 scripts/validate_agent_pressure_evals.py
```

The old v0.3.3 packagers remain compatibility/history code and are not the current M5.1 distribution contract.
