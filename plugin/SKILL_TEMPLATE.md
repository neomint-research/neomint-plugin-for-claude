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

Before writing anything else in this SKILL.md, decide whether the skill is
**auto-triggering** or **explicit-invocation**. The decision drives everything
downstream (frontmatter flag, file layout, pairing obligations).

Decision rule: **"Would firing this without asking surprise the user?"**
- If **no** (the skill is lightweight, scoped, and safe to fire whenever its
  triggers appear) → auto-triggering is the default. Do nothing special.
- If **yes** (the skill runs a long deliberation, spends many turns, writes
  files, or produces output the user should opt into) → explicit-invocation
  is mandatory. Follow the pairing contract below.

For explicit-invocation skills, the pairing is **bidirectional and mandatory**:

- Create `../../commands/<skill-name>.md` at the plugin root. That file carries
  the full contract inline so a `/skill-name` run loads no reference files.
- Uncomment `disable-model-invocation: true` in this skill's frontmatter.
  Without the flag, Claude would auto-fire on trigger words and race the
  user's explicit `/skill-name` invocation.
- This SKILL.md becomes the **Claude AI (Web) fallback** — carry enough of
  the contract inline that a standard run works without reading references.

Layer 1 (`scripts/plugin-check.py`) enforces the pairing in both directions
and will fail the build if one half of it is missing.

Auto-triggering skills do NOT set `disable-model-invocation` and do NOT get a
paired command file. That is correct, not a deficiency.

This decision was introduced in 0.5.1 after `council` had to be refactored
from auto-trigger to explicit-invocation post-hoc — prevent that cost by
making the call up front.

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
