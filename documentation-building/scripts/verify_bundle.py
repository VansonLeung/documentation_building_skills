#!/usr/bin/env python3
"""Read-only standalone bundle links, local provenance hashes and lock consistency."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from doc_common import local_file


def verify(root):
    root = Path(root).resolve(strict=True)
    errors = []
    provenance = json.loads((root / 'provenance.json').read_text())
    for record in provenance['files']:
        try:
            file = local_file(root, record['file'])
            if hashlib.sha256(file.read_bytes()).hexdigest() != record['sha256']:
                errors.append('Local provenance hash changed: ' + record['file'])
        except ValueError as error:
            errors.append(str(error))
    links = 0
    for file in [root / 'README.md', root / 'documentation-building/SKILL.md', *sorted((root / 'documentation-building/references').glob('*.md'))]:
        for target in re.findall(r'\]\(([^)]+)\)', file.read_text()):
            if '://' in target:
                continue
            links += 1
            path = (file.parent / target.split('#')[0]).resolve()
            if not path.is_relative_to(root) or not path.exists():
                errors.append('Missing/nonlocal documentation link: ' + file.name + ': ' + target)
    package = json.loads((root / 'package.json').read_text())
    lock = json.loads((root / 'package-lock.json').read_text())
    if package['dependencies'] != lock['packages']['']['dependencies']:
        errors.append('package.json and lockfile dependencies differ')
    for name, version in package['dependencies'].items():
        if lock['packages']['node_modules/' + name]['version'] != version:
            errors.append('Expected an exact pinned version: ' + name)
    return {'passed': not errors, 'errors': errors, 'local_hashes': len(provenance['files']),
            'documentation_links': links, 'external_project_files_needed': False,
            'not_checked': ['original external sources', 'copyright ownership', 'runtime behavior']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=Path(__file__).resolve().parents[2])
    a = parser.parse_args()
    try:
        result = verify(a.root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {'passed': False, 'errors': [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
