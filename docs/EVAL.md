# Pinky evaluation rules

How Pinky judges a model or a new batch of data. Last updated: 2026-10-05. The locked step 3 rule and how to run it: `docs/STEP3_RUNBOOK.md`. Open proposals: `project.md`.

## Honesty rules (every run)

- Walk-forward only, no random splits. Train rows whose label overlaps the test period are purged.
- Point-in-time inputs: the universe uses only data up to each day; company numbers are as first reported and used only after they became public.
- Dead companies stay in: delisting-aware returns, with −30% extra for bankruptcies.
- Trading costs in every backtest (10 bps per side; 25 bps shown too). Trades fill at the next day's close.
- The 2022+ holdout stays untouched until the final test.
- Rules are fixed before results. Every test is logged, including reruns.
- New data is tested against a placebo (the same values shuffled between stocks within each date), on 3 seeds.
- A control run (new data switched off) must reproduce the previous version first.

## What every report shows

- **Ranking:** rank IC (does the model's order match what happened? −1 = backwards, 0 = no information, +1 = perfect), overall and before/after 2009.
- **Where the skill sits:** the score-group table. A buy-only portfolio needs the top group to beat "All stocks"; IC can come from the bottom of the list.
- **Finding winners:** precision@10, @50 and @10% (share of picks that land in the next year's top 10%; random = 0.10), winner capture, and the monthly top-10's big winners and crashes (trailing SPY by more than 50%).
- **Takeover share** of the top picks: calm buyout targets look safe but aren't skill.
- **Backtest:** CAGR net of costs, max drawdown, turnover and months beating SPY, for top-10, top-50 and top 10%, with and without the holding buffer; vs SPY, the equal-weight universe and naive 12-1 momentum.
- **Stress checks:** 2001–08 vs 2009–20; the window's top-5 winners removed; pick share by sector; IC inside each sector.

## Keep rule for new data (locked 2026-10-03)

Judged on LightGBM, top 10% + buffer, 10 bps, monthly, 2001–2020, mean of seeds 42 / 7 / 99. A script applies it (`scripts/step3_verdict.py`), not a person.
- Keep the new data for a version only if real − placebo is at least +1.0%/yr overall **and** at least +0.5%/yr in both 2001–08 and 2009–20.
- Real − placebo above +3%/yr → leak audit before believing it.
- A (rank label) and B (raw return) are decided separately. Both continue unless one trails the other by more than 4%/yr.
- Weekly trading wins only if it beats monthly by at least 1%/yr at 10 bps and is not worse at 25 bps.
- Open proposal (not approved yet): real must also beat the same model without the new data, on the same 3 seeds.

## Scoreboard (shown every time; never decides)

- Beats +8.7%/yr (best so far: v6_pit Ridge, top 10% + buffer)
- At least SPY in both 2001–08 and 2009–20
- At least the equal-weight universe
- Monthly top-10 crash rate at most 10%; big-winner rate vs random (10%)
- LightGBM IC above 0 in both halves

## How big is noise?

- Identical rerun: about 0.2%/yr. Close variants (paired): SE about 0.8%/yr. A vs B: SE about 2%/yr.
- Top-10 CAGRs move by a few %/yr from tiny changes, so judge on IC and the top 10% first.

## Stop and audit if

- An input is dated after the row it's used on, or a label is used as an input.
- A control run doesn't reproduce the previous version.
- One batch looks too good (more than +3%/yr over its placebo).
- Someone wants to judge by IC alone or change a rule after seeing results.

## What success means

Pass the first four scoreboard rows on 2001–2020 with few crashes among the top picks, then confirm it once on the 2022+ holdout.
