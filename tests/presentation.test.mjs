// This integration suite uses only this checkout and its own installed dependencies.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {getDocument} from 'pdfjs-dist/legacy/build/pdf.mjs';
import {serveDirectory, guardedContext, hash} from '../documentation-building/scripts/presentation_common.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const scripts = path.join(root, 'documentation-building/scripts');
const output = process.env.DOC_TEST_OUTPUT ? path.resolve(process.env.DOC_TEST_OUTPUT) : await fs.mkdtemp(path.join(os.tmpdir(), 'documentation-presentation-test-'));
await fs.mkdir(output, {recursive: true});
const project = path.join(output, 'project');
const command = (file, args) => execFileSync(process.execPath, [path.join(scripts, file), ...args], {encoding: 'utf8', cwd: root});
command('create_presentation.mjs', ['--output', project]);
let english = await fs.readFile(path.join(project, 'deck.html'), 'utf8');
english = english.replace('Approved note keyword: traceability.', 'Approved note keyword: PublicNoteKeyword.')
  .replace('</aside><footer><span>Method', '</aside><aside class="notes" data-share="private">InternalNoteSentinel</aside><footer><span>Method');
await fs.writeFile(path.join(project, 'deck.html'), english);
const server = await serveDirectory(project), browser = await chromium.launch({headless: true});
const checks = [];
try {
  for (const mode of ['http', 'file']) for (const name of ['deck.html', 'deck.zh-Hant.html']) {
    const context = mode === 'http' ? (await guardedContext(browser, server.origin, {viewport: {width: 1440, height: 1000}})).context : await browser.newContext({viewport: {width: 1440, height: 1000}, serviceWorkers: 'block'});
    if (mode === 'file') await context.route('**/*', route => { const u = route.request().url(); return u.startsWith(pathToFileURL(project + path.sep).href) || u.startsWith('data:') ? route.continue() : route.abort(); });
    const page = await context.newPage(), errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(mode === 'http' ? server.origin + '/' + name : pathToFileURL(path.join(project, name)).href);
    await page.waitForFunction(() => !!window.documentationReady);
    await page.evaluate(() => window.documentationReady);
    assert.equal(await page.locator('section.slide').count(), 4);
    await page.evaluate(() => Reveal.slide(2));
    await page.locator('[data-reading]').click();
    assert.equal(await page.locator('body.reading').count(), 1);
    await page.locator('#results .present-slide').click();
    assert.equal(await page.evaluate(() => Reveal.getIndices().h), 2);
    await page.keyboard.press('/');
    await page.locator('[data-query]').fill(name === 'deck.html' ? 'denominator' : '分母');
    assert.equal(await page.locator('[data-results] button').count(), 1);
    await page.locator('[data-query]').press('Enter');
    assert.equal(await page.evaluate(() => Reveal.getIndices().h), 2);
    if (name === 'deck.html') {
      await page.locator('[data-search]').click();
      await page.locator('[data-query]').fill('PublicNoteKeyword');
      assert.equal(await page.locator('[data-results] button').count(), 0);
      await page.locator('[data-notes]').check();
      assert.equal(await page.locator('[data-results] button').count(), 1);
      await page.locator('[data-query]').fill('InternalNoteSentinel');
      assert.equal(await page.locator('[data-results] button').count(), 0);
      await page.locator('[data-query]').press('Escape');
    }
    await page.evaluate(() => Reveal.slide(1, 0, -1));
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#method .fragment.visible').count(), 1);
    await page.keyboard.press('ArrowLeft');
    assert.equal(await page.locator('#method .fragment.visible').count(), 0);
    if (mode === 'http') {
      await page.screenshot({path: path.join(output, name + '-desktop.png')});
      await page.locator('[data-reading]').click(); await page.setViewportSize({width: 390, height: 844});
      await page.waitForFunction(() => [...document.querySelectorAll('body.reading .fragment')].every(e => getComputedStyle(e).opacity === '1'));
      await page.locator('#method h2').scrollIntoViewIfNeeded();
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2));
      assert(Math.abs((await page.locator('.toolbar').boundingBox()).y) < 1, 'Reading toolbar must stay at viewport top');
      await page.screenshot({path: path.join(output, name + '-mobile.png'), animations: 'disabled'});
      await page.locator('#method .present-slide').click();
      await page.locator('[data-language]').click();
      await page.waitForFunction(() => !!window.documentationReady);
      await page.evaluate(() => window.documentationReady);
      assert.equal(await page.evaluate(() => Reveal.getCurrentSlide().id), 'method');
    }
    assert.deepEqual(errors, []);
    checks.push({mode, name, navigation: 'passed', notes_policy: 'passed'});
    await context.close();
  }
} finally { await browser.close(); await server.close(); }

for (const [name, policy, label] of [['deck.html', 'none', 'en-none'], ['deck.html', 'approved', 'en-approved'], ['deck.zh-Hant.html', 'approved', 'zh-approved']]) {
  const directory = path.join(output, label);
  command('export_presentation.mjs', ['--input', path.join(project, name), '--output', directory, '--notes', policy]);
  const manifest = JSON.parse(await fs.readFile(path.join(directory, 'export-manifest.json')));
  assert(manifest.passed, JSON.stringify(manifest)); assert.equal(manifest.slides.length, 4);
  for (const file of manifest.outputs) { const bytes = await fs.readFile(path.join(directory, file.file)); assert.equal(hash(bytes), file.sha256); assert.equal(bytes.length, file.bytes); }
  const office = JSON.parse(execFileSync('python3', [path.join(scripts, 'inspect_office.py'), path.join(directory, 'presentation.pptx'), '--include-text'], {encoding: 'utf8'}));
  assert.equal(office.slide_count, 4); assert(office.slides.every(s => s.pictures === 1 && s.native_text_characters === 0));
  assert(!JSON.stringify(office).includes('InternalNoteSentinel'));
  // PptxGenJS creates empty notes parts even when no notes are supplied.
  if (policy === 'none') assert(office.slides.every(s => s.notes_characters === 0 && !s.notes));
  if (label === 'en-approved') assert(JSON.stringify(office).includes('PublicNoteKeyword'));
  const pdf = await getDocument({data: new Uint8Array(await fs.readFile(path.join(directory, 'presentation.pdf'))), useSystemFonts: true}).promise;
  assert.equal(pdf.numPages, 4);
  let allText = '';
  for (let i = 0; i < 4; i++) {
    const p = await pdf.getPage(i + 1), text = (await p.getTextContent()).items.map(x => x.str).join('').normalize('NFKC').replace(/\s/g, '');
    assert(text.includes(manifest.slides[i].title.normalize('NFKC').replace(/\s/g, '')), `Missing selectable PDF title: ${label} ${i + 1}`);
    assert(Math.abs(p.view[2] / p.view[3] - 16 / 9) < .01); allText += text;
  }
  assert(!allText.includes('InternalNoteSentinel')); assert(!allText.includes('PublicNoteKeyword'));
  await pdf.destroy(); checks.push({label, pptx: 'passed', pdf: 'passed', hashes: 'passed'});
}
// A real source change must invalidate the input fingerprint and reach the PDF.
await fs.writeFile(path.join(project, 'deck.html'), english.replace('From source to explanation', 'A changed teaching title'));
const changed = path.join(output, 'changed');
command('export_presentation.mjs', ['--input', path.join(project, 'deck.html'), '--output', changed]);
const original = JSON.parse(await fs.readFile(path.join(output, 'en-none/export-manifest.json'))), revised = JSON.parse(await fs.readFile(path.join(changed, 'export-manifest.json')));
assert.notEqual(original.inputs.find(f => f.file === 'deck.html').sha256, revised.inputs.find(f => f.file === 'deck.html').sha256);
assert.notEqual(original.outputs.find(f => f.file === 'slide-001.png').sha256, revised.outputs.find(f => f.file === 'slide-001.png').sha256);
const changedPdf = await getDocument({data: new Uint8Array(await fs.readFile(path.join(changed, 'presentation.pdf')))}).promise;
assert((await (await changedPdf.getPage(1)).getTextContent()).items.map(x => x.str).join('').normalize('NFKC').replace(/\s/g, '').includes('Achangedteachingtitle')); await changedPdf.destroy();
const results = {passed: true, checks, source_edit_reached_exports: true, scope: 'Local template and generated packages; no desktop Office application tested'};
await fs.writeFile(path.join(output, 'test-results.json'), JSON.stringify(results, null, 2) + '\n');
console.log(JSON.stringify({passed: true, output, checks: checks.length, source_edit_reached_exports: true}));
