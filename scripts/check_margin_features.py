#!/usr/bin/env python3
"""
Date and leak checks for the batch 2 margin features (no training, no 2022+ labels).

1. Made-up cases for the margin math and date rules (revenue <= 0, prior quarter public first,
   same-day rows, staleness).
2. Dataset: rows, order and all old columns identical to the v9 backup; exactly the four margin
   columns added.
3. Training frames: with margins off, every v9 model frame (A / B, growth real / placebo) equals
   the one built from the v9 backup, so the v9 baselines stay valid. Margin placebo moves only
   margin values.
4. Real data: strictly-after, staleness, never-backwards; dataset = fresh recompute.
5. Independent slow re-implementation (plain Python, no merge_asof) on sampled rows.
6. Hand checks (NVDA, AAPL) printed for eyeballing.
7. Coverage by year, value notes, correlations, leak-power test (fake early dates must look
   better), placebo sanity.

Usage: PYTHONPATH=. python scripts/check_margin_features.py
Exits 1 if any check fails.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from check_growth_features import _day_ranks, _mean_ic, _slow_attach, _slow_reports, same
from pinky import fundamentals as F
from pinky.dataset import feature_columns
from pinky.pit_dataset import DATASET_PATH, DERIVED_DIR
from pinky.train import MODEL_FIXES, dev_rows, pit_training_frame
from pinky.universe import benchmark_closeadj

V9_PATH = DERIVED_DIR / "pit_dataset_v9.parquet"
RESULTS: list[tuple[bool, str]] = []
D = pd.Timestamp
M = F.MARGIN_FEATURES


def check(ok, name: str) -> None:
    RESULTS.append((bool(ok), name))
    print(f"{'PASS' if ok else 'FAIL'} - {name}")


def section(title: str) -> None:
    print(f"\n## {title}\n")


# 1 --------------------------------------------------------------------------------------
def synthetic_cases() -> None:
    section("1. Made-up cases")
    cols = ["ticker", "calendardate", "reportperiod", "date", "revenue", "gp", "opinc"]
    raw = pd.DataFrame(
        [
            ("A", D("2015-06-30"), D("2015-06-30"), D("2015-08-10"), 100.0, 40.0, 10.0),
            ("A", D("2015-09-30"), D("2015-09-30"), D("2015-11-09"), 100.0, 40.0, 10.0),
            ("A", D("2016-06-30"), D("2016-06-30"), D("2016-08-09"), 200.0, 100.0, 30.0),
            ("A", D("2016-09-30"), D("2016-09-30"), D("2016-11-08"), 0.0, 5.0, -5.0),
            ("A", D("2016-12-31"), D("2016-12-31"), D("2017-02-24"), 50.0, 20.0, -10.0),
            ("B", D("2015-06-30"), D("2015-06-30"), D("2016-09-20"), 100.0, 30.0, 5.0),
            ("B", D("2016-06-30"), D("2016-06-30"), D("2016-08-15"), 100.0, 50.0, 20.0),
            ("C", D("2015-03-31"), D("2015-03-31"), D("2015-05-10"), 100.0, 40.0, 10.0),
            ("C", D("2016-03-31"), D("2016-03-31"), D("2016-05-10"), 100.0, 50.0, 10.0),
        ],
        columns=cols,
    )
    anns = pd.DataFrame(columns=["ticker", "ann"]).astype({"ticker": str, "ann": "datetime64[us]"})
    q = F.quarterly_margin_reports(raw, anns)
    t = F.ttm_margin_reports(raw, anns)
    qi = q.set_index(["ticker", "calendardate"])

    check(np.isclose(qi.loc[("A", D("2016-06-30")), "gm_chg_q"], 0.50 - 0.40), "gross margin change 50% − 40% = +0.10")
    check(np.isclose(qi.loc[("A", D("2016-06-30")), "om_chg_q"], 0.15 - 0.10), "operating margin change 15% − 10% = +0.05")
    check(np.isnan(qi.loc[("A", D("2016-09-30")), "gm_q"]), "revenue 0 → margin missing")
    check(np.isnan(qi.loc[("A", D("2016-09-30")), "gm_chg_q"]), "revenue 0 → change missing")
    check(np.isnan(qi.loc[("A", D("2016-12-31")), "gm_chg_q"]), "no change without a prior-year quarter")
    check(np.isnan(qi.loc[("B", D("2016-06-30")), "gm_chg_q"]), "no change when the prior-year quarter became public later")
    check(np.isclose(t.set_index(["ticker", "calendardate"]).loc[("A", D("2016-12-31")), "om_ttm"], -0.2), "TTM operating margin −10 / 50")

    rows = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2016-08-09", "2016-08-10", "2017-02-24", "2017-02-27", "2017-12-29", "2018-01-02"]).astype("datetime64[us]"),
            "Ticker": ["A"] * 6,
        }
    )
    g = F.margin_feature_frame(rows, q, t).set_index(["Date", "Ticker"])

    def val(d: str, c: str) -> float:
        return g.loc[(D(d), "A"), c]

    check(np.isnan(val("2016-08-09", "gm_chg_q")), "row on the news day still sees the older report (no prior-year match)")
    check(np.isclose(val("2016-08-10", "gm_chg_q"), 0.10), "row the day after sees the new report")
    check(np.isnan(val("2017-02-24", "om_ttm")), "on the Dec report's news day the Sep report (revenue 0 → missing) still shows")
    check(np.isclose(val("2017-02-27", "om_ttm"), -0.2), "the Dec report shows on the next row")
    stale = F.margin_feature_frame(
        pd.DataFrame({"Date": pd.to_datetime(["2017-03-30", "2017-04-03"]).astype("datetime64[us]"), "Ticker": ["C", "C"]}), q, t
    ).set_index("Date")
    check(np.isclose(stale.loc[D("2017-03-30"), "gm_chg_q"], 0.10), "quarterly value kept at 364 days")
    check(np.isnan(stale.loc[D("2017-04-03"), "gm_chg_q"]), "quarterly value dropped at 368 days")
    check(np.isclose(stale.loc[D("2017-04-03"), "gm_ttm"], 0.5), "TTM value kept at 368 days (limit 550)")


# 2 --------------------------------------------------------------------------------------
def dataset_structure(old: pd.DataFrame, new: pd.DataFrame) -> None:
    section("2. Dataset vs v9 backup")
    check(len(old) == len(new), f"same row count ({len(old):,} vs {len(new):,})")
    check(old[["Date", "Ticker"]].equals(new[["Date", "Ticker"]]), "same rows in the same order")
    added = [c for c in new.columns if c not in old.columns]
    removed = [c for c in old.columns if c not in new.columns]
    check(added == M and not removed, f"added exactly the four margin columns: {added}")
    changed = [c for c in old.columns if not old[c].equals(new[c])]
    check(not changed, f"all {len(old.columns)} old columns identical" + (f" (changed: {changed})" if changed else ""))
    check([c for c in new.columns if c in old.columns] == list(old.columns), "old columns keep their order")
    fnew = [c for c in feature_columns(new) if c not in feature_columns(old)]
    check(fnew == M, f"model inputs gain exactly the four margin columns ({len(feature_columns(new))} total)")
    check(all(str(new[c].dtype) == "float32" for c in M), "margin columns are float32")


# 3 --------------------------------------------------------------------------------------
def training_frames(old: pd.DataFrame, new: pd.DataFrame) -> None:
    section("3. Training frames (A and B share inputs; rank_label only changes the label)")
    base = list(MODEL_FIXES)
    for name, fixes, placebo in (
        ("v9 plain (A and B baselines)", base, None),
        ("v9 with growth", [*base, "growth"], None),
        ("v9 with growth, placebo seed 42", [*base, "growth"], True),
    ):
        same_frame = pit_training_frame(old, fixes, placebo).equals(pit_training_frame(new, fixes, placebo))
        check(same_frame, f"{name}: frame from the new dataset = frame from the v9 backup")

    real = pit_training_frame(new, [*base, "growth", "margins"])
    plc = pit_training_frame(new, [*base, "growth", "margins"], "margins", 7)
    plain = pit_training_frame(new, [*base, "growth"])
    check([c for c in real.columns if c not in M] == list(plain.columns) and set(real.columns) - set(plain.columns) == set(M),
          "growth + margins frame = growth frame + the four margin columns")
    check(real.drop(columns=M).equals(plain), "turning margins on leaves every other column identical")
    check(plc.drop(columns=M).equals(real.drop(columns=M)), "margin placebo leaves growth and every other column identical")
    moved = (plc[M].fillna(-9).to_numpy() != real[M].fillna(-9).to_numpy()).any(axis=1).mean()
    check(moved > 0.90, f"margin placebo moves margin values for {moved:.1%} of rows")
    alone = pit_training_frame(new, [*base, "margins"])
    check(alone.drop(columns=M).equals(pit_training_frame(new, base)), "margins alone = v9 plain frame + the four margin columns")


# 4 --------------------------------------------------------------------------------------
def real_date_rules(new: pd.DataFrame, q: pd.DataFrame, t: pd.DataFrame) -> None:
    section("4. Date rules on real data")
    for name, r in (("quarterly", q), ("yearly", t)):
        gap = (r["news_date"] - r["reportperiod"]).dt.days
        check((gap >= F.MIN_DAYS_AFTER_PERIOD).all(), f"{name}: news date always ≥ 10 days after period end (min {gap.min()})")
        check((r["news_date"] <= r["date"]).all(), f"{name}: news date never after the filing date")
    g = F.margin_feature_frame(new[["Date", "Ticker"]], q, t, with_dates=True)
    m = new[["Date", "Ticker", *M]].merge(g, on=["Date", "Ticker"], suffixes=("", "_re"), validate="one_to_one")
    check(all(same(m[c], m[f"{c}_re"]).all() for c in M), "dataset values = fresh recompute")
    for tag, cols, limit in (("q", ["gm_chg_q", "om_chg_q"], F.QUARTER_STALE_DAYS), ("t", ["gm_ttm", "om_ttm"], F.TTM_STALE_DAYS)):
        news, period = m[f"news_{tag}"], m[f"period_{tag}"]
        check((news.isna() | (news < m["Date"])).all(), f"{tag}: every used report was public strictly before the row date")
        has = m[cols].notna().any(axis=1)
        age = (m["Date"] - period).dt.days
        check((age[has] <= limit).all(), f"{tag}: no value older than {limit} days since period end")
        s = m.loc[period.notna(), ["Ticker", "Date", f"period_{tag}"]].sort_values(["Ticker", "Date"])
        back = s.groupby("Ticker")[f"period_{tag}"].diff().dt.days < 0
        check(not back.any(), f"{tag}: the quarter shown for a stock never goes backwards in time")


# 5 --------------------------------------------------------------------------------------
def _slow_margins(reports: dict) -> None:
    for r in reports.values():
        ok = r["revenue"] > 0
        r["gm"] = r["gp"] / r["revenue"] if ok else np.nan
        r["om"] = r["opinc"] / r["revenue"] if ok else np.nan
    for r in reports.values():
        cd = r["calendardate"]
        p = reports.get(pd.Timestamp(cd.year - 1, cd.month, cd.day))
        ok = p is not None and p["news"] <= r["news"]
        r["gm_chg"] = r["gm"] - p["gm"] if ok else np.nan
        r["om_chg"] = r["om"] - p["om"] if ok else np.nan


def independent_recompute(new: pd.DataFrame, n_tickers: int = 300, per_ticker: int = 10) -> None:
    section("5. Independent slow recompute (plain Python)")
    rng = np.random.default_rng(1)
    tickers = sorted(new["Ticker"].unique())
    pick = sorted(set(rng.choice(tickers, size=n_tickers, replace=False)) | {"NVDA", "AAPL", "MSFT", "JPM"})
    cols = ["ticker", "calendardate", "reportperiod", "date", "revenue", "gp", "opinc"]
    raw = {
        dim: pd.read_parquet(F._FUND_PATH, columns=cols, filters=[("dimension", "==", dim), ("ticker", "in", pick)])
        for dim in ("ARQ", "ART")
    }
    for df in raw.values():
        for c in ("calendardate", "reportperiod", "date"):
            df[c] = pd.to_datetime(df[c])
    ev = pd.read_parquet(F._EVENTS_PATH, columns=["ticker", "date", "eventcodes"], filters=[("ticker", "in", pick)])
    ann_by = {
        tk: sorted({pd.Timestamp(d) for d, codes in zip(g["date"], g["eventcodes"]) if "22" in str(codes).split("|")})
        for tk, g in ev.groupby("ticker")
    }
    rows = new.loc[new["Ticker"].isin(pick), ["Date", "Ticker", *M]]
    rows = rows.sample(frac=1.0, random_state=1).groupby("Ticker").head(per_ticker)
    mism, n = [], 0
    for tk, g in rows.groupby("Ticker"):
        rq = _slow_reports(raw["ARQ"][raw["ARQ"]["ticker"] == tk], ann_by.get(tk, []), ["revenue"])
        rt = _slow_reports(raw["ART"][raw["ART"]["ticker"] == tk], ann_by.get(tk, []), ["revenue"])
        _slow_margins(rq)
        _slow_margins(rt)
        for r in g.itertuples(index=False):
            date = pd.Timestamp(r.Date)
            aq, _ = _slow_attach(rq, date, F.QUARTER_STALE_DAYS)
            at, _ = _slow_attach(rt, date, F.TTM_STALE_DAYS)
            want = {
                "gm_ttm": at["gm"] if at else np.nan,
                "om_ttm": at["om"] if at else np.nan,
                "gm_chg_q": aq["gm_chg"] if aq else np.nan,
                "om_chg_q": aq["om_chg"] if aq else np.nan,
            }
            n += 1
            bad = [c for c, v in want.items() if not same([getattr(r, c)], [v])[0]]
            if bad:
                mism.append((tk, date.date(), {c: (getattr(r, c), want[c]) for c in bad}))
    check(not mism, f"{n:,} sampled rows ({len(pick)} stocks) match the slow version exactly")
    for x in mism[:10]:
        print("     mismatch:", x)


# 6 --------------------------------------------------------------------------------------
def hand_checks(new: pd.DataFrame, q: pd.DataFrame) -> None:
    section("6. Hand checks")
    for tk, period, lo, hi in (("NVDA", "2016-10-30", "2016-10-01", "2016-12-10"), ("AAPL", "2016-09-24", "2016-10-01", "2016-11-20")):
        mine = q[(q["ticker"] == tk) & ((q["reportperiod"] - D(period)).abs() <= pd.Timedelta(days=7))]
        if mine.empty:
            check(False, f"{tk}: report for the quarter ending ~{period} found")
            continue
        r = mine.iloc[0]
        print(f"     {tk} quarter ending {period}: news {r['news_date'].date()} | gross margin {r['gm_q']:.1%} "
              f"(change {r['gm_chg_q']:+.1%} pts) | operating margin {r['om_q']:.1%} (change {r['om_chg_q']:+.1%} pts)")
        rows = new[(new["Ticker"] == tk) & new["Date"].between(D(lo), D(hi))]
        for x in rows.itertuples(index=False):
            print(f"       {x.Date.date()}  gm_ttm {x.gm_ttm:.3f}  gm_chg_q {x.gm_chg_q:+.4f}  om_ttm {x.om_ttm:.3f}  om_chg_q {x.om_chg_q:+.4f}")
        after = rows[rows["Date"] > r["news_date"]]
        before = rows[rows["Date"] <= r["news_date"]]
        check(
            len(after) and np.isclose(after["om_chg_q"].iloc[0], r["om_chg_q"], rtol=1e-5)
            and (before.empty or not np.isclose(before["om_chg_q"].iloc[-1], r["om_chg_q"], rtol=1e-5)),
            f"{tk}: new quarter appears on the first row after {r['news_date'].date()}, not before",
        )


# 7 --------------------------------------------------------------------------------------
def coverage_and_values(new: pd.DataFrame) -> None:
    section("7a. Coverage by year (share of rows) and value notes")
    x = new[["Date", *M]].assign(year=new["Date"].dt.year)
    by = x.groupby("year")[M].agg(lambda s: s.notna().mean())
    print("     year | " + " | ".join(M))
    for y, r in by.iterrows():
        print(f"     {y} | " + " | ".join(f"{r[c]:.0%}" for c in M))
    gm = new["gm_ttm"].dropna()
    print(f"     gross margin exactly 100% (no cost of revenue reported, e.g. banks): {np.mean(gm == 1.0):.1%} of rows with a value")
    print(f"     gross margin outside 0–100%: {np.mean((gm < 0) | (gm > 1)):.2%}; operating margin < −100%: {np.mean(new['om_ttm'].dropna() < -1):.2%}")
    print("     (A and B rank every input within each date, so extreme values only count as top / bottom ranks)")


def correlations(new: pd.DataFrame) -> None:
    section("7b. Correlations (per-date ranks, every 4th date)")
    dates = np.sort(new["Date"].unique())[::4]
    s = new[new["Date"].isin(dates)]
    old = [c for c in feature_columns(new) if c not in M]
    c = _day_ranks(s, [*M, *old]).corr()
    print("     " + " ".join(f"{x:>10s}" for x in M))
    for a in M:
        print(f"     {a:10s}" + " ".join(f"{c.loc[a, b]:+10.2f}" for b in M))
    print("     strongest link to an older input (price, size, growth):")
    for a in M:
        other = c.loc[a, old].abs().sort_values(ascending=False)
        print(f"       {a}: {other.index[0]} {c.loc[a, other.index[0]]:+.2f}")
    top = max(abs(c.loc[a, b]) for a in M for b in [*M, *old] if a != b)
    print(f"     highest correlation with a margin input {top:.2f} (prep drops one of a pair above 0.92)")


def leak_power(new: pd.DataFrame, q: pd.DataFrame, t: pd.DataFrame) -> None:
    section("7c. Leak-power test (dev rows only, label = 3-month return vs SPY)")
    calendar = pd.DatetimeIndex(benchmark_closeadj().index)
    dev = dev_rows(new, "3m", calendar)
    dev = dev[dev["Date"].dt.year >= 2005]
    keys = dev[["Date", "Ticker"]]
    fake = q.assign(news_date=q["reportperiod"] + pd.Timedelta(days=1))
    fake_t = t.assign(news_date=t["reportperiod"] + pd.Timedelta(days=1))
    leaky = F.margin_feature_frame(keys, fake, fake_t).rename(columns={c: f"{c}_leaky" for c in M})
    x = dev[["Date", "Ticker", *M, "excess_3m"]].merge(leaky, on=["Date", "Ticker"], validate="one_to_one")
    if len(x) != len(dev):
        raise RuntimeError("leak test lost rows in the merge")
    shuffled = F.shuffle_within_date(dev[["Date", "Ticker", *M]].reset_index(drop=True), M, 42)
    for c in M:
        x[f"{c}_placebo"] = shuffled[c].to_numpy()
    ics = {}
    for c in M:
        ics[c] = tuple(_mean_ic(x, col, "excess_3m") for col in (c, f"{c}_leaky", f"{c}_placebo"))
        real, bad, plc = ics[c]
        print(f"     {c}: rank IC with next-3-month return: real dates {real:+.4f} | fake early dates {bad:+.4f} | placebo {plc:+.4f}")
    real, bad, _ = ics["om_chg_q"]
    check(bad > real + 0.005, "om_chg_q: fake early dates give a clearly higher IC (so the test can catch a leak)")
    check(all(abs(v[2]) < 0.005 for v in ics.values()), "placebo has ~zero IC for all four")


def placebo_sanity(new: pd.DataFrame) -> None:
    section("7d. Placebo sanity")
    keep = [*F.GROWTH_FEATURES, "mom_252"]
    base = new[["Date", "Ticker", *M, *keep]]
    p = F.shuffle_within_date(base, M, 42)
    p2 = F.shuffle_within_date(base, M, 7)
    check(p[["Date", "Ticker", *keep]].equals(base[["Date", "Ticker", *keep]]), "growth and other columns untouched")
    key = ["Date", *M]
    srt = lambda d: d[key].sort_values(key, na_position="first").reset_index(drop=True)
    check(srt(p).equals(srt(base)), "each date keeps the same four-value blocks (only moved between stocks)")
    stay = (p[M].fillna(-9e9).to_numpy() == base[M].fillna(-9e9).to_numpy()).all(axis=1).mean()
    print(f"     rows whose block stayed identical: {stay:.2%}")
    check(stay < 0.05, "almost every stock gets another stock's block")
    check(not p[M].equals(p2[M]), "different seeds give different shuffles")
    rr = _day_ranks(pd.DataFrame({"Date": base["Date"], "a": base["om_chg_q"], "b": p["om_chg_q"]}), ["a", "b"]).corr().iloc[0, 1]
    print(f"     rank correlation real vs placebo om_chg_q: {rr:+.4f}")
    check(abs(rr) < 0.01, "placebo values unrelated to the real ones")


def main() -> int:
    synthetic_cases()
    old, new = pd.read_parquet(V9_PATH), pd.read_parquet(DATASET_PATH)
    dataset_structure(old, new)
    training_frames(old, new)
    del old
    q, t = F.quarterly_margin_reports(), F.ttm_margin_reports()
    real_date_rules(new, q, t)
    independent_recompute(new)
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
