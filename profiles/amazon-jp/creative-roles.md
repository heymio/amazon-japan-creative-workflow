# Amazon Japan Creative Roles

Creative Role describes the **shopper job** of an asset. It is independent from page region, native template and media type. A Gallery asset and an A+ asset can share a message while carrying different Creative Roles; an A+ module is never itself a Creative Role.

```yaml
role: HERO_POSITIONING
shopper_job: What is this product and why should I keep looking?
required_evidence: exact product identity and one clear core positioning
common_failures:
  - product is too small or visually secondary
  - hero carries too many equal-priority messages
recommended_regions:
  - gallery
  - a-plus
```

```yaml
role: DIFFERENTIATOR_PROOF
shopper_job: Why choose this product instead of a conventional alternative?
required_evidence: direct visible evidence object tied to the differentiator
common_failures:
  - proof exists only in headline copy
  - visual implies a stronger claim than evidence supports
recommended_regions:
  - gallery
  - a-plus
```

```yaml
role: MECHANISM_PROOF
shopper_job: How does the product create the claimed result?
required_evidence: authoritative mechanism, sequence or interface evidence
common_failures:
  - invented internal structure
  - technical detail has no shopper takeaway
recommended_regions:
  - gallery
  - a-plus
  - video
```

```yaml
role: LIFESTYLE_USE_CASE
shopper_job: When in real life does this product create meaningful value?
required_evidence: credible situation, friction, intervention and outcome
common_failures:
  - generic happy-person stock scene
  - product is incidental to the depicted action
recommended_regions:
  - gallery
  - a-plus
  - video
```

```yaml
role: COMPARISON_DECISION
shopper_job: Which option or approach should I choose?
required_evidence: same-basis decision criteria supported by current facts
common_failures:
  - inconsistent comparison basis
  - decorative checkmarks replace evidence
recommended_regions:
  - gallery
  - a-plus
```

```yaml
role: ECOSYSTEM_COMPATIBILITY
shopper_job: How does this product fit into systems or devices I already use?
required_evidence: supported compatibility relationship and resulting user action
common_failures:
  - logo wall with no user outcome
  - protocol support is overstated as deep native integration
recommended_regions:
  - gallery
  - a-plus
  - brand-story
```

```yaml
role: SPEC_INSTALLATION
shopper_job: Will this fit and can I install or use it in my environment?
required_evidence: dimensions, constraints, installation logic or compatibility facts
common_failures:
  - parameter wall with no purchase-decision value
  - limitations are hidden or visually ambiguous
recommended_regions:
  - gallery
  - a-plus
```

```yaml
role: OBJECTION_HANDLING
shopper_job: What specific reason not to buy can be resolved with evidence?
required_evidence: explicit concern, evidence and bounded reassurance
common_failures:
  - generic reassurance without proof
  - objection answer silently introduces a new claim
recommended_regions:
  - gallery
  - a-plus
```

```yaml
role: BRAND_STORY
shopper_job: Why should I trust this brand and why does this product belong in its portfolio?
required_evidence: relevant brand expertise, design logic or portfolio relationship
common_failures:
  - generic innovation slogans that fit any brand
  - product feature repetition instead of brand context
recommended_regions:
  - brand-story
  - a-plus
```

## Usage rule

Assign exactly one primary Creative Role to each final Asset ID at Stage 7. Region, slot, media type and Creative Role remain separate fields. Additional secondary purposes may be documented in strategy, but they do not erase the primary shopper task.
