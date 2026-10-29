#!/usr/bin/env python3
"""Temporary cross-project fixtures; standard-library unit/integration checks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from doc_common import sha256
from check_documentation import validate
from package_documentation import package


class ToolsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='documentation-skills-test-')
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        for name, label in [('report.html', 'Illustrative'), ('report.zh-Hant.html', '示意')]:
            (self.root / name).write_text(f'<!doctype html><meta charset="utf-8"><h1 id="method">{label}</h1>'
                '<a href="#results">Results</a><h2 id="results">2 / 3</h2><a href="manual.html#filter">Manual</a>', encoding='utf-8')
        (self.root / 'manual.html').write_text('<h1 id="filter">Filter</h1><a href="slides.html#overview">Slides</a>')
        (self.root / 'slides.html').write_text('<section id="overview"><h1>Method</h1><p>Illustrative static slide</p></section>')
        self.config = {'metadata': {'title': 'Cross-project fixture', 'document_date': '2026-10-29'},
            'files': ['report.html', 'report.zh-Hant.html', 'manual.html', 'slides.html'],
            'bilingual': [{'left': 'report.html', 'right': 'report.zh-Hant.html', 'anchors': ['method', 'results']}],
            'required_text': {'report.html': ['Illustrative'], 'report.zh-Hant.html': ['示意']}}

    def test_static_report_manual_slides(self):
        result = validate(self.root, self.config)
        self.assertTrue(result['passed'], result)
        self.assertIn('PDF text/layout', result['not_checked'])

    def test_broken_cross_document_anchor(self):
        (self.root / 'manual.html').write_text('<h1 id="different">Filter</h1>')
        self.assertFalse(validate(self.root, self.config)['passed'])

    def test_duplicate_ids(self):
        with (self.root / 'slides.html').open('a') as f:
            f.write('<p id="overview">Duplicate</p>')
        self.assertFalse(validate(self.root, self.config)['passed'])

    def test_bilingual_missing_section(self):
        (self.root / 'report.zh-Hant.html').write_text('<h1 id="method">示意</h1>')
        self.assertFalse(validate(self.root, self.config)['passed'])

    def test_linked_file_missing_from_package(self):
        self.config['files'].remove('slides.html')
        self.assertFalse(validate(self.root, self.config)['passed'])

    def test_sensitive_value_not_logged(self):
        self.config['forbidden_text'] = ['SECRET-SENTINEL']
        with (self.root / 'manual.html').open('a') as f:
            f.write('SECRET-SENTINEL')
        result = validate(self.root, self.config)
        self.assertFalse(result['passed'])
        self.assertNotIn('SECRET-SENTINEL', json.dumps(result))

    def test_missing_required_text(self):
        self.config['required_text']['report.html'] = ['Absent']
        self.assertFalse(validate(self.root, self.config)['passed'])

    def test_external_links_are_not_claimed_checked(self):
        with (self.root / 'manual.html').open('a') as f:
            f.write('<a href="https://example.invalid/">External</a>')
        result = validate(self.root, self.config)
        self.assertTrue(result['passed'])
        self.assertEqual(len(result['external_links_not_fetched']), 1)

    def test_symlink_rejected(self):
        (self.root / 'alias.html').symlink_to(self.root / 'manual.html')
        self.config['files'].append('alias.html')
        with self.assertRaises(ValueError):
            validate(self.root, self.config)

    def test_path_escape_rejected(self):
        self.config['files'] = ['../outside.txt']
        with self.assertRaises(ValueError):
            validate(self.root, self.config)

    def test_packaging_hashes_and_no_overwrite(self):
        output = self.root / 'handover.zip'
        result = package(self.root, self.config, output)
        self.assertTrue(result['passed'])
        with zipfile.ZipFile(output) as z:
            manifest = json.loads(z.read('manifest.json'))
            self.assertEqual(set(z.namelist()), set(self.config['files']) | {'manifest.json'})
            for item in manifest['files']:
                self.assertEqual(z.read(item['file']), (self.root / item['file']).read_bytes())
                self.assertEqual(sha256(z.read(item['file'])), item['sha256'])
        before = output.read_bytes()
        with self.assertRaises(ValueError):
            package(self.root, self.config, output)
        self.assertEqual(output.read_bytes(), before)

    def test_package_credentials_and_reserved_path_rejected(self):
        for filename in ['.env', 'manifest.json']:
            (self.root / filename).write_text('fixture')
            self.config['files'] = [filename]
            with self.assertRaises(ValueError):
                package(self.root, self.config, self.root / 'blocked.zip')
            self.assertFalse((self.root / 'blocked.zip').exists())

    def test_duplicate_normalized_path_rejected(self):
        self.config['files'] = ['manual.html', './manual.html']
        with self.assertRaises(ValueError):
            package(self.root, self.config, self.root / 'blocked.zip')

    def test_cli_json_and_failure_exit(self):
        config = self.root / 'task.json'
        config.write_text(json.dumps(self.config))
        script = Path(__file__).with_name('check_documentation.py')
        command = [sys.executable, str(script), '--root', str(self.root), '--config', str(config)]
        good = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertTrue(json.loads(good.stdout)['passed'])
        (self.root / 'manual.html').unlink()
        bad = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertFalse(json.loads(bad.stdout)['passed'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
