# Pinky

Local stock-prediction project. **Goal: predict stocks that will perform well and make us profit** — beat the S&P 500 (**SPY**).

- **Favor tech**, and especially **finding future big winners** early ("the next NVDA/TSLA").
- **Still buy other sectors** (energy, industrials, etc.) when they're the best picks — not tech-only.

**Docs:** history, decision logs, results tables → `docs/PROJECT_HISTORY.md`. When the user says `run`, follow `docs/STEP3_RUNBOOK.md` (with the new batch's run names / flags).

## ▶ Resume here (new chat: read this first)

Last updated **2026-10-03**. Step 3 commits: code + date/leak checks `349d0d6`, results `66e83c7` (older milestone commits: `docs/PROJECT_HISTORY.md`).

**State**
- Phase 1 (honest evaluation) and Phase 2 steps 1–3 are **done**. **Still no edge over SPY.**
- **Step 3 — growth features (v8), done 2026-10-03:** 13 runs, all clean on the first try; control reproduced v7 exactly; no leak flag. Locked verdict: **growth DROP on A and B** (real − placebo +0.26%/yr and +0.98%/yr; bar +1.0%). Both continue **without growth**, monthly trading.
- **Final versions:** A (rank label) = `v8_pit_no-growth` (v7_pit inputs) **+7.23%/yr**; B (raw return) = `v7_pit_no-rank_label` **+5.83%/yr**. SPY +7.3%, equal-weight universe +8.0%.
- Showcase shows v6_pit (2026-09-27). Product page is live: https://pinky-research.vercel.app (numbers hand-copied, up to v7; re-check each by hand before any update). Update either **only when the user says**.
- Every report includes: takeover share of top picks, 2009–2020 vs SPY (`REPORT_SPLIT_YEAR`), and the score-group table.
- Local commits are **not pushed** (`git log origin/main..main --oneline`). User said: don't push yet.

**Open user decisions (2026-10-03)**
- Residual-edge check on the final versions (A = `v8_pit_no-growth`, B = `v7_pit_no-rank_label`)?
- SHAP (installed) on the final versions' last-fold models (2020 only): A `models/1y_pit_no-growth`, B `models/1y_pit_no-rank_label_v7`?
- Next batch (Roadmap 2, margin expansion): add the keep condition "real ≥ baseline without the new features, same 3 seeds"? (Step 3: extra columns cost A ~1%/yr even with real data.) Save every fold's model (~9 MB per run; small `train.py` change before training)?
- Push to GitHub?
- Plugins: turn Vercel / Supabase / Railway off in Cursor's settings (applies to all projects)? The project-only switch doesn't work (Gotchas).

**Next:** Roadmap batch 2 (margin expansion), same protocol as step 3 (placebo, 3 seeds). Propose the keep-rule and get the user's OK **before any run**. **Careful:** `--pit` still turns `growth` on by default (it's in `MODEL_FIXES`), so runs without growth need `--without=growth` (or change the default in `train.py`; ask first).

**When you finish a chunk of work:** update this Resume section so the next chat can pick up. Keep this file ~12–15 KB (`wc -c project.md`; every chat reads it): current state only. Move finished-step details (logs, decision logs, results tables) to `docs/PROJECT_HISTORY.md` and leave a 1–2 line summary + pointer here.

## Key findings (summary)

**Bar to beat** (v6_pit, Jan 2001 → Jan 2021): Ridge top 10% + buffer **+8.7%/yr** (+7.8% at 25 bps), Ridge rank IC 0.052. SPY +7.3%/yr (2009–2020 +14.5%). Tables: `docs/PROJECT_HISTORY.md`.
- **Price data predicts how much a stock moves, not which way** (v5). v6 Ridge's lead was all 2001–08, and many of its top-10 were takeover targets (25% acquired within 6 months vs 2.2% base rate): safe, not skill. 2020 broke every model.
- **Rank label (A) = the big lever:** IC ~doubles, but picks become calm stocks that rarely crash **and rarely win big** (top-10: 3.9% big winners, 2.3% crashes; random 10%). Without it (B), LightGBM is the best winner-finder so far (13.4% big winners, 8.0% crashes).
- **Higher IC ≠ better top picks:** v7's IC comes mostly from the bottom of the list; neither A nor B has a top 10% that beats the average stock. Judge the top of the list (score-group table).
- **Growth (v8):** too weak for the bar. **Extra columns cost A ~1%/yr, real or fake**, which the real-vs-placebo rule can't see (open decision above). Weekly trading loses at 25 bps → stay monthly.
- Top-10 CAGRs are noisy by a few %/yr → judge on IC and top 10% first.

## User goals & expectations

- Wants a model that's genuinely smart at finding stocks that perform well; catching the next NVDA/TSLA would be ideal.
- Likes tech most, but also buys other sectors (e.g., energy) — not tech-only.
- First asked for ~10%/month — explained that's unrealistic. Realistic aim: beat SPY by a few %/yr, reliably.
- Accepts a bit more risk (60% sector cap), **no leverage** (account can't). Bullish on tech.
- Data budget flexible (paying for Sharadar). Lots of time and compute.
- New to quant terms: explain metrics in plain words with small examples. Rank IC explained 2026-10-02 (one score per week for the model's whole ranked list; −1 = exactly backwards, 0 = no information, +1 = perfect order; grades order, not size, and not single stocks or just the top picks).

## Decisions

Full wording: `docs/PROJECT_HISTORY.md`.
- **Data:** Sharadar Core US Equities Bundle (API + bulk tables). Key in `.env` (gitignored, never print). License: never share or commit the data.
- **Universe (`pinky/universe.py`):** each day, price ≥ $5 and 21-day avg dollar volume ≥ $5M; common stock + ADRs + Canadian (no preferreds, secondary classes, SPACs); NYSE / NASDAQ / NYSE American → ~1,200–2,850 stocks/day, 11,561 distinct (1998–2026).
- **Delistings:** exit value reinvested in SPY; bankruptcy / liquidation / regulatory delistings also take **−30%** on the last price.
- **Rows:** weekly (every 5th trading day); folds use the daily calendar. Since v7, stocks are scored after ~1 month of prices.
- **Risk:** no leverage; sector cap 60% (Sharadar sectors).
- **Main signal:** undecided; A and B both continue unless one trails by > 4%/yr.
- **Locked holdout:** `HOLDOUT_START = 2022-01-01`; dev runs only use rows whose label ends before it (`train.dev_rows`); score it once, at the very end. Caveat: old 128-stock tests covered 2022–2025 and the 60% cap was picked after seeing them, so it's clean for the pit models but not fully unseen by us.

## Roadmap

**Done:** Phase 1 (honest evaluation, v5_pit); Phase 2 step 1 (evaluation fixes, v6_pit) and step 2 (four model fixes, v7_pit). Details: `docs/PROJECT_HISTORY.md`.

**Phase 2 — company data**, added in batches; keep only what beats the baseline:
1. Growth + revenue acceleration — **tested 2026-10-03 (v8): DROP** on both targets
2. **Margin expansion** ← next
3. Price strength (momentum, 52-week-high proximity, vs sector)
4. Earnings reactions / surprises
5. Reinvestment (R&D/revenue, ROIC)
6. Quality / safety (debt, cash burn, accruals, dilution)
7. Insiders + institutions (no insider / institution tables yet: check plan access first)
8. Industry tailwind
9. Valuation (context only — don't screen out growth)
10. Analyst revisions (expensive; later)

**Phase 3 — only if Phase 2 works:** position sizing, monthly picks report, live paper-trading log.

Data not downloaded yet: Sharadar `metrics` (access confirmed, ~1.4 MB).

## Backtest defaults

- Monthly rebalance, equal weight, **10 bps per side** (25 bps re-prices the same trades via `backtest.with_cost`).
- Portfolios: top-10, top-50, top 10% of each date's stocks; each with and without the **holding buffer** (keep a holding while it ranks in the top 3× N, `BACKTEST_BUFFER_MULT`). Main comparison rows: **top-10 + buffer** and **top 10% + buffer**.
- Sector cap 60% of picks (`BACKTEST_MAX_SECTOR_SHARE`) on all rows except "v5 rules". Signal at day D close, trade at D+1 close.
- Walk-forward: 1-year test folds; the last fold may be shorter (≥ 63 days, `WF_MIN_LAST_TEST_DAYS`) so 2020 is tested.
- Signals compared: LightGBM, Ridge, Blend (avg daily rank), naive 12-1 momentum. Settings: `pinky/config.py` (`BACKTEST_*`, `WF_*`).

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
- graphify does not skip dot-folders: third-party code there (e.g. `.agents/`) gets indexed unless it's listed in `.graphifyignore`.
- Cursor's sandbox blocks `pip install` into `.venv` ("Operation not permitted") → run pip with full permissions. In the sandbox, matplotlib warns that `~/.matplotlib` isn't writable (harmless; it uses a temp folder).
- API key safety: never print `.env`. Before a commit, check the staged diff with a count-only `grep -c -F` for the key (command: `docs/STEP3_RUNBOOK.md` step 7). Run it as its own command, in the normal sandbox: RTK leaves it unchanged, and auto-review blocked a full-permissions call containing it.
- `.git/info/exclude` (local to this clone, 2026-10-03) hides never-commit files from `git status`: `graphify-out/20*/` (dated backups made by `graphify update`), `.agents/`, `product/`, `skills-lock.json`, `.cursor/settings.json`, `.graphifyignore`. Still never stage them; put new never-commit paths there too, not in `.gitignore`. Project skills in `.agents/skills/` still load (checked). Workspace-wide Grep skips these paths → pass the folder as the search path.
- `.cursor/settings.json` `plugins`: Cursor reads only `"enabled": true` and ignores `false` (its code, 2026-10-03), so the Vercel / Supabase / Railway `false` entries don't turn them off (open decision above).
- RTK (2026-10-03): a global hook (`~/.cursor/hooks.json`, all projects) rewrites agent shell commands to compact `rtk` versions (`git`, `grep`, `ls`, `cat`…). Runbook checks give the same results (tested). Its `git status` drops the last newline, so chained output can run together. Raw output: `rtk proxy <cmd>`. Remove: `rtk init -g --agent cursor --uninstall`.

## Rules

Core rules: `AGENTS.md` (always on; every agent and subagent gets it; keep it short). Graphify: `.cursor/rules/graphify.mdc` (on request). Add or change rules only there, never in this file.

## Repo layout

Full layout with details: `docs/PROJECT_HISTORY.md`.
- `pinky/`: `config.py` (universe rules, paths, backtest settings, `HOLDOUT_START`), `sharadar.py`, `universe.py`, `pit_dataset.py` (21 features: 13 price + `history_1y` + `log_mcap` + 6 growth), `fundamentals.py` (growth + placebo shuffle), `preprocess.py`, `walkforward.py`, `train.py` (`MODEL_FIXES`, `--seed=N`, `--placebo`), `metrics.py`, `backtest.py`, plus legacy 128-stock files.
- `scripts/`: `pull_sharadar`, `train_walkforward`, `compare_runs`, `build_showcase`, `check_growth_features`, `step3_verdict`, legacy build scripts.
- `data/sharadar/` (~6 GB, gitignored, never share). `artifacts/`, `models/` (gitignored): per-run outputs named `<file>_<run>`; logs `artifacts/logs/train_<run>.log`. `models/1y_<tag>/` = last fold only; v7's models: `1y_pit_v7`, `1y_pit_no-rank_label_v7`.
- `showcase/`, `product/` (public page), `docs/` (also `ARCHITECTURE.md`, `PRD.md`, `EVAL.md`), `graphify-out/`.
- Agent add-ons (untracked; don't commit; none change training): skills in `.agents/skills/` (`residual-edge-analyzer`, `shap`, `verification-before-completion`, `systematic-debugging`), Context7 plugin. SHAP 0.52.0 is installed in `.venv`; don't follow the skill's `uv venv` step. Residual-edge input recipe: runbook step 8.

## Commands

- Activate venv: `source .venv/bin/activate` (run everything from the repo root with `PYTHONPATH=.`)
- Sharadar pipeline:
  1. Pull: `python scripts/pull_sharadar.py` (~10 min, needs network)
  2. Universe panels: `python -m pinky.universe` (~1 min)
  3. Dataset: `python -m pinky.pit_dataset` (~1 min)
  4. Train/eval: `python scripts/train_walkforward.py --pit` (~8 min alone; output name = `train.VERSION` + `_pit`, currently `v8_pit`)
  - Ablations: `--without=rank_label,size` (see `train.MODEL_FIXES`). Several runs fit in parallel: `OMP_NUM_THREADS=3` each, 6 runs ≈ 13 min on v7 (18 cores, 48 GiB RAM). Launch commands: `docs/STEP3_RUNBOOK.md`.
  - stdout is buffered when redirected to a file → use `python -u` to watch fold progress in a log.
  - Rebuild a report without retraining: `python scripts/train_walkforward.py --report-only=v7_pit` (uses the saved metrics CSV + preds parquet).
  - Compare runs: `python scripts/compare_runs.py v6_pit v7_pit ...`
- Showcase: `python scripts/build_showcase.py` (~1 min; run name = `RUN` at the top). To view it in the IDE browser, serve it: `cd showcase && python3 -m http.server 8765` (`file://` is blocked).
- Product page (Vercel Hobby; update only when the user says): redeploy, take-down and local-view commands → `docs/PROJECT_HISTORY.md` (State log, product page bullets). Never commit `product/.vercel/`.
- GitHub (private): https://github.com/steveonshit/Pinky (`origin/main`).
- Graphify CLI: `/Users/hqschool/Library/Python/3.12/bin` (if `graphify` isn't found: `export PATH="/Users/hqschool/Library/Python/3.12/bin:$PATH"`).
- Legacy 128-stock pipeline commands: `docs/PROJECT_HISTORY.md`.
- Chats: use one chat at a time on Pinky (parallel chats overwrite each other's edits). Long chats get auto-summarized and can lose track → start a new chat. Before editing or resuming, check `git log -3`, `git status` and file times, not just the chat. Details: `docs/PROJECT_HISTORY.md`.
