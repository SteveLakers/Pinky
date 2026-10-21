# Growth round 2 plan (DRAFT)

**Status:** drafted 2026-10-19 (Claude Opus 5.5). **User decisions 2026-10-19 (end of the batch 2 chat):** test the 4 columns **one by one, then all together**; the 2-year label later. Design that follows: section "User decisions" at the bottom. **Not built:** before any code, get the user's OK on the open points there. No code, no runs.

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

## Decisions for the user (asked 2026-10-19)

1. Ideas: 1a = 1 + 2 + 3 in one group (my pick) | 1b = only 1 (the reaction) | 1c = other mix.
2. Longer label (idea 5): 2a = later, separately (my pick) | 2b = now.

## User decisions (2026-10-19)

User: "1, can we do one by one, and than at last everything together, this way we can see which helps and which doesn't. 2a". So the Recommendation above (one group) is replaced by:
- **5 tests**, each its own feature group, all on the plain baselines (A `v9_pit`, B `v9_pit_no-rank_label`):
  1. `ear_3d` alone (price reaction to the latest earnings report)
  2. `rev_sue` alone (sales surprise vs own trend)
  3. `rev_cagr_3y` alone (3-year sales growth)
  4. `rev_up_quarters` alone (quarters of growth out of the last 8)
  5. all 4 together (placebo shuffles all 4 as one block: needs `--placebo` to take several groups, or a 5th group holding all 4)
- Each test: A and B × seeds 42 / 7 / 99 × real / placebo = 12 runs → **60 runs** (~2.5 h, 10 batches of 6).
- 2-year label: later, as a separate test.

**Open points (ask the user before code; my picks first):**
- OK with 60 runs? (Option: run tests 1–4 first, then decide on test 5.)
- Same locked rule for every test (real − placebo ≥ +1.0%/yr and ≥ +0.5%/yr each half; real ≥ baseline). If several KEEP for a version, the highest real mean wins (batch 2's tie-break).
- Honest caveats: 5 tests × 2 versions = 10 chances, so one lucky KEEP is plausible; only the 2022+ holdout settles it. A single column rarely moves a portfolio +1%/yr, so DROP on the singles is likely even if one of them carries real information (its IC and SHAP share are reported as info).
