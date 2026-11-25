# TSF ideas for a project harness

Distilled from eight YouTube videos: the "Tiny Software Factories" (TSF) course, lessons 1–4
(lesson 4 is "The Meta Software Factory"), the companion video "ELITE Agentic Engineers Are
LEAVING THE LOOP", Kent C. Dodds' "The End of Code Review" (idea 16 only; not part of the
course), Steve Yegge's "Software Factories: Escape from Trash Mountain" (idea 17, the stall note
under idea 9 and the Yegge caveats; not part of the course), and "Everything changed", one
developer's orchestration workflow (idea 18 and the notes under ideas 1 and 8; not part of the
course). Sales pitch, filler and the course's web UI specifics are dropped. Each idea maps to the
closest Claude Code mechanism, as a worked example; in another harness, use its equivalent. Use
this as a checklist when auditing a project's harness.

## Core thesis

- **In loop → near loop → out loop.** In loop: you prompt, the agent waits for you. Near loop:
  agents work on their own and stop only at a decision point that needs you (approve, reject,
  decide). Out loop: the system runs without you. The course targets in → near.
- **The human is the bottleneck.** The guiding question: "what can run without me next?"
- **The model is not the edge; the system around it is.** An agent is its "core four": context,
  model, prompt, tools. Engineering skill multiplies what you build on top of them.
- **Specialised beats generic.** A focused agent with focused tools, context and prompt beats one
  agent used for everything.
- **Build the system that builds the system.** Sit in the loop only to build or tune the system.
- **Counterpoint (Yegge):** don't build scaffolding to make the model smarter; it gets smarter on
  its own (the bitter lesson). The mechanical layer (merge queue, CI, review loops) is an
  afternoon's work for the agent, so build it, don't buy it. This cuts against "the system is the
  edge": the system is worth building, not worth growing.
- **Agentic engineering vs vibe coding:** know what the system does so well you don't have to look,
  as opposed to not looking because you don't know.

## Ideas

### 1. Proactive agents = durable agent + trigger + sandbox
The agent starts from an event, not from you: cron, webhook, log event, new ticket, file drop. "It
doesn't wait for you to work, it works for you, then waits." It survives restarts and runs isolated
in its own sandbox.
- Claude Code: `/schedule` (cloud routines), `/loop`, `CronCreate`; CI jobs or webhooks that start
  a headless `claude -p` run; cloud or remote sessions for isolation.
- Isolation can be a whole machine: a rented remote server, so a rogue agent never reaches the
  laptop or personal data, and parallel runs don't exhaust local hardware.
- Pays when: a repeating task has a clear trigger (nightly, per-PR, per-alert).

### 2. Cron prompts
A name, a schedule and a prompt. That's all. The cheapest way to add a repeating job.
- Claude Code: `/schedule` or `/loop`, holding a prompt that calls an existing skill.
- Pays when: a recurring check is done by hand today (dependency updates, flaky tests, docs drift).

### 3. Near-loop decision points
The agent prepares the work (triage, patch, report), then queues concrete questions for you, ideally
pushed to wherever you are (Slack, phone). Your answers flow back in as natural language and the
agent continues.
- Claude Code: `PushNotification`; a PR or draft as the approval gate; skills that end with explicit
  decisions rather than open questions.
- Pays when: work currently stalls waiting for you to start it, not to decide it.

### 4. AI developer workflows (ADWs)
Codify a workflow you run yourself as a fixed sequence, for example: detect → triage → patch → ask
→ apply → verify → save results. Incident response is the main example.
- Claude Code: a skill or `Workflow` script per workflow; hooks for the verify step.

### 5. Specialised subagents with their own core four
Each subagent gets its own model tier, system prompt, tools and budget (time and spend caps).
Downscale the model when the answer needn't be perfect.
- Claude Code: `.claude/agents/*.md` with `model` and `tools` frontmatter and a focused prompt.
- Pays when: one generic agent is used for both mechanical and judgement work.

### 6. Small agent teams with a lead
3–5 specialists, each owning one lane, led by an orchestrator that only manages: routes work, tunes
members, interrupts, steers, and never does the work itself. Agents talk in chat rooms under a
"conversation contract": reply only when addressed, read everything, keep messages short. A sweet
spot between ad-hoc subagents and costly swarms. A strong model as lead with cheaper workhorse
models below it.
- Claude Code: parallel sessions in separate worktrees with a coordinator session (e.g. the `lanes`
  skill); `Workflow`
  for one-shot fan-out.
- Pays when: work splits into parallel lanes that need coordinating, not just parallel answers.
- Lesson 4 adds: one **owner agent per running factory** that owns only that factory's changelog
  and specialisation; only the lead can hire, and every hire is an approval point ("not subagent
  delegation, not agent swarms"). Leads of different factories message each other through a
  **factory mailbox** (list and send tools), so a harness can route work to another place.
- Claude Code: `SendMessage` between sessions in different repos, or a terminal multiplexer's
  command that prompts another session.

### 7. Agentic access parity
Everything you can do, the agent can do: every UI control and setting has a matching tool, so the
agent can reconfigure itself and the system. Bounded by limits you set.
- Claude Code: project scripts and CLIs for every manual step (deploy, seed, reset, inspect), so
  the agent never needs you to click; `update-config` for harness settings.
- Pays when: a task needs a manual step only a human can do today.

### 8. Damage control: remove capability, don't just guard it
Pick tools per agent. If bash is dangerous for a role, remove it and give the agent the exact
narrow tools it needs. Self-modification is capped.
- Claude Code: `PreToolUse` hooks, permission deny rules, per-agent `tools` lists.
- **Constrain the code, not only the tools.** A strict, typed stack plus lint rules (the example is
  the Effect library with Effect lint rules) "almost forces" agents to write code within the
  guardrails. The stack choice is one of the decisions that stays with the human.
- Claude Code: the repo's type checker and linter as a `PostToolUse` or `Stop` hook, or as a CI
  gate.

### 9. Observability: traces and tool summaries
Log every run: prompt, inputs, tool calls, outputs, cost. A cheap model summarises tool calls into
plain sentences so you can follow an agent without reading raw traces. "If you don't measure, you
can't improve."
- Claude Code: status line; `PostToolUse` or `Stop` hooks that append a summary or cost line to a
  log.
- **Stalled work (Yegge).** The daily failure is not a bad run but no run: workers that did nothing
  overnight, work pooled behind one gate. One agent's only job is to look for work nobody is
  looking at.
- Claude Code: a scheduled prompt (idea 2) that lists stale branches, PRs and tasks with no
  activity since the last check.

### 10. Classifier gates (Jev)
Jev (TypeSafe AI, Sept 2026) is a discriminative model that returns typed values, probability
distributions and calibrated confidence in one pass. It is not a text generator. In the videos it
classifies log events as issue or no issue, scores news items, and judges UI similarity. Use it
where the agent needs a fast typed verdict before continuing: route, ignore, escalate, pass/fail.
Not needed where a deterministic check exists (for example, HTTP 4xx/5xx).
- Claude Code: a hook or script that calls the classifier and blocks or routes on the result.

### 11. Hill-climbing (RSI) loops against a verifiable target
Build → measure → compare → fix, repeated until a threshold is met (for example, UI similarity to
a mock). You start it and walk away for ~30 minutes.
- Claude Code: a skill or `Workflow` with an explicit metric and stop condition (score, test pass,
  iteration cap).
- Pays when: the result can be scored automatically.

### 12. Feedback flywheel
Your near-loop signals (upvotes, approvals, rejections) are stored and change what the agent does
next time.
- Claude Code: memory files, or a "learnings" section the agent updates; `revise-claude-md`.

### 13. Template → init → configure → specialise
Keep a generic harness template with good defaults. Mount it into a repo with one command
(init), shape it with a written plan of about 150 lines (configure), then specialise per problem.
- Claude Code: a personal plugin or skill set reused across repos; `/init` plus a project plan.
- **Backport (lesson 4).** A feature built in one running factory that isn't project-specific gets
  ported back into the template, so every new factory starts with one more capability than the
  last. The work compounds instead of being rebuilt per project. There are three states: template
  → empty factory → running factory.
- **The template is a managed artifact.** It has a spec, an append-only changelog (change, reason,
  human decision, diff) and a list of the running factories made from it. A change to it spreads to
  every future factory, so committing one is always an approval point (idea 3).
- Claude Code: the shared skills/plugin repo is the template; its git history and PRs are the
  changelog; a hook, agent or skill that a project grows and others could use goes back there as a
  PR.
- Pays when: several repos share one harness and fixes made in one never reach the others.

### 14. "Liquid software" and DX
Tooling is meant to be reshaped: themes, hotkeys, nav, settings. Good DX makes you invest in the
tool.
- Claude Code: keybindings, status line, output style. Low priority for a harness audit.

### 15. Tokenomics and model tiers
Pick the model per job on the performance, cost and speed trade-off. A strong model at low or
medium effort is often enough. Subscriptions are subsidised and won't last, so know your cost per
task.
- Claude Code: `model` per agent; effort levels.

### 16. Intent-level review: executable laws
Review the intent, not the diff. Before any code exists, the spec is written as machine-checkable
laws (invariants over all inputs); the human reviews the laws, and the implementation is gated on
passing them, not on someone reading it. Agents write code faster than anyone can read diffs, and
adding more AI reviewers keeps finding new nits without ever converging. Formal proof is the ideal;
the practical version shown is property-based tests: a law list run against many generated inputs.
The laws are hard to read, so an agent translates them back into plain language and the human
reviews that translation.
- Claude Code: a laws file per module (property tests: fast-check, Hypothesis or similar),
  written first; reader-test back-translation (lens 6) on it before implementation; once approved,
  the laws are frozen against the implementer (a `PreToolUse` hook or an `Edit(<laws path>)` deny
  rule), and a different agent from the laws author implements; CI runs the laws as the gate;
  idea 11 can loop on "all laws pass".
- Limits: property tests sample inputs and do not prove anything; laws check only what they state,
  so a gap in the spec still passes and spec review gets heavier, not lighter; an agent that writes
  both laws and code can bend either side until they agree. It fits pure, contained logic (storage,
  parsers, money maths, state machines), not UI, integrations, security or performance; diffs that
  touch a trust boundary, secrets or amounts keep their normal review. The author says he has not
  shipped it himself yet.
- Pays when: diff review of a contained module is the bottleneck, or reviews of it keep finding
  logic bugs that a stated invariant would have caught.

### 17. Prune the rules: the append-only dump
Agents write every ruling down and never delete anything, so instruction files and memory grow into
a record of every change of mind. Taken far enough this is **overfencing**: rules piled up after
corrections until no legal work was left and the factory sat idle. Complaints make it worse,
because agents answer blame with more defensive rules. The fix is a regular pass by a fresh model
whose only job is to delete: stale, superseded and duplicate rules.
- Claude Code: a deletion-only pass over CLAUDE.md, memory and skill files by an agent that did not
  write them (`claude-md-improver`, memory cleanup), with additions forbidden as in a reader-test
  lens; corrections phrased as the rule plus why, not as blame.
- Pays when: instruction files only ever grow, or agents stop doing things nobody forbade outright.

### 18. Reports generated from the code
After a run you don't read the diff; you read a report on what was built. As much of it as possible
is generated by a script from the actual code: how actions flow through the app, how the parts
relate, a test-coverage overview. The AI only adds descriptions, because "the AI can lie to you".
From one such report the author spotted a missing signup path, a claim the report contradicted
elsewhere, and error cases no test covered, without opening the code. Questions go back to the
lead agent, which fixes the work or the report format.
- Differs from idea 9 (what the agent did) and idea 16 (laws written before the code): this checks
  what was built, after the fact, against the code itself.
- Claude Code: a project script that emits the report (route or call graph, module dependencies,
  coverage including error paths), run by a `Stop` hook or at the end of a skill or `Workflow`; the
  agent's summary goes beside it, never in place of it.
- Pays when: unattended runs end in an agent-written summary that nobody can check without reading
  the diff.

## Caveats from the course itself

- TSF patterns are deliberate shortcuts: "not recommended as long-term solutions", optimised for
  shipping fast. Treat them as a quick path to value, not production architecture.
- Self-modifying agents are dangerous without limits.
- Measure of success: how many agents do useful work for you right now. Not token-maxing, not
  `while` loops doing random work.

## Caveats from the Yegge talk

- One operator's anecdotes at a scale few can afford (20+ Max subscriptions, ~50 agents), with
  nothing measured. The source is auto-captions without the slides.
- **Output can outrun the humans downstream.** His factory shipped features faster than his users
  could read about them, and they asked him to slow down. The bottleneck is also everyone who has
  to absorb the work, not only the person who starts it.
- **Expect to rebuild.** Each model generation builds something slightly too big for itself to
  maintain; he rewrote his factory about every two months. Keep the harness cheap to throw away.
- Unverified claim: agents that start from notes left by previous holders of their role spend fewer
  tokens checking their environment and act more boldly.

## Caveats from "Everything changed"

- One demo project, nothing measured; about a third of the video is a course ad, and the
  orchestration scripts, skill and report schema are behind the paywall and never shown.

## Questions for a harness audit

1. Which recurring tasks are started by hand but have a natural trigger? (1, 2)
2. Where does work stall waiting for a human to start it, not to decide it? (3)
3. Which workflows do we run step by step that could be codified? (4, 11)
4. Is one generic agent doing both mechanical and judgement work? (5, 15)
5. Which steps need a human because no tool exists for the agent? (7)
6. Which agents hold more capability than their role needs? (8)
7. Can we see what an unattended run did, and what it cost? (9)
8. Where would a typed pass/fail verdict let an agent continue without us? (10)
9. Do our approvals and rejections feed back into the harness? (12)
10. Do harness improvements made in one project flow back to the shared template, and do we know
    which projects run which version of it? (13)
11. Which modules are gated by someone reading the diff, but could be gated by stated laws that
    the human reviews instead? (16)
12. When did anyone last delete a rule from our instruction files, and which rules stop agents
    from doing work we want done? (17)
13. After an unattended run, what tells us what was built, and how much of that is generated from
    the code rather than written by the agent? (18)
