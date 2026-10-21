"""
Sharadar data access (direct API: https://api.sharadar.com/v1.0/data/{table}).

- API key comes from `.env` (SHARADAR_API_KEY); never printed or logged.
- Bulk tables download as zipped CSV, then convert to parquet under data/sharadar/.
- Fundamentals: use As-Reported dimensions (ARQ / ART / ARY). Their `date` is the SEC
  filing date, so joins on `date` are point-in-time. MR* dimensions include restatements
  and would leak future information into a backtest.
"""

from __future__ import annotations

import io
import os
import re
import zipfile
from pathlib import Path
from urllib.parse import quote, quote_plus

import pandas as pd
import pyarrow.parquet as pq
import requests

from pinky.config import DATA_SHARADAR_DIR, PROJECT_ROOT

API_BASE = "https://api.sharadar.com/v1.0/data"

BULK_TABLES = ["tickers", "stocks", "fundamentals", "sp500", "actions", "daily", "events"]

DATE_COLS = {
    "tickers": ["firstadded", "firstpricedate", "lastpricedate", "firstquarter", "lastquarter", "lastupdated"],
    "stocks": ["date", "lastupdated"],
    "fundamentals": ["calendardate", "date", "reportperiod", "lastupdated"],
    "sp500": ["date"],
    "actions": ["date"],
    "daily": ["date", "lastupdated"],
    "events": ["date"],
}

# Only empty fields are missing; default pandas NA parsing turns tickers like "NA" into NaN.
CSV_KW = dict(keep_default_na=False, na_values=[""])


def api_key() -> str:
    key = os.environ.get("SHARADAR_API_KEY", "").strip()
    if not key:
        env = PROJECT_ROOT / ".env"
        if env.exists():
            m = re.search(r"^SHARADAR_API_KEY=(.*)$", env.read_text(), re.M)
            key = m.group(1).strip() if m else ""
    if not key:
        raise RuntimeError("SHARADAR_API_KEY missing: add it to .env")
    return key


def _scrub(text: str) -> str:
    key = api_key()
    for k in {key, quote(key, safe=""), quote_plus(key)}:
        text = text.replace(k, "***")
    return text


def _get(table: str, params: dict, **kw) -> requests.Response:
    """GET one table. Every failure is re-raised with the key removed and no chained traceback
    (requests puts the full URL, key included, in its error messages)."""
    try:
        r = requests.get(f"{API_BASE}/{table}", params={**params, "api_key": api_key()}, **kw)
    except requests.RequestException as e:
        raise RuntimeError(f"{table}: request failed: {_scrub(str(e))}") from None
    if r.status_code != 200:
        msg = f"{table}: HTTP {r.status_code}: {_scrub(r.text)[:300]}"
        r.close()
        raise RuntimeError(msg)
    return r


def query(table: str, **params) -> pd.DataFrame:
    """Small filtered query (CSV). Pass `from_` for the `from` param."""
    if "from_" in params:
        params["from"] = params.pop("from_")
    r = _get(table, {**params, "format": "csv"}, timeout=120)
    return pd.read_csv(io.StringIO(r.text), **CSV_KW)


def bulk_status(table: str) -> dict:
    return _get(table, {"status": "True"}, timeout=60).json()


def download_bulk(table: str, years: str = "full", out_dir: Path = DATA_SHARADAR_DIR) -> Path:
    """Stream the zipped CSV for a whole table to disk. Returns the zip path."""
    zdir = out_dir / "zips"
    zdir.mkdir(parents=True, exist_ok=True)
    path = zdir / f"{table}-{years}.csv.zip"
    tmp = path.with_suffix(".part")
    try:
        with _get(table, {"years": years}, stream=True, timeout=600, allow_redirects=True) as r:
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=8 << 20):
                    f.write(chunk)
    except requests.RequestException as e:
        raise RuntimeError(f"{table}: download failed: {_scrub(str(e))}") from None
    tmp.replace(path)
    return path


def zip_to_parquet(table: str, zip_path: Path, out_dir: Path = DATA_SHARADAR_DIR) -> Path:
    """Convert a bulk zip (one CSV inside) to parquet, parsing known date columns."""
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise RuntimeError(f"{zip_path.name}: expected 1 CSV, found {names}")
        with z.open(names[0]) as f:
            df = pd.read_csv(f, low_memory=False, **CSV_KW)
    for c in DATE_COLS.get(table, []):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in df.select_dtypes("float64").columns:
        df[c] = df[c].astype("float32") if table in {"stocks", "daily"} else df[c]
    path = out_dir / f"{table}.parquet"
    df.to_parquet(path, index=False)
    return path


def load(table: str, columns: list[str] | None = None, out_dir: Path = DATA_SHARADAR_DIR) -> pd.DataFrame:
    return pd.read_parquet(out_dir / f"{table}.parquet", columns=columns)


def pull_all(tables: list[str] | None = None, years: str = "full") -> dict[str, int]:
    """Download + convert every bulk table. Returns row counts."""
    counts = {}
    for t in tables or BULK_TABLES:
        z = download_bulk(t, years=years)
        p = zip_to_parquet(t, z)
        counts[t] = pq.ParquetFile(p).metadata.num_rows
        print(f"[sharadar] {t}: {counts[t]:,} rows -> {p.name} ({p.stat().st_size / 1e6:.0f} MB)")
    return counts


__all__ = [
    "BULK_TABLES",
    "api_key",
    "bulk_status",
    "download_bulk",
    "load",
    "pull_all",
    "query",
    "zip_to_parquet",
]
