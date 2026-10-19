# Step 3 training runbook (v8 growth features)

Moved from `project.md` on 2026-10-03. Current state and open user decisions: `project.md`. Step 3 results: `docs/PROJECT_HISTORY.md` (Key findings → Step 3) and `docs/WALKFORWARD_RESULTS.md`.

## Runbook (done 2026-10-03; reuse for the next batch)

**Ran 2026-10-03 as written:** all 13 runs EXIT 0 on the first try (no reruns), control reproduced v7 exactly, ~39 min of training + ~2 min verdict. For the next batch, change the run names / flags and keep the steps. Cursor sandbox note: `caffeinate` needs full permissions.

**Since v9 (2026-10-12):** growth is off by default: turn it on with `--with=growth` (`--without=growth` now errors), so v8 names map to v9 as `v8_pit_no-growth` → `v9_pit`, `v8_pit` → `v9_pit_with-growth`, `v8_pit_placebo` → `v9_pit_with-growth_placebo`. Every fold's models go to `models/<run>/1y/fold_NN/`, so step 1's model-copy line is obsolete.

**Claude:** each command starts a fresh shell (only the working folder carries over), so run each code block below as **one** command; every block that runs Python starts by activating `.venv`.

**0. Before anything**
- **Go-ahead:** train only after the user says `run` (or clearly asks you to start training). The plan is locked (Step 3 notes below) → don't re-plan or re-ask; confirm in one line and start.
- **Model:** launching is routine, but judging the results is hard work. If the chat isn't on the top model (Cursor on Auto; Claude: check the model dropdown), ask the user to switch to the highest model **before launching**, and wait (model rule in `AGENTS.md`).
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
- Run each block as **one** shell command in the background. Claude: Bash tool with `run_in_background: true` and `timeout: 7200000` (background commands stop after 30 min by default; 2 h is the max). Cursor: Shell tool `block_until_ms: 0` (the default sandbox is fine, v7 ran that way). The block's `wait` ends when its batch ends.
- **Never** start `caffeinate … &` inside a block that ends with `wait`: `wait` also waits for it, and `caffeinate -w $$` only ends with the shell → the block hangs after its runs finish (cost batch 2 ~17 min, 2026-10-19). Keep the Mac awake from a separate background command instead: `caffeinate -i -w <pid of the training shell>`.
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
cd /Users/hqschool/Desktop/Pinky && source .venv/bin/activate
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
- `EXIT 137` = killed, usually out of memory → rerun that run alone (same `launch` line). Other non-zero → read the traceback, fix the cause, rerun only that run, and log it (step 7).

**4. Check all 13 runs before the verdict**

```bash
cd /Users/hqschool/Desktop/Pinky && source .venv/bin/activate
ls artifacts/backtest_stats_1y_v8_*.csv | wc -l     # expect 13
grep -L "EXIT 0" artifacts/logs/train_v8_*.log      # expect no output
for f in artifacts/logs/train_v8_*.log; do n=$(basename "$f" .log); n=${n#train_}; grep -qF "=== Training horizon 1y ($n) ===" "$f" || echo "NAME MISMATCH: $f"; done     # expect no output
PYTHONPATH=. python -c "import json,glob; [print(f, json.load(open(f))) for f in sorted(glob.glob('artifacts/run_config_v8_*.json'))]"     # seed / placebo / fixes fit each name
```

**5. Verdict (~2–10 min; `--weekly` re-runs the backtests with weekly trading)**

```bash
cd /Users/hqschool/Desktop/Pinky && source .venv/bin/activate
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
- `docs/PROJECT_HISTORY.md`: add "Step 3 — growth features (v8)" under Key findings (verdict table + scoreboard); log every test, including reruns. `project.md`: update the Resume section (State / Open user decisions / Next) and the Key findings summary; keep it ~12–15 KB (details go to `docs/PROJECT_HISTORY.md`). `docs/WALKFORWARD_RESULTS.md`: add a v8 section like the v7 one.
- Commit locally. Stage only files you changed (`project.md`, `docs/…`; if code changed, also run `graphify update .`). Key check (prints a count, never the key; must print 0; run it as its own command; Cursor: in the normal sandbox): `git diff --cached | grep -c -F -f <(sed -n 's/^[^=#]*=//p' .env | tr -d '"' | tr -d "'" | awk 'length($0) >= 8') || true`
- Never stage `data/`, `artifacts/`, `models/`, `product/`, `.agents/`, `skills-lock.json`, `.cursor/settings.json`, `.claude/settings.local.json`, the `.claude/skills/` links, `.graphifyignore`, `graphify-out/YYYY-MM-DD/`. **No push.**

**8. Then ask the user (start none of these without an OK)**
- Since 2026-10-16 both checks are scripts: `scripts/residual_edge.py` and `scripts/shap_report.py` (v9+ runs; usage in their docstrings).
- **Residual-edge check** (no install; `.agents/skills/residual-edge-analyzer/`): is the portfolio's return more than its SPY / equal-weight / momentum exposure? Input: `artifacts/backtest_periods_1y_<run>.csv`, rows with `signal == "LightGBM"` and `portfolio == "Top 10% + buffer"`: `start` = date, `gross` = strategy, `spy` = market, `universe_ew` = equal-weight; momentum = `gross` of the `Momentum 12-1` rows (same portfolio and dates). Monthly; gross for every column.
- **SHAP** (which features drive LightGBM): installed 2026-10-03, ready. Only last-fold models are saved (trained on data before 2020, tested on 2020).
- **Next batch:** Roadmap batch 2 (margin expansion), same protocol (placebo, 3 seeds, propose the keep-rule before any run).

## Step 3 notes (company data batch 1 — plan locked 2026-10-03)

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
