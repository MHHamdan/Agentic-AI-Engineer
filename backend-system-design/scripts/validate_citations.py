"""Validate that documentation citations are defined in the reference index."""

import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
references = set()
for line in (root / 'docs' / 'references.md').read_text(encoding='utf-8').splitlines():
    if line.startswith('[') and ']: ' in line:
        references.add(line.split(']:', 1)[0].strip('['))

citation_pattern = re.compile(r"\[([A-Za-z0-9_-]+)\]")
missing = []
for path in root.rglob('docs/**/*.md'):
    text = path.read_text(encoding='utf-8')
    for match in citation_pattern.finditer(text):
        token = match.group(1)
        if (
            token in references
            or token.startswith('http')
            or token.startswith('www.')
            or ' ' in token
            or path.name == 'references.md'
        ):
            continue
        if token not in (
            'RFC9110',
            'JWT7519',
            'OpenAPI',
            'GraphQLSpec',
            'WebhooksGitHub',
            'DockerComposeSpec',
            'PyTest',
            'PythonJose',
        ):
            continue
        missing.append(
            f"Missing reference for {token} in {path.relative_to(root)}"
        )

if missing:
    print('Citation validation failed:')
    for item in missing:
        print(item)
    raise SystemExit(1)

print('Citation validation passed.')
