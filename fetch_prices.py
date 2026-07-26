#!/usr/bin/env python3
"""
Sunoha price fetcher — runs in GitHub Actions (free) and writes prices.json.

Sources: Stooq CSV (primary), Yahoo Finance chart API (fallback).
Robusta (RC) and Cashew (CW) have no free exchange feed — they are left
untouched so the app keeps its last AI-synced or manual value.
Fed Funds (FED) changes only at FOMC meetings — edit MANUAL below when it does.
"""
import json, urllib.request, datetime, sys

UA = {"User-Agent": "Mozilla/5.0 (SunohaPriceBot; +https://github.com)"}

# sym -> (stooq symbol, yahoo symbol, sane range (lo, hi), divisors to try)
FEEDS = {
    # agri desk
    "KC":     ("kc.f",    "KC=F",     (0.5, 8),      (1, 100)),   # arabica USD/lb (quotes often in cents)
    "CC":     ("cc.f",    "CC=F",     (1000, 20000), (1,)),       # cocoa USD/MT
    "ZW":     ("zw.f",    "ZW=F",     (3, 15),       (1, 100)),   # wheat USD/bu
    "ZC":     ("zc.f",    "ZC=F",     (2, 9),        (1, 100)),   # corn USD/bu
    "ZS":     ("zs.f",    "ZS=F",     (6, 25),       (1, 100)),   # soybeans USD/bu
    # macro strip
    "CL":     ("cl.f",    "CL=F",     (20, 200),     (1,)),       # WTI USD/bbl
    "GC":     ("gc.f",    "GC=F",     (1000, 10000), (1,)),       # gold USD/ozt
    "SI":     ("si.f",    "SI=F",     (10, 150),     (1,)),       # silver USD/ozt
    "HG":     ("hg.f",    "HG=F",     (2, 9),        (1, 100)),   # copper USD/lb
    "US10Y":  ("10usy.b", "^TNX",     (1, 9),        (1, 10)),    # ^TNX is x10
    "DXY":    ("dx.f",    "DX-Y.NYB", (80, 130),     (1,)),
    "USDINR": ("usdinr",  "INR=X",    (60, 130),     (1,)),
}
MANUAL = {"FED": 3.63}  # Fed funds target midpoint — update after FOMC moves

AGRI = {"KC", "CC", "ZW", "ZC", "ZS"}

def normalize(sym, raw):
    lo, hi = FEEDS[sym][2]
    for d in FEEDS[sym][3]:
        v = raw / d
        if lo <= v <= hi:
            return round(v, 4)
    return None

def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def from_stooq(sym):
    s = FEEDS[sym][0]
    txt = get(f"https://stooq.com/q/l/?s={s}&f=sd2t2ohlcv&h&e=csv")
    line = txt.strip().splitlines()[-1].split(",")
    close = float(line[6])  # Symbol,Date,Time,Open,High,Low,Close,Volume
    return normalize(sym, close)

def from_yahoo(sym):
    y = FEEDS[sym][1]
    txt = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{y}?range=5d&interval=1d")
    js = json.loads(txt)
    res = js["chart"]["result"][0]
    closes = [c for c in res["indicators"]["quote"][0]["close"] if c]
    return normalize(sym, float(closes[-1]))

def main():
    prices, macros, errs, sources = {}, {}, [], {}
    for sym in FEEDS:
        val = None
        for fn, label in ((from_stooq, "Stooq"), (from_yahoo, "Yahoo Finance")):
            try:
                val = fn(sym)
                if val:
                    sources[sym] = label
                    break
            except Exception as e:
                errs.append(f"{sym}:{fn.__name__}:{e.__class__.__name__}")
        if val is None:
            errs.append(f"{sym}:no-valid-value")
            continue
        (prices if sym in AGRI else macros)[sym] = val
    macros.update(MANUAL)
    sources["FED"] = "Manual (FOMC target midpoint)"

    if not prices and not macros:
        print("No data fetched at all — keeping previous prices.json")
        sys.exit(0)  # don't fail the workflow; yesterday's file stays

    out = {
        "updated": datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%d %H:%M UTC"),
        "prices": prices,
        "macros": macros,
        "sources": sources,
        "note": "Free feed (Stooq/Yahoo). RC robusta & CW cashew have no free "
                "exchange feed - use AI sync or broker quotes for those.",
        "errors": errs,
    }
    with open("prices.json", "w") as f:
        json.dump(out, f, indent=1)
    print("Wrote prices.json:", json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
