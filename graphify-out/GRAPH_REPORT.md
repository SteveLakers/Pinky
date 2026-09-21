# Graph Report - Pinky  (2026-09-21)

## Corpus Check
- 11 files · ~3,011 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: .mdc 4, (none) 4)

## Summary
- 89 nodes · 147 edges · 14 communities (10 shown, 4 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Pinky Architecture Plan
- pull_universe
- raw_io.py
- Pinky
- __init__.py
- adj_close_series
- features.py
- build_universe_labels
- data_pull.py
- labels.py
- build_labels_for_ticker
- load_raw_ticker
- all_tickers
- _safe_filename

## God Nodes (most connected - your core abstractions)
1. `build_bfm_prediction_features()` - 13 edges
2. `load_raw_ticker()` - 11 edges
3. `Pinky Architecture Plan` - 11 edges
4. `adj_close_series()` - 10 edges
5. `_helper_frame()` - 9 edges
6. `build_labels_for_ticker()` - 9 edges
7. `Pinky` - 9 edges
8. `build_universe_labels()` - 8 edges
9. `pull_universe()` - 7 edges
10. `build_universe_features()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Repo layout` --references--> `build_bfm_prediction_features()`  [INFERRED]
  project.md → pinky/features.py
- `pull_universe()` --calls--> `all_tickers()`  [EXTRACTED]
  pinky/data_pull.py → pinky/config.py
- `load_raw_ticker()` --calls--> `_safe_filename()`  [EXTRACTED]
  pinky/raw_io.py → pinky/data_pull.py
- `_helper_frame()` --calls--> `adj_close_series()`  [EXTRACTED]
  pinky/features.py → pinky/raw_io.py

## Import Cycles
- None detected.

## Communities (14 total, 4 thin omitted)

### Community 0 - "Pinky Architecture Plan"
Cohesion: 0.17
Nodes (11): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+3 more)

### Community 1 - "pull_universe"
Cohesion: 0.32
Nodes (8): download_ticker(), pull_universe(), DataFrame, Path, Pull one ticker's daily history. Raises ValueError if the download is empty or…, Write one ticker to parquet under data/raw/., Download and save each ticker. Returns mapping ticker -> parquet path for…, save_ticker()

### Community 2 - "raw_io.py"
Cohesion: 0.40
Nodes (4): pandas, pathlib, Universe + path config for Pinky v1 prototype., Load saved raw parquet bars.

### Community 3 - "Pinky"
Cohesion: 0.20
Nodes (9): Build order, Current starter universe, Pinky, Planned stack (v1), Repo layout, Rules (always on), Status, What it will do (+1 more)

### Community 5 - "adj_close_series"
Cohesion: 0.50
Nodes (4): adj_close_series(), DataFrame, Series, Prefer Adj Close for returns; fall back to Close.

### Community 6 - "features.py"
Cohesion: 0.22
Nodes (16): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+8 more)

### Community 7 - "build_universe_labels"
Cohesion: 0.32
Nodes (7): build_universe_labels(), DataFrame, Path, Write stacked label panel to parquet., Build and stack labels for all starter stocks., save_labels(), CLI: build labels vs SPY from data/raw/ into data/labels/.

### Community 8 - "data_pull.py"
Cohesion: 0.33
Nodes (4): Download daily OHLCV via yfinance and save to data/raw/., CLI: pull the small starter universe into data/raw/., time, yfinance

### Community 10 - "build_labels_for_ticker"
Cohesion: 0.50
Nodes (5): build_labels_for_ticker(), _forward_return(), Series, Return from t to t+horizon_days. NaN near the end where future is unknown., Build excess-return and beat labels for one stock across all horizons. Rows…

### Community 11 - "load_raw_ticker"
Cohesion: 0.67
Nodes (3): load_raw_ticker(), Path, Load one ticker's raw OHLCV parquet. Raises FileNotFoundError if missing.

## Knowledge Gaps
- **16 isolated node(s):** `Goal`, `Locked decisions`, `What we predict`, `Labels (truth the model learns)`, `Models` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 47 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`, `Pinky`, `load_raw_ticker`, `adj_close_series`?**
  _High betweenness centrality (0.447) - this node is a cross-community bridge._
- **Why does `load_raw_ticker()` connect `load_raw_ticker` to `raw_io.py`, `adj_close_series`, `features.py`, `build_universe_labels`, `labels.py`, `build_labels_for_ticker`, `_safe_filename`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.216) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `build_bfm_prediction_features()` (e.g. with `Feature pipeline` and `Repo layout`) actually correct?**
  _`build_bfm_prediction_features()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Goal`, `Locked decisions`, `What we predict` to the rest of the system?**
  _16 weakly-connected nodes found - possible documentation gaps or missing edges._