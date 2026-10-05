# Claude instructions (Pinky)

Core rules (always on):

@AGENTS.md

## Claude app notes

Pinky moved from Cursor to the Claude app on 2026-10-04. These notes adapt the core rules to Claude.

- **Sessions:** Code tab, **Local** environment, folder `~/Desktop/Pinky`. Never Cloud: it runs on Anthropic's servers without Pinky's data, and the Sharadar license forbids sharing the data. One chat at a time on Pinky, Cursor included.
- **Model (rules 13–14):** the top model is `best` (Fable 5.1 where the plan has it, otherwise the newest Opus). `.claude/settings.local.json` makes it the start model and forces every subagent onto it; in the Claude app, the model dropdown next to Send sets the session's model. Before hard work, check which model this session runs. If it isn't the top one (for example after a fallback or a manual switch), stop, ask the user to switch (dropdown, or `/model best`), and wait.
- **Subagents (rule 15):** the built-in Explore and Plan subagents skip `CLAUDE.md` and `AGENTS.md`. Use them only for read-only searches, or paste the rules they need into the prompt. Other subagents get these rules automatically.
- **Shell:** each Bash call starts a fresh shell; only the working folder carries over. Start every command that runs Python with `source .venv/bin/activate &&`. Background commands stop after 30 min unless you pass a longer `timeout` (max 2 h).
- **Skills:** `.claude/skills/` (most are links to `.agents/skills/`). Graphify guidance is the `graphify` skill.
- **Pinky's Claude settings:** `.claude/settings.local.json` (never commit). What it sets: `project.md` → Gotchas → Claude setup.
