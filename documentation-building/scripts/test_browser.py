#!/usr/bin/env python3
"""Optional real-browser smoke tests against an isolated loopback fixture server."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import tempfile
import threading


def run(output, args):
    fixtures = output / 'fixtures'
    fixtures.mkdir()
    labels = {'report.html': ('en', 'Methodology example'),
              'report.zh-Hant.html': ('zh-Hant', '方法報告示例'),
              'manual.html': ('en', 'User guide example'),
              'slides.html': ('en', 'Static slide example')}
    for filename, (language, title) in labels.items():
        (fixtures / filename).write_text(f'''<!doctype html><html lang="{language}"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{font:18px sans-serif;max-width:850px;margin:24px auto;padding:16px}}
table{{width:100%;border-collapse:collapse}}td,th{{padding:12px;border:1px solid #bbb}}
@media print{{@page{{size:A4;margin:18mm}}body{{margin:0}}}}</style>
<main><h1 id="method">{title}</h1><p>Illustrative / 示意 — 2026-10-29</p>
<a href="#results">Results / 結果</a><h2 id="results">Results / 結果</h2>
<table><tr><th>Sample / 樣本</th><th>Count / 計數</th></tr><tr><td>A</td><td>2 / 3</td></tr></table>
<p>This is a constructed fixture, not a benchmark.</p></main></html>''', encoding='utf-8')
    (fixtures / 'overflow.html').write_text('<div style="width:2500px">Overflow fixture</div>')
    (fixtures / 'post.html').write_text('<h1>Blocked mutation fixture</h1><script>fetch("/mutate",{method:"POST"}).catch(()=>{});</script>')
    class Handler(SimpleHTTPRequestHandler):
        posts_received = 0

        def log_message(self, *_):
            pass

        def do_POST(self):
            Handler.posts_received += 1
            self.send_error(500)

    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(fixtures)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    results = []
    try:
        for filename in [*labels, 'overflow.html', 'post.html']:
            folder = output / filename.replace('.', '-')
            command = [args.node, str(Path(__file__).with_name('browser_documentation.mjs')),
                       '--url', f'http://127.0.0.1:{server.server_port}/{filename}',
                       '--playwright-from', args.playwright_from, '--output', str(folder)]
            if filename in labels:
                command.extend(['--ready', '#method', '--pdf', 'true'])
            if args.chromium:
                command.extend(['--chromium', args.chromium])
            result = subprocess.run(command, capture_output=True, text=True, timeout=90)
            record = json.loads((folder / 'browser-validation.json').read_text())
            expected = filename in labels
            if record['passed'] != expected or result.returncode != (0 if expected else 1):
                raise RuntimeError(f'{filename}: unexpected result: {record}; {result.stderr}')
            if expected:
                if not (folder / 'document.pdf').read_bytes().startswith(b'%PDF-'):
                    raise RuntimeError('No PDF export: ' + filename)
                for screen in ['desktop.png', 'mobile.png']:
                    if not (folder / screen).read_bytes().startswith(b'\x89PNG'):
                        raise RuntimeError('No screenshot: ' + filename)
            if filename == 'post.html' and not any(x['method'] == 'POST' for x in record['blocked']):
                raise RuntimeError('POST guard did not trigger')
            results.append({'fixture': filename, 'expected_pass': expected, 'matched': True})
        if Handler.posts_received:
            raise RuntimeError('Mutation reached the fixture server')
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    summary = {'passed': True, 'cases': results, 'server_post_requests': Handler.posts_received,
               'scope': 'Static fixtures only; no real Reveal runtime or production application tested'}
    (output / 'test-results.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--playwright-from', required=True)
    parser.add_argument('--node', default='node')
    parser.add_argument('--chromium')
    parser.add_argument('--output', help='New directory for inspectable fixtures/results; otherwise temporary')
    args = parser.parse_args()
    if args.output:
        output = Path(args.output).resolve()
        output.mkdir()
        run(output, args)
    else:
        with tempfile.TemporaryDirectory(prefix='documentation-browser-test-') as temp:
            run(Path(temp).resolve(), args)
