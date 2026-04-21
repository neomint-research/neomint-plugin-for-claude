---
name: neomint-plugin-entwicklung
description: >
  Governance skill for developing and maintaining the NeoMINT plugin. Always use when
  the NeoMINT plugin is being changed: adding a new skill, modifying an existing skill,
  updating plugin standards, or repackaging the plugin. Also triggers for: "create new
  skill", "improve skill", "update plugin", "change NeoMINT plugin", or when the user
  describes a new capability for the plugin. Ensures all changes follow plugin standards,
  the official skill-creator skill is used, and the plugin is repackaged after every
  change. Proposes improvements to plugin standards or itself after every change.
---

# NeoMINT Plugin Development

This skill accompanies every change to the NeoMINT plugin — from idea to finished
`.plugin` file. It ensures consistency and quality, and optimises itself after every change.

---

## Language

Read `../_shared/language.md` and apply the output language rules defined there.

## Environment detection

Read `../_shared/environments.md` and handle accordingly.
Web fallback: Since plugin development requires file access, explain to the user in
Claude AI (Web) that a folder is needed for this workflow and guide them to use Cowork
or Claude Code instead. You can still help conceptually in the web (design structure,
draft SKILL.md content) without creating actual files.

---

## Step 0 — Pre-research (mandatory before every change)

Before making any change to the plugin, an online research check for the current gold
standard is required. Goal: ensure the plugin is aligned with Anthropic's latest
recommendations and established community practice.

### 0a — Anthropic GitHub (primary source)

Check the official Anthropic repositories for the current state of skills, plugins, and
the skill-creator workflow:

- `https://github.com/anthropics/skills`
- `https://github.com/anthropics/claude-plugins-official`
- `https://github.com/anthropics/claude-code`

Search for relevant terms: "skill", "plugin", "SKILL.md", "skill-creator".
Use WebFetch or WebSearch. Briefly document what was found and whether there are updates
that affect this plugin.

### 0b — Community research (secondary source)

Supplementary web search for community recommendations and best practices:

- Search terms: "Claude Code skills best practices", "claude plugin development", "SKILL.md conventions"
- Sources: Reddit (r/ClaudeAI), GitHub Discussions, relevant blogs

### 0c — Conflict resolution

When Anthropic's guidelines and community recommendations conflict:

> **Anthropic's official guidelines always take precedence.**

Briefly document the conflict and justify why Anthropic's guideline was chosen.

### 0d — Research summary

Present a brief summary to the user:

```
Research result:
- Anthropic GitHub: [updates found / no relevant changes]
- Community: [relevant recommendations / no new findings]
- Consequence for this change: [what should be adjusted / nothing]
```

Only proceed to Step 1 after this summary.

---

## Step 1 — Clarify the goal

Before starting, determine exactly what needs to change:

- **New skill**: What should it do? When trigger? Which web fallback?
- **Modify existing skill**: What isn't working? What should improve?
- **Update plugin standard**: Which rule is missing or outdated?
- **Repackage only**: All changes already made, just generate the plugin file.

Ask if unclear.

---

## Step 2 — Skill-creator requirement (full loop, not just the draft)

For every creation or content change of a skill, without exception:

> **Use the official skill-creator skill, and run its full iteration loop to close.**

Tell the user explicitly: "I'm now starting the skill-creator skill for this step."
Then invoke the skill-creator. The correct invocation is the `Skill` tool with
`skill: "skill-creator"` — not running it via Bash, and not reading `SKILL.md`
manually and paraphrasing. The Skill tool is what loads the full workflow (interview,
draft, testing, iteration) and puts it in context.

### 2a — Write the first draft

Follow the skill-creator's guidance: capture intent, interview where needed, produce
a SKILL.md draft (plus `references/` files where the content exceeds ~400 lines or
has multiple independent sub-domains).

### 2b — Run the iteration loop in full (mandatory, no exceptions)

After the draft, the skill-creator loop is **not optional and not truncatable**,
even if the draft looks clean:

1. **Test cases** — propose 2-4 realistic prompts that cover the skill's main modes
   plus at least one input-edge-case. Get the user's approval of the test set before
   running.
2. **Run** — with the skill AND a baseline (no-skill for new skills, previous
   version for modifications). In Cowork/Claude Code use subagents in parallel;
   in Claude AI (Web) run inline, sequentially.
3. **Structural assertions** — for skills with verifiable structure (required
   sections, required role attributions, required output format), add programmatic
   assertions alongside the qualitative review. This catches silent regressions
   the eye misses.
4. **Generate the eval viewer** — `eval-viewer/generate_review.py --static <path>`
   in Cowork; standard server in Claude Code. Present the output link to the user.
5. **User review** — wait for explicit user feedback. Don't assume "silence means OK".
6. **Improve** — revise SKILL.md (and references) based on the feedback.
7. **Repeat** from step 1 until the user confirms satisfied, feedback is empty, or
   meaningful progress stalls.

> **Hard block:** Step 3 (quality checks) may not begin until the loop in 2b has
> closed. "The draft looks good enough" is not a valid reason to skip. The user's
> design being detailed is not a valid reason to skip. No exceptions — the point
> of the loop is to validate against real prompts, which the author alone cannot do.

If the user tries to skip this step or requests direct changes to a SKILL.md: politely
but clearly point out that this violates plugin standards, and only proceed after explicit
user approval.

Only exception to the Step 2 skill-creator requirement itself: pure metadata changes
(name, version number in `plugin.json`) or adding comments with no functional effect.
The iteration loop exception does not have a carve-out — if Step 2 triggers, 2b runs in full.

---

## Step 3 — Quality checks before finalising

Before the plugin is packaged, check every changed or new skill:

### Required checks

- [ ] **Pre-research completed** — Was Step 0 fully executed and documented?
- [ ] **SKILL_TEMPLATE compliance** — Does the structure match the template in `SKILL_TEMPLATE.md`?
- [ ] **Language block present** — Does the skill reference `../_shared/language.md`?
- [ ] **Environment block present** — Does the skill reference `../_shared/environments.md`?
- [ ] **Web fallback defined** — Is there a dedicated "Procedure in Claude AI (Web)" section?
- [ ] **Description complete** — Does the YAML frontmatter contain `name` and `description` with trigger signals and negative scope?
- [ ] **No internal content** — No NeoMINT GmbH-internal names, addresses, or confidential data in examples?
- [ ] **Character rules and conventions** — Do all examples and filenames follow the defined rules?

If deficiencies are found: correct before continuing.

---

## Step 4 — Repackage the plugin

> **Build-artefact rule.** Every transient artefact produced during packaging,
> grading, or evaluation — intermediate zips, extracted source trees, grader
> report JSON, cache folders — is written under `/tmp`. The plugin root holds
> only source files and the canonical shipping `*.plugin` archive. The Layer 1
> root-whitelist check enforces this; treat any FAIL on "No stray files at
> plugin root" as a blocker. Never add a new whitelist entry to silence it
> unless the file genuinely belongs to the plugin source.

After every change, repackage the plugin. First locate the plugin root folder
(it contains `.claude-plugin/plugin.json`) — either from conversation context or via:

```bash
find /sessions /mnt -name "plugin.json" -path "*/.claude-plugin/*" 2>/dev/null | head -5
```

**Build in `/tmp`, then copy into the workspace folder.** Writing the zip
directly into a mounted workspace folder can fail to atomically replace an
existing archive (the kernel rejects the in-place rename across the mount).
Building in `/tmp` and then copying is both robust and clean.

> **Zip from a clean copy, not from `/tmp` itself.** The recipe below
> `cp -r`s the plugin root into `/tmp/neomint-toolkit-src/` and then
> `cd`s into *that* folder before zipping. Never run `cd /tmp && zip -r
> ….plugin .` — zip would then include every sibling folder in `/tmp`
> (snapshot dirs, other builds, grader workspaces) inside the archive,
> and the user would receive an archive with mystery top-level folders.
> This is not hypothetical: it happened in 0.4.4 and was caught manually
> in verification. The 0.4.5 Layer 1 assertion *Shipping archive
> contents are clean* catches it automatically on the next pass — but
> getting it right the first time is still the discipline. Also: before
> building, delete any pre-existing `/tmp/neomint-toolkit.plugin`;
> `zip -r` appends to an existing archive rather than replacing it.

```bash
# Build outside the mount
rm -rf /tmp/neomint-toolkit-src && \
cp -r /path/to/plugin-root /tmp/neomint-toolkit-src && \
rm -rf /tmp/neomint-toolkit-src/.mcpb-cache /tmp/neomint-toolkit-src/*.plugin && \
cd /tmp/neomint-toolkit-src && \
zip -r /tmp/neomint-toolkit.plugin . \
  -x "*.DS_Store" \
  -x "*/evals/*" \
  -x "*.plugin"

# Verify
unzip -l /tmp/neomint-toolkit.plugin | head -30
python3 -c "
import zipfile, json
z = zipfile.ZipFile('/tmp/neomint-toolkit.plugin')
json.loads(z.read('.claude-plugin/plugin.json'))
print('plugin.json: valid JSON inside archive')
"

# Copy into the user's workspace folder
cp /tmp/neomint-toolkit.plugin /path/to/workspace-folder/neomint-toolkit.plugin
```

Place the finished `.plugin` file in the workspace folder and offer it to the user
for download via a `computer://` link.

---

## Step 5 — Plugin-level iteration loop (three layers)

This step runs after every change **before** packaging. It is the plugin-level
analogue of the skill-creator's test-and-improve loop: the plugin change is
only considered finished when three independent layers all close in one
complete pass.

Mechanics and rationale are in `references/plugin-eval.md`. The summary
below is load-bearing and must be executed in full.

### 5a — Layer 1: Structural check (runnable)

Run the bundled grading script:

```bash
python3 skills/neomint-plugin-entwicklung/scripts/plugin-check.py <plugin-root>
```

The script asserts: plugin.json validity and completeness, version format,
CHANGELOG↔plugin.json version consistency, README completeness (no
mid-sentence truncation), README↔skills coverage (no missing or ghost
skills), `_shared` files present, SKILL_TEMPLATE present, each SKILL.md
has valid YAML frontmatter with name+description and references both
`_shared/language.md` and `_shared/environments.md`, no mid-sentence
truncation in any SKILL.md, every `references/X.md` reference resolves,
no stray files at the plugin root (whitelist).

Exit 0 means Layer 1 passes. Exit 1 means at least one assertion failed —
fix it and re-run.

### 5b — Layer 2: Per-skill evals

Layer 2 asks: did every skill's own eval loop close? The grading script
looks for `skills/<name>/scripts/grade.py` or
`skills/<name>/evals/grade.py` for each skill (excluding `_shared`). If
the script exists, it is executed; exit code 0 counts as PASS, anything
else as FAIL. If neither exists, the skill is recorded as SKIP
(informational — not a failure, but a gap to close when that skill is
next iterated).

### 5c — Layer 3: Independent audit subagent

Spawn a single subagent with a clean prompt, **unprimed**, to inspect
the plugin fresh:

```
I have a plugin at <plugin-root>. Inspect it without preconditioning and
report, under 400 words:

(a) Standards compliance gaps (SKILL.md structure, frontmatter, language
    and environment blocks, internal references).
(b) Skill-quality concerns (unclear descriptions, missing triggers, weak
    negative scope, unclear web fallback).
(c) Documentation mismatches (README claims vs. actual state).
(d) Anything surprising or smelly.

Only report findings, not a plan. No recommendations beyond "this is a
gap".
```

Collect the findings. Cross-check against the Layer 1 report. For each
finding:

- Already caught by Layer 1 → confirmation; proceed.
- Missed by Layer 1 but real → fix it AND add a new Layer 1 assertion
  for it in `scripts/plugin-check.py`. Note the new assertion in 5e.
- False positive → document in 5e why not.

Layer 3 cannot be replaced by assertions — its role is to find the
unknown-unknowns that grow the assertion set over time.

### 5d — Loop to closure

```
loop:
    run Layer 1  (scripts/plugin-check.py)
    run Layer 2  (per-skill graders)
    run Layer 3  (audit subagent)
    if any layer has real failures:
        fix them
        restart the loop (all three layers)
    else:
        done
```

The loop closes only when a single complete pass has zero real failures
across all three layers. No shortcuts. The plugin is only packaged after
a fully positive pass.

### 5e — Self-optimisation (after every change)

Review the change and the findings from 5a/5b/5c. Answer:

1. Did the change reveal a gap in the standard — something that was
   unclear or repeatedly discussed?
2. Did something need to be decided manually that should actually be a
   rule?
3. Did Layer 3 surface a real finding that Layer 1 missed? If so, a new
   Layer 1 assertion is expected.
4. Did the pre-research (Step 0) surface findings that should be
   permanently embedded in the standard?
5. Is anything missing from this skill itself — steps, checks, rules,
   scripts, references?

If yes: formulate improvements and propose them to the user:

```
I suggest the following improvements to the plugin standard:

1. [Observation] → [concrete change to file X]
2. [Observation] → [concrete change to file Y]

Shall I implement these?
```

Only implement standard improvements with user confirmation.

---

## Versioning scheme

Format: `major.minor.fix`
- **major** — incremented only on explicit user instruction
- **minor** — incremented only on explicit user instruction
- **fix** — incremented automatically for every change (even small ones)

After every change: bump the fix version in `plugin.json`, add an entry to `CHANGELOG.md` (newest on top), and update the version reference in `README.md`.

## Plugin structure reference

```
neomint-toolkit/
├── .claude-plugin/
│   └── plugin.json          ← name, version, author
├── CHANGELOG.md             ← version history, newest entry on top
├── README.md                ← user documentation + plugin standards
├── SKILL_TEMPLATE.md        ← template for new skills
└── skills/
    ├── _shared/
    │   ├── environments.md  ← environment logic (single source of truth)
    │   └── language.md      ← output language rules (single source of truth)
    └── <skill-name>/
        └── SKILL.md
```

Any deviation from this structure is a deficiency and must be corrected.

## Additional references

- `references/plugin-eval.md` — detailed mechanics of the three-layer
  plugin iteration loop (Layer 1 structural, Layer 2 per-skill evals,
  Layer 3 independent audit subagent), how to add assertions, and why
  Layer 3 cannot be replaced by a script.
- `scripts/plugin-check.py` — runnable grading script for Layers 1+2.
  Exit code 0 = pass; JSON report written to `/tmp/plugin-check-report.json`.
