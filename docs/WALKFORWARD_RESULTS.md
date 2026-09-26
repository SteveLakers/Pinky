# Walk-Forward Results

## v5_pit — honest baseline on the point-in-time universe (2026-09-26)

Same price-only model (13 stock features; 12 after the correlation drop), new data:
Sharadar point-in-time liquid US universe (price ≥ $5, ≥ $5M/day), delisted stocks included
(delisting-aware returns), weekly rows, 19 test years 2001–2019 (+ early 2020 in the backtest).
Dev only — labels end before 2022-01-01; the holdout is untouched.
Run: `PYTHONPATH=. python scripts/train_walkforward.py --pit` → `artifacts/*_v5_pit.*`

| Signal (10 bps, top-10, Jan 2001 → Feb 2020) | CAGR | Max DD | Months > SPY | Precision@10 | Winner capture |
|---|---|---|---|---|---|
| SPY | +6.9% | −52.1% | — | — | — |
| Equal-weight universe (~1,940 stocks) | +7.5% | — | — | 0.100 (random) | 0.005 (random) |
| Ridge | **+7.6%** | −47.4% | 47% | 0.079 | 0.019 |
| Blend | +0.6% | −68.4% | 43% | 0.104 | 0.028 |
| LightGBM | −8.0% | −86.9% | 43% | 0.148 | 0.027 |
| Momentum 12-1 | −1.4% | −83.5% | 48% | 0.169 | 0.048 |

- Mean rank IC: Ridge 0.066, Blend 0.048, LightGBM 0.025. LightGBM beats Ridge on IC in 26% of folds.
- 60% sector cap changes almost nothing (LightGBM: Technology 21%, Healthcare 17%, no sector near 60%).
- "Ex top-5 winners" barely changes anything — the universe is no longer hand-picked with hindsight.
- 25 bps costs: models lose another ~2.8–2.9%/yr (turnover 150–170%/month); momentum 1.7%/yr (turnover 94%).
- LightGBM (capped) had crushing years vs SPY: 2009 −42.0%, 2011 −47.4%, 2012 −48.5%.

### What the picks look like (monthly top-10, dev window)

| | Volatility (63d, median) | Share ending in top 10% | Share losing > 50% vs SPY | 1y excess (median) |
|---|---|---|---|---|
| LightGBM | 49% | 15% | 18% | −10.6% |
| Ridge | 19% | 8% | 7% | −1.7% |
| Universe | 32% | 10% | 7% | −2.2% |

### Honest read

- **Price data alone has no reliable edge on a realistic universe.** Ridge ≈ equal-weight market; LightGBM and momentum lose money.
- LightGBM learned to pick high-volatility stocks: more winners **and** far more blow-ups. Price history predicts the *size* of moves, not the *direction*.
- The old +41% (and +19% ex-5) came from survivorship (today's 128 big names) + hindsight.
- Next: Phase 2 company data (growth + revenue acceleration) and model fixes (rank target, rank features, score young stocks, size feature).

### Data checks done

- Labels verified by hand: AAPL 2019 +104%, NVDA 2023 +233%, LEHMQ 2008 −99.9%, ENRNQ 2001 −99% (bankruptcies stay in the data).
- Fold purge verified: every train label ends before its test year; last dev label ends 2021-12-31.
- Biggest 1y winners in the data are real (NVAX 2020, GME 2020, QCOM 1999, OKLO 2024). ~195 of 2.8M rows show one-day jumps > 100% on tiny stocks (likely split glitches) — left in for this baseline.

---

## v4 ex5 — hindsight winners removed from train AND test (2026-09-25)

Removed NVDA, SMCI, TSLA, PLTR, AVGO from the universe entirely (123 stocks), retrained, re-backtested.
Run: `PYTHONPATH=. python scripts/train_walkforward.py --ex-winners` → `artifacts/*_v4_ex5.*`

| Signal (10 bps, top-10) | Uncapped | Capped 60% | With winners (v4.1) |
|---|---|---|---|
| LightGBM | +21.0% | +19.4% | +41.2% capped |
| Ridge | **+26.3%** | **+22.6%** | +43.0% uncapped |
| Blend | +22.9% | +20.7% | — |
| Momentum 12-1 | +18.0% | +18.7% | +29.4% |

SPY +14.1%, equal-weight 123 stocks +16.4%. Max DD: all models -31% to -35% (SPY -23%).

- Removing them from **training too** hurts more than only skipping them at pick time (+27% → +19% for LightGBM capped): the model had learned from those winners' patterns.
- **Ridge now clearly beats LightGBM** (+26% vs +21%). This reverses the v4 read that LightGBM was most robust.
- Cap hurts every model here (except momentum).
- LightGBM capped vs 123-stock equal-weight: only **~+3%/yr**; vs naive momentum ~+1%/yr.
- LightGBM capped had bad years: 2018 (-12.5% vs SPY), 2024 (-24% vs SPY).
- Fold 7 (latest) top-5 excess is huge (+151%), driven by MU/INTC/MRVL/AMD picks in the data — one period can swing averages.

### Honest read

- The real edge is **much smaller** than v4.1 showed. Most of the +41% came from 5 hindsight stocks.
- Ridge (simple) is the stronger signal once the winners are gone.
- Survivorship bias still inflates these numbers.

---

## v4.1 — sector cap loosened to 60% (2026-09-25)

User chose a bit more risk, **no leverage** (account can't do margin). Tested caps on LightGBM, top-10, 1x:

| Max per sector | CAGR net | Max DD | Worst month | Tech/AI share | Ex top-5 winners CAGR |
|---|---|---|---|---|---|
| 40% | +36.5% | -34.3% | -26.7% | 38% | +26.2% |
| 50% | +35.3% | -35.4% | -27.7% | 46% | +25.4% |
| **60% (new default)** | **+41.2%** | **-32.3%** | **-22.9%** | **53%** | **+27.2%** |
| 70% | +42.8% | -32.4% | -22.5% | 58% | +27.4% |
| None | +41.4% | -32.6% | -22.5% | 63% | +24.7% |

Also tested (rejected): top-5 picks (same CAGR, worse worst month); 1.25x/1.5x leverage (+44%/+51% CAGR but -42%/-50% max DD; not allowed on account).

- Lower drawdown at 60% is **only because tech won 2018–2025**. Real risk = tech concentration (e.g., 2000–02 style tech crash).
- 60% chosen after seeing results → mild overfit; 50% < 40% shows noise.

---

## v4 — sector cap (max 40%) + Ridge/LightGBM blend (2026-09-25)

Changes vs v3:
1. **Sector cap:** no sector above 40% of the top-10 (skip to next-best name in another sector)
2. **Blend:** average of daily Ridge and LightGBM percentile ranks
3. Every signal (LightGBM, Ridge, Blend, Momentum) run capped/uncapped, with/without top-5 hindsight winners

### Ranking metrics (1y, 8 folds)

| Metric | LightGBM | Ridge | Blend |
|---|---|---|---|
| Mean rank IC | 0.159 | **0.166** | 0.165 |
| Mean top-5 1y excess | 0.524 | **0.594** | 0.578 |

### Portfolio backtest CAGR (Jan 2018 → Oct 2025, net of 10 bps; SPY +14.1%)

| Signal | Uncapped | Capped | Uncapped ex top-5 winners | Capped ex top-5 winners |
|---|---|---|---|---|
| LightGBM | +41.4% | +36.5% | +24.7% | **+26.2%** |
| Ridge | **+43.0%** | +32.0% | +26.3% | +20.1% |
| Blend | +38.6% | +33.7% | **+28.5%** | +24.2% |
| Momentum 12-1 | +29.4% | +32.7% | +18.0% | +17.9% |

Universe equal-weight: +18.2% (all), +16.4% (ex top-5 winners).

- Cap cuts Tech/AI picks from **63% → 38%**; Energy becomes #2 (~16%).
- Cap costs 5–11%/yr on raw CAGR (it blocks the tech winners). Ridge is hurt most.
- On the tougher "ex top-5 winners" test, **LightGBM capped (+26%)** and **Blend uncapped (+28.5%)** lead; Ridge capped drops to +20%.
- Max drawdown still worse than SPY for all models (−31% to −37% vs −23%).
- Capped models still beat capped momentum by ~6–8%/yr on the ex-winners test.

### Honest read

- **No clear winner.** Gaps of 2–4%/yr across 16 variants and 93 months are within noise. Picking the best row = overfitting to hindsight.
- Ridge's lead is mostly tech concentration: it falls apart when capped.
- LightGBM holds up best under the cap → its signal is less "just buy tech."
- Survivorship bias still inflates every number above.

---

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
