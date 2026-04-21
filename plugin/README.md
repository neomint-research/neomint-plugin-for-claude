# NeoMINT Toolkit

A Claude plugin from [NeoMINT GmbH](https://neomint.com) — a growing set of skills for recurring workflows, built to the same quality bar we apply to our own production work. Compatible with Claude Code, Cowork, and Claude AI (Web).

**Current version:** `0.5.10` — see [`CHANGELOG.md`](CHANGELOG.md) for history.
**License:** [Apache License 2.0](LICENSE).

---

## Install

Download the latest `neomint-toolkit.plugin` file from the [`plugin/`](.) directory of the repository and install it the same way you install any local Claude plugin:

- **Claude Code / Cowork:** open the plugin from your file manager, or point your plugin tooling at the `.plugin` file.
- **Building from source:** from inside this `plugin/` directory, run `rm -f neomint-toolkit.plugin && zip -r neomint-toolkit.plugin . -x '*.git*' -x '*.github/*' -x 'CONTRIBUTING.md' -x '*.DS_Store' -x '*/.mcpb-cache/*' -x '*/evals/*' -x '*.plugin'`. `LICENSE` and `SECURITY.md` ship inside the bundle so installed users see the license terms and security policy without needing the repository. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full build procedure.

---

## What's inside

Three skills, each opt-in, each scoped to one job.

### `council`

Context-aware judgment skill with five MECE roles (Cartographer, Analyst, Adversary, Scout, Operator) and a Chairman synthesis. Used when you want a qualified opinion on a plan, design, or draft rather than a blank-slate rewrite.

It runs as a **live, turn-gated deliberation**: one turn per assistant message (T1 Read-back + Grounding · T2 Cartographer · T3 Analyst · T4 Adversary · T5 Scout · T6 Operator · T7 Verdict). The role identifies itself inside the first sentence of its prose — no turn header, no position counter. A turn ends where the advisor's thought ends. You can steer between any two roles using `weiter`, `widersprich`, `vertiefe`, `abzweig`, `stopp`, or free-text interpreted charitably; the vocabulary is introduced once, as prose, at the end of T1, and then you are trusted to remember. The Grounding in T1 puts Hersteller (authoritative source) and Community (practitioner consensus) on the table before any role speaks, so the run starts from a shared, named substrate rather than reasoning in a vacuum. From T3 onward every role must engage with a prior role by name — agreement with reason, extension with reason, or substantive dissent — so the five turns compound instead of drifting into parallel essays. When the question arrives sharp (narrow binary or enumerated choice, context already on the table, Hersteller and Community aligned), the skill runs one compressed verdict turn instead of seven — brief grounding, five MECE angles in prose named by role, verdict sentence, first step. Scope reduction is legitimate when rigor is preserved: the skill shrinks the question, but never simplifies it. The Verdict is adaptive: narrow question → one paragraph; broad question → two paragraphs (operative + management); inconclusive → a paragraph naming the gap and what would resolve it. Follow-up runs are cheaper because `COUNCIL.md` persistence remembers prior framing.

**Primary entry is `/council`.** In Claude Code and Cowork the Council is invoked explicitly by typing `/council` — not by auto-matching on decision language. The slash-command file at [`commands/council.md`](commands/council.md) delegates to the skill's contract, which lives in [`skills/council/SKILL.md`](skills/council/SKILL.md). That SKILL.md is also the fallback for Claude AI (Web), where slash commands are unavailable — its `disable-model-invocation: true` frontmatter blocks auto-triggering so the user remains in charge of when the Council fires. One reference file is loaded on demand: [`references/roles.md`](skills/council/references/roles.md) carries the method, deliverable, failure modes, and abstention triggers per role. A standard run completes without reading it; it is pressure-check material for a role about to post its turn.

### `pdf-umbenennen`

Renames scanned PDF documents based on their content — date, sender, subject — following `yyyy-mm-dd_Sender_Subject-short.pdf`. Reads files in parallel batches. Triggers on phrases like "rename scans", "clean up ScanSnap folder", "name files by date and sender".

### `update-plugin`

Explicit-invocation governance skill for updating any Claude plugin — adding a new skill, modifying an existing skill, updating plugin standards, or repackaging. Enforces pre-research, the official `skill-creator` workflow for every content change, the three-layer iteration loop, and repackaging after every change. Proposes improvements to the standard or to itself after every run. Primary entry is `/update-plugin` (see [`commands/update-plugin.md`](commands/update-plugin.md)); the description-driven trigger is the fallback for Claude AI (Web). This is the generalised successor to `neomint-plugin-entwicklung` — both coexist for now so in-flight references stay valid; new plugin work should prefer `update-plugin`.

### `neomint-plugin-entwicklung`

The original governance skill, NeoMINT-specific. Same mechanics as `update-plugin` but phrased around this toolkit's standards directly. Kept alongside `update-plugin` during the transition; expect it to be removed in a future release once all references are migrated.

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

Any deviation from this structure is a deficiency and must be corrected. The
`commands/` directory is optional and only relevant for **explicit-invocation
skills** — skills the user is expected to fire by name rather than have Claude
auto-trigger on context. For such a skill the contract is bidirectional:
`commands/<name>.md` carries the full contract inline (so a standard run loads
no reference files), and its paired `skills/<name>/SKILL.md` must set
`disable-model-invocation: true` in its frontmatter to prevent auto-triggering
and also serves as the Claude AI (Web) fallback where slash commands are
unavailable. Auto-triggering skills (e.g. `pdf-umbenennen`, `neomint-plugin-entwicklung`)
have no command file and no `disable-model-invocation` flag — that is correct and
intentional, not a deficiency. Layer 1 enforces the pairing: any `commands/X.md`
without a matching `disable-model-invocation` skill, and any skill with that flag
without a matching `commands/<name>.md`, is a violation.

### Required blocks in every SKILL.md

YAML frontmatter with `name` and a **pushy** `description` that includes trigger signals and negative scope (what the skill is *not* for). A `## Language` block referencing `../_shared/language.md`. An `## Environment detection` block referencing `../_shared/environments.md`. A `## Procedure with file access (Claude Code & Cowork)` section. A `## Procedure in Claude AI (Web)` section defining the web fallback. An optional `## Additional references` section listing `references/*.md`.

### Output language

All skill content is written in English for optimal LLM performance. The output language for the user follows `skills/_shared/language.md`: match the user's language by default, or the configured override if set.

### Environment compatibility

Every skill must work in Claude Code, Cowork, and Claude AI (Web). The first two share filesystem semantics; the web fallback is defined per skill (upload → process → download / script / analysis).

### No internal data

Skill examples must not contain NeoMINT GmbH internal names, addresses, customer data, or confidential material.

### Ground-Before-Discuss

Every judgment-producing step in the toolkit — authoring a new skill, grading an existing one, producing a Council verdict — surfaces the authoritative source first and the community position second, *before* discussion. The governance skill's Step 0 pre-research lives this at plugin scope (Anthropic GitHub first, community second, Anthropic wins on conflict). The `council` skill's Phase 1 GROUND lives it at judgment scope (Hersteller first, Community second, divergence named). Neither is optional: a standard decided in a vacuum decays; a judgment reasoned in a vacuum rediscovers settled knowledge. If no authoritative source exists for a question, state that absence explicitly — it's a finding, not a skip. If the community position is unreachable, state the fallback and the cutoff. Silent omission of either source is a contract violation.

### Build artefacts

Transient artefacts — intermediate zips, extracted source trees, grader reports, eval outputs, cache folders — are written to `/tmp` (or an equivalent workspace outside the plugin tree), never to the plugin root. Only the canonical shipping artefact (`*.plugin`) is permitted alongside the plugin root. The Layer 1 root-whitelist in `plugin-check.py` enforces this: anything new at the root must be either added to the whitelist (because it genuinely belongs to the plugin) or moved under `/tmp`. This rule exists because leftover build state was shipped inside the plugin in 0.3.x–0.4.0 — `.mcpb-cache/` and a stray `zimjorit` archive both slipped through until Layer 1 was added in 0.4.1.

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

**Layer 1** — structural assertions on every file (bundled `scripts/plugin-check.py`: plugin.json integrity, version consistency, SKILL.md block completeness, shared-file presence, reference coverage, root-whitelist enforcement, shipping-archive cleanliness).

**Layer 2** — per-skill graders. Each skill ships its own `scripts/grade.py` encoding its own contract. The council grader currently runs 44 checks protecting the seven-turn shape, the five MECE role axes, the GROUND-FIRST discipline with its binding sentence, the adaptive Verdict's three complexity regimes, the `"Reicht" is not a verdict` principle, and the anti-pattern enumeration that forbids the removed ceremony by name.

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

The process is enforced by the `neomint-plugin-entwicklung` skill. In summary:

1. **Pre-research (mandatory).** Check Anthropic GitHub (`anthropics/skills`, `anthropics/claude-plugins-official`, `anthropics/claude-code`) and community sources for the current gold standard. Present a brief research summary before proceeding.
2. **Clarify the goal.** New skill, modification, standard update, or repackage only?
3. **Use the official skill-creator skill.** For every creation or content change of a skill, without exception. Direct edits to SKILL.md without skill-creator violate the plugin standard.
4. **Quality checks.** Run the 8-item checklist (pre-research, template compliance, language block, environment block, web fallback, description, no internal content, conventions).
5. **Update metadata.** Bump version in `plugin.json`, add CHANGELOG entry, update README.
6. **Three-layer iteration loop.** Layer 1 structural, Layer 2 per-skill grader, Layer 3 unprimed audit. The loop closes only when all three pass in one complete pass.
7. **Repackage** into `.plugin` file and deliver.
8. **Self-optimisation.** After every change: did Layer 3 surface something the assertion set missed? If so, a new Layer 1 assertion is expected. Propose improvements to the standard.

See the `neomint-plugin-entwicklung` skill for the full procedure.

---

## Security

To report a security issue, see [`SECURITY.md`](SECURITY.md).

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).

## Author

[NeoMINT GmbH](https://neomint.com)
