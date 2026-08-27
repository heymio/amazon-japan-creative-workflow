# Team Golden Path

A normal Japan marketing teammate should be able to use one public entry point without understanding internal Skill architecture, file hashes, or validator details.

## Scenario

The user starts with `$amazon-japan-creative-workflow`, supplies current product/GTM/source materials, and targets Amazon.co.jp.

Expected user-visible path:

```text
Upload product/GTM/source materials
↓
Review Product / Offer / Claim baseline
↓
Review Consumer / Market / Japan-localization strategy
↓
Review Amazon page narrative and complete asset set
↓
Review qualified creative candidates
↓
Review whole-set quality
↓
Review Amazon Japan simulator page context
↓
Targeted rework only when diagnosed
↓
Final evidence review and acceptance
```

Expected internal behavior:

- Stage 0–7 routes to `listing-strategy`.
- Stage 7.5–8 routes to `creative-production`.
- Stage 8.4 and 9.2 route to `creative-quality`.
- Stage 8.6–9 routes to `listing-simulator-bridge`.
- Stage 9.5 routes back to targeted `creative-production`.
- Stage 10 routes to `evidence-hardening` plus final user acceptance.
- The external simulator is the only Amazon page renderer.
- The user does not manually invoke internal Skills.
- Normal checkpoints show `Done / Open / Next` rather than governance tables.
- `这张先过` locks the current Asset only; `先这样` does not advance a major stage by itself.
