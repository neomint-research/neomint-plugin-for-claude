# COUNCIL — Persistence (`COUNCIL.md`)

Persistence is what makes the Council a system instead of a one-shot
opinion. The second run is structurally cheaper than the first because
`COUNCIL.md` carries forward the repo map, prior verdicts, and open
follow-ups.

---

## Where the file lives

| Environment   | Location                                           |
|---------------|----------------------------------------------------|
| Claude Code   | Repo root (next to README or top-level code).       |
| Cowork        | User-selected folder root (same pattern).           |
| Claude AI Web | Downloadable markdown artifact; user re-uploads.    |

In Cowork: if the user hasn't selected a folder yet, call
`mcp__cowork__request_cowork_directory` before writing. Never write to a
path the user didn't choose.

---

## File schema

```markdown
# COUNCIL — <Project or Repo Name>

## Context
- Repo type / structure summary: <...>
- Primary stack / language: <...>
- Persistent constraints: <...>

## Known dependency patterns
<recurring dependency clusters the Cartographer discovered across runs>

## Sessions

### <ISO date> — <mode> — <one-line question>

**Mode:** FULL | QUICK | AUDIT
**Context:** CODE | DOC | CHAT

#### Role findings (summary)
- Analyst: <one line>
- Cartographer: <one line>
- Adversary: <one line>
- Scout: <one line>
- Operator: <one line>

#### Verdict
OPERATIVE: <one-line technical recommendation>
MANAGEMENT: <one-line plain-language recommendation>

#### Open follow-ups
- [ ] <follow-up 1 — owner or condition>
- [ ] <follow-up 2>

#### Iteration trail
- <optional: REBUTTAL / DEEPEN / BRANCH events with dates>
```

---

## Update rules

**Read first, then write.** When `COUNCIL.md` exists, read it during
T1 ORIENT — before T3 CARTOGRAPHER runs, so the "Known dependency
patterns" block can skip already-mapped surface, and before T8 VERDICT,
so the Chairman can flag contradictions between the new judgment and
prior recorded verdicts.

**Append, don't overwrite.** New sessions are appended at the bottom of
the Sessions block. The file is a trail, not a snapshot. If a later
verdict contradicts an earlier one, both stay — the newer one is
visible by date, the older one stays as historical record.

**Close follow-ups explicitly.** When a new session resolves an open
follow-up from a prior session, close it with a line in the prior
session's checkbox and a pointer to the new session that closed it.
Don't delete the original — traceability matters more than tidiness.

**Update "Known dependency patterns" sparingly.** This block is
aggregate, not session-level. Only update when a pattern has appeared
across multiple sessions and is load-bearing. A one-off dependency
stays in the session entry, not the aggregate.

---

## Cross-environment handling

### Claude Code (CODE-MODE)
- Read during T1 ORIENT, write during T8 VERDICT (the closing Chairman
  turn is where the new session entry gets appended).
- Edit in place (git-tracked; the user can version-control the Council
  trail like any other artifact).

### Cowork
- Same as Claude Code, targeting the user's selected folder.
- Write output files to `/mnt/outputs` or the selected folder so the
  user can download.

### Claude AI (Web)
- No direct filesystem.
- If the user pastes in a prior `COUNCIL.md` (or uploads one), use it as
  context during T1 ORIENT.
- At the end of T8 VERDICT, offer the updated `COUNCIL.md` as a
  downloadable markdown artifact. Make it clear: "Save this and paste
  it back next time — the Council picks up where it left off."

---

## Why COUNCIL.md is not optional

A Council without persistence is a chat-bot with a schema. The
persistence payoff is the second-run economics: Cartographer doesn't
re-scan the same 200 files, Adversary doesn't re-derive the same
failure vectors, Chairman checks new verdicts against old ones for
drift. Skipping the file because "the user didn't ask" forfeits the
payoff and violates the core principle of shrinking-not-simplifying —
it silently simplifies by throwing away state.
