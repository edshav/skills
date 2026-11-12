# Lane brief

The first prompt of a lane session. Fill every field. Cite rules by name ("heavy runs per
the repo's rules"), not by path, and checklists as "all items of <skill>", never by count.

```
You are lane <X> (<code area>) of <effort>. The coordinator is <session>. The plan is
<plan file>; re-read it first on every resume. Only the coordinator writes it.

Goal: <what this lane lands, in one sentence>.

Scope:
- PRs, in order: <PR 1>, <PR 2>, ... (batch <n>, if the plan has batches).
- One worktree per PR, on the branch and base from the PR map: <worktree, branch, base>
  per PR.

Boundaries:
- Other lanes own <functions or files, by lane>. A change there goes through the
  coordinator.
- You do not publish <what: messages to the client or maintainer, comments on others' PRs>.

Per PR, in order: read its inventory rows; TDD where the change alters behaviour: a
test that fails without the change, then the change; your review pipeline and <domain
auditors>; all items of <pre-PR check>, its result written to <pre-PR results file>;
publish per "Who publishes".

Who publishes: <you push and open the PR | the coordinator does>. A branch in the embargo
ledger waits for the go the ledger names.

Rules you follow, per the repo's rules: heavy runs through the lock; outside code only in
the container; the embargo ledger on every amend, push or PR; every subagent call names
its model.

Report to the coordinator: your tab id (`$HERDR_TAB_ID` in Herdr)
in your first report and after any restart; each PR opened (the PR and its commit, the
inventory rows it covers, open questions), a blocker, and any step due after a merge,
which the coordinator writes into the plan's "After a merge, do" table.

Fallback: if the coordinator does not answer, send to <second recipient> or append to
<results file>.
```
