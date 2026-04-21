---
name: skill-name
description: >
  Brief description of what the skill does and when it should trigger.
  Trigger signals: ...
  Do not use for: ...
---

# Skill Name — Short Title

Short description of the skill's goal.

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
