"""Accuracy of satellite bank positions against the human clicks from review_server.py.

Usage: python src/review_report.py sadec_caolanh
Reads data/processed/<reach>/accuracy_review.csv (last answer per item; explore items left out),
bank_positions.csv (current positions, not the value saved at click time), trends.csv and
review_points.json (items flagged unstable are reported as their own group only);
prints and writes results/p0/<reach>_accuracy.md.
error = our_dist_m - user_dist_m (positive = our bank too far landward).
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd


def stats(e):
    a = e.abs()
    return (f'| {len(e)} | {e.mean():+.1f} | {a.median():.1f} | {np.sqrt((e ** 2).mean()):.1f} | '
            f'{a.quantile(.9):.1f} |' if len(e) else '| 0 | - | - | - | - |')


def main():
    reach = sys.argv[1]
    src = pathlib.Path('data/processed', reach)
    f = src / 'accuracy_review.csv'
    try:
        df = pd.read_csv(f, encoding='utf-8-sig')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['id', 'explore', 'hotspot', 'verdict', 'imagery_capture_date',
                                   'our_dist_m', 'user_dist_m'])
    df = df.drop_duplicates('id', keep='last')
    df = df[~df.explore.astype(str).eq('True')]
    tr = pd.read_csv(src / 'trends.csv')
    annual = tr[tr.stable].lrr.abs().median()

    # compare with the CURRENT positions (the algorithm may have changed since the click was saved)
    bp = pd.read_csv(src / 'bank_positions.csv')[['transect', 'side', 'year', 'dist_m']]
    df = df.drop(columns='our_dist_m').merge(bp.rename(columns={'year': 'compared_year', 'dist_m': 'our_dist_m'}),
                                             on=['transect', 'side', 'compared_year'], how='left')
    ok = df[df.verdict.eq('clicked')].dropna(subset=['our_dist_m', 'user_dist_m']).copy()
    ok['err'] = ok.our_dist_m.astype(float) - ok.user_dist_m.astype(float)
    flagged = {i['id'] for i in json.loads((src / 'review_points.json').read_text())['items'] if i.get('unstable')}
    bad, ok = ok[ok.id.isin(flagged)], ok[~ok.id.isin(flagged)]
    month = pd.to_datetime(ok.imagery_capture_date, errors='coerce').dt.month
    groups = [('all', ok.err),
              ('hotspot (abs lrr > 5 m/yr)', ok.err[ok.hotspot.astype(str).eq('True')]),
              ('other stable banks', ok.err[~ok.hotspot.astype(str).eq('True')]),
              ('imagery Jan-Apr (dry)', ok.err[month.between(1, 4)]),
              ('imagery May-Dec (wet/transition)', ok.err[month.between(5, 12)]),
              ('imagery date unknown', ok.err[month.isna()]),
              ('flagged unstable (not in rows above)', bad.err)]
    counts = df.verdict.value_counts()
    lines = [f'# Bank position accuracy vs high-resolution imagery: {reach}', '',
             f'Source: `{f.as_posix()}` (Esri World Imagery Wayback, clicks by hand on the transect line; '
             'last answer per item, explore items excluded).',
             f'Answered: {len(df)} (clicked {counts.get("clicked", 0)}, cannot see {counts.get("cannot_see", 0)}, '
             f'skipped {counts.get("skip", 0)}). error = ours - clicked, positive = our bank too far landward.', '',
             '| Group | n | Mean bias (m) | Median abs error (m) | RMSE (m) | P90 abs error (m) |',
             '|---|---|---|---|---|---|']
    lines += [f'| {name} {stats(e)}' for name, e in groups]
    if len(ok):
        mae = ok.err.abs().median()
        lines += ['', f'Verdict: median abs error {mae:.1f} m = {mae / annual:.1f} x the median annual change of stable '
                      f'transect-sides ({annual:.1f} m/yr), so a single year of change is '
                      f'{"detectable" if mae < annual else "below the measurement error"} on a typical bank.']
    else:
        lines += ['', f'Verdict: no clicked items yet (median annual change {annual:.1f} m/yr).']
    text = '\n'.join(lines) + '\n'
    print(text)
    out = pathlib.Path('results/p1' if reach in ('tien', 'hau', 'islands') else 'results/p0')   # stitched P1 rivers
    out.mkdir(parents=True, exist_ok=True)
    (out / f'{reach}_accuracy.md').write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
