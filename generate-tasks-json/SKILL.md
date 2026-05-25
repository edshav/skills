---
name: generate-tasks-json
description: Use when the user wants to plan a milestone, batch-create GitHub issues, draft features and sub-issues, populate or update tasks.json, or asks anything like "create issues for X feature", "split this work into sub-issues", "prepare a tasks file", or "let's plan out v2". Trigger even if the user does not say "tasks.json" by name — any request to scaffold a Feature plus its implementation breakdown should use this skill, because the bundled create-issues.js workflow runs through this single file.
---

# Generate tasks.json for create-issues.js

This skill covers **how to execute** the issue-planning task: where the `tasks.json` file goes, the script's schema, validation, and the safe run procedure. It does **not** restate the planning rules — those live in `METHODOLOGY.md`.

## Authoritative rules — read this first, every time

[`METHODOLOGY.md`](METHODOLOGY.md) is the **single source of truth** for all issue-planning policy. **Read it in full before drafting** — not "only if a question comes up". It is binding; if anything in this skill ever appears to conflict with it, `METHODOLOGY.md` wins and this skill should be fixed.

It owns, and this skill deliberately does **not** duplicate:

- the **two-level hierarchy** and the **contract-is-the-seam default decomposition** (§6.2.1, §6.3) — when to emit a single `issue` vs. one `parent` + exactly two contract-aligned sub-issues, the >2 exception, no childless `parent`;
- **sub-issue prefixes** and the one-dominant-prefix / splitting rules (§6.4–§6.7);
- **assignment** mapping and load-balancing (§7);
- the **allowed label set** (§7.6).

Apply those rules from the doc. The rest of this skill is mechanics.

## Sourcing issue content from project docs

If the project ships structured documentation (per-feature specs, ADRs, design docs, runbooks, code-analysis traces), use it to fill issue bodies instead of re-deriving scope — this is drafting technique, not policy:

- **If a per-feature spec exists, that spec is the Feature.** Link it from the `parent` description; **lift the spec's own acceptance checklist verbatim** into the consumer (`[UI]`) sub-issue rather than paraphrasing.
- **If the project has architecture / code-analysis docs for the affected area, mine them for the producer sub-issue.** Put documented invariants and known failure modes into the producer issue as explicit "must preserve" acceptance items.
- The producer side may cascade across several modules or packages — that is still **one** sub-issue (the contract), never one-per-module.
- If a routine `[DOCS]` follow-up sub-issue is used, it typically refreshes those same code-analysis / architecture docs to reflect what shipped.

If the project ships none of this, skip this section — write scope from first principles based on the conversation with the user, and link any PRs / issues / external references they mention.

## Workflow

1. **Read the authoritative methodology** (above), then understand the feature: the user-visible functionality, the system layers it touches, and any constraints.
2. **Decide the shape per `METHODOLOGY.md` §6.2.1** — no contract → a single `issue`; a contract → one `parent` + two contract-aligned sub-issues; exceed two only with the doc's stated justification.
3. **Draft the JSON** following the schema below, sourcing content from project docs where available.
4. **Validate locally** in dry-run mode (see "Validate"). Never invoke a live run yourself.

## File location and shape

The script defaults to `./tasks.json` in the current working directory but accepts `--file <path>`. Place the file wherever is convenient — many projects keep it next to the script.

```json
{
  "tasks": [
    /* task objects */
  ]
}
```

## Task object fields

This is the `create-issues.js` schema (a script contract, not team policy). The validator enforces:

- `id` — required, unique string. Wires `parent` ↔ `sub-issue` locally; not posted to GitHub. Use stable kebab-case slugs (`feature-user-profile`).
- `title` — required, what appears on GitHub. Sub-issue titles take a prefix per `METHODOLOGY.md`.
- `type` — one of `parent`, `sub-issue`, `issue`. Anything else fails validation.
- `parent` — required when `type` is `sub-issue`; must reference an existing `id` whose task is `type: parent`.
- `issue_type` — `Feature` for parents, `Task` otherwise. Defaults apply if omitted; set it explicitly.
- `description` — markdown body. The script auto-appends `\n\nPart of #<parent-number>` to sub-issues — do not write that yourself.
- `assignee` — exactly one GitHub login (mapping is in `METHODOLOGY.md`, §7).
- `labels` — array from `METHODOLOGY.md`'s allowed set only (§7.6); omit if none adds value. There is **no** per-task `milestone` field — the script applies the milestone globally.

## Validation cheat-sheet (what the script enforces)

`create-issues.js` rejects the file if any of these hold — check before handing it over:

- a task missing `id` or `title`;
- two tasks sharing an `id`;
- `type` not in `parent` / `sub-issue` / `issue`;
- a `sub-issue` with no `parent`, a non-existent `parent`, or a `parent` whose `type` is not `parent`.

Sanity-check the JSON against these yourself first.

## Skeleton to start from

The default shape (one `parent` + the two contract sides). A canonical worked example with a routine `[DOCS]` third is in `METHODOLOGY.md` §8.4 and `tasks.example.json`.

```json
{
  "tasks": [
    {
      "id": "feature-<slug>",
      "type": "parent",
      "issue_type": "Feature",
      "title": "<User-visible feature name>",
      "description": "<scope, motivation, link to spec / design doc if available>",
      "assignee": "<github-login>",
      "labels": ["enhancement"]
    },
    {
      "id": "<slug>-contract",
      "type": "sub-issue",
      "parent": "feature-<slug>",
      "issue_type": "Task",
      "title": "[DATA] <producer side — deliver the contract shape>",
      "description": "<contract as acceptance criteria + invariants from architecture / code-analysis docs>",
      "assignee": "<github-login>",
      "labels": ["enhancement"]
    },
    {
      "id": "<slug>-ui",
      "type": "sub-issue",
      "parent": "feature-<slug>",
      "issue_type": "Task",
      "title": "[UI] <consumer side — render against the contract>",
      "description": "<spec acceptance checklist, lifted verbatim>",
      "assignee": "<github-login>",
      "labels": ["enhancement"]
    }
  ]
}
```

## Validate

After writing the file, run dry-run mode — it validates, prints what would be created, and makes **no** GitHub API calls:

```bash
REPO="<org>/<repo>" MILESTONE="<milestone>" node create-issues.js --dry-run
```

If the file is elsewhere: append `--file <path>`.

Fix any `❌` lines before reporting done. Do **not** run the live command (without `--dry-run`) yourself — that creates real GitHub issues, a write action requiring explicit user approval. Show the user the dry-run output and the live command and let them invoke it.

## Common mistakes (mechanics)

Planning mistakes (over-decomposition, childless `parent`, wrong prefix / assignment / label) are governed by `METHODOLOGY.md` — follow it. The script-mechanics traps:

- **Writing `Part of #N` into a sub-issue description.** The script appends it automatically; duplicating produces ugly output.
- **Adding a `milestone` field to a task.** The milestone is applied globally (via the `MILESTONE` env var) — a per-task field is noise.
- **Reusing or renaming an `id` across runs after partial success.** With `--resume` the script keys `.create_issues_state.json` by `id`; changing ids mid-flight breaks resume linkage.
- **Running the live command to "just check".** Dry-run is the only thing you run; the live run is the user's.
