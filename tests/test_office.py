import importlib.util
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('inspect_office', Path(__file__).resolve().parents[1] / 'documentation-building/scripts/inspect_office.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'


class OfficeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='office-inspector-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, entries):
        file = self.root / 'fixture.zip'
        with ZipFile(file, 'w') as z:
            for key, value in entries.items():
                z.writestr(key, value)
        return file

    def presentation(self):
        return {
            'ppt/presentation.xml': f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst><p:sldId id="8" r:id="second"/><p:sldId id="1" r:id="first"/></p:sldIdLst></p:presentation>',
            'ppt/_rels/presentation.xml.rels': f'<Relationships xmlns="{REL}"><Relationship Id="first" Type="{R}/slide" Target="slides/slide1.xml"/><Relationship Id="second" Type="{R}/slide" Target="slides/slide8.xml"/></Relationships>',
            'ppt/slides/slide1.xml': f'<p:sld xmlns:p="{P}"><p:pic/></p:sld>',
            'ppt/slides/slide8.xml': f'<p:sld xmlns:p="{P}"><p:pic/></p:sld>',
            'ppt/slides/_rels/slide8.xml.rels': f'<Relationships xmlns="{REL}"><Relationship Id="n" Type="{R}/notesSlide" Target="../notesSlides/notesSlide42.xml"/></Relationships>',
            'ppt/notesSlides/notesSlide42.xml': f'<p:notes xmlns:p="{P}" xmlns:a="{A}"><p:sp><p:nvSpPr><p:nvPr><p:ph type="body"/></p:nvPr></p:nvSpPr><a:t>Approved note</a:t></p:sp></p:notes>'}

    def test_relationship_order_and_nonsequential_notes(self):
        result = module.inspect(self.write(self.presentation()), include_text=True)
        self.assertEqual(result['slide_count'], 2)
        self.assertEqual(result['slides'][0]['part'], 'ppt/slides/slide8.xml')
        self.assertEqual(result['slides'][0]['notes'], 'Approved note')
        self.assertFalse(result['slides'][1]['notes_present'])

    def test_missing_notes_are_valid(self):
        entries = self.presentation()
        del entries['ppt/slides/_rels/slide8.xml.rels']
        result = module.inspect(self.write(entries))
        self.assertTrue(all(not s['notes_present'] for s in result['slides']))

    def test_notes_not_emitted_by_default(self):
        result = module.inspect(self.write(self.presentation()))
        self.assertNotIn('notes', result['slides'][0])

    def test_docx_native_content(self):
        w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        result = module.inspect(self.write({'word/document.xml': f'<w:document xmlns:w="{w}"><w:p><w:r><w:t>Example</w:t></w:r></w:p><w:tbl/></w:document>'}))
        self.assertEqual(result['tables'], 1)
        self.assertEqual(result['native_text_characters'], 7)
        self.assertNotIn('text', result)

    def test_broken_relationship_rejected(self):
        entries = self.presentation()
        del entries['ppt/slides/slide8.xml']
        with self.assertRaises(ValueError):
            module.inspect(self.write(entries))

    def test_non_office_zip_rejected(self):
        with self.assertRaises(ValueError):
            module.inspect(self.write({'readme.txt': 'Not Office'}))

    def test_size_limit(self):
        with self.assertRaises(ValueError):
            module.inspect(self.write(self.presentation()), max_mb=0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
