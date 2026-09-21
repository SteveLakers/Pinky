"""Universe + path config for Pinky v1 prototype."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_FEATURES_DIR = PROJECT_ROOT / "data" / "features"
DATA_LABELS_DIR = PROJECT_ROOT / "data" / "labels"

# Need this many trading days of history before a row is usable
FEATURE_WARMUP_DAYS = 252

# Prediction horizons in trading days (architecture-locked)
HORIZONS = {
    "3m": 63,
    "6m": 126,
    "1y": 252,
    "2y": 504,
}

# How far back to pull daily bars (enough room for 2y labels + features later)
HISTORY_START = "2015-01-01"

# Benchmark + macro helpers (architecture-locked)
BENCHMARK = "SPY"
HELPERS = [
    "IWM",   # relative-strength / size feature (not the beat target)
    "^VIX",  # fear
    "^TNX",  # 10y yield
    "^IRX",  # short rates
]

# Broader liquid universe (~55) across sectors — not just mega-cap winners.
# Still smaller than full NASDAQ-100; expand again later if needed.
UNIVERSE_STOCKS = [
    # Mega / large tech
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "ORCL", "CRM",
    "ADBE", "CSCO", "INTC", "AMD", "QCOM", "TXN", "INTU", "NOW",
    # Consumer / retail / media
    "COST", "NFLX", "PEP", "KO", "WMT", "HD", "MCD", "NKE", "SBUX", "DIS", "CMCSA", "BKNG",
    # Healthcare
    "UNH", "JNJ", "LLY", "ABBV", "MRK", "PFE", "TMO", "ABT", "ISRG",
    # Financials
    "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "BLK",
    # Industrials / energy / other
    "CAT", "GE", "HON", "UPS", "BA", "XOM", "CVX", "LIN", "ACN", "IBM",
]

# Back-compat alias used by older scripts/imports
STARTER_STOCKS = UNIVERSE_STOCKS


def all_tickers() -> list[str]:
    """Unique tickers to download (stocks + benchmark + helpers)."""
    seen: set[str] = set()
    ordered: list[str] = []
    for t in [BENCHMARK, *HELPERS, *UNIVERSE_STOCKS]:
        if t not in seen:
            seen.add(t)
            ordered.append(t)
    return ordered
