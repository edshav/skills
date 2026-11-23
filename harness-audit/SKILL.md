---
name: harness-audit
description: >
  Use when the user wants a project's agent harness (Claude Code, Codex, Cursor or similar)
  audited against agentic-engineering ideas: proactive triggers, near-loop decision points,
  specialised subagents, damage control, observability. Triggers on "audit the harness",
  "what can run without me", "improve our Claude Code setup with agentic ideas",
  "/harness-audit". DO NOT trigger for a code review, a repo-wide code quality audit, a
  single-file change, or general automation recommendations or first-time setup of an agent
  tool.
license: MIT
---

# Harness audit

Find which ideas from [`ideas.md`](ideas.md) would pay off in this project's agent
harness, and propose a short ranked list of changes. This is an audit: change nothing until
the user picks.

## Steps

1. Read [`ideas.md`](ideas.md) in full. It is the only source of ideas. Its mechanism lines
   name Claude Code features. The project's harness is the one its instruction files and
   config folders are written for, not the agent running the audit. When that is another
   harness, map each idea to its equivalent, and write "no equivalent" in the proposal row or
   the idea's "Not now" line where it has none.
2. Inventory the current harness, read-only:
   - every agent instruction file in the repo (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, Cursor
     rules, Copilot instructions) and each harness's config folder (`.claude/`, `.codex/`,
     `.cursor/`, `.github/` agent files or similar: agents, skills, commands, hooks, settings);
   - automation around it: CI config, `Makefile` / package scripts, dev and deploy scripts,
     test commands;
   - what already runs unattended (scheduled jobs, bots, CI checks);
   - the parts of the harness outside the repo: where an instruction file routes work to
     another place as part of the workflow (sessions it messages or hands off to, a folder it
     sends questions to), read that place's instruction files and config too; where it reads
     decisions from a shared record, read the record. One hop only. A path cited for reference
     alone (a doc, an upstream clone, an example) stays outside the inventory.
3. Find where the human is the bottleneck, from evidence in the repo or a linked part read in
   step 2: recent `git log`, TODO/FIXME clusters, manual steps described in READMEs or docs,
   recurring kinds of commits (dependency bumps, flaky-test fixes, doc fixes). If `gh` works here, recent issues and PRs
   count too. Read only, never post.
4. Answer each of the nine "Questions for a harness audit" in `ideas.md` with a short answer
   and the evidence (file path, command or commit). "No evidence" is a valid answer.
5. Propose at most 7 changes, ranked by value for effort.

## Rules

- A proposal needs evidence of the need in this repo or a linked part read in step 2. An idea
  that merely sounds good is not one; list it under "Not now" with one line.
- Prefer what the project and its harness already have (existing scripts, skills, agents,
  hooks) over new machinery. The smallest version that does the job.
- Do not recreate the Tiny Software Factories (TSF) web app or its UI. Take the ideas, not
  the product.
- Follow this project's own agent instructions (`CLAUDE.md`, `AGENTS.md` or equivalent) where
  they conflict with `ideas.md`.
- Anything that acts unattended on production, money, user data or outside services needs an
  approval point in the proposal (idea 3) and narrow tools (idea 8).
- Mark guesses as guesses.

## Output

1. **Current harness:** 5–10 lines on what exists and what already runs without a human,
   naming each linked part outside the repo that was read, or could not be read.
2. **Audit answers:** the nine questions, one or two lines each, with evidence.
3. **Proposals:** a table with: rank, idea # from `ideas.md`, the change in one sentence, files
   it touches or creates, effort (S/M/L), value and why, risk, and how we would know it works.
4. **Not now:** ideas considered and skipped, one line each with the reason.

Then stop and wait for the user to pick.

## After the user picks

Implement the picked changes one at a time, in the smallest version that works. Verify each
(run it, or trigger it once) before starting the next, and report what was verified and what
was not.
