// Optional integration: installed Pandoc and LibreOffice, no dependency installation.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {hash} from '../documentation-building/scripts/presentation_common.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'documentation-guide-test-'));
const results = [];
for (const [language, file, title] of [['en', 'guide.html', 'Example user guide'], ['zh-Hant', 'guide.zh-Hant.html', '使用手冊示例']]) {
  const directory = path.join(output, language);
  const report = JSON.parse(execFileSync('python3', [path.join(root, 'documentation-building/scripts/export_guide.py'),
    '--input', path.join(root, 'documentation-building/assets/guide', file), '--output', directory, '--pdf'], {encoding: 'utf8'}));
  assert(report.passed, JSON.stringify(report));
  assert.equal(report.office.tables, 1); assert(report.office.native_text_characters > 40);
  for (const record of report.outputs) assert.equal(hash(await fs.readFile(path.join(directory, record.file))), record.sha256);
  const config = path.join(output, language + '-expectations.json');
  await fs.writeFile(config, JSON.stringify({required_text: [title]}));
  const pdf = JSON.parse(execFileSync(process.execPath, [path.join(root, 'documentation-building/scripts/inspect_pdf.mjs'),
    '--input', path.join(directory, 'guide.pdf'), '--config', config], {encoding: 'utf8'}));
  assert(pdf.passed); assert(pdf.page_count > 0);
  results.push({language, native_docx: true, pdf_from_docx: true, pdf_text_checked: true, hashes: true});
}
await fs.writeFile(path.join(output, 'test-results.json'), JSON.stringify({passed: true, results}, null, 2) + '\n');
console.log(JSON.stringify({passed: true, output, results}));
