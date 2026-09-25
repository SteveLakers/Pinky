"""Universe + path config for Pinky."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_FEATURES_DIR = PROJECT_ROOT / "data" / "features"
DATA_LABELS_DIR = PROJECT_ROOT / "data" / "labels"
DATA_DATASET_DIR = PROJECT_ROOT / "data" / "dataset"

# Need this many trading days of history before a row is usable
FEATURE_WARMUP_DAYS = 252

# Prediction horizons in trading days (architecture-locked)
HORIZONS = {
    "3m": 63,
    "6m": 126,
    "1y": 252,
    "2y": 504,
}

# Walk-forward (expanding train window, fixed-length test)
WF_MIN_TRAIN_DAYS = 504   # ~2y trading days before first test
WF_TEST_DAYS = 252        # ~1y test fold
WF_STEP_DAYS = 252        # slide forward ~1y per fold


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

# Sector-balanced liquid universe (~128). Tech/AI tilted (~25%), no other sector > ~11%.
# "Tech/AI" is a Pinky bucket (includes AMZN/TSLA/GOOGL/META), not strict GICS.
# Survivorship bias: these are today's large names; delisted losers are missing.
UNIVERSE_BY_SECTOR: dict[str, list[str]] = {
    "Tech/AI": [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "ORCL", "CRM",
        "ADBE", "CSCO", "INTC", "AMD", "QCOM", "TXN", "INTU", "NOW", "IBM", "ACN",
        "AMAT", "LRCX", "KLAC", "MU", "ADI", "MRVL", "CDNS", "SNPS", "ANET", "PANW",
        "SMCI", "PLTR",
    ],
    "Healthcare": [
        "UNH", "JNJ", "LLY", "ABBV", "MRK", "PFE", "TMO", "ABT", "ISRG", "AMGN",
        "GILD", "VRTX", "REGN", "MDT",
    ],
    "Financials": [
        "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "BLK", "SCHW",
        "C", "SPGI", "CB", "PGR",
    ],
    "Industrials": [
        "CAT", "GE", "HON", "UPS", "BA", "DE", "RTX", "LMT", "UNP", "ETN",
        "ADP", "WM", "GD", "EMR",
    ],
    "Consumer Disc": [
        "HD", "MCD", "NKE", "SBUX", "BKNG", "LOW", "TJX", "CMG", "ORLY", "MAR",
        "GM", "F",
    ],
    "Consumer Staples": [
        "COST", "PEP", "KO", "WMT", "PG", "MDLZ", "CL", "MO", "KMB", "GIS",
    ],
    "Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "PSX", "MPC", "OXY"],
    "Materials": ["LIN", "SHW", "APD", "ECL", "NEM", "FCX"],
    "Utilities": ["NEE", "DUK", "SO", "D", "AEP", "EXC"],
    "Real Estate": ["PLD", "AMT", "EQIX", "SPG", "O", "PSA"],
    "Communication": ["NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS"],
}

UNIVERSE_STOCKS = [t for tickers in UNIVERSE_BY_SECTOR.values() for t in tickers]

# Best total-return names over the 2018–2025 test window (known only in hindsight).
HINDSIGHT_WINNERS = ["NVDA", "SMCI", "TSLA", "PLTR", "AVGO"]

TICKER_SECTOR = {t: s for s, tickers in UNIVERSE_BY_SECTOR.items() for t in tickers}

# Portfolio backtest (tradeable, net of costs)
BACKTEST_TOP_N = 10          # equal-weight top-N picks
BACKTEST_COST_BPS = 10.0     # cost per side (buy or sell), 1 bp = 0.01%
BACKTEST_REBALANCE = "M"     # monthly
BACKTEST_MAX_SECTOR_SHARE = 0.60  # max share of picks from one sector (0.60 of 10 = 6 names)

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
