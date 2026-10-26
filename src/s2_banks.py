"""P3 R1: Sentinel-2 bank positions on the Landsat transects (same tiles, islands, transect ids and bank rule).

Usage: python src/s2_banks.py <tile> [<tile> ...]   per tile: data/processed/s2/<tile>/bank_positions.csv
       python src/s2_banks.py stitch                data/processed/s2/{tien,hau,islands}/bank_positions.csv
Geometry (centerline or island ring, transects, open-river edge k0, belt limit) is rebuilt from the tile's Landsat stack
exactly as banklines.main does, so transect ids are the Landsat ones; each transect is then sampled on the 10 m grid
of data/raw/s2/<tile>/mndwi_<year>.tif and banklines.positions runs with px = 10 (canal-filter disc and island area at
the same physical size). Along-transect constants (STEP, MIN_LAND, REFINE, BELT_MARGIN) are in metres / 5 m samples and
unchanged. Other-river masking (own_river, metres) and the > 2% nodata rule as in banklines.load; spikes as in
banklines.main. Stitching reuses the Landsat stitched keys: (tile, tile_transect, normal) -> stitched transect and side;
islands as islands_merge.py (units.csv rows only, transect = island no. x 1000 + ring transect).
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import banklines as bl  # noqa: E402

PX = 10.0
SRC = 's2'


def s2_sides(sides, tf30, tf10):
    """Landsat transect-sides resampled onto the Sentinel-2 grid (k0 and belt limit are along-transect, unchanged)."""
    out = []
    for s in sides:
        r, c = bl.to_rc(bl.to_xy(np.column_stack([s[6], s[7]]), tf30), tf10)
        out.append(s[:6] + (r, c, np.round(r).astype(int), np.round(c).astype(int)) + s[10:])
    return out


def load_s2(tile):
    files = sorted(pathlib.Path('data/raw', SRC, tile).glob('mndwi_*.tif'))
    years = np.array([int(f.stem.split('_')[1]) for f in files])
    pairs = [bl.read(f) for f in files]
    stack, tf = np.array([p[0] for p in pairs]), pairs[0][1]
    inside = bl.own_river(tile, stack.shape[1:], tf)
    share = np.isnan(stack[:, inside]).mean(axis=1)
    keep = share <= bl.MAX_NODATA
    stack[:, ~inside] = np.nan
    return years, share, keep, stack, tf


def run_tile(tile):
    years30, stack30, tf30 = bl.load(tile)
    cfg, t = bl.tile(tile)
    if t and t.get('island'):
        _, sides = bl.island_geometry(stack30, tf30, np.array(cfg['islands'][tile]['polygon']))
    else:
        _, sides = bl.geometry(stack30, tf30, narrow=bool((t or {}).get('narrow')))
    del stack30
    meta = pd.DataFrame([s[:6] for s in sides], columns=['transect', 'side', 'cx', 'cy', 'nx', 'ny'])
    ref = pd.read_csv(f'data/processed/{tile}/bank_positions.csv').drop_duplicates(['transect', 'side'])
    chk = meta.merge(ref[['transect', 'side', 'cx', 'cy']], on=['transect', 'side'], suffixes=('', '_l'))
    assert len(chk) == len(ref) == len(meta) and np.allclose(chk.cx, chk.cx_l) and np.allclose(chk.cy, chk.cy_l), \
        f'{tile}: rebuilt geometry differs from the Landsat output'
    years, share, keep, stack, tf = load_s2(tile)
    sides10 = s2_sides(sides, tf30, tf)
    pos = pd.concat({y: bl.positions(m, sides10, px=PX) for y, m in zip(years[keep], stack[keep])},
                    names=['year']).reset_index()
    df = meta.merge(pos, on=['transect', 'side']).sort_values(['transect', 'side', 'year'])
    valid = df.dropna(subset=['dist_m'])
    g = valid.groupby(['transect', 'side']).dist_m
    prev, nxt = valid.dist_m - g.shift(1), g.shift(-1) - valid.dist_m
    df['spike'] = ((prev.abs() > bl.JUMP) & (nxt.abs() > bl.JUMP) & (np.sign(prev) != np.sign(nxt))).reindex(
        df.index, fill_value=False)
    out = pathlib.Path('data/processed', SRC, tile)
    out.mkdir(parents=True, exist_ok=True)
    df[['transect', 'side', 'cx', 'cy', 'nx', 'ny', 'year', 'dist_m', 'spike']].to_csv(out / 'bank_positions.csv',
                                                                                        index=False)
    pd.DataFrame({'year': years, 'nodata_share': share.round(4), 'kept': keep}).to_csv(out / 'years.csv', index=False)
    print(f'{tile}: years kept {years[keep].tolist()}, dropped {years[~keep].tolist()} '
          f'(nodata {dict(zip(years.tolist(), share.round(3).tolist()))}); valid {df.dist_m.notna().mean():.0%}',
          flush=True)


def stitch():
    """Stitched rivers and the island table on the Landsat ids."""
    root = pathlib.Path('data/processed', SRC)
    k = lambda d: d.assign(nxr=d.nx.round(6), nyr=d.ny.round(6))
    for river in ('tien', 'hau'):
        st = pd.read_csv(f'data/processed/{river}/bank_positions.csv')
        key = k(st.drop_duplicates(['tile', 'tile_transect', 'side']))[['transect', 'side', 'chainage_m', 'tile',
                                                                        'tile_transect', 'nxr', 'nyr']]
        parts = []
        for tile in key.tile.unique():
            d = k(pd.read_csv(root / tile / 'bank_positions.csv')).rename(columns={'transect': 'tile_transect',
                                                                                   'side': 'tile_side'})
            parts.append(d.assign(tile=tile).merge(key, on=['tile', 'tile_transect', 'nxr', 'nyr']))
        df = pd.concat(parts).drop(columns=['nxr', 'nyr', 'tile_side']).sort_values(['transect', 'side', 'year'])
        assert not df.duplicated(['transect', 'side', 'year']).any()
        first = ['transect', 'side', 'chainage_m', 'tile', 'tile_transect']
        (root / river).mkdir(parents=True, exist_ok=True)
        df[first + [c for c in df.columns if c not in first]].to_csv(root / river / 'bank_positions.csv', index=False)
        print(f'{river}: {df.groupby(["transect", "side"]).ngroups} of '
              f'{st.groupby(["transect", "side"]).ngroups} Landsat transect-sides')
    cfg = json.loads(pathlib.Path('data/tiles.json').read_text())
    keep = pd.read_csv('data/processed/units.csv')[['channel', 'transect', 'side']]
    parts = []
    for n, isl in enumerate(sorted(cfg['islands']), 1):
        d = pd.read_csv(root / isl / 'bank_positions.csv').merge(keep[keep.channel == isl].drop(columns='channel'),
                                                                 on=['transect', 'side'])
        parts.append(d.assign(channel=isl, ring_transect=d.transect, transect=n * 1000 + d.transect))
    (root / 'islands').mkdir(parents=True, exist_ok=True)
    pd.concat(parts).to_csv(root / 'islands' / 'bank_positions.csv', index=False)


def main():
    args = sys.argv[1:]
    if args == ['stitch']:
        return stitch()
    for tile in args:
        run_tile(tile)


if __name__ == '__main__':
    main()
