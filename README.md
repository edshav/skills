# skills

A collection of reusable instruction modules ("skills") for AI coding agents — each one a self-contained directory with a `SKILL.md` ([SKILL format](https://agentskills.io/specification)) plus any supporting code or docs.

Each skill is harness- and LLM-agnostic. Drop the folder into your agent's skills directory (e.g. `~/.claude/skills/` for Claude Code, `~/.agents/skills/` for Codex, or the equivalent for your tool), or paste the body of `SKILL.md` into your agent's instruction surface (Cursor rules, Aider conventions, custom GPT system prompt, raw API `system` message, …). See each skill's README for the full per-tool install matrix.

## Skills in this repo

| Skill                                         | What it does                                                                                                                                                                                                                                                                            |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`mutation-analyzer`](mutation-analyzer/)     | Turns the agent into an investigative staff engineer for **mutation-oriented** code analysis — "if I change X, what breaks, where does it silently corrupt, and where does it loudly fail?" Persists structured, code-grounded knowledge files under a `wiki/code-analysis/` directory. |
| [`generate-tasks-json`](generate-tasks-json/) | Bulk-creates well-structured GitHub issues from a single JSON file, plus the **planning methodology** (contract-as-seam decomposition, two-level hierarchy, one Feature + two contract sides by default) that the agent applies when drafting that JSON.                                |

Each skill ships with a generic `evals/evals.json` probing the rules it enforces — customize the placeholders to refer to real entities in your codebase and run with the eval harness of your choice.

## Layout

Each skill is its own self-contained directory.

Start with each skill's `README.md` for the overview, then `SKILL.md` for the actual prompt body.

## Installation

Two common modes per skill, regardless of harness:

- **Native SKILL install** (Claude Code, Codex, other SKILL-aware harnesses): copy the skill folder into the agent's skills directory — per-project (e.g. `<your-repo>/.claude/skills/<skill-name>/`, `<your-repo>/.agents/skills/<skill-name>/`) or user-global (e.g. `~/.claude/skills/<skill-name>/`, `~/.agents/skills/<skill-name>/`).
- **Instruction-surface install** (Cursor, Aider, Copilot, Gemini CLI, custom GPTs, raw API): paste the body of `SKILL.md` into the agent's instruction surface — see each skill's README for the per-tool path.

Most SKILL-aware harnesses auto-load skills on session start; trigger phrases declared in the frontmatter route automatically. In tools without auto-trigger metadata, invoke the skill explicitly (each skill's README documents its trigger phrases and explicit mode prefixes where applicable).

## Contributing

Open an issue or PR. New skills welcome — see [`mutation-analyzer`](mutation-analyzer/) and [`generate-tasks-json`](generate-tasks-json/) for the file layout to imitate.

## License

[MIT](./LICENSE). Each skill also carries its own LICENSE.
