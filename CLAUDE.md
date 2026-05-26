# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A monorepo of reusable, harness- and LLM-agnostic instruction modules ("skills") packaged in the [SKILL format](https://agentskills.io/specification) — YAML frontmatter + Markdown body. Each top-level subdirectory is one self-contained skill; there is no shared build, no root `package.json`, and no CI. Skills are consumed either by dropping the folder into an agent's skills directory (e.g. `~/.claude/skills/<name>/`) or by pasting `SKILL.md`'s body into a non-SKILL-aware instruction surface (Cursor rules, Copilot instructions, etc.).

Current skills: [`generate-tasks-json/`](generate-tasks-json/), [`github-cli/`](github-cli/), [`mutation-analyzer/`](mutation-analyzer/). The root [`README.md`](README.md) is the up-to-date inventory.

## Per-skill anatomy (and what to keep in sync)

Each skill directory contains:

- `SKILL.md` — the actual prompt body, with YAML frontmatter declaring `name`, `description`, and (sometimes) `license`. The `description` is the **trigger contract** — it's what causes a SKILL-aware harness to route a user request to this skill. Editing it changes activation behavior; treat it like a public API.
- `README.md` — human-facing overview, install matrix, design rationale.
- `evals/evals.json` — generic eval suite where each entry's `_probes` field names the specific rule from `SKILL.md` (or `METHODOLOGY.md`) that the eval enforces. When a rule changes, the corresponding eval must change with it.
- `LICENSE` — MIT, per-skill (each carries its own).

When modifying any rule in a `SKILL.md`, audit `README.md` and `evals/evals.json` in the same skill for drift — they encode the same rules in three different registers (prompt, human doc, executable check).

## The one skill with code: `generate-tasks-json`

Node.js ≥ 18, ESM (`"type": "module"` in `package.json`), zero runtime deps beyond the `gh` CLI. The entry point is `create-issues.js`.

```bash
# From inside generate-tasks-json/ (or pass --file <path>):
REPO="<org>/<repo>" MILESTONE="v1" node create-issues.js --dry-run     # validates, prints planned issues, NO API calls
REPO="<org>/<repo>" MILESTONE="v1" node create-issues.js               # live run; prompts for typed 'yes'
REPO="<org>/<repo>" MILESTONE="v1" node create-issues.js --resume      # resume after interruption (state in .create_issues_state.json)
REPO="<org>/<repo>" MILESTONE="v1" node create-issues.js -y            # skip confirmation (CI)
REPO="<org>/<repo>" MILESTONE="v1" node create-issues.js --file path/to/tasks.json
```

`REPO` is required; `MILESTONE` defaults to `v1` and must already exist on GitHub.

There is no linter, formatter, or test runner configured. "Testing" the script means running `--dry-run` against a real `tasks.json` and inspecting the output.

## Two non-negotiable execution rules baked into the skills themselves

These are enforced by the bundled SKILL.md files and override any auto-execute bias:

1. **Never invoke `create-issues.js` without `--dry-run` yourself.** The live run creates real GitHub issues — a write action. Show the user the dry-run output and the live command; let them invoke the live run. (Source: `generate-tasks-json/SKILL.md` → "Validate".)
2. **Every state-changing GitHub action requires explicit per-action user approval** — push, comment, review submit, issue create/close, merge, release, label edit. Read-only `gh` calls (`gh pr view`, `gh issue list`, `gh pr diff`, drafting locally) are frictionless. Positive feedback on a draft ("looks good") is not approval to submit. (Source: `github-cli/SKILL.md` §4–§5.)

If you are editing a SKILL.md and tempted to soften either rule, re-read the README's "Why these design choices" section first — each rule fixes a documented failure mode.

## Issue-planning work in this repo

If the user asks you to draft a `tasks.json`, plan a milestone, or batch-create GitHub issues, the binding rules live in [`generate-tasks-json/METHODOLOGY.md`](generate-tasks-json/METHODOLOGY.md) (two-level hierarchy, contract-as-seam decomposition, single-prefix sub-issues, one assignee per issue, curated label set). Read it in full before drafting — `generate-tasks-json/SKILL.md` is the mechanics; `METHODOLOGY.md` is the policy and wins on any conflict.
