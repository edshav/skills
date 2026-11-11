# lanes

A reusable instruction module for AI agents that runs a multi-PR effort as one
**coordinator** session plus parallel **lane** sessions, each lane owning a slice of the
PRs in its own worktrees.

Packaged in the [SKILL format](https://agentskills.io/specification) (YAML frontmatter +
Markdown body), harness- and LLM-agnostic. See [Harness requirements](#harness-requirements)
for what it assumes.

---

## When to use it

Many PRs across several code areas that can move in parallel. It pays off most when the
work outlives any single session, and when one maintainer reviews PRs in batches.

One area worked in sequence fits one session. A bounded task whose answer fits a paragraph
fits a subagent.

An example of the shape: moving a GUI wallet off a vendored, patched fork of its backend
onto released versions, through many small PRs to a repo someone else maintains.

---

## What it does

1. **Preparation.** A plan file, kept out of git, with an inventory of every change, a
   spec, a PR map (inventory row → PR → branch → commit), lanes cut by code area with
   overlap checked at function level, merge order (and batches), and the review process
   agreed with the client, if any, and the maintainer.
2. **Starting a lane.** A model per lane, a worktree and branch per PR, a named session in
   a terminal multiplexer, and a first prompt from [`brief.md`](brief.md).
3. **The coordinator.** Writes no code: keeps the plan and statuses, routes briefs and
   answers, drafts the client's and maintainer's messages, checks each PR against its
   inventory rows, asks for audit passes.
4. **Shared state in files**: the plan, an "After a merge, do" table, an embargo ledger,
   pre-PR results, a heavy-run lock, a container for outside contributors' code.
5. **Ending a phase** with an inventory round across every lane; process ideas come back
   as proposals naming where they would land, this skill included.

## Supervised first version

This version runs supervised in the coordinator: through preparation and lane start, the
coordinator proposes each decision (each plan section; each lane's model, placement and
brief text) and acts on it after the user's go-ahead. Lanes run at their usual pace. The
point is to watch the method run a few times and correct it; autonomy can grow later by
removing items from the decision list in `SKILL.md`.

---

## Why these design choices

Each rule fixes a failure observed on a real multi-lane effort.

- **Decide in a file, then act.** Sessions die, get renamed and get compacted. A step
  "after PR Y merges, do X", an embargoed branch or a pre-PR result kept only in session
  memory was lost with the session. Every such piece of state now has a file and an owner.
- **Map lanes by worktree and PRs, not session names.** Sessions were renamed mid-effort,
  and a dead coordinator left a lane believing its result was lost. Worktrees and PR lists
  stay put; every brief names a fallback recipient or a results file.
- **Overlap at function level, checked with `git apply`.** Lanes cut by file ownership
  would have serialised all work on one central file. Lanes that edit different functions
  of it run in parallel, once the patches apply cleanly in plan order and with each pair
  of lanes swapped.
- **A heavy-run lock.** Several sessions ran whole-package race-detector suites at once
  and exhausted memory. One lock, per-process time limits, and long loops started after
  the pre-PR check.
- **Briefs cite rules, not counts or paths.** A brief that said "all four items" after the
  checklist had grown to eight made an agent skip items; copied paths went stale.
- **An inventory round at the end of a phase.** Asking every lane for unfiled findings,
  PRs missing the audit pass and its PR mapping found PRs that had skipped the audit pass
  and issues nobody had filed.

---

## Harness requirements

- Several agent sessions that can run in parallel and message each other, or a shared
  file they can append to.
- Git worktrees.
- Optional: a terminal multiplexer (e.g. Herdr, tmux) to place sessions; a review
  pipeline, a pre-PR check and an external-PR review of your own. The skill names these
  by role; bind them to your own commands in your agent's instructions.

---

## Files in this repo

| File | Purpose |
| ---- | ------- |
| `SKILL.md` | The prompt body: preparation, lanes, coordinator, state files, failure modes, ending a phase |
| `brief.md` | The lane brief template: a lane session's first prompt |
| `evals/evals.json` | Generic evals, one rule each, named in `_probes` |
| `LICENSE` | MIT |

---

## Install

Claude Code plugin:

```
/plugin install lanes --marketplace edshav/skills
```

### Native SKILL install (SKILL-aware harnesses)

| Harness     | Project scope                                     | User scope                |
| ----------- | ------------------------------------------------- | ------------------------- |
| Claude Code | `<your-repo>/.claude/skills/lanes/`               | `~/.claude/skills/lanes/` |
| Codex       | `<your-repo>/.agents/skills/lanes/`               | `~/.agents/skills/lanes/` |
| Other       | Whatever directory your harness reads skills from | Same, user-global location |

### Instruction-surface install (everything else)

Paste the body of `SKILL.md` into the coordinator's instruction surface (Cursor rules,
`GEMINI.md`, a system prompt), and keep `brief.md` where the coordinator can read it.

---

## License

[MIT](./LICENSE).
