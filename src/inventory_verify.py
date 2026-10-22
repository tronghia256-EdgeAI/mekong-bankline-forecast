"""Check that every candidate's verbatim quote really appears on its source page.

Usage: python src/inventory_verify.py data/hotspots/candidates_X.csv [...]
For each row with a `quote`, downloads `source_url`, strips the HTML to text and looks for the quote after
Unicode NFC normalisation, case folding and whitespace collapsing. Writes the columns `quote_found`
(yes / no / fetch_error / no_quote) and `checked_on` back into the same file and prints a summary.
Rows marked `no` are fabricated or misquoted and must not enter the inventory.
"""
import datetime
import html
import re
import sys
import time
import unicodedata

import pandas as pd
import requests

HEADERS = {'User-Agent': 'Mozilla/5.0 (research; riverbank erosion inventory)'}


def norm(t):
    t = unicodedata.normalize('NFC', html.unescape(t)).casefold()
    t = re.sub(r'[“”„"‘’\']', '', t)        # quotes differ between page and copy
    return re.sub(r'\s+', ' ', t).strip()


def page_text(url, cache):
    if url not in cache:
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        r.encoding = r.apparent_encoding if r.encoding in (None, 'ISO-8859-1') else r.encoding
        t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
        cache[url] = norm(re.sub(r'<[^>]+>', ' ', t))
        time.sleep(1)
    return cache[url]


def main():
    today = datetime.date.today().isoformat()
    cache = {}
    for f in sys.argv[1:]:
        df = pd.read_csv(f, encoding='utf-8-sig', dtype=str)
        found = []
        for _, r in df.iterrows():
            q = r.get('quote')
            if not isinstance(q, str) or not q.strip():
                found.append('no_quote')
                continue
            try:
                found.append('yes' if norm(q) in page_text(r.source_url.strip(), cache) else 'no')
            except requests.RequestException:
                found.append('fetch_error')
        df['quote_found'], df['checked_on'] = found, today
        df.to_csv(f, index=False, encoding='utf-8-sig')
        print(f, pd.Series(found).value_counts().to_dict())


if __name__ == '__main__':
    main()
