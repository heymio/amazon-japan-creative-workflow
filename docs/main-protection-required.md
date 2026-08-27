# Main protection requirement

At the start of M5.1, GitHub reports `main` as `protected: false` and the repository rulesets collection is empty. This is a release-readiness gap, not a solved condition.

Target state before v0.1.1 production publication:

- merge through pull request;
- require the Amazon Japan Creative Workflow validation check to pass before merge;
- prohibit ordinary direct pushes to `main`;
- require at least one approval when repository plan/settings support it;
- retain an explicitly documented break-glass path only if necessary.

M5.1 code and CI may inspect and report this live state, but must never claim branch protection is enabled merely because CI is green. The current ChatGPT GitHub connector does not expose repository-administration writes, so enabling protection remains a separate repository setting action until the GitHub API reports the target state.
