#!/usr/bin/env python3
"""
Date and leak checks for the growth round 2 features (no training, no 2022+ labels).

1. Made-up cases: earnings-reaction window (weekend news, day −2 / +2 moves left out, known only
   after day +1), sales surprise (std floor), steady quarters, 3-year growth, prior quarters
   public first, staleness, end of the price data.
2. Dataset: rows, order and all old columns identical to the batch 2 backup; exactly the four
   round 2 columns added.
3. Training frames: with the round 2 groups off, every older model frame (plain, growth, margins,
   their placebos) equals the one built from the backup, so the v9 baselines and batch 2 runs stay
   valid. Each group adds only its own columns; its placebo moves only them.
4. Real data: strictly-after (reaction: after day +1), staleness, never-backwards; dataset = fresh
   recompute.
5. Independent slow re-implementation (plain Python, no merge_asof) on sampled rows.
6. Hand checks (NVDA, AAPL) printed for eyeballing.
7. Coverage by year, value notes, correlations, leak-power test (fake early dates must look
   better), placebo sanity.

Usage: PYTHONPATH=. python scripts/check_growth2_features.py
Exits 1 if any check fails.
"""

from __future__ import annotations

import statistics
import sys
from bisect import bisect_left
from calendar import monthrange

import numpy as np
import pandas as pd

from check_growth_features import RSI_FIX_ROWS, _day_ranks, _mean_ic, _slow_attach, _slow_reports, same, without_rsi_fix_rows
from pinky import fundamentals as F
from pinky.dataset import feature_columns
from pinky.pit_dataset import DATASET_PATH, DERIVED_DIR
from pinky.train import MODEL_FIXES, dev_rows, pit_training_frame
from pinky.universe import benchmark_closeadj, load_panel

BATCH2_PATH = DERIVED_DIR / "pit_dataset_batch2.parquet"
RESULTS: list[tuple[bool, str]] = []
D = pd.Timestamp
G2 = F.GROWTH2_FEATURES
SINGLES = ("ear", "sue", "cagr", "steady")


def check(ok, name: str) -> None:
    RESULTS.append((bool(ok), name))
    print(f"{'PASS' if ok else 'FAIL'} - {name}")


def section(title: str) -> None:
    print(f"\n## {title}\n")


def prices() -> tuple[pd.DataFrame, pd.Series]:
    tr = load_panel("tr")
    return tr, benchmark_closeadj().reindex(tr.index).ffill()


# 1 --------------------------------------------------------------------------------------
def _toy_prices() -> tuple[pd.DataFrame, pd.Series]:
    cal = pd.bdate_range("2012-01-02", "2019-12-31")
    a = pd.Series(10.0, index=cal)
    a[D("2015-05-08"):] = 10.5  # Fri = day −1 of the Sun 2015-05-10 news → inside its window
    steps = {"2015-08-03": 9.45, "2015-08-04": 10.5, "2015-08-05": 11.55, "2015-08-06": 12.6, "2015-08-07": 13.65}
    for d, v in steps.items():
        a[D(d)] = v
    a[D("2015-08-10"):] = 21.0  # day +2 of the Thu 2015-08-06 announcement → outside
    spy = pd.Series(100.0, index=cal)
    spy[D("2015-08-05"):] = 101.0
    return pd.DataFrame({"A": a, "C": 10.0}), spy


def synthetic_cases() -> None:
    section("1. Made-up cases")
    rev = [100, 104, 108, 112, 110, 115, 120, 125, 130, 140, 150, 170, 180, 185, 190, 200]
    qe = pd.date_range("2012-03-31", periods=16, freq="QE")
    rows = [("A", c, c, c + pd.Timedelta(days=40), float(r), 0.4 * r) for c, r in zip(qe, rev)]
    b_rev = [100, 100, 100, 100, 90, 110, 95, 120, 100, 100, 100, 100]
    rows += [("B", c, c, c + pd.Timedelta(days=40), float(r), 0.4 * r) for c, r in zip(qe, b_rev)]
    late = {D("2014-12-31"): D("2015-08-30")}  # C = A, but its Q4 2014 report came out after Q1 and Q2 2015
    rows += [("C", c, c, late.get(c, c + pd.Timedelta(days=40)), float(r), 0.4 * r) for c, r in zip(qe[:15], rev)]
    rows += [("N", D("2015-06-30"), D("2015-06-30"), D("2015-08-10"), 100.0, 40.0)]  # no prices
    rows += [("C", D("2019-09-30"), D("2019-09-30"), D("2019-12-31"), 300.0, 120.0)]  # day +1 past the data
    rows += [("L", D("2012-06-30"), D("2012-06-30"), D("2016-01-15"), 100.0, 40.0),  # filed 3.5 years late
             ("L", D("2015-06-30"), D("2015-06-30"), D("2015-08-10"), 150.0, 60.0)]
    raw = pd.DataFrame(rows, columns=["ticker", "calendardate", "reportperiod", "date", "revenue", "gp"])
    anns = pd.DataFrame([("A", D("2015-08-06"))], columns=["ticker", "ann"]).astype({"ann": "datetime64[us]"})
    tr, spy = _toy_prices()
    q = F.quarterly_growth2_reports(tr, spy, raw, anns)
    t = F.ttm_growth2_reports(raw.drop(columns="gp"), anns)
    qi, ti = q.set_index(["ticker", "calendardate"]), t.set_index(["ticker", "calendardate"])

    def yoy(cur: float, prev: float) -> float:
        return cur / prev - 1.0

    prev4 = [yoy(110, 100), yoy(115, 104), yoy(120, 108), yoy(125, 112)]
    check(np.std(prev4, ddof=1) < F.SUE_MIN_STD, "toy: previous 4 quarters' growth spread below the 0.01 floor")
    want = (yoy(130, 110) - np.mean(prev4)) / F.SUE_MIN_STD
    check(np.isclose(qi.loc[("A", D("2014-03-31")), "rev_sue"], want), "sales surprise uses the 0.01 floor when the spread is tiny")
    prev4 = [yoy(140, 115), yoy(150, 120), yoy(170, 125), yoy(180, 130)]
    want = (yoy(185, 140) - np.mean(prev4)) / np.std(prev4, ddof=1)
    check(np.isclose(qi.loc[("A", D("2015-06-30")), "rev_sue"], want), "sales surprise = (growth − mean of 4 before) / their std")
    check(np.isnan(qi.loc[("A", D("2013-12-31")), "rev_sue"]), "no surprise without 4 earlier quarters of growth")
    check(qi.loc[("A", D("2014-12-31")), "rev_up_quarters"] == 8, "steady: 8 of 8 quarters grew")
    check(np.isnan(qi.loc[("A", D("2014-09-30")), "rev_up_quarters"]), "steady: missing with only 7 known quarters")
    check(qi.loc[("B", D("2014-12-31")), "rev_up_quarters"] == 4, "steady: 4 of 8 quarters grew (ups and downs)")
    check(np.isnan(qi.loc[("C", D("2015-03-31")), "rev_sue"]), "surprise missing when an earlier quarter became public later")
    check(np.isnan(qi.loc[("C", D("2015-03-31")), "rev_up_quarters"]), "steady missing when an earlier quarter became public later")
    check(np.isclose(ti.loc[("A", D("2015-12-31")), "rev_cagr_3y"], (200 / 112) ** (1 / 3) - 1), "3-year growth (200 / 112)^(1/3) − 1")
    check(np.isnan(ti.loc[("A", D("2014-12-31")), "rev_cagr_3y"]), "no 3-year growth without a report 3 years earlier")
    check(np.isnan(ti.loc[("L", D("2015-06-30")), "rev_cagr_3y"]), "3-year growth needs the earlier report public first")

    check(qi.loc[("A", D("2015-06-30")), "news_date"] == D("2015-08-06"), "toy: the Thu announcement is the news date")
    check(np.isclose(qi.loc[("A", D("2015-06-30")), "ear_3d"], 0.30 - 0.01), "reaction = +30% stock − 1% SPY over days −1…+1")
    check(qi.loc[("A", D("2015-06-30")), "ear_known"] == D("2015-08-07"), "reaction known at day +1 (Fri)")
    check(qi.loc[("A", D("2015-03-31")), "news_date"] == D("2015-05-10"), "toy: a Sunday filing date is the news date")
    check(np.isclose(qi.loc[("A", D("2015-03-31")), "ear_3d"], 0.05), "Sunday news: day 0 = Mon, so the Fri move is day −1 (+5%)")
    check(qi.loc[("A", D("2015-03-31")), "ear_known"] == D("2015-05-12"), "Sunday news: known Tue (day +1)")
    check(np.isnan(qi.loc[("N", D("2015-06-30")), "ear_3d"]) and pd.notna(qi.loc[("N", D("2015-06-30")), "ear_known"]),
          "no prices → reaction missing (but still dated, so an older one can't show)")
    check(pd.isna(qi.loc[("C", D("2019-09-30")), "ear_known"]), "day +1 past the price data → reaction not known yet")

    rows = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                ["2015-05-11", "2015-05-12", "2015-05-13", "2015-08-06", "2015-08-07", "2015-08-10",
                 "2016-12-30", "2017-01-03", "2015-09-02"]
            ).astype("datetime64[us]"),
            "Ticker": ["A"] * 8 + ["C"],
        }
    )
    g = F.growth2_feature_frame(rows, q, t, with_dates=True).set_index(["Date", "Ticker"])

    def val(d: str, c: str, tk: str = "A") -> float:
        return g.loc[(D(d), tk), c]

    check(np.isclose(val("2015-05-12", "ear_3d"), 0.0), "Tue (day +1): still the older quarter's reaction (flat → 0)")
    check(np.isclose(val("2015-05-13", "ear_3d"), 0.05), "Wed (day +2): the new reaction shows")
    check(np.isclose(val("2015-05-11", "rev_up_quarters"), 8) and val("2015-05-11", "period_q") == D("2015-03-31"),
          "Mon after Sunday news: the new quarter's sales numbers already show")
    check(val("2015-08-06", "period_q") == D("2015-03-31"), "on the announcement day the new quarter is hidden")
    check(val("2015-08-07", "period_q") == D("2015-06-30") and np.isclose(val("2015-08-07", "ear_3d"), 0.05),
          "day +1: new sales numbers, old reaction")
    check(np.isclose(val("2015-08-10", "ear_3d"), 0.29), "day +2: the new reaction (+29%, the day +2 jump left out)")
    check(pd.notna(val("2016-12-30", "ear_3d")), "reaction kept 365 days after the quarter end")
    check(np.isnan(val("2017-01-03", "ear_3d")) and np.isnan(val("2017-01-03", "rev_sue")), "dropped at 369 days")
    check(val("2015-09-02", "period_q", "C") == D("2015-06-30"), "a late catch-up filing never replaces a newer quarter")


# 2 --------------------------------------------------------------------------------------
def dataset_structure(old: pd.DataFrame, new: pd.DataFrame) -> None:
    section("2. Dataset vs batch 2 backup")
    check(len(old) == len(new), f"same row count ({len(old):,} vs {len(new):,})")
    check(old[["Date", "Ticker"]].equals(new[["Date", "Ticker"]]), "same rows in the same order")
    added = [c for c in new.columns if c not in old.columns]
    removed = [c for c in old.columns if c not in new.columns]
    check(added == G2 and not removed, f"added exactly the four round 2 columns: {added}")
    changed = [c for c in old.columns if not old[c].equals(new[c])]
    check(not changed, f"all {len(old.columns)} old columns identical" + (f" (changed: {changed})" if changed else ""))
    check([c for c in new.columns if c in old.columns] == list(old.columns), "old columns keep their order")
    fnew = [c for c in feature_columns(new) if c not in feature_columns(old)]
    check(fnew == G2, f"model inputs gain exactly the four round 2 columns ({len(feature_columns(new))} total)")
    check(all(str(new[c].dtype) == "float32" for c in G2), "round 2 columns are float32")


# 3 --------------------------------------------------------------------------------------
def training_frames(old: pd.DataFrame, new: pd.DataFrame) -> None:
    section("3. Training frames (A and B share inputs; rank_label only changes the label)")
    base = list(MODEL_FIXES)
    for name, fixes, placebo in (
        ("v9 plain (A and B baselines)", base, None),
        ("v9 with growth", [*base, "growth"], None),
        ("v9 with growth, placebo seed 42", [*base, "growth"], True),
        ("v9 with margins, margin placebo seed 7", [*base, "margins"], "margins"),
        ("v9 with growth + margins", [*base, "growth", "margins"], None),
    ):
        seed = 7 if placebo == "margins" else 42
        same_frame = pit_training_frame(old, fixes, placebo, seed).equals(pit_training_frame(new, fixes, placebo, seed))
        check(same_frame, f"{name}: frame from the new dataset = frame from the batch 2 backup")

    plain = pit_training_frame(new, base)
    for g in (*SINGLES, "growth2"):
        cols = F.GROUP_FEATURES[g]
        real = pit_training_frame(new, [*base, g])
        check(set(real.columns) - set(plain.columns) == set(cols) and real.drop(columns=cols).equals(plain),
              f"{g}: frame = plain frame + {cols}")
        plc = pit_training_frame(new, [*base, g], g, 7)
        check(plc.drop(columns=cols).equals(real.drop(columns=cols)), f"{g} placebo leaves every other column identical")
        key = ["Date", *cols]
        srt = lambda d: d[key].sort_values(key).reset_index(drop=True)
        check(srt(plc).equals(srt(real)), f"{g} placebo keeps each date's values (only moved between stocks)")
        rr = max(abs(_day_ranks(pd.DataFrame({"Date": real["Date"], "a": real[c], "b": plc[c]}), ["a", "b"]).corr().iloc[0, 1])
                 for c in cols)
        check(rr < 0.01, f"{g} placebo unrelated to the real values (|rank corr| ≤ {rr:.4f})")
        del real, plc


# 4 --------------------------------------------------------------------------------------
def real_date_rules(new: pd.DataFrame, q: pd.DataFrame, t: pd.DataFrame, cal: pd.DatetimeIndex) -> None:
    section("4. Date rules on real data")
    has_known = q["ear_known"].notna()
    day0 = cal.searchsorted(q["news_date"].to_numpy(), side="left")
    nxt = pd.Series(cal[np.minimum(day0 + 1, len(cal) - 1)], index=q.index)
    check((q.loc[has_known, "ear_known"] == nxt[has_known]).all(), "reaction known on the trading day after day 0")
    check((q.loc[has_known, "ear_known"] > q.loc[has_known, "news_date"]).all(), "reaction always known strictly after the news date")
    print(f"     news date → reaction known: median {(q['ear_known'] - q['news_date']).dt.days.median():.0f} days, "
          f"max {(q['ear_known'] - q['news_date']).dt.days.max():.0f}")

    g = F.growth2_feature_frame(new[["Date", "Ticker"]], q, t, with_dates=True)
    m = new[["Date", "Ticker", *G2]].merge(g, on=["Date", "Ticker"], suffixes=("", "_re"), validate="one_to_one")
    check(all(same(m[c], m[f"{c}_re"]).all() for c in G2), "dataset values = fresh recompute")
    for tag, cols, limit in (
        ("e", ["ear_3d"], F.QUARTER_STALE_DAYS),
        ("q", ["rev_sue", "rev_up_quarters"], F.QUARTER_STALE_DAYS),
        ("t", ["rev_cagr_3y"], F.TTM_STALE_DAYS),
    ):
        news, period = m[f"news_{tag}"], m[f"period_{tag}"]
        check((news.isna() | (news < m["Date"])).all(), f"{tag}: every used value was known strictly before the row date")
        has = m[cols].notna().any(axis=1)
        age = (m["Date"] - period).dt.days
        check((age[has] <= limit).all(), f"{tag}: no value older than {limit} days since period end")
        s = m.loc[period.notna(), ["Ticker", "Date", f"period_{tag}"]].sort_values(["Ticker", "Date"])
        back = s.groupby("Ticker")[f"period_{tag}"].diff().dt.days < 0
        check(not back.any(), f"{tag}: the quarter shown for a stock never goes backwards in time")
    own = m.dropna(subset=["period_e"]).merge(
        q[["ticker", "reportperiod", "news_date"]].drop_duplicates(["ticker", "reportperiod"], keep="last"),
        left_on=["Ticker", "period_e"], right_on=["ticker", "reportperiod"], how="left",
    )
    check((own["news_date"] < own["news_e"]).all(), "every reaction used is dated after its own report's news date")


# 5 --------------------------------------------------------------------------------------
def _back(cd: pd.Timestamp, quarters: int) -> pd.Timestamp:
    i = cd.year * 12 + cd.month - 1 - 3 * quarters
    y, mo = divmod(i, 12)
    return pd.Timestamp(y, mo + 1, monthrange(y, mo + 1)[1])


def _slow_round2(rq: dict, rt: dict, px: list[float], spy: list[float], cal: list[pd.Timestamp]) -> dict:
    for r in rq.values():
        y = r["yoy_revenue"]
        prev = [rq.get(_back(r["calendardate"], k)) for k in range(1, 8)]
        public = [p if p is not None and p["news"] <= r["news"] else None for p in prev]
        four = [p["yoy_revenue"] for p in public[:4] if p is not None and not np.isnan(p["yoy_revenue"])]
        if not np.isnan(y) and len(four) == 4:
            r["sue"] = (y - sum(four) / 4) / max(statistics.stdev(four), F.SUE_MIN_STD)
        else:
            r["sue"] = np.nan
        eight = [y] + [p["yoy_revenue"] if p is not None else np.nan for p in public]
        r["up"] = float(sum(v > 0 for v in eight)) if not any(np.isnan(v) for v in eight) else np.nan
        d0 = bisect_left(cal, r["news"])
        s, e = d0 - 2, d0 + 1
        r["known"] = cal[e] if e < len(cal) else None
        ok = s >= 0 and e < len(cal) and np.isfinite(px[s]) and np.isfinite(px[e]) and px[s] > 0
        r["ear"] = (px[e] / px[s] - 1.0) - (spy[e] / spy[s] - 1.0) if ok else np.nan
    for r in rt.values():
        p = rt.get(_back(r["calendardate"], 12))
        ok = p is not None and r["revenue"] > 0 and p["revenue"] > 0 and p["news"] <= r["news"]
        r["cagr"] = (r["revenue"] / p["revenue"]) ** (1 / 3) - 1 if ok else np.nan
    return {k: {**r, "news": r["known"]} for k, r in rq.items() if r["known"] is not None}


def independent_recompute(new: pd.DataFrame, tr: pd.DataFrame, spy: pd.Series, n_tickers: int = 300, per_ticker: int = 10) -> None:
    section("5. Independent slow recompute (plain Python)")
    rng = np.random.default_rng(2)
    tickers = sorted(new["Ticker"].unique())
    pick = sorted(set(rng.choice(tickers, size=n_tickers, replace=False)) | {"NVDA", "AAPL", "MSFT", "AMZN"})
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
    cal = list(pd.DatetimeIndex(tr.index))
    spy_l = [float(x) for x in spy.to_numpy()]
    rows = new.loc[new["Ticker"].isin(pick), ["Date", "Ticker", *G2]]
    rows = rows.sample(frac=1.0, random_state=2).groupby("Ticker").head(per_ticker)
    mism, n = [], 0
    for tk, g in rows.groupby("Ticker"):
        rq = _slow_reports(arq[arq["ticker"] == tk], ann_by.get(tk, []), ["revenue", "gp"])
        rt = _slow_reports(art[art["ticker"] == tk].assign(gp=np.nan), ann_by.get(tk, []), ["revenue"])
        px = [float(x) for x in tr[tk].to_numpy()] if tk in tr.columns else [np.nan] * len(cal)
        re = _slow_round2(rq, rt, px, spy_l, cal)
        for r in g.itertuples(index=False):
            date = pd.Timestamp(r.Date)
            aq, _ = _slow_attach(rq, date, F.QUARTER_STALE_DAYS)
            at, _ = _slow_attach(rt, date, F.TTM_STALE_DAYS)
            ae, _ = _slow_attach(re, date, F.QUARTER_STALE_DAYS)
            want = {
                "ear_3d": ae["ear"] if ae else np.nan,
                "rev_sue": aq["sue"] if aq else np.nan,
                "rev_cagr_3y": at["cagr"] if at else np.nan,
                "rev_up_quarters": aq["up"] if aq else np.nan,
            }
            n += 1
            bad = [c for c, v in want.items() if not same([getattr(r, c)], [v], rtol=1e-4)[0]]
            if bad:
                mism.append((tk, date.date(), {c: (getattr(r, c), want[c]) for c in bad}))
    check(not mism, f"{n:,} sampled rows ({len(pick)} stocks) match the slow version exactly")
    for x in mism[:10]:
        print("     mismatch:", x)


# 6 --------------------------------------------------------------------------------------
def hand_checks(new: pd.DataFrame, q: pd.DataFrame) -> None:
    section("6. Hand checks")
    for tk, period, lo, hi in (("NVDA", "2016-10-30", "2016-10-25", "2016-12-10"), ("AAPL", "2016-09-24", "2016-10-10", "2016-11-20")):
        mine = q[(q["ticker"] == tk) & ((q["reportperiod"] - D(period)).abs() <= pd.Timedelta(days=7))]
        if mine.empty:
            check(False, f"{tk}: report for the quarter ending ~{period} found")
            continue
        r = mine.iloc[0]
        print(f"     {tk} quarter ending {period}: news {r['news_date'].date()} | reaction known {r['ear_known'].date()} | "
              f"ear_3d {r['ear_3d']:+.1%} | rev_sue {r['rev_sue']:+.2f} | up quarters {r['rev_up_quarters']:.0f}")
        rows = new[(new["Ticker"] == tk) & new["Date"].between(D(lo), D(hi))]
        for x in rows.itertuples(index=False):
            print(f"       {x.Date.date()}  ear_3d {x.ear_3d:+.4f}  rev_sue {x.rev_sue:+.3f}  "
                  f"rev_cagr_3y {x.rev_cagr_3y:+.3f}  rev_up_quarters {x.rev_up_quarters:.0f}")
        after = rows[rows["Date"] > r["ear_known"]]
        before = rows[rows["Date"] <= r["ear_known"]]
        check(
            len(after) and np.isclose(after["ear_3d"].iloc[0], r["ear_3d"], rtol=1e-5)
            and (before.empty or not np.isclose(before["ear_3d"].iloc[-1], r["ear_3d"], rtol=1e-5)),
            f"{tk}: new reaction appears on the first row after {r['ear_known'].date()}, not before",
        )


# 7 --------------------------------------------------------------------------------------
def coverage_and_values(new: pd.DataFrame) -> None:
    section("7a. Coverage by year (share of rows) and value notes")
    x = new[["Date", *G2]].assign(year=new["Date"].dt.year)
    by = x.groupby("year")[G2].agg(lambda s: s.notna().mean())
    print("     year | " + " | ".join(G2))
    for y, r in by.iterrows():
        print(f"     {y} | " + " | ".join(f"{r[c]:.0%}" for c in G2))
    e = new["ear_3d"].dropna()
    print(f"     ear_3d: median {e.median():+.4f}, 1st–99th pct {e.quantile(0.01):+.3f} … {e.quantile(0.99):+.3f}, |x| > 50%: {np.mean(e.abs() > 0.5):.3%}")
    s = new["rev_sue"].dropna()
    print(f"     rev_sue: median {s.median():+.2f}, 1st–99th pct {s.quantile(0.01):+.1f} … {s.quantile(0.99):+.1f}")
    c = new["rev_cagr_3y"].dropna()
    print(f"     rev_cagr_3y: median {c.median():+.3f}, 1st–99th pct {c.quantile(0.01):+.3f} … {c.quantile(0.99):+.3f}")
    u = new["rev_up_quarters"].dropna().value_counts(normalize=True).sort_index()
    print("     rev_up_quarters share: " + ", ".join(f"{int(k)}: {v:.0%}" for k, v in u.items()))
    check(set(u.index) <= set(range(9)), "rev_up_quarters only takes 0–8")
    print("     (A and B rank every input within each date, so extreme values only count as top / bottom ranks)")


def correlations(new: pd.DataFrame) -> None:
    section("7b. Correlations (per-date ranks, every 4th date)")
    dates = np.sort(new["Date"].unique())[::4]
    s = new[new["Date"].isin(dates)]
    old = [c for c in feature_columns(new) if c not in G2]
    c = _day_ranks(s, [*G2, *old]).corr()
    print("     " + " ".join(f"{x:>16s}" for x in G2))
    for a in G2:
        print(f"     {a:16s}" + " ".join(f"{c.loc[a, b]:+16.2f}" for b in G2))
    print("     strongest link to an older input (price, size, growth, margins):")
    for a in G2:
        other = c.loc[a, old].abs().sort_values(ascending=False)
        print(f"       {a}: {other.index[0]} {c.loc[a, other.index[0]]:+.2f}, {other.index[1]} {c.loc[a, other.index[1]]:+.2f}")
    top = max(abs(c.loc[a, b]) for a in G2 for b in [*G2, *old] if a != b)
    print(f"     highest correlation with a round 2 input {top:.2f} (prep drops one of a pair above 0.92)")


def leak_power(new: pd.DataFrame, q: pd.DataFrame, t: pd.DataFrame) -> None:
    section("7c. Leak-power test (dev rows only, label = 3-month return vs SPY)")
    calendar = pd.DatetimeIndex(benchmark_closeadj().index)
    dev = dev_rows(new, "3m", calendar)
    dev = dev[dev["Date"].dt.year >= 2005]
    keys = dev[["Date", "Ticker"]]
    early = q["reportperiod"] + pd.Timedelta(days=1)
    fake = q.assign(news_date=early, ear_known=early)
    fake_t = t.assign(news_date=t["reportperiod"] + pd.Timedelta(days=1))
    leaky = F.growth2_feature_frame(keys, fake, fake_t).rename(columns={c: f"{c}_leaky" for c in G2})
    x = dev[["Date", "Ticker", *G2, "excess_3m"]].merge(leaky, on=["Date", "Ticker"], validate="one_to_one")
    if len(x) != len(dev):
        raise RuntimeError("leak test lost rows in the merge")
    shuffled = F.shuffle_within_date(dev[["Date", "Ticker", *G2]].reset_index(drop=True), G2, 42)
    for c in G2:
        x[f"{c}_placebo"] = shuffled[c].to_numpy()
    ics = {}
    for c in G2:
        ics[c] = tuple(_mean_ic(x, col, "excess_3m") for col in (c, f"{c}_leaky", f"{c}_placebo"))
        real, bad, plc = ics[c]
        print(f"     {c}: rank IC with next-3-month return: real dates {real:+.4f} | fake early dates {bad:+.4f} | placebo {plc:+.4f}")
    for c in ("ear_3d", "rev_sue"):
        real, bad, _ = ics[c]
        check(bad > real + 0.005, f"{c}: fake early dates give a clearly higher IC (so the test can catch a leak)")
    check(all(abs(v[2]) < 0.005 for v in ics.values()), "placebo has ~zero IC for all four")


def placebo_sanity(new: pd.DataFrame) -> None:
    section("7d. Placebo sanity (all four as one block, as in test 5)")
    keep = [*F.GROWTH_FEATURES, *F.MARGIN_FEATURES, "mom_252"]
    base = new[["Date", "Ticker", *G2, *keep]]
    p = F.shuffle_within_date(base, G2, 42)
    p2 = F.shuffle_within_date(base, G2, 7)
    check(p[["Date", "Ticker", *keep]].equals(base[["Date", "Ticker", *keep]]), "growth, margins and other columns untouched")
    key = ["Date", *G2]
    srt = lambda d: d[key].sort_values(key, na_position="first").reset_index(drop=True)
    check(srt(p).equals(srt(base)), "each date keeps the same four-value blocks (only moved between stocks)")
    stay = (p[G2].fillna(-9e9).to_numpy() == base[G2].fillna(-9e9).to_numpy()).all(axis=1).mean()
    print(f"     rows whose block stayed identical: {stay:.2%}")
    check(stay < 0.05, "almost every stock gets another stock's block")
    check(not p[G2].equals(p2[G2]), "different seeds give different shuffles")


def main() -> int:
    synthetic_cases()
    old, new = pd.read_parquet(BATCH2_PATH), pd.read_parquet(DATASET_PATH)
    same_rows, problem = without_rsi_fix_rows(old, new)
    check(problem is None, f"since the batch 2 backup the dataset gained only the {RSI_FIX_ROWS} RSI-fix rows (RSI 100 or 50)"
          + (f": {problem}" if problem else ""))
    dataset_structure(old, same_rows)
    training_frames(old, same_rows)
    del old, same_rows
    tr, spy = prices()
    q, t = F.quarterly_growth2_reports(tr, spy), F.ttm_growth2_reports()
    real_date_rules(new, q, t, pd.DatetimeIndex(tr.index))
    independent_recompute(new, tr, spy)
    del tr
    hand_checks(new, q)
    coverage_and_values(new)
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
