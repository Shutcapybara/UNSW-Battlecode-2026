"""Local integration fixtures, based on the site's inspected HTML (no account data).

Run: python3 browser-extension/tests/server.py
Then open http://127.0.0.1:8765/team/battles or /tests/dom.html.
This server is only a test fixture and is not included in the installable ZIP.
"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import html
import time

ROOT = Path(__file__).resolve().parent.parent
SCENARIO = 'normal'

def row(battle, kind, opponent):
    return f'''<tr><td><time datetime="2026-09-21T07:13:54.337Z">21 Sept, 16:43</time></td>
    <td>{kind}</td><td>+24</td><td><a href="/teams/7"><span class="name">Our team</span> 1552</a></td>
    <td>W 4 – 1 L</td><td><a href="/teams/64">{html.escape(opponent)}</a></td>
    <td><a href="/battles/{battle}">Watch replay</a></td></tr>'''

def listing(page):
    rows = row(3558, 'Unranked', 'Alpha 1691') + row(3482, 'Ranked', 'Beta 1514') if page == 1 else row(3450, 'Ranked', 'Alpha 1542') + row(3220, 'Unranked', 'Gamma 1561')
    nav = '<a href="?page=2">Next</a>' if page == 1 else '<a href="?page=1">Prev</a>'
    return f'''<!doctype html><meta charset="utf-8"><title>Battlecode filter test</title>
    <link rel="stylesheet" href="/content.css"><style>body{{background:#111827;color:#e5e7eb;font:16px system-ui;margin:32px}}a{{color:#7dd3fc}}button{{padding:6px;margin:4px}}td,th{{padding:12px}}</style>
    <p>LOCAL TEST FIXTURE · <a href="/tests/dom.html">Parser tests</a> · <a href="/scenario/normal">Normal</a> · <a href="/scenario/failure">Failed lookup</a> · <a href="/scenario/slow">Slow lookup</a> · <a href="/scenario/login">Expired session</a> · <a href="/scenario/page-failure">Pagination failure</a></p>
    <main><h1>Your battles</h1><p>4 battles</p><div class="ui-toolbar"><input aria-label="Search opponents" type="search"><label><input type="checkbox" checked>Ranked</label><label><input type="checkbox" checked>Unranked</label></div>
    <div class="battle-table"><table><thead><tr>{''.join(f'<th>{h}</th>' for h in ['Time','Type','Δ Rating','Your team','Score','Opponent',''])}</tr></thead><tbody>{rows}</tbody></table></div>
    <nav aria-label="Pages">{nav}</nav></main><script src="/tests/mock-storage.js"></script><script src="/core.js"></script><script src="/content.js"></script>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global SCENARIO
        url = urlparse(self.path)
        path = url.path
        if path.startswith('/scenario/'):
            SCENARIO = path.split('/')[-1]
            self.send_response(302)
            self.send_header('Location', '/team/battles?clear-cache=1')
            self.end_headers()
            return
        code = 200
        mime = 'text/html; charset=utf-8'
        if path == '/team/battles':
            page = int(parse_qs(url.query).get('page', ['1'])[0])
            # Only fail fetches; keep the browser UI accessible.
            if SCENARIO == 'login' and self.headers.get('Sec-Fetch-Dest') == 'empty':
                body = '<main><h1>Sign in</h1></main>'
            elif SCENARIO == 'page-failure' and page == 2:
                code, body = 503, 'Temporary failure'
            else:
                body = listing(page)
        elif path.startswith('/battles/'):
            battle = path.split('/')[-1]
            if SCENARIO == 'slow':
                time.sleep(3)
            if SCENARIO == 'failure' and battle == '3482':
                code, body = 503, 'Temporary failure'
            else:
                versions = {'3558': 'v5 · latest', '3482': 'v4 · previous', '3450': 'v1 · original'}
                label = f'<p class="ui-muted mt-3">Your bot: {versions[battle]}</p>' if battle in versions else '<p>Version unavailable</p>'
                body = f'<main>{label}<h1><a href="/teams/7">Our team</a> vs <a href="/teams/64">Opponent</a></h1></main>'
        else:
            file = (ROOT / path.lstrip('/')).resolve()
            if not file.is_relative_to(ROOT) or not file.is_file():
                code, body = 404, 'Not found'
            else:
                body = file.read_text()
                mime = {'.js': 'text/javascript', '.css': 'text/css'}.get(file.suffix, mime)
        data = body.encode()
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except BrokenPipeError:
            pass

if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
