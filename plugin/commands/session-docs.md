---
description: Read all project docs at session start, or write updates after new findings — keeps KNOWN_ISSUES.md, HANDOVER.md, memory files, and the task list in sync.
argument-hint: "[start | update | handover, optional]"
---

# /session-docs

The user has invoked the session-docs skill. Run it exactly as specified in
the `session-docs` skill — the skill carries the full contract (READ mode at
session start, WRITE mode after findings, HANDOVER mode for session close,
and all auto-trigger rules).

## What to do now

1. Load the skill: read `skills/session-docs/SKILL.md` — this is the contract.
   Every rule about which files to read, in what order, what to write after
   each finding, and the template rules for missing files lives there.
   Do not paraphrase from memory; read it.
2. Apply the shared conventions: `skills/_shared/language.md` for
   output-language rules, `skills/_shared/environments.md` for Claude
   Code / Cowork / Web differences.
3. Determine the mode from the argument or conversation context:
   - **No argument / `start`** → READ mode: read all project docs, summarise
     active blocker, last-session work, and next concrete step.
   - **`update`** → WRITE mode: persist a new finding to the appropriate file.
   - **`handover`** → HANDOVER mode: bring all docs to current state and
     produce a handover summary ready to paste into the next session.
4. From here, follow the skill verbatim.
