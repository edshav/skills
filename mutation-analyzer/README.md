# mutation-analyzer

A reusable instruction module for AI coding agents that turns the model into an
investigative staff engineer for **mutation-oriented** code analysis: not "explain
the codebase," but "if I change X, what breaks, where does it silently corrupt, and
where does it loudly fail?"

It produces **code-grounded, persistable knowledge files** under a wiki directory,
designed to survive across sessions so the second pass doesn't redo the first.

Packaged in the [SKILL format](https://agentskills.io/specification) (YAML
frontmatter + Markdown body), harness- and LLM-agnostic. The body of `SKILL.md`
is a self-contained system prompt you can drop into any agentic coding assistant
(Claude Code, Codex, Cursor, Cline / Roo Code, Aider, GitHub Copilot, Gemini CLI,
custom GPTs, raw API calls, …). See [Install](#install) below for the per-tool
matrix.

---

## Why this exists

Generic "explain this codebase" answers are throwaway. They feel productive in the
moment, then evaporate. The expensive question in any real refactor is:

> _If I change this struct / column / endpoint, what breaks, where, and how?_

Answering that requires discipline an unsteered model lacks:

- Trace data through **every** layer (DB → API → template → client), not just the one
  in front of you.
- Identify **silent corruption** sites (precision loss, dropped fields, stale caches) —
  these are the bugs LLMs ship, because tests still pass.
- Surface **invariants the code alone won't reveal** (legacy field names that look
  optional but aren't, multi-tenant assumptions, single-coin transaction rules).
- **Persist** the analysis to disk, typed, cross-linked, indexed — so the next session
  starts from the corpus instead of re-reading the same files.

This skill enforces that discipline by routing the model through a five-mode state
machine with non-skippable checklists and mandatory file outputs.

---

## The 5-mode state machine

```
                ┌───────────────────────────────────────────────────────┐
                │                                                       │
                ▼                                                       │
  ┌──────────────────┐         ┌──────────────────┐        ┌──────────────────┐
  │ 1. Interview     │  scope  │ 2. Explore       │  evid. │ 3. Synthesize    │
  │   (default)      │────────▶│   (checklist)    │───────▶│   (auto-runs,    │
  │                  │         │                  │        │    writes files) │
  └──────────────────┘         └──────────────────┘        └──────────────────┘
         ▲                              │                           │
         │                              ▼                           ▼
         │                       ⚠️  INCOMPLETE          ┌──────────────────────┐
         │                       (back to Explore        │ <WIKI>/code-analysis/│
         │                        with gap stated)       │   <domain>/          │
         │                                               │     flow.full.md     │
         │                                               │     flow.compact.md  │
         │                                               │     patterns.md      │
         │                                               │     impact.md        │
         │                                               │ <WIKI>/index.md ◀────│ (mandatory)
         │                                               └──────────────────────┘
         │                                                          │
         │                                                          ▼
         │   ┌──────────────────────────┐         ┌──────────────────────────┐
         └───│ 5. Lint                  │◀────────│ 4. Consolidate           │
             │   (audit existing wiki)  │         │   (cross-domain merge)   │
             └──────────────────────────┘         └──────────────────────────┘
```

The Interview → Explore → Synthesize arc **auto-chains**. The user does not have to
remember to say "now synthesize." As soon as Explore's mandatory checklist is satisfied,
the model continues into Synthesize and writes the wiki files in the same turn. To stop
before files are written, the user must explicitly say so (e.g. "explore only", "don't
write yet").

Consolidate and Lint are user-triggered audit modes that operate on the existing wiki,
not on raw code.

### Mode 1 — Interview (default)

Define scope. 5–12 targeted questions, **all about data flow across layers**, not about
struct definitions or "what does this module do." The model stops asking once it can
identify data origin, transformation points, and consumption points.

Good question: _"Is this value consumed by both the JSON API and the client-side
controller, or only one?"_
Bad question: _"What fields does the User struct have?"_

### Mode 2 — Explore

Code-grounded answer with a non-skippable checklist:

1. Where the entity is **defined** (source of truth).
2. Where it is **used** (≥3 distinct usage points).
3. ≥2 **transformation** points.
4. ≥1 **serialization boundary** (DB or API).
5. ≥1 **domain-specific constraint** (linked to the project's constraints file when
   one exists).

For every entity, the model must also state what depends on it directly, what depends
on derived data, where a **silent failure** occurs, and where a **hard failure** occurs
— _before_ synthesizing.

If any item is missing, the model emits ⚠️ INCOMPLETE and does **not** proceed to
Synthesize until the gap is filled or the user accepts it.

### Mode 3 — Synthesize (auto-runs after Explore)

Produces a structured document following a strict 10-section template, then **writes
it to disk**. Files written, per domain:

| File                                                | When                                                                                                                                  |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `<wiki>/code-analysis/<domain>/flow.full.md`        | Always (Sections 1–8).                                                                                                                |
| `<wiki>/code-analysis/<domain>/flow.compact.md`     | Always (Section 9 — LLM-optimized).                                                                                                   |
| `<wiki>/code-analysis/<domain>/patterns.md`         | When the flow reveals reusable architectural behavior. **Single-domain is sufficient.**                                               |
| `<wiki>/code-analysis/<domain>/impact.md`           | When the flow reveals non-trivial mutation risk. **Single-domain is sufficient.**                                                     |
| `<wiki>/code-analysis/<domain>/<subarea>.impact.md` | When sub-areas have distinct blast radii (e.g. `summary.impact.md`, `transactions.impact.md`).                                        |
| `<wiki>/index.md`                                   | **Always** — updated to point to every file created, extended, or merged. The index is the source of truth for what knowledge exists. |

Patterns and impact are produced **here, per domain, at synthesis time**. This is a
deliberate design choice: a single-domain pattern is still worth documenting because
the next domain to encounter it benefits.

**Cross-links** are typed: `depends-on`, `derived-from`, `shares-pattern-with`. They go
in a `See also:` block at the bottom of each file using repo-root-relative paths.

### Mode 4 — Consolidate

User-triggered (`Consolidate: <scope>`). Operates on **existing wiki files**, not raw
code. Job: when the same pattern or the same mutation risk appears in 2+ domains'
files, pick one canonical home (the most upstream domain, or a `core/constraints.md`
file if it's a cross-domain invariant), trim duplicates to references, and wire
`shares-pattern-with` links.

This is **not** where patterns/impact are first created — Synthesize already created
them per-domain. Consolidate prevents drift between domains, nothing more.

### Mode 5 — Lint

User-triggered (`Lint: <scope>`). Audits the wiki for:

- Contradictions between files.
- Duplication that should have been consolidated.
- Missing typed cross-links.
- Incomplete flows (a `flow.full.md` missing required sections).
- Constraint violations (a flow that contradicts the constraints file).
- **Missing pattern files** — a flow that documents reusable behavior but has no
  `patterns.md`.
- **Missing impact files** — a flow that documents non-trivial risk but has no
  `impact.md`.

Output is severity-ranked (Critical / High / Medium / Low) with action labels
(Immediate / Next Refactor / Optional).

---

## Why these design choices

A few decisions in here look fiddly but each fixes a specific failure mode:

**Auto-chain Interview → Explore → Synthesize.** Without this, models stop after
exploring and the user has to know to ask for the writeup. The writeup is the point;
exploration without persistence is throwaway.

**Mandatory Explore checklist.** A free-form "explore" produces shallow answers. The
checklist (definition, usage, transformation, serialization, constraint) forces breadth
across layers. The ⚠️ INCOMPLETE gate makes the model surface what it doesn't know
instead of fabricating.

**Silent vs hard failure as required output.** The bugs that ship from LLM-assisted
refactors are almost always **silent**: tests pass, the field renders, the number is
just wrong. Forcing the model to name silent-failure sites explicitly is the single
highest-value rule in the skill.

**Per-domain patterns/impact at synthesis time, not at consolidate time.** Earlier
versions deferred pattern/impact creation until a second domain emerged. This left the
first domain's flow file alone and the knowledge half-captured. Single-domain creation
fixes that.

**Constraints file with ID-linking (optional).** If the project has a curated
constraint list (e.g. `wiki/core/constraints.md` with C1, C2, …), synthesis cites by
ID rather than re-deriving the rule each time. Prevents the model from inventing
slightly different wordings of the same invariant.

**Mandatory index update.** Without an authoritative index, generated files become
landfill — you can't tell what's current, what's stale, or what exists at all. The
index update is non-optional.

**Typed cross-links.** `depends-on`, `derived-from`, `shares-pattern-with`. Untyped
"see also" lists are noise; typed links let Lint mechanically detect missing reverse
edges and let impact analysis fan out.

---

## Adapting to a new project

Open `SKILL.md` and do two edits — the inline `<!-- comments -->` walk you through
both:

1. **Replace `<WIKI-ROOT>`** with your wiki directory name (`wiki`, `docs`,
   `knowledge`, whatever).
2. **Fill in the `Project Invariants` block** with 3–6 bullets of hard rules the
   code alone won't reveal — numeric precision splits, multi-tenancy rules,
   legacy field names that look optional but aren't. If you maintain a curated
   constraints file with stable IDs, uncomment the pointer at the bottom of that
   block so synthesis cites by ID instead of paraphrasing.

Leave everything else alone — the state machine, checklists, file layout, and
template are project-agnostic.

### What the wiki layout looks like in practice

```
<wiki-root>/
├── index.md                          ← authoritative index (always updated)
├── core/
│   ├── constraints.md                ← optional: C1, C2, ... canonical invariants
│   └── maintenance.md                ← optional: governance rules
└── code-analysis/
    ├── checkout/
    │   ├── flow.full.md
    │   ├── flow.compact.md
    │   ├── patterns.md
    │   └── impact.md
    ├── address-page/
    │   ├── flow.full.md
    │   ├── flow.compact.md
    │   ├── summary.impact.md         ← sub-area impact
    │   ├── transactions.impact.md
    │   └── charts.impact.md
    └── mempool/
        ├── flow.full.md
        ├── flow.compact.md
        └── impact.md
```

---

## Files in this repo

- `SKILL.md` — the instruction module itself. YAML frontmatter (`name`, `description`)
  plus a Markdown body that defines the five-mode state machine, checklists, and
  output template. Customize the `Project Invariants` block and `<WIKI-ROOT>`
  placeholder for your project.
- `evals/evals.json` — a generic eval set that probes each rule of the state machine.
  Customize the `<ENTITY>` / `<LAYER>` placeholders to refer to real things in your
  codebase. The schema is the common `evals.json` shape consumed by skill-builder
  tooling and eval harnesses.
- `LICENSE` — MIT.

---

## Install

1. **Copy this folder** into your agent's skills directory or instruction surface
   (see the matrices below).
2. **Edit the `Project Invariants` block** and replace the `<WIKI-ROOT>` placeholder
   in `SKILL.md` with your wiki directory name (e.g. `wiki`, `docs`, `knowledge`).
3. **Reload your agent**, if it does not auto-detect new skills. The skill
   auto-activates on mutation-oriented phrasing in SKILL-aware harnesses; in others,
   invoke the modes explicitly (see [Triggering](#triggering) below).

### Native SKILL install (SKILL-aware harnesses)

Copy the folder into the agent's skills directory, per-project or user-global:

| Harness     | Project scope                                       | User scope                                |
| ----------- | --------------------------------------------------- | ----------------------------------------- |
| Claude Code | `<your-repo>/.claude/skills/mutation-analyzer/`     | `~/.claude/skills/mutation-analyzer/`     |
| Codex       | `<your-repo>/.agents/skills/mutation-analyzer/`     | `~/.agents/skills/mutation-analyzer/`     |
| Other       | Whatever directory your harness reads skills from   | Same, in the user-global location         |

### Instruction-surface install (everything else)

The body of `SKILL.md` (everything after the YAML frontmatter) is a self-contained
system prompt with no harness-specific runtime dependencies — it only assumes the
agent can read files and write files in the working directory.

Drop it into whichever instruction surface your tool exposes:

| Tool                        | Where to put the SKILL.md body                            |
| --------------------------- | --------------------------------------------------------- |
| Cursor                      | `.cursor/rules/mutation-analyzer.mdc` (or `.cursorrules`) |
| Cline / Roo Code            | Custom Instructions panel                                 |
| Aider                       | `--read SKILL.md` or include in `CONVENTIONS.md`          |
| GitHub Copilot Chat         | `.github/copilot-instructions.md`                         |
| Gemini CLI                  | `GEMINI.md` at repo root                                  |
| Custom GPT / Claude Project | Paste into the system instructions / project knowledge    |
| Any LLM via API             | Prepend as `system` message                               |

In tools without auto-trigger metadata, you'll need to invoke the modes explicitly
(`Interview: ...`, `Explore: ...`, `Synthesize: ...`, etc.) rather than relying on
keyword routing. Everything else — the checklist, the auto-chain, the output template
— is enforced by the prompt itself, not by the host.

---

## Triggering

In SKILL-aware harnesses, the skill auto-activates on phrases like:

- "Trace how X flows through the system"
- "I want to modify X, what do I check?"
- "Where is X used?"
- "What breaks if I change X?"
- "How does data move from backend to frontend for X?"

In any tool, you can drive it explicitly with mode prefixes:

- `Interview: <topic>` — scope before exploring
- `Explore: <question>` — jump straight to Explore
- `Synthesize: <topic>` — re-synthesize an already-explored topic
- `Consolidate: <scope>` — cross-domain consolidation
- `Lint: <scope>` — audit existing wiki

The skill deliberately **declines** general "explain the architecture" requests and
redirects to Interview mode to scope first. It is not a tour guide; it is a mutation
safety tool.

---

## License

[MIT](./LICENSE). Use it, fork it, adapt it to your stack — no attribution required
but appreciated. PRs welcome, especially for adaptation notes for tools not listed
above.
