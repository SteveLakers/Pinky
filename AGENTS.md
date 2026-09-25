# Agent instructions (Pinky)

1. **Read `project.md` first.** It is the source of truth for goals, status, and rules.
2. **Use the highest AI models.** Go very heavy on the strongest models for reasoning, planning, decisions, and thinking. The user does not care about token cost. Hard sub-work → subagents on the strongest model; pass this instruction to every subagent.
3. **Stop and ask** the user to switch Cursor from Auto to the highest model before any hard task — and if a task turns hard mid-way, stop at a safe point and ask. Wait for their reply before doing the work (unless they say continue).
4. Follow all rules in `.cursor/rules/` (honesty, concise bullets, ask before large decisions, graphify first).
