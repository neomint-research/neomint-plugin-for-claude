---
name: skill-name
description: >
  Brief description of what the skill does and when it should trigger.
  Trigger signals: ...
  Do not use for: ...
# Uncomment the next line if this is an explicit-invocation skill
# (see "Invocation model" below). Leave commented for auto-trigger.
# disable-model-invocation: true
---

# Skill Name — Short Title

Short description of the skill's goal.

---

## Invocation model — decide this first

Before writing anything else in this SKILL.md, decide which of the **three
legal patterns** this skill follows. The decision drives everything
downstream (frontmatter flag, file layout, pairing obligations).

**Pattern 1 — Auto-only** (default for lightweight, scoped tasks)
No `disable-model-invocation` flag. No paired command file. The model
decides when to fire based on the description's trigger signals. Correct
when the skill is safe to run whenever the signals appear and there is no
meaningful argument a user would pass explicitly.

**Pattern 2 — Command-only** (for heavy, multi-turn, opt-in workflows)
`disable-model-invocation: true` in frontmatter. Paired `commands/<name>.md`
file that carries the full contract inline so `/name` runs without reading
references. Correct when auto-firing would race the user's intent — long
deliberations (`/council`), governance pipelines (`/update-plugin`), or
anything the user should explicitly opt into.

**Pattern 3 — Auto + Command** (added in 0.6.0)
No `disable-model-invocation` flag. Paired `commands/<name>.md` file.
The skill auto-fires on clear intent signals AND the user can invoke it
explicitly with arguments. Correct when both paths are legitimate — e.g.
`rename-pdf`: the model can trigger it on "clean up my scans", and the user
can also call `/rename-pdf ~/inbox` with a folder argument to skip the
inventory step. The auto-path covers the discovery case; the command-path
covers the direct case.

Decision rule in one sentence: **"Does this skill need a user-facing
command entry?"** If yes → either Pattern 2 (heavy, so auto-firing would be
wrong) or Pattern 3 (both paths are fine). If no → Pattern 1.

Layer 1 (`scripts/plugin-check.py`) enforces:
- Every `commands/<name>.md` needs a paired `skills/<name>/SKILL.md` (Pattern
  2 or 3).
- Every non-auto skill (Pattern 2) needs its paired command, otherwise the
  skill is unreachable in Claude Code / Cowork.

This decision was introduced in 0.5.1 after `council` had to be refactored
from auto-trigger to explicit-invocation post-hoc. The third pattern was
added in 0.6.0 when `rename-pdf` needed both an auto-trigger surface (so
users can say "rename my scans" in plain language) and a command surface
(so power users can pass a folder path as argument).

---

## Language

Read `../_shared/language.md` and apply the output language rules defined there.

## Environment detection

Read `../_shared/environments.md` and handle accordingly for Claude Code, Cowork,
and Claude AI (Web).

Then define the **web fallback** for this skill (see below).

---

## Procedure with file access (Claude Code & Cowork)

<!-- Describe the main skill logic here -->

### 1. ...
### 2. ...
### 3. ...

---

## Procedure in Claude AI (Web)

<!-- Define the web fallback: what does this skill do when no file access is available?
     Options: request upload → process → offer download/script
              Or: solve the task entirely in chat (e.g. pure analysis)
              Or: clearly communicate what is not possible without file access -->

---

## Additional references

<!--
  Use this section when you split content into the skill's references/ subfolder.

  When to split: if SKILL.md approaches or exceeds ~400 lines, or if the skill
  has multiple independent sub-domains (e.g. different roles, different phases,
  different file formats), extract the detail into references/<topic>.md files
  and leave only the overview in SKILL.md. This is Anthropic's recommended
  Progressive Disclosure pattern — metadata is always loaded, SKILL.md body is
  loaded on trigger, references/ are loaded on demand.

  Link from SKILL.md with a short hint about when to read each file, e.g.:

    - `references/roles.md` — role definitions, methods, failure modes.
    - `references/phases.md` — phase mechanics and hand-off formats.
-->
