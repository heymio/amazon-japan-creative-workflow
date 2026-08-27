# Exception routing

## Principle

Return the smallest affected decision to its owning stage. Do not repair upstream ambiguity by inference, and do not reopen unrelated approved assets.

## Structured block

```yaml
status: BLOCKED
problem_class: <specific class>
missing_or_invalid_field: <specific field>
return_to: listing-strategy | creative-production | creative-quality | listing-simulator-bridge | evidence-hardening
asset_id: <affected asset when applicable>
reason: <why the current stage cannot proceed safely>
preserve:
  - <unaffected approved asset or contract>
```

## Common routes

- Missing product / offer / claim / shopper-value decision → `listing-strategy`.
- Missing proof object, real UI source, or product-identity source required by the Creative Brief → `listing-strategy` unless the brief itself is sound and only a production source reference is missing.
- Candidate execution defect with valid brief → `creative-production` targeted retry or reopen.
- Whole-set repetition / rhythm defect → `creative-quality` diagnosis, then reopen the smallest required production subset.
- Simulator slot / Variation / content binding ambiguity → `listing-simulator-bridge`; unresolved upstream content ownership returns to `listing-strategy`.
- Physical file / approval / claim-source mismatch → `evidence-hardening`; wrong creative file returns only the affected Asset ID to `creative-production`.

## Escalation ladder

When the same defect survives the allowed targeted retry budget, escalate classification instead of generating indefinitely:

```text
EXECUTION_PROBLEM
→ CREATIVE_DIRECTION_PROBLEM
→ STRATEGY_PROBLEM
```

## Recovery

Legacy/corrupted-project recovery is exception-only. It is not part of the normal creative production path.
