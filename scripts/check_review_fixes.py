#!/usr/bin/env python3
"""
Checks for the 2026-10-21 code review fixes (docs/CODE_REVIEW_2026-10-21.md). No training.

1. Fills: a stock without a real traded close on the trade day can't be bought (even though the
   delisting-aware price panel has a value), but a holding may stay; the universe basket skips it.
2. Drawdown: the starting value counts as a peak; daily values inside a holding period count;
   costs come off at the period start; re-pricing costs re-prices the drawdown.
3. CLI: misspelled, malformed, empty or repeated options stop the run.
4. API key: request errors and HTTP errors never show the key (or its URL-encoded form).
5. Verdicts refuse runs scored with different backtests.
6. Real data (saved v9 baselines): without `tradeable` the new code reproduces the saved monthly
   returns exactly; with it, no new buy lacks a real price; daily drawdown ≥ the old sampled one.
7. RSI: no losses in 14 days → 100 (rising) or 50 (flat), short histories stay missing. The rebuilt
   dataset = the pre-fix backup plus exactly the rows the old RSI dropped (found independently from
   the price panels); every other value identical (top_* labels re-ranked without the new rows).

Usage: PYTHONPATH=.:scripts python scripts/check_review_fixes.py
Exits 1 if any check fails.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

import step3_verdict as v3
import train_walkforward as cli
from pinky import sharadar
from pinky.backtest import _daily_drawdown, _max_drawdown, run_backtest, summarize_backtest, with_cost
from pinky.config import BACKTEST_BUFFER_MULT, BACKTEST_MAX_SECTOR_SHARE, BACKTEST_TOP_FRAC, BACKTEST_TOP_N, BENCHMARK
from check_growth_features import without_rsi_fix_rows
from pinky.config import FEATURE_WARMUP_DAYS
from pinky.pit_dataset import DATASET_PATH, DATASET_SAMPLE_EVERY, DERIVED_DIR, _rsi
from pinky.train import ARTIFACTS_DIR, backtest_settings
from pinky.universe import backtest_prices, load_panel, sector_map, tradeable_panel

RESULTS: list[tuple[bool, str]] = []


def check(ok, name: str) -> None:
    RESULTS.append((bool(ok), name))
    print(f"{'PASS' if ok else 'FAIL'} - {name}")


def section(title: str) -> None:
    print(f"\n## {title}\n")


# 1 --------------------------------------------------------------------------------------
def _toy() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cal = pd.bdate_range("2020-01-01", "2020-04-30")
    prices = pd.DataFrame({"X": 10.0, "Y": 10.0, "Z": 10.0, BENCHMARK: 100.0}, index=cal)
    prices.loc["2020-02-04":, "X"] = 12.0  # X: last real trade Feb 3; panel keeps a synthetic value
    prices.loc["2020-02-10":, "X"] = 13.0
    traded = pd.DataFrame(True, index=cal, columns=prices.columns)
    traded.loc["2020-02-04":, "X"] = False
    signal = [pd.Timestamp("2020-01-02"), pd.Timestamp("2020-02-03"), pd.Timestamp("2020-03-02")]
    preds = pd.DataFrame(
        [(d, t, s) for d in signal for t, s in (("X", 3.0), ("Y", 2.0), ("Z", 1.0))],
        columns=["Date", "Ticker", "score"],
    )
    return prices, traded, preds


def fills() -> None:
    section("1. Fills need a real traded price on the trade day")
    prices, traded, preds = _toy()
    late = preds[preds["Date"] >= "2020-02-03"]  # X is first picked on Feb 3 → trade Feb 4 (no real price)
    old = run_backtest(late, "score", prices, top_n=1, cost_bps=0.0)
    new = run_backtest(late, "score", prices, top_n=1, cost_bps=0.0, tradeable=traded)
    check(old["picks"].iloc[0] == "X", "toy: without `tradeable` X is bought at its synthetic price (the old bug)")
    check(new["picks"].iloc[0] == "Y", "with `tradeable` the order goes to the next name (Y)")
    check(np.isclose(new["universe_ew"].iloc[0], 0.0), "universe basket skips X on its untraded day")
    held = run_backtest(preds, "score", prices, top_n=1, cost_bps=0.0, buffer_mult=3.0, tradeable=traded)
    check(held["picks"].tolist()[:2] == ["X", "X"], "a holding bought while it traded may be kept after its last trade")
    check(np.isclose(held["gross"].iloc[1], 13.0 / 12.0 - 1.0), "the kept holding follows the price panel (exit value)")
    check(old["universe_ew"].iloc[0] > 0, "toy: the old universe basket included X's synthetic gain")


# 2 --------------------------------------------------------------------------------------
def drawdowns() -> None:
    section("2. Drawdown")
    check(np.isclose(_max_drawdown(pd.Series([-0.20, 0.10])), -0.20), "sampled: a loss in the first period counts (−20%)")
    check(np.isclose(_daily_drawdown(pd.Series([(1.0, 0.5, 1.0)])), -0.50), "daily: a −50% dip that recovers in-period counts")
    check(np.isclose(_daily_drawdown(pd.Series([(1.0, 1.1), (1.0, 1.0)]), pd.Series([0.0, 0.10])), 1.1 * 0.9 / 1.1 - 1.0),
          "daily: a 10% cost at the second period's start is a 10% drop")
    cal = pd.bdate_range("2020-01-01", "2020-03-31")
    a = pd.Series(10.0, index=cal)
    a.loc["2020-01-15":"2020-01-20"] = 5.0  # crash and recovery inside January
    prices = pd.DataFrame({"A": a, BENCHMARK: 100.0}, index=cal)
    preds = pd.DataFrame({"Date": [cal[0], pd.Timestamp("2020-02-03")], "Ticker": "A", "score": 1.0})
    bt = run_backtest(preds, "score", prices, top_n=1)
    s = summarize_backtest(bt)
    check(np.isclose(s["max_dd_net"], 5.0 / 10.0 * (1 - 0.001) - 1.0, atol=1e-9),
          f"backtest: the in-month −50% shows (max DD {s['max_dd_net']:.2%}; old code: {_max_drawdown(bt['net']):.2%})")
    hi = summarize_backtest(with_cost(bt, 100.0))
    check(hi["max_dd_net"] < s["max_dd_net"], "re-pricing costs re-prices the drawdown")
    check(s["backtest_version"] == 2, "stats carry backtest_version 2")


# 3 --------------------------------------------------------------------------------------
def cli_flags() -> None:
    section("3. Command-line options")
    o = cli.parse_args(["--pit", "--with=ear", "--placebo=ear", "--seed=7", "--without=rank_label"])
    check(o["pit"] and o["with_"] == ["ear"] and o["placebo"] == "ear" and o["seed"] == 7 and o["without"] == ["rank_label"],
          "good options parse as before")
    check(cli.parse_args(["--pit", "--placebo"])["placebo"] == "growth", "bare --placebo = growth")
    for bad in (["--pit=true"], ["--pit", "--placebo="], ["--pit", "--with=ear", "--with=sue"], ["--pt"], ["--pit", "--placebo", "--placebo=ear"]):
        try:
            cli.parse_args(bad)
            stopped = False
        except SystemExit:
            stopped = True
        check(stopped, f"{' '.join(bad)} stops the run")


# 4 --------------------------------------------------------------------------------------
def api_key_scrub() -> None:
    section("4. API key never in error messages (fake key, no network)")
    fake = "FAKEkey/123+456=789"
    real_key, real_get = sharadar.api_key, requests.get
    encoded = requests.utils.quote(fake, safe="")
    try:
        sharadar.api_key = lambda: fake

        def boom(url, params=None, **kw):
            raise requests.ConnectionError(f"Max retries exceeded with url: {url}?api_key={encoded}&status=True")

        requests.get = boom
        for name, call in (("bulk_status", lambda: sharadar.bulk_status("tickers")), ("query", lambda: sharadar.query("tickers")),
                           ("download_bulk", lambda: sharadar.download_bulk("tickers", out_dir=Path(tempfile.mkdtemp())))):
            try:
                call()
                msg, ctx = "no error", False
            except RuntimeError as e:
                msg, ctx = str(e), e.__suppress_context__
            check(fake not in msg and encoded not in msg and ctx, f"{name}: connection error scrubbed, no chained traceback")

        def denied(url, params=None, **kw):
            r = requests.Response()
            r.status_code, r._content, r.url = 401, f"bad key {fake}".encode(), f"{url}?api_key={encoded}"
            r._content_consumed = True
            return r

        requests.get = denied
        try:
            sharadar.bulk_status("tickers")
            msg = "no error"
        except RuntimeError as e:
            msg = str(e)
        check("401" in msg and fake not in msg and encoded not in msg, "bulk_status: HTTP 401 scrubbed (was raise_for_status)")
    finally:
        sharadar.api_key, requests.get = real_key, real_get


# 5 --------------------------------------------------------------------------------------
def verdict_guard() -> None:
    section("5. Verdicts refuse mixed backtests")
    real_dir, real_out = v3.ARTIFACTS_DIR, list(v3.OUT)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        row = {"signal": v3.SIGNAL, "portfolio": v3.PORTFOLIO, "period": "all", "cagr_net": 0.07}
        settings = {k: v for k, v in backtest_settings().items() if k != "inputs"}
        for run, version in (("old", 1), ("new_a", 2), ("new_b", 2)):
            stats = pd.DataFrame([{**row, **({"backtest_version": version} if version > 1 else {})}])
            stats.to_csv(tmp / f"backtest_stats_1y_{run}.csv", index=False)
            cfg = {"version": "v9", **({"backtest": settings} if version > 1 else {})}
            (tmp / f"run_config_{run}.json").write_text(json.dumps(cfg))
        try:
            v3.ARTIFACTS_DIR = tmp
            check(v3.same_backtest(["new_a", "new_b"]), "two runs with the same backtest: OK")
            check(not v3.same_backtest(["old", "new_a"]), "old (version 1) vs new (version 2): refused")
        finally:
            v3.ARTIFACTS_DIR, v3.OUT[:] = real_dir, real_out


# 6 --------------------------------------------------------------------------------------
def real_data() -> None:
    section("6. Real data: saved v9 baselines, seed 42")
    prices, traded, raw, sectors = backtest_prices(), tradeable_panel(), load_panel("closeadj"), sector_map()
    ports = {"Top-10 + buffer": {"top_n": BACKTEST_TOP_N}, "Top 10% + buffer": {"top_frac": BACKTEST_TOP_FRAC}}
    for run in ("v9_pit", "v9_pit_no-rank_label"):
        preds = pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_1y_{run}.parquet")
        cfg = json.loads((ARTIFACTS_DIR / f"run_config_{run}.json").read_text())
        first = ARTIFACTS_DIR.parent / cfg["rescored"][0]["backup"] if cfg.get("rescored") else ARTIFACTS_DIR
        saved = pd.read_csv(first / f"backtest_periods_1y_{run}.csv")  # as first scored (backtest version 1)
        for port, kw in ports.items():
            kw = {**kw, "sectors": sectors, "max_sector_share": BACKTEST_MAX_SECTOR_SHARE, "buffer_mult": BACKTEST_BUFFER_MULT}
            old = run_backtest(preds, "pred_excess_lgbm", prices, **kw)
            new = run_backtest(preds, "pred_excess_lgbm", prices, tradeable=traded, **kw)
            s = saved[(saved["signal"] == "LightGBM") & (saved["portfolio"] == port)]
            check(len(s) == len(old) and np.allclose(old["net"].to_numpy(), s["net"].to_numpy(), rtol=0, atol=1e-12),
                  f"{run} {port}: without `tradeable` = the saved monthly returns")
            prev, bad = set(), 0
            for r in new.itertuples():
                picks = r.picks.split(",")
                bad += sum(t not in prev and (t not in raw.columns or pd.isna(raw.at[r.start, t])) for t in picks)
                prev = set(picks)
            check(bad == 0, f"{run} {port}: with `tradeable`, no new buy lacks a real price")
            a, b = summarize_backtest(old), summarize_backtest(new)
            sampled = _max_drawdown(new["net"])
            check(b["max_dd_net"] <= sampled + 1e-12, f"{run} {port}: daily DD {b['max_dd_net']:.2%} ≤ sampled {sampled:.2%}")
            print(f"     CAGR net {a['cagr_net']:+.2%} → {b['cagr_net']:+.2%} | universe {a['cagr_universe_ew']:+.2%} → "
                  f"{b['cagr_universe_ew']:+.2%} | SPY DD daily {b['max_dd_spy']:.2%}")


# 7 --------------------------------------------------------------------------------------
def _old_rsi(close: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    delta = close.diff()
    gain = delta.clip(lower=0.0).rolling(window).mean()
    loss = (-delta.clip(upper=0.0)).rolling(window).mean()
    return 100.0 - (100.0 / (1.0 + gain / loss.where(loss != 0.0)))


def rsi_fix() -> None:
    section("7. RSI fix")
    i = pd.bdate_range("2020-01-01", periods=40)
    toy = pd.DataFrame({"up": np.arange(40) + 10.0, "flat": 10.0, "down": 50.0 - np.arange(40),
                        "young": [np.nan] * 30 + list(range(10))}, index=i)
    last = _rsi(toy).iloc[-1]
    check(last["up"] == 100.0 and last["flat"] == 50.0 and last["down"] == 0.0 and np.isnan(last["young"]),
          "made-up: rising 100, flat 50, falling 0, < 14 days missing")
    check(np.isnan(_old_rsi(toy).iloc[-1]["up"]), "made-up: the old formula gave missing for a steady rise (the bug)")

    tr, univ, vol = load_panel("tr"), load_panel("universe"), load_panel("volume")
    pos = np.arange(FEATURE_WARMUP_DAYS, len(tr), DATASET_SAMPLE_EVERY)
    r, c = np.nonzero(univ.notna().to_numpy()[pos])
    rows = pos[r]
    ret = tr / tr.shift(1) - 1.0
    vm = vol.rolling(21).mean()
    ok = np.ones(len(rows), dtype=bool)
    for w in (ret, tr / tr.shift(5) - 1.0, tr / tr.shift(21) - 1.0, ret.rolling(21).std(), vol / vm.where(vm != 0.0)):
        ok &= np.isfinite(w.to_numpy(dtype="float64")[rows, c])
    dropped = ok & ~np.isfinite(_old_rsi(tr).to_numpy(dtype="float64")[rows, c])
    want = set(zip(tr.index[rows[dropped]], tr.columns[c[dropped]]))
    del tr, univ, vol, ret, vm

    old, new = pd.read_parquet(DERIVED_DIR / "pit_dataset_pre_rsi.parquet"), pd.read_parquet(DATASET_PATH)
    same_rows, problem = without_rsi_fix_rows(old, new)
    key = ["Date", "Ticker"]
    extra = new[key].merge(old[key], on=key, how="left", indicator=True).query("_merge == 'left_only'")
    got = set(zip(extra["Date"], extra["Ticker"]))
    check(problem is None and got == want, f"rows added = the {len(want)} rows the old RSI dropped (found from the price panels)")
    changed = [col for col in old.columns if not old[col].equals(same_rows[col])]
    check(list(same_rows.columns) == list(old.columns) and not changed,
          "every other row and value identical to the pre-fix backup" + (f" (changed: {changed})" if changed else ""))
    print(f"     rows {len(old):,} → {len(new):,}; stocks {old['Ticker'].nunique():,} → {new['Ticker'].nunique():,}")


def main() -> int:
    fills()
    drawdowns()
    cli_flags()
    api_key_scrub()
    verdict_guard()
    real_data()
    rsi_fix()
    failed = [n for ok, n in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    for n in failed:
        print(f"FAILED: {n}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
