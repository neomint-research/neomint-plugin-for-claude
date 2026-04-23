# Environment Detection — NeoMINT Plugin Standard

All skills in the NeoMINT plugin must detect the current environment at the start
and adapt their behavior accordingly. Three environments are relevant:

---

## Claude Code

**Signals:** `Bash` tool available, full access to the local file system.

**Behavior:** Normal operation. Ask for a path if not provided, read and write files
directly.

---

## Cowork

**Signals:** `Bash` tool available, system context contains "Cowork mode".
File access via the user's selected folder (mounted at a session-specific path).

**Behavior:**
- If the user has not yet selected a folder: call `mcp__cowork__request_cowork_directory`
  so they can choose one.
- Then proceed as in Claude Code.
- Write outputs (new files, results) to the selected folder so the user can access them.

---

## Claude AI (Web)

**Signals:** No `Bash` tool, no direct access to the user's local file system.

**Behavior:** Each skill must define its own web fallback. The general principle:

1. **Input via upload** — Ask the user to upload the relevant files into the chat.
2. **Processing in context** — Read the files and perform the requested transformation
   or analysis.
3. **Output as download or script** — Deliver results either as a downloadable file
   or as a shell script the user can run locally.

The specific web fallback is defined in each skill's own "Procedure in Claude AI (Web)"
section.

---

## Decision tree

```
Bash tool available?
├── No  → Claude AI Web → execute the skill's web fallback
└── Yes →
    System context contains "Cowork"?
    ├── Yes → Cowork → check folder, call request_cowork_directory if needed, then proceed
    └── No  → Claude Code → proceed normally
```
