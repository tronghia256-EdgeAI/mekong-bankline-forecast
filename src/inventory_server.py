"""Local page for the owner's review of the reported-erosion inventory (one row at a time).

Usage: python src/inventory_server.py [port]      (then open http://localhost:8770)
Serves src/inventory_page.html and the in-scope rows of data/hotspots/inventory_draft.csv (inventory_build.py) with
their matched commune polygons and measured bank points. Each answer is appended at once to
data/hotspots/inventory_review.csv (site_id, verdict, lat, lon, note, timestamp); later rows win.
verdict: keep (right river and commune, location = commune bank), keep_point (owner clicked the exact place),
reject (not main-channel bank erosion, or wrong), duplicate (same site-event as another row; note which), unsure.
"""
import csv
import datetime
import http.server
import json
import math
import pathlib
import sys
import threading

import pandas as pd
from shapely.geometry import mapping, shape

COLS = ['site_id', 'verdict', 'lat', 'lon', 'note', 'timestamp']
VERDICTS = {'keep', 'keep_point', 'reject', 'duplicate', 'unsure'}
SHOW = ['site_id', 'status', 'province_old', 'district_old', 'commune_old', 'hamlet_or_landmark', 'river', 'bank',
        'channel', 'event_year', 'severity', 'length_m', 'unit_type', 'source_type', 'confidence', 'notes', 'quote',
        'source_url', 'source_ref', 'source_date', 'communes_matched', 'units_2km', 'lat', 'lon']
PAGE = pathlib.Path(__file__).with_name('inventory_page.html')
ORDER = {'measured': 0, 'commune_unmeasured': 1, 'unmatched': 2}

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
answers = pathlib.Path('data/hotspots/inventory_review.csv')
lock = threading.Lock()


def clean(v):
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else v


def build():
    inv = pd.read_csv('data/hotspots/inventory_draft.csv', encoding='utf-8-sig', dtype=str)
    inv = inv[inv.status.isin(ORDER)].copy()
    inv['o'] = inv.status.map(ORDER)
    inv = inv.sort_values(['o', 'province_old', 'river_id', 'event_year'])
    gj = json.loads(pathlib.Path('data/raw/admin/communes_mekong.geojson').read_text(encoding='utf-8'))
    geom = {(f['properties']['district'], f['properties']['commune']): f['geometry'] for f in gj['features']}
    units = pd.read_csv('data/processed/units.csv')
    items = []
    for _, r in inv.iterrows():
        it = {k: clean(r.get(k)) for k in SHOW}
        pairs = [tuple(x.split(' / ', 1)) for x in str(r.communes_matched).split('; ') if ' / ' in x]
        it['polygons'] = [mapping(shape(geom[p]).simplify(0.0003)) for p in pairs if p in geom]
        u = units[(units.river == r.river_id) & units.apply(lambda x: (x.district, x.commune) in pairs, axis=1)]
        it['banks'] = u[['lat', 'lon']].round(6).values.tolist()
        items.append(it)
    return items


items = build()
items_raw = json.dumps({'items': items}, ensure_ascii=False).encode()
known = {i['site_id'] for i in items}


def answered():
    if not answers.exists():
        return {}
    with open(answers, newline='', encoding='utf-8-sig') as f:
        return {r['site_id']: r for r in csv.DictReader(f)}


class Handler(http.server.BaseHTTPRequestHandler):
    def send(self, body, ctype='application/json', code=200):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            self.send(PAGE.read_bytes(), 'text/html; charset=utf-8')
        elif path == '/items':
            self.send(items_raw)
        elif path == '/answered':
            self.send(json.dumps(answered(), ensure_ascii=False).encode())
        else:
            self.send(b'not found', 'text/plain', 404)

    def do_POST(self):
        if self.path != '/answer':
            return self.send(b'not found', 'text/plain', 404)
        try:
            a = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            assert a['site_id'] in known and a['verdict'] in VERDICTS
            row = {'site_id': a['site_id'], 'verdict': a['verdict'],
                   'lat': round(float(a['lat']), 6) if a.get('lat') not in (None, '') else '',
                   'lon': round(float(a['lon']), 6) if a.get('lon') not in (None, '') else '',
                   'note': str(a.get('note', ''))[:1000],
                   'timestamp': datetime.datetime.now().isoformat(timespec='seconds')}
            assert row['verdict'] != 'keep_point' or row['lat'] != ''
        except (KeyError, ValueError, TypeError, AssertionError) as e:
            return self.send(json.dumps({'error': repr(e)}).encode(), code=400)
        with lock:
            new = not answers.exists()
            with open(answers, 'a', newline='', encoding='utf-8-sig') as f:
                w = csv.DictWriter(f, COLS)
                if new:
                    w.writeheader()
                w.writerow(row)
        print(row['site_id'], row['verdict'], row['lat'], row['lon'], flush=True)
        self.send(json.dumps(row).encode())

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    print(f'{len(items)} rows, {len(answered())} answered -> http://localhost:{port}  (Ctrl+C to stop)', flush=True)
    http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
