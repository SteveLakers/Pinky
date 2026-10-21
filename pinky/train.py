"""
Walk-forward training + evaluation (LightGBM + Ridge baseline).

v2 prep:
- Cross-sectional z-score by day (stock ranking curve)
- Drop highly correlated features (fit on train only)
- Focus horizon: 1y (others optional)
- Smaller / more regularized LightGBM

v3: saves out-of-sample predictions and adds a tradeable cost-aware backtest to the report.
v4: Ridge/LightGBM rank blend + sector-capped portfolio backtest.
v5: `pit=True` runs on the Sharadar point-in-time universe (delisted stocks included,
    weekly rows, daily calendar for folds) and never touches the 2022+ holdout.
    Report adds precision@10 and winner capture.
v6: same models, new yardstick — a shorter last fold tests 2020 (COVID crash), holding
    buffer, top-50 / top-10% portfolios, precision@50 / @10%.
v7: four model fixes for pit runs (`MODEL_FIXES`; each can be switched off with `without`):
    return models learn each day's return rank, features are per-day percentile ranks,
    stocks younger than 1y are scored, and size (log market cap) is a feature.
v8: fifth fix `growth` = six company growth features (fundamentals.py). `placebo` shuffles
    them across stocks within each date (same values, no link to the stock); `seed` sets
    model randomness. Monthly portfolio returns are saved for paired run comparisons.
v9: `growth` is opt-in (`FEATURE_GROUPS`, switched on with `with_`), so a plain pit run is
    version A without growth (= v8_pit_no-growth). Every fold's models are saved under
    models/<run>/<horizon>/fold_NN/ (before: only the last fold, in a folder shared by versions).
    Batch 2 (same v9 defaults): `margins` group (four margin features); `placebo` names the group
    it shuffles (True = growth, as in v8), so growth can stay real while margins are shuffled.
    Growth round 2 (same v9 defaults): one group per new column (`ear`, `sue`, `cagr`, `steady`)
    and `growth2` = all four; groups that share columns can't be on together.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pinky.backtest import (
    between_years,
    default_prices,
    momentum_scores,
    pick_sector_share,
    run_backtest,
    summarize_backtest,
    top_winners,
    with_cost,
    within_sector_ic,
    yearly_table,
)
from pinky.config import (
    BACKTEST_BUFFER_MULT,
    BACKTEST_COST_BPS,
    BACKTEST_MAX_SECTOR_SHARE,
    BACKTEST_TOP_FRAC,
    BACKTEST_TOP_N,
    BACKTEST_WIDE_TOP_N,
    HOLDOUT_START,
    HORIZONS,
    PROJECT_ROOT,
    REPORT_SCORE_GROUPS,
    REPORT_SPLIT_YEAR,
    UNIVERSE_MIN_DOLLAR_VOLUME,
    UNIVERSE_MIN_PRICE,
    UNIVERSE_STOCKS,
)
from pinky.dataset import load_dataset
from pinky.fundamentals import GROUP_FEATURES, shuffle_within_date
from pinky.metrics import (
    acquired_share,
    brier_score,
    calibration_table,
    daily_rank_ic,
    precision_at_k,
    score_group_table,
    top_decile_hit_rate,
    top_n_basket_excess,
    universe_mean_excess,
    winner_capture,
)
from pinky.pit_dataset import DATASET_PATH, load_pit_dataset
from pinky.preprocess import cross_section_rank, prepare_fold_frames, ranking_feature_cols
from pinky.universe import acquisition_dates, backtest_prices, benchmark_closeadj, sector_map
from pinky.walkforward import WalkForwardFold, iter_walk_forward_folds

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODELS_DIR = PROJECT_ROOT / "models"

# Primary focus after v1 failure
DEFAULT_HORIZONS = ["1y"]
SPLIT_YEAR = REPORT_SPLIT_YEAR

VERSION = "v9"
MODEL_FIXES = ("rank_label", "rank_features", "young", "size")
# company data under test: off unless `with_` names it
FEATURE_GROUPS = ("growth", "margins", "ear", "sue", "cagr", "steady", "growth2")
ROUND2_GROUPS = ("ear", "sue", "cagr", "steady", "growth2")
DEFAULT_SEED = 42
PRED_COLS = [
    "pred_excess_ridge",
    "pred_excess_lgbm",
    "pred_excess_blend",
    "pred_beat_logit",
    "pred_beat_lgbm",
]


def _xy_return(df: pd.DataFrame, fcols: list[str], horizon: str, rank_label: bool = False):
    x = df[fcols].to_numpy(dtype=float)
    y = df[f"excess_{horizon}"]
    if rank_label:
        y = y.groupby(df["Date"]).rank(pct=True) - 0.5
    return x, y.to_numpy(dtype=float)


def _xy_beat(df: pd.DataFrame, fcols: list[str], horizon: str):
    x = df[fcols].to_numpy(dtype=float)
    y = df[f"beat_{horizon}"].to_numpy(dtype=float)
    return x, y


def _fit_return_models(x_train, y_train, seed: int = DEFAULT_SEED):
    # Ridge = simple baseline we must beat
    ridge = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=1.0, random_state=seed)),
        ]
    )
    ridge.fit(x_train, y_train)

    # Smaller, more regularized LightGBM (fix #5)
    # No row sampling: the old subsample=0.7 never took effect (LightGBM also needs
    # subsample_freq > 0), so every run through v8 trained on all rows. Turning it on is a
    # model change to test, not a fix.
    lgbm = lgb.LGBMRegressor(
        n_estimators=120,
        learning_rate=0.03,
        num_leaves=15,
        max_depth=4,
        min_child_samples=40,
        subsample=1.0,
        colsample_bytree=0.5,
        reg_lambda=5.0,
        reg_alpha=0.1,
        random_state=seed,
        verbosity=-1,
    )
    lgbm.fit(x_train, y_train)
    return ridge, lgbm


def _fit_beat_models(x_train, y_train, seed: int = DEFAULT_SEED):
    logit = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=500,
                    random_state=seed,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    logit.fit(x_train, y_train)

    lgbm = lgb.LGBMClassifier(
        n_estimators=120,
        learning_rate=0.03,
        num_leaves=15,
        max_depth=4,
        min_child_samples=40,
        subsample=1.0,  # no row sampling (see _fit_return_models)
        colsample_bytree=0.5,
        reg_lambda=5.0,
        reg_alpha=0.1,
        random_state=seed,
        verbosity=-1,
    )
    lgbm.fit(x_train, y_train)
    return logit, lgbm


def _eval_prepared(
    horizon: str,
    fold: WalkForwardFold,
    test: pd.DataFrame,
    fcols: list[str],
    ridge,
    lgbm_ret,
    logit,
    lgbm_beat,
    n_train: int,
) -> dict:
    x_test = test[fcols].to_numpy(dtype=float)
    test = test.copy()
    test["pred_excess_ridge"] = ridge.predict(x_test)
    test["pred_excess_lgbm"] = lgbm_ret.predict(x_test)
    # Models are on different scales: blend daily percentile ranks, not raw values.
    by_day = test.groupby("Date")
    test["pred_excess_blend"] = 0.5 * (
        by_day["pred_excess_ridge"].rank(pct=True) + by_day["pred_excess_lgbm"].rank(pct=True)
    )
    test["pred_beat_logit"] = logit.predict_proba(x_test)[:, 1]
    test["pred_beat_lgbm"] = lgbm_beat.predict_proba(x_test)[:, 1]

    excess_col = f"excess_{horizon}"
    beat_col = f"beat_{horizon}"

    row = {
        "fold_id": fold.fold_id,
        "horizon": horizon,
        "test_start": fold.test_start.date().isoformat(),
        "test_end": fold.test_end.date().isoformat(),
        "n_train": n_train,
        "n_test": len(test),
        "n_purged": fold.n_purged,
        "n_features": len(fcols),
        "beat_rate_test": float(test[beat_col].mean()),
        "ic_ridge": daily_rank_ic(test, "pred_excess_ridge", excess_col),
        "ic_lgbm": daily_rank_ic(test, "pred_excess_lgbm", excess_col),
        "ic_blend": daily_rank_ic(test, "pred_excess_blend", excess_col),
        "top_decile_hit_ridge": top_decile_hit_rate(test, "pred_excess_ridge", beat_col),
        "top_decile_hit_lgbm": top_decile_hit_rate(test, "pred_excess_lgbm", beat_col),
        "top5_excess_ridge": top_n_basket_excess(test, "pred_excess_ridge", excess_col, n=5),
        "top5_excess_lgbm": top_n_basket_excess(test, "pred_excess_lgbm", excess_col, n=5),
        "top5_excess_blend": top_n_basket_excess(test, "pred_excess_blend", excess_col, n=5),
        "universe_mean_excess": universe_mean_excess(test, excess_col),
        "brier_logit": brier_score(test[beat_col].to_numpy(), test["pred_beat_logit"].to_numpy()),
        "brier_lgbm": brier_score(test[beat_col].to_numpy(), test["pred_beat_lgbm"].to_numpy()),
    }
    row["ic_lgbm_beats_ridge"] = (
        row["ic_lgbm"] > row["ic_ridge"]
        if not (np.isnan(row["ic_lgbm"]) or np.isnan(row["ic_ridge"]))
        else False
    )
    row["top5_lgbm_beats_ridge"] = (
        row["top5_excess_lgbm"] > row["top5_excess_ridge"]
        if not (np.isnan(row["top5_excess_lgbm"]) or np.isnan(row["top5_excess_ridge"]))
        else False
    )
    extra = [c for c in (f"stock_fwd_{horizon}", f"top_{horizon}") if c in test.columns]
    preds = test[["Date", "Ticker", excess_col, beat_col, *extra, *PRED_COLS]].assign(
        fold_id=fold.fold_id
    )
    return row, preds


def dev_rows(df: pd.DataFrame, horizon: str, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    """Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen."""
    pos = calendar.searchsorted(pd.Timestamp(HOLDOUT_START))
    cutoff = calendar[pos - HORIZONS[horizon]]
    return df[df["Date"] < cutoff]


def run_horizon(
    df: pd.DataFrame,
    horizon: str,
    calendar: pd.DatetimeIndex | None = None,
    rank_label: bool = False,
    zscore: bool = True,
    seed: int = DEFAULT_SEED,
) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Train/eval all folds for one horizon with CS prep + tuned LightGBM.

    Returns fold metrics, models (`folds`: every fold's fitted models, feature columns and
    dates; `test_cs`: the last fold's prepared test rows) and out-of-sample predictions.
    """
    rows = []
    pred_parts = []
    folds = []
    test_cs = None

    for fold in iter_walk_forward_folds(df, horizon, calendar=calendar):
        train_cs, test_cs, fcols = prepare_fold_frames(fold.train, fold.test, zscore=zscore)
        x_tr, y_tr = _xy_return(train_cs, fcols, horizon, rank_label=rank_label)
        x_tb, y_tb = _xy_beat(train_cs, fcols, horizon)

        ridge, lgbm_ret = _fit_return_models(x_tr, y_tr, seed)
        logit, lgbm_beat = _fit_beat_models(x_tb, y_tb, seed)

        metrics, preds = _eval_prepared(
            horizon,
            fold,
            test_cs,
            fcols,
            ridge,
            lgbm_ret,
            logit,
            lgbm_beat,
            n_train=len(train_cs),
        )
        rows.append(metrics)
        pred_parts.append(preds)
        folds.append(
            {
                "fold_id": fold.fold_id,
                "train_start": fold.train_start,
                "train_end": fold.train_end,
                "test_start": fold.test_start,
                "test_end": fold.test_end,
                "feature_cols": fcols,
                "ridge": ridge,
                "lgbm_return": lgbm_ret,
                "logit": logit,
                "lgbm_beat": lgbm_beat,
            }
        )
        print(
            f"[{horizon}] fold {fold.fold_id}: "
            f"feats={len(fcols)} | "
            f"IC lgbm={metrics['ic_lgbm']:.3f} ridge={metrics['ic_ridge']:.3f} "
            f"blend={metrics['ic_blend']:.3f} | "
            f"top5 lgbm={metrics['top5_excess_lgbm']:.3f} "
            f"ridge={metrics['top5_excess_ridge']:.3f} "
            f"blend={metrics['top5_excess_blend']:.3f} "
            f"univ={metrics['universe_mean_excess']:.3f}"
        )

    models = {"folds": folds, "test_cs": test_cs}
    return pd.DataFrame(rows), models, pd.concat(pred_parts, ignore_index=True)


def save_models(models_by_h: dict, run_name: str) -> Path:
    """Every fold's models → models/<run>/<horizon>/fold_NN/, plus folds.json (fold dates)."""
    root = MODELS_DIR / run_name
    dates = ("train_start", "train_end", "test_start", "test_end")
    for h, pack in models_by_h.items():
        out = root / h
        for m in pack["folds"]:
            d = out / f"fold_{m['fold_id']:02d}"
            d.mkdir(parents=True, exist_ok=True)
            joblib.dump(m["lgbm_return"], d / "lgbm_return.joblib")
            joblib.dump(m["lgbm_beat"], d / "lgbm_beat.joblib")
            joblib.dump(m["ridge"], d / "ridge_return.joblib")
            joblib.dump(m["logit"], d / "logit_beat.joblib")
            (d / "feature_cols.txt").write_text("\n".join(m["feature_cols"]))
        table = [
            {"fold_id": m["fold_id"], **{k: m[k].date().isoformat() for k in dates}}
            for m in pack["folds"]
        ]
        (out / "folds.json").write_text(json.dumps(table, indent=1))
    return root


def _fmt_pct(x: float) -> str:
    return f"{100 * x:+.1f}%"


def _ranking_lines(
    horizon: str,
    preds: pd.DataFrame,
    mom: pd.DataFrame,
    acq: pd.Series | None = None,
) -> list[str]:
    """Does the model find the future top decile / the year's biggest winners?"""
    top_col, fwd_col = f"top_{horizon}", f"stock_fwd_{horizon}"
    if top_col not in preds or fwd_col not in preds:
        return []
    k, wide_k, frac, n_win = BACKTEST_TOP_N, BACKTEST_WIDE_TOP_N, BACKTEST_TOP_FRAC, 20
    mom = mom.merge(preds[["Date", "Ticker", top_col, fwd_col]], on=["Date", "Ticker"])
    avg_n = preds.groupby("Date").size().mean()
    acq_head = f" Acquired ≤ 6m, top-{k} | Acquired ≤ 6m, top {frac:.0%} |" if acq is not None else ""
    lines = [
        f"## Finding winners `{horizon}` (out-of-sample, monthly)",
        "",
        "- **Precision**: share of the top picks that land in the future top 10% "
        f"(top-{k}, top-{wide_k}, and the top {frac:.0%} of each date's stocks).",
        f"- **Winner capture**: each year's {n_win} biggest winners — share of months each "
        f"sat in the monthly top-{k}.",
        *(
            [
                "- **Acquired ≤ 6m**: share of top picks whose company is bought out within "
                "6 months (takeover targets trade calm and steady; they are not future winners)."
            ]
            if acq is not None
            else []
        ),
        "",
        f"| Signal | Precision@{k} | Precision@{wide_k} | Precision@{frac:.0%} | Winner capture |"
        + acq_head,
        "|---|---|---|---|---|" + ("---|---|" if acq is not None else ""),
    ]
    for name, frame, col in [
        ("LightGBM", preds, "pred_excess_lgbm"),
        ("Ridge", preds, "pred_excess_ridge"),
        ("Blend", preds, "pred_excess_blend"),
        ("Momentum 12-1 (naive)", mom, "mom_12_1"),
    ]:
        p = precision_at_k(frame, col, top_col, k=k)
        p_wide = precision_at_k(frame, col, top_col, k=wide_k)
        p_frac = precision_at_k(frame, col, top_col, frac=frac)
        w = winner_capture(frame, col, fwd_col, k=k, n_winners=n_win)
        row = f"| {name} | {p:.3f} | {p_wide:.3f} | {p_frac:.3f} | {w:.3f} |"
        if acq is not None:
            a_k = acquired_share(frame, col, acq, k=k)
            a_frac = acquired_share(frame, col, acq, frac=frac)
            row += f" {a_k:.1%} | {a_frac:.1%} |"
        lines.append(row)
    random_row = f"| Random (expected) | 0.100 | 0.100 | 0.100 | {k / avg_n:.3f} |"
    if acq is not None:
        base = acquired_share(preds, "pred_excess_ridge", acq, frac=1.0)
        random_row += f" {base:.1%} | {base:.1%} |"
    lines += [
        random_row,
        "",
        f"Average stocks to choose from per date: {avg_n:,.0f}.",
        "",
    ]
    return lines


def _score_group_lines(
    horizon: str,
    preds: pd.DataFrame,
    mom: pd.DataFrame,
) -> tuple[list[str], pd.DataFrame]:
    """Where the ranking skill sits: what each score group did next."""
    excess_col = f"excess_{horizon}"
    if excess_col not in preds:
        return [], pd.DataFrame()
    n_groups, k = REPORT_SCORE_GROUPS, BACKTEST_TOP_N
    mom = mom.merge(preds[["Date", "Ticker", excess_col]], on=["Date", "Ticker"])
    signals = {
        "LightGBM": (preds, "pred_excess_lgbm"),
        "Ridge": (preds, "pred_excess_ridge"),
        "Blend": (preds, "pred_excess_blend"),
        "Momentum 12-1": (mom, "mom_12_1"),
    }
    tables = {
        sig: score_group_table(frame, col, excess_col, n_groups=n_groups, top_n=k)
        for sig, (frame, col) in signals.items()
    }
    lines = [
        f"## Where the ranking skill sits `{horizon}` (out-of-sample, every date)",
        "",
        f"- Each date's stocks are split into {n_groups} equal groups by score "
        f"(1 = lowest, {n_groups} = highest), plus the top-{k} names; averaged over dates.",
        "- Rank IC grades the whole list. A buy-only portfolio gets only the top, so skill "
        "at the bottom (spotting losers) doesn't help it.",
        "- **Median** = the typical stock; **mean** is pulled up by a few big winners.",
        "",
    ]
    for title, col, fmt in [
        (f"Share beating SPY over the next `{horizon}`", "beat_spy", lambda x: f"{100 * x:.1f}%"),
        (f"Median `{horizon}` excess vs SPY", "median_excess", _fmt_pct),
        (f"Mean `{horizon}` excess vs SPY", "mean_excess", _fmt_pct),
    ]:
        lines += [
            f"### {title}",
            "",
            "| Score group | " + " | ".join(signals) + " |",
            "|---|" + "---|" * len(signals),
        ]
        for row in tables["LightGBM"].index:
            cells = [fmt(tables[sig][col].get(row, np.nan)) for sig in signals]
            lines.append(f"| {row} | " + " | ".join(cells) + " |")
        lines.append("")
    table = pd.concat(tables, names=["signal", "group"]).reset_index()
    return lines, table


def _backtest_lines(
    horizon: str,
    preds: pd.DataFrame,
    prices: pd.DataFrame,
    sectors: dict[str, str] | None = None,
    mom: pd.DataFrame | None = None,
) -> tuple[list[str], pd.DataFrame]:
    """Report lines + one stats row per (signal, portfolio)."""
    excess_col = f"excess_{horizon}"
    n, wide_n, frac = BACKTEST_TOP_N, BACKTEST_WIDE_TOP_N, BACKTEST_TOP_FRAC
    cap, buf, bps_hi = BACKTEST_MAX_SECTOR_SHARE, BACKTEST_BUFFER_MULT, 25.0
    mom = mom if mom is not None else momentum_scores(preds, prices)
    signals = {
        "LightGBM": (preds, "pred_excess_lgbm"),
        "Ridge": (preds, "pred_excess_ridge"),
        "Blend": (preds, "pred_excess_blend"),
        "Momentum 12-1": (mom, "mom_12_1"),
    }
    capped = {"max_sector_share": cap}
    buffered = {"max_sector_share": cap, "buffer_mult": buf}
    main = f"Top-{n} + buffer"
    portfolios = {
        f"Top-{n} (v5 rules)": {"top_n": n},
        f"Top-{n}": {"top_n": n, **capped},
        main: {"top_n": n, **buffered},
        f"Top-{wide_n}": {"top_n": wide_n, **capped},
        f"Top-{wide_n} + buffer": {"top_n": wide_n, **buffered},
        f"Top {frac:.0%}": {"top_frac": frac, **capped},
        f"Top {frac:.0%} + buffer": {"top_frac": frac, **buffered},
    }
    bts = {
        (sig, port): run_backtest(frame, col, prices, sectors=sectors, **kw)
        for sig, (frame, col) in signals.items()
        for port, kw in portfolios.items()
    }
    stats = {key: summarize_backtest(bt) for key, bt in bts.items()}
    stats_hi = {key: summarize_backtest(with_cost(bt, bps_hi)) for key, bt in bts.items()}

    ref = stats[("Ridge", main)]
    lines = [
        f"## Portfolio backtest `{horizon}` signal (out-of-sample, tradeable)",
        "",
        f"- Monthly rebalance, equal weight, cost **{BACKTEST_COST_BPS:.0f} bps per side** on "
        f"real turnover; the {bps_hi:.0f} bps figure re-prices the same trades.",
        f"- Signal is the `{horizon}` forecast, re-ranked monthly.",
        f"- Sector cap: no sector above {cap:.0%} of picks (all rows except *v5 rules*).",
        f"- **Buffer**: a holding is kept while it ranks in the top {buf:g}× N "
        f"(top-{n} → top {buf * n:.0f}).",
        f"- **Top {frac:.0%}**: the top {frac:.0%} of each date's stocks "
        "(size follows the universe).",
        "- **Blend** = average of daily Ridge and LightGBM percentile ranks.",
        "",
        f"Window: {ref['start']} → {ref['end']} ({ref['months']} months). "
        "Trades fill at next day's close.",
        f"Same window — SPY: CAGR {_fmt_pct(ref['cagr_spy'])}, max DD "
        f"{_fmt_pct(ref['max_dd_spy'])}. Equal-weight universe: CAGR "
        f"{_fmt_pct(ref['cagr_universe_ew'])}.",
        "",
    ]
    header = "| Portfolio | " + " | ".join(signals) + " |"
    rule = "|---|" + "---|" * len(signals)
    tables = [
        (
            f"CAGR net of {BACKTEST_COST_BPS:.0f} bps ({bps_hi:.0f} bps in brackets)",
            lambda k: f"{_fmt_pct(stats[k]['cagr_net'])} ({_fmt_pct(stats_hi[k]['cagr_net'])})",
        ),
        ("Months beating SPY", lambda k: f"{100 * stats[k]['months_beat_spy']:.0f}%"),
        (
            "Turnover per month (buys + sells)",
            lambda k: f"{100 * stats[k]['avg_monthly_turnover']:.0f}%",
        ),
        ("Max drawdown", lambda k: _fmt_pct(stats[k]["max_dd_net"])),
    ]
    for title, cell in tables:
        lines += [f"### {title}", "", header, rule]
        for port in portfolios:
            lines.append(f"| {port} | " + " | ".join(cell((sig, port)) for sig in signals) + " |")
        lines.append("")

    split_rows = []
    lines += [
        f"### Before and after {SPLIT_YEAR} (net of {BACKTEST_COST_BPS:.0f} bps)",
        "",
        "| Portfolio | Years | " + " | ".join(signals) + " | SPY | Univ EW |",
        "|---|---|" + "---|" * (len(signals) + 2),
    ]
    for port in [main, f"Top {frac:.0%} + buffer"]:
        for first, last in [(None, SPLIT_YEAR - 1), (SPLIT_YEAR, None)]:
            sub = {sig: between_years(bts[(sig, port)], first, last) for sig in signals}
            years = sub["Ridge"]["start"].dt.year
            label = f"{years.min()}–{years.max()}"
            part = {sig: summarize_backtest(b) for sig, b in sub.items()}
            ridge = part["Ridge"]
            lines.append(
                f"| {port} | {label} | "
                + " | ".join(_fmt_pct(part[sig]["cagr_net"]) for sig in signals)
                + f" | {_fmt_pct(ridge['cagr_spy'])} | {_fmt_pct(ridge['cagr_universe_ew'])} |"
            )
            split_rows += [
                {
                    "signal": sig,
                    "portfolio": port,
                    "period": label,
                    **part[sig],
                    f"cagr_net_{bps_hi:.0f}bps": summarize_backtest(with_cost(b, bps_hi))["cagr_net"],
                }
                for sig, b in sub.items()
            ]
    lines.append("")

    winners = set(top_winners(prices, preds["Date"].min(), preds["Date"].max()))
    lines += [
        f"### {main} without the window's top-5 winners (hindsight stress test)",
        "",
        f"Removed: {', '.join(sorted(winners))}.",
        "",
        "| Signal | CAGR net | CAGR net, winners removed |",
        "|---|---|---|",
    ]
    for sig, (frame, col) in signals.items():
        bt = run_backtest(
            frame, col, prices, exclude=winners, sectors=sectors, **portfolios[main]
        )
        lines.append(
            f"| {sig} | {_fmt_pct(stats[(sig, main)]['cagr_net'])} | "
            f"{_fmt_pct(summarize_backtest(bt)['cagr_net'])} |"
        )
    lines.append("")

    for sig in ["Ridge", "LightGBM"]:
        yt = yearly_table(bts[(sig, main)])
        lines += [
            f"### {sig}, {main}, by year (net of {BACKTEST_COST_BPS:.0f} bps)",
            "",
            "| Year | Net | SPY | Univ EW | Net − SPY |",
            "|---|---|---|---|---|",
        ]
        for year, r in yt.iterrows():
            lines.append(
                f"| {year} | {_fmt_pct(r['net'])} | {_fmt_pct(r['spy'])} | "
                f"{_fmt_pct(r['universe_ew'])} | {_fmt_pct(r['net_minus_spy'])} |"
            )
        lines.append("")

    for sig in ["Ridge", "LightGBM"]:
        share = pick_sector_share(bts[(sig, main)], sectors)
        lines += [f"### {sig}, {main}: average pick share by sector", ""]
        lines += [f"- {sec}: {100 * v:.0f}%" for sec, v in share.items()]
        lines.append("")

    for name, col in [
        ("LightGBM", "pred_excess_lgbm"),
        ("Ridge", "pred_excess_ridge"),
        ("Blend", "pred_excess_blend"),
    ]:
        wic = within_sector_ic(preds, col, excess_col, sectors)
        lines += [f"### {name} rank IC inside each sector (`{horizon}`)", ""]
        lines += [f"- {sec}: {v:.3f}" for sec, v in wic.items()]
        lines.append("")

    table = pd.DataFrame(
        [
            {
                "signal": sig,
                "portfolio": port,
                "period": "all",
                **stats[(sig, port)],
                f"cagr_net_{bps_hi:.0f}bps": stats_hi[(sig, port)]["cagr_net"],
            }
            for sig, port in bts
        ]
        + split_rows
    )
    periods = pd.concat(
        [bt.drop(columns="picks").assign(signal=sig, portfolio=port) for (sig, port), bt in bts.items()],
        ignore_index=True,
    )
    return lines, table, periods


def _write_summary(
    all_metrics: pd.DataFrame,
    path: Path,
    preds_by_h: dict[str, pd.DataFrame] | None = None,
    exclude: list[str] | None = None,
    run_name: str = VERSION,
    universe_desc: str | None = None,
    prices: pd.DataFrame | None = None,
    sectors: dict[str, str] | None = None,
    acq: pd.Series | None = None,
    fixes: list[str] | None = None,
    placebo: bool | str | None = None,
    seed: int = DEFAULT_SEED,
) -> None:
    exclude = exclude or []
    if universe_desc is None:
        n_stocks = len(set(UNIVERSE_STOCKS) - set(exclude))
        universe_desc = f"{n_stocks} stocks, sector-balanced (Tech/AI ~25%)."
    lines = [
        f"# Pinky Walk-Forward Training Report ({run_name})",
        "",
        f"Universe: {universe_desc}",
        *([f"Removed from universe (train + test): {', '.join(exclude)}."] if exclude else []),
        _prep_desc(fixes or [], placebo, seed),
        "Validation: expanding walk-forward + label purge (no random splits).",
        "Baseline to beat: **Ridge**.",
        "",
    ]
    for horizon in list(HORIZONS):
        m = all_metrics[all_metrics["horizon"] == horizon]
        if m.empty:
            continue
        ic_lgbm = m["ic_lgbm"].mean()
        ic_ridge = m["ic_ridge"].mean()
        ic_blend = m["ic_blend"].mean()
        top5_lgbm = m["top5_excess_lgbm"].mean()
        top5_ridge = m["top5_excess_ridge"].mean()
        top5_blend = m["top5_excess_blend"].mean()
        univ = m["universe_mean_excess"].mean()
        beat_ic = m["ic_lgbm_beats_ridge"].mean()
        beat_top = m["top5_lgbm_beats_ridge"].mean()

        pass_ic = ic_lgbm > ic_ridge
        pass_top = top5_lgbm > top5_ridge
        soft = "PASS" if pass_ic and pass_top else "FAIL / MIXED"

        lines += [
            f"## Horizon `{horizon}` ({len(m)} folds)",
            "",
            f"- Mean rank IC — LightGBM: **{ic_lgbm:.3f}** | Ridge: **{ic_ridge:.3f}** "
            f"| Blend: **{ic_blend:.3f}**",
            f"- LightGBM beats Ridge on IC in **{100 * beat_ic:.0f}%** of folds",
            f"- Mean top-5 excess — LightGBM: **{top5_lgbm:.3f}** | Ridge: **{top5_ridge:.3f}** "
            f"| Blend: **{top5_blend:.3f}** | Universe: **{univ:.3f}**",
            f"- LightGBM beats Ridge on top-5 in **{100 * beat_top:.0f}%** of folds",
            f"- Avg features used: **{m['n_features'].mean():.1f}**",
            f"- Mean test beat rate: **{100 * m['beat_rate_test'].mean():.0f}%**",
            f"**Soft bar vs Ridge:** **{soft}**",
            "",
        ]

    if preds_by_h:
        prices = prices if prices is not None else default_prices()
        prices = prices.drop(columns=exclude, errors="ignore")
        for horizon, preds in preds_by_h.items():
            mom = momentum_scores(preds, prices)
            lines += _ranking_lines(horizon, preds, mom, acq)
            group_lines, groups = _score_group_lines(horizon, preds, mom)
            lines += group_lines
            if not groups.empty:
                groups.to_csv(path.parent / f"score_groups_{horizon}_{run_name}.csv", index=False)
            bt_lines, bt_table, bt_periods = _backtest_lines(horizon, preds, prices, sectors, mom)
            lines += bt_lines
            bt_table.to_csv(path.parent / f"backtest_stats_{horizon}_{run_name}.csv", index=False)
            bt_periods.to_csv(path.parent / f"backtest_periods_{horizon}_{run_name}.csv", index=False)

    path.write_text("\n".join(lines))


def placebo_group(placebo: bool | str | None) -> str | None:
    """The feature group a run shuffles: True (v8 / early v9 configs) = growth; False / None = none."""
    return "growth" if placebo is True else (placebo or None)


def _prep_desc(fixes: list[str], placebo: bool | str | None = None, seed: int = DEFAULT_SEED) -> str:
    placebo = placebo_group(placebo)
    parts = [
        "per-day percentile-rank features" if "rank_features" in fixes else "per-day z-score features",
        "target = each day's return rank" if "rank_label" in fixes else "target = raw excess return",
        "stocks < 1y old scored" if "young" in fixes else "stocks need 1y of history",
        "size feature (log market cap)" if "size" in fixes else "no size feature",
        "company growth features" if "growth" in fixes else "no growth features",
        *(["margin features"] if "margins" in fixes else []),
        *[f"growth round 2: {', '.join(GROUP_FEATURES[g])}" for g in ROUND2_GROUPS if g in fixes],
    ]
    desc = "Prep: " + ", ".join(parts) + " + correlated-feature drop + regularized LightGBM."
    if placebo:
        desc += f" **Placebo: {placebo} values shuffled across stocks within each date.**"
    if seed != DEFAULT_SEED:
        desc += f" Model seed {seed}."
    return desc


def _pit_universe_desc(n_stocks: int) -> str:
    return (
        f"point-in-time liquid US stocks (price ≥ ${UNIVERSE_MIN_PRICE:.0f}, "
        f"≥ ${UNIVERSE_MIN_DOLLAR_VOLUME / 1e6:.0f}M/day traded), delisted stocks included, "
        f"{n_stocks:,} distinct stocks. Rows sampled weekly. "
        f"Dev only: labels end before {HOLDOUT_START} (holdout untouched)."
    )


def rewrite_summary(run_name: str, horizons: list[str] | None = None) -> Path:
    """Rebuild a pit run's report from its saved metrics + predictions (no retraining)."""
    horizons = horizons or list(DEFAULT_HORIZONS)
    metrics = pd.read_csv(ARTIFACTS_DIR / f"walkforward_metrics_{run_name}.csv")
    preds_by_h = {
        h: pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_{h}_{run_name}.parquet") for h in horizons
    }
    config_path = ARTIFACTS_DIR / f"run_config_{run_name}.json"
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    n_stocks = config.get("n_stocks") or pd.read_parquet(DATASET_PATH, columns=["Ticker"])["Ticker"].nunique()
    path = ARTIFACTS_DIR / f"walkforward_summary_{run_name}.md"
    _write_summary(
        metrics,
        path,
        preds_by_h,
        run_name=run_name,
        universe_desc=_pit_universe_desc(n_stocks),
        prices=backtest_prices(),
        sectors=sector_map(),
        acq=acquisition_dates(),
        fixes=config.get("fixes", []),
        placebo=config.get("placebo", False),
        seed=config.get("seed", DEFAULT_SEED),
    )
    print(f"Wrote {path}")
    return path


def pit_training_frame(
    df: pd.DataFrame,
    fixes: list[str],
    placebo: bool | str | None = None,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """Pit dataset → model frame for the given fixes (placebo shuffle before ranking)."""
    placebo = placebo_group(placebo)
    for g in FEATURE_GROUPS:
        missing = [c for c in GROUP_FEATURES[g] if c not in df.columns]
        if g in fixes and missing:
            raise ValueError(f"{g} is on but the dataset lacks {missing}; rebuild: python -m pinky.pit_dataset")
    if placebo and placebo not in fixes:
        raise ValueError(f"placebo shuffles {placebo}, which is off")
    if "young" not in fixes:
        df = df[df["history_1y"] >= 1.0].drop(columns="history_1y")
    if "size" not in fixes:
        df = df.drop(columns="log_mcap")
    on = {c for g in FEATURE_GROUPS if g in fixes for c in GROUP_FEATURES[g]}
    off = [c for g in FEATURE_GROUPS if g not in fixes for c in GROUP_FEATURES[g] if c not in on]
    df = df.drop(columns=list(dict.fromkeys(off)), errors="ignore")
    if placebo:
        df = shuffle_within_date(df, GROUP_FEATURES[placebo], seed)
    if "rank_features" in fixes:
        df = cross_section_rank(df, ranking_feature_cols(df))
    return df.reset_index(drop=True)


def pit_tag(
    tag: str = "",
    without: list[str] | None = None,
    with_: list[str] | None = None,
    placebo: bool | str | None = None,
    seed: int = DEFAULT_SEED,
) -> str:
    """Output tag of a pit run, built from its options (run name = `<VERSION>_<tag>`).

    A growth placebo keeps v8's tag `placebo`; other groups get `placebo-<group>`.
    """
    placebo = placebo_group(placebo)
    return "_".join(
        [
            "pit",
            *([tag] if tag else []),
            *[f"no-{f}" for f in without or []],
            *[f"with-{g}" for g in FEATURE_GROUPS if g in (with_ or [])],
            *([("placebo" if placebo == "growth" else f"placebo-{placebo}")] if placebo else []),
            *([f"s{seed}"] if seed != DEFAULT_SEED else []),
        ]
    )


def run_all(
    horizons: list[str] | None = None,
    save: bool = True,
    exclude: list[str] | None = None,
    tag: str = "",
    pit: bool = False,
    without: list[str] | None = None,
    with_: list[str] | None = None,
    placebo: bool | str | None = None,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """Run walk-forward training. Default focus: 1y.

    `exclude` drops tickers from train and test; `tag` keeps that run's outputs separate.
    `pit` uses the Sharadar point-in-time universe and only dev rows (holdout untouched).
    Pit runs use all `MODEL_FIXES` except those in `without` (tagged `no-<fix>`), plus the
    `FEATURE_GROUPS` named in `with_` (tagged `with-<group>`). Legacy runs use none of them.
    `placebo` names one group that is on (True = growth) and shuffles its features within each
    date (tagged `placebo` for growth, `placebo-<group>` otherwise); `seed` sets model
    randomness (tagged `s<seed>` unless the default).
    """
    horizons = horizons or list(DEFAULT_HORIZONS)
    exclude = exclude or []
    without = without or []
    with_ = with_ or []
    placebo = placebo_group(placebo)
    unknown = sorted(set(without) - set(MODEL_FIXES)) + sorted(set(with_) - set(FEATURE_GROUPS))
    if unknown:
        raise ValueError(
            f"Unknown options {unknown}; without takes some of {list(MODEL_FIXES)}, "
            f"with takes some of {list(FEATURE_GROUPS)}"
        )
    fixes = (
        [f for f in MODEL_FIXES if f not in without] + [g for g in FEATURE_GROUPS if g in with_]
        if pit
        else []
    )
    if (placebo or seed != DEFAULT_SEED or with_) and not pit:
        raise ValueError("with, placebo and seed options are for pit runs")
    if placebo and placebo not in fixes:
        raise ValueError(f"placebo={placebo} needs that group on (with {placebo}); groups: {list(FEATURE_GROUPS)}")
    cols = [c for g in with_ for c in GROUP_FEATURES[g]]
    if len(cols) != len(set(cols)):
        raise ValueError(f"with={with_}: these groups share columns; turn on only one of them")
    calendar = prices = sectors = universe_desc = acq = None
    if pit:
        tag = pit_tag(tag, without, with_, placebo, seed)
        df = pit_training_frame(load_pit_dataset(), fixes, placebo, seed)
        calendar = pd.DatetimeIndex(benchmark_closeadj().index)
        prices = backtest_prices()
        sectors = sector_map()
        acq = acquisition_dates()
    else:
        df = load_dataset()
    run_name = f"{VERSION}_{tag}" if tag else VERSION
    if exclude:
        df = df[~df["Ticker"].isin(exclude)].reset_index(drop=True)
        print(f"[universe] removed {exclude} → {df['Ticker'].nunique()} stocks")
    if pit:
        universe_desc = _pit_universe_desc(df["Ticker"].nunique())
        off = [f for f in (*MODEL_FIXES, *FEATURE_GROUPS) if f not in fixes]
        print(f"[fixes] on: {fixes or 'none'} | off: {off or 'none'}")
        print(f"[seed] {seed} | placebo: {f'{placebo} shuffled within each date' if placebo else 'off'}")
    parts = []
    models_by_h = {}
    preds_by_h = {}

    for h in horizons:
        print(f"\n=== Training horizon {h} ({run_name}) ===")
        df_h = dev_rows(df, h, calendar) if pit else df
        metrics, models, preds = run_horizon(
            df_h,
            h,
            calendar=calendar,
            rank_label="rank_label" in fixes,
            zscore="rank_features" not in fixes,
            seed=seed,
        )
        parts.append(metrics)
        models_by_h[h] = models
        preds_by_h[h] = preds

    all_metrics = pd.concat(parts, ignore_index=True)

    if save:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        metrics_path = ARTIFACTS_DIR / f"walkforward_metrics_{run_name}.csv"
        all_metrics.to_csv(metrics_path, index=False)
        for h, preds in preds_by_h.items():
            preds.to_parquet(ARTIFACTS_DIR / f"oos_preds_{h}_{run_name}.parquet", index=False)
        (ARTIFACTS_DIR / f"run_config_{run_name}.json").write_text(
            json.dumps(
                {
                    "version": VERSION,
                    "fixes": fixes,
                    "n_stocks": int(df["Ticker"].nunique()),
                    "seed": seed,
                    "placebo": placebo or False,
                }
            )
        )
        summary_path = ARTIFACTS_DIR / f"walkforward_summary_{run_name}.md"
        _write_summary(
            all_metrics,
            summary_path,
            preds_by_h,
            exclude,
            run_name,
            universe_desc=universe_desc,
            prices=prices,
            sectors=sectors,
            acq=acq,
            fixes=fixes,
            placebo=placebo,
            seed=seed,
        )

        models_root = save_models(models_by_h, run_name)

        if "1y" in models_by_h:
            last = models_by_h["1y"]["folds"][-1]
            test = models_by_h["1y"]["test_cs"]
            x = test[last["feature_cols"]].to_numpy(dtype=float)
            p = last["lgbm_beat"].predict_proba(x)[:, 1]
            y = test["beat_1y"].to_numpy(dtype=float)
            calibration_table(y, p).to_csv(
                ARTIFACTS_DIR / f"calibration_1y_last_fold_{run_name}.csv", index=False
            )

        print(f"\nWrote {metrics_path}")
        print(f"Wrote {summary_path}")
        print(f"Wrote models under {models_root}")

    return all_metrics


if __name__ == "__main__":
    run_all()
