# v0.1.1 Release Candidate Notes

Status: release candidate only. Do not publish until the real-agent and repository-governance gates are satisfied and the user explicitly confirms publication.

## M5.1 fixes

### Official multi-Skill distribution

- Replaces the unsupported v0.1.0 `.skill.zip` multi-Skill layout with an OpenAI Plugin bundle.
- Adds `.codex-plugin/plugin.json` with `"skills": "./skills/"`.
- Packages all current runtime/support Skills under `skills/<skill-name>/`.
- Keeps the Codex bundle with `.agents/skills/` for repository/project installation.
- Forbids the old `internal-skills/` discovery layout in current artifacts.

### Git-derived release provenance

- Derives the authoritative release SHA from `git rev-parse HEAD`.
- Rejects an expected/source SHA that differs from HEAD.
- Rejects dirty tracked Git state.
- Records only the verified clean HEAD in `BUILD_INFO.json` and the release manifest.

### Current artifact cleanup

- Excludes `amazon-japan-creative-workflow/scripts/validate_project_state.py` from Plugin and Codex current artifacts because its `listing-hardening` dependency is intentionally legacy-only.

### Agent pressure eval readiness

- Adds ten pressure cases covering transition commands, current-asset lock semantics, ambiguous pause wording, evidence gaps, strategy rollback, targeted rework, Simulator Pending, fail-closed hardening, long-context routing, and a cross-Skill Golden Path.
- Deterministic CI validates the case definitions only.
- A real-agent PASS result bound to the intended release commit remains mandatory before publication.

### Repository governance

- Adds read-only governance observation tooling.
- Does not claim `main` is protected until GitHub live state reports protection/ruleset coverage.

## v0.1.0 deprecation

The v0.1.0 `.skill.zip` is unsupported for new multi-Skill installations. v0.1.0 remains historical; use the v0.1.1 Plugin bundle after publication, or use the Codex bundle/repository checkout for pilot work.

## Unchanged business architecture

M0–M4 workflow ownership, creative QA, Simulator bridge semantics, and fail-closed evidence hardening are unchanged by M5.1.
