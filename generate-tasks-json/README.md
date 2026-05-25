# generate-tasks-json

Bulk-create well-structured GitHub issues from a single JSON file — and a planning discipline that keeps issue trees small, readable, and aligned with how the work actually ships.

Two things, sold together:

1. **A script** (`create-issues.js`) that reads a `tasks.json` file and creates GitHub issues for you in bulk via the official `gh` CLI — parents, sub-issues, sub-issue links, issue types, labels, assignees, milestone.
2. **A planning methodology** ([`METHODOLOGY.md`](METHODOLOGY.md)) that constrains _what_ you write into that JSON file: two-level hierarchy, one Feature + the two sides of its data contract by default, single-prefix sub-issues, one assignee each.

Without (2), (1) is just a batch creator and you end up with sprawling thirty-issue feature trees nobody can navigate. With (2), the file you hand the script is small and easy to review before any real GitHub state is created.

Packaged in the [SKILL format](https://agentskills.io/specification) (YAML frontmatter + Markdown body), harness- and LLM-agnostic — drop into any agentic coding assistant (Claude Code, Codex, Cursor, Aider, custom GPTs, raw API, …) or run the script by hand.

---

## Why this exists

Most feature work in a typical web app has the same shape: something **produces** data, something else **consumes** it. The natural seam for splitting that feature into issues is the **contract between the producer and consumer** — _not_ the underlying layers (DB, service, controller, view).

Splitting along the contract gives you:

- Exactly the number of issues you need (usually two: producer side, consumer side).
- An explicit, reviewable interface between sub-issues.
- Balanced load — you can fatten the contract to move computation to whichever side has slack.

Splitting along layers gives you:

- One issue per package or module that touches the feature.
- Nobody knows the boundary until the PRs collide in review.
- Chronic over-decomposition.

The methodology codifies the contract-as-seam discipline plus the surrounding hygiene (assignment, labels, naming, hierarchy depth) so the team doesn't relitigate it every milestone. The script is the cheapest way to apply it consistently across a milestone — write one JSON file, get the same structured issue tree every time.

See [`METHODOLOGY.md`](METHODOLOGY.md) for the full rules.

---

## What's in the box

| File                                       | Purpose                                                                                  | Audience                  |
| ------------------------------------------ | ---------------------------------------------------------------------------------------- | ------------------------- |
| `README.md`                                | This file — what it is, why, how to install / use                                        | humans                    |
| [`METHODOLOGY.md`](METHODOLOGY.md)         | The binding planning rules (hierarchy, contract-as-seam, prefixes, assignment, labels)   | humans + AI coding agents |
| [`SKILL.md`](SKILL.md)                     | How to mechanically draft a `tasks.json` for the script — written as a SKILL              | AI coding agents          |
| [`create-issues.js`](create-issues.js)     | The Node.js script that consumes `tasks.json` and creates the GitHub issues              | run via `node`            |
| [`tasks.example.json`](tasks.example.json) | A worked example: one Feature + two contract sides + a `[DOCS]` follow-up                | humans                    |
| [`package.json`](package.json)             | Marks the script as ESM so `import` works                                                | Node                      |
| `LICENSE`                                  | MIT                                                                                      |                           |

---

## Install

Prerequisites:

- Node.js ≥ 18
- The official GitHub CLI: `brew install gh && gh auth login`

Drop this folder wherever is convenient:

- **Inside a single project** that uses the methodology: `<your-repo>/.github/scripts/generate-tasks-json/` (or just `.github/scripts/`).
- **As a native SKILL available to all your projects**: into your agent's user-global skills directory — e.g. `~/.claude/skills/generate-tasks-json/` (Claude Code), `~/.agents/skills/generate-tasks-json/` (Codex), or your harness's equivalent.
- **Standalone**: clone this repo and run the script with `--file` pointing at any `tasks.json`.

The script has no runtime dependencies beyond `gh` and Node built-ins — `package.json` exists only to mark it as ESM.

---

## Use

1. **Read [`METHODOLOGY.md`](METHODOLOGY.md) first** if you've never used this before. It is short.
2. **Write `tasks.json`** — see [`tasks.example.json`](tasks.example.json) for the shape. AI coding agents should use [`SKILL.md`](SKILL.md).
3. **Validate with a dry-run** — no GitHub API calls, deterministic mock issue numbers, fully reviewable:
   ```bash
   REPO="your-org/your-repo" MILESTONE="v1" node create-issues.js --dry-run
   ```
4. **Run for real** — pauses for a typed `yes` confirmation:
   ```bash
   REPO="your-org/your-repo" MILESTONE="v1" node create-issues.js
   ```
5. **If interrupted**, resume without creating duplicates (state lives in `.create_issues_state.json`):
   ```bash
   REPO="your-org/your-repo" MILESTONE="v1" node create-issues.js --resume
   ```

**Environment variables** — `REPO` is required (`<org>/<repo>`); `MILESTONE` is optional (defaults to `v1` and must already exist in the repo).

**CLI flags** — `--file <path>` (defaults to `./tasks.json`), `--dry-run`, `--resume`, `-y` / `--yes` (skip confirmation prompt — for CI).

---

## Installing in other harnesses (instruction-surface install)

The body of `SKILL.md` (everything after the YAML frontmatter) is self-contained with no harness-specific runtime dependencies — it only assumes the agent can read and write files in the working directory and run `node create-issues.js`.

Drop it into whichever instruction surface your tool exposes:

| Tool                        | Where to put the SKILL.md body                              |
| --------------------------- | ----------------------------------------------------------- |
| Cursor                      | `.cursor/rules/generate-tasks-json.mdc` (or `.cursorrules`) |
| Cline / Roo Code            | Custom Instructions panel                                   |
| Aider                       | `--read SKILL.md` or include in `CONVENTIONS.md`            |
| GitHub Copilot Chat         | `.github/copilot-instructions.md`                           |
| Gemini CLI                  | `GEMINI.md` at repo root                                    |
| Custom GPT / Claude Project | Paste into the system instructions / project knowledge      |
| Any LLM via API             | Prepend as `system` message                                 |

In tools without auto-trigger metadata you'll need to invoke the skill explicitly ("draft a `tasks.json` for X") rather than relying on keyword routing. Everything else — the workflow, the validation cheat-sheet, the dry-run-first rule — is enforced by the prompt itself, not by the host.

---

## Adapting to your project

The methodology is generic but you will likely want to customize a few things in `METHODOLOGY.md`:

- **Sub-issue prefixes** (`[API]`, `[DB]`, `[UI]`, `[WS]`, `[DATA]`, `[DOCS]`) — these match a typical web app; rename, drop, or extend for your stack (e.g. add `[INFRA]`, `[MOBILE]`, `[ML]`).
- **Prefix → assignee mapping** (§7.2) — which login picks up which prefix by default for your team.
- **Allowed labels** (§7.6) — the methodology assumes a small fixed set. Edit it to match the labels that actually exist in your repo. **The script will fail if you specify a label that does not exist on GitHub** — that is intentional, it forces the allowed set to stay curated.
- **Spec / design-doc sourcing** (in `SKILL.md`) — if your project has structured specs or design docs, specialize the "Sourcing issue content" section to point at them so the agent lifts content verbatim instead of paraphrasing.

The script itself shouldn't need editing for most uses.

---

## How the script works (one paragraph)

`create-issues.js` reads `tasks.json`, validates the shape (unique ids, valid types, parents resolve), then for each task: creates the GitHub issue via `gh issue create`, sets its issue-type via the GraphQL API (`Feature` for parents, `Task` for others), and for sub-issues links them to the parent via the native sub-issues API (with a comment-based fallback if that fails). Progress is persisted to `.create_issues_state.json` after each successful issue so `--resume` can pick up exactly where a failed or interrupted run stopped. Rate limits and `502` / `503` are handled with exponential backoff. Dry-run skips all API calls and uses deterministic mock issue numbers so the output is reproducible and reviewable.

---

## License

[MIT](./LICENSE). Use it, fork it, adapt it to your stack — no attribution required but appreciated.
