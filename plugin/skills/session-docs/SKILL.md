---
name: session-docs
user-invocable: true
description: >
  Keeps all project documentation in sync — reads at session start, writes
  immediately after new findings. Use this skill for any project that has
  KNOWN_ISSUES.md, HANDOVER.md, memory files, or a task list. Triggers
  automatically: at session start (read mode), after every CI log or tool
  result that brings new information (write mode), after any user correction
  or preference (memory write), after any status change (task list update),
  and explicitly on "session abschliessen", "übergabe vorbereiten",
  "aufräumen", "dokumentieren", "was ist der aktuelle Stand".
  Also invocable via /session-start to guarantee a full read at the start
  of any new chat — regardless of the opening message.
  Creates missing files from templates — never asks whether to create, just
  creates and fills.
  Do NOT use for: general file editing unrelated to project documentation,
  writing code, or tasks outside the four documentation types.
---

# session-docs — Project Documentation Always in Sync

This skill manages four documentation locations throughout a work session.
It reads at the right moment to give Claude full context, and writes
immediately when new information arrives — not at the end of the session.

---

## Language

Read `../_shared/language.md` and apply the output language rules defined there.
Always respond in the language the user writes in.

## Environment detection

Read `../_shared/environments.md` and handle accordingly.
Web fallback: see "Procedure in Claude AI (Web)" below.

## Security — never repeat credentials

When reading project files (HANDOVER.md, credentials.md, memory files), you
will encounter API tokens, passwords, and SSH keys. Never repeat these values
in your response. Refer to them by name only: "the API token", "the webhook
secret". This applies to session start summaries, fix suggestions, and all
other output.

---

## Invocation model

Pattern 3 — Auto + Command. No `disable-model-invocation` flag. This skill
fires automatically whenever its trigger conditions are met. Additionally,
the `/session-start` command guarantees a full READ MODE run at the start of
any new chat — regardless of the opening message. Use `/session-start` when
starting a new session without a HANDOVER.md as the opening message.

---

## The four documentation locations

| Location | File | Trigger: Read | Trigger: Write |
|---|---|---|---|
| Known Issues | `KNOWN_ISSUES.md` | Session start | After every new finding |
| Handover | `HANDOVER.md` | Session start | After every direction change |
| Memory | `.auto-memory/*.md` | Session start (index), on-demand (detail) | After every user correction or new project fact |
| Task list | TaskCreate/TaskUpdate tools | Before starting any task | At start and end of every work step |

---

## Procedure with file access (Claude Code & Cowork)

### READ MODE — Session Start

At the very beginning of a session, before any other action, read in this order:

1. **MEMORY.md index** — scan for entries relevant to the current project.
   Read the individual memory files that seem relevant. This tells Claude
   about preferences, past mistakes, and project facts.

2. **KNOWN_ISSUES.md** — read all open issues. This prevents running into
   already-known dead ends. Pay attention to: active blockers, confirmed
   root causes, things already ruled out.

3. **HANDOVER.md** — read the "Aktiver Blocker" / "Next Step" section.
   This is the single most important thing: what should happen right now?

4. **Task list** — call TaskList to see what is pending or in progress.
   Avoid creating duplicate tasks.

If any of these files do not exist: create them from the templates in
`references/templates.md` before proceeding. Fill in what is already known
from context; mark unknowns as `<!-- TODO: fill in -->`.

---

### WRITE MODE — Four triggers, four rules

#### Trigger 1: New finding from a tool result → KNOWN_ISSUES.md

When a tool result (CI log, API response, file read, bash output) contains
new information about a known or new issue:

1. If the issue already has a KI-NNN entry: add the finding as a new line
   under the current run's subsection. Update `**Status:**` if it changed.
   Mark confirmed root causes and ruled-out hypotheses explicitly.
2. If this is a new issue: create a new KI-NNN entry with Status, Symptom,
   Ursache (if known), and the first finding.
3. If an issue is now resolved: move it to the archive table at the bottom.
4. Always update `*Zuletzt aktualisiert*` timestamp.

Do this **before** taking the next action. Not at the end of the session.

**What to record:** new findings, confirmed hypotheses, ruled-out hypotheses
("X ist NICHT die Ursache" is as valuable as "X ist die Ursache"), timing
data, error messages with run number references.

---

#### Trigger 2: Direction change → HANDOVER.md

When the active blocker changes, an issue is resolved, or a new diagnostic
approach is taken:

1. Update the "Aktiver Blocker" / "Next Step" section — what is the concrete
   next action?
2. Add newly resolved items to "Was bereits geklärt ist" / "What is done".
3. Adjust the priority of the waiting task list.
4. Update the stand timestamp at the bottom: `*Stand: YYYY-MM-DD (Run #NNN) — one-line summary*`

Do NOT update: infrastructure reference sections, workflow code snippets —
these change only with real stack changes.

---

#### Trigger 3: User correction or new project fact → Memory

When the user corrects an approach, states a preference, or a new
durable project fact is confirmed:

1. Check MEMORY.md index — does a relevant entry already exist?
2. If yes: update the existing file. Do not create a duplicate.
3. If no: create a new `<type>_<topic>.md` file and add a line to MEMORY.md.
4. MEMORY.md line format: `- [Title](file.md) — one-line hook` (max 150 chars)

Memory file format:
```markdown
---
name: Short name
description: One-liner — used to decide relevance in future sessions
type: feedback | project | user | reference
---

The fact or rule. For feedback/project: lead with the rule, then:
**Why:** the reason the user gave.
**How to apply:** when and where this kicks in.
```

Do NOT put in memory: code patterns, git history, temporary debugging state,
things readable from the current code, the current session's work-in-progress.

---

#### Trigger 4: Task started or completed → Task list

- New task identified → `TaskCreate` immediately, before starting the work
- Task being started → `TaskUpdate` status: `in_progress` BEFORE the first action
- Task completed → `TaskUpdate` status: `completed`
- Task no longer relevant → `TaskUpdate` status: `deleted`

Right granularity: one task = one concrete, completable work step.
Not too coarse ("debug git-pages"), not too fine ("read log line 47").
Good: "Check putBlobSemaphore deadlock via goroutine dump".

---

### SESSION CLOSE — Explicit checklist

When the user says "session abschliessen", "übergabe vorbereiten",
"aufräumen", or similar: run this checklist in full.

1. **KNOWN_ISSUES.md**
   - [ ] All findings from this session recorded?
   - [ ] New issues created?
   - [ ] Resolved issues moved to archive?
   - [ ] All statuses correct?

2. **HANDOVER.md**
   - [ ] "Next Step" / "Aktiver Blocker" clear and specific?
   - [ ] "What is done" complete?
   - [ ] Infrastructure reference still accurate (IPs, tokens, ports)?
   - [ ] Stand timestamp and run number current?

3. **Memory**
   - [ ] New user preferences saved?
   - [ ] New project facts saved?
   - [ ] Stale entries updated or removed?

4. **Task list**
   - [ ] All completed tasks marked `completed`?
   - [ ] Open tasks clearly described for the next session?

After the checklist: confirm to the user what was updated.
Short, no explanations: "KNOWN_ISSUES ✅ (KI-008 updated), HANDOVER ✅, Memory ✅ (1 new entry), Tasks ✅"

---

### FILE CREATION — Templates

If a documentation file does not exist, create it immediately from the
template. Never ask whether to create — just create and fill what is known.

See `references/templates.md` for the full templates for:
- `KNOWN_ISSUES.md`
- `HANDOVER.md`
- Memory files (`feedback_*.md`, `project_*.md`, etc.)

The templates define the structure. Claude fills in the content from
conversation context. Unknown values are marked `<!-- TODO: fill in -->`.

---

### Priority when time or context is short

If only one location can be updated: **KNOWN_ISSUES first** — it holds
findings that cannot be derived later. HANDOVER and Memory can be
reconstructed from KNOWN_ISSUES; specific findings cannot.

---

## Procedure in Claude AI (Web)

No file access in the web. Adapted behavior:

1. **Read mode:** Ask the user to paste the content of KNOWN_ISSUES.md,
   HANDOVER.md, or MEMORY.md directly into the chat. Work from that.

2. **Write mode:** Output the updated file content as a code block the user
   can copy and paste back into their file. Label clearly:
   `Updated KNOWN_ISSUES.md — replace from line N to line M`.

3. **Task list:** Use a markdown checklist in the response as a substitute
   for TaskCreate/TaskUpdate. Tell the user which tasks to add manually.

4. **Session close:** Run the same checklist, output all updated file
   content as labeled code blocks in one response.

---

## Additional references

- `references/templates.md` — full file templates for KNOWN_ISSUES.md,
  HANDOVER.md, and memory files. Read when creating a file from scratch.
