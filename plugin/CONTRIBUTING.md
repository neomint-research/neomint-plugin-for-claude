# Contributing to the NeoMINT Toolkit

Thank you for wanting to contribute. This document describes how changes land in the toolkit. The process is deliberately opinionated — it's the same process we use internally, and the reason the plugin hasn't drifted.

## Ground rules

1. **The `update-plugin` skill governs every change.** New skill, skill modification, standard update, repackage — all of it runs through that skill. If you are using Claude Code or Cowork with this plugin installed, invoke it explicitly with `/update-plugin [what you want to change]`. In Claude AI (Web), where slash commands are unavailable, the skill's pushy description triggers the same contract when you describe your change.
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

**Layer 1 — structural assertions.** Run `python3 skills/update-plugin/scripts/plugin-check.py` from the plugin root. It verifies plugin.json integrity, version consistency across plugin.json / README / CHANGELOG, SKILL.md block completeness (Language block, Environment block, Web fallback, description with triggers and negative scope), shared-file presence, reference coverage, root-file whitelist, runtime-artefact sweep (nothing of the form `*.plugin`, `*-workspace/`, `iteration-workspace/`, etc. in the tree), and the commands↔skills pairing in all three legal patterns.

**Layer 2 — per-skill graders.** Each skill may ship a `scripts/grade.py` that encodes its own contract (e.g. the council grader enforces all five phases, the Ground-Before-Discuss wording, the two-track output format, and the anti-pattern list). If you change a skill, its grader must pass. If you add a new capability, add a grader assertion for it in the same change.

**Layer 3 — unprimed audit.** Before packaging, a subagent with no context from the change reads the delta and returns a findings list with severity labels. If there are BLOCKER or MAJOR findings: fix the defects or, if the auditor identified a category of defect the assertion set doesn't catch, promote that category into a new Layer 1 or Layer 2 assertion so the next change can't regress.

The loop closes only when all three layers pass in one complete pass. If Layer 3 flags something new, Layer 1 or Layer 2 grows by one assertion — this is how the standard improves.

### 5. Version bump and CHANGELOG

Format: `major.minor.fix`.
`fix` increments automatically for every change, even small ones.
`minor` and `major` only on explicit maintainer instruction.

Every change must:
- bump the appropriate version field in `.claude-plugin/plugin.json`,
- add a top entry to `CHANGELOG.md` (newest on top, succinct, names the observable effect),
- update the version reference in `README.md`.

### 6. Workspace and artefacts

All runtime output from the iteration loop — intermediate zips, extracted source trees, grader JSON reports, snapshots, eval-viewer HTML, the shipping archive itself — lives in `/tmp/<plugin-name>-workspace/` and never in the source tree. Layer 1's runtime-artefact sweep blocks any file matching `*.plugin`, `*-workspace/`, `iteration-workspace/`, `skill-snapshot/`, `eval-viewer-iter*.html`, `COUNCIL.md`, or `plugin-check-report.json` anywhere inside the repo.

The shipping `.plugin` archive is **not** committed. It is rebuilt by CI when a tag is pushed (see the next step) and attached to the corresponding GitHub Release as an asset.

If you want to build a local copy for testing, use the workspace directory:

```bash
mkdir -p /tmp/neomint-toolkit-workspace/src
cp -r plugin/* /tmp/neomint-toolkit-workspace/src/
cd /tmp/neomint-toolkit-workspace/src
zip -r /tmp/neomint-toolkit-workspace/neomint-toolkit.plugin . \
  -x "*.git*" \
  -x "*.github/*" \
  -x "CONTRIBUTING.md" \
  -x "*.DS_Store" \
  -x "*/.mcpb-cache/*" \
  -x "*/evals/*" \
  -x "*.plugin"
```

`LICENSE` and `SECURITY.md` are intentionally **included** in the shipping archive: installed users should see the license terms and the security-reporting policy without having to visit the GitHub repository. `CONTRIBUTING.md` and `.github/` are intentionally **excluded** — they are only relevant to people working on the repository itself. This split is enforced by the `never_shipped` set in `skills/update-plugin/scripts/plugin-check.py`; if the exclusion list changes, that set must change too. The CI release workflow applies the same rules in Python rather than `zip -x`, but the semantics are identical.

### 7. Cut the release

Push a `vX.Y.Z` git tag that matches `plugin/.claude-plugin/plugin.json`:

```bash
git tag v0.6.0
git push origin v0.6.0
```

The tag push triggers [`.github/workflows/release.yml`](../.github/workflows/release.yml), which:

1. Asserts that the tag version matches `plugin.json` and the top entry in `CHANGELOG.md`.
2. Re-runs `plugin-check.py` (Layer 1 + Layer 2) against `plugin/`.
3. Rebuilds the `.plugin` archive deterministically with the exclusion rules encoded in the workflow.
4. Extracts the matching `## X.Y.Z — YYYY-MM-DD` block from `CHANGELOG.md` as release notes.
5. Publishes a GitHub Release with the rebuilt `neomint-toolkit.plugin` attached as an asset.

Older versions are reachable via their GitHub Release assets — don't keep versioned `.plugin` files in the working tree. `.gitignore` blocks `*.plugin` precisely to prevent that accumulation.

If a tag was pushed without a corresponding plugin.json or CHANGELOG update, the workflow fails loudly. Fix the mismatch locally and force-push the tag (`git tag -f vX.Y.Z && git push origin vX.Y.Z --force`) — the release itself is idempotent.

### 8. Self-optimisation

After every change, answer:
- Did the change reveal a gap in the standard — something that was unclear or repeatedly discussed?
- Did something need to be decided manually that should actually be a rule?
- Did Layer 3 surface a category of defect that should become a Layer 1 or Layer 2 assertion?

If yes, propose the improvement in the same PR or a follow-up PR. Standards only stay alive if they grow.

## What kinds of contributions are welcome

- **New skills** that solve a recurring workflow and don't duplicate an existing one. Start by opening an issue describing the workflow, the trigger signals, and the negative scope (what the skill is *not* for). Issue first, then PR — it's faster than writing a skill we decline to merge.
- **Modifications to existing skills** that sharpen triggers, close a failure mode, add a web fallback, or improve grader coverage.
- **Layer 1 / Layer 2 assertions** promoted from real Layer 3 findings — name the incident the new assertion would have caught.
- **Standard updates** — use the `[standard]` issue template; quote the rule today, describe the problem, propose the replacement, say how it will be enforced.

## What is out of scope

- Changes that skip the three-layer loop.
- Skill rewrites driven by taste rather than a named failure mode.
- Ad-hoc edits to `SKILL.md` files without running `skill-creator`.
- Committing build artefacts (`*.plugin`, workspaces, eval reports) into the source tree.
