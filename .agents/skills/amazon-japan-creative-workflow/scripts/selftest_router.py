from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "stage-4": "listing-strategy",
    "stage-7": "listing-strategy",
    "stage-7.5": "creative-production",
    "stage-8": "creative-production",
    "stage-8.4": "creative-quality",
    "stage-8.6": "listing-simulator-bridge",
    "stage-9": "listing-simulator-bridge",
    "stage-9.2": "creative-quality",
    "stage-9.5": "creative-production",
    "stage-10": "evidence-hardening",
}


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label}: missing {needle!r}")


def main() -> int:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    manifest = (ROOT / "core" / "manifest.yaml").read_text(encoding="utf-8")
    routing = (ROOT / "references" / "routing.md").read_text(encoding="utf-8")
    agent = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    require(skill, "name: amazon-japan-creative-workflow", "skill identity")
    require(skill, "$amazon-japan-creative-workflow", "normal invocation")
    require(manifest, "distribution_version: 0.1.0", "manifest version")
    require(manifest, "repository: heymio/japan-listing-demo", "baseline repository")
    require(manifest, "version: v0.3.3", "baseline version")
    require(manifest, "commit: 67dbb772398af1ff67547b12bb401d96e2a588d8", "baseline commit")
    require(manifest, "market: JP", "market")
    require(manifest, "locale: ja-JP", "locale")
    require(manifest, "channel: amazon-jp", "channel")

    stage_needles = {
        "stage-4": "0–7 → `listing-strategy`",
        "stage-7": "0–7 → `listing-strategy`",
        "stage-7.5": "7.5–8 → `creative-production`",
        "stage-8": "7.5–8 → `creative-production`",
        "stage-8.4": "8.4 → `creative-quality`",
        "stage-8.6": "8.6–9 → `listing-simulator-bridge`",
        "stage-9": "8.6–9 → `listing-simulator-bridge`",
        "stage-9.2": "9.2 → `creative-quality`",
        "stage-9.5": "9.5 → `creative-production`",
        "stage-10": "10 → `evidence-hardening`",
    }
    for stage, owner in EXPECTED.items():
        require(routing, stage_needles[stage], f"{stage} owner {owner}")

    require(skill, "`这张先过`", "current-asset acceptance")
    require(skill, "current Asset", "current-asset-only semantics")
    require(skill, "`先这样`", "ambiguous pause wording")
    require(skill, "does not advance", "ambiguous wording must not advance")
    require(agent, "Amazon Japan Creative Workflow", "agent display name")

    print(f"PASS: {len(EXPECTED)} stage routes + transition semantics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
