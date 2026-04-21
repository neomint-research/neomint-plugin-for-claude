# Contributing to the NeoMINT Toolkit

Thank you for wanting to contribute. This document describes how changes land in the toolkit. The process is deliberately opinionated — it's the same process we use internally, and the reason the plugin hasn't drifted.

## Ground rules

1. **The `neomint-plugin-entwicklung` skill governs every change.** New skill, skill modification, standard update, repackage — all of it runs through that skill. If you are using Claude Code or Cowork with this plugin installed, the skill is invoked automatically when you describe your change. If you are editing by hand, read `skills/neomint-plugin-entwicklung/SKILL.md` first and follow it manually.
2. **The `skill-creator` skill is mandatory for content changes.** Every creation or content change of a skill goes through Anthropic's official `skill-creator` skill. Direct edits to a `SKILL.md` file without the skill-creator workflow violate the plugin standard. The only exceptions are pure metadata changes (name, version number in `plugin.json`) or comment-only edits.
3. **Ground-Before-Discuss.** Before proposing a change, state what Anthropic's current guidance says (Anthropic GitHub — `anthropics/skills`, `anthropics/claude-plugins-official`, `anthropics/claude-code` — is the primary source) and what the community consensus is, with sources. Anthropic wins on conflict. "I just think this would be better" is not a valid opener.

## Development workflow

### 1. Pre-research

Before touching any file, check the current state of the Anthropic reference repositories for anything that affects your proposal. Search for your specific topic (description format, SKILL.md conventions, plugin.json fields, grader patterns). Document what you found — even "nothing relevant changed" counts.

### 2. Clarify the goal

Is this a new skill, a modification to an existing skill, a plugin-standard update, or a build-only repackage? The governance skill routes differently for each.

### 3. Run `skill-creator` for content changes

If the change is to a `SKILL.md`, invoke `skill-creator`. It guides you through interview, draft, testing, and iteration. It will catch things you did not think to check.

### 4. Three-layer iteration loop

The loop is how we know the plugin is actually consistent, not just consistent-according-to-the-person-who-made-the-change.

**Layer 1 — structural assertions.** Run `python3 skills/neomint-plugin-entwicklung/scripts/plugin-check.py` from the plugin root. It verifies plugin.json integrity, version consistency across plugin.json / README / CHANGELOG, SKILL.md block completeness (Language block, Environment block, Web fallback, description with triggers and negative scope), shared-file presence, reference coverage, root-file whitelist, and shipping-archive cleanliness.

**Layer 2 — per-skill graders.** Each skill may ship a `scripts/grade.py` that encodes its own contract (e.g. the council grader enforces all five phases, the Ground-Before-Discuss wording, the two-track output format, and the anti-pattern list). If you change a skill, its grader must pass. If you add a new capability, add a grader assertion for it in the same change.

**Layer 3 — unprimed audit.** Before packaging, a subagent with no context from the change reads the delta and returns `SHIP` or `HOLD` with named defects. If `HOLD`: fix the defects or, if the auditor identified a category of defect the assertion set doesn't catch, promote that category into a new Layer 1 or Layer 2 assertion so the next change can't regress.

The loop closes only when all three layers pass in one complete pass. If Layer 3 flags something new, Layer 1 or Layer 2 grows by one assertion — this is how the standard improves.

### 5. Version bump and CHANGELOG

Format: `major.minor.fix`.
`fix` increments automatically for every change, even small ones.
`minor` and `major` only on explicit maintainer instruction.

Every change must:
- bump the appropriate version field in `.claude-plugin/plugin.json`,
- add a top entry to `CHANGELOG.md` (newest on top, succinct, names the observable effect),
- update the version reference in `README.md`.

### 6. Repackage

After all layers pass, build the shipping archive from a clean copy of the plugin tree. **Do not zip from the plugin root while there is a pre-existing `*.plugin` file present** — `zip -r` appends to existing archives, so always remove the target first, and always zip from a clean copy so no sibling directories leak in.

From the plugin root:

```bash
rm -f neomint-toolkit.plugin
zip -r neomint-toolkit.plugin . \
  -x "*.git*" \
  -x "*.github/*" \
  -x "CONTRIBUTING.md" \
  -x "*.DS_Store" \
  -x "*/.mcpb-cache/*" \
  -x "*/evals/*" \
  -x "*.plugin"
```

`LICENSE` and `SECURITY.md` are intentionally **included** in the shipping archive: installed users should see the license terms and the security-reporting policy without having to visit the GitHub repository. `CONTRIBUTING.md` and `.github/` are intentionally **excluded** — they are only relevant to people working on the repository itself. This split is enforced by the `never_shipped` set in `skills/neomint-plugin-entwicklung/scripts/plugin-check.py`; if you change the zip exclusion list, update that set too.

After packaging, run Layer 1 again. The `Shipping archive contents are clean` assertion verifies nothing snuck in.

### 7. Self-optimisation

After every change, answer:
- Did the change reveal a gap in the standard — something that was unclear or repeatedly discussed?
- Did something need to be decided manually that should actually be a rule?
- Did Layer 3 surface a category of defect that should become a Layer 1 or Layer 2 assertion?

If yes, propose the improvement in the same PR or a follow-up PR. Standards only stay alive if they grow.

## What kinds of contributions are welcome

- **New skills** that solve a recurring workflow and don't duplicate an existing one. Start by opening an issue describing the workflow, the trigger signals, and the negative scope (what the skill is *not* for). Issue first, then PR — it's faster than writing a skill we decline to merge.
- **Modifications to existing skills** that sharpen triggers, close a failure mode, add a web fallback, or improve grader coverage.
- **Plugin-standard updates** that come from a specific incident (ideally citable in the PR: "this prevents X, which happened in version Y").
- **Pointed criticism and audit findings.** Open an issue. "The council grader has this blind spot" or "the Ground-Before-Discuss rule is underspecified for case X" are exactly the kind of feedback we want.

## What we will probably decline

- Skills that are broad grab-bags rather than one-job-done-well.
- Pure stylistic README rewrites without a specific reading problem identified.
- Changes that bypass `skill-creator` for content or bypass the three-layer loop for governance. We will ask you to re-do them.

## Reporting issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`. For security issues, see [`SECURITY.md`](SECURITY.md) — please do not open public issues for vulnerabilities.

## License of contributions

By submitting a contribution — whether as a pull request, a patch attached to an issue, or code posted in a discussion — you agree that it is licensed under the [Apache License 2.0](LICENSE), consistent with the rest of the project. This matches the inbound-equals-outbound model used by most Apache-licensed projects on GitHub. If you cannot license your contribution under Apache 2.0 (for example, because your employer hasn't cleared it), please don't submit the contribution.
