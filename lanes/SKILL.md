---
name: lanes
description: >
  Use when one effort spans many PRs across several code areas that can move in parallel:
  plan it, then run it as one coordinator session plus parallel lane sessions. Also
  triggers on "split into lanes", "start a lane", "coordinator session", "lane brief", and
  on ending a phase of such work ("inventory round", "close the lanes"). Not for: one
  area done in sequence (one session), or a bounded task whose answer fits a paragraph
  (a subagent).
license: MIT
---

# Lanes

A multi-PR effort runs as one **coordinator** session, which writes no code, and several
**lane** sessions, each owning a slice of the PRs. Sessions die, get renamed and get
compacted; files outlive them. The whole method: decide in a file, then act.

## When it applies

Many PRs across several code areas that can move in parallel. It pays off most when the
work outlives any single session, and when one maintainer reviews PRs in batches.

One area worked in sequence fits one session. A bounded task whose answer fits a
paragraph fits a subagent.

## The user decides

The coordinator runs supervised through preparation and lane start. It proposes each
decision there and acts on it after the user's go-ahead. A proposal is a few lines: what,
why, and the alternative weighed. Then the coordinator stops and waits. A go-ahead covers
the decision it was given for; the next decision is asked again. Writing an approved
decision into the plan file needs no second go-ahead. When unsure whether something is a
decision, ask.

Decisions include:
- each plan section: the inventory buckets, the spec, the PR map, the lane cut, batches
  and merge order, the review process;
- per lane: its model, its placement and name, the full text of its brief before it is
  sent.

Lanes run at their usual pace; their briefs add no extra stops.

## 1. Preparation

Done when the plan file has every section below in place. The plan file sits next to the
code and is kept out of git.

1. **Inventory.** One row per change the effort must land (a hunk, a finding, a
   requirement), sorted into buckets.
2. **Spec.** What done means: a spec the PRs are measured against.
3. **PR map.** Inventory row → PR → branch → commit, the commit filled in from the
   lane's report. Each PR's branch name follows the repo's convention, and its base is
   the base branch (e.g. `origin/main`) or the PR it builds on. Each PR carries its open
   questions for the maintainer or the developer. Every row lands in a PR or states why
   it does not.
4. **Lanes.** Cut by code area and merge order, with overlap checked at function level:
   two lanes may share a file when they edit different functions. When the changes
   already exist as patches, check with `git apply` onto the base branch, in plan order and
   with each pair of lanes swapped; otherwise compare the lanes' function lists. A
   function two lanes both edit fixes an order: the later PR rebases onto the earlier
   one. The lanes table names each lane's functions, PR order, worktrees, session model
   (as approved) and, once the lane reports, its tab id.
5. **Merge order**, and batches when the maintainer reviews in batches. Batch 1: every PR
   that stands on the base branch by itself. Batch n+1: PRs that build on a batch-n PR,
   started after the maintainer's pass on batch n so they take in the remarks. Before
   asking the maintainer to review a batch, the coordinator runs the trial build (section 3).
6. **Review process.** Agreed with the client, if any, and the maintainer before the
   first PR: who reviews, who merges, who requests reviews.
7. **"After a merge, do"** (section 4) and **Status**, empty at the start.

## 2. Starting a lane

- **Model, per lane and per task.** The strongest model for the lane session itself when it
  touches money, consensus, keys or judgement calls. Inside a lane, each subagent call names
  its model and gets the cheapest one that fits: the strongest for the first grade of
  judgement items (tests, mutations, money logic) and for fact-checking a review text with
  technical claims; a cheaper one for mechanical checks, re-grades after a small fix, trial
  builds and fact-checking a short text (a one-line closing comment). Effort stays at the
  default. The coordinator stays on the strongest model: it catches errors across PRs, and
  it saves by taking fewer, shorter turns, not by a cheaper model.
- **Worktree.** One worktree per PR, on the branch and base the PR map names.
- **Placement.** One session per lane, in a terminal multiplexer if you use one (e.g.
  Herdr, tmux), in the repo's workspace or session. The tab is named `<lane> · <session name>`:
  the lane first, because sidebars cut names from the end (`b · 6c`; the coordinator
  `coord · da`). The tab gets the last segment of the session name once the session
  runs; cross-session messages go to the full name. The workspace already says the repo.
  The lane label names the code area loosely; the plan's PR list stays the authority. A
  security or embargoed lane gets a neutral label (`sec`), never what it fixes. When a
  lane's report arrives from a new session name, the coordinator renames the tab. It
  finds the tab by the tab id the lane states in its first report and in its first
  report after a restart. A resumed session does not notice a restart by itself: the
  coordinator asks for the report when a lane's session name changes in the session list.
- **First prompt.** Filled in from [`brief.md`](brief.md).

Per-PR steps, in the lane:
1. Branch as above; read the PR's inventory rows.
2. TDD where the change alters behaviour: a test that fails without the change, then
   the change.
3. Run your review pipeline, plus every domain auditor whose area the diff touches.
4. Run your pre-PR check and write its result to the pre-PR results file. Before handing
   the check to its grader, the author walks the check's mutation categories itself, so the
   grader confirms rather than finds. A commit made after the check gets its diff read for
   leftovers (debug output, stray files) before the push.
5. Publish per the brief's "Who publishes": push and open the PR in one command
   (`git push … && gh pr create …`). Where a hook asks before a push or a post, its prompt
   is the user's word: say in two or three lines what goes out (branch, head, PR or post),
   then run the command, with no dialog of your own. Without such a hook, ask for it (and
   for any other outward step: a post to the code host, a message) through the
   AskUserQuestion dialog, with options like "push and open" / "not yet", not as a
   question in the reply text, where it gets lost in long output. A PR body states what a
   test checks and what the pre-PR check needs, not reasoning about edge modes; text for
   the code host goes through the review pipeline once, after the code has settled. A
   branch in the embargo ledger waits for the go the ledger names.
6. Report to the coordinator: the PR and its commit, the inventory rows it covers, any
   step due after a merge.

A gap in tests the user has accepted on one PR may be accepted on a like PR without asking
again; the lane names it in its report.

**Scale the pipeline by risk.** The plan assigns each PR a tier; the brief names it.
- *Comments, docs or tests only:* the review pipeline once; from the pre-PR check only the
  items that need no mutations (stand-alone, consequences, overlap); no live run.
- *Logic without money, consensus or keys:* the full review pipeline and the full pre-PR
  check; no live run unless sync or restart behaviour changes.
- *Money, consensus or keys:* everything: the full review pipeline, the full pre-PR check,
  every domain auditor, the live run.

Below the top tier, one combined review agent replaces the separate review agents: they
read the same diff and mostly overlap.

## 3. The coordinator

Writes no code. It:
- keeps the plan file: statuses and the "After a merge, do" table, from lane reports;
- routes briefs to lanes and answers between them, taking branch names and heads for a
  brief from git or the code host, never from memory;
- drafts the client's and the maintainer's messages, for the user to send;
- checks each reported PR against its inventory rows, and asks for an **audit pass**: the
  inventory marks what the PR actually landed.

Before the review request for a batch, it makes the **trial build**: the base branch plus
every PR of the batch, outside contributors' PRs included (their code only in the
outside-code container), merged in the planned order; build, vet and the full test suite
run on the result. Each PR green alone is not enough: combinations show a test type
declared twice, a test that fails with another PR's change, and pairs of PRs that
conflict on merge. Findings go back to the lanes before the request is sent.

A lane session stays open while it has an open PR, a pending step in the "After a merge,
do" table, or an embargoed branch. Once all its PRs are merged and nothing is pending for
it, the coordinator closes it, after moving any open item into the plan (section 6).
The coordinator checks this after each merge of a lane's PR and whenever a lane reports
nothing open. Before closing, it asks the lane the close-out questions: findings not
filed, steps pending after a merge, what only its context holds, what slowed it and what
it would change. Answers on code and tasks go into the plan; answers on process go into
the retrospective file, as proposals for the user. Why:
an idle session costs nothing, but waking it after the prompt cache expires (about an hour)
re-reads its whole context uncached, hundreds of thousands of tokens for a long lane, and
autocompact costs about one such pass plus a summary and drops detail. Its state is in the
plan file, the embargo ledger and the pre-PR results file, so a fresh session picks it up
from a brief. Keep the context only where it pays: a lane answering the reviewer on its
own open PR.

**Keep small steps off long sessions.** Waking a lane after the prompt cache expires
re-reads its whole context uncached. A mechanical step (merging the base into a PR with a
known resolution, waiting for CI, rerunning a known command) goes to a fresh cheap-model
subagent or a coordinator script, not to a lane session. A lane runs /clear between
unrelated tasks and resumes from the plan file and its brief.

**Reports are short.** A lane writes the detail to its results file and sends the
coordinator 5–8 lines: the file path, the new head, and what needs a decision. The
coordinator passes the user only what needs their decision.

It finds a lane by worktree and PR list; the tab name is only a label, and the tab id
locates the tab. Session names change; worktrees and PRs do not.

## 4. Shared resources and state files

Anything that would die with a session goes into a file at the moment it is decided.
Lanes read the plan file; only the coordinator writes it.

| File | Holds | Updated by |
|---|---|---|
| Plan file | every section of 1. Preparation, and statuses | the coordinator, from lane reports |
| "After a merge, do" table, in the plan | one line per pending step: the merge that unblocks it, the step, who does it; struck when done | the coordinator, when a lane reports the step |
| Embargo ledger, out of git | unpublished security branches: branch, head, worktree, who gives the go | the owning lane, on every amend, push or PR |
| Pre-PR results file | each PR's pre-PR check result and the commit it ran on | the lane, after each run |
| Heavy-run lock | a script every heavy run goes through: race-detector runs, whole-package suites, long loops | each session, per run |
| Retrospective file | process notes from lane close-outs and reports; proposals waiting for the user | the coordinator |
| Outside-code container | the only place an outside contributor's code builds and runs: no network after dependencies, no host mounts, no credentials, queued on the same lock | whoever reviews the outside PR |

The plan holds current state: the lanes table, the "After a merge, do" table and open
items. The coordinator moves finished history to an archive file next to it, so each resume
re-reads a short plan.

An outside contributor's PR goes through your external-PR review, and nothing is posted
until all its checks have run.

## 5. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| A lane's report goes nowhere, or a lane decides its result is lost | the coordinator died or was renamed | every brief names a fallback recipient or a results file; the coordinator maps lanes by worktree and PRs |
| After compaction or a restart, a session has forgotten a pending step, an embargo or a pre-PR result | the state lived only in session memory | the files of section 4; on resume, a session re-reads the plan file first |
| Test runs exhaust memory, or sessions queue for many minutes | heavy runs from several sessions at once | the lock, a time limit per test process, long loops split into batches and started after the pre-PR check |
| An agent skips checklist items, or follows a brief to a moved file | brief rot: a count ("all four items") outlived the checklist; a copied path went stale | write "all items of <skill>"; cite rules ("heavy runs per the repo's rules"), not paths |

## 6. Ending a phase

Done when every lane has answered the inventory round and every open item sits in the
plan file.

1. **Inventory round.** Ask every lane still open the close-out questions (section 3) and
   its lane ↔ PR mapping.
2. **Audit pass** over every PR without one. The coordinator tracks this from the PR list;
   lanes do not.
3. **Close the lanes.** Each open item moves into the plan ("After a merge, do" or
   Status) before its lane closes; which lanes close is set in section 3.
4. **Process ideas** from the retrospective file go to the user as proposals that wait for
   a go-ahead, each naming where it would land: this skill, the repo's rules, or the user's
   own config.
