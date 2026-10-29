#!/usr/bin/env node
// Read-only cross-platform text/page/outline inspection; never reserializes PDFs.
import fs from 'node:fs/promises';
import path from 'node:path';
import {getDocument} from 'pdfjs-dist/legacy/build/pdf.mjs';
import {args, hash} from './presentation_common.mjs';
const options = args(['input', 'config', 'include-text']);
if (options.help) { console.log('inspect_pdf.mjs --input <document.pdf> [--config <expectations.json>] [--include-text true]'); process.exit(0); }
if (!options.input) throw Error('--input is required');
let doc;
try {
  const config = options.config ? JSON.parse(await fs.readFile(options.config, 'utf8')) : {};
  const bytes = await fs.readFile(options.input);
  doc = await getDocument({data: new Uint8Array(bytes), useSystemFonts: true, isEvalSupported: false}).promise;
  const pages = [];
  let text = '';
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i), content = (await page.getTextContent()).items.map(x => x.str).join(' ');
    const row = {page: i, characters: content.trim().length, width: page.view[2] - page.view[0], height: page.view[3] - page.view[1]};
    if (options['include-text'] === 'true') row.text = content;
    pages.push(row); text += content + '\n';
  }
  const outline = await doc.getOutline(), errors = [];
  if (config.expected_pages !== undefined && config.expected_pages !== doc.numPages) errors.push('Unexpected page count');
  if (config.require_outline && !outline?.length) errors.push('Outline missing');
  if (config.min_chars_per_page !== undefined && pages.some(p => p.characters < config.min_chars_per_page)) errors.push('Page below configured text threshold');
  // Some CJK fonts expose compatibility radicals; compare canonical meaning,
  // retain the unmodified extracted strings when --include-text is requested.
  const compact = value => value.normalize('NFKC').replace(/\s/g, '');
  for (const required of config.required_text || []) if (!compact(text).includes(compact(required))) errors.push('Required text absent');
  console.log(JSON.stringify({passed: !errors.length, file: path.basename(options.input), sha256: hash(bytes),
    page_count: doc.numPages, pages, outline: outline?.map(x => x.title) || [], errors,
    comparison_normalization: 'NFKC plus whitespace removal; extracted PDF bytes/text are not rewritten',
    not_checked: ['manual visual review', 'annotations/links', 'font fidelity', 'factual accuracy']}, null, 2));
  process.exitCode = errors.length ? 1 : 0;
} catch (error) { console.error(JSON.stringify({passed: false, error: error.message})); process.exitCode = 1; }
finally { await doc?.destroy(); }
