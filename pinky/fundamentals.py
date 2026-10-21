"""
Point-in-time company growth and margin features from Sharadar SF1 (as-reported only).

Uses ARQ (quarterly) and ART (trailing 12 months). Never MR*: those rows are dated at
period end and leak ~2.5 months.

News date = the day a report's numbers became public:
- its earnings announcement (events code 22). An announcement belongs to the latest
  report period that ended at least `MIN_DAYS_AFTER_PERIOD` days before it (shorter gaps
  are early previews), and it must come no later than that report's SEC filing.
  Several → the latest (can only be late, never early).
- otherwise the SEC filing date. Events start Aug 2004; earlier years use filings.
  Filings dated < 10 days after period end are data errors (no real 10-Q is that fast); skipped.

Features attach with merge_asof(allow_exact_matches=False), so a number is used only on
dates strictly after its news date. A report published after a newer one (late catch-up
filing) never replaces the newer one.

Margins (batch 2): gross and operating margin over the last 12 months (ART), and their change
vs the same quarter a year ago (ARQ, in margin points). Revenue <= 0 -> missing.

Growth round 2 (one group per column, `growth2` = all four):
- ear_3d: stock minus SPY return over trading days -1..+1 around the quarter's news date
  (day 0 = first trading day on or after it); usable only after day +1's close.
- rev_sue: this quarter's revenue YoY minus the mean of the previous 4 quarters', divided by
  their std (floor `SUE_MIN_STD`); all 4 public by this quarter's news date.
- rev_cagr_3y: 12-month revenue vs 3 years earlier, per year (ART).
- rev_up_quarters: of this and the previous 7 quarters, how many grew YoY; all 8 known and public.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pinky.config import DATA_SHARADAR_DIR

GROWTH_FEATURES = [
    "rev_yoy_q",
    "rev_accel",
    "gp_yoy_q",
    "rev_yoy_ttm",
    "days_since_news",
    "has_growth",
]
MARGIN_FEATURES = ["gm_ttm", "gm_chg_q", "om_ttm", "om_chg_q"]
GROWTH2_FEATURES = ["ear_3d", "rev_sue", "rev_cagr_3y", "rev_up_quarters"]
GROUP_FEATURES = {
    "growth": GROWTH_FEATURES,
    "margins": MARGIN_FEATURES,
    "ear": ["ear_3d"],
    "sue": ["rev_sue"],
    "cagr": ["rev_cagr_3y"],
    "steady": ["rev_up_quarters"],
    "growth2": GROWTH2_FEATURES,
}

EARNINGS_EVENT_CODE = "22"
MIN_DAYS_AFTER_PERIOD = 10
QUARTER_STALE_DAYS = 365
TTM_STALE_DAYS = 550
REACTION_DAYS = (1, 1)  # trading days before / after day 0
SUE_QUARTERS = 4
SUE_MIN_STD = 0.01
STEADY_QUARTERS = 8

_FUND_PATH = DATA_SHARADAR_DIR / "fundamentals.parquet"
_EVENTS_PATH = DATA_SHARADAR_DIR / "events.parquet"


def _dates(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s).astype("datetime64[us]")


def first_filed(raw: pd.DataFrame) -> pd.DataFrame:
    """Keep the earliest filing per ticker/quarter, ignoring filings dated < 10 days after period end."""
    out = raw.assign(
        ticker=raw["ticker"].astype(str),
        date=_dates(raw["date"]),
        reportperiod=_dates(raw["reportperiod"]),
        calendardate=_dates(raw["calendardate"]),
    )
    out = out.loc[(out["date"] - out["reportperiod"]).dt.days >= MIN_DAYS_AFTER_PERIOD]
    out = out.sort_values(["date", "ticker", "calendardate"], kind="stable")
    return out.drop_duplicates(["ticker", "calendardate"], keep="first").reset_index(drop=True)


def earnings_announcements(events: pd.DataFrame) -> pd.DataFrame:
    """ticker, ann for events whose codes include 22 (earnings announcement)."""
    codes = events["eventcodes"].fillna("").astype(str)
    hit = codes.str.split("|").map(lambda xs: EARNINGS_EVENT_CODE in xs).astype(bool)
    out = pd.DataFrame(
        {
            "ticker": events.loc[hit, "ticker"].astype(str).to_numpy(),
            "ann": _dates(events.loc[hit, "date"]).to_numpy(),
        }
    )
    return out.drop_duplicates().reset_index(drop=True)


def with_news_dates(reports: pd.DataFrame, announcements: pd.DataFrame) -> pd.DataFrame:
    """Add `ann` (the report's own announcement, else NaT) and `news_date` (ann, else filing)."""
    out = reports.reset_index(drop=True).drop(columns=["ann", "news_date"], errors="ignore")
    if announcements.empty:
        out["ann"] = pd.Series(pd.NaT, index=out.index, dtype="datetime64[us]")
    else:
        periods = (
            out[["ticker", "reportperiod", "calendardate"]]
            .sort_values(["reportperiod", "calendardate"], kind="stable")
            .drop_duplicates(["ticker", "reportperiod"], keep="last")
        )
        anns = announcements[["ticker", "ann"]].copy()
        anns["cut"] = anns["ann"] - pd.Timedelta(days=MIN_DAYS_AFTER_PERIOD)
        owner = pd.merge_asof(
            anns.sort_values("cut", kind="stable"),
            periods,
            left_on="cut",
            right_on="reportperiod",
            by="ticker",
            direction="backward",
        ).dropna(subset=["calendardate"])
        owner = owner.merge(out[["ticker", "calendardate", "date"]], on=["ticker", "calendardate"])
        owner = owner.loc[owner["ann"] <= owner["date"]]
        latest = owner.groupby(["ticker", "calendardate"], as_index=False)["ann"].max()
        out = out.merge(latest, on=["ticker", "calendardate"], how="left", validate="one_to_one")
        out["ann"] = out["ann"].astype("datetime64[us]")
    out["news_date"] = out["ann"].where(out["ann"].notna(), out["date"])
    return out


def add_yoy(reports: pd.DataFrame, col: str, months: int = 12) -> pd.Series:
    """col / same calendar period `months` earlier − 1. Both > 0; the earlier report public first."""
    cur = reports[["ticker", "calendardate", col, "news_date"]]
    prev = cur.assign(calendardate=cur["calendardate"] + pd.offsets.MonthEnd(months))
    m = cur.merge(prev, on=["ticker", "calendardate"], how="left", suffixes=("", "_prev"), validate="one_to_one")
    ok = (m[col] > 0) & (m[f"{col}_prev"] > 0) & (m["news_date_prev"] <= m["news_date"])
    return pd.Series(np.where(ok, m[col] / m[f"{col}_prev"] - 1.0, np.nan), index=reports.index)


def margin(reports: pd.DataFrame, col: str) -> pd.Series:
    """col / revenue; missing unless revenue > 0."""
    rev = reports["revenue"]
    return (reports[col] / rev.where(rev > 0)).astype("float64")


def add_change(reports: pd.DataFrame, col: str, months: int = 12) -> pd.Series:
    """col minus the same calendar period `months` earlier; the earlier report public first."""
    cur = reports[["ticker", "calendardate", col, "news_date"]]
    prev = cur.assign(calendardate=cur["calendardate"] + pd.offsets.MonthEnd(months))
    m = cur.merge(prev, on=["ticker", "calendardate"], how="left", suffixes=("", "_prev"), validate="one_to_one")
    ok = m["news_date_prev"].notna() & (m["news_date_prev"] <= m["news_date"])
    return pd.Series(np.where(ok, m[col] - m[f"{col}_prev"], np.nan), index=reports.index)


def add_accel(reports: pd.DataFrame, yoy_col: str = "rev_yoy_q") -> pd.Series:
    """This quarter's YoY minus last quarter's; last quarter must have been public first."""
    cur = reports[["ticker", "calendardate", yoy_col, "news_date"]]
    prev = cur.assign(calendardate=cur["calendardate"] + pd.offsets.MonthEnd(3))
    m = cur.merge(prev, on=["ticker", "calendardate"], how="left", suffixes=("", "_pq"), validate="one_to_one")
    ok = m["news_date_pq"].notna() & (m["news_date_pq"] <= m["news_date"])
    return pd.Series(np.where(ok, m[yoy_col] - m[f"{yoy_col}_pq"], np.nan), index=reports.index)


def _earlier_quarters(reports: pd.DataFrame, col: str, n: int) -> pd.DataFrame:
    """col for each of the `n` quarters before every report; missing unless public by its news date."""
    cur = reports[["ticker", "calendardate"]]
    out = {}
    for k in range(1, n + 1):
        prev = reports[["ticker", "calendardate", col, "news_date"]]
        prev = prev.assign(calendardate=prev["calendardate"] + pd.offsets.MonthEnd(3 * k))
        m = cur.merge(prev, on=["ticker", "calendardate"], how="left", validate="one_to_one")
        out[k] = m[col].where(m["news_date"] <= reports["news_date"].to_numpy()).to_numpy()
    return pd.DataFrame(out, index=reports.index)


def add_sue(reports: pd.DataFrame, col: str = "rev_yoy_q") -> pd.Series:
    """(col − mean of the previous `SUE_QUARTERS` quarters') / max(their std, `SUE_MIN_STD`)."""
    prev = _earlier_quarters(reports, col, SUE_QUARTERS)
    ok = reports[col].notna() & prev.notna().all(axis=1)
    sd = prev.std(axis=1, ddof=1).clip(lower=SUE_MIN_STD)
    return ((reports[col] - prev.mean(axis=1)) / sd).where(ok)


def add_up_quarters(reports: pd.DataFrame, col: str = "rev_yoy_q") -> pd.Series:
    """How many of this and the previous `STEADY_QUARTERS` − 1 quarters had col > 0; all known."""
    vals = pd.concat([reports[[col]], _earlier_quarters(reports, col, STEADY_QUARTERS - 1)], axis=1)
    return (vals > 0).sum(axis=1).astype("float64").where(vals.notna().all(axis=1))


def add_reaction(reports: pd.DataFrame, tr: pd.DataFrame, spy: pd.Series) -> pd.DataFrame:
    """`ear_3d` (stock − SPY over trading days −1…+1 around news_date) and `ear_known` (day +1).

    `ear_known` is missing only when day +1 is past the price data (not known yet).
    """
    before, after = REACTION_DAYS
    cal = pd.DatetimeIndex(tr.index)
    day0 = cal.searchsorted(reports["news_date"].to_numpy(), side="left")
    start, end = day0 - before - 1, day0 + after
    inside = (start >= 0) & (end < len(cal))
    col = tr.columns.get_indexer(reports["ticker"])
    ok = inside & (col >= 0)
    px = tr.to_numpy(dtype="float64")
    bench = spy.reindex(cal).to_numpy(dtype="float64")
    s, e, c = start[ok], end[ok], col[ok]
    ear = np.full(len(reports), np.nan)
    ear[ok] = (px[e, c] / px[s, c] - 1.0) - (bench[e] / bench[s] - 1.0)
    known = np.full(len(reports), np.datetime64("NaT"), dtype="datetime64[us]")
    known[end < len(cal)] = cal[end[end < len(cal)]].to_numpy().astype("datetime64[us]")
    return pd.DataFrame({"ear_3d": np.where(np.isfinite(ear), ear, np.nan), "ear_known": known}, index=reports.index)


def _load_dimension(dimension: str, value_cols: list[str]) -> pd.DataFrame:
    cols = ["ticker", "calendardate", "reportperiod", "date", *value_cols]
    raw = pd.read_parquet(_FUND_PATH, columns=cols, filters=[("dimension", "==", dimension)])
    return first_filed(raw)


def load_announcements() -> pd.DataFrame:
    events = pd.read_parquet(_EVENTS_PATH, columns=["ticker", "date", "eventcodes"])
    return earnings_announcements(events)


def quarterly_growth_reports(
    raw: pd.DataFrame | None = None,
    announcements: pd.DataFrame | None = None,
) -> pd.DataFrame:
    reports = first_filed(raw) if raw is not None else _load_dimension("ARQ", ["revenue", "gp"])
    anns = announcements if announcements is not None else load_announcements()
    reports = with_news_dates(reports, anns)
    reports["rev_yoy_q"] = add_yoy(reports, "revenue")
    reports["gp_yoy_q"] = add_yoy(reports, "gp")
    reports["rev_accel"] = add_accel(reports, "rev_yoy_q")
    return reports


def ttm_growth_reports(
    raw: pd.DataFrame | None = None,
    announcements: pd.DataFrame | None = None,
) -> pd.DataFrame:
    reports = first_filed(raw) if raw is not None else _load_dimension("ART", ["revenue"])
    anns = announcements if announcements is not None else load_announcements()
    reports = with_news_dates(reports, anns)
    reports["rev_yoy_ttm"] = add_yoy(reports, "revenue")
    return reports


def quarterly_margin_reports(
    raw: pd.DataFrame | None = None,
    announcements: pd.DataFrame | None = None,
) -> pd.DataFrame:
    reports = first_filed(raw) if raw is not None else _load_dimension("ARQ", ["revenue", "gp", "opinc"])
    anns = announcements if announcements is not None else load_announcements()
    reports = with_news_dates(reports, anns)
    reports["gm_q"] = margin(reports, "gp")
    reports["om_q"] = margin(reports, "opinc")
    reports["gm_chg_q"] = add_change(reports, "gm_q")
    reports["om_chg_q"] = add_change(reports, "om_q")
    return reports


def ttm_margin_reports(
    raw: pd.DataFrame | None = None,
    announcements: pd.DataFrame | None = None,
) -> pd.DataFrame:
    reports = first_filed(raw) if raw is not None else _load_dimension("ART", ["revenue", "gp", "opinc"])
    anns = announcements if announcements is not None else load_announcements()
    reports = with_news_dates(reports, anns)
    reports["gm_ttm"] = margin(reports, "gp")
    reports["om_ttm"] = margin(reports, "opinc")
    return reports


def quarterly_growth2_reports(
    tr: pd.DataFrame,
    spy: pd.Series,
    raw: pd.DataFrame | None = None,
    announcements: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Quarterly growth reports + ear_3d / ear_known, rev_sue, rev_up_quarters."""
    reports = quarterly_growth_reports(raw, announcements)
    reaction = add_reaction(reports, tr, spy)
    reports["ear_3d"], reports["ear_known"] = reaction["ear_3d"], reaction["ear_known"]
    reports["rev_sue"] = add_sue(reports)
    reports["rev_up_quarters"] = add_up_quarters(reports)
    return reports


def ttm_growth2_reports(
    raw: pd.DataFrame | None = None,
    announcements: pd.DataFrame | None = None,
) -> pd.DataFrame:
    reports = first_filed(raw) if raw is not None else _load_dimension("ART", ["revenue"])
    anns = announcements if announcements is not None else load_announcements()
    reports = with_news_dates(reports, anns)
    reports["rev_cagr_3y"] = (1.0 + add_yoy(reports, "revenue", months=36)) ** (1.0 / 3.0) - 1.0
    return reports


def published_reports(reports: pd.DataFrame, value_cols: list[str], tag: str) -> pd.DataFrame:
    """Reports in the order they became public, minus any older than one already public."""
    news, period = f"news_{tag}", f"period_{tag}"
    r = reports[["ticker", "news_date", "reportperiod", *value_cols]].rename(
        columns={"ticker": "Ticker", "news_date": news, "reportperiod": period}
    )
    r = r.dropna(subset=[news]).sort_values([news, period], kind="stable")
    newest_before = r.groupby("Ticker")[period].cummax().groupby(r["Ticker"]).shift()
    return r.loc[newest_before.isna() | (r[period] > newest_before)]


def _asof_attach(
    rows: pd.DataFrame,
    reports: pd.DataFrame,
    value_cols: list[str],
    stale_days: int,
    tag: str,
) -> pd.DataFrame:
    news, period = f"news_{tag}", f"period_{tag}"
    out = pd.merge_asof(
        rows.sort_values("Date", kind="stable"),
        published_reports(reports, value_cols, tag),
        left_on="Date",
        right_on=news,
        by="Ticker",
        direction="backward",
        allow_exact_matches=False,
    )
    early = out[news].notna() & (out[news] >= out["Date"])
    if early.any():
        raise RuntimeError(f"{int(early.sum())} {tag} news dates are not strictly before the row Date")
    age = (out["Date"] - out[period]).dt.days
    for c in value_cols:
        out[c] = out[c].where(age <= stale_days)
    return out


def growth_feature_frame(
    rows: pd.DataFrame,
    quarterly: pd.DataFrame | None = None,
    ttm: pd.DataFrame | None = None,
    with_dates: bool = False,
) -> pd.DataFrame:
    """Date, Ticker + the six growth columns (+ news/period dates of the used reports if `with_dates`)."""
    keys = pd.DataFrame({"Date": _dates(rows["Date"]), "Ticker": rows["Ticker"].astype(str)})
    if keys.duplicated(["Date", "Ticker"]).any():
        raise ValueError("growth attach needs unique Date, Ticker rows")

    q = quarterly if quarterly is not None else quarterly_growth_reports()
    t = ttm if ttm is not None else ttm_growth_reports()
    out = _asof_attach(keys, q, ["rev_yoy_q", "gp_yoy_q", "rev_accel"], QUARTER_STALE_DAYS, "q")
    out = _asof_attach(out, t, ["rev_yoy_ttm"], TTM_STALE_DAYS, "t")

    latest = out[["news_q", "news_t"]].max(axis=1)
    out["days_since_news"] = (out["Date"] - latest).dt.days.astype("float32")
    out["has_growth"] = out[["rev_yoy_q", "gp_yoy_q", "rev_yoy_ttm"]].notna().any(axis=1).astype("float32")
    for c in ("rev_yoy_q", "rev_accel", "gp_yoy_q", "rev_yoy_ttm"):
        out[c] = out[c].astype("float32")
    helpers = ["news_q", "period_q", "news_t", "period_t"] if with_dates else []
    return out[["Date", "Ticker", *GROWTH_FEATURES, *helpers]]


def attach_growth_features(rows: pd.DataFrame) -> pd.DataFrame:
    """Add the six growth columns to a Date/Ticker frame (row order kept)."""
    extra = growth_feature_frame(rows[["Date", "Ticker"]])
    extra = extra.astype({"Date": rows["Date"].dtype, "Ticker": rows["Ticker"].dtype})
    return rows.merge(extra, on=["Date", "Ticker"], how="left", validate="one_to_one")


def margin_feature_frame(
    rows: pd.DataFrame,
    quarterly: pd.DataFrame | None = None,
    ttm: pd.DataFrame | None = None,
    with_dates: bool = False,
) -> pd.DataFrame:
    """Date, Ticker + the four margin columns (+ news/period dates of the used reports if `with_dates`)."""
    keys = pd.DataFrame({"Date": _dates(rows["Date"]), "Ticker": rows["Ticker"].astype(str)})
    if keys.duplicated(["Date", "Ticker"]).any():
        raise ValueError("margin attach needs unique Date, Ticker rows")

    q = quarterly if quarterly is not None else quarterly_margin_reports()
    t = ttm if ttm is not None else ttm_margin_reports()
    out = _asof_attach(keys, q, ["gm_chg_q", "om_chg_q"], QUARTER_STALE_DAYS, "q")
    out = _asof_attach(out, t, ["gm_ttm", "om_ttm"], TTM_STALE_DAYS, "t")
    for c in MARGIN_FEATURES:
        out[c] = out[c].astype("float32")
    helpers = ["news_q", "period_q", "news_t", "period_t"] if with_dates else []
    return out[["Date", "Ticker", *MARGIN_FEATURES, *helpers]]


def attach_margin_features(rows: pd.DataFrame) -> pd.DataFrame:
    """Add the four margin columns to a Date/Ticker frame (row order kept)."""
    extra = margin_feature_frame(rows[["Date", "Ticker"]])
    extra = extra.astype({"Date": rows["Date"].dtype, "Ticker": rows["Ticker"].dtype})
    return rows.merge(extra, on=["Date", "Ticker"], how="left", validate="one_to_one")


def growth2_feature_frame(
    rows: pd.DataFrame,
    quarterly: pd.DataFrame,
    ttm: pd.DataFrame,
    with_dates: bool = False,
) -> pd.DataFrame:
    """Date, Ticker + the four round 2 columns (+ news/period dates of the used reports if `with_dates`).

    ear_3d attaches on its known date (day +1), the rest on the report's news date.
    """
    keys = pd.DataFrame({"Date": _dates(rows["Date"]), "Ticker": rows["Ticker"].astype(str)})
    if keys.duplicated(["Date", "Ticker"]).any():
        raise ValueError("growth2 attach needs unique Date, Ticker rows")

    reaction = quarterly.assign(news_date=quarterly["ear_known"])
    out = _asof_attach(keys, reaction, ["ear_3d"], QUARTER_STALE_DAYS, "e")
    out = _asof_attach(out, quarterly, ["rev_sue", "rev_up_quarters"], QUARTER_STALE_DAYS, "q")
    out = _asof_attach(out, ttm, ["rev_cagr_3y"], TTM_STALE_DAYS, "t")
    for c in GROWTH2_FEATURES:
        out[c] = out[c].astype("float32")
    helpers = ["news_e", "period_e", "news_q", "period_q", "news_t", "period_t"] if with_dates else []
    return out[["Date", "Ticker", *GROWTH2_FEATURES, *helpers]]


def attach_growth2_features(rows: pd.DataFrame, tr: pd.DataFrame, spy: pd.Series) -> pd.DataFrame:
    """Add the four round 2 columns to a Date/Ticker frame (row order kept); `tr`, `spy` = daily prices."""
    extra = growth2_feature_frame(rows[["Date", "Ticker"]], quarterly_growth2_reports(tr, spy), ttm_growth2_reports())
    extra = extra.astype({"Date": rows["Date"].dtype, "Ticker": rows["Ticker"].dtype})
    return rows.merge(extra, on=["Date", "Ticker"], how="left", validate="one_to_one")


def shuffle_within_date(df: pd.DataFrame, cols: list[str], seed: int) -> pd.DataFrame:
    """Placebo: give each row another same-date row's values of `cols` (block kept together)."""
    missing = sorted(set(cols) - set(df.columns))
    if missing:
        raise ValueError(f"placebo needs all of its columns; missing {missing}")
    if not df.index.is_unique:
        raise ValueError("placebo needs a unique index")
    rng = np.random.default_rng(seed)
    base = df.sort_values("Date", kind="stable").index
    order = df.assign(_r=rng.random(len(df))).sort_values(["Date", "_r"], kind="stable").index
    out = df.copy()
    out.loc[base, cols] = df.loc[order, cols].to_numpy()
    return out


def shuffle_growth_within_date(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Placebo for the six growth columns (v8 name; same shuffle as `shuffle_within_date`)."""
    return shuffle_within_date(df, GROWTH_FEATURES, seed)


__all__ = [
    "GROUP_FEATURES",
    "GROWTH2_FEATURES",
    "GROWTH_FEATURES",
    "MARGIN_FEATURES",
    "add_accel",
    "add_change",
    "add_reaction",
    "add_sue",
    "add_up_quarters",
    "add_yoy",
    "attach_growth2_features",
    "attach_growth_features",
    "attach_margin_features",
    "earnings_announcements",
    "first_filed",
    "growth2_feature_frame",
    "growth_feature_frame",
    "load_announcements",
    "margin",
    "margin_feature_frame",
    "published_reports",
    "quarterly_growth2_reports",
    "quarterly_growth_reports",
    "quarterly_margin_reports",
    "shuffle_growth_within_date",
    "shuffle_within_date",
    "ttm_growth2_reports",
    "ttm_growth_reports",
    "ttm_margin_reports",
    "with_news_dates",
]
