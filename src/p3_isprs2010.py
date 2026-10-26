"""P3 R3 (illustration, not a gate): the 2010 deterministic bank forecast checked against our measured banks.

Usage: python src/p3_isprs2010.py
Source: Lam Dao Nguyen et al. 2010, ISPRS Archives XXXVIII-8, pp. 287-292 (open access; PDF kept local in papers/,
never committed). The paper extrapolates a weighted linear regression (DSAS transects, banks 1966/1989-2009) to 2015 and
2020 and prints the predicted change per transect in Appendices 1-7 (p. 290-292; m, negative = erosion). PRED below is
those columns (3) and (5) transcribed as printed; no number is digitised from the maps.
Site location: each site-side is the 2009 bankline of the paper's Figs. 3-6 traced as a few vertices in the maps' own
UTM grid (frame ticks; paper datum Indian 1960 / UTM 48N, EPSG:3148; read by eye, +-50 m) and moved to WGS84 / UTM 48N.
The maps are off by 70-460 m against our 2009 composite (checked on data/raw/*/mndwi_2009.tif), so the
match is along the bank, not by position: start at our transect-side (named channel and side) whose 2008-10 mean bank is
nearest to the trace's anchor (the cape apex or islet head, a shape both maps show; the upstream end at Sa Đéc), walk
towards the transect nearest to the other end, and keep transects until the distance along our (running-median) 2008-10
bank reaches the trace length; the same walk along the transect origins (centreline / island ring) gives a second
extent, and the medians of both are reported as the matching range. Names on the maps are checked against
data/processed/units.csv; the median distance of the matched banks to the trace is reported as the location offset.
Measured: retreat (+ = landward) 2009 -> 2015 and 2009 -> 2020 as differences of 3-yr means (2008-10, 2014-16, 2019-21,
>= 2 valid years each; spikes and non-detections out as in sat_labels.positions). Medians use all values; the maximum is
given with and without changes faster than sat_labels.MAX_RATE (30 m/yr, the edge-switch rule of the labels). Theil-Sen
rate = lrr in trends.csv (2000-2024). Descriptive only, no tests.
Writes results/p3/isprs2010.md, figures/fig12_isprs2010.png + .svg.
"""
import pathlib
import sys

import numpy as np
import pandas as pd
from rasterio.crs import CRS
from rasterio.warp import transform
from shapely.geometry import LineString, Point

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from figures import BLUE, COL1, INK, INK2, ORANGE, chart_axes, plt, save  # noqa: E402
from sat_labels import KEY, MAX_RATE, MIN_YRS, positions  # noqa: E402

BASE, P15, P20, PRE = (2008, 2010), (2014, 2016), (2019, 2021), (2000, 2002)

# Appendix columns (3) 2015 and (5) 2020 as printed, transect 1..n of each appendix (m, negative = erosion)
PRED = {
    'SD': ('App. 1, p. 290-291', [-28, -65, -79, -101, -101, -100, -127, -142, -165, -162, -156, -172, -191, -220, -256,
                                  -259, -261, -295, -261, -245, -223, -205, -183, -160, -147, -141, -123, -122, -125,
                                  -109, -84, -61, -37, -30, -24, -18, -9, -8],
           [-67, -133, -160, -201, -204, -203, -258, -283, -331, -326, -314, -349, -380, -431, -486, -481, -479, -527,
            -476, -444, -406, -367, -327, -284, -260, -247, -207, -205, -206, -181, -136, -94, -57, -44, -35, -27, -10,
            -10]),
    'TP-L': ('App. 2, p. 291', [7, -10, -36, -22, -15, -9, -16, -24, -26, -34, -32, -33, -34, -38, -41, -47, -50, -56, -58,
                                -61, -110, -113, -115, -119, -128, -131, -135, -139, -143, -150, -155, -164, -170, -184,
                                -181, -171, -128, -79, -40],
             [11, -24, -62, -42, -34, -22, -35, -51, -57, -71, -66, -69, -71, -80, -85, -97, -103, -115, -118, -122, -226,
              -230, -235, -241, -255, -259, -265, -272, -276, -284, -293, -304, -310, -330, -320, -294, -211, -122, -56]),
    'TP-R': ('App. 3, p. 291', [53, 57, 73, 78, 89, 95, 101, 100, 102, 105, 108, 101, 102, 99, 89, 82, 74, 61, 57, 49, 40,
                                32, 17, 4, 3, -8, -12, -13, -16],
             [98, 103, 126, 129, 147, 156, 165, 161, 163, 166, 171, 146, 146, 139, 122, 110, 96, 77, 75, 64, 51, 40, 20, 2,
              8, -15, -21, -23, -27]),
    'LK-4': ('App. 4, p. 291-292', [-66, -75, -69, -63, -61, -60, -50, -80, -91, -81, -92, -81, -87, -93, -92, -70, -51,
                                    -36, -18, -13, -13, -17, -19, -23, -22],
             [-118, -136, -126, -117, -114, -120, -91, -150, -170, -147, -169, -145, -156, -168, -167, -128, -92, -64, -33,
              -24, -24, -30, -32, -40, -39]),
    'LK-5': ('App. 5, p. 292', [0, -15, -16, -22, -24, -29, -35, -45, -54, -65, -74, -72, -75, -83, -98],
             [3, -22, -26, -36, -40, -47, -56, -71, -86, -105, -121, -116, -122, -132, -153]),
    'CM-6': ('App. 6, p. 292', [-13, -16, -20, -21, -30, -37, -44, -50, -58, -64, -66, -73, -77, -78, -81, -77, -72, -67,
                                -68, -69, -68, -61, -53],
             [-22, -22, -29, -30, -44, -57, -71, -87, -106, -120, -126, -137, -146, -147, -152, -147, -140, -133, -135,
              -138, -135, -123, -108]),
    'CM-7': ('App. 7, p. 292', [-78, -102, -102, -92, -82, -80, -74, -74, -71, -75, -73, -70, -67, -66, -66, -67, -67, -68,
                                -64, -65, -67, -68],
             [-163, -200, -195, -175, -160, -154, -146, -148, -144, -150, -143, -136, -130, -127, -127, -128, -129, -131,
              -126, -131, -137, -142]),
}
# headline numbers printed in the text (p. 287, 289, 290); retreat +, accretion -
TEXT = {'SD': '137 / 254 m mean (= App. 1 average); >200 / >400 m at T14-22',
        'TP-L': 'max 184 / 330 m at T34 (= App. 2)',
        'TP-R': 'accretion to 108 / 171 m at T50 (= App. 3)',
        'LK-4': '"upper side" 169 / 254 m (App. 4 prints max 93 / 170 m)',
        'LK-5': '"lower side" 91 / 170 m (App. 5 prints max 98 / 153 m)',
        'CM-6': 'both sides 100 / 200 m (App. 6 prints max 81 / 152 m)',
        'CM-7': 'both sides 100 / 200 m (= App. 7 max, T2)'}

# site-side: (label, map, our channel and side, traced 2009 bank in the map grid (EPSG:3148), first to last transect)
SITES = {
    'SD': ('Sa Đéc: An Hiệp / Tân Quy Đông-Tây (site 1)', 'Fig. 3', 'tien', 'R',
           [(585690, 1136980), (586860, 1136540), (587850, 1136450), (588440, 1136540), (589020, 1137240),
            (589840, 1137590)]),
    'TP-L': ('Thường Phước cape, "left side" T1-39 (site 2)', 'Fig. 4', 'tien', 'L',
             [(524410, 1198170), (524950, 1197010), (525450, 1196100), (525950, 1195440), (526450, 1194690),
              (526780, 1194440)]),
    'TP-R': ('Thường Phước cape, "right side" T40-68 (site 2)', 'Fig. 4', 'tien', 'L',
             [(526780, 1194440), (528110, 1194320), (528940, 1194440), (529610, 1194690), (530280, 1195020)]),
    'LK-4': ('Long Khánh A islet head, App. 4 face T1-25 (site 3)', 'Fig. 5', 'isl_tien_02', 'I',
             [(530350, 1193300), (530820, 1192880), (531620, 1192200), (532650, 1191870)]),
    'LK-5': ('Long Khánh A islet head, App. 5 face T1-15 (site 3)', 'Fig. 5', 'isl_tien_02', 'I',
             [(531400, 1194330), (530980, 1194000), (530300, 1193440)]),
    'CM-6': ('"Châu Ma" islet head, App. 6 (west) face T1-23 (site 4)', 'Fig. 6', 'isl_tien_04', 'I',
             [(538750, 1182590), (538910, 1183140), (539160, 1183700), (539350, 1184180), (539600, 1184870)]),
    'CM-7': ('"Châu Ma" islet head, App. 7 (east) face T1-22 (site 4)', 'Fig. 6', 'isl_tien_04', 'I',
             [(539600, 1184870), (539780, 1184510), (540020, 1184080), (540310, 1183610), (540650, 1183040),
              (540840, 1182710)]),
}
# trace vertex the match starts from: 0 = first, -1 = last (cape apex / islet head; upstream end at Sa Đéc)
ANCHOR = {'SD': 0, 'TP-L': -1, 'TP-R': 0, 'LK-4': 0, 'LK-5': -1, 'CM-6': -1, 'CM-7': 0}
ACCRETION = {'TP-R'}        # the paper predicts accretion: its extreme is the largest accretion (most negative retreat)
NAMES = {'SD': 'Sa Đéc', 'TP-L': 'T. Phước, upstr.', 'TP-R': 'T. Phước, downstr.', 'LK-4': 'L. Khánh A, SW',
         'LK-5': 'L. Khánh A, NW', 'CM-6': 'Châu Ma, W', 'CM-7': 'Châu Ma, E'}     # figure row labels
GRID2 = '#c8c7c2'


def to_wgs(xy, src=3148):
    x, y = transform(CRS.from_epsg(src), CRS.from_epsg(32648), *zip(*xy))
    return LineString(list(zip(x, y)))


def bank_table():
    """All transect-sides with commune, lrr, 2008-10 bank xy (WGS84 UTM 48N) and the two retreats."""
    u = pd.read_csv('data/processed/units.csv')
    tr = pd.concat([pd.read_csv(f'data/processed/{r}/trends.csv').assign(channel=r) for r in ('tien', 'hau')]
                   + [pd.read_csv('data/processed/islands/trends.csv').drop(columns='transect')
                      .rename(columns={'ring_transect': 'transect'})])
    u = u.merge(tr[KEY + ['cx', 'cy', 'nx', 'ny', 'lrr', 'kind']], on=KEY, how='left', validate='one_to_one')
    w = positions(u)
    mean3 = lambda p: w.loc[:, p[0]:p[1]].mean(1).where(w.loc[:, p[0]:p[1]].notna().sum(1) >= MIN_YRS)  # noqa: E731
    base = mean3(BASE).to_numpy()
    u['bx'], u['by'] = u.cx + u.nx * base, u.cy + u.ny * base
    for name, per in (('r15', P15), ('r20', P20)):
        u[name] = (mean3(per) - mean3(BASE)).to_numpy()
        u[name + '_jump'] = u[name].abs() > MAX_RATE * (sum(per) - sum(BASE)) / 2
    u['r_pre'] = (mean3(BASE) - mean3(PRE)).to_numpy()          # 2001 -> 2009, before the forecast
    return u.dropna(subset=['bx'])


def match(u, key, walk='bank'):
    """Our transect-sides from the anchor along the bank for the trace length; distances to the trace (both datums).
    walk='bank': length measured on our 2008-10 bank (5-transect running median, so a wild bank does not count);
    walk='origin': on the transect origins (centreline / island ring), the alternative extent for the range."""
    _, _, ch, side, xy = SITES[key]
    anchor = ANCHOR[key]
    line = to_wgs(xy)
    c = u[(u.channel == ch) & (u.side == side)].sort_values('transect')
    near = [c.iloc[np.hypot(c.bx - x, c.by - y).argmin()] for x, y in (line.coords[0], line.coords[-1])]
    a, b = near if anchor == 0 else near[::-1]
    c = c[c.transect >= a.transect] if b.transect > a.transect else c[c.transect <= a.transect].iloc[::-1]
    if walk == 'bank':
        x, y = (c[k].rolling(5, center=True, min_periods=1).median() for k in ('bx', 'by'))
    else:
        x, y = c.cx, c.cy
    along = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
    m = c[along <= line.length].copy()
    for col, src in (('d', 3148), ('d_wgs', 32648)):
        ln = to_wgs(xy, src)
        m[col] = [ln.distance(Point(p)) for p in zip(m.bx, m.by)]
    return m, np.hypot(a.bx - line.coords[anchor][0], a.by - line.coords[anchor][1])


def summary(u):
    rows = []
    for k, (ref, p15, p20) in PRED.items():
        m, end_d = match(u, k)
        alt = match(u, k, 'origin')[0]
        ext = np.min if k in ACCRETION else np.max        # extreme in the predicted direction (retreat +)
        r = dict(key=k, ref=ref, n_pred=len(p15), n_ours=len(m), n_meas15=int(m.r15.notna().sum()),
                 n_meas20=int(m.r20.notna().sum()), n_jump15=int(m.r15_jump.sum()), n_jump20=int(m.r20_jump.sum()),
                 communes=', '.join(m.commune.dropna().value_counts().index),
                 chain=f'{m.transect.iloc[0]}-{m.transect.iloc[-1]}', end_d=end_d, d_med=m.d.median(),
                 d_med_wgs=m.d_wgs.median(), lrr=m.lrr.median(), lrr_ext=ext(m.lrr.dropna()), pre_rate=m.r_pre.median() / 8,
                 pred_rate=np.median(-(np.array(p20) - np.array(p15)) / 5))
        for h, p, col in ((2015, p15, 'r15'), (2020, p20, 'r20')):
            p = -np.array(p, float)                       # paper: negative = erosion -> retreat +
            r[f'p{h}_med'], r[f'p{h}_ext'] = np.median(p), ext(p)
            r[f'm{h}_med'], r[f'm{h}_ext'] = m[col].median(), ext(m[col].dropna())
            r[f'm{h}_extc'] = ext(m.loc[~m[col + '_jump'], col].dropna())
            r[f'm{h}_alt'] = alt[col].median()
        r['chain_alt'] = f'{alt.transect.iloc[0]}-{alt.transect.iloc[-1]}'
        rows.append(r)
    return pd.DataFrame(rows)


def figure(s):
    """Dumbbell per site-side and year: predicted (open diamond) to measured (dot) median retreat; grey bar = measured
    median over the alternative extent (matching range)."""
    fig, ax = plt.subplots(figsize=(COL1 * .8, COL1 * .72))
    chart_axes(ax)
    ax.grid(axis='y', visible=False)
    ax.axvline(0, color=INK2, lw=.6, zorder=1)
    for i, r in enumerate(s.itertuples()):
        for h, col, dy in ((2015, BLUE, -.17), (2020, ORANGE, .17)):
            y, p, m, a = i + dy, getattr(r, f'p{h}_med'), getattr(r, f'm{h}_med'), getattr(r, f'm{h}_alt')
            ax.plot((min(m, a), max(m, a)), (y, y), color=GRID2, lw=4, solid_capstyle='butt', zorder=1)
            ax.plot((p, m), (y, y), color=col, lw=1, zorder=2)
            ax.scatter(p, y, s=18, marker='D', facecolor='white', edgecolor=col, lw=1, zorder=3)
            ax.scatter(m, y, s=18, color=col, zorder=3)
    ax.set_yticks(range(len(s)), [NAMES[k] for k in s.key])
    ax.invert_yaxis()
    ax.tick_params(axis='y', length=0)
    ax.set_xlabel('Retreat since 2009, median (m)')
    h = [plt.Line2D([], [], color=c, marker=mk, mfc=fc, mec=c, ls='', ms=4.5, label=l) for c, mk, fc, l in (
        (BLUE, 'D', 'white', 'Predicted 2015'), (ORANGE, 'D', 'white', 'Predicted 2020'),
        (BLUE, 'o', BLUE, 'Measured 2015'), (ORANGE, 'o', ORANGE, 'Measured 2020'))]
    h.append(plt.Line2D([], [], color=GRID2, lw=4, label='Matching range'))
    ax.legend(handles=h, loc='upper center', bbox_to_anchor=(.3, -.17), ncol=3, handletextpad=.6, columnspacing=.6,
              handlelength=1.4)
    save(fig, 'fig12_isprs2010')


def report(s):
    f = lambda v: '' if pd.isna(v) else f'{v:.0f}'  # noqa: E731
    L = ['# R3. The 2010 deterministic bank forecast against measured banks (illustration, not a gate)', '',
         'Generated by `python src/p3_isprs2010.py` (docs/p3_plan.md R3). Source: Lam Dao Nguyen, Nguyen Thanh Minh, '
         'Pham Thi Mai Thy, Hoang Phi Phung, Hoang Van Huan (2010), "Analysis of changes in the riverbanks of Mekong '
         'River - Vietnam by using multi-temporal remote sensing data", ISPRS Archives XXXVIII Part 8, Kyoto, pp. 287-292 '
         '(open-access PDF downloaded 2026-10-26, kept in papers/, not committed).', '',
         '## What the paper predicts', '',
         '- Method (p. 288): banks digitised from a 1966 topographic map and Landsat/ASTER/ERS-2 images (1989-2009, '
         'resampled to 30 m), DSAS transects on a baseline that is a buffer of the 2009 bank, linear regression with the '
         'authors\' inverse-squared-time weights (Tables 1-4, p. 289: the last image carries 0.32-0.43 of the weight for '
         '2015), extrapolated to 2015 and 2020. Base year 2009: last image 24 Jun 2009 at Sa Đéc (wet season), 30 Jan '
         '2009 at sites 2-4. No interval and no hindcast; the only skill figure is a correlation coefficient per transect.',
         '- Printed numbers: the predicted change per transect for 2015 and 2020 in Appendices 1-7 (p. 290-292; m, '
         'negative = erosion) and headline numbers in the text. The change is read here as the predicted bank minus the '
         '2009 bank (the paper does not say whether the observed or the regressed 2009 position is meant).', '',
         '| Site-side | Source | Transects | Pred. 2015 median / max (m) | Pred. 2020 median / max (m) | Implied rate, median (m/yr) | Text |',
         '|---|---|---|---|---|---|---|']
    for _, r in s.iterrows():
        L.append(f'| {r.key} | {r.ref} | {r.n_pred} | {f(r.p2015_med)} / {f(r.p2015_ext)} | {f(r.p2020_med)} / '
                 f'{f(r.p2020_ext)} | {r.pred_rate:.1f} | {TEXT[r.key]} |')
    L += ['', 'Retreat + (landward), accretion -. "max" = extreme in the predicted direction (largest accretion for '
          'TP-R). Implied rate = (2020 - 2015) / 5 per transect. Three text numbers disagree with their own appendix '
          '(Long Khánh A 169 / 254 m and 91 / 170 m; Châu Ma 100 / 200 m for the App. 6 side); the appendix values are '
          'used below.', '',
          '## Site matching', '',
          'Each site-side was traced on the paper\'s map (Figs. 3-6, p. 289-290; UTM grid ticks on the frame) as 3-6 '
          'vertices of the 2009 bank, taken as Indian 1960 / UTM 48N (EPSG:3148, the datum the paper names), moved to '
          'WGS84 (shift ~10 m E, ~90 m N). Against our 2009 composite (data/raw/*/mndwi_2009.tif) the traces are off by '
          '70-460 m in directions that differ between maps, so the match is along the bank: start at our transect-side '
          '(named channel and side) whose 2008-10 bank is nearest to the trace\'s anchor (cape apex or islet head, a '
          'shape both data sets show; the upstream end at Sa Đéc) and keep our transects for the trace length along the '
          'bank (measured on our running-median 2008-10 bank; the same walk along our transect origins, i.e. centreline or '
          'island ring, gives the alternative extent used for the range). Our transects are ~100 m apart, as are theirs '
          '(stated for Sa Đéc). Map labels: Bình Thạnh / An Hiệp (Fig. 3), Thường Phước 2 / '
          'Tân Châu (Fig. 4), Long Khánh A / Long Thuận (Fig. 5), Hồng Ngự / Phú Tân (Fig. 6).', '',
          '| Site-side | Paper description | Our channel, side, transects (anchor first) | Alternative extent | Communes (units.csv) | n ours | Anchor to our bank (m) | Our bank to trace, median, EPSG:3148 / grid read as WGS84 (m) |',
          '|---|---|---|---|---|---|---|---|']
    for _, r in s.iterrows():
        lab, fig_, ch, side, _ = SITES[r.key]
        L.append(f'| {r.key} | {lab}, {fig_} | {ch} {side}, {r.chain} | {r.chain_alt} | {r.communes} | {r.n_ours} | {r.end_d:.0f} | '
                 f'{r.d_med:.0f} / {r.d_med_wgs:.0f} |')
    L += ['', '- Sa Đéc (site 1): the eroding bank south of Bình Thạnh is our Tien right (mainland) bank; matched by '
          'name (An Hiệp, Châu Thành) and by the map grid.',
          '- Thường Phước (site 2): both "sides" of the cape are one bank, our Tien left bank (Thường Phước 2, Thường Thới '
          'Tiền, Hồng Ngự). "Left side" T1-39 is the NNW-SSE reach upstream of the cape, "right side" T40-68 the W-E reach '
          'downstream of it.',
          '- Long Khánh A (site 3): head of our island isl_tien_02 (commune Long Khánh A, Hồng Ngự). Appendix 4 ("right '
          'side", 25 transects) lies on the south-west face towards Long Thuận, Appendix 5 ("left side", 15) on the '
          'north-west face. The text calls them "upper" and "lower" side without saying which is which, so they are '
          'labelled by appendix. Transects 1-5 of Appendix 5 run off the map; that end of the trace is extrapolated '
          '(~0.5 km).',
          '- "Châu Ma" (site 4): no commune or island of that name is in units.csv; the map grid puts the islet head on '
          'our island isl_tien_04 (commune Phú Thuận B, Hồng Ngự). Appendix 6 ("right side", 23) is its west face, '
          'Appendix 7 ("left side", 22) its east face. This match rests on the map grid only.',
          '- Our 2008-10 banks follow the water edge of our 2009 composite; the paper\'s traced 2009 banks lie 70-460 m '
          'from them (median per site-side in the table), e.g. the Long Khánh A head ~400 m east of ours and the Châu Ma '
          'west face ~450 m east of ours. Likely causes: the paper\'s georeferencing (to a 1966 1:50,000 map, Indian '
          '1960), a digitised soil / vegetation edge against our first water from land (sand spits at island heads in '
          'Jan-Apr), and our reading of the traces. The site ends are therefore uncertain by a few hundred metres along '
          'the bank, which matters most for the maximum. Read each match as a candidate stretch, not a '
          'transect-by-transect pairing; LK-5 and CM-6 keep only 8 and 9 measured transects (non-detections and edge '
          'switches at the islet heads).', '',
          '## Comparison', '',
          '| Site-side | Year | Predicted median | Measured median | Alternative extent | Ratio | Diff. | Predicted max | Measured max | Ratio | Diff. | Measured max, all values | n measured |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for _, r in s.iterrows():
        for h in (2015, 2020):
            pm, mm, pe, me = r[f'p{h}_med'], r[f'm{h}_med'], r[f'p{h}_ext'], r[f'm{h}_extc']
            L.append(f'| {r.key} | {h} | {f(pm)} | {f(mm)} | {f(r[f"m{h}_alt"])} | {mm / pm:.2f} | {f(mm - pm)} | {f(pe)} | {f(me)} | '
                     f'{me / pe:.2f} | {f(me - pe)} | {f(r[f"m{h}_ext"])} | {r[f"n_meas{str(h)[2:]}"]} |')
    L += ['', 'Measured = 3-yr mean 2014-16 (or 2019-21) minus 3-yr mean 2008-10 per transect-side, m, + = retreat; '
          'ratio = measured / predicted, diff. = measured - predicted (m). Medians use all values; "Measured max" leaves '
          'out changes faster than 30 m/yr (the edge-switch rule of the satellite labels), the next column keeps them '
          '(values of 1-2 km there are bar or ring switches at islet heads, not retreat).', '',
          '| Site-side | Paper implied rate 2015-20, median (m/yr) | Our rate 2001 -> 2009 (3-yr means), median (m/yr) | Our rate 2009 -> 2020, median (m/yr) | Our Theil-Sen 2000-2024, median / max (m/yr) | Values > 30 m/yr, 2015 / 2020 |',
          '|---|---|---|---|---|---|']
    for _, r in s.iterrows():
        L.append(f'| {r.key} | {r.pred_rate:.1f} | {r.pre_rate:.1f} | {r.m2020_med / 11:.1f} | {r.lrr:.1f} / '
                 f'{r.lrr_ext:.1f} | {r.n_jump15} / {r.n_jump20} |')
    L += ['', 'Figure: figures/fig12_isprs2010.png (+ .svg). Median bank retreat since 2009 per site-side, predicted in '
          '2010 (open diamonds) and measured (dots), 2015 blue, 2020 orange; grey bar = measured median over the '
          'alternative matched extent. Negative = accretion.']
    L += ['', '## Reading', ''] + reading(s) + ['']
    pathlib.Path('results/p3').mkdir(parents=True, exist_ok=True)
    pathlib.Path('results/p3/isprs2010.md').write_text('\n'.join(L), encoding='utf-8')
    print('wrote results/p3/isprs2010.md')


def reading(s):
    r = s.set_index('key')
    ratio = lambda k: r.at[k, 'm2020_med'] / r.at[k, 'p2020_med']  # noqa: E731
    under = ['LK-4', 'LK-5', 'CM-7']
    flip = [k for k in r.index if np.sign(r.at[k, 'm2020_med'] - r.at[k, 'p2020_med'])
            != np.sign(r.at[k, 'm2020_alt'] - r.at[k, 'p2020_med'])]
    return [
        f'- Mainland banks, over-predicted. Sa Đéc: {r.at["SD", "m2020_med"]:.0f} m measured against '
        f'{r.at["SD", "p2020_med"]:.0f} m predicted by 2020 (median, ratio {ratio("SD"):.2f}; max '
        f'{r.at["SD", "m2020_extc"]:.0f} vs {r.at["SD", "p2020_ext"]:.0f} m). Our 2001 -> 2009 rate there '
        f'({r.at["SD", "pre_rate"]:.0f} m/yr) is close to the paper\'s implied {r.at["SD", "pred_rate"]:.0f} m/yr, so the '
        f'history behind the forecast was right; retreat went on to ~2015 ({r.at["SD", "m2015_med"]:.0f} m) and then '
        f'nearly stopped ({r.at["SD", "m2020_med"] - r.at["SD", "m2015_med"]:.0f} m more by 2020; cause not examined '
        f'here). Thường Phước left side: {r.at["TP-L", "p2020_med"]:.0f} m predicted, '
        f'{r.at["TP-L", "m2020_med"]:.0f} m measured (our 2001 -> 2009 rate was already only '
        f'{r.at["TP-L", "pre_rate"]:.0f} m/yr). Thường Phước right side: {-r.at["TP-R", "p2020_med"]:.0f} m of '
        f'accretion predicted, {-r.at["TP-R", "m2020_med"]:.0f} m measured; the 2001 -> 2009 accretion '
        f'({-r.at["TP-R", "pre_rate"]:.0f} m/yr in our data; the paper notes strong accretion in 2003-2009) did not '
        f'continue.',
        f'- Islet heads, mostly under-predicted. Long Khánh A (both faces) and the Châu Ma east face kept eroding at '
        f'{r.loc[under, "lrr"].min():.0f}-{r.loc[under, "lrr"].max():.0f} m/yr (Theil-Sen, median): measured 2020 '
        f'medians {r.loc[under, "m2020_med"].min():.0f}-{r.loc[under, "m2020_med"].max():.0f} m against '
        f'{r.loc[under, "p2020_med"].min():.0f}-{r.loc[under, "p2020_med"].max():.0f} m predicted (ratios '
        f'{min(ratio(k) for k in under):.2f}-{max(ratio(k) for k in under):.2f}); the weighted fit had implied '
        f'{r.loc[under, "pred_rate"].min():.0f}-{r.loc[under, "pred_rate"].max():.0f} m/yr. The Châu Ma west face '
        f'(CM-6) is undecided: {r.at["CM-6", "m2020_med"]:.0f} or {r.at["CM-6", "m2020_alt"]:.0f} m measured '
        f'against {r.at["CM-6", "p2020_med"]:.0f} m predicted, depending on the matched extent.',
        f'- Matching range: with the alternative extent the 2020 medians are '
        + ', '.join(f'{k} {r.at[k, "m2020_alt"]:.0f}' for k in r.index if abs(r.at[k, 'm2020_alt'] - r.at[k, 'm2020_med']) >= 10)
        + ' m (other site-sides within 10 m of the primary). The sign of the miss changes only for '
        + (', '.join(flip) or 'none') + '.',
        f'- Plain reading: the weighted linear extrapolation missed in both directions, by '
        f'{(r.m2020_med - r.p2020_med).abs().min():.0f}-{(r.m2020_med - r.p2020_med).abs().max():.0f} m at the '
        'median at an 11-yr horizon. It over-predicted where erosion slowed or stopped after 2009 (mainland bends) and '
        'under-predicted where it went on (most islet-head faces), and it gave no interval that could have warned of either. '
        'This argues for forecasts with verified coverage rather than for a better point rate.',
        '- Limits: one paper, seven site-sides, descriptive only. The matches are candidate stretches (map '
        'georeferencing off by up to ~460 m); the maxima depend on the site ends and on edge switches at islet heads. '
        'The paper\'s base is its own digitised 2009 bank (wet-season image at Sa Đéc), ours a dry-season 3-yr mean '
        '2008-10; a base offset of a few tens of metres does not change the reading.',
    ]


def main():
    u = bank_table()
    s = summary(u)
    pd.set_option('display.width', 250)
    print(s.drop(columns=['ref', 'communes']).round(1).to_string())
    report(s)
    figure(s)


if __name__ == '__main__':
    main()
