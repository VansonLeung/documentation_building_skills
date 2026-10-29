#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {args, hash} from './presentation_common.mjs';

const options = args(['output']);
if (options.help) { console.log('create_presentation.mjs --output <new-directory>'); process.exit(0); }
if (!options.output) throw Error('--output is required');
const here = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(here, '../assets/presentation');
const require = createRequire(import.meta.url);
const revealRoot = path.resolve(path.dirname(require.resolve('reveal.js')), '..');
const revealPackage = JSON.parse(await fs.readFile(path.join(revealRoot, 'package.json'), 'utf8'));
// Resolve required vendor files before creating the destination.
const vendors = [['dist/reveal.js', 'reveal.js'], ['dist/reveal.css', 'reveal.css'], ['LICENSE', 'reveal-LICENSE.txt']];
for (const [file] of vendors) await fs.access(path.join(revealRoot, file));
const output = path.resolve(options.output);
await fs.mkdir(output); // Existing destination is never replaced.
const records = [];
for (const entry of await fs.readdir(source, {withFileTypes: true})) {
  if (!entry.isFile()) throw Error('Only regular template files are supported');
  const data = await fs.readFile(path.join(source, entry.name));
  await fs.writeFile(path.join(output, entry.name), data);
  records.push({file: entry.name, sha256: hash(data)});
}
await fs.mkdir(path.join(output, 'vendor'));
for (const [file, name] of vendors) {
  const data = await fs.readFile(path.join(revealRoot, file));
  await fs.writeFile(path.join(output, 'vendor', name), data);
  records.push({file: 'vendor/' + name, sha256: hash(data)});
}
await fs.writeFile(path.join(output, 'template-manifest.json'), JSON.stringify({
  schema_version: 1, template: 'unbranded-bilingual-presentation', reveal: revealPackage.version,
  note: 'Synthetic teaching examples. Maintained HTML is the editing source.', files: records
}, null, 2) + '\n');
console.log(JSON.stringify({passed: true, output, files: records.length, entry: 'deck.html', language: 'deck.zh-Hant.html'}));
