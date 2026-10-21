#!/usr/bin/env python3
"""
Date and leak checks for the v8 growth features (no training, no 2022+ labels).

1. Made-up cases for each date rule (previews, catch-up filings, same-day rows, staleness).
2. Dataset: old columns identical to the v7 backup; the six growth columns added (plus batch 2's
   four margin columns after them, checked in check_margin_features.py).
3. Real data: announcement window, quarter owner, strictly-after, staleness, never-backwards.
4. Independent slow re-implementation (plain Python, no merge_asof) on sampled rows.
5. Volume around announcement vs filing dates (real news moves volume).
6. Hand checks (NVDA, AAPL, MSFT) printed for eyeballing.
7. Coverage by year, correlations, leak-power test (fake early dates must look better),
   placebo sanity.

Usage: PYTHONPATH=. python scripts/check_growth_features.py
Exits 1 if any check fails.
"""

from __future__ import annotations

import sys
import warnings
from datetime import timedelta

import numpy as np
import pandas as pd

from pinky import fundamentals as F
from pinky.dataset import feature_columns
from pinky.pit_dataset import DATASET_PATH, DERIVED_DIR
from pinky.train import dev_rows
from pinky.universe import benchmark_closeadj, load_panel

V7_PATH = DERIVED_DIR / "pit_dataset_v7.parquet"
RESULTS: list[tuple[bool, str]] = []
D = pd.Timestamp


def check(ok, name: str) -> None:
    RESULTS.append((bool(ok), name))
    print(f"{'PASS' if ok else 'FAIL'} - {name}")


def same(a, b, rtol: float = 1e-5, atol: float = 1e-6) -> np.ndarray:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return (np.isnan(a) & np.isnan(b)) | np.isclose(a, b, rtol=rtol, atol=atol)


def section(title: str) -> None:
    print(f"\n## {title}\n")


# 1 --------------------------------------------------------------------------------------
def synthetic_cases() -> None:
    section("1. Made-up cases")
    raw = pd.DataFrame(
        [
            ("A", D("2015-06-30"), D("2015-06-30"), D("2015-08-10"), 100.0, 40.0),
            ("A", D("2015-09-30"), D("2015-09-30"), D("2015-11-09"), 110.0, 44.0),
            ("A", D("2015-12-31"), D("2015-12-31"), D("2016-02-25"), 120.0, 48.0),
            ("A", D("2016-03-31"), D("2016-03-31"), D("2016-05-10"), 125.0, 50.0),
            ("A", D("2016-06-30"), D("2016-06-30"), D("2016-08-09"), 150.0, 66.0),
            ("A", D("2016-09-30"), D("2016-09-30"), D("2016-11-08"), 176.0, 80.0),
            ("A", D("2016-12-31"), D("2016-12-31"), D("2017-02-24"), 180.0, 81.0),
            ("A", D("2016-12-31"), D("2016-12-31"), D("2017-03-30"), 999.0, 999.0),
            ("A", D("2017-03-31"), D("2017-03-31"), D("2017-05-10"), 160.0, 70.0),
            ("A", D("2017-06-30"), D("2017-06-30"), D("2017-06-20"), 1.0, 1.0),
            ("A", D("2017-09-30"), D("2017-09-30"), D("2017-10-05"), 1.0, 1.0),
            ("B", D("2015-06-30"), D("2015-06-30"), D("2015-08-10"), 40.0, 15.0),
            ("B", D("2016-03-31"), D("2016-03-31"), D("2016-09-15"), 50.0, 20.0),
            ("B", D("2016-06-30"), D("2016-06-30"), D("2016-09-15"), 60.0, 25.0),
        ],
        columns=["ticker", "calendardate", "reportperiod", "date", "revenue", "gp"],
    )
    anns = pd.DataFrame(
        [
            ("A", D("2016-08-04")),
            ("A", D("2016-11-10")),
            ("A", D("2017-01-05")),
            ("A", D("2017-01-20")),
            ("A", D("2017-02-01")),
            ("B", D("2016-08-20")),
        ],
        columns=["ticker", "ann"],
    ).astype({"ann": "datetime64[us]"})
    q = F.quarterly_growth_reports(raw, anns)
    t = F.ttm_growth_reports(raw.drop(columns="gp"), anns)
    qi = q.set_index(["ticker", "calendardate"])

    def news(tk: str, cd: str) -> pd.Timestamp:
        return qi.loc[(tk, D(cd)), "news_date"]

    check(news("A", "2016-06-30") == D("2016-08-04"), "announcement 35 days after quarter end is used")
    check(news("A", "2016-09-30") == D("2016-11-08"), "announcement after the filing is ignored (filing date used)")
    check(news("A", "2016-12-31") == D("2017-02-01"), "5-day preview skipped; latest of two releases used")
    check(qi.loc[("A", D("2016-12-31")), "revenue"] == 180.0, "later amendment ignored (first filing kept)")
    check(("A", D("2017-06-30")) not in qi.index, "row filed before its period ended is dropped")
    check(("A", D("2017-09-30")) not in qi.index, "row filed only 5 days after period end is dropped")
    check(news("B", "2016-06-30") == D("2016-08-20"), "catch-up: announcement goes to the newest quarter")
    check(news("B", "2016-03-31") == D("2016-09-15"), "catch-up: older quarter keeps its filing date")
    check(np.isclose(qi.loc[("A", D("2016-06-30")), "rev_yoy_q"], 0.5), "YoY revenue 150 / 100 − 1")
    check(np.isclose(qi.loc[("A", D("2016-09-30")), "gp_yoy_q"], 80 / 44 - 1), "YoY gross profit 80 / 44 − 1")
    check(
        np.isclose(qi.loc[("A", D("2016-12-31")), "rev_accel"], (180 / 120 - 1) - (176 / 110 - 1)),
        "acceleration across Sep 30 → Dec 31 quarter ends",
    )
    check(np.isnan(qi.loc[("A", D("2015-06-30")), "rev_yoy_q"]), "no YoY without a prior-year quarter")

    rows = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                ["2016-08-04", "2016-08-05", "2016-09-15", "2016-09-16", "2017-02-01", "2017-02-02",
                 "2018-03-30", "2018-04-02"]
            ).astype("datetime64[us]"),
            "Ticker": ["A", "A", "B", "B", "A", "A", "A", "A"],
        }
    )
    g = F.growth_feature_frame(rows, q, t).set_index(["Date", "Ticker"])

    def val(d: str, tk: str, c: str) -> float:
        return g.loc[(D(d), tk), c]

    check(val("2016-08-04", "A", "days_since_news") == 86, "row on the news day still sees the older report (86 days old)")
    check(np.isclose(val("2016-08-05", "A", "rev_yoy_q"), 0.5), "row the day after sees the new report")
    check(val("2016-08-05", "A", "days_since_news") == 1, "days_since_news = 1 the day after")
    check(np.isclose(val("2016-09-15", "B", "rev_yoy_q"), 0.5), "catch-up day shows the newer quarter (public since Aug 20)")
    check(np.isclose(val("2016-09-16", "B", "rev_yoy_q"), 0.5), "older quarter published later never replaces the newer one")
    check(np.isclose(val("2017-02-01", "A", "rev_yoy_q"), 176 / 110 - 1), "Q4 hidden on its own news day")
    check(np.isclose(val("2017-02-02", "A", "rev_yoy_q"), 180 / 120 - 1), "Q4 visible the next day")
    check(np.isclose(val("2018-03-30", "A", "rev_yoy_q"), 0.28), "quarterly value kept at 364 days")
    check(np.isnan(val("2018-04-02", "A", "rev_yoy_q")), "quarterly value dropped at 367 days")
    check(np.isclose(val("2018-04-02", "A", "rev_yoy_ttm"), 0.28), "yearly (TTM) value kept at 367 days (limit 550)")


# 2 --------------------------------------------------------------------------------------
def dataset_structure(new: pd.DataFrame) -> None:
    section("2. Dataset vs v7 backup")
    old = pd.read_parquet(V7_PATH)
    check(len(old) == len(new), f"same row count ({len(old):,} vs {len(new):,})")
    check(old[["Date", "Ticker"]].equals(new[["Date", "Ticker"]]), "same rows in the same order")
    later = [*F.MARGIN_FEATURES, *F.GROWTH2_FEATURES]  # batch 2 and growth round 2 columns, added after growth
    added = [c for c in new.columns if c not in old.columns and c not in later]
    removed = [c for c in old.columns if c not in new.columns]
    check(added == F.GROWTH_FEATURES and not removed, f"added exactly the six growth columns: {added}")
    changed = [c for c in old.columns if not old[c].equals(new[c])]
    check(not changed, f"all {len(old.columns)} old columns identical" + (f" (changed: {changed})" if changed else ""))
    fnew = [c for c in feature_columns(new) if c not in feature_columns(old) and c not in later]
    check(fnew == F.GROWTH_FEATURES, f"model inputs gain exactly the six growth columns (+ {len(later)} later columns)")
    dtypes = {c: str(new[c].dtype) for c in F.GROWTH_FEATURES}
    check(all(v == "float32" for v in dtypes.values()), "growth columns are float32")


# 3 --------------------------------------------------------------------------------------
def real_date_rules(new: pd.DataFrame, q: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    section("3. Date rules on real data")
    for name, r in (("quarterly", q), ("yearly", t)):
        a = r.dropna(subset=["ann"])
        lag = (a["ann"] - a["reportperiod"]).dt.days
        check((lag >= F.MIN_DAYS_AFTER_PERIOD).all(), f"{name}: every announcement ≥ 10 days after period end ({len(a):,})")
        check((a["ann"] <= a["date"]).all(), f"{name}: every announcement on or before its SEC filing")
        check((r["news_date"] <= r["date"]).all(), f"{name}: news date never after the filing date")
        gap = (r["news_date"] - r["reportperiod"]).dt.days
        check((gap >= F.MIN_DAYS_AFTER_PERIOD).all(), f"{name}: news date always ≥ 10 days after period end (min {gap.min()})")
        periods = r[["ticker", "reportperiod"]].drop_duplicates().sort_values("reportperiod")
        probe = a.assign(cut=a["ann"] - pd.Timedelta(days=F.MIN_DAYS_AFTER_PERIOD))[["ticker", "ann", "cut", "reportperiod"]]
        own = pd.merge_asof(
            probe.sort_values("cut"), periods.rename(columns={"reportperiod": "owner"}),
            left_on="cut", right_on="owner", by="ticker", direction="backward",
        )
        check((own["owner"] == own["reportperiod"]).all(), f"{name}: each announcement belongs to the newest quarter ended ≥ 10 days before it")
        print(f"     announcement → filing gap: median {(a['date'] - a['ann']).dt.days.median():.0f} days; "
              f"period end → news: median {(r['news_date'] - r['reportperiod']).dt.days.median():.0f} days")

    g = F.growth_feature_frame(new[["Date", "Ticker"]], q, t, with_dates=True)
    m = new[["Date", "Ticker", *F.GROWTH_FEATURES]].merge(g, on=["Date", "Ticker"], suffixes=("", "_re"), validate="one_to_one")
    check(all(same(m[c], m[f"{c}_re"]).all() for c in F.GROWTH_FEATURES), "dataset values = fresh recompute")
    for tag, cols, limit in (("q", ["rev_yoy_q", "gp_yoy_q", "rev_accel"], F.QUARTER_STALE_DAYS), ("t", ["rev_yoy_ttm"], F.TTM_STALE_DAYS)):
        news, period = m[f"news_{tag}"], m[f"period_{tag}"]
        check((news.isna() | (news < m["Date"])).all(), f"{tag}: every used report was public strictly before the row date")
        has = m[cols].notna().any(axis=1)
        age = (m["Date"] - period).dt.days
        check((age[has] <= limit).all(), f"{tag}: no value older than {limit} days since period end")
        s = m.loc[period.notna(), ["Ticker", "Date", f"period_{tag}"]].sort_values(["Ticker", "Date"])
        back = s.groupby("Ticker")[f"period_{tag}"].diff().dt.days < 0
        check(not back.any(), f"{tag}: the quarter shown for a stock never goes backwards in time")
    dsn = m["days_since_news"].dropna()
    check((dsn >= 1).all(), f"days_since_news ≥ 1 everywhere (min {dsn.min():.0f})")
    return m


# 4 --------------------------------------------------------------------------------------
_PREV_Q = {3: (12, -1), 6: (3, 0), 9: (6, 0), 12: (9, 0)}


def _slow_reports(raw: pd.DataFrame, anns: list[pd.Timestamp], value_cols: list[str]) -> dict:
    best: dict = {}
    for r in raw.to_dict("records"):
        if (r["date"] - r["reportperiod"]).days < F.MIN_DAYS_AFTER_PERIOD:
            continue
        k = r["calendardate"]
        if k not in best or r["date"] < best[k]["date"]:
            best[k] = r
    reports = list(best.values())
    by_period: dict = {}
    for r in reports:
        if r["reportperiod"] not in by_period or r["calendardate"] > by_period[r["reportperiod"]]["calendardate"]:
            by_period[r["reportperiod"]] = r
    periods = sorted(by_period)
    for r in reports:
        r["news"] = r["date"]
    for a in anns:
        cut = a - timedelta(days=F.MIN_DAYS_AFTER_PERIOD)
        earlier = [p for p in periods if p <= cut]
        if not earlier:
            continue
        r = by_period[max(earlier)]
        if a <= r["date"] and (r.get("ann") is None or a > r["ann"]):
            r["ann"] = a
    for r in reports:
        if r.get("ann") is not None:
            r["news"] = r["ann"]
    out = {r["calendardate"]: r for r in reports}

    def yoy(r, col):
        cd = r["calendardate"]
        p = out.get(pd.Timestamp(cd.year - 1, cd.month, cd.day))
        if p is None or not (r[col] > 0 and p[col] > 0) or p["news"] > r["news"]:
            return np.nan
        return r[col] / p[col] - 1.0

    for r in reports:
        for c in value_cols:
            r[f"yoy_{c}"] = yoy(r, c)
    for r in reports:
        cd = r["calendardate"]
        mo, dy = _PREV_Q[cd.month]
        pq = out.get(pd.Timestamp(cd.year + dy, mo, 1) + pd.offsets.MonthEnd(0))
        ok = pq is not None and pq["news"] <= r["news"]
        r["accel"] = r["yoy_revenue"] - pq["yoy_revenue"] if ok else np.nan
    return out


def _slow_attach(reports: dict, date: pd.Timestamp, stale: int):
    kept, newest = [], None
    for r in sorted(reports.values(), key=lambda r: (r["news"], r["reportperiod"])):
        if newest is None or r["reportperiod"] > newest:
            kept.append(r)
        newest = r["reportperiod"] if newest is None else max(newest, r["reportperiod"])
    seen = [r for r in kept if r["news"] < date]
    if not seen:
        return None, None
    r = seen[-1]
    return (r if (date - r["reportperiod"]).days <= stale else None), r["news"]


def independent_recompute(new: pd.DataFrame, n_tickers: int = 300, per_ticker: int = 10) -> None:
    section("4. Independent slow recompute (plain Python)")
    rng = np.random.default_rng(0)
    tickers = sorted(new["Ticker"].unique())
    pick = sorted(set(rng.choice(tickers, size=n_tickers, replace=False)) | {"NVDA", "AAPL", "MSFT"})
    cols = ["ticker", "calendardate", "reportperiod", "date"]
    arq = pd.read_parquet(F._FUND_PATH, columns=[*cols, "revenue", "gp"], filters=[("dimension", "==", "ARQ"), ("ticker", "in", pick)])
    art = pd.read_parquet(F._FUND_PATH, columns=[*cols, "revenue"], filters=[("dimension", "==", "ART"), ("ticker", "in", pick)])
    for df in (arq, art):
        for c in ("calendardate", "reportperiod", "date"):
            df[c] = pd.to_datetime(df[c])
    ev = pd.read_parquet(F._EVENTS_PATH, columns=["ticker", "date", "eventcodes"], filters=[("ticker", "in", pick)])
    ann_by = {
        tk: sorted({pd.Timestamp(d) for d, codes in zip(g["date"], g["eventcodes"]) if "22" in str(codes).split("|")})
        for tk, g in ev.groupby("ticker")
    }
    rows = new.loc[new["Ticker"].isin(pick), ["Date", "Ticker", *F.GROWTH_FEATURES]]
    rows = rows.sample(frac=1.0, random_state=0).groupby("Ticker").head(per_ticker)
    mism, n = [], 0
    for tk, g in rows.groupby("Ticker"):
        rq = _slow_reports(arq[arq["ticker"] == tk], ann_by.get(tk, []), ["revenue", "gp"])
        rt = _slow_reports(art[art["ticker"] == tk].assign(gp=np.nan), ann_by.get(tk, []), ["revenue"])
        for r in g.itertuples(index=False):
            date = pd.Timestamp(r.Date)
            aq, nq = _slow_attach(rq, date, F.QUARTER_STALE_DAYS)
            at, nt = _slow_attach(rt, date, F.TTM_STALE_DAYS)
            news = [x for x in (nq, nt) if x is not None]
            want = {
                "rev_yoy_q": aq["yoy_revenue"] if aq else np.nan,
                "gp_yoy_q": aq["yoy_gp"] if aq else np.nan,
                "rev_accel": aq["accel"] if aq else np.nan,
                "rev_yoy_ttm": at["yoy_revenue"] if at else np.nan,
                "days_since_news": (date - max(news)).days if news else np.nan,
            }
            want["has_growth"] = float(any(not np.isnan(want[c]) for c in ("rev_yoy_q", "gp_yoy_q", "rev_yoy_ttm")))
            n += 1
            bad = [c for c, v in want.items() if not same([getattr(r, c)], [v])[0]]
            if bad:
                mism.append((tk, date.date(), bad, {c: (getattr(r, c), want[c]) for c in bad}))
    check(not mism, f"{n:,} sampled rows ({len(pick)} stocks) match the slow version exactly")
    for x in mism[:10]:
        print("     mismatch:", x)


# 5 --------------------------------------------------------------------------------------
def volume_test(q: pd.DataFrame, tickers: set[str]) -> None:
    section("5. Trading volume around news dates")
    warnings.simplefilter("ignore", RuntimeWarning)
    vol = load_panel("volume")
    v = vol.to_numpy(dtype="float64")
    col = pd.Series(np.arange(vol.shape[1]), index=vol.columns.astype(str))
    days = vol.index

    def abnormal(tk: pd.Series, when: pd.Series, offsets: list[int]) -> np.ndarray:
        ci = col.reindex(tk.to_numpy()).to_numpy()
        pos = days.searchsorted(when.to_numpy())
        ok = ~np.isnan(ci) & (pos >= 30) & (pos + max(offsets) < len(days))
        ci, pos = ci[ok].astype(int), pos[ok]
        base = np.nanmedian(v[pos[:, None] + np.arange(-25, -5)[None, :], ci[:, None]], axis=1)
        base = np.where(base > 0, base, np.nan)
        return np.stack([v[pos + k, ci] / base for k in offsets], axis=1)

    a = q.dropna(subset=["ann"])
    a = a[a["ticker"].isin(tickers) & ((a["date"] - a["ann"]).dt.days >= 7)]
    offsets = [-3, -2, -1, 0, 1, 2, 3]
    prof = abnormal(a["ticker"], a["ann"], offsets)
    print(f"     {len(prof):,} quarters with filing ≥ 7 days after the announcement")
    print("     median volume vs normal, by trading day relative to the announcement date:")
    print("     " + " | ".join(f"{k:+d}: {np.nanmedian(prof[:, i]):.2f}×" for i, k in enumerate(offsets)))
    spike_ann = np.nanmax(prof[:, 3:5], axis=1)
    spike_fil = np.nanmax(abnormal(a["ticker"], a["date"], [0, 1]), axis=1)
    print(f"     day 0–1 spike: announcement median {np.nanmedian(spike_ann):.2f}× ({np.nanmean(spike_ann > 2):.0%} > 2×) "
          f"| filing median {np.nanmedian(spike_fil):.2f}× ({np.nanmean(spike_fil > 2):.0%} > 2×)")
    check(np.nanmedian(spike_ann) > 1.5 * np.nanmedian(spike_fil), "volume spikes at the announcement, not the later filing")
    valid = prof[np.isfinite(prof).any(axis=1)]
    peak = np.array(offsets)[np.argmax(np.where(np.isfinite(valid), valid, -np.inf), axis=1)]
    print(f"     biggest-volume day: {np.mean(peak <= -1):.0%} before day 0, "
          f"{np.mean(np.isin(peak, [0, 1])):.0%} on day 0–1, {np.mean(peak >= 2):.0%} on day 2–3")
    check(np.nanmedian(prof[:, 3:5]) > max(np.nanmedian(prof[:, i]) for i in (0, 1, 5, 6)), "volume peaks on day 0–1 (dates not early or late)")


# 6 --------------------------------------------------------------------------------------
def hand_checks(new: pd.DataFrame, q: pd.DataFrame) -> None:
    section("6. Hand checks")
    cases = [
        ("NVDA", "2016-10-30", "2016-10-01", "2016-12-10"),
        ("AAPL", "2016-09-24", "2016-10-01", "2016-11-20"),
        ("MSFT", "2002-03-31", "2002-04-01", "2002-06-01"),
    ]
    for tk, period, lo, hi in cases:
        mine = q[(q["ticker"] == tk) & ((q["reportperiod"] - D(period)).abs() <= pd.Timedelta(days=7))]
        if mine.empty:
            check(False, f"{tk}: report for the quarter ending ~{period} found")
            continue
        r = mine.iloc[0]
        print(f"     {tk} quarter ending {period}: announced {r['ann'].date() if pd.notna(r['ann']) else '—'} | "
              f"filed {r['date'].date()} | news {r['news_date'].date()} | revenue {r['revenue']:,.0f} | YoY {r['rev_yoy_q']:+.1%}")
        rows = new[(new["Ticker"] == tk) & new["Date"].between(D(lo), D(hi))]
        for x in rows.itertuples(index=False):
            print(f"       {x.Date.date()}  rev_yoy_q {x.rev_yoy_q:+.3f}  gp_yoy_q {x.gp_yoy_q:+.3f}  "
                  f"rev_yoy_ttm {x.rev_yoy_ttm:+.3f}  days_since_news {x.days_since_news:.0f}")
        after = rows[rows["Date"] > r["news_date"]]
        before = rows[rows["Date"] <= r["news_date"]]
        check(
            len(after) and np.isclose(after["rev_yoy_q"].iloc[0], r["rev_yoy_q"], rtol=1e-5)
            and (before.empty or not np.isclose(before["rev_yoy_q"].iloc[-1], r["rev_yoy_q"], rtol=1e-5)),
            f"{tk}: new quarter appears on the first row after {r['news_date'].date()}, not before",
        )


# 7 --------------------------------------------------------------------------------------
def coverage(m: pd.DataFrame, q: pd.DataFrame) -> None:
    section("7a. Coverage by year (share of rows)")
    src = (
        q[["ticker", "reportperiod", "news_date", "ann"]]
        .rename(columns={"ticker": "Ticker", "reportperiod": "period_q", "news_date": "news_q"})
        .drop_duplicates(["Ticker", "period_q", "news_q"])
    )
    x = m.merge(src, on=["Ticker", "period_q", "news_q"], how="left", validate="many_to_one")
    x["year"] = x["Date"].dt.year
    x["by_ann"] = x["ann"].notna().where(x["period_q"].notna())
    by = x.groupby("year").agg(
        rows=("Ticker", "size"),
        growth=("has_growth", "mean"),
        rev_yoy_q=("rev_yoy_q", lambda s: s.notna().mean()),
        by_ann=("by_ann", "mean"),
    )
    print("     year | rows | has growth | quarterly YoY | latest quarter dated by announcement")
    for y, r in by.iterrows():
        print(f"     {y} | {r['rows']:,.0f} | {r['growth']:.0%} | {r['rev_yoy_q']:.0%} | {r['by_ann']:.0%}")


def _day_ranks(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return df.groupby("Date")[cols].rank(pct=True)


def correlations(new: pd.DataFrame) -> None:
    section("7b. Correlations (per-date ranks, every 4th date)")
    dates = np.sort(new["Date"].unique())[::4]
    s = new[new["Date"].isin(dates)]
    old = [c for c in feature_columns(new) if c not in F.GROWTH_FEATURES]
    r = _day_ranks(s, [*F.GROWTH_FEATURES, *old])
    c = r.corr()
    g = F.GROWTH_FEATURES
    print("     " + " ".join(f"{x[:10]:>10s}" for x in g))
    for a in g:
        print(f"     {a[:15]:15s}" + " ".join(f"{c.loc[a, b]:+10.2f}" for b in g))
    print("     strongest link to an old feature:")
    for a in g:
        other = c.loc[a, old].abs().sort_values(ascending=False)
        print(f"       {a}: {other.index[0]} {c.loc[a, other.index[0]]:+.2f}")
    top = max(abs(c.loc[a, b]) for a in g for b in g if a != b)
    print(f"     highest growth-growth correlation {top:.2f} (prep drops one of a pair above 0.92)")


def _mean_ic(df: pd.DataFrame, col: str, label: str) -> float:
    d = df[["Date", col, label]].dropna()
    r = d.groupby("Date")[[col, label]].rank(pct=True)
    r["Date"] = d["Date"]
    per = r.groupby("Date").apply(lambda g: g[col].corr(g[label]) if len(g) > 20 else np.nan)
    return float(per.mean())


def leak_power(new: pd.DataFrame, q: pd.DataFrame, t: pd.DataFrame) -> None:
    section("7c. Leak-power test (dev rows only, label = 3-month return vs SPY)")
    calendar = pd.DatetimeIndex(benchmark_closeadj().index)
    dev = dev_rows(new, "3m", calendar)
    dev = dev[dev["Date"].dt.year >= 2005]
    keys = dev[["Date", "Ticker"]]
    fake = q.assign(news_date=q["reportperiod"] + pd.Timedelta(days=1))
    fake_t = t.assign(news_date=t["reportperiod"] + pd.Timedelta(days=1))
    leaky = F.growth_feature_frame(keys, fake, fake_t)[["Date", "Ticker", "rev_yoy_q"]].rename(columns={"rev_yoy_q": "rev_yoy_q_leaky"})
    x = dev[["Date", "Ticker", "rev_yoy_q", "excess_3m"]].merge(leaky, on=["Date", "Ticker"], validate="one_to_one")
    if len(x) != len(dev):
        raise RuntimeError("leak test lost rows in the merge")
    x["rev_yoy_q_placebo"] = F.shuffle_growth_within_date(dev[["Date", "Ticker", *F.GROWTH_FEATURES]].reset_index(drop=True), 42)["rev_yoy_q"].to_numpy()
    real, bad, plc = (_mean_ic(x, c, "excess_3m") for c in ("rev_yoy_q", "rev_yoy_q_leaky", "rev_yoy_q_placebo"))
    print(f"     rank IC with next-3-month return: real dates {real:+.4f} | fake early dates (quarter end + 1 day) {bad:+.4f} | placebo {plc:+.4f}")
    check(bad > real + 0.005, "using fake early dates gives a clearly higher IC (so the test can catch a leak)")
    check(abs(plc) < 0.005, "placebo has ~zero IC")


def placebo_sanity(new: pd.DataFrame) -> None:
    section("7d. Placebo sanity")
    base = new[["Date", "Ticker", *F.GROWTH_FEATURES, "mom_252"]]
    p = F.shuffle_growth_within_date(base, 42)
    p2 = F.shuffle_growth_within_date(base, 7)
    check(p[["Date", "Ticker", "mom_252"]].equals(base[["Date", "Ticker", "mom_252"]]), "non-growth columns untouched")
    key = ["Date", *F.GROWTH_FEATURES]
    srt = lambda d: d[key].sort_values(key, na_position="first").reset_index(drop=True)
    check(srt(p).equals(srt(base)), "each date keeps the same six-value blocks (only moved between stocks)")
    stay = (p[F.GROWTH_FEATURES].fillna(-9e9).to_numpy() == base[F.GROWTH_FEATURES].fillna(-9e9).to_numpy()).all(axis=1).mean()
    print(f"     rows whose block stayed identical: {stay:.2%} (expected ~1 / stocks per date, plus identical blocks)")
    check(stay < 0.05, "almost every stock gets another stock's block")
    check(not p[F.GROWTH_FEATURES].equals(p2[F.GROWTH_FEATURES]), "different seeds give different shuffles")
    rr = _day_ranks(pd.DataFrame({"Date": base["Date"], "a": base["rev_yoy_q"], "b": p["rev_yoy_q"]}), ["a", "b"]).corr().iloc[0, 1]
    print(f"     rank correlation real vs placebo rev_yoy_q: {rr:+.4f}")
    check(abs(rr) < 0.01, "placebo values unrelated to the real ones")


def main() -> int:
    synthetic_cases()
    new = pd.read_parquet(DATASET_PATH)
    dataset_structure(new)
    q, t = F.quarterly_growth_reports(), F.ttm_growth_reports()
    m = real_date_rules(new, q, t)
    independent_recompute(new)
    volume_test(q, set(new["Ticker"].unique()))
    hand_checks(new, q)
    coverage(m, q)
    correlations(new)
    leak_power(new, q, t)
    placebo_sanity(new)
    failed = [n for ok, n in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    for n in failed:
        print(f"FAILED: {n}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
