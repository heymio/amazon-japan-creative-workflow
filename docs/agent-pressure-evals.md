# Agent pressure evals

M5.1 separates deterministic case-definition validation from real-agent execution evidence.

## Why

The repository's historical Router and Golden Path tests prove contracts and documentation, not actual model behavior. A release must not treat textual fixtures as proof that a real agent routes correctly under pressure.

## Cases

`evals/agent-pressure/manifest.json` defines exactly 10 pressure cases covering transition commands, current-asset locking, ambiguous pause wording, missing evidence, strategy rollback, targeted Set-QA rework, Simulator Pending, fail-closed hardening, long-context routing stability, and a cross-Skill Golden Path.

Run deterministic definition validation with:

```bash
python3 scripts/validate_agent_pressure_evals.py
```

This validates coverage and expected structured assertions only.

## Real-agent result contract

A real run must write a separate JSON result artifact and must not modify the source case manifest:

```json
{
  "schema_version": "1.0",
  "source_commit": "40-character-git-sha",
  "model": "exact-model-or-agent-identifier",
  "runner": "codex-or-chatgpt",
  "cases": [
    {
      "case_id": "advance-clear-continue",
      "status": "PASS",
      "evidence": "Observed route/transition behavior and concise rationale."
    }
  ]
}
```

A formal v0.1.1 publication gate requires all 10 case IDs exactly once and every status `PASS`. Missing results are `UNVERIFIED`, never implicitly passing.

## Current M5.1 boundary

The deterministic CI added by M5.1 validates the eval definitions and preserves the contract for a real Codex/ChatGPT run. Until an actual runner produces a passing result bound to the intended release commit, v0.1.1 remains a release candidate rather than a production-ready publication.
