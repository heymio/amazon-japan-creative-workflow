# M4 Evidence Hardening

## Boundary

Stage 10 is a verification step after creative production, page-context review, and any targeted rework.

The current workflow uses:

```text
Production Freeze
+ listing-evidence-auditor exact-file evidence
+ listing-simulator-bridge bindings/import state
+ exact final HTML + browser-runtime evidence
        ↓
evidence-hardening
        ↓
PASS / UNVERIFIED / FAIL
```

`evidence-hardening` does not render Amazon UI and does not repair assets. The external Amazon Japan Listing Simulator remains the only page renderer.

## Final checks

Final eligibility requires all four checks to PASS:

1. `production_freeze`
   - exact required Asset ID set;
   - every required Asset ID is user-approved;
   - exact `candidate_id -> output_ref` exists;
   - no blocked/revision-pending assets;
   - Set QA is final;
   - freeze is ready for hardening.
2. `exact_asset_evidence`
   - required-set evidence gate passes;
   - every required asset has real physical SHA-256 evidence;
   - auditor evidence points to the same output as Production Freeze;
   - every required asset is `VERIFIED` or `HUMAN_APPROVED`.
3. `simulator_binding`
   - every required asset has an explicit binding;
   - every binding points to the approved output;
   - no Pending assets;
   - no Simulator blocking conflicts;
   - binding/readiness flags are complete.
4. `final_runtime`
   - exact standalone HTML SHA-256 is known;
   - browser-runtime evidence binds to that SHA;
   - offline is true;
   - network requests and external resource dependencies are zero;
   - 375 / 390 / 430 px checks show no page-level horizontal overflow or broken images.

## Status semantics

- `PASS`: all checks pass; `final_eligible=true`.
- `UNVERIFIED`: required independent/semantic/runtime evidence is missing or unresolved; Final is blocked without treating absence as a deterministic contradiction.
- `FAIL`: a deterministic conflict exists, such as a binding/output mismatch, invalidated evidence, pending assets, or final HTML hash mismatch.

A caller-authored or Simulator-carried `hard_verification_status` never creates PASS. M4 recomputes it.

## Review eligibility

Review mode and Final mode remain separate. Pending assets or unresolved semantic evidence may still permit Simulator review, but never Final delivery.

## Legacy compatibility

`listing-hardening` and Delivery State 0.1/0.2 validators remain in the repository for v0.3.3 compatibility and regression tests. New routing uses `evidence-hardening` for Stage 10.

M4 intentionally does not redesign installation, distribution, release packaging, or the real 43-template Simulator registry. Those remain outside this milestone.
