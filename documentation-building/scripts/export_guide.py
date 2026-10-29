#!/usr/bin/env python3
"""Optional maintained HTML -> native DOCX -> PDF. Uses installed converters only."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from inspect_office import inspect


def executable(value):
    candidate = shutil.which(value)
    if not candidate:
        raise ValueError('Required executable unavailable: ' + value)
    return candidate


def export(input_file, output, pandoc='pandoc', soffice='soffice', pdf=False, reference=None):
    input_file = Path(input_file).resolve(strict=True)
    if input_file.suffix.lower() != '.html':
        raise ValueError('Expected a maintained HTML guide')
    pandoc = executable(pandoc)
    if pdf:
        soffice = executable(soffice)
    if reference:
        reference = Path(reference).resolve(strict=True)
    output = Path(output).absolute()
    output.mkdir()  # Never replace an existing export directory.
    report = {'passed': False, 'input': input_file.name, 'contract': {
        'docx_native_text': True, 'pdf_source': 'docx' if pdf else None,
        'reference': 'user-supplied' if reference else 'clean-pandoc-default'},
        'not_checked': ['Microsoft Word import', 'manual pagination/visual review', 'factual accuracy']}
    try:
        if not reference:
            reference = output / 'reference.docx'
            reference.write_bytes(subprocess.check_output([pandoc, '--print-default-data-file=reference.docx'], timeout=30))
        command = [pandoc, str(input_file), '--from=html', '--to=docx', '--metadata=title:',
                   '--reference-doc=' + str(reference), '--resource-path=' + str(input_file.parent),
                   '--output=' + str(output / 'guide.docx')]
        subprocess.run(command, check=True, timeout=90, capture_output=True)
        report['office'] = inspect(output / 'guide.docx')
        report['tools'] = {'pandoc': subprocess.check_output([pandoc, '--version'], text=True).splitlines()[0]}
        if pdf:
            with tempfile.TemporaryDirectory(prefix='documentation-office-profile-') as temp:
                profile = Path(temp).resolve().as_uri()
                subprocess.run([soffice, '-env:UserInstallation=' + profile, '--headless', '--convert-to', 'pdf',
                                '--outdir', str(output), str(output / 'guide.docx')],
                               check=True, timeout=120, capture_output=True)
            if not (output / 'guide.pdf').read_bytes().startswith(b'%PDF-'):
                raise ValueError('DOCX-derived PDF was not generated')
            report['tools']['office_renderer'] = subprocess.check_output([soffice, '--version'], text=True).strip()
        report['inputs'] = [{'file': input_file.name, 'sha256': hashlib.sha256(input_file.read_bytes()).hexdigest()},
                            {'role': 'reference', 'sha256': hashlib.sha256(reference.read_bytes()).hexdigest()}]
        report['outputs'] = [{'file': p.name, 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                             for p in sorted(output.iterdir()) if p.is_file()]
        report['passed'] = True
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
    (output / 'export-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--pdf', action='store_true')
    parser.add_argument('--reference')
    parser.add_argument('--pandoc', default='pandoc')
    parser.add_argument('--soffice', default='soffice')
    a = parser.parse_args()
    try:
        report = export(a.input, a.output, a.pandoc, a.soffice, a.pdf, a.reference)
    except (OSError, ValueError) as error:
        report = {'passed': False, 'error': str(error)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
