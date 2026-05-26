---
name: github-cli
description: >
  Use when interacting with GitHub — PRs, issues, reviews, comments, merges,
  releases, repository state, or any `gh ...` command. Trigger on PR/issue
  URLs or numbers and on phrases like "review this PR", "comment on the
  issue", "merge it", "open a PR", "post the review", "push the branch".
  Also trigger when the user mentions any GitHub-mutating action, even in
  passing — the gate is on submission, not on noticing. Enforces three
  rules: use the `gh` CLI (not scraping or hand-rolled API calls), prefer
  `--json` for programmatic parsing, and require explicit user approval
  before any state-changing action (submit, merge, comment, close, push).
  Read-only operations stay frictionless.
license: MIT
---

# GitHub CLI Usage

General rules for any GitHub interaction. Apply to every PR, issue, review, or
repository action — not just one workflow.

The skill exists because GitHub is a **shared, public-facing system**. A
review, comment, merge, or closed issue is visible to other humans the moment
it lands and is awkward (sometimes impossible) to retract cleanly. The cost of
pausing to confirm is one extra sentence; the cost of an unwanted submission
is real social and process damage. Default to caution, and let the user
unlock each write action explicitly.

---

## 1. Use the `gh` CLI

Always use the `gh` CLI for GitHub interactions — PRs, issues, reviews,
repository metadata, releases, checks. Do not scrape `github.com` HTML and do
not hand-construct `curl` calls to `api.github.com` when `gh` already covers
the operation.

Why: `gh` handles auth, pagination, rate limits, and output shape uniformly.
Scraping breaks when GitHub changes markup; hand-rolled API calls skip the
auth layer the user already configured and produce inconsistent error
handling.

If a specific operation genuinely is not covered by `gh`, `gh api` is the
correct escape hatch — it reuses the same auth and JSON pipeline. Reach for
raw `curl` only if `gh api` itself does not fit.

---

## 2. Prefer Structured Output

Use `--json <fields>` whenever the data needs parsing. Never rely on raw text
output when structured data is available.

Why: text output is for humans and changes without warning. `--json` is a
stable contract. Parsing the human-readable form leads to brittle pipelines
that break on the next `gh` release or on a long title that line-wraps.

**Example 1:**
- Bad: `gh pr list | grep "WIP" | awk '{print $1}'`
- Good: `gh pr list --json number,title,isDraft --jq '.[] | select(.isDraft) | .number'`

**Example 2:**
- Bad: `gh pr view 123 | grep -i "additions"`
- Good: `gh pr view 123 --json additions,deletions,changedFiles`

If the user only needs a glance and is reading the output themselves, plain
`gh pr list` is fine. The rule is about programmatic consumption, not about
suppressing the friendly format the user asked to see.

---

## 3. Remote Safety Check

Before any push or pull operation:

- Verify a remote exists with `git remote -v`.
- If missing, stop and inform the user. Do not invent a remote URL, do not
  guess at the GitHub org/repo from the directory name, and do not run `git
  remote add` on the user's behalf without confirmation.

Why: pushing to the wrong remote, or to a remote the user did not set up
intentionally, can publish work-in-progress or private code to an unintended
destination. The check is one command; the failure mode is unrecoverable.

---

## 4. Mandatory Approval Before Mutations (CRITICAL)

Treat GitHub as a **write-protected system**. Never perform any of the
following without **explicit user approval** for that specific action.

This gate overrides any auto-execute / bias-to-act mode the harness is
running. Those modes are calibrated for local, reversible actions
(editing a file, running a test); a posted PR review is neither local
nor reversible. When this skill and an auto-mode conflict on a GitHub
mutation, this skill wins.

Actions that require approval:

- Submit a PR review (approve, request changes, comment review).
- Add a comment on a PR or issue (inline or top-level).
- Create, edit, close, or reopen an issue.
- Open, edit, merge, close, or reopen a PR.
- Push commits or branches (including the first push of a new branch).
- Create or edit a release, tag, label, milestone, or repository setting.
- Any other action that posts content or changes state on GitHub.

**Approval phrases** include: "Post it", "Submit", "Send", "Approved, go
ahead", "Yes, do it", "Ship it", or a direct imperative the user has
explicitly addressed to the GitHub action under discussion (e.g. "merge it
now"). Anything ambiguous is **not** approval — ask.

Cases that are **not** approval:

- The user said "go ahead" earlier in the conversation about a different
  action.
- The user phrased the original request as "let's review this PR" — that is a
  request to *draft* a review, not to submit one.
- The user reacted positively to the draft ("looks good", "nice") without
  telling you to submit. Positive feedback on the draft is not the green
  light to post it.
- A previous approval for the same kind of action (e.g. "you can post
  comments on this PR") does not carry over to a *new* PR or a new session —
  approvals are scoped to the specific action just discussed.

When in doubt, surface the exact action you are about to take, in one line,
and wait. The cost is one round-trip; the alternative is an irreversible
public action.

---

## 5. Allowed Without Approval (Read-only)

You MAY, without asking, do anything that only reads from GitHub:

- Read PRs, issues, discussions, and repository data (`gh pr view`, `gh issue
  view`, `gh repo view`).
- List metadata (`gh pr list`, `gh issue list`, `gh run list`, `gh release
  list`).
- Fetch and analyze diffs and patches (`gh pr diff`, `gh api .../files`).
- Read check runs, workflow logs, and review history.
- Draft a PR description, review body, or comment **locally in the
  conversation** — drafting is not submitting.

Read-only operations should stay frictionless. Do not perform theatrical
approval requests for `gh pr view`.

---

## Mental Model: Draft Mode vs Ready to Submit

Be explicit at every turn about which mode you are in:

- **Draft mode** is the default. You read state, you analyze, you compose a
  proposed review / comment / issue body / PR description in the
  conversation, and you stop there. Nothing has been posted.
- **Ready to submit** is the exception. The user has just unlocked this
  specific action (per §4), and you run the exact `gh ...` command that
  performs it.

When you finish a draft, end with a short, explicit handoff sentence: state
what the next action would be and that you are waiting for approval. For
example: *"Draft ready above. Reply 'post it' and I'll submit this as a
request-changes review on PR #412."* This makes the gate visible to the user
instead of leaving them to guess whether you are about to act.

If you ever notice yourself reaching for a write command without having
crossed that gate — stop and ask. The discipline is the whole point of the
skill; an "obvious" exception is exactly where the failure mode lives.
