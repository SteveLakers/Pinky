# Pinky PRD (product requirements)

**Version:** 0.2 · **Updated:** 2026-10-05 (v0.1: 2026-09-21) · **Owner:** HQ (local) · **Status:** research; no edge over SPY yet

Current state, results and next steps live in `project.md`. This file holds the stable requirements.

## 1. Problem

Most stock tools ask "will this stock go up?" In a rising market almost everything does. Pinky asks: **which stocks will beat SPY over the next year?**

## 2. Goal

- Pick stocks that beat SPY and make a profit after costs.
- Lean toward tech and toward finding future big winners early (the next NVDA or TSLA), but buy any sector (energy, industrials…) when it's the best pick.
- Realistic target: beat SPY by a few % a year, reliably. A target of 10% a month was ruled out as unrealistic.

## 3. User

The owner, for personal research and investing decisions. Not a public app, a broker tool or a trading bot.

## 4. Constraints

- No leverage (the account can't use margin). At most 60% of the picks from one sector.
- Runs locally on this Mac. Sharadar data never leaves it (license); data, models and keys are never committed.
- Training runs only when the owner says `run`. Nothing is pushed to GitHub until the owner says so.

## 5. Requirements

| ID | Requirement |
|---|---|
| FR1 | Download and refresh Sharadar data (prices, company reports, events, delistings) |
| FR2 | Build a daily point-in-time universe of liquid US stocks, dead companies included |
| FR3 | Build a weekly dataset where every input was public on its date |
| FR4 | Train and test walk-forward with purge; never use the 2022+ holdout before the final test |
| FR5 | Backtest monthly portfolios after costs, vs SPY, the equal-weight universe and momentum |
| FR6 | Show the standard checks in every report (`docs/EVAL.md`) |
| FR7 | Test each new data batch against a placebo, with a rule fixed before results |
| FR8 | Every number reproducible from saved files; no invented data or metrics |

Later (Phase 3, only if the model shows a real edge): position sizing, a monthly picks report, a paper-trading log.

## 6. Out of scope

Leverage or options, live or automatic trading, intraday trading, exact price targets, claims of guaranteed profit.

## 7. Success

1. On the 2001–2020 test years: beat SPY and the equal-weight universe in both 2001–08 and 2009–20, with few crashes among the top picks.
2. Then confirm it once on the locked 2022+ holdout.

## 8. Risks

| Risk | Guard |
|---|---|
| Look-ahead leaks | Point-in-time data, news dates, 59 date/leak checks, a leak-power test |
| Survivorship and hindsight | Dead companies included; no hand-picked stock list |
| Luck from testing many ideas | Rules locked before results, placebo, 3 seeds, a one-time holdout |
| Tech concentration | 60% sector cap; results split before and after 2009 |
| Costs and taxes | 10 and 25 bps costs in backtests; taxes not modeled |

## 9. Roadmap

Phase 1 (honest evaluation) and Phase 2 steps 1–3 are done. Next come company-data batches, one at a time: margins, price strength, earnings reactions, reinvestment, quality, insiders and institutions, industry tailwind, valuation, analyst revisions. Phase 3 only if Phase 2 works. Details: `project.md` → Roadmap.
