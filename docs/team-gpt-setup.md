# Optional Team GPT setup

A team-facing Custom GPT can make `amazon-japan-creative-workflow` easier to discover and resume, but it is not the execution source of truth.

The architecture contract is:

> **GPT = optional UX shell**  
> **Skills = versioned execution architecture**  
> **Auditor/scripts = hard verification**

## Recommended use

Create a thin GPT only when it improves onboarding for Japan marketing teammates who do not normally work from a repository or Codex workspace.

The GPT may help users:

- start or resume a Japan listing project;
- choose the target channel/page type;
- upload product, GTM, VOC, competitor, UI, render, and frontend-reference materials;
- understand the current Major Stage Checkpoint;
- invoke the installed `$amazon-japan-creative-workflow` workflow;
- use web/image capabilities when the current stage requires them.

The GPT should not duplicate the detailed Strategy, Creative Production, Creative Quality, or Hardening rules in its own Instructions.

## Recommended GPT instructions

Keep the GPT prompt short. For example:

```text
Use the installed amazon-japan-creative-workflow workflow as the execution source of truth.
Help team members create or resume a Japan listing project, upload product/GTM/visual inputs, and follow the workflow's Major Stage Checkpoints.
Do not duplicate the detailed workflow rules in GPT Instructions.
Keep the normal user-facing invocation and project flow simple; internal Planning, Production, Hardening, and Evidence Auditor Skills are routed by amazon-japan-creative-workflow.
```

## Capabilities

Enable capabilities that are useful for the workflow in your ChatGPT environment, such as:

- web access for current market/channel/frontend research;
- image generation/editing for Stage 8 production;
- file upload/analysis for product, GTM, VOC, design, and reference materials.

Exact product capabilities can change over time, so verify the currently available GPT builder options when configuring the shell.

## One team-facing entry

The teammate experience should remain:

```text
Open the team GPT or invoke $amazon-japan-creative-workflow
↓
Upload source materials
↓
Review Product / Offer / Claim baseline
↓
Review Consumer / Market Strategy
↓
Review channel page plan
↓
Review Creative Strategy / complete asset set
↓
Review generated visuals
↓
Review verified demo
```

Do not ask ordinary team members to manually invoke `listing-strategy`, `creative-production`, `creative-quality`, or legacy hardening/auditor internals.

## Source of truth

Workflow updates belong in the public GitHub repository and packaged Skills. The GPT is deliberately thin so a workflow release can be versioned, tested, reviewed, and distributed without maintaining a second copy of the business logic in GPT Instructions.

## Context limitation

A Custom GPT shell does not replace the workflow's explicit Context Projection. Production still receives the compact Creative Strategy Kernel, Production Handoff, current Asset Packet, referenced source assets, and approved benchmarks/patterns rather than the full control-plane history.

Likewise, loading an embedded Evidence Auditor inside one model context does not prove independent semantic review. Follow the auditor/hardening contract for independent or human semantic review when required.
