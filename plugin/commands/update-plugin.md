---
description: Update a Claude plugin — full governance pipeline (pre-research, skill-creator loop, quality checks, three-layer plugin loop, repackage). Use for adding a new skill, modifying an existing one, updating plugin standards, or repackaging.
argument-hint: "[what to change, e.g. 'add an invoice-extract skill' or 'tighten the council description']"
---

# /update-plugin

**Output language:** respond in the language the user wrote in. German
in → German out, English in → English out. If the user has set an
explicit language preference earlier in the conversation, respect that
instead. This rule applies from your first response, before any skill
file is read. (Full rule: `skills/_shared/language.md`.)

The user has invoked the plugin-update governance loop. Run it exactly
as specified in the `update-plugin` skill — the skill carries the full
contract (Step 0 pre-research → Step 5 three-layer plugin loop →
packaging).

## What to do now

1. Load the skill: read `skills/update-plugin/SKILL.md` — this is the
   contract. Every rule about pre-research sources, the mandatory
   skill-creator iteration loop, quality checks, the three Step-5
   layers, the build-artefact rule, the versioning agent rule, and the
   self-optimisation pass lives there. Do not paraphrase from memory;
   read it.
2. Apply the shared conventions: `skills/_shared/language.md` for
   output-language rules, `skills/_shared/environments.md` for Claude
   Code / Cowork / Web differences.
3. Locate the plugin root if it isn't already obvious from the
   conversation:

   ```bash
   find /sessions /mnt -name "plugin.json" -path "*/.claude-plugin/*" 2>/dev/null | head -5
   ```

4. Run Step 0 (pre-research) before touching any file. The research
   summary in 0d is the user-visible gate that opens Step 1.
5. From Step 1 onward, follow the skill verbatim.

## Guardrails the skill already enforces — reminders, not duplication

- **Step 0 is mandatory.** No edits, no scaffolding, no proposals
  before the research summary is on screen. The user is allowed to
  steer between sources but not to skip the step.
- **Step 2 means the real skill-creator skill.** When a skill's
  content changes, invoke the `skill-creator` skill via the `Skill`
  tool — not by reading its SKILL.md and paraphrasing. Run its full
  iteration loop (test cases → user approval → subagent runs → eval
  viewer → user review → improve → repeat). "The draft looks good
  enough" is not a valid reason to skip; the user's design being
  detailed is not a valid reason to skip. Only pure metadata changes
  (name field, version number) skip Step 2 entirely.
- **Step 5 closes by passing all three layers in one complete pass.**
  Layer 1 (`scripts/plugin-check.py`), Layer 2 (per-skill graders),
  Layer 3 (unprimed audit subagent). Any real failure restarts the
  loop. The plugin is packaged only after a clean pass.
- **Build-artefact rule.** Transient artefacts (intermediate zips,
  extracted source trees, grader JSON, cache folders) live under
  `/tmp`. The plugin root holds only source files and the canonical
  shipping `*.plugin` archive. A FAIL on Layer 1's "No stray files at
  plugin root" is a blocker — never silence it by adding to the
  whitelist.
- **Agent versioning rule.** An agent running this loop may only ever
  bump the **fix** level. Never propose a minor or major bump — that
  judgment belongs to the user. If the change subjectively warrants
  more than a fix, deliver the fix bump and ask the user whether to
  re-label it.
- **Self-optimisation in 5e is not optional.** After every clean pass,
  surface concrete proposals to improve the standard or this skill
  itself. Do not implement them without explicit user confirmation.
- **"Reicht" is not a verdict.** Stop only when sure, or name what
  would need to become true to be sure.

## Now

Begin with Step 0 (pre-research) following `skills/update-plugin/SKILL.md`.
