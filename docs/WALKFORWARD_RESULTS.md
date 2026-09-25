# Walk-Forward Results

## v3 — bigger balanced universe + trading-cost backtest (2026-09-25)

Changes vs v2:
1. Universe 58 → **128** stocks, sector-balanced (Tech/AI 25%, no other sector > 11%)
2. New **portfolio backtest**: monthly rebalance, equal-weight top-10, **10 bps per side** costs, trades fill next day's close
3. Honesty checks: naive momentum baseline, "remove top-5 hindsight winners" stress test, random-pick sanity check

### Ranking metrics (1y, 8 folds)

| Metric | LightGBM | Ridge |
|---|---|---|
| Mean rank IC | 0.159 | **0.166** |
| Folds LightGBM wins (IC) | 25% | — |
| Mean top-5 1y excess | 0.524 | **0.594** |
| Test beat rate | 49% | 49% |

**Soft bar vs Ridge: FAIL.** On the bigger universe, Ridge is slightly better.

### Portfolio backtest (Jan 2018 → Oct 2025, net of 10 bps)

| Strategy | CAGR net | Max drawdown |
|---|---|---|
| SPY | +14.1% | -23.0% |
| All 128 stocks equal-weight | +18.2% | — |
| Random top-10 (20 seeds, mean) | +16.0% | — |
| Momentum 12-1 (naive) | +29.4% | -23.2% |
| **LightGBM top-10** | **+41.4%** | -32.6% |
| Ridge top-10 | +43.0% | -34.5% |
| LightGBM, top-5 winners removed | +24.7% | -29.6% |
| Momentum, top-5 winners removed | +18.0% | -24.0% |

Top-5 winners in the window: NVDA, SMCI, TSLA, PLTR, AVGO.

- Costs are small: ~0.9%/yr drag at 10 bps (78% monthly turnover). Even at 25 bps, still +39%.
- LightGBM picks are **63% Tech/AI** on average (universe is 25%).
- Beat SPY in 57% of months; 2022 roughly flat vs SPY.

### Honest read

- **The +41% is inflated.** The universe is today's big winners (survivorship / hindsight bias). NVDA, SMCI, PLTR are in the list *because* they won.
- Remove just 5 hindsight winners and it drops to **+24.7%**, still ~+10%/yr over SPY and ~+7% over naive momentum.
- The model is mostly a **smarter momentum / tech tilt**. It beats naive momentum in every test.
- Ridge ≈ LightGBM. The simple model is as good (or better) right now.

### Next levers

- Fix survivorship: point-in-time universe (needs historical index membership — paid data)
- Sector caps in the portfolio (e.g., max 40% Tech/AI)
- Consider Ridge (or a blend) as the main model

---

## v2 prep (2026-09-23, 58 stocks)

- Cross-sectional z-score, correlated features dropped (31 → 11), 1y focus, regularized LightGBM
- Rank IC: LightGBM 0.122 vs Ridge 0.108 (wins 88% of folds)
- Top-5 excess: LightGBM 0.425 vs Ridge 0.434
- Soft bar: FAIL / MIXED
