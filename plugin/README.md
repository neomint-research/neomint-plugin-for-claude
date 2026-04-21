# NeoMINT Toolkit

A Claude plugin from [NeoMINT GmbH](https://neomint.com) — a growing set of skills for recurring workflows, built to the same quality bar we apply to our own production work. Compatible with Claude Code, Cowork, and Claude AI (Web).

**Current version:** `0.4.9` — see [`CHANGELOG.md`](CHANGELOG.md) for history.
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

Context-aware judgment skill with five MECE roles (Analyst, Cartographer, Adversary, Scout, Operator) and a Chairman synthesis. Used when you want a qualified opinion on a plan, design, or draft rather than a blank-slate rewrite.

It runs as a **turn-gated live deliberation**: one phase per assistant message (T1 Orient · T2 **Ground** (Hersteller + Community, before any role speaks) · T3 Cartographer · T4 Analyst · T5 Adversary · T6 Scout · T7 Operator · T8 Verdict in FULL mode; three-turn compressed form in QUICK mode). Each turn ends in a visible sentinel so you can follow along, rebut a specific role, deepen any point, branch to a new premise, or abort cleanly — without restarting. The verdict produces a two-track output: an operative track with references and a management track with one recommendation. Every role turn from T4 onward must cite a prior role turn by direct quote, and the Chairman's verdict must cite each role — so you can see who heard whom. Follow-up runs are cheaper because `COUNCIL.md` persistence remembers prior framing.

Triggers include decision language ("should we", "is this a good idea"), validation language ("check my reasoning", "poke holes"), risk language ("what could go wrong", "blind spots"), and completeness language ("what's missing", "audit").

### `pdf-umbenennen`

Renames scanned PDF documents based on their content — date, sender, subject — following `yyyy-mm-dd_Sender_Subject-short.pdf`. Reads files in parallel batches. Triggers on phrases like "rename scans", "clean up ScanSnap folder", "name files by date and sender".

### `neomint-plugin-entwicklung`

The governance skill that accompanies every change to the plugin itself. It ensures the official `skill-creator` skill is used for content changes, mandates pre-research against Anthropic's own repositories, enforces a three-layer iteration loop, and repackages the plugin after every change. This is the skill that makes the other two keep working.

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
└── skills/
    ├── _shared/
    │   ├── environments.md  ← environment logic (single source of truth)
    │   └── language.md      ← output language rules (single source of truth)
    └── <skill-name>/
        ├── SKILL.md
        └── references/      ← optional, for progressive disclosure
```

Any deviation from this structure is a deficiency and must be corrected.

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

Every change must bump the appropriate version field in `plugin.json`, add a top entry to `CHANGELOG.md`, and update the version reference in this README.

---

## How it's built

The toolkit is maintained through a three-layer iteration loop, described in full in [`CONTRIBUTING.md`](CONTRIBUTING.md):

**Layer 1** — structural assertions on every file (bundled `scripts/plugin-check.py`: plugin.json integrity, version consistency, SKILL.md block completeness, shared-file presence, reference coverage, root-whitelist enforcement, shipping-archive cleanliness).

**Layer 2** — per-skill graders. Each skill ships its own `scripts/grade.py` encoding its own contract. The council grader currently runs 33 checks.

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
