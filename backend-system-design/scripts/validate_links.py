"""Validate markdown links across the documentation repository."""

import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
errors = []

for path in root.rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    for match in pattern.finditer(text):
        label, link = match.groups()
        if link.startswith("http") or link.startswith("#") or "://" in link:
            continue
        link_path = link.split("#", 1)[0].split("?", 1)[0]
        target = (path.parent / link_path).resolve()
        if not target.exists():
            errors.append(f"Broken link in {path.relative_to(root)}: {link}")

if errors:
    print("Link validation failed:")
    for error in errors:
        print(error)
    raise SystemExit(1)

print("Link validation passed.")
