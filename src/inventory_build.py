"""P1: merge reported-erosion candidates and place them on the measured banks (commune level).

Usage: python src/inventory_build.py
Inputs: data/hotspots/reported_candidates.csv (G3 search), data/hotspots/candidates_*.csv (later searches; only rows
whose quote was found on the source page by inventory_verify.py), data/raw/satlo/odv_points_ag_dt_tg.csv (ODV/MARD
points with coordinates), data/processed/units.csv (reach_units.py), data/raw/admin/communes_mekong.geojson.
Each row's commune(s) are matched to the pre-2025 commune polygons; the bank points of that commune on the same
river give its reach units. Writes data/hotspots/inventory_draft.csv and prints a summary. status:
  measured            commune found and the commune has measured bank points on that river
  commune_unmeasured  commune found but none of its banks on that river are measured (e.g. behind a cù lao)
  unmatched           commune name not found (merged commune, typo, or not given)
  out_of_scope        canal/tributary/Vam Nao or unresolved channel, or event outside 2000-2024
"""
import glob
import json
import pathlib
import re
import unicodedata

import numpy as np
import pandas as pd
from rasterio.warp import transform

PROV = {'An Giang': 'An Giang', 'Dong Thap': 'Đồng Tháp', 'Tien Giang (old)': 'Tiền Giang', 'Đồng Tháp': 'Đồng Tháp'}
CHANNELS = {'Tien main': 'tien', 'Hau main': 'hau', 'islet bank': None}
CITY = re.compile(r'^(tp|tx|thanh pho|thi xa)\s')


def key(s):
    """Lower-case ASCII name without administrative prefix, '?' or parentheses."""
    s = re.sub(r'\(.*?\)|\?', '', str(s))
    s = unicodedata.normalize('NFD', s.replace('Đ', 'D').replace('đ', 'd'))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower().strip()
    s = re.sub(r'^(xa|phuong|p\.|p|thi tran|tt|huyen|thanh pho|tp|thi xa|tx)\.?\s+', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def communes():
    gj = json.loads(pathlib.Path('data/raw/admin/communes_mekong.geojson').read_text(encoding='utf-8'))
    c = pd.DataFrame([f['properties'] for f in gj['features']])[['province', 'district', 'district_type', 'commune']]
    c['ck'], c['dk'] = c.commune.map(key), c.district.map(key)
    c['city'] = c.district_type.isin(['Thành phố', 'Thị xã'])
    return c


def match(c, province, district, commune):
    """Rows of `c` for one commune name, narrowed by district (and city vs huyện) when ambiguous."""
    m = c[(c.province == province) & (c.ck == key(commune))]
    if len(m) > 1 and isinstance(district, str):
        d = m[m.dk == key(district)]
        if len(d) > 1:
            d = d[d.city == bool(CITY.match(key(district.replace('TP ', 'tp ').replace('TX ', 'tx '))) or
                                 district.startswith(('TP', 'TX')))]
        m = d if len(d) else m
    return m


def river_of(row):
    r = str(row.get('river', ''))
    return CHANNELS.get(row.get('channel')) or ('tien' if 'Tiền' in r else 'hau' if 'Hậu' in r else None)


def main():
    c, units = communes(), pd.read_csv('data/processed/units.csv')
    g3 = pd.read_csv('data/hotspots/reported_candidates.csv', dtype=str).assign(source_file='reported_candidates')
    new = [pd.read_csv(f, encoding='utf-8-sig', dtype=str).assign(source_file=pathlib.Path(f).stem)
           for f in sorted(glob.glob('data/hotspots/candidates_*.csv'))]
    new = [d[d.quote_found.eq('yes')] for d in new]
    df = pd.concat([g3] + new, ignore_index=True)
    out = []
    for _, r in df.iterrows():
        river, prov = river_of(r), PROV.get(r.province, r.province)
        year = pd.to_numeric(r.event_year, errors='coerce')
        rec = dict(r)
        rec.update(river_id=river, province_old=prov)
        if r.channel not in CHANNELS or river is None or not (2000 <= year <= 2024):
            rec['status'] = 'out_of_scope'
            out.append(rec)
            continue
        names = [n.strip() for n in re.split(r';|,|-| to ', str(r.commune_old)) if key(n)]
        hits = pd.concat([match(c, prov, r.district_old, n) for n in names]) if names else c.iloc[:0]
        if hits.empty:
            rec['status'] = 'unmatched'
            out.append(rec)
            continue
        on = units[(units.river == river) & units.commune.isin(hits.commune) & units.district.isin(hits.district)
                   & units.province.eq(prov)]
        rec.update(communes_matched='; '.join(hits.district + ' / ' + hits.commune), n_bank_points=len(on),
                   units_2km='; '.join(sorted(on.unit_2km.unique())), units_5km='; '.join(sorted(on.unit_5km.unique())),
                   status='measured' if len(on) else 'commune_unmeasured')
        out.append(rec)

    # ODV/MARD points with coordinates: nearest measured bank point of the same river within 1 km
    odv = pd.read_csv('data/raw/satlo/odv_points_ag_dt_tg.csv', dtype={'lon': str})
    odv = odv[odv.channel.isin(['Tien main', 'Hau main'])]
    ux, uy = transform('EPSG:4326', 'EPSG:32648', units.lon.tolist(), units.lat.tolist())
    for _, r in odv.iterrows():
        river = CHANNELS[r.channel]
        x, y = transform('EPSG:4326', 'EPSG:32648', [float(str(r.lon).replace(',', '.'))], [r.lat])
        d = np.hypot(np.array(ux) - x[0], np.array(uy) - y[0])
        d[(units.river != river).to_numpy()] = np.inf
        i = d.argmin()
        rec = dict(site_id=f'ODV{r.stt}', province=r.province, province_old=r.province, river_id=river,
                   channel=r.channel, hamlet_or_landmark=r.dia_danh, length_m=r.dai_m, severity=r.muc_do_canh_bao,
                   source_type='odv_mard_points', source_file='odv_points_ag_dt_tg', notes=r.note, lat=r.lat,
                   lon=r.lon, unit_type='điểm', confidence='medium')
        if d[i] <= 1000:
            u = units.iloc[i]
            rec.update(communes_matched=f'{u.district} / {u.commune}', n_bank_points=1, units_2km=u.unit_2km,
                       units_5km=u.unit_5km, status='measured', notes=f'{r.note} | nearest bank {d[i]:.0f} m')
        else:
            rec.update(status='commune_unmeasured', notes=f'{r.note} | nearest measured bank {d[i]:.0f} m')
        out.append(rec)

    inv = pd.DataFrame(out)
    inv.to_csv('data/hotspots/inventory_draft.csv', index=False, encoding='utf-8-sig')
    print(f'{len(inv)} rows:', inv.status.value_counts().to_dict())
    s = inv[inv.status.isin(['measured', 'commune_unmeasured', 'unmatched'])]
    print(pd.crosstab([s.province_old, s.river_id], s.status).to_string())
    print('\nunmatched:', '; '.join(f'{r.site_id} {r.district_old}/{r.commune_old}' for _, r in
                                    inv[inv.status == 'unmatched'].iterrows()))
    cu = inv[inv.status == 'commune_unmeasured']
    print('\ncommune_unmeasured by commune:')
    print(cu.groupby(['river_id', 'communes_matched'], dropna=False).size().sort_values(ascending=False).to_string())


if __name__ == '__main__':
    main()
