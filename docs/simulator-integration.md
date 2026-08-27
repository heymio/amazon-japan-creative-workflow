# Amazon Japan Listing Simulator Integration

## M3 contract

This workflow does not render Amazon UI. It produces deterministic folder/ZIP import packs for the external Amazon Japan Listing Simulator and consumes the resulting page-context review through later Creative Quality routing.

### Explicit bindings

Known relationships are serialized in `asset-slot-contract.json` and repeated exactly in `listing-simulator-manifest.json`:

- `asset_id`
- `slot_id`
- project-root-relative `output_ref`
- optional `variation_id`
- content-region coordinates when applicable: `content_id`, `module_id`, registry-owned `template_id`, `slot_key`

Higher-quality interoperability comes from explicit mapping, not filename heuristics. A supported media file with no binding becomes `pending_assets`; the bridge does not infer its slot or Variation from its filename.

### Stable slots

Gallery/detail slots use `profiles/amazon-jp/slot-taxonomy.json`. A+/Brand Story/Shoppable template IDs come from the Simulator registry. The file `template-registry.synthetic.json` is synthetic test data only and must never be treated as the real 43-template registry.

### Parent / Variation inheritance

Parent data is inherited unless the Variation overrides it. Merge keys are semantic:

- Gallery/media: `slot_id`
- specifications: specification key
- content assets: `content_id + module_id + slot_key`

An absent field inherits. Explicit `null` disables the inherited value. Collection entries are never merged by list position.

### Active content selection

One preview can activate one Basic or Premium A+ enhanced-description variant and one Brand Story or Shoppable Collections brand-content variant.

### Eligibility metadata

The bridge carries these exact fields:

- `production_freeze_ready`
- `required_asset_set_complete`
- `approved_output_matches`
- `asset_binding_complete`
- `blocking_conflicts`
- `hard_verification_status` (`PASS`, `UNVERIFIED`, `FAIL`)

The bridge may derive binding completeness from the actual pack. It never upgrades hard verification.

### Security

Folder/ZIP packs reject path traversal, absolute paths, Windows absolute forms, symlinks, duplicate normalized ZIP paths, `.env`/`.env.local`, executable JavaScript, oversized members, and suspicious compression ratios. ZIP output is deterministic: sorted paths, fixed timestamps, and fixed permissions via the shared packager.

## Real registry boundary

M3 proves the interoperability contract with synthetic registry records representing Basic A+, Premium A+, Brand Story, and Shoppable Collections. Compatibility with the Simulator's actual 43-template registry is intentionally deferred until the real registry is supplied and tested.
