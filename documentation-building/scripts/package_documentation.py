#!/usr/bin/env python3
"""ZIP an explicit allowlist with a verified hash manifest. No overwrite."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import zipfile
import json
from doc_common import emit, file_list, load_config, local_file, sha256


def package(root, config, output):
    root = Path(root).resolve(strict=True)
    selected = file_list(config)
    metadata = config.get('metadata')
    if not isinstance(metadata, dict) or not metadata.get('title') or not metadata.get('document_date'):
        raise ValueError('metadata.title and metadata.document_date are required')
    datetime.strptime(metadata['document_date'], '%Y-%m-%d')
    entries = []
    names = set()
    output = output.absolute()
    for name in selected:
        path = local_file(root, name)
        arc = path.relative_to(root).as_posix()
        if arc in names or arc == 'manifest.json':
            raise ValueError('Duplicate or reserved archive path: ' + arc)
        if any(x in {'.git', 'node_modules', '.venv', '__pycache__'} for x in path.relative_to(root).parts):
            raise ValueError('Runtime/private directory selected: ' + arc)
        if path.name.startswith('.env') or path.name in {'.DS_Store', 'id_rsa', 'id_ed25519'} or path.suffix.lower() in {'.pem', '.key'}:
            raise ValueError('Credential/metadata file selected: ' + arc)
        if path == output.resolve():
            raise ValueError('Output ZIP must not be a selected input')
        names.add(arc)
        entries.append((arc, path))
    if output.exists() or output.is_symlink():
        raise ValueError('Output exists; choose a new path: ' + str(output))
    records = []
    created = False
    try:
        with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as z:
            created = True
            for arc, path in entries:
                # Read once so manifest describes exactly the bytes being packaged.
                data = path.read_bytes()
                z.writestr(arc, data)
                records.append({'file': arc, 'bytes': len(data), 'sha256': sha256(data)})
            manifest = {'schema_version': 1, 'metadata': metadata,
                        'packaged_at': datetime.now(timezone.utc).isoformat(), 'files': records,
                        'scope': 'Explicit selection; hashes are integrity checks, not factual or privacy approval'}
            z.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        with zipfile.ZipFile(output) as z:
            if z.testzip() is not None:
                raise ValueError('ZIP CRC check failed')
            for record in records:
                data = z.read(record['file'])
                if len(data) != record['bytes'] or sha256(data) != record['sha256']:
                    raise ValueError('ZIP manifest mismatch: ' + record['file'])
    except Exception:
        if created:
            output.unlink(missing_ok=True)
        raise
    return {'passed': True, 'files': len(records), 'zip': str(output),
            'bytes': output.stat().st_size, 'sha256': sha256(output.read_bytes())}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--config', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    try:
        result = package(Path(a.root).resolve(strict=True), load_config(a.config), Path(a.output))
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        result = {'passed': False, 'errors': [str(exc)]}
    emit(result)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
