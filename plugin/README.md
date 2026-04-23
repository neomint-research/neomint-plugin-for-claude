# NeoMINT Toolkit

A Claude plugin from [NeoMINT GmbH](https://neomint.com) — a growing set of skills for recurring workflows, built to the same quality bar we apply to our own production work. Compatible with Claude Code, Cowork, and Claude AI (Web).

**Current version:** `0.6.15` — see [`CHANGELOG.md`](CHANGELOG.md) for history.
**License:** [Apache License 2.0](LICENSE).

---

## Install

Download the latest `neomint-toolkit.plugin` file from the project's [GitHub Releases](https://github.com/neomint/NeoMINT-plugin/releases) page — the archive is attached as a release asset, not committed to the source tree — and install it the same way you install any local Claude plugin:

- **Claude Code / Cowork:** open the plugin from your file manager, or point your plugin tooling at the `.plugin` file.
- **Building from source (for local testing):** from inside this `plugin/` directory, run `rm -f neomint-toolkit.plugin && zip -r neomint-toolkit.plugin . -x '*.git*' -x '*.github/*' -x 'CONTRIBUTING.md' -x '*.DS_Store' -x '*/.mcpb-cache/*' -x '*/evals/*' -x '*.plugin'`. `LICENSE` and `SECURITY.md` ship inside the bundle so installed users see the license terms and security policy without needing the repository. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full build and release procedure.

---

## What's inside

Five skills, each opt-in, each scoped to one job. Four are paired with a `/skill-name` slash command (Pattern 2 or 3); `video-preview` is Pattern 1 (auto-trigger only, no command).

### `council`

Context-aware judgment skill with five MECE roles (Cartographer, Analyst, Adversary, Scout, Operator) and a Chairman synthesis. Used when you want a qualified opinion on a plan, design, or draft rather than a blank-slate rewrite.

It runs as a **live, turn-gated deliberation**: one turn per assistant message (T1 Read-back + Grounding · T2 Cartographer · T3 Analyst · T4 Adversary · T5 Scout · T6 Operator · T7 Verdict). The role identifies itself inside the first sentence of its prose — no turn header, no position counter. A turn ends where the advisor's thought ends. You can steer between any two roles using `weiter`, `widersprich`, `vertiefe`, `abzweig`, `stopp`, or free-text interpreted charitably; the vocabulary is introduced once, as prose, at the end of T1, and then you are trusted to remember. The Grounding in T1 puts Hersteller (authoritative source) and Community (practitioner consensus) on the table before any role speaks, so the run starts from a shared, named substrate rather than reasoning in a vacuum. From T3 onward every role must engage with a prior role by name — agreement with reason, extension with reason, or substantive dissent — so the five turns compound instead of drifting into parallel essays. When the question arrives sharp (narrow binary or enumerated choice, context already on the table, Hersteller and Community aligned), the skill runs one compressed verdict turn instead of seven — brief grounding, five MECE angles in prose named by role, verdict sentence, first step. Scope reduction is legitimate when rigor is preserved: the skill shrinks the question, but never simplifies it. The Verdict is adaptive: narrow question → one paragraph; broad question → two paragraphs (operative + management); inconclusive → a paragraph naming the gap and what would resolve it. Follow-up runs are cheaper because `COUNCIL.md` persistence remembers prior framing.

**Primary entry is `/council`.** In Claude Code and Cowork the Council is invoked explicitly by typing `/council` — not by auto-matching on decision language. The slash-command file at [`commands/council.md`](commands/council.md) delegates to the skill's contract, which lives in [`skills/council/SKILL.md`](skills/council/SKILL.md). That SKILL.md is also the fallback for Claude AI (Web), where slash commands are unavailable — its `disable-model-invocation: true` frontmatter blocks auto-triggering so the user remains in charge of when the Council fires. One reference file is loaded on demand: [`references/roles.md`](skills/council/references/roles.md) carries the method, deliverable, failure modes, and abstention triggers per role. A standard run completes without reading it; it is pressure-check material for a role about to post its turn.

### `rename-pdf`

Renames scanned PDF documents based on their content — date, sender, subject — following `yyyy-mm-dd_Sender_Subject-short.pdf`. Reads files in parallel batches. Triggers on phrases like "rename scans", "clean up ScanSnap folder", "name files by date and sender" in either English or German. Also runs via the `/rename-pdf [folder]` command for direct argumented use — an example of the **Auto + Command** pattern (see *Invocation patterns* below). Previously shipped as pdf-umbenennen (German name); renamed in 0.6.0 so the skill's identifier follows Anthropic's English-by-default convention.

### `session-docs`

Auto-trigger skill that keeps all project documentation in sync throughout
a work session. Reads at session start (MEMORY.md → KNOWN_ISSUES.md →
HANDOVER.md → task list), writes immediately after new findings — no
"remember to update at the end" discipline required. Four update triggers,
each scoped to the right documentation location: CI/tool results → KNOWN_ISSUES,
direction changes → HANDOVER, user corrections → Memory, work steps → task list.
Creates missing files from bundled templates. Also responds to explicit calls:
"session abschliessen", "übergabe vorbereiten", "aufräumen".

### `video-preview`

Turns a website, web app, dashboard, or static HTML/CSS page into a compressed
MP4 preview video using Puppeteer (headless Chromium) and ffmpeg. Default output:
1080×1920 (9:16 portrait), H.264, optimised for Signal, WhatsApp, Slack, or email.
Three interaction patterns: scroll-through (page from top to bottom), click-demo
(defined sequence of selectors to click, with frame capture between each action),
and highlight-zoom (CSS transform zoom into a specific element). Output naming
follows `yyyy-mm-dd_description_preview.mp4`. Automatically detects missing
Puppeteer or ffmpeg and gives install instructions; in Claude AI (Web), delivers
a ready-to-run `record.js`, `stitch.sh`, and `README.md` instead of executing
directly. Triggers on phrases like "make a preview video", "record the page",
"zeig das als Clip", or "ich will das schnell teilen können".

### `update-plugin`

Explicit-invocation governance skill for updating any Claude plugin — adding a new skill, modifying an existing skill, updating plugin standards, or repackaging. Enforces pre-research, the official `skill-creator` workflow for every content change, the three-layer iteration loop, and repackaging after every change. Proposes improvements to the standard or to itself after every run. Primary entry is `/update-plugin` (see [`commands/update-plugin.md`](commands/update-plugin.md)); the description-driven trigger is the fallback for Claude AI (Web). `update-plugin` is the generalised successor to the earlier NeoMINT-specific governance skill, removed in 0.6.0.

---

## Plugin standards

These rules apply to every skill in the toolkit. They are the working standard, not aspirational.

### Structure

```
neomint-toolkit/
├── .claude-plugin/
│   └── plugin.json          ← name, version, author
├── CHANGELOG.md             ← version history, newest entry on top
├── README.md                ← this file; user documentation + plugin standards
├── SKILL_TEMPLATE.md        ← template for new skills
├── commands/                ← optional, slash-command entry points
│   └── <command>.md         ← one .md per command, carries full contract
└── skills/
    ├── _shared/
    │   ├── environments.md  ← environment logic (single source of truth)
    │   └── language.md      ← output language rules (single source of truth)
    └── <skill-name>/
        ├── SKILL.md
        └── references/      ← optional, for progressive disclosure
```

Any deviation from this structure is a deficiency and must be corrected.

**Three legal invocation patterns.** A skill can follow any one of three
shapes, and Layer 1 enforces the choice.

1. **Auto-only** (default, e.g. `council`'s predecessor before the
   command-only refactor, and most small skills). No `disable-model-invocation`
   flag. No command file. The model decides when to fire from the
   description's trigger signals. Correct for lightweight, scoped tasks
   that are safe to fire on signal.

2. **Command-only** (heavy workflows that must not race user intent, e.g.
   `/council`, `/update-plugin`). `disable-model-invocation: true` in the
   skill's frontmatter. Paired `commands/<name>.md` carries the full
   contract inline so `/name` loads no reference files; the SKILL.md
   serves as the Claude AI (Web) fallback. Auto-firing is disabled because
   the skill is opinionated enough that the user must opt in.

3. **Auto + Command** (added in 0.6.0 with `rename-pdf`). No
   `disable-model-invocation` flag. Paired `commands/<name>.md`. The
   skill auto-fires on clear intent signals AND accepts an explicit
   `/name [argument]` invocation. Correct when both paths are
   legitimate — the auto path covers discovery ("can you clean up my
   scans?") and the command path covers direct use with arguments
   (`/rename-pdf ~/inbox`).

Layer 1 enforces the pairing:
- Every `commands/<name>.md` needs a paired `skills/<name>/SKILL.md` (pattern
  2 or 3).
- Every non-auto skill (pattern 2) needs its paired command, otherwise the
  skill is unreachable in Claude Code / Cowork.

### Required blocks in every SKILL.md

YAML frontmatter with `name` and a **pushy** `description` that includes trigger signals and negative scope (what the skill is *not* for). A `## Language` block referencing `../_shared/language.md`. An `## Environment detection` block referencing `../_shared/environments.md`. A `## Procedure with file access (Claude Code & Cowork)` section. A `## Procedure in Claude AI (Web)` section defining the web fallback. An optional `## Additional references` section listing `references/*.md`.

### Required blocks in every `commands/*.md`

YAML frontmatter (between `---` markers) with at least a `description` field. An optional `argument-hint` field for autocomplete. Layer 1 enforces the presence of frontmatter on every command file.

### Output language

All skill content is written in English for optimal LLM performance. The output language for the user follows `skills/_shared/language.md`: match the user's language by default, or the configured override if set.

### Environment compatibility

Every skill must work in Claude Code, Cowork, and Claude AI (Web). The first two share filesystem semantics; the web fallback is defined per skill (upload → process → download / script / analysis).

### No internal data

Skill examples must not contain NeoMINT GmbH internal names, addresses, customer data, or confidential material.

### Ground-Before-Discuss

Every judgment-producing step in the toolkit — authoring a new skill, grading an existing one, producing a Council verdict — surfaces the authoritative source first and the community position second, *before* discussion. The governance skill's Step 0 pre-research lives this at plugin scope (Anthropic GitHub first, community second, Anthropic wins on conflict). The `council` skill's Phase 1 GROUND lives it at judgment scope (Hersteller first, Community second, divergence named). Neither is optional: a standard decided in a vacuum decays; a judgment reasoned in a vacuum rediscovers settled knowledge. If no authoritative source exists for a question, state that absence explicitly — it's a finding, not a skip. If the community position is unreachable, state the fallback and the cutoff. Silent omission of either source is a contract violation.

### Build artefacts

All runtime artefacts live in `/tmp/<plugin-name>-workspace/` — iteration outputs, grader reports, eval viewer HTML, extracted source trees, the shipping `.plugin` zip itself. Nothing gets written into the plugin source tree, and no `*.plugin` archive is permitted at the plugin root. Distribution is via GitHub Releases; the build pipeline uploads the archive from `/tmp/<plugin-name>-workspace/<plugin-name>.plugin`. Layer 1 enforces both halves: the root-whitelist rejects stray files at the plugin root, and a recursive sweep rejects runtime artefacts (`*.plugin`, `*-workspace/`, `skill-snapshot/`, `eval-viewer-iter*.html`, `COUNCIL.md`) anywhere in the plugin tree or the repo root. The rule exists because leftover build state was shipped inside the plugin in 0.3.x–0.4.0 (`.mcpb-cache/`, stray archives) and runtime artefacts silently accumulated in the source tree up to 0.5.x until the 0.6.0 cleanup made the contract uniform.

### Versioning

Format: `major.minor.fix`.
`major` increments only on explicit user instruction.
`minor` increments only on explicit user instruction.
`fix` increments automatically for every change (even small ones).

**Agent rule (binding):** an agent may only ever bump the `fix` level. Never unilaterally propose a minor or major bump — not because a refactor feels large, not because user-facing behavior changes visibly, not because many files are touched. If a change subjectively warrants more than a fix, deliver the fix bump and ask the user whether they want to re-label it. The semantic judgment belongs to the user; the mechanical increment belongs to the agent.

Every change must bump the appropriate version field in `plugin.json`, add a top entry to `CHANGELOG.md`, and update the version reference in this README.

---

## How it's built

The toolkit is maintained through a three-layer iteration loop, described in full in [`CONTRIBUTING.md`](CONTRIBUTING.md):

**Layer 1** — structural assertions on every file (bundled `scripts/plugin-check.py`: plugin.json integrity, version consistency, SKILL.md block completeness, shared-file presence, reference coverage, root-whitelist enforcement, runtime-artefact sweep across the entire repo, slash-command ⇔ skill pairing).

**Layer 2** — per-skill graders. Each skill ships its own `scripts/grade.py` encoding its own contract. The council grader protects the seven-turn shape, the five MECE role axes, the GROUND-FIRST discipline with its binding sentence, the adaptive Verdict's three complexity regimes, the `"Reicht" is not a verdict` principle, and the anti-pattern enumeration that forbids the removed ceremony by name. Counts drift as skills iterate; the binding number is always whatever the grader script actually asserts.

**Layer 3** — an unprimed audit subagent with no context from the change under review. It reads the delta and reports SHIP / HOLD with named defects. Blind spots the assertion set didn't know to look for surface here; the next iteration either fixes them or promotes them into a new Layer 1 or Layer 2 assertion.

The loop closes only when all three layers pass in one complete pass. This is the same rigor we apply to our consulting work, made visible.

---

## Open Research

This plugin is part of [NeoMINT GmbH](https://neomint.com)'s broader open-source work on making AI and the Model Context Protocol genuinely accessible. The skills themselves are utilities. The interesting part — and the reason this repository is public — is the governance model:

- **Ground-Before-Discuss** as a first-class rule rather than a habit
- A **three-layer quality loop** with an explicit role for unprimed audit
- A **skill-creator-first** workflow that refuses shortcuts even when the user asks for them

Each of these started as a specific failure we kept hitting and was promoted into a standard only after it proved load-bearing. The history lives in [`CHANGELOG.md`](CHANGELOG.md). The method is portable to other plugins and, we think, to other kinds of work.

Issues, pull requests, and pointed criticism are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Adding a new skill

The process is enforced by the `update-plugin` skill (slash command `/update-plugin`). In summary:

1. **Pre-research (mandatory).** Check Anthropic GitHub (`anthropics/skills`, `anthropics/claude-plugins-official`, `anthropics/claude-code`) and community sources for the current gold standard. Present a brief research summary before proceeding.
2. **Clarify the goal.** New skill, modification, standard update, or repackage only?
3. **Use the official skill-creator skill.** For every creation or content change of a skill, without exception. Direct edits to SKILL.md without skill-creator violate the plugin standard. Run the full iteration loop to closure — propose tests, get user approval, run subagents in parallel, generate the eval-viewer, wait for explicit user review, improve, repeat.
4. **Quality checks.** Run the 8-item checklist (pre-research, template compliance, language block, environment block, web fallback, description, no internal content, conventions).
5. **Update metadata.** Bump the `fix` field in `plugin.json`, add a CHANGELOG entry on top, update the version reference in this README.
6. **Run the three-layer plugin loop.** Layer 1 (`scripts/plugin-check.py`), Layer 2 (per-skill graders auto-discovered), Layer 3 (unprimed audit subagent). The loop closes only when one complete pass has zero real failures across all three layers.
7. **Repackage.** Build the `.plugin` archive in `/tmp/<plugin-name>-workspace/`, verify, and upload as a GitHub Release asset. Never commit the archive into the repo.
8. **Self-optimisation.** Surface concrete proposals for improving the standard or the governance skill itself, and only implement them after the user agrees.

The full contract — including the workspace path rule, the agent-only-bumps-fix rule, and the slash-command/SKILL.md frontmatter pairing — lives in [`skills/update-plugin/SKILL.md`](skills/update-plugin/SKILL.md) and [`skills/update-plugin/references/plugin-eval.md`](skills/update-plugin/references/plugin-eval.md).
