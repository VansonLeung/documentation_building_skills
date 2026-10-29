"""Shared filesystem helpers. Standard library only; no document mutations."""
import hashlib
import json
from pathlib import Path


def local_file(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError('Expected a non-empty relative file path')
    candidate = root / name
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError('Path leaves document root: ' + name)
    current = candidate
    while current != root and current != current.parent:
        if current.is_symlink():
            raise ValueError('Symlinks are not accepted: ' + name)
        current = current.parent
    if not resolved.is_file():
        raise ValueError('Missing file: ' + name)
    return resolved


def file_list(config):
    files = config.get('files')
    if not isinstance(files, list) or not files or any(not isinstance(f, str) for f in files):
        raise ValueError('files must be a non-empty list of relative file paths')
    if len(files) != len(set(files)):
        raise ValueError('Duplicate file selections')
    return files


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_config(path):
    config = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(config, dict):
        raise ValueError('Config must be an object')
    return config


def emit(result):
    print(json.dumps(result, ensure_ascii=False, indent=2))
