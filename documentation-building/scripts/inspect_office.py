#!/usr/bin/env python3
"""Inspect Office ZIP/XML without editing; relationships determine slide/note order."""
import argparse
import json
import posixpath
from pathlib import Path
import zipfile
import xml.etree.ElementTree as E

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def inspect(file, include_text=False, max_mb=256):
    with zipfile.ZipFile(file) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive parts')
        if sum(i.file_size for i in z.infolist()) > max_mb * 1024 * 1024:
            raise ValueError('Archive exceeds uncompressed size limit')
        if z.testzip() is not None:
            raise ValueError('ZIP CRC error')
        xml = {n: E.fromstring(z.read(n)) for n in names if n.endswith(('.xml', '.rels'))}

        def relationships(part):
            rel_path = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
            result = {}
            if rel_path not in xml:
                return result
            for rel in xml[rel_path]:
                if rel.get('TargetMode') == 'External':
                    continue
                raw = rel.get('Target', '')
                target = posixpath.normpath(raw.lstrip('/') if raw.startswith('/') else posixpath.join(posixpath.dirname(part), raw))
                if target.startswith('../') or target not in names:
                    raise ValueError('Missing or escaping relationship target: ' + rel_path)
                result[rel.get('Id')] = (target, rel.get('Type', ''))
            return result

        result = {'passed': True, 'file': Path(file).name, 'zip_xml': 'passed',
                  'not_checked': ['Office application import', 'visual layout', 'factual accuracy']}
        if 'ppt/presentation.xml' in xml:
            rels = relationships('ppt/presentation.xml')
            slides = []
            for item in xml['ppt/presentation.xml'].findall('p:sldIdLst/p:sldId', NS):
                relationship = rels.get(item.get('{' + NS['r'] + '}id'))
                if not relationship or not relationship[1].endswith('/slide'):
                    raise ValueError('Presentation slide relationship missing')
                part = relationship[0]
                note_targets = [target for target, kind in relationships(part).values() if kind.endswith('/notesSlide')]
                notes = []
                for target in note_targets:
                    for shape in xml[target].findall('.//p:sp', NS):
                        if shape.find('.//p:ph[@type="body"]', NS) is not None:
                            notes.extend(t.text or '' for t in shape.findall('.//a:t', NS))
                row = {'part': part, 'pictures': len(xml[part].findall('.//p:pic', NS)),
                       'native_text_characters': sum(len(t.text or '') for t in xml[part].findall('.//a:t', NS)),
                       'notes_present': bool(note_targets), 'notes_characters': len(' '.join(notes).strip())}
                if include_text:
                    row['notes'] = ' '.join(notes)
                slides.append(row)
            result.update({'kind': 'pptx', 'slide_count': len(slides), 'slides': slides})
        elif 'word/document.xml' in xml:
            doc = xml['word/document.xml']
            result.update({'kind': 'docx', 'paragraphs': len(doc.findall('.//w:p', NS)),
                           'tables': len(doc.findall('.//w:tbl', NS)), 'pictures': len(doc.findall('.//w:drawing', NS)),
                           'native_text_characters': sum(len(t.text or '') for t in doc.findall('.//w:t', NS))})
            if include_text:
                result['text'] = ' '.join(t.text or '' for t in doc.findall('.//w:t', NS))
        else:
            raise ValueError('Expected a PPTX or DOCX package')
        return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('file')
    p.add_argument('--include-text', action='store_true', help='Include notes/body text in output; may contain private content')
    p.add_argument('--max-uncompressed-mb', type=int, default=256)
    a = p.parse_args()
    try:
        result = inspect(a.file, a.include_text, a.max_uncompressed_mb)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, E.ParseError) as error:
        result = {'passed': False, 'error': str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
