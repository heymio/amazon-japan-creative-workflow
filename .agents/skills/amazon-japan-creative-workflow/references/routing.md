# Routing contract

## Stage map

- 0–7 → `listing-strategy`
- 7.5–8 → `creative-production`
- 8.4 → `creative-quality`
- 8.6–9 → `listing-simulator-bridge`
- 9.2 → `creative-quality`
- 9.5 → `creative-production`
- 10 → `evidence-hardening` plus final user acceptance

## Formal state flow

```text
Project Brief / Product Truth
        ↓
Creative Strategy Kernel / Message Architecture
        ↓
Production Handoff / Complete Asset Set / Page Visual System
        ↓
Creative Brief / Candidate Ledger / Selection Lock
        ↓
Asset Quality + Set Quality
        ↓
Simulator Binding + Import Pack + Page-context QA
        ↓
Targeted Diagnosis / Smallest-sufficient Rework
        ↓
Final Evidence State / Final User Acceptance
```

## Ownership rules

`listing-strategy` owns strategy, product/offer/claim facts, shopper value, Japan localization, page architecture, and required asset roles. Production cannot invent missing upstream decisions.

`creative-production` owns how a locked creative brief is executed and revised. It does not rewrite the message architecture to rescue a weak brief.

`creative-quality` owns creative diagnosis. It can block or reopen work but does not generate replacement assets itself.

`listing-simulator-bridge` owns interop contracts, not Amazon UI rendering.

`evidence-hardening` owns final evidence eligibility, not art direction.

## User-facing continuity

Users normally invoke only `$amazon-japan-creative-workflow`. Internal Skills are routing targets, not separate required user workflows.
