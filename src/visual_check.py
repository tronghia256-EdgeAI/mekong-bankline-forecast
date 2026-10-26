"""EXPLORATORY plan C (docs/exploratory_plan.md): blind visual check of analysis B on Esri Wayback imagery.

Usage:
  python src/visual_check.py sample          -> data/processed/visual_check/{items.json, key.csv}
  python src/visual_check.py serve [port]    -> http://localhost:8780 (src/visual_check_page.html);
                                                answers appended to data/processed/visual_check/answers.csv
  python src/visual_check.py report          -> results/p2/visual_check.md
Groups (seed 0): E_om all never-reported satellite-eroding units; E_rep 12 reported eroding; N_rep 24 reported units
below the 9.3 m floor; N_non 12 never-reported units below the floor. The page shows a neutral id only.
"""
import csv
import datetime
import http.server
import json
import pathlib
import sys
import threading

import numpy as np
import pandas as pd
from scipy.stats import beta

OUT = pathlib.Path('data/processed/visual_check')
PAGE = pathlib.Path(__file__).with_name('visual_check_page.html')
FLOOR = 9.3
N = {'E_rep': 12, 'N_rep': 24, 'N_non': 12}
Q1 = ['clear', 'possible', 'none', 'cannot_tell']
Q2 = ['yes', 'partly', 'no', 'cannot_tell']
COLS = ['id', 'q1_loss', 'q2_protection', 'note', 'old_release', 'old_capture', 'new_release', 'new_capture', 'timestamp']


def sample():
    d = pd.read_csv('data/processed/explore_reporting_units.csv')
    rep, ero, below = d['r_any report'] == 1, d.lab_p75_20 == 1, d.win_p75 < FLOOR
    rng = np.random.default_rng(0)
    pools = {'E_om': d[ero & ~rep], 'E_rep': d[ero & rep], 'N_rep': d[rep & below], 'N_non': d[~rep & below]}
    parts = [pools['E_om'].assign(group='E_om')]
    for g, n in N.items():
        p = pools[g]
        parts.append(p.iloc[np.sort(rng.choice(len(p), n, replace=False))].assign(group=g))
    s = pd.concat(parts)
    s = s.iloc[rng.permutation(len(s))].reset_index(drop=True)
    s['id'] = [f'V{i + 1:02d}' for i in range(len(s))]
    u = pd.read_csv('data/processed/units.csv')
    u = u[u.in_scope]
    items = []
    for r in s.itertuples():
        p = u[u.unit_2km == r.unit]
        items.append({'id': r.id, 'points': p[['lat', 'lon']].round(6).values.tolist(),
                      'center': [round(p.lat.median(), 6), round(p.lon.median(), 6)]})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'items.json').write_text(json.dumps({'items': items}), encoding='utf-8')
    s[['id', 'unit', 'group', 'channel', 'side', 'km', 'communes', 'win_p75', 'n_win']].to_csv(OUT / 'key.csv', index=False,
                                                                                            encoding='utf-8')
    print(s.group.value_counts().to_string(), f'\n{len(s)} items -> {OUT}')


def answered():
    f = OUT / 'answers.csv'
    if not f.exists():
        return {}
    with open(f, newline='', encoding='utf-8-sig') as fh:
        return {r['id']: r for r in csv.DictReader(fh)}


def serve(port):
    raw = (OUT / 'items.json').read_bytes()
    ids = {i['id'] for i in json.loads(raw)['items']}
    lock = threading.Lock()

    class H(http.server.BaseHTTPRequestHandler):
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
                self.send(raw)
            elif path == '/answered':
                self.send(json.dumps(answered()).encode())
            else:
                self.send(b'not found', 'text/plain', 404)

        def do_POST(self):
            if self.path != '/answer':
                return self.send(b'not found', 'text/plain', 404)
            try:
                a = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                assert a['id'] in ids and a['q1_loss'] in Q1 and a['q2_protection'] in Q2
                row = {k: str(a.get(k, ''))[:500 if k == 'note' else 40] for k in COLS[:-1]}
                row['timestamp'] = datetime.datetime.now().isoformat(timespec='seconds')
            except (KeyError, ValueError, TypeError, AssertionError) as e:
                return self.send(json.dumps({'error': repr(e)}).encode(), code=400)
            with lock:
                f = OUT / 'answers.csv'
                new = not f.exists()
                with open(f, 'a', newline='', encoding='utf-8-sig') as fh:
                    w = csv.DictWriter(fh, COLS)
                    if new:
                        w.writeheader()
                    w.writerow(row)
            print(row['id'], row['q1_loss'], row['q2_protection'], flush=True)
            self.send(json.dumps(row).encode())

        def log_message(self, *args):
            pass

    print(f'{len(ids)} items, {len(answered())} answered -> http://localhost:{port}  (Ctrl+C to stop)', flush=True)
    http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()


def ci(k, n):
    """Exact (Clopper-Pearson) 95% interval in %."""
    lo = beta.ppf(.025, k, n - k + 1) if k else 0.
    hi = beta.ppf(.975, k + 1, n - k) if k < n else 1.
    return f'{k}/{n} = {100 * k / n:.0f}% [{100 * lo:.0f}, {100 * hi:.0f}]' if n else '-'


def report():
    key = pd.read_csv(OUT / 'key.csv')
    a = pd.DataFrame(answered().values())
    d = key.merge(a, on='id', how='left')
    groups = ['E_om', 'E_rep', 'N_rep', 'N_non']
    names = {'E_om': 'eroding, never reported', 'E_rep': 'eroding, reported',
             'N_rep': 'reported, below floor', 'N_non': 'never reported, below floor'}
    L = ['# Visual check of analysis B on high-resolution imagery (EXPLORATORY, plan C)', '',
         'Generated by `python src/visual_check.py report`. Plan C of `docs/exploratory_plan.md` (written and committed before '
         'sampling). One reviewer (the owner), blind to the group; earliest vs latest Esri World Imagery Wayback release per '
         f'unit (other releases allowed). Answered {d.q1_loss.notna().sum()} of {len(d)}. Shares with exact 95% CIs; '
         '"seen" = answer other than cannot tell.', '',
         '| group | units | answered | Q1 loss clear | Q1 clear or possible | Q2 protection yes/partly | neither loss nor protection |',
         '|---|---|---|---|---|---|---|']
    for g in groups:
        x = d[d.group == g]
        q1 = x[x.q1_loss.isin(Q1[:3])]
        q2 = x[x.q2_protection.isin(Q2[:3])]
        both = x[x.q1_loss.isin(Q1[:3]) & x.q2_protection.isin(Q2[:3])]
        L.append(f'| {names[g]} | {len(x)} | {x.q1_loss.notna().sum()} | {ci((q1.q1_loss == "clear").sum(), len(q1))} | '
                 f'{ci(q1.q1_loss.isin(["clear", "possible"]).sum(), len(q1))} | '
                 f'{ci(q2.q2_protection.isin(["yes", "partly"]).sum(), len(q2))} | '
                 f'{ci((both.q1_loss.eq("none") & both.q2_protection.eq("no")).sum(), len(both))} |')
    L += ['', 'Imagery capture dates (old / new), median: '
          f'{pd.to_datetime(d.old_capture, errors="coerce").median():%Y-%m} / '
          f'{pd.to_datetime(d.new_capture, errors="coerce").median():%Y-%m}.' if d.q1_loss.notna().any() else '', '',
          '## Per unit', '', '| id | group | unit | communes | win_p75 (m) | Q1 loss | Q2 protection | old / new capture | note |',
          '|---|---|---|---|---|---|---|---|---|']
    for r in d.sort_values(['group', 'id']).itertuples():
        L.append(f'| {r.id} | {r.group} | {r.unit} | {r.communes} | {r.win_p75:.0f} | {r.q1_loss} | {r.q2_protection} | '
                 f'{r.old_capture} / {r.new_capture} | {r.note if isinstance(r.note, str) else ""} |')
    pathlib.Path('results/p2/visual_check.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L[:12]))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'sample':
        sample()
    elif cmd == 'serve':
        serve(int(sys.argv[2]) if len(sys.argv) > 2 else 8780)
    else:
        report()
