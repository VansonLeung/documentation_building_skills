#!/usr/bin/env node
// Optional dependency: an existing Playwright installation and Chromium.
// Never installs packages, clicks controls, edits documents, or changes server data.
import {createRequire} from 'node:module';
import path from 'node:path';
import fs from 'node:fs/promises';

const args = process.argv.slice(2), options = {};
if (args.includes('--help')) { console.log('See references/pdf-and-delivery.md'); process.exit(0); }
for (let i = 0; i < args.length; i += 2) {
  if (!args[i]?.startsWith('--') || !args[i + 1]) throw new Error('Expected --option value');
  options[args[i].slice(2)] = args[i + 1];
}
const target = new URL(options.url);
if (target.protocol !== 'http:' || !['127.0.0.1', 'localhost', '[::1]'].includes(target.hostname) || target.username || target.password) {
  throw new Error('Use a loopback HTTP preview without credentials');
}
if (!options.output) throw new Error('--output directory is required');
const output = path.resolve(options.output);
// A fresh directory prevents mixing old screenshots/PDFs with new results.
await fs.mkdir(output);
const require = options['playwright-from']
  ? createRequire(path.join(path.resolve(options['playwright-from']), 'package.json'))
  : createRequire(import.meta.url);
let browser, context;
const report = {passed: false, url: target.href, checks: [], blocked: [],
  not_checked: ['translation', 'fact accuracy', 'manual visual review', 'interactive controls',
                'PDF text/bookmarks/pagination', 'CSS background images', 'audio quality/seeking']};
try {
  const {chromium} = require('playwright');
  browser = await chromium.launch({headless: true, ...(options.chromium ? {executablePath: options.chromium} : {})});
  context = await browser.newContext({serviceWorkers: 'block', reducedMotion: 'reduce'});
  // GET/HEAD restriction is a network guard, not proof the server is read-only.
  await context.route('**/*', async route => {
    const req = route.request(), u = new URL(req.url());
    if (['data:', 'blob:'].includes(u.protocol)) return route.continue();
    if (u.origin !== target.origin || !['GET', 'HEAD'].includes(req.method())) {
      report.blocked.push({method: req.method(), url: u.href});
      return route.abort();
    }
    return route.continue();
  });
  // Prevent websocket side effects on previews. Requires Playwright >= 1.48.
  if (typeof context.routeWebSocket !== 'function') throw new Error('Need Playwright >= 1.48 for websocket blocking');
  await context.routeWebSocket('**/*', socket => { report.blocked.push({method: 'WEBSOCKET', url: socket.url()}); socket.close(); });
  const page = await context.newPage(), errors = [], badResponses = [], failed = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', r => { if (r.status() >= 400) badResponses.push({status: r.status(), url: r.url()}); });
  page.on('requestfailed', req => failed.push({url: req.url(), error: req.failure()?.errorText}));
  for (const [name, width, height] of [['desktop', 1440, 1000], ['mobile', 390, 844]]) {
    await page.setViewportSize({width, height});
    const response = await page.goto(target.href, {waitUntil: 'networkidle', timeout: 30000});
    if (!response?.ok()) throw new Error('Preview failed to load');
    if (options.ready) await page.locator(options.ready).waitFor({state: 'visible'});
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(() => [...document.images].every(i => i.complete), null, {timeout: 10000});
    const state = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
      brokenImages: [...document.images].filter(i => !i.naturalWidth).length,
      media: [...document.querySelectorAll('audio,video')].map(m => ({autoplay: m.autoplay, paused: m.paused}))
    }));
    await page.screenshot({path: path.join(output, name + '.png'), fullPage: true});
    report.checks.push({name, ...state});
  }
  if (options.pdf === 'true') {
    await page.setViewportSize({width: 1280, height: 1000});
    await page.emulateMedia({media: 'print', colorScheme: 'light'});
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({path: path.join(output, 'document.pdf'), format: 'A4', preferCSSPageSize: true,
      printBackground: true, tagged: true, outline: true});
    report.pdf_exported = true;
  }
  report.page_errors = errors; report.http_errors = badResponses; report.failed_requests = failed;
  report.passed = !errors.length && !badResponses.length && !failed.length && !report.blocked.length &&
    report.checks.every(c => !c.overflow && !c.brokenImages && c.media.every(m => !m.autoplay && m.paused));
} catch (e) { report.error = e.message; }
finally {
  await browser?.close();
  await fs.writeFile(path.join(output, 'browser-validation.json'), JSON.stringify(report, null, 2) + '\n');
}
console.log(JSON.stringify(report, null, 2));
process.exitCode = report.passed ? 0 : 1;
