# Agent pressure evals

M5.1 separates deterministic case-definition validation from real-agent execution evidence.

## Why

The repository's historical Router and Golden Path tests prove contracts and documentation, not actual model behavior. Textual fixtures must not be treated as proof that a real agent routes correctly under pressure.

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

A valid real-agent result requires all 10 case IDs exactly once and every status `PASS`. Missing results are `UNVERIFIED`, never implicitly passing.

## v0.1.1 publication policy

For v0.1.1, real-agent execution evidence is **recommended production-readiness evidence, not a pilot-publication hard gate**. This avoids requiring a long-lived model API credential solely to publish a pilot-ready artifact.

The pressure cases and validator remain in the repository so the team can run them later in an authenticated Codex/ChatGPT environment. Until an actual runner produces a passing result bound to the evaluated commit, the workflow must not be described as having passed real-agent E2E validation or as fully production-ready on that basis.

## Current M5.1 boundary

Deterministic CI validates the eval definitions and preserves the fail-closed result contract. v0.1.1 may be published as **pilot-ready** once its deterministic artifact checks and repository-governance publication gate pass and the user explicitly approves publication. Real-agent pressure testing remains a recommended pilot follow-up before promoting the workflow to production-ready status.
