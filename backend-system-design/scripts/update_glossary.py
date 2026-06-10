"""Summarize glossary terms from the documentation."""

from pathlib import Path

glossary_file = Path(__file__).resolve().parent.parent / 'docs' / 'glossary.md'
text = glossary_file.read_text(encoding='utf-8').splitlines()
terms = [line[3:].strip() for line in text if line.startswith('## ')]
print('Glossary terms:')
for term in terms:
    print(f'- {term}')
print(f'Found {len(terms)} glossary definitions.')
