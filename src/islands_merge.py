"""P1: one table for all river-island rings (banklines island mode), for review and labels.

Usage: python src/islands_merge.py
Reads data/tiles.json (islands), data/processed/isl_*/{bank_positions,trends}.csv and data/processed/units.csv; writes
data/processed/islands/{bank_positions,trends}.csv with transect = island number x 1000 + ring transect and the
columns channel and ring_transect. Only transect-sides kept in units.csv are written (ring banks that duplicate a
main-channel bank are left out), so a review sample never lands on a bank already checked on the main channel.
"""
import json
import pathlib

import pandas as pd


def main():
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    keep = pd.read_csv('data/processed/units.csv')[['channel', 'transect', 'side']]
    out = pathlib.Path('data/processed/islands')
    out.mkdir(parents=True, exist_ok=True)
    for name in ('bank_positions', 'trends'):
        parts = []
        for k, isl in enumerate(sorted(cfg['islands']), 1):
            f = pathlib.Path('data/processed', isl, f'{name}.csv')
            if f.exists():
                d = pd.read_csv(f).merge(keep[keep.channel == isl].drop(columns='channel'), on=['transect', 'side'])
                parts.append(d.assign(channel=isl, ring_transect=d.transect, transect=k * 1000 + d.transect))
        pd.concat(parts).to_csv(out / f'{name}.csv', index=False)
    t = pd.read_csv(out / 'trends.csv')
    print(f'{t.channel.nunique()} islands, {len(t)} transect-sides with a trend:',
          t.groupby('side').size().to_dict(), t.kind.value_counts().to_dict())


if __name__ == '__main__':
    main()
