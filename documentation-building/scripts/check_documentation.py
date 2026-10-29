#!/usr/bin/env python3
"""Validate explicit static HTML selections. No browser, network, or writes."""
import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from doc_common import emit, file_list, load_config, local_file


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.text = [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'base':
            raise ValueError('HTML base tags need project-specific URL validation')
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.links.append(attrs[key])

    def handle_data(self, text):
        self.text.append(text)


def validate(root, config):
    root = Path(root).resolve(strict=True)
    selected = file_list(config)
    errors, remote, skipped = [], [], []
    docs, texts = {}, {}
    paths = {name: local_file(root, name) for name in selected}
    # Scan only declared UTF-8 text formats; PDF/image/audio require other checks.
    for name, path in paths.items():
        if path.suffix.lower() in {'.html', '.htm', '.json', '.txt', '.md', '.csv', '.svg', '.jsonl', '.css', '.js', '.mjs'}:
            texts[name] = path.read_text(encoding='utf-8')
        else:
            skipped.append(name)

    def document(path):
        if path not in docs:
            docs[path] = Document(path.read_text(encoding='utf-8'))
        return docs[path]

    for name, path in paths.items():
        if path.suffix.lower() not in {'.html', '.htm'}:
            continue
        doc = document(path)
        errors.extend(f'{name}: duplicate id {key}' for key, n in Counter(doc.ids).items() if n > 1)
        for href in doc.links:
            u = urlsplit(href)
            if u.scheme in {'http', 'https'} or u.netloc:
                remote.append({'file': name, 'url': href})
                continue
            if u.scheme in {'data', 'blob', 'mailto', 'tel'}:
                continue
            if u.scheme:
                errors.append(f'{name}: unsupported/nonportable scheme {u.scheme}')
                continue
            try:
                raw_path = unquote(u.path)
                target = root / raw_path.lstrip('/') if raw_path.startswith('/') else path.parent / raw_path
                if not raw_path:
                    target = path
                elif target.is_dir():
                    target = target / 'index.html'
                target = local_file(root, str(target.relative_to(root)))
                if config.get('require_packaged_links', True) and target not in paths.values():
                    errors.append(f'{name}: linked file is not selected: {href}')
                # PDF fragments/media positions are opaque to this static checker.
                fragment = unquote(u.fragment)
                if fragment and target.suffix.lower() in {'.html', '.htm'}:
                    if fragment not in document(target).ids:
                        errors.append(f'{name}: missing HTML anchor: {href}')
            except (ValueError, OSError) as exc:
                errors.append(f'{name}: invalid local link {href}: {exc}')
    for pair in config.get('bilingual', []):
        left, right = (document(local_file(root, pair[k])) for k in ('left', 'right'))
        anchors = pair.get('anchors')
        if anchors is None:
            if set(left.ids) != set(right.ids):
                errors.append('Bilingual ID sets differ: ' + pair['left'] + ' / ' + pair['right'])
        elif not anchors or not set(anchors).issubset(set(left.ids) & set(right.ids)):
            errors.append('Missing bilingual anchors: ' + pair['left'] + ' / ' + pair['right'])
    for name, required in config.get('required_text', {}).items():
        local_file(root, name)
        if name not in texts:
            raise ValueError('required_text target must be selected UTF-8 text: ' + name)
        for phrase in required:
            if phrase not in texts[name]:
                errors.append(f'{name}: missing required text: {phrase}')
    for name, text in texts.items():
        for phrase in config.get('forbidden_text', []):
            if phrase and phrase in text:
                # Do not print the sensitive value into logs.
                errors.append(f'{name}: forbidden text detected')
    return {'passed': not errors, 'files_checked': len(paths), 'html_checked': len(docs),
            'errors': errors, 'external_links_not_fetched': remote,
            'binary_files_not_inspected': skipped,
            'not_checked': ['translation meaning', 'JavaScript-generated DOM', 'CSS imports/srcset',
                            'PDF text/layout', 'fact accuracy', 'playback', 'privacy in binary assets']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--config', required=True)
    a = p.parse_args()
    try:
        result = validate(Path(a.root).resolve(strict=True), load_config(a.config))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        result = {'passed': False, 'errors': [str(exc)]}
    emit(result)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
