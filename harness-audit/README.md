# harness-audit

A reusable instruction module for AI agents that audits a project's Claude Code harness
against a catalogue of agentic-engineering ideas, proposes at most 7 ranked changes, and
stops for you to pick.

Packaged in the [SKILL format](https://agentskills.io/specification) (YAML frontmatter +
Markdown body). The audit method is harness-agnostic, but the catalogue maps every idea to
a Claude Code mechanism, so it pays off most in Claude Code projects.

---

## When to use it

You want to know what in a project could run without you next: which recurring tasks have a
natural trigger, where work stalls waiting for you to start it, which agents hold more tools
than their role needs, whether you can see what an unattended run did.

Not for a code review, a repo-wide code quality audit, a single-file change, or general Claude
Code automation recommendations or first-time setup.

## What it does

1. Reads [`ideas.md`](ideas.md): 15 ideas, the course's own caveats and nine audit
   questions, distilled from the "Tiny Software Factories" course and a companion video.
2. Inventories the harness read-only: `CLAUDE.md` / `AGENTS.md`, `.claude/`, CI, scripts,
   what already runs unattended.
3. Finds where the human is the bottleneck from evidence in the repo: `git log`, TODO
   clusters, manual steps in docs, recurring commits, and issues and PRs if `gh` works.
4. Answers the nine questions with evidence, then proposes at most 7 changes in a table
   (idea #, change, files, effort, value, risk, how we'd know it works), plus a "Not now" list.
5. Stops. After you pick, implements the picks one at a time and verifies each.

## Why these design choices

- **Read-only until the pick.** An audit that edits as it goes makes you review changes you
  never chose. The skill ends on a decision point instead.
- **Evidence or "Not now".** Every idea in the catalogue sounds good in the abstract. A
  proposal has to point at something in this repo that shows the need.
- **Cap of 7.** A short ranked list gets acted on; a long one gets skimmed.
- **Existing mechanisms first.** A cron prompt calling an existing skill beats new machinery.
- **The project's `CLAUDE.md` wins** over the catalogue where they conflict.
- **Approval point and narrow tools** for anything unattended that touches production,
  money, user data or outside services.
- **Ideas, not the product.** The course builds a web app; the skill does not recreate it.

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

Copy the `harness-audit/` folder into your agent's skills directory, per project
(`<repo>/.claude/skills/harness-audit/`) or user-global (`~/.claude/skills/harness-audit/`).
Keep `ideas.md` next to `SKILL.md`; the skill reads it by relative path.

### Instruction-surface install (everything else)

Paste the body of `SKILL.md` into the agent's instruction surface and put `ideas.md` where
the agent can read it, adjusting the pointer if the path differs.

## Triggering

Fires on "audit the harness", "what can run without me", "improve our Claude Code setup
with agentic ideas", or `/harness-audit`. Does not fire on a code review, a repo-wide code
quality audit, a single-file change, or general automation recommendations or first-time setup.

## License

MIT. See [LICENSE](LICENSE).
