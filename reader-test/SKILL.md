---
name: reader-test
description: >
  Use when a spec, plan, proposal, estimate or client-facing document has been written
  or substantially revised and someone else is about to act on it — before it ships, is
  sent, or gets built from, and above all when an error in it would cost money or
  rework. Surfaces the errors a document's own author cannot see. Also triggers on
  "reader test", "прогони читателей", "check this doc", "find what's wrong with this
  spec", "is this ready to send?". DO NOT trigger for copy-editing, tone or formatting —
  this finds errors of fact, arithmetic and specification, not prose problems.
license: MIT
---

# Reader testing

A document you wrote is unreadable to you. You know what it means, so you read your
intent instead of your words. Every serious error in a document you authored is invisible
from inside the authoring context — not because you were careless, but because the missing
sentence is present in your head.

The fix is to hand the file to readers who have nothing but the file.

## The one rule

**Readers get files, never conversation.** No summary of what the document is for, no
"we decided X earlier", no warning about which parts are shaky. The moment you supply
context you have rebuilt the blindness you are trying to escape — the reader will read
your framing instead of the file, and confirm you.

State this to each reader explicitly ("you have no context from any prior conversation —
that is deliberate"), or they will apologise for the gap and hedge every finding.

## Shaping the prompt

Three things decide whether you get findings or a book report.

**One lens per reader, and forbid the others.** "Review this document" returns a shallow
sweep of everything and nothing. A reader restricted to arithmetic and explicitly told
that wording, structure and missing features belong to other readers cannot retreat to
the easy findings — it has to keep digging in its own territory. Name the forbidden
territory in the prompt; "focus on X" is weaker than "do not report Y, another reader
has that lens."

**Demand checkability.** Require a line number, a quote, and for numbers the arithmetic.
Tell them plainly: *a finding I cannot check against the file is worthless.* This is what
separates a reader from a critic, and it also suppresses the vague "consider clarifying"
noise that costs you time to triage.

**Ask for coverage, not just hits.** Have fact-checking readers end with a short list of
what they checked and found *correct*. Without it you cannot tell a clean document from a
lazy reader, and you will not know which parts went unread.

Two smaller things that pay for themselves: give absolute paths, and forbid editing
(`DO NOT EDIT ANY FILE`) — a reader that starts fixing stops reading. On very large
documents, narrow each reader to the fewest files it needs; readers asked to hold several
long files at once fail mid-response more often, and the recovery is to relaunch with a
tighter scope rather than to retry the same prompt.

### The shape of a reader prompt

Assembled, those requirements look like this. Substitute the lens, and keep the rest —
each line is load-bearing, and the one that gets dropped when this is rebuilt from memory
is the forbidding of the other lenses, which is the line that buys the depth.

```text
You are reviewing a document. You have no context from any prior conversation — that is
deliberate. Do not ask for it and do not apologise for it. The file is all you get, and
it is all the next person to read it will get either.

Read: /absolute/path/to/document.md
For checking claims against their source, you may also open: /absolute/path/to/repo

Your lens is <LENS NAME>, and only that: <one-sentence position>.
Other readers have the other lenses. Do not report <lens>, <lens> or <lens> — findings
outside your lens are noise here, and reporting them costs me the depth I need inside it.

DO NOT EDIT ANY FILE. You are reading, not fixing.

For each finding give the line number, the quoted text, and what is wrong with it. Where
a number is involved, show the arithmetic and compute it with a script rather than in
your head. A finding I cannot check against the file is worthless to me.

Finish with a short list of what you checked and found correct, so I can tell a clean
document from an unread section.
```

### Without parallel readers

The isolation is what does the work, not the parallelism. In a harness that cannot
dispatch subagents, open a fresh session per lens, attach only the file, and paste the
same prompt — slower, and you lose nothing but wall clock. What does not substitute is
running the lenses yourself in the session where the document was written: there you
would be reading your intent again, which is the exact failure the whole harness exists
to route around.

## The lenses

Four are the standard set. Add the fifth whenever the document describes a system that
handles money, personal data, or anything irreversible.

### 1. The executor

*Position*: "You have been handed this and told to build it starting Monday, and told not
to come back with questions. Where would you have to guess?"

Finds: unstated triggers and ordering; branches with no defined outcome; a flag written
and never read; a state entered and never left; a thing linked to that nothing builds;
happy-path-only behaviour; two sections implying different behaviour; code assumed to
already exist.

Ask for the finding phrased as *the question they would be forced to answer themselves* —
that phrasing is what makes the gap concrete instead of "section 3 is underspecified".

### 2. The numbers auditor

*Position*: recompute everything; trust no stated total.

Require a script for every calculation and require the arithmetic in the report. Point it
explicitly at any estimate table and at the whole chain that hangs off it — rows → sum →
unit conversion → comparison against a previous figure — because that chain is where the
same number gets restated four times and drifts. Also: units and orders of magnitude, any
figure stated in two places, and every "X is cheaper/faster than Y" claim that has numbers
behind it. Counts in prose ("three reasons", "seven fields") are numbers too: make it count
the list that follows.

### 3. Source fidelity

*Position*: "does the source actually say that?"

Give it the repository paths so it can open the code and the correspondence. It checks
`file.md:123` citations for both rot (the lines moved) and substance (the source never
said it). Two classes deserve to be called out in the prompt, because they are the
expensive ones:

- **Claims about what was said to or agreed with another party.** An intention recorded
  as a completed action is the single most damaging error a planning document can carry,
  and it is invisible to every other lens. Tell the reader that a draft is not a sent
  message and that message files may record their own status.
- **Claims about code behaviour.** "The endpoint returns X", "this field carries no
  address" — these get written from memory and are wrong about a third of the time.

### 4. Internal consistency

*Position*: the document against itself, no other files.

Revision leaves scars. This lens hunts the stale region: analysis that a later section
contradicts, replaces or delegates away, but which still reads as live — the most
dangerous class, because a reader going top-to-bottom acts on it before reaching the
correction. Also: superseded markers whose scope is unclear, terms used with two meanings,
internal cross-references pointing at sections that do not say that, and future-tense
statements that a later section reports as done.

### 5. Money and data risk

*Position*: adversarial, and its mirror.

Give it the promises document (terms, contract, published copy) alongside the design, and
send it in two directions:

- **The attacker** who wants to be paid twice, paid for someone else's work, to exceed a
  cap, or to break intake for everyone. What does the system actually *prove*, versus what
  does it *assume*?
- **The honest user who loses out** — the path where someone does everything right and
  ends up unpaid *and never finds out*: a submission that looks accepted but is not, a
  state with no exit, a rejection with no outbound channel, a deadline they cannot see.

Require concrete walkthroughs with names and exact field names. "Insufficient validation"
is not a finding; "Alice files with Bob's txid, signature verifies against her own address,
nothing ties the two" is.

## Choosing and sizing

Run all four (or five) against one document rather than one lens against four documents —
the lenses are what generate depth. For a document set, add a cross-document reader whose
only job is figure agreement across files, since hand-propagated numbers fall out of step
exactly there.

Scale by consequence, not length. A one-page thing nobody builds from does not need this.
A specification someone will implement, an estimate that becomes a price, or a document
going to a client, does.

## Triaging what comes back

**Findings are suspicions, not verdicts.** Readers lack context by construction, so some
findings are the context working as intended. Check each against the file before acting —
but check, do not dismiss: the reflex to explain why a finding is fine is the same reflex
that produced the gap.

**Look for a direction.** Errors in a document are rarely random. If several findings are
all "stated as done but only decided", or all "the estimate grew where a mechanism was
missing", the direction is the real finding and it predicts the errors nobody caught.

**A gap is not automatically a thing to fill.** Findings arrive phrased as absence — "this
state has no exit", "this term has no clearing action", "this column has no source" — and
absence asks to be filled. But the same finding is equally evidence that *the mechanism
should not exist*. Decide by scale: if a mechanism serves thirty events over five months
and repairing it costs more than a person looking at a thirty-row table, the finding is
telling you to delete, not to specify. Answering every gap with an addition is how a
document grows a third in size and an estimate doubles across three passes while the
thing actually delivered stays the same — and it is the most common way this harness gets
misused, because the additions all look justified one at a time.

**Repeats across lenses are load-bearing.** Two readers forbidden from each other's
territory arriving at the same passage means the passage is genuinely broken.

**Expect the passes to differ in kind, not to shrink.** In practice the first pass finds
errors, the second finds under-specification, and a pass on an older approved document
finds missing mechanisms. A second pass returning a shorter list is not evidence of
convergence — check that the lenses were the same before you read it that way.

## Reporting to the user

Lead with what changes their decision — the finding that alters a number, a promise, or a
build order — not with the count. Say what you verified and rejected, and say which
findings you have not yet fixed, by name. If the pass moved a figure that someone else is
holding, that consequence is the headline, not a footnote.

## Cost

A full pass is several hundred thousand tokens and a few minutes of wall clock. That is
cheap against one wrong number in a document that becomes a price, and cheap against
building the wrong thing for two days. It is not cheap enough to run on every edit — run
it when a document has been substantially revised, when it is about to be acted on, and
again after a revision large enough to have introduced new stale regions.
