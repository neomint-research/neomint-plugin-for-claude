> **Dieses Repository ist archiviert.**
> Die kanonische Quelle ist [git.neomint.com/nm/neomint-plugin-for-claude](https://git.neomint.com/nm/neomint-plugin-for-claude).
> Issues, PRs und Releases werden dort gepflegt. Dieses GitHub-Repo bleibt als Read-only-Spiegel erhalten.

# NeoMINT Plugin for Claude

This repository is the public record of how [NeoMINT GmbH](https://neomint.com) builds and maintains a Claude plugin in production. It contains two things that share a commit history on purpose:

1. **A shipping Claude plugin** — `neomint-toolkit`, a small set of skills for recurring workflows (council deliberation, PDF renaming, plugin governance). The installable artefact lives in [`plugin/`](plugin/).
2. **An open record of the governance that produced it** — the iteration loop, the audit mechanics, and the evolving standard the skills are held to. That record lives in the plugin source, the commit history, and this README.

The plugin is genuinely useful on its own. The reason the repository is public is the second thing: we treat how the plugin is produced as the interesting artefact.

---

## Repository layout

```
neomint-plugin-for-claude/
├── README.md                 ← this file; repo-level intro
├── LICENSE                   ← Apache License 2.0
├── SECURITY.md               ← vulnerability disclosure policy
├── .github/                  ← CI workflow + issue/PR templates
└── plugin/                   ← the shipping plugin (everything below this is
    ├── .claude-plugin/         the plugin itself — see plugin/README.md for
    ├── skills/                 install instructions, skill docs, and the
    ├── commands/               plugin's own standards)
    ├── CHANGELOG.md
    ├── CONTRIBUTING.md
    ├── README.md
    ├── SKILL_TEMPLATE.md
    ├── LICENSE
    └── SECURITY.md
```

`LICENSE` and `SECURITY.md` are duplicated on purpose: the copies at the repo root exist for GitHub's discovery conventions, the copies inside `plugin/` ship inside the `.plugin` bundle so a user who only has the installed plugin still has the license text and security-contact information (Apache 2.0 §4 requires the license text to travel with the work).

---

## The plugin

See [`plugin/README.md`](plugin/README.md) for install instructions, the three skills and their triggers, the plugin's internal standards, and the build procedure. A short summary:

- **`council`** — turn-gated live deliberation with five MECE roles and a Chairman synthesis, built to answer decision-language prompts ("should we…", "check my reasoning", "what could go wrong") with a qualified opinion rather than a blank-slate rewrite.
- **`rename-pdf`** — renames scanned PDFs by content (date · sender · subject) in parallel batches. Auto-triggers on the right signals and also runs via `/rename-pdf [folder]`.
- **`update-plugin`** — the governance skill that gates every change to the plugin itself, enforcing pre-research, the official `skill-creator` workflow, and the three-layer iteration loop below. Runs via `/update-plugin`.

The installable artefact is distributed as a `.plugin` archive on the project's GitHub Releases page — it is built per release and is not committed to the source tree. Current version is recorded in [`plugin/.claude-plugin/plugin.json`](plugin/.claude-plugin/plugin.json) and [`plugin/CHANGELOG.md`](plugin/CHANGELOG.md).

---

## The governance model

Three mechanisms, each introduced after a specific failure we kept hitting. All three are enforced, not aspirational.

### Ground-Before-Discuss

Every judgment-producing step in the toolkit — authoring a new skill, grading an existing one, producing a Council verdict — surfaces the authoritative source *before* any discussion: Hersteller first (Anthropic GitHub repositories, official docs), community second, divergence named explicitly.

At plugin scope this lives in the governance skill's Step 0 pre-research. At judgment scope it lives in the Council's Phase 1 `GROUND` turn, which requires visible `WebSearch` / `WebFetch` tool calls, not narration.

If no authoritative source exists for a question, that absence is stated as a finding — not silently skipped. Silent omission of either source is a contract violation. A standard decided in a vacuum decays; a judgment reasoned in a vacuum rediscovers settled knowledge.

### Three-layer iteration loop

Every change to the plugin passes three layers before it is considered complete:

- **Layer 1** — structural assertions on the plugin root. Implemented deterministically in [`plugin/skills/update-plugin/scripts/plugin-check.py`](plugin/skills/update-plugin/scripts/plugin-check.py). Covers `plugin.json` integrity, version consistency with the CHANGELOG top entry, SKILL.md required blocks, shared-file presence, reference-doc coverage, root-whitelist enforcement, runtime-artefact sweep, the commands↔skills pairing in all three legal patterns, and consistency between documented build commands and the coded never-shipped design.
- **Layer 2** — per-skill graders. Each skill ships its own `scripts/grade.py` encoding the skill's own contract. Counts drift as skills iterate; the binding number is always whatever the grader script actually asserts.
- **Layer 3** — an unprimed audit subagent. It sees only the delta and reports `SHIP` or `HOLD` with named defects. Blind spots the assertion set didn't know to look for surface here; the next iteration either fixes them in place or promotes them into a new Layer 1 or Layer 2 assertion. Layer 3 is not in the CI, on purpose — it needs a reasoning model, not a deterministic check.

The loop closes only when all three layers pass in a single complete pass. The CI at [`.github/workflows/plugin-check.yml`](.github/workflows/plugin-check.yml) runs Layers 1 and 2 on every push and PR to `main`.

### Skill-creator-first

Every creation or content change of a skill goes through Anthropic's official `skill-creator` skill, without exception. Direct edits to `SKILL.md` without `skill-creator` are a plugin-standard violation, even when a user (or a future Claude instance) asks for a shortcut. The rule refuses shortcuts specifically because the failure mode it prevents — ad-hoc skill edits that pass smell-tests but miss trigger signals or negative scope — was the shape of the majority of bugs we saw in the 0.3.x series.

---

## Why this is public

The skills themselves are utilities. They save real time in real workflows. But the reason the repository is open is the governance model above, and particularly the two moves inside it that we keep finding portable:

- Making **Ground-Before-Discuss** a first-class contractual rule rather than a habit, with visible enforcement (real tool calls, not narration).
- Making the **unprimed-audit role** explicit and distinct from the structural and per-contract checks, so that blind spots can surface from a position that doesn't share the change's context.

Each of these started as a specific failure and was promoted into a standard only after it proved load-bearing across multiple cycles. The history lives in [`plugin/CHANGELOG.md`](plugin/CHANGELOG.md) — the versioning rule (`fix` auto-increments on every change, no matter how small) means the changelog is also the log of how the standard evolved.

The method is portable to other plugins and, we think, to other kinds of structured judgment work.

---

## Contributing

See [`plugin/CONTRIBUTING.md`](plugin/CONTRIBUTING.md) for the full contribution procedure, including the three-layer loop contributors are expected to run locally. Issues, pull requests, and pointed criticism are welcome.

---

## Security

See [`SECURITY.md`](SECURITY.md) for the vulnerability disclosure policy.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).

## Author

[NeoMINT GmbH](https://neomint.com)
