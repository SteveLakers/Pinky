# Growth round 2 plan (DRAFT)

**Status:** drafted 2026-10-19 (Claude Opus 5.5) while batch 2 trains. **Not approved:** needs the user's OK, and batch 2's verdict first (it decides the base). No code, no runs.

## Why a round 2

- v8 growth: DROP (real − placebo +0.26 / +0.98%/yr; bar +1.0%).
- SHAP (2026-10-16): the models already give growth ~22% of the ranking weight, so "growth weighs too little" is not the problem.
- Data: the fastest 20% of growers have the worst median next year but the most big winners **and** the most crashes. Past growth is a lottery ticket. Round 2 should look for what **separates winners from crashers among growers**, not more growth columns.
- Batch 2 (2026-10-19): margins DROP in every test, so round 2's base = the plain baselines. The fast-grower table shows margin **change** doesn't separate winners (big winners flat at 11–14% across groups), but **being loss-making** does mark the lottery tickets (17% big winners and 18% crashes vs 11% / 9.5% for profitable fast growers). The separator must come from somewhere else: the market's reaction to the news (idea 1) is the strongest candidate.

## Candidate ideas (pick 2–3 before any results)

| # | Idea | Columns | Data | Notes |
|---|---|---|---|---|
| 1 | **Market's reaction to the report** | `ear_3d`: stock return minus SPY, trading days −1…+1 around the latest earnings announcement | events (code 22) + `tr` prices: have it | Classic signal (post-earnings drift). Usable only from day +2 (strictly after the window closes). Announcements start Aug 2004; before that, the filing date (weaker), so 2001–04 is thin → the 2001–08 half test is harder. Overlaps Roadmap 4. |
| 2 | **Sales surprise vs own trend** | `rev_sue`: this quarter's sales growth minus the mean of the previous 4 quarters, divided by their spread | ARQ: have it | No analyst estimates in Sharadar, so "surprise" = vs the company's own trend. Needs 8 quarters of history. |
| 3 | **Multi-year and steady growth** | `rev_cagr_3y` (12-month sales vs 3 years earlier), `rev_up_quarters` (of the last 8 quarters, how many grew vs a year ago) | ART / ARQ: have it | Steady growers vs one-off jumps. |
| 4 | **Rule of 40** | `rule40`: 12-month sales growth + operating margin | have it | SaaS rule of thumb. Only worth it if batch 2 shows margins matter. |
| 5 | **Longer label (2 years)** | none (changes the target) | have it | Not a feature test: a new model target. Dev rows lose a year; overlapping labels make it noisier. Later, separately. |

## Recommendation

- **One new group `growth2` with 4 columns: `ear_3d`, `rev_sue`, `rev_cagr_3y`, `rev_up_quarters`** (ideas 1–3). Few columns on purpose: extra columns cost A ~1%/yr even when real.
- Base = whatever batch 2 keeps for each version (baseline, margins, or growth + margins).
- Test it alone on that base: A and B × seeds 42 / 7 / 99 × real / placebo (`--placebo=growth2`) = **12 runs** (~30 min).
- Same locked keep rule as batch 2 (real − placebo ≥ +1.0%/yr overall and ≥ +0.5%/yr each half; real ≥ the base), plus a leak audit if the gap is > +3%/yr.
- Same checks as batches 1–2 before any run: made-up cases, independent recompute, leak-power test (fake early dates must look better), placebo sanity, old columns identical.
- Info after the runs: SHAP; the fast-grower table, split by `ear_3d` and `rev_sue`.

## Decisions for the user (after batch 2's verdict)

1. Ideas: 1a = 1 + 2 + 3 in one group (my pick) | 1b = only 1 (the reaction) | 1c = other mix.
2. Longer label (idea 5): 2a = later, separately (my pick) | 2b = now.
