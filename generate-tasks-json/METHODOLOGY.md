## Rules for GitHub Issues & Project Board

These rules govern how features are planned, decomposed, and tracked as GitHub issues. They are designed to keep issue trees small, reviewable, and aligned with how the work actually ships through PRs.

---

### 1. Single Source of Truth

- All feature discussions, bug reports, and technical decisions must take place within **GitHub Issues**, not in external messengers. This ensures a searchable history for stakeholders and the team.

---

### 2. Milestone-Driven Progress

- Every issue must be attached to a specific **Milestone** (e.g. `v1`). This allows the Product Owner (or whoever tracks delivery) to see overall release completion at a glance.

---

### 3. Assignment Principle

- **One Responsible Person per Issue:** Each issue must have exactly **one assignee**.
- Assignment defines ownership and responsibility for delivery.
- Detailed assignment rules are in **Section 7**.

---

### 4. No Direct Pushes to Master

- All code changes must be submitted via **Pull Requests (PR)**.
- Every PR should reference its corresponding issue number in the description (e.g. `Closes #12`). This triggers GitHub automation to move the issue to the **Done** column and close it automatically upon merge.

---

### 5. Project Board Management (Board View)

- The **Board** view is the primary tool for daily operations.
- **Status Integrity:** developers are responsible for keeping their cards up to date:
  - Move to **In Progress** when work starts.
  - Move toward **Review / Done** when a PR is opened.

- **Group by Assignee:** the board should be viewed with this grouping to visualize workload distribution clearly.

---

## 6. Flexible Issue Structure per Feature

We use a **two-level issue hierarchy**.

---

### 6.1. Feature (Parent Issue)

- A **Feature** represents a complete, user-visible piece of functionality (e.g. "User Profile Page", "Bulk Export").
- Each Feature is created as a **parent issue** with `issue_type: Feature`.
- A Feature must have:
  - a clear description of scope,
  - exactly **one assignee** (Feature Owner).

**Feature Owner responsibilities:**

- Overall coordination.
- Ensuring all sub-issues are completed.
- Integration into a working result.

---

### 6.2. Sub-issues (Implementation Tasks)

Each sub-issue represents a **concrete, executable unit of work**:

- should be completable in a single PR,
- should not require deep implicit knowledge from other issues.

Sub-issues are created with:

- `type: sub-issue`,
- `issue_type: Task`.

**Examples:**

- Data aggregation / business logic.
- Database schema / queries / indexing.
- API endpoint / WebSocket / event schema.
- UI rendering (templates, controllers).
- Client-side behavior.

---

### 6.2.1. The contract is the seam (default decomposition)

Most Features have the same shape: some part of the system **produces** data or behavior, and another part **consumes** it. The work splits cleanly along the **contract between them**, and that is the _only_ split made by default.

- **No contract** (the change is purely on one side — say, a pure visual tweak or a pure backend refactor with no observable contract change) → a **single `issue`**, with checkbox steps in its description for internal planning. No sub-issues.
- **There is a contract** → **1 Feature (`parent`) + exactly 2 sub-issues**: one for the side that **produces** the contract (typically `[DATA]` / `[WS]` / `[API]` / `[DB]`) and one for the side that **consumes** it (typically `[UI]`).
- **More than two sub-issues is the exception**, allowed only when one side is genuinely several independent PRs (e.g. a schema migration that must land before the aggregation depending on it). A `[DOCS]` follow-up is the one routine third.

**Examples of producer ↔ consumer handoffs** the contract-as-seam rule applies to:

- Backend service → Frontend view — the HTTP / WebSocket payload is the contract.
- Server-rendered template ↔ progressive-enhancement JS controller — the rendered DOM and data-attributes are the contract.
- Microservice A → Microservice B — the wire protocol / event schema is the contract.
- Library or SDK → consumer app — the public API surface is the contract.

Whatever the handoff, the producer sub-issue's acceptance criterion is "the contract is delivered as agreed" (often a schema / parity / contract test) and the consumer sub-issue's acceptance criterion is "rendered correctly against that contract" (typically the spec's own acceptance checklist).

**Keep the contract fat, not raw.** Push computation, formatting, and any precision-sensitive values behind the contract — the consumer should render, not compute. This also balances workload between the two sub-issues. Balance volume via contract fatness, never by padding the issue count.

The producer side may cascade across several modules or packages — that is still **one** sub-issue (the contract), never one-per-module. A single sub-issue that touches three packages is fine; three sub-issues for the same contract is over-decomposition.

Over-decomposition (many thin issues split by underlying layer) is the most common planning failure. Fewer, contract-aligned issues are preferred every time.

---

### 6.3. Structure Constraints

- Only **two levels are allowed**: Feature → Sub-issues.
- ❌ No nested sub-tasks or deeper hierarchies.
- **A `parent` must have sub-issues — a childless `parent` is invalid.** A Feature too small to split, or with no producer↔consumer contract, is created as a single `type: issue` (with checkbox steps in its description), **not** as a `parent` with nothing under it.
- The default is **exactly two sub-issues** (see §6.2.1); deviating in either direction requires the reasoning stated in §6.2.1.

---

### 6.4. Naming Convention (Prefixes)

Sub-issue titles must use a prefix that signals the area of responsibility. The default prefix set:

- `[API]`
- `[DB]`
- `[UI]`
- `[WS]`
- `[DATA]`
- `[DOCS]`

**Example:**

```text
[API] User profile endpoint
[UI] User profile page rendering
[DB] Profile activity index
[DOCS] Document the user profile page
```

Adapt the set to your stack — add `[INFRA]`, `[MOBILE]`, `[ML]`, etc. if they're load-bearing in your project. Keep the set small; if every issue needs a different prefix, the prefix is no longer signal.

---

### 6.5. Prefix Selection Rule (Single Responsibility)

Each sub-issue must use **exactly one prefix**.

Prefixes do **not** represent all affected parts of the system. They must reflect the **primary area of responsibility** — where the main work is performed.

**Rules:**

- Always choose **one dominant prefix**.
- Do **not** combine prefixes (e.g. ❌ `[API][DB][UI]`).
- If a task spans multiple domains equally:
  - Split it into multiple sub-issues.
  - In practice this is the producer↔consumer contract split of §6.2.1; splitting further, per touched layer, is the exception, not the default.

---

### 6.6. How to Choose the Prefix

Select the prefix based on the **initiator of the change** — where the work actually happens:

- `[API]` — endpoint or data contract.
- `[DB]` — schema, queries, indexing, performance.
- `[UI]` — rendering, templates, interaction.
- `[WS]` — WebSocket / real-time updates.
- `[DATA]` — aggregation, transformation, internal logic.
- `[DOCS]` — documentation (wiki, README, in-repo guides).

---

### 6.7. Splitting Rule

Instead of:

```text
[API][UI] Add sorting to a list
```

Do:

```text
[API] Add sorting support to the endpoint
[UI] Implement sorting in the list view
```

This is the producer↔consumer contract split of §6.2.1 — the producer side and the consumer side. Do **not** split further by layer (DB vs. DATA vs. WS) unless one side is genuinely several independent PRs.

---

## 7. Developers & Assignment Strategy

Strict frontend/backend ownership is not enforced.

---

### 7.1. General Principle

- Any developer can work on any issue.
- Assignment defines **responsibility**, not specialization.
- Code review ensures cross-domain quality.

---

### 7.2. Prefix-Based Assignment (Recommended)

Assignments should be guided by the **issue prefix**, but also balanced across the team. Define a default mapping for your team — example:

- `[DB]`, `[DATA]`, `[WS]`, `[API]` → preferably assign to **alice**.
- `[UI]` → preferably assign to **bob**.
- `[DOCS]` → assign to whoever has the most context on the area being documented (no fixed default).

Replace `alice` / `bob` with your team's actual GitHub logins.

**Balancing rule:**

- Do not strictly follow the preferred mapping if it creates workload imbalance.
- If one developer becomes a bottleneck, issues should be reassigned to the other.
- Load balancing has higher priority than specialization.

**Goal:**

- Maintain steady delivery flow.
- Avoid bottlenecks.
- Encourage cross-domain contribution.

---

### 7.3. Important Constraints

- The mapping is a **guideline, not a restriction**.
- Do **not** split or reassign issues purely based on specialization.
- Do **not** create additional sub-issues just to match assignment preferences.

---

### 7.4. Assignment Responsibility

- Each issue must have **exactly one assignee**.
- The assignee is responsible for:
  - implementation,
  - opening the PR,
  - driving the issue to completion.

---

### 7.5. Flexibility in Practice

- Developers may take issues outside their "preferred" area.
- Cross-domain work is encouraged.
- Reviews should be performed by the most experienced developer in the relevant area.

---

### 7.6. Labels

Use a **strict and predefined set of labels**.

Only labels that already exist in the repository are allowed. **If a label does not exist on GitHub, the issue creation script will fail.** That failure is intentional — it forces the allowed set to stay curated.

#### Allowed labels (example set)

- `enhancement`
- `bug`
- `infrastructure`
- `documentation`
- `refactoring` (use only when behavior does not change)

Adapt the list to your repo's actual labels.

#### Rules

- Only use labels from the approved list above.
- Do **not** introduce new labels without updating the repository first.
- Do **not** use generic or low-value labels such as `duplicate`, `invalid`, `wontfix`, `question`, `good first issue`, `help wanted`.

#### Notes

- Labels are **optional** and should be used only when they add value.
- Over-labeling should be avoided.
- Issue classification should rely primarily on:
  - structure (Feature / sub-issue),
  - prefixes (`[API]`, `[DB]`, etc.).

---

## 8. Automated Issue Creation

To speed up the creation of large milestones, we use a Node.js script (`create-issues.js`) that reads a `tasks.json` file and handles parent / sub-issue linking via the GitHub API.

---

### 8.1. Prerequisites

- `brew install gh`
- `gh auth login`
- Node.js ≥ 18

---

### 8.2. JSON Structure & Rules

`tasks.json` is an array of task objects. Each task requires a unique string `id`.

**Types:**

- `parent` → Feature.
- `sub-issue` → Task linked to parent.
- `issue` → standalone task.

---

### 8.3. Important Rules

- Sub-issues must follow the **prefix naming convention**.
- Issue structure must follow the **two-level hierarchy**.
- Default to **one Feature + two contract-aligned sub-issues** (§6.2.1); a childless `parent` is invalid (§6.3).
- Do **not** split tasks based on developer specialization.
- Sub-issues should reflect **system boundaries** (API, DB, UI, etc.), not roles.
- Assignment should follow the **Prefix-Based Assignment rule**, but may be adjusted for balance.

---

### 8.4. Example `tasks.json`

The canonical shape: one Feature + the two contract sides (+ a routine `[DOCS]` follow-up when the project ships docs alongside the area):

```json
{
  "tasks": [
    {
      "id": "feature-user-profile",
      "type": "parent",
      "issue_type": "Feature",
      "title": "User Profile Page",
      "description": "Display a user's profile at /users/:username (name, avatar, bio, recent activity). Spec: docs/specs/user-profile.md.",
      "assignee": "alice",
      "labels": ["enhancement"]
    },
    {
      "id": "user-profile-contract",
      "type": "sub-issue",
      "parent": "feature-user-profile",
      "issue_type": "Task",
      "title": "[API] User profile endpoint",
      "description": "Deliver GET /api/users/:username returning { name, avatar_url, bio, recent_activity[] }. Recent activity is computed and shaped server-side (no joining or aggregation on the client). Acceptance: schema test against the agreed JSON shape; auth / visibility rules enforced per spec.",
      "assignee": "alice",
      "labels": ["enhancement"]
    },
    {
      "id": "user-profile-ui",
      "type": "sub-issue",
      "parent": "feature-user-profile",
      "issue_type": "Task",
      "title": "[UI] User profile page rendering",
      "description": "Render the profile page against the agreed API shape. Acceptance is the spec's acceptance checklist (header layout, empty state when no recent activity, loading skeleton, 404 error state).",
      "assignee": "bob",
      "labels": ["enhancement"]
    },
    {
      "id": "user-profile-docs",
      "type": "sub-issue",
      "parent": "feature-user-profile",
      "issue_type": "Task",
      "title": "[DOCS] Document the user profile page",
      "description": "After the two implementation issues land, document the shipped endpoint surface, page anatomy, and any known limitations in docs/user-profile.md.",
      "assignee": "bob",
      "labels": ["documentation"]
    }
  ]
}
```

**Exception (more than two implementation sub-issues):** only when one contract side is genuinely several independent PRs — e.g. a DB schema migration that must merge before the aggregation depending on it, justifying a separate `[DB]` issue ahead of `[DATA]`. This is the documented exception of §6.2.1, not the template.

---

### 8.5. Running the script

```bash
# Dry-run (validates and prints what WILL be created using deterministic mock IDs, no API calls):
REPO="your-org/your-repo" MILESTONE="v1" node create-issues.js --dry-run

# Live run (creates real issues; pauses for typed 'yes' confirmation):
REPO="your-org/your-repo" MILESTONE="v1" node create-issues.js

# Resume a previous failed or interrupted run to prevent duplicate issues:
REPO="your-org/your-repo" MILESTONE="v1" node create-issues.js --resume

# Skip the interactive confirmation prompt (useful for CI):
REPO="your-org/your-repo" MILESTONE="v1" node create-issues.js -y

# Point at a tasks.json elsewhere on disk:
REPO="your-org/your-repo" MILESTONE="v1" node create-issues.js --file path/to/tasks.json
```

`REPO` is required (`<org>/<repo>`). `MILESTONE` defaults to `v1` — the milestone must already exist in the repo.
