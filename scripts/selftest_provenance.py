from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    text = (ROOT / "docs" / "provenance.md").read_text(encoding="utf-8")
    required = [
        "heymio/japan-listing-demo",
        "v0.3.3",
        "67dbb772398af1ff67547b12bb401d96e2a588d8",
        "independent",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f"FAIL: provenance missing {missing}")
    print("PASS: provenance is explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
