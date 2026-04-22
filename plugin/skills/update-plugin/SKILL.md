---
name: update-plugin
disable-model-invocation: true
user-invocable: true
description: >
  Governance skill for updating any Claude plugin — adding a new skill,
  modifying an existing skill, updating plugin standards, or repackaging
  the plugin. Trigger phrases: "create a new skill", "improve a skill",
  "update the plugin", "change the plugin", "repackage the plugin", or
  any description of a new plugin capability. Ensures changes follow the
  plugin's standards, the official skill-creator skill is used for every
  content change, and the plugin is repackaged after every change.
  Proposes improvements to the plugin standards or to itself after every
  change. Bound to `/update-plugin` in Claude Code and Cowork; falls
  back to description-triggering in Claude AI (Web). Do NOT use for:
  general coding or scripting tasks, work that does not modify a plugin's
  source, using a plugin's other skills to get work done (as opposed to
  editing them), or user questions about how a skill behaves at runtime —
  this skill is strictly for authoring and maintaining a plugin, not for
  operating it.
---

# Update Plugin

This skill accompanies every change to a Claude plugin — from idea to
finished `.plugin` file. It ensures consistency and quality, and proposes
improvements to itself after every change.

It is the default governance skill for the NeoMINT plugin and applies the
same discipline to any other plugin built to a comparable standard. When
the user works on a plugin that does not yet have a `_shared/` standard,
this skill still applies its own rigor (pre-research, skill-creator loop,
quality checks, three-layer plugin loop, repackaging) and offers to
introduce the missing scaffolding.

---

## Language

Read `../_shared/language.md` and apply the output language rules defined
there.

## Environment detection

Read `../_shared/environments.md` and handle accordingly. The web fallback
for this skill is described below under "Procedure in Claude AI (Web)".

---

## Workspace-and-artefact rule (binding, every step)

> **Every runtime artefact lives in `/tmp/<plugin-name>-workspace/`.
> Never in the plugin source tree. Never in the user's working folder
> outside the plugin repo either.**

This covers:

- skill-creator iteration workspaces (eval runs, subagent transcripts,
  snapshots of prior skill versions, eval-viewer HTML output, grading
  reports)
- plugin-check Layer 1 / Layer 2 JSON reports
- Layer 3 subagent findings
- intermediate zips, extracted source trees, build scratch
- any other file that is not part of the plugin's source-of-truth

Why this is a hard rule: plugins are installed read-only in Claude Code
and Cowork. A skill that writes into its own source tree at runtime
either (a) fails on installation because the tree is read-only, or
(b) pollutes the developer's checkout with artefacts that end up
committed by accident and shipped inside the next `.plugin` archive.
Both failure modes have happened in this plugin before. The `/tmp`
workspace is writable in every environment that can run the skill, and
is automatically cleaned between sessions.

The shipping `.plugin` archive itself is also a build artefact and
belongs in `/tmp/<plugin-name>.plugin`. Distribution is via GitHub
Releases (or equivalent) — never by committing the archive into the
plugin repo. Layer 1 enforces: no `*.plugin`, no `*-workspace/`, no
`skill-snapshot/` anywhere inside the plugin tree or the repo root.

When the skill needs to write a workspace file, use:

```
/tmp/<plugin-name>-workspace/
├── iteration-N/          ← skill-creator iteration N
│   ├── eval-M/           ← one prompt evaluated
│   │   ├── with_skill/   ← subagent run with the skill
│   │   ├── without_skill/← baseline run
│   │   └── grading.json  ← per-eval grading
│   ├── benchmark.json    ← aggregated results for iteration
│   └── eval-viewer.html  ← static review page
├── skill-snapshot/       ← frozen copy of the prior skill version
└── plugin-check/         ← Layer 1 / Layer 2 reports
```

`<plugin-name>` is the `name` field from `.claude-plugin/plugin.json` —
deterministic, single source of truth, never derived from the folder
name.

---

## Procedure with file access (Claude Code & Cowork)

This is the full plugin-update loop. Execute it in order, from Step 0 to
Step 5, for every change to the plugin. Each step carries its own
contract; Step 5's consistency loop is the gate that must close fully
before the plugin is packaged.

### Step 0 — Pre-research (mandatory before every change)

Before making any change to the plugin, an online research check for the
current gold standard is required. Goal: ensure the plugin is aligned
with Anthropic's latest recommendations and established community
practice.

#### 0a — Anthropic GitHub (primary source)

Check the official Anthropic repositories for the current state of
skills, plugins, and the skill-creator workflow:

- `https://github.com/anthropics/skills`
- `https://github.com/anthropics/claude-plugins-official`
- `https://github.com/anthropics/claude-code`

Search for relevant terms: "skill", "plugin", "SKILL.md", "skill-creator".
Use WebFetch or WebSearch. Briefly document what was found and whether
there are updates that affect this plugin.

#### 0b — Community research (secondary source)

Supplementary web search for community recommendations and best
practices:

- Search terms: "Claude Code skills best practices", "claude plugin
  development", "SKILL.md conventions"
- Sources: Reddit (r/ClaudeAI), GitHub Discussions, relevant blogs

#### 0c — Conflict resolution

When Anthropic's guidelines and community recommendations conflict:

> **Anthropic's official guidelines always take precedence.**

Briefly document the conflict and justify why Anthropic's guideline was
chosen.

#### 0d — Research summary

Present a brief summary to the user:

```
Research result:
- Anthropic GitHub: [updates found / no relevant changes]
- Community: [relevant recommendations / no new findings]
- Consequence for this change: [what should be adjusted / nothing]
```

Only proceed to Step 1 after this summary.

---

### Step 1 — Clarify the goal

Before starting, determine exactly what needs to change:

- **New skill**: What should it do? When should it trigger? What is the
  web fallback?
- **Modify existing skill**: What isn't working? What should improve?
- **Update plugin standard**: Which rule is missing or outdated?
- **Repackage only**: All changes already made — just generate the
  plugin file.

Ask if unclear.

---

### Step 2 — Skill-creator requirement (full loop, not just the draft)

For every creation or content change of a skill, without exception:

> **Use the official skill-creator skill, and run its full iteration
> loop to close.**

Tell the user explicitly: "I'm now starting the skill-creator skill for
this step." Then invoke the skill-creator. The correct invocation is the
`Skill` tool with `skill: "skill-creator"` — not running it via Bash, and
not reading `SKILL.md` manually and paraphrasing. The Skill tool is what
loads the full workflow (interview, draft, testing, iteration) and puts
it in context.

#### 2a — Write the first draft

Follow the skill-creator's guidance: capture intent, interview where
needed, produce a SKILL.md draft (plus `references/` files where the
content exceeds ~400 lines or has multiple independent sub-domains).

#### 2b — Run the iteration loop in full (mandatory, no exceptions)

After the draft, the skill-creator loop is **not optional and not
truncatable**, even if the draft looks clean:

1. **Test cases** — propose 2-4 realistic prompts that cover the skill's
   main modes plus at least one input edge case. Get the user's approval
   of the test set before running.
2. **Run** — with the skill AND a baseline (no-skill for new skills,
   previous version for modifications). In Cowork/Claude Code use
   subagents in parallel; in Claude AI (Web) run inline, sequentially.
3. **Structural assertions** — for skills with verifiable structure
   (required sections, required role attributions, required output
   format), add programmatic assertions alongside the qualitative
   review. This catches silent regressions the eye misses.
4. **Generate the eval viewer** — `eval-viewer/generate_review.py
   --static <path>` in Cowork; standard server in Claude Code. Present
   the output link to the user.
5. **User review** — wait for explicit user feedback. Don't assume
   "silence means OK".
6. **Improve** — revise SKILL.md (and references) based on the feedback.
7. **Repeat** from step 1 until the user confirms satisfied, feedback is
   empty, or meaningful progress stalls.

> **Hard block:** Step 3 (quality checks) may not begin until the loop
> in 2b has closed. "The draft looks good enough" is not a valid reason
> to skip. The user's design being detailed is not a valid reason to
> skip. No exceptions — the point of the loop is to validate against
> real prompts, which the author alone cannot do.

If the user tries to skip this step or requests direct changes to a
SKILL.md: politely but clearly point out that this violates plugin
standards, and only proceed after explicit user approval.

Only exception to the Step 2 skill-creator requirement itself: pure
metadata changes (name, version number in `plugin.json`) or adding
comments with no functional effect. The iteration loop exception does
not have a carve-out — if Step 2 triggers, 2b runs in full.

---

### Step 3 — Quality checks before finalising

Before the plugin is packaged, check every changed or new skill:

#### Required checks

- [ ] **Pre-research completed** — Was Step 0 fully executed and
      documented?
- [ ] **SKILL_TEMPLATE compliance** — Does the structure match the
      template in `SKILL_TEMPLATE.md`?
- [ ] **Language block present** — Does the skill reference
      `../_shared/language.md`?
- [ ] **Environment block present** — Does the skill reference
      `../_shared/environments.md`?
- [ ] **Web fallback defined** — Is there a dedicated "Procedure in
      Claude AI (Web)" section?
- [ ] **Description complete** — Does the YAML frontmatter contain
      `name` and `description` with trigger signals and negative scope?
- [ ] **No internal content** — No organisation-internal names,
      addresses, or confidential data in examples?
- [ ] **Character rules and conventions** — Do all examples and
      filenames follow the defined rules?

If deficiencies are found: correct before continuing.

---

### Step 4 — Repackage the plugin

The plugin source repo holds only source files. The shipping `.plugin`
archive is **never** committed into the repo or copied into the user's
workspace folder. It is built in `/tmp` and uploaded to a release host
(GitHub Releases for this plugin) by the user.

This was changed in the 0.6.0 cleanup: prior versions kept a "canonical
shipping archive at the plugin root", which conflicted with the
read-only-installation reality and made it impossible to enforce a
clean repo without a special-case whitelist entry. The new contract is
simpler and uniform: every artefact lives in `/tmp/<plugin-name>-workspace/`,
the archive included.

First locate the plugin root folder (it contains
`.claude-plugin/plugin.json`) — either from conversation context or via:

```bash
find /sessions /mnt -name "plugin.json" -path "*/.claude-plugin/*" 2>/dev/null | head -5
```

> **Zip from a clean copy, not from `/tmp` itself.** The recipe below
> `cp -r`s the plugin root into `/tmp/<plugin-name>-workspace/src/`
> and then `cd`s into *that* folder before zipping. Never run
> `cd /tmp && zip -r ….plugin .` — zip would then include every
> sibling folder in `/tmp` (snapshot dirs, other builds, grader
> workspaces) inside the archive, and the user would receive an
> archive with mystery top-level folders. Also: before building,
> delete any pre-existing `/tmp/<plugin-name>-workspace/<plugin-name>.plugin`;
> `zip -r` appends to an existing archive rather than replacing it.

```bash
WORK=/tmp/<plugin-name>-workspace
mkdir -p "$WORK"
rm -rf "$WORK/src" "$WORK/<plugin-name>.plugin"
cp -r /path/to/plugin-root "$WORK/src"
# Defensive scrub — the source tree should already be clean, but if a
# stray runtime artefact slipped in we drop it before zipping.
rm -rf "$WORK/src/.mcpb-cache" \
       "$WORK/src/"*.plugin \
       "$WORK/src/"*-workspace \
       "$WORK/src/skill-snapshot"
cd "$WORK/src"
zip -r "$WORK/<plugin-name>.plugin" . \
  -x "*.DS_Store" \
  -x "*/evals/*" \
  -x "*.plugin" \
  -x "*/__pycache__/*" \
  -x "*.pyc"

# Verify
unzip -l "$WORK/<plugin-name>.plugin" | head -30
python3 -c "
import zipfile, json
z = zipfile.ZipFile('$WORK/<plugin-name>.plugin')
json.loads(z.read('.claude-plugin/plugin.json'))
print('plugin.json: valid JSON inside archive')
"
```

Replace `<plugin-name>` with the actual plugin name from
`.claude-plugin/plugin.json`. Offer the finished archive to the user
via a `computer://` link pointing at `/tmp/<plugin-name>-workspace/<plugin-name>.plugin`,
together with a one-line reminder that the next step is to upload the
archive as the new GitHub Release asset. Do not copy the archive into
the workspace folder.

#### Delivery — `/tmp` first, `dist/` as documented fallback

The standard delivery path is the `computer://` link into the `/tmp`
workspace. If the user reports that the link will not open or the
"Save As" dialog refuses the `/tmp` source — a known issue in Cowork
where tmpfs paths are sometimes not routable through the file-browser
"Save" flow — fall back to staging the archive in `dist/` at the repo
root:

```bash
mkdir -p /path/to/repo/dist
rm -f /path/to/repo/dist/*.plugin    # idempotent: drop any stale archive
cp "$WORK/<plugin-name>.plugin" /path/to/repo/dist/
```

The `rm -f` before the `cp` matters because P7's archive-shape check
(0.6.3) asserts that every `dist/*.plugin` matches the repo's current
`plugin.json` version. If a prior release's archive is still in
`dist/`, re-running the fallback step would leave both archives in
place and Layer 1 would FAIL on version drift. The idempotent recipe
keeps the `dist/` directory at exactly one archive — the current
release candidate — so a re-run is safe.

Then share a `computer://` link pointing at
`/path/to/repo/dist/<plugin-name>.plugin`. Layer 1 explicitly
allow-lists `dist/*.plugin` files; anything else under `dist/`
(wrong extension, nested directory) is still a FAIL. `.gitignore`
covers `*.plugin` repo-wide so the staging copy never lands in a
commit. The `dist/` directory itself is not tracked — create it on
demand (`mkdir -p /path/to/repo/dist`) only when the fallback is
actually needed.

`dist/` is a transition zone, not a permanent home. The archive's
destination is the GitHub Release asset list; a file in `dist/` is a
staging copy the user can open from Cowork's file browser *on the way
to* uploading. After the release is cut, `dist/` is expected to be
empty again. The `plugin-check.py --strict-release` flag (added in
0.6.4) enforces this post-release invariant — invoke it manually
after cutting a release, or wire it into CI on release-tag pushes.

See `references/plugin-eval.md` "Delivery — /tmp first, dist/ as
documented fallback" for the full rationale and the Layer 1 contract.

---

### Step 5 — Plugin-level iteration loop (three layers)

This step runs after every change **before** packaging. It is the
plugin-level analogue of the skill-creator's test-and-improve loop: the
plugin change is only considered finished when three independent layers
all close in one complete pass.

Mechanics and rationale are in `references/plugin-eval.md`. The summary
below is load-bearing and must be executed in full.

#### 5a — Layer 1: Structural check (runnable)

Run the bundled grading script:

```bash
python3 skills/update-plugin/scripts/plugin-check.py <plugin-root>
```

The script asserts: plugin.json validity and completeness, version
format, CHANGELOG↔plugin.json version consistency, README completeness
(no mid-sentence truncation), README↔skills coverage (no missing or
ghost skills), `_shared` files present, SKILL_TEMPLATE present, each
SKILL.md has valid YAML frontmatter with name+description and
references both `_shared/language.md` and `_shared/environments.md`,
no mid-sentence truncation in any SKILL.md, every `references/X.md`
reference resolves, no stray files at the plugin root (whitelist), and
no runtime artefacts anywhere in the plugin tree or repo root
(`*.plugin`, `*-workspace/`, `skill-snapshot/`, `eval-viewer-iter*.html`,
`COUNCIL.md`, `iteration-workspace/`).

Exit 0 means Layer 1 passes. Exit 1 means at least one assertion
failed — fix it and re-run.

#### 5b — Layer 2: Per-skill evals

Layer 2 asks: did every skill's own eval loop close? The grading script
looks for `skills/<name>/scripts/grade.py` or
`skills/<name>/evals/grade.py` for each skill (excluding `_shared`). If
the script exists, it is executed; exit code 0 counts as PASS, anything
else as FAIL. If neither exists, the skill is recorded as SKIP
(informational — not a failure, but a gap to close when that skill is
next iterated).

#### 5c — Layer 3: Independent audit subagent

Spawn a single subagent with a clean prompt, **unprimed**, to inspect
the plugin fresh:

```
I have a plugin at <plugin-root>. Inspect it without preconditioning
and report, under 400 words.

For each finding, classify two things:

1. CATEGORY (a-e):
   (a) Standards compliance gaps — SKILL.md structure, frontmatter,
       language and environment blocks, internal references.
   (b) Skill-quality concerns — unclear descriptions, missing triggers,
       weak negative scope, unclear web fallback.
   (c) Documentation mismatches — README claims vs. actual state.
   (d) Slash-command / skill pairing issues.
   (e) Anything surprising or smelly.

2. KIND:
   - STRUCTURE — a contract is violated: a required section is missing,
     a reference doesn't resolve, a version is out of sync, a flag is
     absent where the standard mandates it, the archive contains stray
     content. These should be Layer 1 assertions if they aren't
     already.
   - WORDING — the text is merely inconsistent across files, unclear,
     or open to misreading; no contract is violated. Fix the wording.
     Do NOT promote these into Layer 1 assertions.

Also classify severity (HIGH / MEDIUM / LOW) separately — but apply
severity after KIND, because a pure WORDING drift is almost never HIGH
even when it looks dramatic in isolation. A STRUCTURE violation is
almost always at least MEDIUM.

Only report findings, not a plan. No recommendations beyond "this is a
gap".
```

Collect the findings. Cross-check against the Layer 1 report. For each
finding:

- Already caught by Layer 1 → confirmation; proceed.
- Missed by Layer 1, **KIND=STRUCTURE**, real → fix it AND add a new
  Layer 1 assertion for it in `scripts/plugin-check.py`. Note the new
  assertion in 5e.
- Missed by Layer 1, **KIND=WORDING**, real → fix the wording only; do
  NOT add a Layer 1 assertion. Wording drift is not a structural
  contract and would require fuzzy matching to automate, which
  generates false positives. Layer 3 catches these cheaply on the next
  pass; that is the right division of labour.
- False positive → document in 5e why not.

Layer 3 cannot be replaced by assertions — its role is to find the
unknown-unknowns that grow the assertion set over time, and to flag
the wording inconsistencies that Layer 1 is not designed to catch.

#### 5d — Loop to closure

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

The loop closes only when a single complete pass has zero real
failures across all three layers. No shortcuts. The plugin is only
packaged after a fully positive pass.

#### 5e — Self-optimisation (after every change)

Review the change and the findings from 5a/5b/5c. Answer:

1. Did the change reveal a gap in the standard — something that was
   unclear or repeatedly discussed?
2. Did something need to be decided manually that should actually be a
   rule?
3. Did Layer 3 surface a real finding that Layer 1 missed? If so, a
   new Layer 1 assertion is expected.
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

## Procedure in Claude AI (Web)

This skill authors and maintains a Claude plugin — which means it writes
files, runs scripts, spawns subagents, and rebuilds a `.plugin` archive.
None of those are possible in Claude AI (Web), where there is no
filesystem and no subprocess execution.

The web fallback is therefore deliberately narrow:

1. **State the constraint plainly.** Tell the user that full plugin
   development requires file access, and that Cowork or Claude Code is
   the right environment for this workflow.
2. **Offer conceptual help instead.** In the web, this skill can still
   help: design a new skill's structure, draft a SKILL.md body, sketch
   references, reason about the Layer 3 audit prompt, or work through
   a self-optimisation proposal — all as text the user can copy into
   their file-access environment later.
3. **Do not simulate file operations.** Never pretend to run
   `plugin-check.py`, never invent assertion counts, never claim a
   layer has passed. The three-layer loop in Step 5 is a
   file-and-subprocess contract; claiming a pass without execution is
   a standard violation.
4. **Hand off cleanly.** When the user is ready to actually ship,
   produce a short hand-off note listing the files that need to
   change, the version bump, and the CHANGELOG entry — so resuming in
   Cowork or Claude Code is a single paste rather than a re-derivation.

---

## Versioning scheme

Format: `major.minor.fix`

- **major** — incremented only on explicit user instruction
- **minor** — incremented only on explicit user instruction
- **fix** — incremented automatically for every change (even small
  ones)

> **Agent rule (binding):** An agent running this skill may only ever
> bump the **fix** level. Never unilaterally propose a minor or major
> bump — not because a refactor feels large, not because the
> user-facing behavior changes visibly, not because the change touches
> many files. If a change subjectively warrants more than a fix,
> deliver the fix bump and ask the user whether they want to re-label
> it as minor or major. Never the other direction. The judgment of
> semantic level belongs to the user; the mechanical increment belongs
> to the agent.

After every change: bump the fix version in `plugin.json`, add an entry
to `CHANGELOG.md` (newest on top), and update the version reference in
`README.md`.

---

## Plugin structure reference

```
<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          ← name, version, author
├── CHANGELOG.md             ← version history, newest entry on top
├── README.md                ← user documentation + plugin standards
├── SKILL_TEMPLATE.md        ← template for new skills
├── commands/                ← optional, slash-command entry points (one .md per command)
│   └── <command>.md         ← carries full contract for its command (self-sufficient)
└── skills/
    ├── _shared/
    │   ├── environments.md  ← environment logic (single source of truth)
    │   └── language.md      ← output language rules (single source of truth)
    └── <skill-name>/
        ├── SKILL.md
        └── references/      ← optional, for progressive disclosure
```

Any deviation from this structure is a deficiency and must be
corrected.

A skill follows one of **three legal patterns**, and the `commands/`
directory is relevant only for patterns 2 and 3.

**Pattern 1 — Auto-only** (default for light, scoped skills). No
`disable-model-invocation` flag in SKILL.md. No command file. Claude
decides when to fire from the description's trigger signals. Correct
whenever firing-on-signal would not surprise the user and there is no
meaningful argument the user would want to pass explicitly.

**Pattern 2 — Command-only** (heavy, multi-turn, or opinionated skills —
e.g. `/council`, `/update-plugin`). Pairing is mandatory and
bidirectional:

- `commands/<name>.md` is the primary entry in Claude Code and Cowork.
  It must carry the full contract inline so a standard run loads no
  reference files.
- `skills/<name>/SKILL.md` must set both `disable-model-invocation:
  true` and `user-invocable: true` in its frontmatter. The first
  prevents auto-triggering; the second is required as of Claude Code
  late-2025 to preserve slash-command invocation when
  `disable-model-invocation` is set (see `references/plugin-eval.md`
  for the upstream issue references). The SKILL.md serves as the
  Claude AI (Web) fallback where slash commands are unavailable.

**Pattern 3 — Auto + Command** (introduced in 0.6.0 with `rename-pdf`).
The skill keeps its auto-trigger surface AND ships a companion command.
No `disable-model-invocation` flag. Paired `commands/<name>.md` exists
and carries the full contract for the command path. Use this when both
entry points are legitimate — the auto path handles discovery ("could
you clean up my scans?") and the command path handles direct argumented
use (`/rename-pdf ~/inbox`).

Decision rule: ask **"does this skill need a command entry at all?"**
- If no → Pattern 1.
- If yes and auto-firing would race the user's intent (long deliberation,
  opinionated workflow) → Pattern 2.
- If yes and both paths are legitimate → Pattern 3.

Layer 1 enforces:
- Every `commands/<name>.md` needs a paired `skills/<name>/SKILL.md`
  (Pattern 2 or 3).
- Every non-auto skill (Pattern 2) needs its paired command, otherwise
  the skill is unreachable in Claude Code / Cowork.

See `scripts/plugin-check.py`.

Pattern 2 was introduced in 0.5.0 for the `council` skill; the
`user-invocable: true` addition was introduced when this skill was
renamed from `neomint-plugin-entwicklung` to `update-plugin`. Pattern 3
was introduced in 0.6.0 alongside the `pdf-umbenennen` → `rename-pdf`
rename.

---

## Additional references

- `references/plugin-eval.md` — detailed mechanics of the three-layer
  plugin iteration loop (Layer 1 structural, Layer 2 per-skill evals,
  Layer 3 independent audit subagent), how to add assertions, and why
  Layer 3 cannot be replaced by a script.
- `scripts/plugin-check.py` — runnable grading script for Layers 1+2.
  Exit code 0 = pass; JSON report written to
  `/tmp/plugin-check-report.json`.
