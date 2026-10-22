"""Local page for checking bank positions against Esri Wayback high-resolution imagery.

Usage: python src/review_server.py sadec_caolanh [port]      (then open http://localhost:8765)
Serves src/review_page.html and data/processed/<reach>/review_points.json (from review_sample.py).
Each answer is appended at once to data/processed/<reach>/accuracy_review.csv; the page resumes at
the first unanswered item. A re-answered item gets a new row (review_report.py keeps the last).
"""
import csv
import datetime
import http.server
import json
import pathlib
import sys
import threading

COLS = ['id', 'transect', 'side', 'explore', 'hotspot', 'imagery_release', 'imagery_capture_date',
        'imagery_source', 'compared_year', 'our_dist_m', 'user_dist_m', 'verdict', 'note', 'timestamp']
VERDICTS = {'clicked', 'cannot_see', 'skip'}
PAGE = pathlib.Path(__file__).with_name('review_page.html')

reach = sys.argv[1]
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
out = pathlib.Path('data/processed', reach)
points_raw = (out / 'review_points.json').read_bytes()
items = {i['id']: i for i in json.loads(points_raw)['items']}
answers = out / 'accuracy_review.csv'
lock = threading.Lock()


def answered():
    """Last answer per item id (rows are appended, so later rows win)."""
    if not answers.exists():
        return {}
    with open(answers, newline='', encoding='utf-8-sig') as f:
        return {r['id']: r for r in csv.DictReader(f)}


def num(v):
    return '' if v in (None, '') else float(v)


class Handler(http.server.BaseHTTPRequestHandler):
    def send(self, body, ctype='application/json', code=200):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]   # the page itself reads ?review
        if path in ('/', '/index.html'):
            self.send(PAGE.read_bytes(), 'text/html; charset=utf-8')
        elif path == '/points':
            self.send(points_raw)
        elif path == '/answered':
            self.send(json.dumps(answered()).encode())
        else:
            self.send(b'not found', 'text/plain', 404)

    def do_POST(self):
        if self.path != '/answer':
            return self.send(b'not found', 'text/plain', 404)
        try:
            a = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            it = items[a['id']]
            assert a['verdict'] in VERDICTS
            year = int(a['compared_year']) if a.get('compared_year') else ''
            our = next((b['dist_m'] for b in it['banks'] if b['year'] == year), '')
            row = {'id': it['id'], 'transect': it['transect'], 'side': it['side'], 'explore': it['explore'],
                   'hotspot': it['hotspot'], 'imagery_release': str(a.get('imagery_release', ''))[:40],
                   'imagery_capture_date': str(a.get('imagery_capture_date', ''))[:10],
                   'imagery_source': str(a.get('imagery_source', ''))[:40], 'compared_year': year,
                   'our_dist_m': our, 'user_dist_m': num(a.get('user_dist_m')) if a['verdict'] == 'clicked' else '',
                   'verdict': a['verdict'], 'note': str(a.get('note', ''))[:500],
                   'timestamp': datetime.datetime.now().isoformat(timespec='seconds')}
        except (KeyError, ValueError, TypeError, AssertionError) as e:
            return self.send(json.dumps({'error': repr(e)}).encode(), code=400)
        with lock:
            new = not answers.exists()
            with open(answers, 'a', newline='', encoding='utf-8-sig') as f:
                w = csv.DictWriter(f, COLS)
                if new:
                    w.writeheader()
                w.writerow(row)
        print(row['id'], row['verdict'], row['compared_year'], row['our_dist_m'], row['user_dist_m'], flush=True)
        self.send(json.dumps(row).encode())

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    print(f'{len(items)} items, {len(answered())} answered -> http://localhost:{port}  (Ctrl+C to stop)', flush=True)
    http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
