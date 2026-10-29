import http from 'node:http';
import path from 'node:path';
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';

export const hash = bytes => createHash('sha256').update(bytes).digest('hex');
export function args(allowed) {
  const options = {}, values = process.argv.slice(2);
  for (let i = 0; i < values.length; i += 2) {
    if (values[i] === '--help') return {help: true};
    const key = values[i]?.slice(2);
    if (!values[i]?.startsWith('--') || !allowed.includes(key) || !values[i + 1]) throw Error('Expected supported --option value');
    if (key in options) throw Error('Duplicate option: ' + key);
    options[key] = values[i + 1];
  }
  return options;
}
export async function serveDirectory(directory) {
  const root = await fs.realpath(directory), inputs = new Map();
  const types = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.json': 'application/json'};
  const server = http.createServer(async (req, res) => {
    if (!['GET', 'HEAD'].includes(req.method)) { res.writeHead(405); res.end(); return; }
    try {
      const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      if (name.split('/').some(s => s.startsWith('.') || s === 'node_modules')) { res.writeHead(403); res.end(); return; }
      const file = await fs.realpath(path.resolve(root, '.' + (name === '/' ? '/deck.html' : name)));
      if (!file.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
      const data = await fs.readFile(file), relative = path.relative(root, file).split(path.sep).join('/');
      inputs.set(relative, {file: relative, bytes: data.length, sha256: hash(data)});
      res.writeHead(200, {'Content-Type': types[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store'});
      res.end(req.method === 'HEAD' ? undefined : data);
    } catch { res.writeHead(404); res.end('Not found'); }
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return {origin: `http://127.0.0.1:${server.address().port}`, inputs,
    close: () => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); })};
}
export async function guardedContext(browser, origin, options = {}) {
  const blocked = [];
  const context = await browser.newContext({serviceWorkers: 'block', reducedMotion: 'reduce', ...options});
  await context.route('**/*', route => {
    const request = route.request(), url = new URL(request.url());
    if (['data:', 'blob:'].includes(url.protocol)) return route.continue();
    if (url.origin !== origin || !['GET', 'HEAD'].includes(request.method())) {
      blocked.push({method: request.method(), url: url.href}); return route.abort();
    }
    return route.continue();
  });
  await context.routeWebSocket('**/*', socket => { blocked.push({method: 'WEBSOCKET', url: socket.url()}); socket.close(); });
  return {context, blocked};
}
