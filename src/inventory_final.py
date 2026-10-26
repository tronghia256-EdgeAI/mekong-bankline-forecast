"""P1: final reported-erosion inventory = inventory_draft.csv + the owner's review (inventory_review.csv).

Usage: python src/inventory_final.py
Writes data/hotspots/inventory.csv: every draft row with review_verdict, review_note, merged_into (duplicate target)
and use_in_analysis (kept, on a measured bank, event year 2015-2024). Duplicates and rejects stay in the file so the
review is auditable but are not counted. Prints the counts for the paper (docs/paper_notes.md).
"""
import pandas as pd

YEARS = (2015, 2024)
d = pd.read_csv('data/hotspots/inventory_draft.csv', encoding='utf-8-sig', dtype=str)
r = pd.read_csv('data/hotspots/inventory_review.csv', encoding='utf-8-sig', dtype=str).drop_duplicates('site_id', keep='last')
d = d.merge(r[['site_id', 'verdict', 'note']].rename(columns={'verdict': 'review_verdict', 'note': 'review_note'}),
            on='site_id', how='left')
d['merged_into'] = d.review_note.where(d.review_verdict == 'duplicate')
yr = pd.to_numeric(d.event_year, errors='coerce')
d['use_in_analysis'] = ((d.review_verdict == 'keep') & (d.status == 'measured') & yr.between(*YEARS)).fillna(False)
d.to_csv('data/hotspots/inventory.csv', index=False, encoding='utf-8-sig')
rev = d[d.review_verdict.notna()]
print('reviewed', len(rev), rev.review_verdict.value_counts().to_dict())
print('rows', len(d), d.status.value_counts().to_dict())
print('use_in_analysis', int(d.use_in_analysis.sum()), 'of kept', int((d.review_verdict == 'keep').sum()))
print(d[d.use_in_analysis].groupby('source_type').size().to_dict())
print('pre-2015 or later kept, measured, outside window:',
      d[(d.review_verdict == 'keep') & (d.status == 'measured') & ~yr.between(*YEARS)].site_id.tolist())
