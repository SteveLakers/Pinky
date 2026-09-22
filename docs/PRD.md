# Pinky PRD (Product Requirements Document)

**Version:** 0.1  
**Date:** 2026-09-21  
**Status:** Active — local prototype  
**Owner:** HQ (local)

---

## 1. Problem

Most stock “prediction” tools ask: “Will this stock go up?”  
In a rising market, almost everything can go up — so that question is weak.

**Pinky asks a better question:**  
Will this stock **beat SPY**, and **by how much**, over a chosen time horizon?

---

## 2. Product goal

Build a **local** system that, for a liquid stock and horizon, outputs:

1. Expected **excess return vs SPY**
2. **Probability** of beating SPY
3. An **honest confidence range** (not fake certainty)

Horizons (v1):

| Label | Trading days (approx) |
|-------|------------------------|
| 3 months | 63 |
| 6 months | 126 |
| 1 year | 252 |
| 2 years | 504 |

---

## 3. Who it’s for

- **Primary user:** you (builder / decision-maker)
- **Not for (v1):** public app users, brokers, auto-trading bots

---

## 4. What success looks like

Pinky is successful when:

- Predictions are **relative to SPY**, not absolute price calls
- Evaluation uses **walk-forward + purge** (no random-split cheating)
- LightGBM **beats a simple linear baseline** on agreed metrics
- Results are reported with **honest** caveats (no faked data/metrics)

Detailed pass/fail bar: `docs/EVAL.md`

---

## 5. In scope (v1)

### Data
- Pull daily OHLCV via **yfinance**
- Benchmark: **SPY**
- Helpers (features only, not beat targets): **IWM, VIX, TNX, IRX**
- Universe: liquid majors (currently **58** stocks; may expand)

### Features
- Stock technicals
- Relative strength vs SPY / IWM
- Macro (VIX / rates)
- Multi-period momentum
- Market regime (bull / high-vol)

### Labels
- `excess` = stock forward return − SPY forward return
- `beat` = 1 if excess > 0 else 0  
  (per stock, date, horizon)

### Models
- Per horizon, two heads:
  - return model → expected excess vs SPY
  - beat model → P(beat SPY)
- **8 models total** in v1 (4 horizons × 2)
- Plus **linear baseline** for honesty checks

### Validation
- Walk-forward only
- Purge overlapping label windows
- Metrics: rank quality, top basket vs SPY, probability calibration

### Delivery (v1)
- Local Python pipeline on your Mac
- Saved datasets + trained model artifacts
- Evaluation report before any UI

---

## 6. Out of scope (v1)

- Predicting exact future prices
- Trading illiquid / tiny tickers
- Live auto-trading / broker execution
- Polished public UI before model quality is proven
- Claiming guaranteed profits

---

## 7. Functional requirements

| ID | Requirement |
|----|-------------|
| FR1 | System can refresh raw market data for the configured universe |
| FR2 | System can build a feature matrix with no future leakage in features |
| FR3 | System can build excess/beat labels for all 4 horizons |
| FR4 | System can join features + labels into a train-ready dataset |
| FR5 | System can train LightGBM + linear baseline per horizon/head |
| FR6 | System can run walk-forward evaluation with purge |
| FR7 | System can produce a prediction for a ticker+horizon: excess, P(beat), confidence range |
| FR8 | All metrics and data claims must be reproducible from saved files |

---

## 8. Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR1 | Runs locally; no cloud dependency required for v1 core flow |
| NFR2 | No invented/fake market data |
| NFR3 | Clear docs: architecture, eval checklist, this PRD |
| NFR4 | Git checkpoints before major changes |
| NFR5 | Training only when explicitly requested |

---

## 9. Current status (as of 2026-09-21)

**Done**
- Architecture locked
- Data pull (58 stocks + helpers)
- Feature builder
- Labels vs SPY
- Eval checklist
- Initial git commit

**Not done**
- Train-ready joined dataset
- Walk-forward + purge implementation
- Model training
- Evaluation report
- Prediction API / UI

---

## 10. Milestones

1. **M0 — Design** ✅  
2. **M1 — Data + features + labels** ✅  
3. **M2 — Train-ready dataset + walk-forward/purge** ⏳ next  
4. **M3 — Train + evaluate** (only on explicit go)  
5. **M4 — Prediction interface** (only if M3 passes eval bar)

---

## 11. Risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| Inflated backtest scores | Overlapping labels / random splits | Walk-forward + purge mandatory |
| Mega-cap bias | Universe full of historical winners | Broader liquid universe; monitor beat ~50% |
| yfinance quality limits | Free data can be messy | Prototype only; upgrade data later if results real |
| Overfitting | Too many features / too little honesty | Linear baseline; fold stability checks |

---

## 12. Open decisions

- When to expand beyond 58 names toward full NASDAQ-100 style
- Exact walk-forward fold lengths / retrain cadence
- Exact confidence-range method (quantile model vs conformal vs simple residual bands)
- Whether/when to connect GitHub remote

---

## 13. Related docs

- `docs/ARCHITECTURE.md` — technical design
- `docs/EVAL.md` — how we judge model quality
- `project.md` — live project status + rules
