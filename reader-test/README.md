# reader-test

A reusable instruction module for AI agents that finds the errors in a document its own
author cannot see — by handing the file to readers who have nothing but the file.

Not proofreading, and not a review pass over prose. It targets the class of error that
survives every re-read by the person who wrote it: the number that drifted between two
tables, the intention recorded as a completed action, the state with no exit, the section
a later revision silently contradicted.

Packaged in the [SKILL format](https://agentskills.io/specification) (YAML frontmatter +
Markdown body), harness- and LLM-agnostic. See [Install](#install) for the per-tool
matrix and [Harness requirements](#harness-requirements) for the one real dependency.

---

## Why this exists

A document you wrote is unreadable to you. You know what it means, so you read your
intent instead of your words — the missing sentence is present in your head, so its
absence on the page is invisible.

This is not carelessness and it does not respond to care. Re-reading harder does not
help, because the thing doing the re-reading is the same thing that produced the gap.
Nor does asking a model that watched you write it: it has the conversation, so it has
your intent too, and it will confirm you.

What works is isolation. A reader with the file and nothing else hits the gap the way
the next person to open the document will hit it — because that is exactly what they are.

The skill exists because that isolation is easy to state and easy to erode. Every
instinct while dispatching a reader says to be helpful: *here's what this is for, don't
worry about section 4, we already decided that part.* Each of those sentences rebuilds
the blindness the pass was supposed to escape.

---

## The lenses

One reader per lens, each forbidden the others' territory. A reader restricted to
arithmetic — and told that wording, structure and missing features belong to someone
else — cannot retreat to the easy findings, so it keeps digging in its own.

| # | Lens | Position | Finds |
| - | ---- | -------- | ----- |
| 1 | **Executor** | "You build this Monday and cannot come back with questions. Where would you have to guess?" | Unstated triggers and ordering, branches with no defined outcome, a flag written and never read, a state entered and never left, happy-path-only behaviour, code assumed to already exist |
| 2 | **Numbers auditor** | Recompute everything; trust no stated total | Estimate chains that drift across restatements, unit and magnitude errors, a figure stated in two places, "X is cheaper than Y" claims, prose counts that don't match the list beneath them |
| 3 | **Source fidelity** | "Does the source actually say that?" | Citation rot and citation invention, claims about what was agreed with another party, claims about code behaviour written from memory |
| 4 | **Internal consistency** | The document against itself, no other files | Stale regions a later section contradicts but which still read as live, terms with two meanings, cross-references that don't say what they're cited for |
| 5 | **Money / data risk** | Adversarial, and its mirror | What the system *proves* versus what it *assumes*; and the honest user who does everything right, ends up unpaid, and never finds out |

Lenses 1–4 are the standard set. Add lens 5 whenever the document describes a system
handling money, personal data, or anything irreversible.

---

## Why these design choices

Each of these looks like an extra sentence in a prompt and each fixes a specific
failure:

**Readers get files, never conversation.** The single rule the whole thing rests on.
Supplying context makes the reader read your framing instead of the file, and a reader
reading your framing agrees with you. This is also the rule most likely to erode under
the impulse to be helpful, which is why it is stated as one rule rather than as a
guideline among others.

**Say that the missing context is deliberate.** Without it, readers apologise for the
gap and hedge every finding into uselessness — you get "this may be intentional, but…"
attached to real errors.

**Forbid the other lenses by name.** "Focus on X" is weaker than "do not report Y,
another reader has that lens." The first is a suggestion about emphasis; the second
removes the escape route to shallow findings.

**Demand a line number, a quote, and the arithmetic.** This is what separates a reader
from a critic. It also suppresses "consider clarifying" noise that costs real time to
triage, and it makes every finding cheap to verify or reject.

**Ask for coverage, not just hits.** Without a closing list of what was checked and
found correct, a clean document and a lazy reader produce identical output.

**Forbid editing.** A reader that starts fixing stops reading.

**Findings are suspicions, not verdicts.** Readers lack context by construction, so some
findings are the context working as intended. They get checked against the file before
they reach the user — but checked, not waved off, since the reflex to explain why a
finding is fine is the same reflex that produced the gap.

**A gap is not automatically a thing to fill.** Findings arrive phrased as absence, and
absence asks to be filled. The same finding is equally evidence the mechanism should not
exist. This is the most common way the harness gets misused: answer every gap with an
addition and the document grows a third while the thing delivered stays the same — and
each addition looks justified on its own.

---

## Harness requirements

The skill assumes the agent can **read files** and **start readers that do not share the
current conversation**. In practice that means one of:

- a harness with subagent/task dispatch (Claude Code, Codex, Cursor agents, …) — readers
  run in parallel, which is how a full pass fits in a few minutes;
- or any tool at all, run manually: a fresh session per lens, with only the document
  attached.

The parallelism is a speed optimisation. The isolation is the mechanism. What does not
work in any harness is running the lenses inside the session where the document was
written — that reproduces exactly the blindness being routed around, so the skill will
not do it.

---

## Files in this repo

- `SKILL.md` — the instruction module itself. YAML frontmatter (`name`, `description`,
  `license`) plus a Markdown body: the one rule, how to shape a reader prompt, a
  copy-paste prompt template, the five lenses, and how to triage what comes back.
- `evals/evals.json` — a generic eval set; each entry's `_probes` field names the rule
  from `SKILL.md` that it defends. Replace the `<DOC-PATH>` / `<REPO-PATH>` placeholders
  with real files from your project. Note that several evals grade *the reader prompts
  the skill produces*, not just the findings it reports — the prompt is where this skill
  succeeds or fails.
- `LICENSE` — MIT.

---

## Install

1. **Copy this folder** into your agent's skills directory or instruction surface (see
   the matrices below).
2. **No customization required.** Unlike the other skills in this repo, there are no
   project placeholders in `SKILL.md` — the lenses are domain-agnostic.
3. **Reload your agent**, if it does not auto-detect new skills.

### Native SKILL install (SKILL-aware harnesses)

| Harness     | Project scope                                     | User scope                      |
| ----------- | ------------------------------------------------- | ------------------------------- |
| Claude Code | `<your-repo>/.claude/skills/reader-test/`         | `~/.claude/skills/reader-test/` |
| Codex       | `<your-repo>/.agents/skills/reader-test/`         | `~/.agents/skills/reader-test/` |
| Other       | Whatever directory your harness reads skills from | Same, user-global location      |

### Instruction-surface install (everything else)

The body of `SKILL.md` is a self-contained system prompt. It assumes only that the agent
can read files and dispatch context-free readers (see
[Harness requirements](#harness-requirements)).

| Tool                        | Where to put the SKILL.md body                      |
| --------------------------- | --------------------------------------------------- |
| Cursor                      | `.cursor/rules/reader-test.mdc` (or `.cursorrules`) |
| Cline / Roo Code            | Custom Instructions panel                           |
| Aider                       | `--read SKILL.md` or include in `CONVENTIONS.md`    |
| GitHub Copilot Chat         | `.github/copilot-instructions.md`                   |
| Gemini CLI                  | `GEMINI.md` at repo root                            |
| Custom GPT / Claude Project | Paste into the system instructions                  |
| Any LLM via API             | Prepend as `system` message                         |

In a tool without subagents, use the manual path: the skill's prompt template is written
to be pasted into a fresh session, one per lens.

---

## Triggering

In SKILL-aware harnesses, the skill auto-activates on phrases like:

- "reader test this spec" / "прогони читателей"
- "check this doc before I send it"
- "find what's wrong with this spec"
- "is this ready to send to the client?"
- "I just rewrote the estimate — anything broken in it?"

It deliberately **does not** trigger for copy-editing, tone, or formatting requests. It
finds errors of fact, arithmetic and specification; prose problems are ordinary editing
work and don't need five readers.

### When to run it

Scale by consequence, not by length. A specification someone will implement, an estimate
that becomes a price, or a document going to a client, is worth a pass. A one-pager
nobody builds from is not.

A full pass costs several hundred thousand tokens and a few minutes — cheap against one
wrong number in a document that becomes a price, and cheap against building the wrong
thing for two days. Not cheap enough to run on every edit: run it when a document has
been substantially revised, when it is about to be acted on, and again after a revision
large enough to have introduced new stale regions.

---

## License

[MIT](./LICENSE). Use it, fork it, adapt the lenses to your domain — no attribution
required but appreciated. PRs welcome, especially new lenses that earned their keep on a
real document.
