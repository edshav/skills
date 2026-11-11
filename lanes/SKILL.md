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
   one. The lanes table names each lane's functions, PR order and worktrees.
5. **Merge order**, and batches when the maintainer reviews in batches. Batch 1: every PR
   that stands on the base branch by itself. Batch n+1: PRs that build on a batch-n PR,
   started after the maintainer's pass on batch n so they take in the remarks.
6. **Review process.** Agreed with the client, if any, and the maintainer before the
   first PR: who reviews, who merges, who requests reviews.
7. **"After a merge, do"** (section 4) and **Status**, empty at the start.

## 2. Starting a lane

- **Model.** The strongest model for lanes that touch money, consensus, keys or judgement
  calls; a cheaper one for mechanical checks. Every subagent call inside a lane names its
  model too. Effort stays at the default.
- **Worktree.** One worktree per PR, on the branch and base the PR map names.
- **Placement.** One session per lane, in a terminal multiplexer if you use one (e.g.
  Herdr, tmux), in the repo's workspace or session. Its name is short and leads with the
  lane (`b-sync`; the coordinator `coord`): sidebars and tab bars cut long names, and the
  workspace already says the repo.
- **First prompt.** Filled in from [`brief.md`](brief.md).

Per-PR steps, in the lane:
1. Branch as above; read the PR's inventory rows.
2. TDD where the change alters behaviour: a test that fails without the change, then
   the change.
3. Run your review pipeline, plus every domain auditor whose area the diff touches.
4. Run your pre-PR check and write its result to the pre-PR results file.
5. Publish per the brief's "Who publishes": push and open the PR. A branch in the embargo
   ledger waits for the go the ledger names.
6. Report to the coordinator: the PR and its commit, the inventory rows it covers, any
   step due after a merge.

## 3. The coordinator

Writes no code. It:
- keeps the plan file: statuses and the "After a merge, do" table, from lane reports;
- routes briefs to lanes and answers between them;
- drafts the client's and the maintainer's messages, for the user to send;
- checks each reported PR against its inventory rows, and asks for an **audit pass**: the
  inventory marks what the PR actually landed.

It maps lanes by worktree and PR list. Session names change; worktrees and PRs do not.

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
| Outside-code container | the only place an outside contributor's code builds and runs: no network after dependencies, no host mounts, no credentials, queued on the same lock | whoever reviews the outside PR |

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

1. **Inventory round.** Ask every lane for its unfiled findings, its PRs missing the audit
   pass, its lane ↔ PR mapping, and process ideas.
2. **Audit pass** over every PR the round found missing.
3. **Close the lanes.** Each open item moves into the plan ("After a merge, do" or
   Status) before its lane closes.
4. **Process ideas** go to the user as proposals that wait for a go-ahead, each naming
   where it would land: this skill, the repo's rules, or the user's own config.
