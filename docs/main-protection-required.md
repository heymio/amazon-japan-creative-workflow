# Main protection requirement

At the start of M5.1, GitHub reports `main` as `protected: false` and the repository rulesets collection is empty. This is a release-readiness gap, not a solved condition.

## Required v0.1.1 ruleset

Before v0.1.1 production publication, create an **Active branch ruleset** targeting `main` (or the default branch) with all of the following protections:

1. **Require a pull request before merging** (`pull_request`).
   - A PR is mandatory; ordinary direct pushes to `main` must not be the normal path.
   - If this repository has no independent reviewer, required approving reviews may remain `0`; otherwise prefer at least `1` approval.
2. **Require status checks before merging** (`required_status_checks`).
   - Required context: `validate`.
   - Required source: GitHub Actions app ID `15368`.
   - The latest observed successful `validate` check on `main` is produced by that GitHub Actions app.
3. **Block force pushes** (`non_fast_forward`).
4. **Block deletion** (`deletion`).
5. Enforcement must be **Active**. `Evaluate` or `Disabled` does not satisfy the production gate.

An explicitly documented break-glass bypass may be retained only if necessary. The release gate must not treat an arbitrary matching ruleset, an Evaluate ruleset, or the branch API's `protected: true` boolean alone as sufficient evidence.

## Verification

`scripts/check_github_governance.py` validates detailed ruleset contents, not only their existence. It returns PASS only when at least one Active ruleset targeting `main` contains all four required rule types and binds the `validate` status check to GitHub Actions app `15368`.

`.github/workflows/check-governance.yml` fetches live branch metadata plus full ruleset details and runs the checker fail-closed.

M5.1 code and CI may inspect and report this live state, but must never claim repository governance is ready merely because ordinary CI is green. The current ChatGPT GitHub connector exposes repository-administration reads but not writes, so enabling the ruleset remains a repository setting action until the live GitHub API reports the required state.
