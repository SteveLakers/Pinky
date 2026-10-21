# Pinky

Local stock-prediction project. **Goal: predict stocks that will perform well and make us profit** — beat the S&P 500 (**SPY**).

- **Favor tech**, and especially **finding future big winners** early ("the next NVDA/TSLA").
- **Still buy other sectors** (energy, industrials, etc.) when they're the best picks — not tech-only.

**Docs:** history, decision logs, results tables → `docs/PROJECT_HISTORY.md`. Batch 2 plan → `docs/BATCH2_PLAN.md`. Growth round 2 plan + runbook → `docs/GROWTH_ROUND2_PLAN.md`. When the user says `run`, follow `docs/STEP3_RUNBOOK.md` with the current plan's Runbook section (run names / flags).

## ▶ Resume here (new chat: read this first)

Last updated **2026-10-21**. Milestone commits: `git log --grep "Batch 2"`; older: `docs/PROJECT_HISTORY.md`.

**State**
- **Code review (2026-10-21):** 6 findings (`docs/CODE_REVIEW_2026-10-21.md`) confirmed; 1, 2, 4, 5, 6 fixed = **backtest version 2** (37/37 checks). #3 (RSI drops 252 rows) open. Details: `docs/GROWTH_ROUND2_PLAN.md` → Code review fixes.
- Phase 1 (honest evaluation) and Phase 2 steps 1–3 are **done**. **Still no edge over SPY.**
- **Step 3 (v8 growth) = DROP**; growth stays opt-in (`--with=growth`). v9 saves every fold's models; its baselines = the old A and B exactly.
- **Final versions = batch 2 baselines** (LightGBM top 10% + buffer, net of 10 bps, mean of 3 seeds): A = `v9_pit` (+ `_s7`, `_s99`) **+7.15%/yr** (2001–08 −2.01%, 2009–20 +13.74%); B = `v9_pit_no-rank_label` (+ seeds) **+6.11%/yr** (−2.50%, +12.26%); re-scored with backtest v2 (v1: +7.14 / +6.10). Max drawdown A −49%, B −55%. SPY +7.28% (−2.74%, +14.53%), equal-weight universe +8.01%.
- **Batch 2 (margins), 2026-10-19: DROP on all 4 tests** (24 clean runs); finals stay the baselines; margins stay opt-in (`--with=margins`). Numbers: `docs/WALKFORWARD_RESULTS.md` → v9 batch 2.
- **Residual edge + SHAP, 2026-10-16:** no reliable edge in A or B (Key findings, last bullet; `docs/PROJECT_HISTORY.md` → Residual edge + SHAP).
- Showcase: v6_pit. Product page https://pinky-research.vercel.app (class project; **v2 live since 2026-10-07**; `docs/PROJECT_HISTORY.md` → Product page redesign v2; study guide `product/presenter-notes.md`). Update either only when the user says.
- Every report includes: takeover share of top picks, 2009–2020 vs SPY (`REPORT_SPLIT_YEAR`), and the score-group table.
- GitHub: last push 2026-10-12; every push needs the user's OK (`git log origin/main..main --oneline`).
- **Tools:** Claude app since 2026-10-04, ECC plugin since 2026-10-09 (Gotchas → Claude setup, Plugins). **Subagents fail for now** (2026-10-19: `best` sends them to `claude-fable-5-1` → "out of usage credits").

**Keep rule (user, batch 2; log: `docs/PROJECT_HISTORY.md` → Batch 2 decisions):** real − placebo ≥ +1.0%/yr overall and ≥ +0.5%/yr in each half (mean of seeds 42/7/99) **plus** real ≥ the baseline above (same 3 seeds).

**Next: growth round 2** (`docs/GROWTH_ROUND2_PLAN.md`): 4 new columns **one by one, then all 4 together** = 5 tests, 60 runs; 2-year label later. User 2026-10-21: same locked rule, **one test at a time** (all 5 run). **Code built + checked 2026-10-21** (85/85; old checks pass; old frames identical). Next: train only on `run` (plan → Runbook). Optional, ask first: SHAP on the margin runs. Don't push (user, 2026-10-16: no).

**When you finish a chunk of work:** update this Resume section. Keep this file ≤ ~15 KB (`wc -c project.md`): current state only; move finished details to `docs/PROJECT_HISTORY.md` with a 1–2 line pointer here.

## Key findings (summary)

**Bar to beat** (v6_pit, Jan 2001 → Jan 2021): Ridge top 10% + buffer **+8.7%/yr**, Ridge rank IC 0.052. SPY +7.3%/yr (2009–2020 +14.5%). Tables: `docs/PROJECT_HISTORY.md`.
- **Price data predicts how much a stock moves, not which way** (v5). v6 Ridge's lead was all 2001–08 and leaned on takeover targets: safe, not skill. 2020 broke every model.
- **Rank label (A) = the big lever:** IC ~doubles, but picks become calm stocks that rarely crash **and rarely win big**. Without it (B), LightGBM is the best winner-finder so far.
- **Higher IC ≠ better top picks:** v7's IC comes mostly from the bottom of the list; neither A nor B has a top 10% that beats the average stock. Judge the top of the list (score-group table).
- **Margins (batch 2):** DROP. A: helps 2001–08, hurts 2009–20 (a "profitable, steady" tilt). B: real margins lose to shuffled ones. Among fast growers, margin *change* doesn't pick winners; **loss-making** fast growers are the lottery tickets (most big winners and most crashes).
- **Growth (v8):** too weak for the bar. **Extra columns cost A ~1%/yr, real or fake**, which the real-vs-placebo rule can't see (batch 2 adds a check). Weekly trading loses at 25 bps → stay monthly.
- Top-10 CAGRs are noisy by a few %/yr → judge on IC and top 10% first.
- **What the models are (2026-10-16):** no reliable alpha in either. A = calm-stock picker, B = trend picker; both shun stocks with < 1 year of trading. Fastest growers: worst median next year but the most big winners and crashes (a lottery ticket).

## User goals & expectations

- Wants a model that's genuinely smart at finding stocks that perform well; catching the next NVDA/TSLA would be ideal.
- Likes tech most, but also buys other sectors (e.g., energy) — not tech-only.
- First asked for ~10%/month — explained that's unrealistic. Realistic aim: beat SPY by a few %/yr, reliably.
- Accepts a bit more risk (60% sector cap), **no leverage** (account can't).
- Data budget flexible (paying for Sharadar). Lots of time and compute.
- New to quant terms: explain metrics in plain words with small examples. Rank IC (one score per week for the whole ranked list: −1 backwards, 0 no information, +1 perfect order; grades order, not size).
- Presents Pinky in class from the product page (2026-10); a full tech demo is due at the end of the term.

## Decisions

Full wording: `docs/PROJECT_HISTORY.md`.
- **Data:** Sharadar Core US Equities Bundle (API + bulk tables). Key in `.env` (gitignored, never print). License: never share or commit the data.
- **Universe (`pinky/universe.py`):** each day, price ≥ $5 and 21-day avg dollar volume ≥ $5M; common stock + ADRs + Canadian (no preferreds, secondary classes, SPACs); NYSE / NASDAQ / NYSE American → ~1,200–2,850 stocks/day.
- **Delistings:** exit value reinvested in SPY; bankruptcy / liquidation / regulatory delistings also take **−30%** on the last price.
- **Rows:** weekly (every 5th trading day); folds use the daily calendar. Since v7, stocks are scored after ~1 month of prices.
- **Risk:** no leverage; sector cap 60% (Sharadar sectors).
- **Main signal:** undecided; A and B both continue unless one trails by > 4%/yr.
- **Locked holdout:** `HOLDOUT_START = 2022-01-01`; dev runs only use rows whose label ends before it (`train.dev_rows`); score it once, at the very end. Not fully unseen by us: the 60% cap was picked after old 2022–25 tests.

## Roadmap

**Done:** Phase 1 (honest evaluation, v5_pit); Phase 2 step 1 (evaluation fixes, v6_pit) and step 2 (four model fixes, v7_pit). Details: `docs/PROJECT_HISTORY.md`.

**Phase 2 — company data**, added in batches; keep only what beats the baseline:
1. Growth + revenue acceleration — **tested 2026-10-03 (v8): DROP** on both targets; kept in the code (`--with=growth`). **Growth round 2** next: `docs/GROWTH_ROUND2_PLAN.md`.
2. Margin expansion — **tested 2026-10-19: DROP** (alone and with growth, A and B); kept in the code (`--with=margins`)
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

Monthly rebalance, equal weight, **10 bps per side** (25 bps re-priced), 60% sector cap, holding buffer 3× N; signal at D close, trade at D+1 close. Main comparison rows: **top-10 + buffer** and **top 10% + buffer**. Full list (portfolios, signals, walk-forward folds): `docs/ARCHITECTURE.md`; settings: `pinky/config.py` (`BACKTEST_*`, `WF_*`).

## Gotchas (learned the hard way)

- Sharadar CSVs must be parsed with `sharadar.CSV_KW` (`keep_default_na=False`). Otherwise the ticker "NA" becomes blank.
- `fiscalperiod` is text ("2009-Q4"), not a date.
- Fundamentals: use **AR\*** dimensions only (dated by SEC filing date). **MR\*** rows are dated at quarter-end → ~2.5 months of future leak.
- Any dataset column that doesn't start with a prefix in `dataset.LABEL_PREFIXES` is treated as a **model input**. New label columns must get a prefix there, or they leak.
- Rows are weekly → always pass the daily `calendar` to `iter_walk_forward_folds`. Otherwise "252 days" silently becomes 252 weeks.
- Forward returns and backtests must use the `tr` panel (delisting-aware), never raw `closeadj`.
- pandas `to_numpy()` can return a read-only array → use `np.array(..., copy=True)` before writing into it.
- LightGBM `subsample` needs `subsample_freq` > 0 (now `subsample=1.0`; it never sampled through v8). Turning it on is a model change to test.
- Filtered Sharadar API queries return only the last year unless you pass `from_=`.
- Sharadar tickers are unique (reused symbols get a suffix, e.g. `CNO1`).
- `pd.merge_asof` needs both frames sorted by the `on` key **globally** (not ticker-first), else "left keys must be sorted". Among equal keys it takes the last right row → sort the right side by (news date, period) so the newest quarter wins.
- Quarter math: `pd.DateOffset(months=3)` maps Sep 30 → Dec 30 (wrong); use `pd.offsets.MonthEnd(n)`.
- SF1 has a few reports "filed" 0–9 days after period end (data errors); `fundamentals.first_filed` skips them.
- Earnings events (code 22) start 2004-08-23; ADRs (6-K filers) have none → filing dates.
- Size: panels 7,227 days × 17,340 stocks; dataset build peaks ~14 GB RAM, a training run ~4–5 GB (machine: 48 GiB RAM, 18 cores).
- Run names come from the options (`train.run_all`), not the log file name. The runbook uses log name = run name and checks it.
- Untracked `data/reference/` comes from another chat — leave it alone.
- API key safety: never print `.env`. Before a commit, check the staged diff with a count-only `grep -c -F` for the key (command: `docs/STEP3_RUNBOOK.md` step 7). Run it as its own command.
- `.git/info/exclude` (local; the full list) hides never-commit files from `git status` (`.agents/`, `product/`, local settings…). Never stage them; put new never-commit paths there, not in `.gitignore`. Workspace-wide Grep skips these paths → pass the folder as the search path.
- **Claude setup:** Local only, never Cloud (Sharadar license); notes: `CLAUDE.md`; settings `.claude/settings.local.json` (never commit). Full notes: `docs/PROJECT_HISTORY.md` → Claude and plugin setup.
- Plugins: Context7 + ECC (user, 2026-10-09); Vercel / Supabase / Railway are ZerMap-only. ECC hooks on everywhere; GateGuard checks only risky commands; a Stop hook (`~/.claude/hooks/ecc-report-check.js`) makes every reply name the ECC tools it used. Never "Uninstall" a plugin; change its scope (`.claude/settings.local.json` → `enabledPlugins`). Details: `docs/PROJECT_HISTORY.md` → Claude and plugin setup.

## Rules

Core rules: `AGENTS.md` (always on, for every agent; keep it short). Claude-only notes: `CLAUDE.md`. Graphify: the `graphify` skill. Add or change rules only there, never in this file.

## Repo layout

Full layout with details: `docs/PROJECT_HISTORY.md`.
- `pinky/`: the pipeline (module map, features, switches: `docs/ARCHITECTURE.md`; settings and `HOLDOUT_START`: `config.py`), plus legacy 128-stock files.
- `scripts/`: pull_sharadar, train_walkforward, compare_runs, build_showcase, check_growth_features, check_margin_features, check_growth2_features, step3_verdict, batch_verdict, fast_grower_margins, residual_edge, shap_report, product_numbers, product_page_data, legacy build scripts.
- `data/sharadar/` (~6 GB, gitignored, never share). `artifacts/`, `models/` (gitignored): per-run outputs `<file>_<run>`; logs `artifacts/logs/train_<run>.log`; `models/<run>/1y/fold_NN/` = every fold's models (v9+; older layout: `docs/PROJECT_HISTORY.md` → Moved from project.md).
- `showcase/`, `product/` (public page), `docs/` (also `ARCHITECTURE.md`, `PRD.md`, `EVAL.md`), `graphify-out/`.
- Agent add-ons (untracked; don't commit; none change training): skills in `.agents/skills/` (linked into `.claude/skills/`). SHAP 0.52.0 is in `.venv`; don't follow the shap skill's `uv venv` step. Residual-edge input recipe: runbook step 8.

## Commands

- Activate venv: `source .venv/bin/activate` (run everything from the repo root with `PYTHONPATH=.`; Claude: in the same command).
- Sharadar pipeline:
  1. Pull: `python scripts/pull_sharadar.py` (~10 min, needs network)
  2. Universe panels: `python -m pinky.universe` (~1 min)
  3. Dataset: `python -m pinky.pit_dataset` (~1 min)
  4. Train/eval: `python scripts/train_walkforward.py --pit` (~8 min alone; output name = `train.VERSION` + `_pit`, currently `v9_pit` = A without growth)
  - Ablations: `--without=rank_label,size` (`train.MODEL_FIXES`). Company data under test: `--with=growth,margins` or growth round 2's `ear` / `sue` / `cagr` / `steady` / `growth2` (`train.FEATURE_GROUPS`, off by default since v9; `--without=growth` errors); placebo `--placebo=<group>` (bare `--placebo` = growth). Parallel runs: `OMP_NUM_THREADS=3` each. Launch commands: `docs/STEP3_RUNBOOK.md`.
  - stdout is buffered when redirected to a file → use `python -u` to watch fold progress in a log.
  - Re-score a run with today's backtest (no retraining; old outputs → `artifacts/superseded/`): `python scripts/train_walkforward.py --report-only=v9_pit`.
  - Compare runs: `python scripts/compare_runs.py v6_pit v7_pit ...`
  - Explain runs: `python scripts/residual_edge.py A=v9_pit,v9_pit_s7,v9_pit_s99` (seconds) and `python scripts/shap_report.py A=v9_pit,...` (~5 min; v9+ runs). Design and outputs: each script's docstring.
- Showcase: `python scripts/build_showcase.py` (~1 min; run name = `RUN` at the top). View: click `showcase/index.html` in the Claude chat (Browser pane).
- Product page (only when the user says): `python scripts/product_numbers.py` (~5 min), then `python scripts/product_page_data.py` fills every number (never type them). Deploy, take-down, preview: `docs/PROJECT_HISTORY.md` (State log; Product page redesign). Never commit `product/.vercel/`.
- GitHub (private): https://github.com/steveonshit/Pinky (`origin/main`).
- Graphify CLI: `/Users/hqschool/Library/Python/3.12/bin/graphify` (not on the shell PATH: use the full path, or `export PATH=…` in the same command).
- Legacy 128-stock pipeline commands: `docs/PROJECT_HISTORY.md`.
- Chats: one at a time on Pinky, Cursor and Claude together (parallel chats overwrite each other's edits). Long chats lose track → start a new chat. Before editing or resuming, check `git log -3`, `git status` and file times, not just the chat.
