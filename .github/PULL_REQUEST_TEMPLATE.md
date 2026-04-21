<!-- Thanks for contributing. Please keep this template — blank PRs are harder to review. -->

## What this change does

<!-- One or two sentences. The observable effect, not the implementation. -->

## Why

<!-- What incident, gap, or request motivated this? If it's a skill content change, what failure mode does it close? -->

## Governance checklist

- [ ] **Pre-research (Step 0)** — checked Anthropic GitHub (`anthropics/skills`, `anthropics/claude-plugins-official`, `anthropics/claude-code`) and community sources; documented below.
- [ ] **skill-creator used** — for any content change to a `SKILL.md`, the official `skill-creator` skill was used (or this PR is metadata-only).
- [ ] **Three-layer loop passed** — `plugin-check.py` clean, all per-skill graders green, unprimed audit returned `SHIP`.
- [ ] **Version bumped** — `plugin.json`, `README.md` version reference, and `CHANGELOG.md` top entry all updated.
- [ ] **No internal data** — no NeoMINT GmbH internal names, addresses, or customer material in examples.

## Pre-research summary

<!--
Anthropic GitHub: [updates found / no relevant changes]
Community: [relevant recommendations / no new findings]
Consequence for this change: [what was adjusted / nothing]
-->

## Self-optimisation

<!-- Did this change surface a gap that should become a new Layer 1 or Layer 2 assertion? If yes, is it addressed here or in a follow-up? -->
