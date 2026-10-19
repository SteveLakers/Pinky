# Pinky project history

Moved from `project.md` on 2026-10-03 to keep `project.md` short: state log, user decision logs, notes on finished steps, results tables, full design / roadmap / repo-layout notes. Current state, next step and open decisions: `project.md`. Step 3 runbook and locked plan: `docs/STEP3_RUNBOOK.md`. Per-version results: `docs/WALKFORWARD_RESULTS.md`.

## State log (snapshot 2026-10-03)

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
- **User asked (2026-10-03) whether the new add-ons help training:** they don't change training; they help check results afterwards (verification, debugging, residual-edge, SHAP). The user then asked for a detailed handover so the next agent can start training → `docs/STEP3_RUNBOOK.md`.
- **User (2026-10-03, later):** wants **very short replies by default** (saves tokens); more detail only when asked. SHAP installed (see Repo layout).
- **Phase 2 step 3 — growth features (v8): done 2026-10-03** (user said "Start train"; launched and judged on Claude Opus 5.5). Locked verdict: **DROP on A and B** (real − placebo +0.26%/yr and +0.98%/yr; bar +1.0%). Both continue without growth, monthly trading. Details: Key findings → Step 3, `docs/WALKFORWARD_RESULTS.md`, `artifacts/step3_verdict.md`.
- **Step 3 build (done 2026-10-03):** `pinky/fundamentals.py` (growth features), wired into `pit_dataset.py` (dataset rebuilt: same 2,932,585 rows, 21 features). `train.py`: `VERSION = "v8"`, `growth` in `MODEL_FIXES`, `--placebo`, `--seed=N`, `pit_training_frame()`, monthly returns saved as `artifacts/backtest_periods_1y_<run>.csv`. `backtest.run_backtest(rebalance="weekly")`. `compare_runs.py` adds equal-weight universe and monthly top-10 big-winner / crash rows. New scripts: `scripts/check_growth_features.py` (59 date/leak checks) and `scripts/step3_verdict.py` (the locked rule; refuses to run until all 13 runs exist). v7 dataset backup: `data/sharadar/derived/pit_dataset_v7.parquet` (checksum-verified copy).
## Setup cleanup (2026-10-03, user-approved)

From the user's 5-task list, done in one chat (commits `6fd9a2d`, `53b996f`). Keep it this way unless the user says otherwise.
- **Rules, one copy each:** core rules → `AGENTS.md`, the only always-on rule file (subagents get it automatically; checked). `.cursor/rules/` keeps only `graphify.mdc`, now on request (use graphify for questions that span several files; skip it when the file is known). Merged into `AGENTS.md` and deleted: `read-project-md.mdc`, `strong-models.mdc`, `pinky-rules.mdc`, `communication.mdc`. `project.md`'s Rules section is a pointer. Always-on rules: 5,780 → 2,308 B.
- **Model rule:** the user removed "token cost doesn't matter", "go very heavy" and "I got money"; kept "always use the top model, never downgrade"; subagents only when they clearly help. Also dropped: "fast/cheap models for trivial lookups" (contradicted "never downgrade") and "copy this rule into every subagent prompt" (not needed).
- **`project.md` shortened** (every chat reads it): ~49 KB → ~15 KB. Step 3 runbook → `docs/STEP3_RUNBOOK.md`; state log, decision logs, results tables, full layout → this file (moved verbatim; fact check: no number or URL lost).
- **Local git excludes** in `.git/info/exclude` (not `.gitignore`): `graphify-out/20*/`, `.agents/`, `product/`, `skills-lock.json`, `.cursor/settings.json`, `.graphifyignore`. `data/reference/` left alone.
- **Plugins:** the user asked to turn Vercel / Supabase / Railway off for this project only: `"enabled": false` entries next to `context7-plugin` in `.cursor/settings.json`. Doesn't work (Cursor reads only `true` entries); entries kept. Context7 stays on.
- **Plugins made ZerMap-only (same day, user's choice: off for Pinky, ZerMap must keep them).** Cursor loads plugins from 3 places (its code and logs): the account (every project); a project's `.cursor/settings.json` (`true` only; key = plugin name for `cursor-public`, else `marketplace/name`); Claude Code (`~/.claude/plugins/installed_plugins.json`, skipped in a project whose `.claude/settings.json` or `settings.local.json` sets the plugin to `false` in `enabledPlugins`). Done:
  - ZerMap `.cursor/settings.json`: `vercel/vercel-plugin`, `supabase`, `railway` = true. The user then removed the account install of all three. Logs: account list empty; ZerMap's project list has all 3; Pinky's only Context7.
  - Pinky `.claude/settings.local.json`: `"vercel-plugin@vercel": false` (Vercel was also installed in Claude Code, 2026-04-12). Listed in `.git/info/exclude`.
  - Railway MCP server: removed from `~/.cursor/mcp.json` (now empty; backup `~/.cursor/mcp.json.bak-2026-10-03`), added to ZerMap `.cursor/mcp.json`.
  - `use-railway` skill had 3 identical global copies: `~/.cursor/skills` (moved to ZerMap `.cursor/skills/`), `~/.claude/skills` (removed; backup `~/.cursor/use-railway-claude-skill-backup-2026-10-03.tar.gz`), `~/.agents/skills` (moved to `~/.cursor/skill-backups-2026-10-03/use-railway-from-agents/`).
  - Checked after a full Cursor restart (2026-10-03 20:46): Pinky's window loads 0 Claude Code plugins and only Context7 from the marketplace; no Vercel / Supabase / Railway tools. ZerMap's windows load all 3 plus Claude Code's Vercel. Windows with no folder (and other projects) still get Claude Code's Vercel (enabled in `~/.claude/settings.json`).
  - How to check: `rg 'loadClaudePlugin|listEnabledPlugins completed|Adding enabled plugin' ~/Library/Application\ Support/Cursor/logs/<latest>/window*/`. Find which window is which project by counting `Desktop/Pinky` vs `Desktop/ZerMap` mentions in each window folder. Use `rg --no-filename`, not `-h` (that prints help).
  - ZerMap's `.cursor/` changes are uncommitted in its repo.
  - Never full "Uninstall" these plugins: it removes them from every project, ZerMap included.
- **RTK 0.51.0** (`brew install rtk`, then `rtk init -g --agent cursor`): created `~/.cursor/hooks.json` with one `preToolUse` hook (`rtk hook cursor`, matcher `Shell`), global for all projects. Telemetry off.

## Move to the Claude app (2026-10-04, user-approved)

The user asked to move everything for Pinky to the Claude app on this Mac. Two Cursor chats got the request; the first stopped mid-way, the second finished it (config only). Cursor files stay as a fallback.
- **Rules:** `CLAUDE.md` loads `AGENTS.md` and adds Claude notes (sessions, model, subagents, shell, skills). `AGENTS.md` rule 14 is tool-neutral now: check the model; ask only if it isn't the top one or you can't tell.
- **Model:** `.claude/settings.local.json` → `model: best`, plus `CLAUDE_CODE_SUBAGENT_MODEL=best` and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (without them, Explore runs on Opus when the main chat runs Fable). Checked in the docs and in the app's bundled Claude Code 2.1.286: the variable goes through the same parser as `--model`, which maps `best` to Fable if available, else Opus. The app's model dropdown sets each session's model.
- **Plugins:** Context7 installed in Claude for Pinky only (local scope; remote MCP server, nothing to install). The `upstash/context7` marketplace was added to `~/.claude/settings.json` (`extraKnownMarketplaces`); backups `~/.claude/plugins/*.bak-2026-10-04`. Vercel stays off for Pinky.
- **Skills:** `.claude/skills/` links to the 4 skills in `.agents/skills/` and to `~/.agents/skills/find-skills`; the graphify rule is a skill now. Links listed in `.git/info/exclude`; `.claude/` added to `.graphifyignore`.
- **Claude shell facts (docs + bundled binary):** each Bash call starts a fresh shell (venv activation and `export PATH` don't carry over); background commands stop after 30 min by default (max 2 h via `timeout`); `graphify` isn't on the shell PATH. Runbook and `project.md` updated for these.
- **Not ported:** RTK (Cursor-only hook), Cursor chat history, Cursor's Context7 extras (skill, `docs-researcher` agent, `/docs` command; Claude's plugin ships only the MCP server).
- **Cursor-only gotchas (moved from `project.md`, for the fallback):** the sandbox blocks `pip install` into `.venv` ("Operation not permitted"; run pip with full permissions) and makes matplotlib warn that `~/.matplotlib` isn't writable (harmless; it uses a temp folder). RTK (global hook `~/.cursor/hooks.json`, all projects) rewrites agent shell commands to compact `rtk` versions (`git`, `grep`, `ls`, `cat`…); runbook checks give the same results (tested); its `git status` drops the last newline, so chained output can run together; raw output: `rtk proxy <cmd>`; remove: `rtk init -g --agent cursor --uninstall`. Run the key check in the normal sandbox (RTK leaves it unchanged; auto-review blocked a full-permissions call containing it). Plugin scope: Customize → plugin, from the project that keeps it, then reload; plugin sources and how to check: Setup cleanup (above). The Railway MCP server and `use-railway` skill are ZerMap-only too. Project skills in `.agents/skills/` load in Cursor (checked 2026-10-03).

## First Claude chat (2026-10-05, Claude Opus 5.5)

The user asked the first Claude chat to read the code, all Cursor chats and `project.md`, then ask questions. Answers and actions:
- **Model:** the user's dropdown has Fable 5, not 5.1; this chat ran on Opus 5.5. Docs now say Fable 5. Not yet checked: whether `best` (start model, subagents) reaches Fable 5 on this account.
- **LightGBM row sampling (user: "decide what is best"):** `subsample=0.7` never took effect (LightGBM also needs `subsample_freq` > 0), so v2–v8 trained every tree on all rows; seeds only changed column sampling and bin setup. Chosen: make the code say what ran (`subsample=1.0`). Checked on synthetic data: predictions bit-for-bit identical on seeds 42 / 7 / 99, return and beat models. Turning row sampling on stays a separate model change (own runs, new baselines).
- **Railway (user: yes, ZerMap-only in Claude too):** Claude loaded a user-scope `railway` MCP server (`~/.claude.json`, command `railway mcp`) in every project, Pinky and DwellSense included. ZerMap already has its own (`ZerMap/.mcp.json`, enabled in its `.claude/settings.local.json`, plus project-scope Railway / Supabase / Vercel plugins). The app's auto-mode check blocked the agent's `claude mcp remove railway -s user`, so the user runs it. Undo: `claude mcp add -s user railway -- railway mcp`.
- **Docs (user: yes):** `README.md`, `docs/ARCHITECTURE.md`, `docs/PRD.md` (v0.2) and `docs/EVAL.md` rewritten for the current Sharadar pipeline; they point to `project.md` for numbers. `project.md`'s backtest-defaults and repo-layout lines now point to `docs/ARCHITECTURE.md`.
- **Open decisions (user: keep them all):** they stay in `project.md`, to decide at batch 2.
- Context7 needs a one-time sign-in in Claude (`/mcp` in a terminal `claude` session).
- The 14 Cursor chats are JSONL files in `~/.cursor/projects/Users-hqschool-Desktop-Pinky/agent-transcripts/`.

## Claude and plugin setup (moved from project.md 2026-10-12, unchanged)

- **Claude setup (2026-10-04):** Code tab, **Local**, folder `~/Desktop/Pinky` (never Cloud: Sharadar license). Rules: `CLAUDE.md` (loads `AGENTS.md`). `.claude/settings.local.json` (never commit): start model `best`, every subagent forced onto `best` (this account has Fable 5, not 5.1; the dropdown sets each session's model), Context7 on (one-time sign-in: `/mcp` in a terminal `claude` session), Vercel off. Railway: a user-scope MCP server in `~/.claude.json` loads everywhere until the user runs `claude mcp remove railway -s user` (ZerMap has its own). Old Cursor chats (JSONL): `~/.cursor/projects/Users-hqschool-Desktop-Pinky/agent-transcripts/`. More, incl. Cursor-fallback notes: `docs/PROJECT_HISTORY.md` → Move to the Claude app.
- Plugins: Pinky uses Context7 + ECC (user's choice, 2026-10-09); Vercel / Supabase / Railway are ZerMap-only. **ECC** (`ecc@ecc`): user scope; hooks on in all projects since 2026-10-19 (user `pluginConfigs` → `hooks_enabled: true`; Pinky also `ECC_HOOKS_ENABLED=true` in `.claude/settings.local.json` → `env`, which overrides the plugin option; standard profile). GateGuard (user 2026-10-19: keep only the risky-command check) is turned down by two `env` lines in `~/.claude/settings.json`: `"ECC_DISABLED_HOOKS": "pre:edit-write:gateguard-fact-force"` (no first-edit-per-file check) and `"GATEGUARD_BASH_ROUTINE_DISABLED": "1"` (no first-command check; risky commands still checked). Claude's auto mode refuses to add them (self-modification); the user added them 2026-10-19 (checked: valid JSON, edit check OFF, risky-command check ON). `~/.claude/CLAUDE.md` (global, all projects, 2026-10-19): every reply names each ECC tool used (skills/commands/agents `ecc:…`, MCP `mcp__plugin_ecc_…`), why, and what it did; hooks only when they block, change a file, or change what the agent did. Hook logs: `~/.claude/bash-commands.log`, `~/.claude/cost-tracker.log`, `~/.local/share/ecc-homunculus/projects/fa0f9ece6536/observations.jsonl` (≤ 5,000 chars of each tool call's input/output, secret-looking values scrubbed; local only), `~/.gateguard/`. ~31K tokens per session; bundles chrome-devtools-mcp (own Chrome profile, `~/.cache/chrome-devtools-mcp/`). `~/.claude/settings.json` → `env`: every subagent forced onto `best` (most ECC agents ask for Sonnet/Haiku), chrome-devtools usage stats off. Never "Uninstall" a plugin (removes it everywhere); change its scope (Claude: `.claude/settings.local.json` → `enabledPlugins`).
- **ECC-report Stop hook (user, 2026-10-19):** `~/.claude/hooks/ecc-report-check.js` (Node), in `~/.claude/settings.json` → `hooks.Stop` (Claude added it with the user's OK). It reads the current turn from the transcript (from the last prompt the user typed). ECC tool = Skill or Agent `ecc:…`, `mcp__plugin_ecc_…`, or a typed `/ecc:…`. If one isn't named in an "ECC used" line in the saved reply text, it blocks the reply once (`stop_hook_active` prevents loops); any error lets the reply through. It can't see ECC tools a subagent uses inside its own run. Tested: 14 fake and real-transcript cases, then a live block in Claude. Seen once while testing: reply text written before a wrap-up box with a question was not saved to the transcript (the user may not have seen it) → put ECC lines after the wrap-up. Same day: subagents (forced onto `best`) went to `claude-fable-5-1` and failed with "out of usage credits" (HTTP 429), so none ran; this conflicts with "Fable 5, not 5.1" above (unresolved).
- **Tools (State line, 2026-10-09):** Claude app since 2026-10-04 (Gotchas → Claude setup). 2026-10-05: Cursor chats read, old docs rewritten, LightGBM `subsample` fixed in code (no result change). 2026-10-09: ECC plugin installed for every project (Gotchas → Plugins). Still the user's step: `claude mcp remove railway -s user`.

## Batch 2 decisions (2026-10-09, Claude Opus 5.5)

User chose to continue on Opus 5.5 for this chat only (`CLAUDE.md` keeps Fable as the top model). Settled the 4 open decisions from 2026-10-03:
- **Keep rule for batch 2:** yes, add "real ≥ the same version without the new features (mean of seeds 42/7/99)" to step 3's real-vs-placebo rule. Reason: in step 3, extra columns cost A ~1%/yr even with real data, and real − placebo can't see that. Only seed 42 baselines exist (`v8_pit_no-growth`, `v7_pit_no-rank_label`), without saved folds → 6 baseline runs (seeds 42, 7, 99 for A and B).
- **Save every fold's model:** yes (~9 MB per run; small `train.py` change before training; predictions must stay bit-identical).
- **Push to GitHub:** yes. Before the push: no data / artifacts / models files in the unpushed commits (checked by path), key check 0.
- **SHAP / residual-edge:** run both on the 6 baseline runs (user: "do what's best for accurate and training"). Why not now: only 2020 models are saved (COVID year), and B (`v7_pit_no-rank_label`) has no `backtest_periods` file (made before v8).

### Step 2: code prep + baseline runs (2026-10-12, Claude Opus 5.5 Max)

User decisions: **growth opt-in** (kept, off unless asked; user: "growth data is definitely important… we just haven't found the best way to use it yet", maybe the time frame is too short or growth doesn't weigh enough), **one model folder per run with every fold**, **run the 6 baselines now** (they double as the check that the code change broke nothing), **push after the key check**.
- Code `7f0b6c4` (v9): `MODEL_FIXES` = rank_label, rank_features, young, size (on; `--without=`); `FEATURE_GROUPS` = growth (off; `--with=`, runs tagged `with-<group>`); `--without=growth` now errors; models in `models/<run>/1y/fold_NN/` + `folds.json`.
- Smoke test before training (2001–03 folds, 3 threads): predictions identical to `v8_pit_no-growth` and `v7_pit_no-rank_label`; every reloaded fold model reproduces its predictions. Also confirms on real data that the 2026-10-05 LightGBM `subsample` edit changed nothing.
- 6 runs (`v9_pit`, `v9_pit_no-rank_label`, each also `_s7`, `_s99`; 6 at once, 3 threads each, ~15 min, on battery with `caffeinate -i`): all 20 folds, EXIT 0, 8.5–8.6 MB of models each. Seed 42 = the saved runs exactly (2,031,316 predictions and the 44-row backtest tables identical).
- New baselines (LightGBM top 10% + buffer, net of 10 bps; all / 2001–08 / 2009–20):

| | Seed 42 | Seed 7 | Seed 99 | Mean |
|---|---|---|---|---|
| A (`v9_pit`) | +7.23% / −1.55% / +13.52% | +7.12% / −2.24% / +13.85% | +7.08% / −2.31% / +13.84% | **+7.14% / −2.03% / +13.74%** |
| B (`v9_pit_no-rank_label`) | +5.83% / −2.27% / +11.60% | +6.07% / −2.95% / +12.55% | +6.40% / −2.29% / +12.63% | **+6.10% / −2.50% / +12.26%** |

SPY +7.28% / −2.74% / +14.53%; equal-weight universe +8.01%.
- Growth against these 3-seed baselines (step 3's real runs, mean of 3 seeds): A −0.84%/yr (−2.07% / +0.12%), B **+0.10%/yr** (−1.37% / +1.24%). Earlier chat estimate for B, from the 1-seed baseline: +0.37%/yr (corrected for the user).
- Growth discussion (input for "growth round 2"): past growth is public and mostly priced in (e.g. Lakonishok, Shleifer & Vishny 1994: fastest past growers did worse afterward); what tends to move prices is growth vs expectations (Roadmap 4). Ideas: growth surprises, multi-year growth, a longer horizon (2y labels exist; noisier); measure growth's weight per year with SHAP first; pick 2–3 variants before any results. Not answered yet: 2 extra growth runs (A, B, seed 42, `--with=growth`) for that SHAP check.

### Residual edge + SHAP on the baselines (2026-10-16, Claude Opus 5.5 Max)

User: "1 yes, go" (2 growth runs + SHAP and residual edge). New scripts: `scripts/residual_edge.py`, `scripts/shap_report.py` (design fixed in their docstrings before results). Outputs: `artifacts/residual_edge/`, `artifacts/shap/`.
- **Growth runs** `v9_pit_with-growth`, `v9_pit_no-rank_label_with-growth` (seed 42, ~25 min with reports): identical to `v8_pit` / `v8_pit_no-rank_label` (2,031,316 predictions, backtest tables), so `--with=growth` reproduces v8.
- **Residual edge** (LightGBM top 10% + buffer, gross monthly, 240 months; primary baseline = equal-weight universe; alternates SPY, EW + 12-1 momentum, SPY + momentum; HAC; 36-month rolling): both **BASELINE_EXPLAINED**, decision-eligible (R² ~0.85).
  - A (3-seed average): loading 0.66 on the equal-weight universe (a calmer copy); alpha **+1.85%/yr, t = 1.03** (seeds +1.7% to +2.0%); cost drag 0.37%/yr, so ~+1.5% net. Active return 2001–08 −1.9%/yr, 2009–20 +4.3%/yr.
  - B: alpha **+0.22%/yr, t = 0.13** (seeds +0.05% to +0.36%); EW + momentum model: 0.48 EW + 0.36 momentum (a momentum mix); cost drag 0.70%/yr, so slightly negative net. Active return −1.6% / +1.4%.
- **SHAP** (all 20 folds, every test row, LightGBM return model, TreeExplainer path-dependent; rebuilt predictions = saved on every fold; additivity error < 1e-14). Added after the first results: *ranking share* (SHAP minus each date's mean), because `history_1y` in B carried a shift shared by all normal stocks (plain share 31% → ranking share 16%). Ranking share by family (top-pick lift in brackets):
  - A: volatility **57%** (+70%; calmer = higher score, direction −0.9), trend 17%, size 13%, stock age 11%, short-term moves 2%, volume 0%. Stable from 2003 on.
  - B: volatility 34% (+26%), trend 32% (**+75%**: price above its 200-day average, 6-month return), size 16% (smaller = higher), stock age 16% (−20%), short-term 2%, volume 0%.
  - Both: stocks with < 1 year of trading (2–4% of rows) are pushed far down (average score percentile 7–20%, ~0% of top picks; checked 2010, 2015, 2020). Last day / week / month return, RSI, 50-day average and volume add up to 4.0% (A) / 3.5% (B) of the ranking weight (~1% with growth on).
  - With growth: growth gets **22%** of the ranking weight in both (A 14–29% by year; B 8–30%, rising to 25–30% in 2016–20) and ~20% of the top-pick lift. Direction is **negative** for growth levels (sales growth 12 months −0.62 A / −0.50 B; gross profit growth −0.25 / −0.66): faster past growth → lower score. Sales acceleration slightly positive (+0.2).
- **Exploratory data check** (no decision rests on it; dev rows 2001–2020, weekly, equal weight per date): fastest 20% sales growers (typical +44%/yr) had the **worst median next-year return vs SPY (−5.8%; −3.4% in 2001–08, −7.4% in 2009–20)** but the most big winners (top 10% next year: 12.6% vs 8–10%) and the most crashes (trailing SPY by > 50%: 11.3% vs 3.5–7%). Quarterly growth: same pattern (−4.7% median, 12.7% big winners, 10.8% crashes). Middle growers did best on the median. So "growth weighs too little" is not the problem: the model already leans on it, and past growth is a lottery ticket (more NVDAs, more crashes). Growth round 2 should look for what separates the winners from the crashers among fast growers (margins → batch 2, earnings surprises / price reaction → Roadmap 4).

### Batch 2 code: margins (2026-10-16, Claude Opus 5.5)

User approved both parts of `docs/BATCH2_PLAN.md` (24 runs: margins alone + growth with margins) and chose to continue on Opus 5.5 (not Fable 5) for this chat. Built before any training:
- `pinky/fundamentals.py`: `MARGIN_FEATURES` (`gm_ttm`, `gm_chg_q`, `om_ttm`, `om_chg_q`; growth's date rules) + generic `shuffle_within_date` (growth's shuffle is now a wrapper, same RNG → old placebo runs reproduce).
- `pinky/pit_dataset.py`: margins attached after growth; dataset rebuilt, v9 backup `pit_dataset_v9.parquet`.
- `pinky/train.py` (VERSION stays v9): `FEATURE_GROUPS` = growth, margins; `placebo` names a group (`--placebo=margins` → tag `placebo-margins`; bare `--placebo` = growth, tag `placebo` as before).
- `scripts/check_margin_features.py` 50/50 (details: `docs/BATCH2_PLAN.md` → Code checks); `check_growth_features.py` still 59/59. `scripts/batch_verdict.py 2` = the locked rule, smoke-tested on existing runs. `shap_report.py` knows the margins family.

### Batch 2 results: margins (2026-10-19, Claude Opus 5.5)

User said `run` (continue on Opus 5.5). 24 runs, all EXIT 0 on the first try, 20 folds each, names and configs checked; no reruns. Runs 14:16–15:25; batch 2 started ~17 min late (batch 1 ended 14:30, batch 2 began 14:47) because the launch block's `wait` also waited on `caffeinate -i -w $$ &` (a child of the same shell that only ends with the shell); killed it after batch 1 finished and kept the Mac awake with a separate `caffeinate -i -w <pid>` (runbook gotcha added). Verdict (`scripts/batch_verdict.py 2`, all / 2001–08 / 2009–20):

| Test | Real (mean of 3) | Placebo (mean of 3) | Real − placebo | Real − baseline |
|---|---|---|---|---|
| Part 1 margins, A | +6.95% / −0.87% / +12.51% | +6.83% / −2.66% / +13.67% | +0.12% / +1.79% / −1.16% | −0.19% |
| Part 1 margins, B | +4.78% / −4.08% / +11.14% | +6.03% / −2.90% / +12.44% | −1.25% / −1.17% / −1.30% | −1.32% |
| Part 2 growth + margins, A | +7.06% / −1.29% / +13.02% | +6.29% / −4.35% / +14.03% | +0.77% / +3.06% / −1.01% | −0.08% |
| Part 2 growth + margins, B | +4.77% / −4.74% / +11.63% | +6.24% / −3.61% / +13.36% | −1.47% / −1.13% / −1.73% | −1.34% |

- **DROP on all 4** (no ON HOLD). Details and paired tests: `docs/WALKFORWARD_RESULTS.md` → v9 batch 2.
- Fast-grower table (`scripts/fast_grower_margins.py`, `artifacts/fast_grower_margins.md`; info only, design fixed 2026-10-19 before running; dev rows 2001–20, top 20% by 12-month sales growth, median growth +42%): all fast growers median −5.8% vs SPY, big winners 12.6%, crashes 11.3% (all stocks −1.4% / 10.0% / 6.8%).
  - Margin change does **not** separate winners: big-winner share is flat across quintiles (11–14%). The extremes are worst: biggest operating-margin rise median −10.3%, crashes 16.0%; biggest fall −7.1%, 13.2%; middle quintiles −2.3% to −4.5%, crashes ~8%. Same with quarterly growth.
  - **Profitability level splits the lottery:** loss-making fast growers (~19% of them) have 17.0% big winners **and** 17.9% crashes (median −8.6%); profitable ones 11.4% / 9.5% (median −4.8%). Unprofitable fast growers are where both the NVDAs and the blow-ups come from.
- Not run (ask first): SHAP / residual edge on the margin runs (finals stay the baselines, already analyzed).

## Product page redesign v2 (2026-10-07, Claude Opus 5.5)

User asked (on Opus 5.5, chose to continue rather than switch to Fable 5): the page still read like an article; make it more concise, more visual, more interactive, then teach them everything on it. User's choices: "a little dark matrix vibe"; hide details behind clicks (keep every fact).
- `product/index.html` rebuilt (v1 kept as `product/index.backup-2026-10-06.html`): dark theme with a one-click light mode (projector fallback, remembered in localStorage); hero with Matrix-style code rain (canvas, a few pink columns = Pinky's picks), typed prompt and a scoreboard; 7 chapters, about one screen each: how it works (2,000-dot canvas machine, 5 auto-playing steps), the test (3-stage "first number fell apart" stepper + 5 rule tabs with an exam-year slider), results (version switch, every-stock overlay, "replay the race", split, report card), lessons (5 cards that open a drawer; calm/hunter switch merged with the sector chart), latest test (result + 4 auto-advancing tabs), progress (clickable timeline + roadmap); pinky promise; FAQ. Keyboard ← → jumps chapters. Height at 1440 px: 7,460 px (v1: 16,400). Still no vendor, model names, thresholds, costs or sector cap.
- Fonts: Geist Mono added (`product/fonts/geist-mono.woff2`, OFL, copied from Next.js in ZerMap's node_modules; license `OFL-GeistMono.txt`); Newsreader no longer used.
- Numbers: new `scripts/product_page_data.py` writes the page's `DATA` block from `artifacts/product_numbers.json` and rewrites the text of every `data-v="path|format"` element (59 bound numbers; first run: 0 differences from the hand-written text). Hand-copied constants, re-checked 2026-10-07 against their sources: v4 +41.2% / v4_ex5 +19.4% / S&P +14.1% (`artifacts/walkforward_summary_v4*.md`), cheat detector 0.0018 / 0.0168 / 0.0002 (`docs/STEP3_RUNBOOK.md`), 59/59 and the terminal lines (check script output), NVDA +29.77% on 2016-11-11 (tr panel), the five famous failures are in the test set (ENRNQ, WCOEQ, LEHMQ, WAMUQ, MTLQQ).
- Checked in headless Chrome over CDP (scratchpad `cdp.py`): 1920, 1440, 1280, 768, 390 px, dark and light, reduced motion; every control clicked; no JS errors, no horizontal overflow. Bug found and fixed: clicking a step before the machine started threw an error.
- `product/presenter-notes.md` rewritten for v2: pitch, a 2-minute seat-side talk track, section-by-section guide, glossary, numbers table, ~30 follow-up Q&As, secret-sauce list (for the user only), tips.
- **Published 2026-10-07** (user: "it needs to be online hosted"): redeployed with the State-log command from a copy in the session scratchpad; the CLI login had expired again ("Not authorized"), the user ran `npx vercel@latest login`, then `deploy --prod` worked. Checked logged out: https://pinky-research.vercel.app returns 200 and is byte-identical to `product/index.html`; both fonts load.

## Product page redesign (2026-10-06, Claude Opus 5.5)

User asked (on Opus 5.5, declined switching to Fable 5): more visuals, more animations, more sections, text and look less "AI", keep the style, no secret sauce; loosely follow the teacher's brief (one-page project spec shown in class, good visuals instead of screenshots, stand out, a live link for Mr. Lake); then teach the user everything on the page.
- `product/index.html` rebuilt: hero with spec sheet, ticker tape, stats band, 11 numbered sections (bar, how it works, the field, the test, build log, where it stands with a version toggle, findings, sectors, latest test v8 with placebo and leak checks, next, FAQ), pinky-promise band; ~20 inline SVG / canvas visuals with scroll animations (reduced-motion and no-JS fallbacks). Still no vendor, model names, thresholds, costs or sector cap.
- Numbers: all recomputed from saved artifacts by `scripts/product_numbers.py` (new; writes `artifacts/product_numbers.json`); the 59 date / leak checks were rerun (59/59). One mistake caught before any preview: the $10,000-growth chart data had been typed by hand; replaced with the computed series and checked point by point.
- Checked in headless Chrome at 1920, 1440, 1280, 768 and 390 px wide: every section and chart reveals, no horizontal overflow, no JS errors.
- Old page kept as `product/index.backup-2026-10-02.html`; presenter study guide `product/presenter-notes.md` (both local only, not uploaded: `.vercelignore` allows only `index.html` and `fonts/`).
- Not published yet: waiting for the user's OK.
- **Local preview in the Claude app:** the app's preview server can't read `~/Desktop` ("Operation not permitted"), so copy `product/` to the session scratchpad (`rsync -a --exclude .vercel product/ <scratchpad>/preview/`) and point `.claude/launch.json` (local only, in `.git/info/exclude`) at that folder: `cd <folder> && exec python3 -m http.server 8766 --bind 127.0.0.1`. Re-copy after each edit. Full-page screenshots: headless Chrome with `--force-prefers-reduced-motion` (everything shown in its final state); phone width needs an iframe wrapper, because Chrome windows can't be narrower than ~500 px.

## User decisions (2026-09-26)

- Phase 2 model fixes: **all four approved** (list under Roadmap).
- Evaluation fixes approved and done in v6_pit: holding buffer, 2020 test block, top-50 / top 10% reports.
- User wants **company data features**, not just price — that is the core of Phase 2.
- Build **step by step** so we can tell what helps. Showcase update **after step 1** (done). GitHub: **don't push yet**.
- Add to every future report (2026-09-27): takeover share of top picks, and 2009–2020 vs SPY (done in `train.py`).
- User confirmed the highest model for Phase 2 (2026-09-26). New chats: ask again before hard work (model rule in `AGENTS.md`).

## Step 2 notes (model fixes — done)

- `train.MODEL_FIXES` = `rank_label`, `rank_features`, `young`, `size`; pit runs use all unless `--without=a,b` (run tagged `no-<fix>`). Legacy runs use none.
- Dataset (`pit_dataset.py`) now keeps stocks with ≥ ~1 month of prices (`SHORT_FEATURES`), adds `history_1y` and `log_mcap` (Sharadar DAILY; verified point-in-time). v6 dataset backup: `data/sharadar/derived/pit_dataset_v6.parquet`.
- Rank features run once before the walk-forward (`preprocess.cross_section_rank`; per-day only, so no leak). Each run saves `artifacts/run_config_<run>.json` (fixes, stock count) for `--report-only`.

## Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr)

- Ridge rank IC **0.052**; Ridge top 10% + buffer **+8.7%/yr** (+7.8% at 25 bps); Ridge top-10 + buffer +8.3%/yr.
- Also check: 2009–2020 vs SPY (Ridge trails: +12.6% vs +14.5%/yr) and the takeover share of top picks (Ridge top-10: 25%; base rate 2.2%).
- Per-portfolio numbers: `artifacts/backtest_stats_1y_v6_pit.csv`. Side by side: `PYTHONPATH=. python scripts/compare_runs.py v6_pit v7_pit`.
- v7_pit (step 2) passes the IC part (0.056–0.063) but not the portfolio part (best top 10% + buffer: LightGBM +7.2%). Top-10 CAGRs are noisy by a few %/yr: judge on IC and top 10% first. Caveat: IC can come mostly from sorting the bottom of the list (v7's did), so a higher IC alone doesn't mean better picks. Check the report's score-group table: does the top group beat the "All stocks" row?
- Never touch the 2022+ holdout until the final test. Caveat: the old 128-stock tests (2018 → Oct 2025) already covered 2022–2025, and the 60% sector cap was picked after seeing them, so the holdout is clean for the pit models but not fully unseen by us.

## Data facts for Phase 2

- Fundamentals ARQ: filing dates 1993 → 2026, 17,045 tickers, revenue filled 97% (ART 92%).
- 9,492 of the 10,043 v6 dataset stocks (95%) have ARQ rows. The v7 dataset has 10,902 stocks (young stocks added).
- `daily.parquet` columns: `marketcap`, `ev`, `evebit`, `evebitda`, `pb`, `pe`, `ps`.
- Pinky pulls 7 Sharadar tables (`sharadar.BULK_TABLES`: tickers, stocks, fundamentals, sp500, actions, daily, events). Not downloaded yet: `metrics` (access confirmed, ~1.4 MB). No insider or institution tables: check plan access before Roadmap batch 7.

## Key findings

### Step 3 — growth features (v8) (2026-10-03)

LightGBM top 10% + buffer, net of 10 bps, mean of 3 seeds (all / 2001–08 / 2009–20). SPY +7.3% (−2.7% / +14.5%); equal-weight universe +8.0%.

| | Real | Placebo | Real − placebo | Without growth (1 seed) |
|---|---|---|---|---|
| A (rank label) | +6.30% / −4.10% / +13.86% | +6.04% / −3.94% / +13.27% | +0.26% / −0.16% / +0.59% | +7.23% / −1.55% / +13.52% |
| B (raw return) | +6.20% / −3.87% / +13.50% | +5.22% / −5.25% / +12.85% | +0.98% / +1.38% / +0.65% | +5.83% / −2.27% / +11.60% |

- **Growth: DROP on both** (bar: ≥ +1.0%/yr overall and ≥ +0.5%/yr per half). B missed by 0.02%/yr; paired monthly test t = +1.19 (A +0.51): not reliable either way. Control reproduced v7 exactly; no leak flag.
- Final versions: A = `v8_pit_no-growth` (+7.23%), B = `v7_pit_no-rank_label` (+5.83%); both continue (gap ≤ 4%/yr). Weekly trading loses at 25 bps → stay monthly.
- Scoreboard (final versions): neither beats +8.7%, SPY in both halves, or the equal-weight universe. Top-10 crashes A 2.3% / B 8.0%; big winners A 3.9% / B 13.4% (random 10%). LightGBM IC > 0 in both halves for both.
- Hint only: real growth lifts LightGBM IC in 2009–2020 (A 0.075 → 0.083, B 0.046 → 0.055; placebo 0.076 / 0.047). Too small for the portfolio bar.
- **Extra columns cost A ~1%/yr, real or fake** (mostly 2001–08). The real-vs-placebo rule can't see this → proposal for the next batch: also require real ≥ the no-new-features baseline (same 3 seeds).
- Placebo cost tilt (info only): fake data turns over more (A 37% vs 34%/month, B 59% vs 52%) but explains only 0.04 / 0.08%/yr of the gap. Gap before costs: A +0.22%, B +0.90%.
- Full write-up: `docs/WALKFORWARD_RESULTS.md`.

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

## Decisions (full, as of 2026-10-03)

- **Data:** Sharadar Core US Equities Bundle — active. Direct API + bulk tables. Key in `.env` (gitignored, never print). License: never share or commit the data.
- **Universe (`pinky/universe.py`):** each day, price ≥ $5 and 21-day avg dollar volume ≥ $5M (nominal $). Common stock + ADRs + Canadian; no preferreds, secondary share classes, or SPACs (SIC 6770); NYSE / NASDAQ / NYSE American only. → **~1,200–2,850 stocks/day (yearly averages), 11,561 distinct** (1998–2026).
- **Delistings:** exit value reinvested in SPY. Bankruptcy / liquidation / regulatory delistings also take **−30%** on the last price (Shumway 1997).
- **Dataset rows:** weekly (every 5th trading day); folds use the daily calendar. Since v7 (`young` fix), stocks are scored after ~1 month of prices; missing long-window features get the day's middle value. v5/v6 needed 1y of history.
- **Sectors:** Sharadar sectors (current classification) for the cap. The custom "Tech/AI" bucket only applies to the old 128-stock universe.
- **Risk:** no leverage. Sector cap 60%.
- **Main signal:** undecided. After step 3 both continue without growth: A (rank label, v7_pit inputs) +7.23%/yr, B (raw return, v7 no-rank_label) +5.83%/yr; drop one only if it trails by > 4%/yr.
- **Locked holdout:** `HOLDOUT_START = 2022-01-01`. Dev runs only use rows whose label ends before it (`train.dev_rows`). Score the holdout once, at the very end.

## Roadmap (full, as of 2026-10-03)

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
1. Growth + revenue acceleration — **tested 2026-10-03 (v8): DROP** on both targets
2. **Margin expansion** ← next
3. Price strength (momentum, 52-week-high proximity, vs sector)
4. Earnings reactions / surprises
5. Reinvestment (R&D/revenue, ROIC)
6. Quality / safety (debt, cash burn, accruals, dilution)
7. Insiders + institutions
8. Industry tailwind
9. Valuation (context only — don't screen out growth)
10. Analyst revisions (expensive; later)

**Phase 3 — only if Phase 2 works:** position sizing, monthly picks report, live paper-trading log.

## Repo layout (full, as of 2026-10-03)

- `pinky/config.py` — universe rules, paths, backtest settings, `HOLDOUT_START`, `DELIST_RETURN_PERFORMANCE`
- `pinky/sharadar.py` — Sharadar API: bulk download → parquet, small queries (key never printed)
- `pinky/universe.py` — point-in-time universe panels, delisting-aware `tr` panel, sectors, SPY, `backtest_prices()`
- `pinky/pit_dataset.py` — weekly features + labels on the point-in-time universe (13 price features + `history_1y` + `log_mcap`; since v8 also the 6 growth features = 21)
- `pinky/fundamentals.py` — growth features from SF1 ARQ/ART (announcement / filing dates, YoY, staleness) + placebo shuffle (`shuffle_growth_within_date`)
- `pinky/preprocess.py` — per-day z-score or percentile rank + correlated-feature drop
- `pinky/walkforward.py` — expanding walk-forward folds + label purge (`calendar` param)
- `pinky/train.py` — Ridge / LightGBM / Blend, report, `pit=True` and `exclude` runs, `dev_rows`, `MODEL_FIXES` (`--without=`), `--seed=N`, `--placebo`, `pit_training_frame`
- `pinky/metrics.py` — IC, top-N, precision@k, winner capture, score groups, calibration
- `pinky/backtest.py` — monthly (or weekly) top-N / top-fraction backtest, costs, sector cap (`sectors` param), holding buffer, stress tests
- Legacy (128 stocks, yfinance): `data_pull.py`, `raw_io.py`, `features.py`, `labels.py`, `dataset.py`
- `scripts/` — `pull_sharadar`, `train_walkforward`, `compare_runs`, `build_showcase`, `check_growth_features` (59 date/leak checks), `step3_verdict` (locked keep-rule), plus legacy build scripts
- `showcase/index.html` — one-page visual (offline), built from v6_pit artifacts by `scripts/build_showcase.py`.
- `product/index.html` — public product page for non-coders (static, hand-written, inline SVG charts, no build step); `product/fonts/` = Newsreader + Libre Franklin (OFL licenses included); `product/.vercelignore` = Vercel upload allowlist; `product/.gitignore` keeps `.vercel/` and `.env*` out of git.
- `data/sharadar/` (~6 GB, gitignored, never share) — tables (`*.parquet`), `zips/`, `panels/` (Date × Ticker), `spy.parquet`, `derived/pit_dataset.parquet`
- `artifacts/`, `models/` — outputs (gitignored). Per run: `walkforward_summary_<run>.md`, `walkforward_metrics_<run>.csv`, `oos_preds_1y_<run>.parquet`, `backtest_stats_1y_<run>.csv`, `backtest_periods_1y_<run>.csv` (monthly returns, v8+), `score_groups_1y_<run>.csv`, `run_config_<run>.json`. Training logs: `artifacts/logs/train_<run>.log` (last line `EXIT <code>`). Step 3 verdict: `artifacts/step3_verdict.md`. `models/1y_<tag>/` holds only the **last fold's** models per tag (~440 KB; `1y_pit` = latest full pit run, overwritten; ablations get `1y_pit_no-<fix>`, seeds / placebo get their own folders). After step 3, `1y_pit` and `1y_pit_no-rank_label` hold v8 models (with growth); v7's are in `1y_pit_v7` and `1y_pit_no-rank_label_v7`.
- `docs/` — `WALKFORWARD_RESULTS.md`, `ARCHITECTURE.md`, `PRD.md`, `EVAL.md`
- `AGENTS.md`, `.cursor/rules/` — agent instructions. `graphify-out/` — knowledge graph.
- Agent add-ons (2026-10-02; untracked, don't commit). Skills in `.agents/skills/` (listed in `skills-lock.json`):
  - `residual-edge-analyzer`: does a portfolio beat SPY / equal-weight / momentum beyond their exposure? Needs one dated monthly CSV (strategy + baselines on each row, same cost basis). Since v8, every run saves `artifacts/backtest_periods_1y_<run>.csv` (per month: net, gross, SPY, equal-weight universe, for every signal × portfolio, incl. Momentum 12-1) → pivot it; older runs get the file via `--report-only`. Use gross for all columns (SPY and equal-weight carry no costs).
  - `shap`: which features drive LightGBM. **Installed 2026-10-03** (user asked): `shap[plots]==0.52.0` into the existing `.venv` (Python 3.12.0), also in `requirements.txt`. 29 packages added (shap, numba, llvmlite, slicer, tqdm, packaging, matplotlib, IPython + their dependencies); nothing removed or changed (numpy, pandas, scipy, scikit-learn, lightgbm same); `pip check` clean; smoke test on a small LightGBM passed (additivity OK). No Pinky code imports matplotlib / IPython / psutil. Don't follow the skill's `uv venv` step (it makes a new environment). Only last-fold models are saved (see runbook step 8).
  - None of these add-ons change training; they are for checking results afterwards.
  - `verification-before-completion`, `systematic-debugging` (obra/superpowers).
  - Context7 plugin (current library docs), enabled for Pinky in `.cursor/settings.json`. `.graphifyignore` keeps `.agents/` out of the graph.

## Other notes moved from project.md (2026-10-03)

- Last updated **2026-10-03**. Phase 1 code: `c0cdfe7`. Phase 2 step 1 (v6_pit): `5be6e83`. Showcase + report checks: `cf84035`. Step 2 (v7_pit): `9030d73`. Score-group table: `340e866`. Step 3 plan locked 2026-10-03; **step 3 code + date/leak checks done 2026-10-03 (all pass): `349d0d6`**; v8 dataset built. **Step 3 trained 2026-10-03 (13 runs, all clean): growth DROP on A and B → both continue without growth, monthly trading. See Key findings → Step 3.** Results commit: `66e83c7`.
- Legacy: `pull_data.py` → `build_features.py` → `build_labels.py` → `build_dataset.py` → `train_walkforward.py` (`--ex-winners` drops hindsight winners)
- Tip: use one chat at a time on Pinky (parallel chats can overwrite each other's edits). On 2026-09-26/27 two chats worked in turn, which confused where work happened. On 2026-10-03 the training chat committed `66e83c7` and `0a0a0a8` while another chat restructured docs (the docs chat paused, then based its edits on `0a0a0a8`).
- Long chats get auto-summarized by Cursor (the agent then works from a summary; the full record is still saved). One very long chat also got a "Request blocked by Anthropic" error on a harmless question (likely a false positive). Fix for both: start a new chat — it picks up from `project.md`. On 2026-10-03 the long step-3 chat lost track (it forgot it had started `fundamentals.py`), so before resuming, check `git status` and file times, not just the chat.
