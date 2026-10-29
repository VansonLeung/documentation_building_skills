#!/usr/bin/env node
// Adapted from the LD HTML-first export pipeline; only template-compatible decks.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import PptxGenJS from 'pptxgenjs';
import {args, hash, serveDirectory, guardedContext} from './presentation_common.mjs';

const options = args(['input', 'output', 'notes', 'author', 'chromium']);
if (options.help) { console.log('export_presentation.mjs --input <deck.html> --output <new-directory> [--notes none|approved] [--author <name>] [--chromium <executable>]'); process.exit(0); }
if (!options.input || !options.output) throw Error('--input and --output are required');
const notePolicy = options.notes || 'none';
if (!['none', 'approved'].includes(notePolicy)) throw Error('--notes must be none or approved');
const input = await fs.realpath(options.input), output = path.resolve(options.output);
if (path.extname(input) !== '.html') throw Error('Expected an HTML deck');
await fs.mkdir(output); // Keep successful prior exports untouched.
let server, browser;
const report = {schema_version: 1, passed: false, input: path.basename(input),
  contract: {pptx_mode: 'full-slide-images', native_text_editable: false, animation: 'none', speaker_notes: notePolicy,
    pdf_source: 'html', html_source_sanitized: false},
  not_checked: ['Microsoft PowerPoint/Keynote import', 'manual visual review', 'general fact accuracy']};
try {
  server = await serveDirectory(path.dirname(input));
  browser = await chromium.launch({headless: true, ...(options.chromium ? {executablePath: options.chromium} : {})});
  const {context, blocked} = await guardedContext(browser, server.origin, {viewport: {width: 1280, height: 720}, deviceScaleFactor: 2});
  const page = await context.newPage(), errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', r => { if (r.status() >= 400) errors.push('HTTP ' + r.status()); });
  const url = server.origin + '/' + encodeURIComponent(path.basename(input)) + '?export=1';
  const response = await page.goto(url, {waitUntil: 'networkidle', timeout: 30000});
  if (!response?.ok()) throw Error('Deck failed to load');
  await page.waitForFunction(() => !!window.documentationReady);
  await page.evaluate(async () => { await window.documentationReady; await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });
  const dimensions = await page.locator('section.slide').evaluateAll(slides => slides.map(s => {
    const r = s.getBoundingClientRect();
    return {id: s.id, width: r.width, height: r.height};
  }));
  if (!dimensions.length || dimensions.some(s => !s.id) || new Set(dimensions.map(s => s.id)).size !== dimensions.length) throw Error('Deck needs unique non-empty slide IDs');
  const {width, height} = dimensions[0];
  if (width < 100 || height < 100 || dimensions.some(s => Math.abs(s.width - width) > 1 || Math.abs(s.height - height) > 1)) throw Error('Slides need a common non-empty fixed export size');
  const issues = await page.locator('section.slide').evaluateAll(slides => slides.flatMap(s => {
    const rect = s.getBoundingClientRect(), issues = [];
    for (const el of s.querySelectorAll('header,.slide-content,footer,table,.steps,.callouts')) {
      const r = el.getBoundingClientRect();
      if (r.bottom > rect.bottom + 1 || r.right > rect.right + 1 || el.scrollWidth > el.clientWidth + 3 || el.scrollHeight > el.clientHeight + 3) issues.push({slide: s.id, element: el.className || el.tagName});
    }
    return issues;
  }));
  report.layout_issues = issues;
  if (issues.length) throw Error('Slide content overflows export bounds');
  const pptx = new PptxGenJS();
  pptx.defineLayout({name: 'DOCUMENTATION', width: width / 96, height: height / 96}); pptx.layout = 'DOCUMENTATION';
  pptx.title = await page.title(); if (options.author) pptx.author = options.author;
  pptx.lang = await page.locator('html').getAttribute('lang') || 'en';
  const records = [], gallery = [];
  for (let i = 0; i < dimensions.length; i++) {
    const slide = page.locator('section.slide').nth(i), filename = `slide-${String(i + 1).padStart(3, '0')}.png`;
    const title = await slide.locator('h1,h2').first().innerText();
    await slide.screenshot({path: path.join(output, filename), animations: 'disabled'});
    const s = pptx.addSlide(); s.addImage({path: path.join(output, filename), x: 0, y: 0, w: width / 96, h: height / 96, altText: title});
    if (notePolicy === 'approved') {
      const notes = await slide.locator('.notes[data-share="approved"]').allTextContents();
      if (notes.length) s.addNotes(notes.join('\n'));
    }
    records.push({id: dimensions[i].id, title, screenshot: filename});
    gallery.push(`<figure><img src="${filename}" alt="Slide ${i + 1}"><figcaption>${i + 1}</figcaption></figure>`);
  }
  if (errors.length || blocked.length) throw Error('Browser errors or external/mutating requests detected');
  await pptx.writeFile({fileName: path.join(output, 'presentation.pptx')});
  await page.emulateMedia({media: 'screen'});
  await page.pdf({path: path.join(output, 'presentation.pdf'), width: width / 96 + 'in', height: height / 96 + 'in', printBackground: true, tagged: true, outline: true, preferCSSPageSize: true});
  await fs.writeFile(path.join(output, 'contact-sheet.html'), '<!doctype html><meta charset="utf-8"><title>Slide review</title><style>body{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));font:16px sans-serif}figure{margin:10px}img{width:100%}</style>' + gallery.join(''));
  report.slides = records; report.size_px = {width, height}; report.errors = errors; report.blocked = blocked;
  report.inputs = [...server.inputs.values()].sort((a, b) => a.file.localeCompare(b.file));
  const here = path.dirname(fileURLToPath(import.meta.url));
  report.tool_sources = await Promise.all(['export_presentation.mjs', 'presentation_common.mjs'].map(async file => ({file, sha256: hash(await fs.readFile(path.join(here, file)))})));
  report.tools = {node: process.version, chromium: browser.version()};
  report.dependency_lock_sha256 = hash(await fs.readFile(path.resolve(here, '../../package-lock.json')));
  report.outputs = await Promise.all((await fs.readdir(output)).sort().map(async file => { const bytes = await fs.readFile(path.join(output, file)); return {file, bytes: bytes.length, sha256: hash(bytes)}; }));
  report.passed = true;
} catch (error) { report.error = error.message; }
finally { await browser?.close(); await server?.close(); await fs.writeFile(path.join(output, 'export-manifest.json'), JSON.stringify(report, null, 2) + '\n'); }
console.log(JSON.stringify({passed: report.passed, slides: report.slides?.length, output, error: report.error}));
process.exitCode = report.passed ? 0 : 1;
