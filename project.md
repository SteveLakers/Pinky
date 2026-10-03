# Pinky

Local stock-prediction project. **Goal: predict stocks that will perform well and make us profit** — beat the S&P 500 (**SPY**).

- **Favor tech**, and especially **finding future big winners** early ("the next NVDA/TSLA").
- **Still buy other sectors** (energy, industrials, etc.) when they're the best picks — not tech-only.

## ▶ Resume here (new chat: read this first)

Last updated **2026-10-03**. Phase 1 code: `c0cdfe7`. Phase 2 step 1 (v6_pit): `5be6e83`. Showcase + report checks: `cf84035`. Step 2 (v7_pit): `9030d73`. Score-group table: `340e866`. Step 3 plan locked 2026-10-03; **step 3 code + date/leak checks done 2026-10-03 (all pass): `349d0d6`**; v8 dataset built. **Ready to train: follow the runbook below once the user says `run`.**

### Step 3 training runbook (next agent: do this when the user says `run`)

Everything is built and checked; **nothing is trained yet**. Every command below was tested on 2026-10-03 (with stand-ins, no training). Go step by step.

**0. Before anything**
- **Go-ahead:** train only after the user says `run` (or clearly asks you to start training). The plan is locked (Step 3 notes below) → don't re-plan or re-ask; confirm in one line and start.
- **Model:** launching is routine, but judging the results is hard work. If the chat is on Auto, ask the user to switch to the highest model **before launching**, and wait (Rule 10).
- **Locked:** no changes to features, rules or thresholds; no extra seeds or reruns to "fix" a result; no 2022+ data; no push; no showcase / product-page update.
- **Expect modest results:** with honest dates, revenue growth alone barely ranked 3-month returns (leak-power test, IC +0.0018). DROP is a real possibility, and a valid answer.

**1. Pre-flight (~2 min)**

```bash
cd /Users/hqschool/Desktop/Pinky && source .venv/bin/activate
git status --short | grep -v '^??'     # expect no output (tracked files clean)
PYTHONPATH=. python -c "import pyarrow.parquet as pq; s=pq.read_schema('data/sharadar/derived/pit_dataset.parquet'); print('growth ok' if 'rev_yoy_q' in s.names else 'OLD DATASET: STOP')"
PYTHONPATH=. python scripts/check_growth_features.py | tail -1     # optional, ~1 min: expect "59/59 checks passed"
for m in 1y_pit 1y_pit_no-rank_label; do [ -e "models/${m}_v7" ] || cp -Rp "models/$m" "models/${m}_v7"; done     # keep v7's last-fold models (v8 runs overwrite these 2 folders); copies only once
```

- Memory: ~4–5 GB per run; 6 at once fit on this Mac (v7 did). If Activity Monitor's memory pressure isn't green, launch 4 at a time.
- Keep the Mac awake and plugged in during the runs (sleep pauses them).

**2. Launch: 3 batches, one after another (~40 min total)**
- Run each block as **one** shell command in the background (Cursor Shell tool: `block_until_ms: 0`; the default sandbox is fine, v7 ran that way). The block's `wait` ends when its batch ends.
- Every block repeats the 2 setup lines. Log: `artifacts/logs/train_<run>.log`; its last line becomes `EXIT <code>`. Log name = the run name the code builds from the options.

Batch 1: control alone (~8 min). It must reproduce v7, so it tests the whole setup before the 12 real runs.

```bash
cd /Users/hqschool/Desktop/Pinky && source .venv/bin/activate && mkdir -p artifacts/logs
launch() { local n=$1; shift; (OMP_NUM_THREADS=3 PYTHONPATH=. python -u scripts/train_walkforward.py --pit "$@" > "artifacts/logs/train_$n.log" 2>&1; echo "EXIT $?" >> "artifacts/logs/train_$n.log") & }
launch v8_pit_no-growth --without=growth
wait
```

Control check: must print `OK`. If `STOP`: launch nothing more, tell the user, debug first (`.agents/skills/systematic-debugging/SKILL.md`). v7 used the same seed (42) and threads (3), so only tiny noise (~0.2%/yr) is expected.

```bash
PYTHONPATH=. python -c "
import pandas as pd
rows = {r: pd.read_csv(f'artifacts/backtest_stats_1y_{r}.csv').query('signal == \"LightGBM\" and portfolio == \"Top 10% + buffer\"').set_index('period')['cagr_net'] for r in ('v7_pit', 'v8_pit_no-growth')}
d = rows['v8_pit_no-growth'] - rows['v7_pit']
print(pd.DataFrame(rows).map('{:+.2%}'.format).assign(diff=d.map('{:+.2%}'.format)).to_string()); print('OK: reproduces' if d.abs().max() <= 0.005 else 'STOP: control differs > 0.5%/yr')
"
```

(v7_pit reference: all +7.23%, 2001–2008 −1.55%, 2009–2020 +13.52%.)

Batch 2: A = with rank label (6 runs, ~15 min).

```bash
cd /Users/hqschool/Desktop/Pinky && source .venv/bin/activate && mkdir -p artifacts/logs
launch() { local n=$1; shift; (OMP_NUM_THREADS=3 PYTHONPATH=. python -u scripts/train_walkforward.py --pit "$@" > "artifacts/logs/train_$n.log" 2>&1; echo "EXIT $?" >> "artifacts/logs/train_$n.log") & }
launch v8_pit
launch v8_pit_s7 --seed=7
launch v8_pit_s99 --seed=99
launch v8_pit_placebo --placebo
launch v8_pit_placebo_s7 --placebo --seed=7
launch v8_pit_placebo_s99 --placebo --seed=99
wait
```

Batch 3: B = raw return, no rank label (6 runs, ~15 min).

```bash
cd /Users/hqschool/Desktop/Pinky && source .venv/bin/activate && mkdir -p artifacts/logs
launch() { local n=$1; shift; (OMP_NUM_THREADS=3 PYTHONPATH=. python -u scripts/train_walkforward.py --pit "$@" > "artifacts/logs/train_$n.log" 2>&1; echo "EXIT $?" >> "artifacts/logs/train_$n.log") & }
launch v8_pit_no-rank_label --without=rank_label
launch v8_pit_no-rank_label_s7 --without=rank_label --seed=7
launch v8_pit_no-rank_label_s99 --without=rank_label --seed=99
launch v8_pit_no-rank_label_placebo --without=rank_label --placebo
launch v8_pit_no-rank_label_placebo_s7 --without=rank_label --placebo --seed=7
launch v8_pit_no-rank_label_placebo_s99 --without=rank_label --placebo --seed=99
wait
```

**3. Watch progress** (poll every few minutes; don't `sleep` in the shell)

```bash
for f in artifacts/logs/train_v8_*.log; do printf '%-46s folds=%-3s %s\n' "$(basename "$f" .log)" "$(grep -c '\] fold ' "$f")" "$(tail -n 1 "$f")"; done
```

- Done = `folds=20` and last line `EXIT 0`. Near the top, each log prints `[fixes] …` and `[seed] … | placebo: …`; check they fit the run name.
- Harmless: zsh `nice(5) failed` messages (sandbox) and a joblib "physical cores" warning.
- `EXIT 137` = killed, usually out of memory → rerun that run alone (same `launch` line). Other non-zero → read the traceback, fix the cause, rerun only that run, and log it in this file.

**4. Check all 13 runs before the verdict**

```bash
ls artifacts/backtest_stats_1y_v8_*.csv | wc -l     # expect 13
grep -L "EXIT 0" artifacts/logs/train_v8_*.log      # expect no output
for f in artifacts/logs/train_v8_*.log; do n=$(basename "$f" .log); n=${n#train_}; grep -qF "=== Training horizon 1y ($n) ===" "$f" || echo "NAME MISMATCH: $f"; done     # expect no output
PYTHONPATH=. python -c "import json,glob; [print(f, json.load(open(f))) for f in sorted(glob.glob('artifacts/run_config_v8_*.json'))]"     # seed / placebo / fixes fit each name
```

**5. Verdict (~2–10 min; `--weekly` re-runs the backtests with weekly trading)**

```bash
PYTHONPATH=. python scripts/step3_verdict.py --weekly     # also writes artifacts/step3_verdict.md
PYTHONPATH=. python scripts/compare_runs.py v7_pit v8_pit v8_pit_placebo v8_pit_no-growth v7_pit_no-rank_label v8_pit_no-rank_label v8_pit_no-rank_label_placebo
```

How to read the verdict (the script applies the locked rule; don't re-judge by hand):
- Per version (A, B): Real / Placebo / Real − placebo for all, 2001–08 and 2009–20 (mean of 3 seeds), per-seed lines, a paired monthly test, then **Growth: KEEP or DROP**.
- A also gets the control line: it must say "reproduces v7".
- **"ON HOLD"** at the end = control mismatch or a gap > +3%/yr (possible leak). Then don't report a KEEP; tell the user; audit first (rerun `check_growth_features.py`; systematic-debugging skill).
- DROP = that version continues without growth (A → `v8_pit_no-growth`, B → `v7_pit_no-rank_label`; same inputs). The scoreboard, A vs B and the weekly test use these final runs.
- A vs B: both continue unless one trails by > 4%/yr.
- Scoreboard (info only; doesn't decide): beats +8.7%/yr; ≥ SPY in both halves; ≥ equal-weight universe; monthly top-10 crash rate ≤ 10%; big-winner rate (random = 10%); LightGBM IC > 0 in both halves.
- Weekly vs monthly: weekly wins only if ≥ +1%/yr better at 10 bps and not worse at 25 bps.
- Noise yardsticks: identical rerun ~0.2%/yr; close variants (paired) SE ~0.8%/yr; A − B SE ~2%/yr. KEEP means real growth data beat fake data; it does **not** mean we beat SPY.

**6. Report to the user** (plain words, short bullets, answer first)
- Start with: does real growth data help A? B? (KEEP / DROP, one line each).
- Then each final version's yearly return vs SPY (+7.3%) and the equal-weight universe (+8.0%), both halves; big winners / crashes; weekly vs monthly.
- Explain terms with small examples: *placebo* = the same growth numbers shuffled between stocks on each date (fake data that looks real); *gap* = extra yearly return from the real numbers.
- Be honest about noise, and that the 2022+ holdout is still untested.
- Ask open questions in plain text at the end, not in a question form (text written before a form isn't visible to the user).

**7. Wrap up**
- `project.md`: add "Step 3 — growth features (v8)" under Key findings (verdict table + scoreboard); update this Resume section (State / Waiting / Next); log every test, including reruns. `docs/WALKFORWARD_RESULTS.md`: add a v8 section like the v7 one.
- Commit locally. Stage only files you changed (`project.md`, `docs/…`; if code changed, also run `graphify update .`). Key check (prints a count, never the key; must print 0): `git diff --cached | grep -c -F -f <(sed -n 's/^[^=#]*=//p' .env | tr -d '"' | tr -d "'" | awk 'length($0) >= 8') || true`
- Never stage `data/`, `artifacts/`, `models/`, `product/`, `.agents/`, `skills-lock.json`, `.cursor/settings.json`, `.graphifyignore`, `graphify-out/YYYY-MM-DD/`. **No push.**

**8. Then ask the user (start none of these without an OK)**
- **Residual-edge check** (no install; `.agents/skills/residual-edge-analyzer/`): is the portfolio's return more than its SPY / equal-weight / momentum exposure? Input: `artifacts/backtest_periods_1y_<run>.csv`, rows with `signal == "LightGBM"` and `portfolio == "Top 10% + buffer"`: `start` = date, `gross` = strategy, `spy` = market, `universe_ew` = equal-weight; momentum = `gross` of the `Momentum 12-1` rows (same portfolio and dates). Monthly; gross for every column.
- **SHAP** (which features drive LightGBM): installed 2026-10-03, ready. Only last-fold models are saved (trained on data before 2020, tested on 2020).
- **Next batch:** Roadmap batch 2 (margin expansion), same protocol (placebo, 3 seeds, propose the keep-rule before any run).

**Open user decisions (raised 2026-10-03, not answered yet)**
- Save **every** fold's model (SHAP across all years, not just 2020)? Needs a small `train.py` change **before** training (~9 MB per run; last-fold models are ~440 KB). If the user doesn't ask, train as built.
- Run the residual-edge check after the runs?
- Push to GitHub?
- Add info-only lines to the step 3 report: real − placebo gap **before costs**, and turnover? The placebo is reshuffled every week (`shuffle_growth_within_date`), while real growth numbers mostly change once a quarter, so trading costs could tilt the gap (v7 cost drag for LightGBM top 10% + buffer: 0.37%/yr; 0.54%/yr in 2001–08). The saved stats already have `cagr_gross` and `avg_monthly_turnover`. Doesn't change the locked rule.

### State and history

**State**
- Phase 1 (honest evaluation): **done**.
- Phase 2 **step 1 — new yardstick (v6_pit): done.** Same price-only models; 2020 now tested; holding buffer; top-50 / top 10% portfolios. Still **no reliable edge** (see Key findings).
- **Showcase updated to v6_pit: done** (2026-09-27). Leads with the honest result; every number is computed from saved artifacts; text checked against the data.
- **Every report now includes both checks the user asked for:** share of top picks acquired within 6 months (top-10 and top 10%, vs base rate) and results before/after 2009 vs SPY (`REPORT_SPLIT_YEAR` in `config.py`).
- **Phase 2 step 2 — four model fixes (v7_pit): done**, plus one ablation per fix and a control (all off = v6). Results in Key findings and `docs/WALKFORWARD_RESULTS.md`. Short version: IC doubles, crashes drop, **still no edge over SPY**; no run passes the bar. The **rank label** turns models into calm, low-volatility pickers (few big winners), which clashes with the goal.
- **Public product page: done (2026-09-30, not committed yet).** `product/index.html`: plain-language intro for non-coders (goal, method, honest-testing rules, findings, next steps, FAQ). No secrets: no data vendor, model names, cost level, thresholds, sector cap, file paths or repo links. Numbers are **hand-copied** (v6_pit, v7_pit, v7 no-rank_label, v4/v4_ex5, universe counts), not built by a script → when the user asks for an update (not before), re-check every number by hand, then redeploy. View: `cd product && python3 -m http.server 8766`.
- **Product page is live (2026-09-30, short-term):** https://pinky-research.vercel.app (Vercel Hobby, free; CLI logged in on this Mac). Headline changed to "AI vs. the S&P 500" on 2026-10-02 (the old question now opens the intro). Share only this link; per-deploy URLs are login-protected. **Redeploy from a copy outside git:** deploying from `product/` now gets blocked on Hobby ("commit author doesn't have permission"), because the CLI attaches the local commit author. Run from the repo root: `rm -rf /tmp/pinky-deploy && mkdir -p /tmp/pinky-deploy/.vercel && cp product/index.html product/.vercelignore /tmp/pinky-deploy/ && cp -R product/fonts /tmp/pinky-deploy/ && cp product/.vercel/project.json /tmp/pinky-deploy/.vercel/ && (cd /tmp/pinky-deploy && npx vercel@latest deploy --prod)`. If the CLI says "Not authorized", run `npx vercel@latest login` again (needed after 2 days). Take down: `npx vercel@latest project remove pinky-research`. `product/.vercelignore` limits the upload to `index.html` + `fonts/`; `product/.vercel/` (project link) is gitignored by `product/.gitignore` — never commit it.
- **Score-group table in every report: done (2026-10-02).** New report section "Where the ranking skill sits" (`train._score_group_lines`, `metrics.score_group_table`): per weekly score decile, plus the top-10 names and all stocks, the share beating SPY and the median and mean 1y excess. Saved as `artifacts/score_groups_<h>_<run>.csv`. Reports for `v7_pit` and `v7_pit_no-rank_label` were rebuilt with `--report-only` (the rest of each report is unchanged).
  - **Neither step-3 starting point has a top group that beats the average stock.** All stocks: 47.7% beat SPY, mean +1.6%. v7 LightGBM top 10%: 49.0%, mean +0.4%. No-rank-label LightGBM top 10%: 46.3%, mean +1.2%. Momentum's top-10: 36.4%, median −16.1%.
- **User decisions (2026-10-02):**
  1. Step 3 runs on **both** return targets (rank label and raw). Before running step 3, propose a pick rule and get the user's OK, so the choice isn't made after seeing results.
  2. Showcase and product page: update **only when the user says**.
  3. Score-group table: approved, done (above).
  4. `product/` stays **uncommitted** (user said no).
- **User decisions (2026-10-03):** step 3 plan approved. Use **announcement dates** (not later SEC filings) when a matching earnings event exists; test weekly vs monthly trading after the model has news; keep-rule is the **middle** bar (real beats fake by ≥ 1%/yr overall and ≥ 0.5%/yr in each half), **three seeds each** (42 / 7 / 99); A and B both continue unless one trails by > 4%/yr. Do **not** train until the user says `run`.
- **User asked (2026-10-03) whether the new add-ons help training:** they don't change training; they help check results afterwards (verification, debugging, residual-edge, SHAP). The user then asked for a detailed handover so the next agent can start training → the runbook above.
- **User (2026-10-03, later):** wants **very short replies by default** (saves tokens); more detail only when asked. SHAP installed (see Repo layout).
- **Waiting on the user:** **`run`** (training; all checks passed); push permission; the open decisions at the end of the runbook (per-fold models, residual-edge, gap-before-costs lines).
- **Next:** user says `run` → runbook above (control → A → B → checks → verdict → report → docs + local commit). Showcase rebuild only when the user says.
  - **Step 3 build (done 2026-10-03):** `pinky/fundamentals.py` (growth features), wired into `pit_dataset.py` (dataset rebuilt: same 2,932,585 rows, 21 features). `train.py`: `VERSION = "v8"`, `growth` in `MODEL_FIXES`, `--placebo`, `--seed=N`, `pit_training_frame()`, monthly returns saved as `artifacts/backtest_periods_1y_<run>.csv`. `backtest.run_backtest(rebalance="weekly")`. `compare_runs.py` adds equal-weight universe and monthly top-10 big-winner / crash rows. New scripts: `scripts/check_growth_features.py` (59 date/leak checks) and `scripts/step3_verdict.py` (the locked rule; refuses to run until all 13 runs exist). v7 dataset backup: `data/sharadar/derived/pit_dataset_v7.parquet` (checksum-verified copy).
- 24 local commits are **not pushed** (check: `git log origin/main..main --oneline`). User said: don't push yet.

**User decisions (2026-09-26)**
- Phase 2 model fixes: **all four approved** (list under Roadmap).
- Evaluation fixes approved and done in v6_pit: holding buffer, 2020 test block, top-50 / top 10% reports.
- User wants **company data features**, not just price — that is the core of Phase 2.
- Build **step by step** so we can tell what helps. Showcase update **after step 1** (done). GitHub: **don't push yet**.
- Add to every future report (2026-09-27): takeover share of top picks, and 2009–2020 vs SPY (done in `train.py`).
- User confirmed the highest model for Phase 2 (2026-09-26). New chats: ask again before hard work (Rule 10).

**Step 2 notes (model fixes — done)**
- `train.MODEL_FIXES` = `rank_label`, `rank_features`, `young`, `size`; pit runs use all unless `--without=a,b` (run tagged `no-<fix>`). Legacy runs use none.
- Dataset (`pit_dataset.py`) now keeps stocks with ≥ ~1 month of prices (`SHORT_FEATURES`), adds `history_1y` and `log_mcap` (Sharadar DAILY; verified point-in-time). v6 dataset backup: `data/sharadar/derived/pit_dataset_v6.parquet`.
- Rank features run once before the walk-forward (`preprocess.cross_section_rank`; per-day only, so no leak). Each run saves `artifacts/run_config_<run>.json` (fixes, stock count) for `--report-only`.

**Step 3 notes (company data batch 1 — plan locked 2026-10-03)**

**A** = with the rank label (calm-stock target; baseline `v7_pit`). **B** = without it (raw return, big-winner target; baseline `v7_pit_no-rank_label`). Both get the growth features.

1. `pinky/fundamentals.py`: load SF1 **ARQ + ART only** (never MR*). Drop filings dated < 10 days after period end (no real 10-Q is that fast: data errors; 121 ARQ / 182 ART reports, 0.02%; tightened 2026-10-03 during the date checks, before any results); keep the **first-filed** row per (ticker, calendardate).
2. **News date** (user chose announcement dates now, not filing dates): Sharadar events code `22` (earnings announcement) if it falls after period end, at least 10 days later (skip previews), and no later than the SEC filing. An announcement belongs to the **newest** quarter that ended ≥ 10 days before it (fixes catch-up filings). If several match, use the **latest** (can only be late, never early). No match → filing date. Events start Aug 2004; earlier years stay on filings. A report published after a newer one (late catch-up filing) never replaces the newer one.
3. Features (6): `rev_yoy_q`, `rev_accel`, `gp_yoy_q`, `rev_yoy_ttm`, `days_since_news`, `has_growth`. YoY matches `calendardate` with `MonthEnd` math (both sides > 0; prior news date ≤ current). Attach with `merge_asof(..., allow_exact_matches=False)` so numbers are used only on dates **after** the news date. Stale: quarterly > 365 days since period end → missing; TTM > 550 days → missing.
4. `MODEL_FIXES` adds `growth` (`--without=growth` = v7 inputs). `VERSION` = v8. Back up `pit_dataset.parquet` as `pit_dataset_v7.parquet` before rebuild.
5. **Locked keep-rule** (judge LightGBM, Top 10% + buffer, 10 bps, 2001–2020; do not change after seeing results):
   - Real vs **placebo** (growth columns shuffled within each date, block of 6). Keep growth on a version if real − fake ≥ **+1.0%/yr overall** and ≥ **+0.5%/yr in both 2001–08 and 2009–20**. Average **3 seeds** (42, 7, 99).
   - Decide A and B separately. If growth does not help a version, that version continues **without** it.
   - A vs B: **both continue**. Drop one only if it trails by **> 4%/yr**.
   - Weekly vs monthly (same predictions, no extra training): weekly wins only if it beats monthly by ≥ 1%/yr after 10 bps **and** does not lose at 25 bps. Default reports stay monthly until that test.
   - Scoreboard only (does not decide): > +8.7%/yr; ≥ SPY in both halves; ≥ equal-weight universe (+8.0%); crashes ≤ 10%; IC > 0 in both halves. **IC > 0.052 is retired** as a gate (it grades the whole list and would knock out B).
   - No feature tweaks after results. Log every test. 2022+ holdout untouched. Jump > +3%/yr vs fake → leak audit before believing it.
6. Training (only after the user says `run`): 13 runs. A: 3 seeds real + 3 seeds placebo; B: the same six with `--without=rank_label`; control `--without=growth` (→ `v8_pit_no-growth`; must reproduce `v7_pit` within 0.5%/yr; inputs proven identical). Exact commands, checks and verdict: **Step 3 training runbook** at the top of this file.
7. **Date/leak checks (2026-10-03, `scripts/check_growth_features.py`, 59/59 pass; logged per the integrity rule):**
   - Made-up cases for every date rule (previews, catch-up filings, amendments, same-day rows, staleness): all pass.
   - Dataset vs v7 backup: same rows in the same order, all 37 old columns identical, exactly the 6 growth columns added. The growth-off model frame equals the v7 frame for A and B (`pit_training_frame`), so the control gets v7 inputs exactly.
   - Real data: every announcement ≥ 10 days after period end and ≤ the filing; every number used only on rows strictly after its news date; nothing older than 365 / 550 days; the quarter shown never goes backwards. Median: news 41 days after period end, announcement 2 days before filing.
   - Independent plain-Python re-implementation: 2,758 sampled rows (303 stocks) match exactly.
   - Volume (100k quarters, filing ≥ 7 days after announcement): spike on announcement day 0–1 median 2.57× normal (65% > 2×) vs filing day 1.20× (18%). Median profile peaks on days 0–1 (1.82×, 1.94×), not later → dates are not early.
   - Hand checks: NVDA (Q3 FY17, +53.6% YoY, appears 2016-11-11, day after the release), AAPL (Q4 FY16, −9.0%, appears 2016-10-28), MSFT 2002 (filing date, appears after 2002-04-30).
   - Coverage: 93–96% of rows have growth from 2001 (75% in 1999, 87% in 2021: many new listings). From 2005, ~85% of latest quarters are dated by announcement.
   - Correlations (per-date ranks): highest growth pair 0.84 (`rev_yoy_q` / `gp_yoy_q`), below the 0.92 drop threshold; max link to an old feature 0.28 (momentum) → new information.
   - **Leak-power test** (dev rows 2005+, label = 3-month return vs SPY): rank IC of `rev_yoy_q` with real dates **+0.0018**; with fake early dates (quarter end + 1 day) **+0.0168**; placebo **+0.0002**. So a leak would show up clearly, and ours doesn't. Caveat: with honest dates, revenue growth alone barely ranks 3-month returns, so expect small gains if any.
   - Placebo: same values per date, moved between stocks as six-value blocks (99.8% of rows end up with a different block), unrelated to real values (rank corr +0.0002).
   - Backtest code unchanged for monthly: rebuilt v7_pit stats match the saved ones (max diff 2e-16). v7 weekly vs monthly (LightGBM top 10% + buffer): +7.29% vs +7.23% at 10 bps, +6.36% vs +6.63% at 25 bps → monthly (same as the earlier test).

**Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr)**
- Ridge rank IC **0.052**; Ridge top 10% + buffer **+8.7%/yr** (+7.8% at 25 bps); Ridge top-10 + buffer +8.3%/yr.
- Also check: 2009–2020 vs SPY (Ridge trails: +12.6% vs +14.5%/yr) and the takeover share of top picks (Ridge top-10: 25%; base rate 2.2%).
- Per-portfolio numbers: `artifacts/backtest_stats_1y_v6_pit.csv`. Side by side: `PYTHONPATH=. python scripts/compare_runs.py v6_pit v7_pit`.
- v7_pit (step 2) passes the IC part (0.056–0.063) but not the portfolio part (best top 10% + buffer: LightGBM +7.2%). Top-10 CAGRs are noisy by a few %/yr: judge on IC and top 10% first. Caveat: IC can come mostly from sorting the bottom of the list (v7's did), so a higher IC alone doesn't mean better picks. Check the report's score-group table: does the top group beat the "All stocks" row?
- Never touch the 2022+ holdout until the final test. Caveat: the old 128-stock tests (2018 → Oct 2025) already covered 2022–2025, and the 60% sector cap was picked after seeing them, so the holdout is clean for the pit models but not fully unseen by us.

**Data facts for Phase 2**
- Fundamentals ARQ: filing dates 1993 → 2026, 17,045 tickers, revenue filled 97% (ART 92%).
- 9,492 of the 10,043 v6 dataset stocks (95%) have ARQ rows. The v7 dataset has 10,902 stocks (young stocks added).
- `daily.parquet` columns: `marketcap`, `ev`, `evebit`, `evebitda`, `pb`, `pe`, `ps`.
- Pinky pulls 7 Sharadar tables (`sharadar.BULK_TABLES`: tickers, stocks, fundamentals, sp500, actions, daily, events). Not downloaded yet: `metrics` (access confirmed, ~1.4 MB). No insider or institution tables: check plan access before Roadmap batch 7.

**When you finish a chunk of work:** update this Resume section so the next chat can pick up.

## Gotchas (learned the hard way)

- Sharadar CSVs must be parsed with `sharadar.CSV_KW` (`keep_default_na=False`). Otherwise the ticker "NA" becomes blank.
- `fiscalperiod` is text ("2009-Q4"), not a date.
- Fundamentals: use **AR\*** dimensions only (dated by SEC filing date). **MR\*** rows are dated at quarter-end → ~2.5 months of future leak.
- Any dataset column that doesn't start with a prefix in `dataset.LABEL_PREFIXES` is treated as a **model input**. New label columns must get a prefix there, or they leak.
- Rows are weekly → always pass the daily `calendar` to `iter_walk_forward_folds`. Otherwise "252 days" silently becomes 252 weeks.
- Forward returns and backtests must use the `tr` panel (delisting-aware), never raw `closeadj`.
- pandas `to_numpy()` can return a read-only array → use `np.array(..., copy=True)` before writing into it.
- Filtered Sharadar API queries return only the last year unless you pass `from_=`.
- Sharadar tickers are unique (reused symbols get a suffix, e.g. `CNO1`).
- `pd.merge_asof` needs both frames sorted by the `on` key **globally** (not ticker-first), else "left keys must be sorted". Among equal keys it takes the last right row → sort the right side by (news date, period) so the newest quarter wins.
- Quarter math: `pd.DateOffset(months=3)` maps Sep 30 → Dec 30 (wrong); use `pd.offsets.MonthEnd(n)`.
- SF1 has a few reports "filed" 0–9 days after period end (data errors); `fundamentals.first_filed` skips them.
- Earnings events (code 22) start 2004-08-23; ADRs (6-K filers) have none → filing dates.
- ~195 of 2.8M rows show one-day jumps > 100% on tiny stocks (likely split glitches); left in for the baseline.
- Size: panels are 7,227 days × 17,340 stocks. Dataset build peaks ~14 GB RAM (machine: 48 GiB RAM = 51.5 GB, 18 cores, 1.3 TB free). A training run needs ~4–5 GB.
- Run names come from the code (`train.run_all` builds them from the options), not from the log file name. Example: the v7 control was logged as `train_v7_pit_control.log`, but its files are named `v7_pit_no-rank_label_no-rank_features_no-young_no-size`. The step 3 runbook uses log name = run name and checks it.
- Untracked `data/reference/` comes from another chat — leave it alone.
- `graphify update` backs up the previous graph into a dated folder (`graphify-out/YYYY-MM-DD/`, untracked). Don't commit them.
- graphify does not skip dot-folders: third-party code there (e.g. `.agents/`) gets indexed unless it's listed in `.graphifyignore`.
- Cursor's sandbox blocks `pip install` into `.venv` ("Operation not permitted") → run pip with full permissions. In the sandbox, matplotlib warns that `~/.matplotlib` isn't writable (harmless; it uses a temp folder).
- API key safety: never print `.env`. Before a commit, check the staged diff with a count-only `grep -c -F` for the key.

## Rules (always on)

Apply at all times unless the user says otherwise. Mirrored in `.cursor/rules/`.

1. **Never lie.** Never fake data, results, or information.
2. **Double-check before answering.**
3. **Be concise.** Straight to the point, no filler. **Very short by default** (user, 2026-10-03: saves tokens); more detail only when asked.
4. **No exceptions** unless the user says so.
5. **Auto-update `project.md`** after big features/updates, and as the project changes.
6. **Challenge bad ideas.** If the user is wrong or a better way exists, say so.
7. **Stress-test the approach.** If it isn't the best, say so. The user won't be mad.
8. **Hunt for mistakes** in statements, plans, and requests. Report them right away.
9. **Every new chat:** read `project.md` first.
10. **HIGHEST MODELS — top priority, all agents.** Go heavy on the highest models for reasoning, planning, decisions, and thinking. Token cost doesn't matter. Never downgrade to save cost (`.cursor/rules/strong-models.mdc`).
    - User runs Cursor on **Auto**; agents can't change the main model → **before a hard task, or if a task turns hard mid-way: STOP, ask the user to switch to the highest model, and wait** (unless the user says continue).
    - Hard sub-work → subagents on the strongest model; copy this rule into every subagent prompt.
11. **Communication:** simple sentences, bullet points, **ask before large decisions/changes**.
12. **Graphify first:** `graphify query/explain/path` before exploring code; `graphify update .` after code changes.

Also: **no push** until the user says; **training only when the user says**.

## User goals & expectations

- Wants a model that's genuinely smart at finding stocks that perform well; catching the next NVDA/TSLA would be ideal.
- Likes tech most, but also buys other sectors (e.g., energy) — not tech-only.
- First asked for ~10%/month — explained that's unrealistic. Realistic aim: beat SPY by a few %/yr, reliably.
- Accepts a bit more risk (60% sector cap), **no leverage** (account can't). Bullish on tech.
- Data budget flexible (paying for Sharadar). Lots of time and compute.
- New to quant terms: explain metrics in plain words with small examples. Rank IC explained 2026-10-02 (one score per week for the model's whole ranked list; −1 = exactly backwards, 0 = no information, +1 = perfect order; grades order, not size, and not single stocks or just the top picks).

## Key findings

### Four model fixes — v7_pit + ablations (2026-09-27)

Same price features; same yardstick. SPY +7.3%/yr (2009–2020 +14.5%). Control (all fixes off) reproduces v6_pit.

| | v6_pit | v7_pit | v7 without rank label |
|---|---|---|---|
| Rank IC Ridge / LightGBM | 0.052 / 0.015 | 0.056 / 0.063 | 0.024 / 0.031 |
| Top 10% + buffer, LightGBM (2009–2020) | +4.3% (+8.9%) | +7.2% (+13.5%) | +5.8% (+11.6%) |
| Top 10% + buffer, Ridge (2009–2020) | **+8.7%** (+12.6%) | +6.8% (+11.8%) | +5.2% (+10.4%) |
| LightGBM top-10: big winners / crashes (random 10% / ~7%) | 14.7% / 18.5% | 3.9% / 2.3% | 13.4% / 8.0% |

- **Still no edge over SPY; no run passes the bar.** Best broad portfolio: LightGBM top 10% + buffer +7.2% vs SPY +7.3%.
- **Rank label = the big lever:** IC ~doubles, but picks become calm low-volatility stocks (median vol 14–16% vs 33%) that rarely crash **and rarely win big** — against the goal.
- **Without the rank label**, LightGBM is the best winner-finder so far (13.4% big winners, crashes 18.5% → 8.0%).
- **v7's IC comes mostly from the bottom of the list** (checked 2026-10-02 on saved v7 predictions; 1y excess vs SPY by weekly score decile). LightGBM bottom 10%: median −8.5%, 42.5% beat SPY. Top 10%: 49.0% beat SPY vs 47.7% for all stocks, but mean +0.4% vs +1.6% (few big winners). Ridge's top-10: only 44% beat SPY. Higher IC does not mean better top picks; for a buy-only portfolio, judge the top of the list.
- Rank features beat z-scores on robustness: z-scores bring back takeover targets (41% of Ridge's top-10). Young stocks: small IC gain. Size: helps LightGBM.
- Full table + ablations: `docs/WALKFORWARD_RESULTS.md`.

### New yardstick — v6_pit (2026-09-26)

Same price-only models as v5_pit. 2020 now tested (20 folds, backtest Jan 2001 → Jan 2021), holding buffer, wider portfolios. SPY +7.3%/yr, equal-weight universe +8.2%/yr.

| CAGR net of 10 bps (25 bps) | LightGBM | Ridge | Momentum 12-1 |
|---|---|---|---|
| Top-10 + buffer | −6.2% (−8.5%) | +8.3% (+5.9%) | −1.6% (−2.7%) |
| Top-50 + buffer | +2.0% (+0.2%) | +7.7% (+5.9%) | +3.6% (+2.6%) |
| Top 10% + buffer | +4.3% (+3.1%) | **+8.7% (+7.8%)** | +7.0% (+6.2%) |

- **Still no reliable edge.** Ridge's lead is all from 2001–2008. **2009–2020: Ridge (top 10% + buffer) +12.6%/yr vs SPY +14.5%.**
- **Ridge's top-10 are mostly takeover targets:** 25% get acquired within 6 months (base rate 2.2%). Calm, steady "pending deal" stocks = accidental merger arbitrage, not winner-finding.
  - Those bought-out picks: median 63-day volatility 5.5% (other picks 25.5%), 0% crash (other picks 11%), mean 1y excess vs SPY only +0.2%. Safe, but no edge.
- **2020 broke every model:** rank IC −0.17 to −0.22 that year. Mean Ridge IC 0.066 → 0.052.
- **Buffer:** big help for top 10% (turnover 103% → 45%/month); little help for top-10, because top picks fall to a median rank of ~168 within a month (the signal jumps around).
- Ridge finds fewer big winners than random (precision 0.06–0.08 vs 0.10). Momentum finds the most (0.15–0.17) but concentrated momentum crashes (−84% to −91% drawdowns).
- Full report: `artifacts/walkforward_summary_v6_pit.md`. History: `docs/WALKFORWARD_RESULTS.md`.

### Honest baseline — v5_pit (2026-09-26)

Point-in-time liquid US universe, delisted stocks included, 1y signal, monthly top-10, 10 bps, **Jan 2001 → Feb 2020** (19 test years; 2022+ holdout untouched).

| Signal | CAGR | Max DD | Precision@10 | Winner capture |
|---|---|---|---|---|
| SPY | +6.9% | −52% | — | — |
| Equal-weight whole universe | +7.5% | — | 0.10 (random) | 0.005 (random) |
| Ridge | +7.6% | −47% | 0.08 | 0.019 |
| Blend | +0.6% | −68% | 0.10 | 0.028 |
| LightGBM | **−8.0%** | −87% | 0.15 | 0.027 |
| Naive 12-1 momentum | −1.4% | −84% | 0.17 | 0.048 |

- LightGBM picks volatile "lottery tickets": 1.5× random chance of a top-10% winner, but 2.6× the normal chance of losing > 50% vs SPY. **Price data predicts how much a stock moves, not which way.**
- Ridge picks calm, rising stocks → about market return, smaller drawdowns. **Correction (found in v6):** many of those calm picks are takeover targets (25% of Ridge's top-10 acquired within 6 months vs 2.2% base rate) — safe, not skill.
- 2020 was not tested in v5 (last partial year dropped). v6 added it: 2020 broke every model.
- The 60% sector cap barely matters here (picks are already spread out).
- Full report: `artifacts/walkforward_summary_v5_pit.md`. History: `docs/WALKFORWARD_RESULTS.md`.

### Old 128-stock results (inflated by survivorship + hindsight)

- 2018–2025: LightGBM +41%/yr vs SPY +14%. With NVDA/SMCI/TSLA/PLTR/AVGO removed: +19%. Precision@10 0.32–0.34.
- Details in `docs/WALKFORWARD_RESULTS.md` (v1 → v4 ex5).

## Decisions

- **Data:** Sharadar Core US Equities Bundle — active. Direct API + bulk tables. Key in `.env` (gitignored, never print). License: never share or commit the data.
- **Universe (`pinky/universe.py`):** each day, price ≥ $5 and 21-day avg dollar volume ≥ $5M (nominal $). Common stock + ADRs + Canadian; no preferreds, secondary share classes, or SPACs (SIC 6770); NYSE / NASDAQ / NYSE American only. → **~1,200–2,850 stocks/day (yearly averages), 11,561 distinct** (1998–2026).
- **Delistings:** exit value reinvested in SPY. Bankruptcy / liquidation / regulatory delistings also take **−30%** on the last price (Shumway 1997).
- **Dataset rows:** weekly (every 5th trading day); folds use the daily calendar. Since v7 (`young` fix), stocks are scored after ~1 month of prices; missing long-window features get the day's middle value. v5/v6 needed 1y of history.
- **Sectors:** Sharadar sectors (current classification) for the cap. The custom "Tech/AI" bucket only applies to the old 128-stock universe.
- **Risk:** no leverage. Sector cap 60%.
- **Main signal:** undecided. Step 3 keeps both A (rank label) and B (raw return); drop one only if it trails by > 4%/yr.
- **Locked holdout:** `HOLDOUT_START = 2022-01-01`. Dev runs only use rows whose label ends before it (`train.dev_rows`). Score the holdout once, at the very end.

## Roadmap

**Phase 1 — honest evaluation: done (2026-09-25/26).**
- Proved the old results were inflated: removing NVDA/SMCI/TSLA/PLTR/AVGO from train + test cut +41%/yr to +19%.
- Free data covered only ~22% of stocks that left the S&P 500 → switched to paid Sharadar. (Re-check 2026-09-30: the share depends on the definition — 29.9% have any free data, 19.3% have data before they left, 11.0% cover their whole membership. The product page just says "missing most".)
- Scoring tools: top-10% label, precision@10, time-weighted winner capture (first version was flawed — random scored 0.62), locked 2022+ holdout.
- Pipeline: Sharadar pull → daily point-in-time universe (dead stocks included) → delisting-aware returns → weekly dataset (2.83M rows, 10,043 stocks, 1999–2026) → `--pit` training (19 test years, 2001–2019).
- Result (v5_pit): **no edge** — Ridge +7.6%/yr ≈ SPY +6.9%, LightGBM −8.0%.
- Bugs caught: bankrupt stocks counted as 0% in the backtest, ticker "NA" read as blank, `fiscalperiod` would be wiped, `top_` label leak risk, weekly rows breaking fold day counts (see Gotchas).

**Phase 2 step 1 — evaluation fixes: done (v6_pit).** Holding buffer, 2020 test block, top-50 / top 10% reports.

**Phase 2 model fixes (from Phase 1 findings — all four approved 2026-09-26):**
- Train on each day's **return rank** instead of raw return (a few +5,000% stocks pull LightGBM toward lottery tickets).
- Scale features by **daily rank** instead of z-score (one bad tick can squash a whole day).
- Let stocks **without 1y of history** be scored (so a new PLTR isn't invisible for a year).
- Add **size** (market cap) as a feature.

**Phase 2 — company data**, added in batches; keep only what beats the baseline:
1. **Growth + revenue acceleration** ← first
2. Margin expansion
3. Price strength (momentum, 52-week-high proximity, vs sector)
4. Earnings reactions / surprises
5. Reinvestment (R&D/revenue, ROIC)
6. Quality / safety (debt, cash burn, accruals, dilution)
7. Insiders + institutions
8. Industry tailwind
9. Valuation (context only — don't screen out growth)
10. Analyst revisions (expensive; later)

**Phase 3 — only if Phase 2 works:** position sizing, monthly picks report, live paper-trading log.

## Backtest defaults

- Monthly rebalance, equal weight, **10 bps per side** (25 bps re-prices the same trades via `backtest.with_cost`).
- Portfolios: top-10, top-50, top 10% of each date's stocks; each with and without the **holding buffer** (keep a holding while it ranks in the top 3× N, `BACKTEST_BUFFER_MULT`). Main comparison rows: **top-10 + buffer** and **top 10% + buffer**.
- Sector cap 60% of picks (`BACKTEST_MAX_SECTOR_SHARE`) on all rows except "v5 rules". Signal at day D close, trade at D+1 close.
- Walk-forward: 1-year test folds; the last fold may be shorter (≥ 63 days, `WF_MIN_LAST_TEST_DAYS`) so 2020 is tested.
- Signals compared: LightGBM, Ridge, Blend (avg daily rank), naive 12-1 momentum. Settings: `pinky/config.py` (`BACKTEST_*`, `WF_*`).

## Repo layout

- `pinky/config.py` — universe rules, paths, backtest settings, `HOLDOUT_START`, `DELIST_RETURN_PERFORMANCE`
- `pinky/sharadar.py` — Sharadar API: bulk download → parquet, small queries (key never printed)
- `pinky/universe.py` — point-in-time universe panels, delisting-aware `tr` panel, sectors, SPY, `backtest_prices()`
- `pinky/pit_dataset.py` — weekly features + labels on the point-in-time universe (13 price features + `history_1y` + `log_mcap`)
- `pinky/preprocess.py` — per-day z-score or percentile rank + correlated-feature drop
- `pinky/walkforward.py` — expanding walk-forward folds + label purge (`calendar` param)
- `pinky/train.py` — Ridge / LightGBM / Blend, report, `pit=True` and `exclude` runs, `dev_rows`
- `pinky/metrics.py` — IC, top-N, precision@k, winner capture, score groups, calibration
- `pinky/backtest.py` — monthly top-N / top-fraction backtest, costs, sector cap (`sectors` param), holding buffer, stress tests
- Legacy (128 stocks, yfinance): `data_pull.py`, `raw_io.py`, `features.py`, `labels.py`, `dataset.py`
- `scripts/` — `pull_sharadar`, `train_walkforward`, `compare_runs`, `build_showcase`, plus legacy build scripts
- `showcase/index.html` — one-page visual (offline), built from v6_pit artifacts by `scripts/build_showcase.py`.
- `product/index.html` — public product page for non-coders (static, hand-written, inline SVG charts, no build step); `product/fonts/` = Newsreader + Libre Franklin (OFL licenses included); `product/.vercelignore` = Vercel upload allowlist; `product/.gitignore` keeps `.vercel/` and `.env*` out of git.
- `data/sharadar/` (~6 GB, gitignored, never share) — tables (`*.parquet`), `zips/`, `panels/` (Date × Ticker), `spy.parquet`, `derived/pit_dataset.parquet`
- `artifacts/`, `models/` — outputs (gitignored). Per run: `walkforward_summary_<run>.md`, `walkforward_metrics_<run>.csv`, `oos_preds_1y_<run>.parquet`, `backtest_stats_1y_<run>.csv`, `backtest_periods_1y_<run>.csv` (monthly returns, v8+), `score_groups_1y_<run>.csv`, `run_config_<run>.json`. Training logs: `artifacts/logs/train_<run>.log` (last line `EXIT <code>`). Step 3 verdict: `artifacts/step3_verdict.md`. `models/1y_<tag>/` holds only the **last fold's** models per tag (~440 KB; `1y_pit` = latest full pit run, overwritten; ablations get `1y_pit_no-<fix>`, seeds / placebo get their own folders).
- `docs/` — `WALKFORWARD_RESULTS.md`, `ARCHITECTURE.md`, `PRD.md`, `EVAL.md`
- `AGENTS.md`, `.cursor/rules/` — agent instructions. `graphify-out/` — knowledge graph.
- Agent add-ons (2026-10-02; untracked, don't commit). Skills in `.agents/skills/` (listed in `skills-lock.json`):
  - `residual-edge-analyzer`: does a portfolio beat SPY / equal-weight / momentum beyond their exposure? Needs one dated monthly CSV (strategy + baselines on each row, same cost basis). Since v8, every run saves `artifacts/backtest_periods_1y_<run>.csv` (per month: net, gross, SPY, equal-weight universe, for every signal × portfolio, incl. Momentum 12-1) → pivot it; older runs get the file via `--report-only`. Use gross for all columns (SPY and equal-weight carry no costs).
  - `shap`: which features drive LightGBM. **Installed 2026-10-03** (user asked): `shap[plots]==0.52.0` into the existing `.venv` (Python 3.12.0), also in `requirements.txt`. 29 packages added (shap, numba, llvmlite, slicer, tqdm, packaging, matplotlib, IPython + their dependencies); nothing removed or changed (numpy, pandas, scipy, scikit-learn, lightgbm same); `pip check` clean; smoke test on a small LightGBM passed (additivity OK). No Pinky code imports matplotlib / IPython / psutil. Don't follow the skill's `uv venv` step (it makes a new environment). Only last-fold models are saved (see runbook step 8).
  - None of these add-ons change training; they are for checking results afterwards.
  - `verification-before-completion`, `systematic-debugging` (obra/superpowers).
  - Context7 plugin (current library docs), enabled for Pinky in `.cursor/settings.json`. `.graphifyignore` keeps `.agents/` out of the graph.

## Commands

- Activate venv: `source .venv/bin/activate` (run everything from the repo root with `PYTHONPATH=.`)
- Sharadar pipeline:
  1. Pull: `python scripts/pull_sharadar.py` (~10 min, needs network)
  2. Universe panels: `python -m pinky.universe` (~1 min)
  3. Dataset: `python -m pinky.pit_dataset` (~1 min)
  4. Train/eval: `python scripts/train_walkforward.py --pit` (~8 min alone; output name = `train.VERSION` + `_pit`, currently `v8_pit`)
  - Ablations: `--without=rank_label,size` (see `train.MODEL_FIXES`). Several runs fit in parallel: `OMP_NUM_THREADS=3` each, 6 runs ≈ 13 min on v7 (18 cores, 48 GiB RAM). Step 3 launch commands: runbook at the top.
  - stdout is buffered when redirected to a file → use `python -u` to watch fold progress in a log.
  - Rebuild a report without retraining: `python scripts/train_walkforward.py --report-only=v7_pit` (uses the saved metrics CSV + preds parquet).
  - Compare runs: `python scripts/compare_runs.py v6_pit v7_pit ...`
- Legacy: `pull_data.py` → `build_features.py` → `build_labels.py` → `build_dataset.py` → `train_walkforward.py` (`--ex-winners` drops hindsight winners)
- Showcase: `python scripts/build_showcase.py` (~1 min; run name = `RUN` at the top). To view it in the IDE browser, serve it: `cd showcase && python3 -m http.server 8765` (`file://` is blocked).
- GitHub (private): https://github.com/steveonshit/Pinky (`origin/main`) — push only when the user says.
- Graphify CLI: `/Users/hqschool/Library/Python/3.12/bin` (if `graphify` isn't found: `export PATH="/Users/hqschool/Library/Python/3.12/bin:$PATH"`); run `graphify update .` after code changes.
- Tip: use one chat at a time on Pinky (parallel chats can overwrite each other's edits). On 2026-09-26/27 two chats worked in turn, which confused where work happened.
- Long chats get auto-summarized by Cursor (the agent then works from a summary; the full record is still saved). One very long chat also got a "Request blocked by Anthropic" error on a harmless question (likely a false positive). Fix for both: start a new chat — it picks up from this file. On 2026-10-03 the long step-3 chat lost track (it forgot it had started `fundamentals.py`), so before resuming, check `git status` and file times, not just the chat.
