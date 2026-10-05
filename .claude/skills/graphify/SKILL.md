---
name: graphify
description: Graphify knowledge graph (graphify-out/). Use it for code questions that span several files; skip it when you already know the file. Run `graphify update .` after code changes.
---

# Graphify

- **Use it** for codebase or architecture questions that span several files, before broad Read / Grep / Glob searches. The graph shows cross-file links and inferred edges that Grep and Read miss.
  - `graphify query "<question>"`: scoped subgraph for the question
  - `graphify path "<A>" "<B>"`: dependency path between two symbols
  - `graphify explain "<concept>"`: all nodes related to a concept
- **Skip it** when you already know the file(s) to read or edit, or when `graphify-out/graph.json` doesn't exist.
- If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files.
- Read `graphify-out/GRAPH_REPORT.md` only for a broad architecture review, when query / path / explain don't surface enough.
- When a subagent will explore code across several files, tell it to use graphify too.
- After changing code files, run `graphify update .` (AST-only, no API cost).
- `graphify` isn't on the shell PATH: run it as `/Users/hqschool/Library/Python/3.12/bin/graphify …` (in Claude, an `export PATH` doesn't carry over to the next command).
