"""Validate that topic front matter points to existing lab files."""

from pathlib import Path

root = Path(__file__).resolve().parent.parent
errors = []

for path in sorted((root / "docs" / "topics").rglob("*.md")):
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("code_lab:"):
            continue
        lab_path = line.split(":", 1)[1].strip()
        target = (path.parent / lab_path).resolve()
        if not target.exists():
            errors.append(
                f"Missing code_lab target in {path.relative_to(root)}: {lab_path}"
            )

if errors:
    print("Code lab validation failed:")
    for error in errors:
        print(error)
    raise SystemExit(1)

print("Code lab validation passed.")
