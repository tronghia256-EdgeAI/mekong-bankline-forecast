"""Graphical abstract for the Geomorphology submission -> figures/graphical_abstract.{png,pdf,tif}.

Usage: python src/graphical_abstract.py
Elsevier asks for a landscape image readable at 5 x 13 cm (at least 531 x 1328 px); this one is drawn at that size,
300 dpi. Map: in-scope bank points (data/processed/units.csv) coloured by their 2000-2024 Theil-Sen rate (trends.csv).
Numbers (results files):
- pooled split-conformal coverage, h = 3: 92.4 % (results/p2/forecast.md)
- banks retreating > 10 m/yr in the previous decade: 60.2 % (results/p4/review_checks.md)
- Mondrian by past rate (post hoc PH1a) at those banks: 86.1 % (results/p4/posthoc.md)
- units marked by reports 76 %, by measured retreat 13 %, kappa -0.01 (results/p2/h3.md)
"""
import pathlib

import matplotlib.pyplot as plt
import pandas as pd

from figures import BLUE, ORANGE, AQUA, INK, INK2, GRID, RATE

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'figures'
CM = 1 / 2.54
COVERAGE = [('All banks', 92.4, BLUE), ('Fast-retreating\n(> 10 m yr$^{-1}$)', 60.2, ORANGE),
            ('Same, calibrated by\npast rate (post hoc)', 86.1, AQUA)]
LABELS = [('Public\nreports', 76, INK2), ('Measured\nretreat ≥ 20 m', 13, BLUE)]


def bank_points():
    u = pd.read_csv(ROOT / 'data/processed/units.csv')
    u = u[u.in_scope]
    parts = []
    for src in ('tien', 'hau', 'islands'):
        t = pd.read_csv(ROOT / f'data/processed/{src}/trends.csv')[['transect', 'side', 'lrr']]
        sel = u[u.channel.str.startswith('isl')] if src == 'islands' else u[(u.channel == src)]
        parts.append(sel.merge(t, on=['transect', 'side']))
    return pd.concat(parts)


def bars(ax, rows, ref=None):
    """Horizontal bars on a 0-100 % scale; labels left of the axes, values in a column right of 100 %."""
    for i, (label, value, colour) in enumerate(rows):
        ax.barh(i, value, height=.62, color=colour)
        ax.text(104, i, f'{value:.0f}%', va='center', ha='left', fontsize=8, fontweight='bold', color=INK)
        ax.text(-4, i, label, va='center', ha='right', fontsize=7, color=INK)
    if ref:
        ax.axvline(ref, color=INK2, lw=.8, ls=(0, (3, 2)))
        ax.text(ref, -.62, f'nominal {ref}%', ha='center', va='bottom', fontsize=6.5, color=INK2)
    ax.set(xlim=(0, 100), ylim=(len(rows) - .45, -.7))
    ax.axis('off')


def main():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42, 'savefig.dpi': 300})
    fig = plt.figure(figsize=(13 * CM, 5 * CM))
    am = fig.add_axes([0, .1, .27, .74])
    ab = fig.add_axes([.465, .1, .155, .66])
    ac = fig.add_axes([.8, .3, .11, .4])

    p = bank_points()
    p = p.sort_values('lrr', key=abs)
    sc = am.scatter(p.lon, p.lat, c=p.lrr, cmap=RATE, vmin=-10, vmax=10, s=.6, lw=0, rasterized=True)
    am.set_aspect(1 / 0.985)
    am.axis('off')
    cax = fig.add_axes([.14, .07, .11, .03])
    cb = fig.colorbar(sc, cax=cax, orientation='horizontal', ticks=[-10, 0, 10])
    cb.ax.tick_params(labelsize=6, length=2, color=INK2, pad=1)
    cb.outline.set_linewidth(.4)
    cax.set_title('retreat, m yr$^{-1}$', fontsize=6, pad=2, color=INK2)
    am.text(.98, .97, 'Tien and Hau rivers\nLandsat, 2000–2024', transform=am.transAxes, ha='right', va='top',
            fontsize=6.5, color=INK2)

    bars(ab, COVERAGE, ref=90)
    bars(ac, LABELS)
    ac.text(.6, -.55, 'agreement κ = −0.01', transform=ac.transAxes, ha='center', fontsize=7, color=INK)

    heads = [(.005, 'Annual banklines\nevery 100 m'), (.30, 'Forecast intervals:\ncoverage'),
             (.71, 'Erosion labels:\nshare of 2 km units')]
    for x, h in heads:
        fig.text(x, .985, h, ha='left', va='top', fontsize=8, fontweight='bold', color=INK)
    for x in (.285, .695):
        fig.add_artist(plt.Line2D([x, x], [.05, .95], color=GRID, lw=.6))
    for ext in ('png', 'pdf', 'tif'):
        fig.savefig(OUT / f'graphical_abstract.{ext}')
    plt.close(fig)
    print('wrote', OUT / 'graphical_abstract.png')


if __name__ == '__main__':
    main()
