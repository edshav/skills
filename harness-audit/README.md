# harness-audit

A reusable instruction module for AI agents that audits a project's agent harness (Claude
Code, Codex, Cursor or similar) against a catalogue of agentic-engineering ideas, proposes at
most 7 ranked changes, and stops for you to pick.

Packaged in the [SKILL format](https://agentskills.io/specification) (YAML frontmatter +
Markdown body), harness- and LLM-agnostic. The catalogue maps each idea to a Claude Code
mechanism as a worked example; in another harness the audit maps it to that harness's
equivalent. See [Harness requirements](#harness-requirements).

---

## When to use it

You want to know what in a project could run without you next: which recurring tasks have a
natural trigger, where work stalls waiting for you to start it, which agents hold more tools
than their role needs, whether you can see what an unattended run did.

Not for a code review, a repo-wide code quality audit, a single-file change, or general
automation recommendations or first-time setup of an agent tool.

## What it does

1. Reads [`ideas.md`](ideas.md): 15 ideas, the course's own caveats and nine audit
   questions, distilled from the "Tiny Software Factories" course and a companion video.
2. Inventories the harness read-only: agent instruction files (`CLAUDE.md`, `AGENTS.md`,
   Cursor rules and the like), harness config folders, CI, scripts, what already runs
   unattended. Where those files route work to another place (sessions they hand off to, a
   folder that answers questions, a shared decision record), it reads that place's
   instruction files (or the record itself) too, one hop; a path cited only for reference is
   left out.
3. Finds where the human is the bottleneck from evidence in the repo or a linked part: `git
   log`, TODO clusters, manual steps in docs, recurring commits, and issues and PRs if `gh`
   works.
4. Answers the nine questions with evidence, then proposes at most 7 changes in a table
   (idea #, change, files, effort, value, risk, how we'd know it works), plus a "Not now" list.
5. Stops. After you pick, implements the picks one at a time and verifies each.

## Why these design choices

- **Read-only until the pick.** An audit that edits as it goes makes you review changes you
  never chose. The skill ends on a decision point instead.
- **Evidence or "Not now".** Every idea in the catalogue sounds good in the abstract. A
  proposal has to point at something in this repo, or in a linked part it read, that shows
  the need.
- **Cap of 7.** A short ranked list gets acted on; a long one gets skimmed.
- **Existing mechanisms first.** A cron prompt calling an existing skill beats new machinery.
- **The project's own agent instructions win** (`CLAUDE.md`, `AGENTS.md` or equivalent) over
  the catalogue where they conflict.
- **Approval point and narrow tools** for anything unattended that touches production,
  money, user data or outside services.
- **Ideas, not the product.** The course builds a web app; the skill does not recreate it.

## Harness requirements

- An agent that can read the repo and run read-only shell commands (`git log`, `grep`).
- Optional: `gh` for issues and PRs as evidence.
- The audit reads whatever agent instruction files and config the project has; it needs no
  particular harness. Proposals name mechanisms of the harness the project uses (a scheduler,
  subagents, hooks, permission rules); where that harness has no equivalent, the proposal says
  so.

## Files in this repo

| File | Purpose |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The prompt body: steps, rules, output format, the after-pick phase. |
| [`ideas.md`](ideas.md) | The idea catalogue and the nine audit questions. |
| [`evals/evals.json`](evals/evals.json) | Evals; each `_probes` names the rule it enforces. |
| [`LICENSE`](LICENSE) | MIT. |

## Install

Claude Code plugin:

```
/plugin install harness-audit --marketplace edshav/skills
```

### Native SKILL install (SKILL-aware harnesses)

Copy the `harness-audit/` folder into your agent's skills directory:

| Harness     | Project scope                                     | User scope                         |
| ----------- | ------------------------------------------------- | ---------------------------------- |
| Claude Code | `<your-repo>/.claude/skills/harness-audit/`       | `~/.claude/skills/harness-audit/`  |
| Codex       | `<your-repo>/.agents/skills/harness-audit/`       | `~/.agents/skills/harness-audit/`  |
| Other       | Whatever directory your harness reads skills from | Same, user-global location         |

Keep `ideas.md` next to `SKILL.md`; the skill reads it by relative path.

### Instruction-surface install (everything else)

Paste the body of `SKILL.md` into the agent's instruction surface and put `ideas.md` where
the agent can read it, adjusting the pointer if the path differs.

## Triggering

Fires on "audit the harness", "what can run without me", "improve our Claude Code setup
with agentic ideas", or `/harness-audit`. Does not fire on a code review, a repo-wide code
quality audit, a single-file change, or general automation recommendations or first-time setup
of an agent tool.

## License

MIT. See [LICENSE](LICENSE).
