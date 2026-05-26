# github-cli

A reusable instruction module for AI coding agents that disciplines **every
GitHub interaction**: PRs, issues, reviews, comments, merges, releases. Not a
single workflow — a baseline rule set that overlays on top of whatever PR or
issue skill is in play.

Packaged in the [SKILL format](https://agentskills.io/specification) (YAML
frontmatter + Markdown body), harness- and LLM-agnostic. The body of
`SKILL.md` is a self-contained system prompt you can drop into any agentic
coding assistant (Claude Code, Codex, Cursor, Cline / Roo Code, Aider, GitHub
Copilot, Gemini CLI, custom GPTs, raw API calls, …). See
[Install](#install) below for the per-tool matrix.

---

## Why this exists

GitHub is a **shared, public-facing system**. Anything an agent posts — a
review, a comment, a merge, an issue close — is visible to other humans the
moment it lands, and is awkward (often impossible) to retract cleanly. The
default failure mode of an undisciplined agent on GitHub is not "it didn't
do enough"; it is "it did too much, too fast, with no warning, and now the
PR author has been pinged with the wrong review."

Three failure modes recur:

1. **Reaching for scraping or raw `curl` when `gh` would have worked**, which
   breaks the moment GitHub touches its markup or auth flow.
2. **Parsing the human-readable `gh` output**, which breaks the moment a
   field wraps, a title contains spaces, or `gh` changes a column header.
3. **Treating "let's review this PR" as approval to submit a review**, which
   posts unretractable content to a public surface before the user has even
   read the draft.

This skill encodes the rules that prevent each.

---

## The rules at a glance

| #   | Rule                                       | Why                                                                                                            |
| --- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| 1   | Use the `gh` CLI                           | Uniform auth, pagination, rate limits; scraping and hand-rolled `api.github.com` calls are brittle.            |
| 2   | Prefer `--json` for parsing                | Text output is for humans and changes without warning; `--json <fields>` is a stable contract.                 |
| 3   | Remote safety check before push/pull       | Pushing to the wrong remote is unrecoverable; `git remote -v` is one command.                                  |
| 4   | **Mandatory approval before any mutation** | GitHub state changes are public and unretractable; default to caution and let the user unlock each one.        |
| 5   | Read-only ops are frictionless             | `gh pr view`, `gh issue list`, drafting locally — no approval theater; the gate is on **submission**, not on **reading**. |

Plus a **mental model**: every turn is either *draft mode* (the default,
nothing posted) or *ready to submit* (the exception, user just unlocked one
specific action). End each draft with an explicit handoff sentence so the
gate is visible.

The full text — including approval-phrase examples, what does NOT count as
approval, and the read-only allowlist — lives in `SKILL.md`.

---

## Why these design choices

A few decisions look conservative but each fixes a specific failure mode:

**Per-action approval, not session-level approval.** "You can comment on this
PR" does not generalize to a different PR or a different action on the same
PR. Approvals are scoped narrowly because that is where the failure mode
lives — a blanket "yes" gets reused for an action the user did not actually
sanction.

**Positive feedback on a draft is not approval to submit.** "Looks good" /
"nice" / "perfect" are reactions to the draft, not commands. An agent that
treats them as submit signals will sooner or later post a review the user
was still composing in their head.

**Drafting locally is explicitly allowed.** The skill does not want to make
read-and-think workflows expensive. The rule is on **submission**, not on
**reading** or on **composing**. An agent that asked for approval before
running `gh pr view` would be useless; an agent that asked before running
`gh pr review --approve` is exactly right.

**`gh api` is named as the escape hatch.** When `gh` does not cover an
operation, the right move is `gh api` (same auth, same JSON pipeline), not
raw `curl`. Naming this in the skill prevents a well-intentioned model from
inventing its own API client.

**Approval phrases are listed, not left implicit.** "Post it", "Submit",
"Send", "Approved, go ahead" are the recognized green lights. Ambiguous
phrases are explicitly *not* approval. This removes the most common
rationalization path: "well, they said 'sounds good' — that's close enough."

---

## Relationship to other skills

This skill is a **baseline policy**, not a workflow. It composes with
workflow skills that touch GitHub — for example, a code-review skill, a PR
description generator, or a release runbook. Those skills define *what* to
do; this one defines *how* to interact with GitHub while doing it.

If a workflow skill says "submit the review" and the user has not approved
it, this skill wins. The workflow can stage every byte of the review body;
the post still waits on the user.

---

## Adapting to a new project

There is nothing to adapt. Unlike skills that bake in a project-specific
constraint file or naming convention, the rules here apply uniformly across
repos and orgs. Drop `SKILL.md` in and go.

The one thing worth checking is whether your project has org-specific
write-gating policies (e.g. CODEOWNERS rules, branch protection that
requires a human approver) that *strengthen* the defaults here. Those still
apply — this skill is the floor, not the ceiling.

---

## Files in this repo

- `SKILL.md` — the instruction module itself. YAML frontmatter (`name`,
  `description`, `license`) plus a Markdown body containing the five rules
  and the draft-mode / ready-to-submit mental model.
- `evals/evals.json` — a generic eval set probing each rule (CLI choice,
  JSON output, remote safety, mutation approval, read-only frictionlessness,
  mode discipline). The schema is the common `evals.json` shape consumed by
  skill-builder tooling and eval harnesses.
- `LICENSE` — MIT.

---

## Install

1. **Copy this folder** into your agent's skills directory or instruction
   surface (see the matrices below).
2. **Reload your agent**, if it does not auto-detect new skills. The skill
   auto-activates on GitHub-touching phrasing in SKILL-aware harnesses; in
   others it should be loaded as a standing rule (see
   [Triggering](#triggering)).

### Native SKILL install (SKILL-aware harnesses)

Copy the folder into the agent's skills directory, per-project or
user-global:

| Harness     | Project scope                                     | User scope                       |
| ----------- | ------------------------------------------------- | -------------------------------- |
| Claude Code | `<your-repo>/.claude/skills/github-cli/`          | `~/.claude/skills/github-cli/`   |
| Codex       | `<your-repo>/.agents/skills/github-cli/`          | `~/.agents/skills/github-cli/`   |
| Other       | Whatever directory your harness reads skills from | Same, in the user-global location |

### Instruction-surface install (everything else)

The body of `SKILL.md` (everything after the YAML frontmatter) is a
self-contained system prompt with no harness-specific runtime dependencies —
it only assumes the agent can shell out to `gh` and `git`.

Drop it into whichever instruction surface your tool exposes:

| Tool                        | Where to put the SKILL.md body                       |
| --------------------------- | ---------------------------------------------------- |
| Cursor                      | `.cursor/rules/github-cli.mdc` (or `.cursorrules`)   |
| Cline / Roo Code            | Custom Instructions panel                            |
| Aider                       | `--read SKILL.md` or include in `CONVENTIONS.md`     |
| GitHub Copilot Chat         | `.github/copilot-instructions.md`                    |
| Gemini CLI                  | `GEMINI.md` at repo root                             |
| Custom GPT / Claude Project | Paste into the system instructions / project knowledge |
| Any LLM via API             | Prepend as `system` message                          |

Because this is a baseline policy rather than a discrete workflow, it works
best loaded **always-on** rather than as a triggered skill — the rules
should be in scope every time the agent considers a GitHub action, not just
when it remembers to look them up.

---

## Triggering

In SKILL-aware harnesses, the skill auto-activates on GitHub-touching
phrasing:

- "Review this PR" / "look at PR #412"
- "Open a PR for this branch"
- "Comment on the issue"
- "Merge it" / "close that issue"
- "Push the branch"
- Any `gh ...` command the user mentions or asks you to run
- Any github.com URL pasted into the conversation

If your harness supports always-on / standing rules, prefer that over
triggered activation — the discipline matters most on the actions the agent
**did not realize** were GitHub-mutating, which is exactly the case where
keyword triggering misses.

---

## License

[MIT](./LICENSE). Use it, fork it, adapt it to your stack — no attribution
required but appreciated. PRs welcome, especially for adaptation notes for
tools not listed above.
