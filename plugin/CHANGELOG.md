# Changelog

All notable changes to the NeoMINT Toolkit are documented here.
The most recent change is always at the top.

Format: `major.minor.fix`
- **major** — incremented only on explicit user instruction
- **minor** — incremented only on explicit user instruction
- **fix** — incremented automatically for every change

---

## 0.4.9 — 2026-04-21

- Repository restructure: plugin sources moved from the repo root into a
  dedicated `plugin/` subdirectory, and the repository gains its own
  top-level `README.md` distinct from the plugin's. The motivation: the
  repo is both a shipping vehicle for the plugin and a record of the
  governance research that produced it. Those two audiences want
  different entry points. The repo-level README introduces the research
  angle (Ground-Before-Discuss, three-layer iteration loop,
  unprimed-audit workflow) and points at `plugin/` for the shipping
  artefact. The plugin's own README is untouched in substance — it still
  documents install, skills, and plugin standards — but its build
  command now runs from inside `plugin/` instead of from the repo root.
  `LICENSE` and `SECURITY.md` live both at the repo root (for GitHub
  discovery) and inside `plugin/` (so the `.plugin` bundle remains
  Apache-2.0 §4-compliant for redistribution). The CI workflow at
  `.github/workflows/plugin-check.yml` now invokes `plugin-check.py`
  with `plugin` as the explicit root argument; per-skill graders are
  addressed via `plugin/skills/…` paths.

---

## 0.4.8 — 2026-04-21

- `council` skill: turn-gated live deliberation. Previously the Council
  could render the entire five-phase judgment as a single wall-of-text
  assistant message, which made the deliberation impossible to follow
  live, impossible to interrupt at a specific role, and trivial to
  shortcut under token pressure. The user's observation — "der user
  muss die Diskussion live mitverfolgen können … wie einem council
  wirklich zuzuhören" — identified this as the core defect that
  remained after 0.4.7. The fix reshapes the skill around a one-phase-
  per-assistant-message contract:
  - **Turn map.** FULL now runs as eight turns (T1 ORIENT · T2 GROUND ·
    T3 CARTOGRAPHER · T4 ANALYST · T5 ADVERSARY · T6 SCOUT · T7 OPERATOR
    · T8 VERDICT). QUICK compresses to three turns. AUDIT uses FULL as
    a baseline and the Chairman may insert DEEPEN turns on the fly;
    K grows visibly, never silently.
  - **Sentinel contract.** Every phase message ends with exactly
    `=== TURN <N>/<K> COMPLETE — <PHASE NAME> ===` followed by an
    AWAITING-USER line listing the accepted continuation tokens
    (`NEXT`, `REBUTTAL`, `DEEPEN`, `BRANCH`, `ABORT`). The sentinel is
    the hard stop — content after it is a contract violation. This is
    the structural fix to the Claude-Code multi-phase-workflow failure
    mode documented in `anthropics/claude-code` issue #21672.
  - **Role turn micro-format.** Each role turn opens with an Axis
    line, a one-sentence Thesis, a hardest-first Finding, a mandatory
    Cross-reference (from T4 onward: a direct quote from a prior role),
    a mandatory Dissent or reasoned concurrence, and a Resolvable? line.
    The micro-format forces the turns to compound instead of staying
    five parallel essays, and gives the grader structural anchors.
  - **Visible tool calls in GROUND.** T2 requires at least one real
    `WebSearch` / `WebFetch` invocation when web access is available.
    Narrating "I searched for X" without the actual tool call is a
    contract violation — the user must see the grounding was performed,
    not asserted.
  - **Chairman citation rule.** T8 VERDICT now contains a mandatory
    `## Citations` block with a short direct quote from each of T3–T7,
    attributed by turn number. The Chairman adds no new findings under
    its own voice — if a gap is visible, a DEEPEN turn is inserted
    instead. This is how the Chairman visibly *listens* rather than
    summarising.
  - **References.** `references/turns.md` added as the single source of
    truth for the live-turn contract, including exact sentinel format,
    continuation-token semantics, role-turn micro-format, worked FULL
    and QUICK examples, and anti-shortcut enforcement. `references/
    phases.md` rewritten with turn-numbered section headers (T1..T8).
  - **Layer 2 grader.** `skills/council/scripts/grade.py` extended from
    20 to 33 assertions, all enforcing the new contract: turn-gated
    section present, sentinel template exact, continuation tokens
    present, role micro-format markers present, Chairman citation
    block present, turn counts declared (FULL=8, QUICK=3), NO-DOWNGRADE
    for K declared, `turns.md` exists with worked examples and
    references #21672, anti-pattern "two phases in one message" called
    out, turn-header template exact, `references/phases.md` carries
    T1..T8 labels. Two legacy assertions (Persistence line format,
    phase-block ordering) were updated to accept the new turn-numbered
    form without loosening their intent.
  - **Layer 3 finding → Layer 2 assertion (self-optimisation).** The
    first 0.4.8 audit pass returned `HOLD` on one MEDIUM: the 32-
    assertion grader had locked the *phase-numbering convention* in
    `SKILL.md` and `phases.md` but did not scan the other reference
    files. `references/persistence.md` still used "Phase 0" / "Phase 3"
    from the pre-0.4.8 shape in three places, and `references/ground.md`
    had "Phase 1" in its title — both would have decoupled the reference
    corpus from the skill body without any grader firing. Fix was
    twofold: correct the four stale labels, and add assertion #33 — a
    stale-phase scanner that forbids `Phase 0`..`Phase 4` across
    `SKILL.md` and every `references/*.md`, with an escape hatch
    (nearby "old" / "legacy" / "previous" / "pre-0.4.8" prose) for
    intentional historical references. A negative test (injecting
    `Phase 0` into persistence.md with no qualifier) confirms the new
    assertion fires. Total: 33/33 PASS.
  - **Description rewrite.** The YAML folded-scalar description now
    names the live-turn contract explicitly — "delivered turn by turn
    — one phase per message, ending in a sentinel so the user can
    follow and intervene" — so the trigger signals include the
    deliberation shape, not just the role roster. The full phrase
    "turn-gated live deliberation" remains in the body heading at
    line 21. The description has been trimmed to stay under the
    1024-char hard limit (995 chars).
- No changes to `pdf-umbenennen` or `neomint-plugin-entwicklung` in this
  cycle. The governance skill's Step 2 exception does **not** apply here
  — this is a content change of a skill, so `skill-creator` was used for
  the redesign.

---

## 0.4.7 — 2026-04-21

- `SECURITY.md`: security-report contact changed from the placeholder
  `security@neomint.com` to `info@neomint.com`. A short explanatory
  sentence was added so readers understand the general mailbox is the
  monitored destination and that no dedicated security alias exists.
  No other behaviour changes; per the governance skill's Step 2
  exception, this is a pure metadata change and does not require the
  `skill-creator` workflow.

---

## 0.4.6 — 2026-04-21

- Repository-publication layer added so the plugin can ship as the public
  `neomint-research/claude-neomint-plugin` repository on GitHub.
  - New root files: `LICENSE` (Apache 2.0), `SECURITY.md`, `CONTRIBUTING.md`,
    `.gitignore`.
  - New `.github/` scaffolding: `workflows/plugin-check.yml` runs Layer 1
    and every per-skill grader on every PR and push to `main`; PR template
    enforces the governance checklist; three issue templates (bug, skill
    proposal, standard update).
- `README.md` rewritten for GitHub-first reading: install block at the top,
  Open Research positioning, explicit link to `CONTRIBUTING.md`. Plugin
  standards section preserved verbatim — it is the substance.
- Layer 1 (`plugin-check.py`) updated so the new root files don't register
  as stray, and so `.github/` and `CONTRIBUTING.md` are explicitly excluded
  from the shipping archive's allowed top-level set. `LICENSE` and
  `SECURITY.md` DO ship — users of the `.plugin` bundle see the license
  and the security policy without needing the repo.
- No content changes to any skill. `skill-creator` was therefore not
  required for this cycle (repackage-and-publication-only change). The
  governance skill's Step 2 exception applies.
- **Layer 3 finding → Layer 1 assertion.** The first 0.4.6 audit pass
  returned `HOLD`: the documented build commands in `README.md` and
  `CONTRIBUTING.md` excluded `LICENSE` and `SECURITY.md` via `-x`, even
  though the `never_shipped` design requires those files to ship inside
  the `.plugin` bundle. Layer 1's archive-cleanliness check only
  catches *extra* content, not *missing* content, so it would have
  false-PASSed. Fix was twofold: correct both build commands, and add
  two new Layer 1 assertions per documentation file — "build cmd does
  not exclude shipped root files" and "build cmd excludes every
  never-shipped root file" — using `fnmatch` so zip globs like
  `*.git*` match `.gitignore` correctly. A negative test confirms the
  new assertions fire on the exact defect pattern. Layer 1 now totals
  51 checks (up from 47); post-fix: 51/51 PASS.
- CI workflow (`.github/workflows/plugin-check.yml`) tightened: the
  `if: always()` flag was removed from Layer 2 grader steps so the
  pipeline fails fast on Layer 1 failure rather than reporting mixed
  signals. Comment added explaining the design choice.
- `CONTRIBUTING.md` license clause clarified: "submitting" is defined
  as PR, patch on an issue, or code posted in a discussion; inbound-
  equals-outbound Apache 2.0 explicitly named.
- **Canonical archive rule tightened.** While preparing the repo for
  publication, a stray `test-neomint-toolkit.plugin` from an earlier
  session was found at the plugin root. The old "No stray files at
  plugin root" rule tolerated *any* file ending in `.plugin`, and the
  "Shipping archive contents are clean" rule picked `plugins[-1]`
  alphabetically — so with two archives present, the wrong one was
  being validated. Now: only `<plugin-name>.plugin` (read from
  `plugin.json`) is permitted at the root, and the archive-cleanliness
  check targets that canonical name specifically. Negative test
  confirms the tightened rule catches the stray-archive case.

---

## 0.4.5 — 2026-04-21

- Three self-optimisation upgrades from the 0.4.4 cycle, each addressing a manual call that should have been a standard.
- **Ground-Before-Discuss** named as a plugin-wide standard in README. Both the governance skill's Step 0 pre-research (Anthropic GitHub first, Community second) and the council skill's new Phase 1 GROUND (Hersteller first, Community second) already follow this shape; the README now names the shared principle so the parallel is visible and future skills inherit it. Silent omission of either source is a contract violation; if a source doesn't exist or isn't reachable, the absence is stated as a finding.
- **Layer 1 validates the shipping archive.** `plugin-check.py` gains a new assertion *Shipping archive contents are clean* that opens the `*.plugin` at the plugin root and verifies its top-level entries are a subset of the root whitelist. Catches the 0.4.4 failure automatically — zipping from the wrong directory, snapshot folders leaking into the archive, stray build trees. Skipped when no `.plugin` exists at the root.
- **Step 4 of the governance skill gains an explicit warning block** about zipping from a clean source copy rather than from `/tmp` itself, including the concrete failure mode: `cd /tmp && zip -r ….plugin .` silently packs every sibling folder in `/tmp` into the archive. The warning references today's Layer 1 assertion as the safety net — but the discipline is to get it right the first time. Also names the `zip -r` append-to-existing-archive trap (delete the target `.plugin` before running zip).
- Layer 1 + Layer 2 dogfood on this release: 47 PASS, 0 FAIL, 0 SKIP (one more assertion than 0.4.4's 46 — the new archive-contents check).

## 0.4.4 — 2026-04-21

- Council skill gains a mandatory **GROUND** phase between ORIENT and MAP. The user's principle: "Der erste Schritt muss immer sein: Was sagt der Hersteller. Der zweite: Was sagt die Community. Erst das wird diskutiert." Before any of the five roles speaks, two sources must be on the table — the authoritative / first-party position (Hersteller: vendor docs, RFC, ISO, primary law, repo's own ADR) and the practitioner consensus (Community: Stack Overflow, forums, maintainer blogs, peer analyses). Divergence between the two is a first-class finding, not a footnote.
- Phase count grows 4 → 5: **ORIENT → GROUND → MAP → COUNCIL → VERDICT**. MAP's input now includes the GROUND block; the four judging roles each see it in their starting context; the Chairman's MECE check now gates on grounding completeness before publication.
- New reference `skills/council/references/ground.md` — what counts as a Hersteller source by question type (vendor docs / RFC / primary law / guideline body / repo ADR), what counts as a Community source (practitioner forums, issue trackers, peer analyses, the repo's own commit history), how to handle divergence (three named patterns: Hersteller-conservative/Community-pragmatic, Hersteller-current/Community-stale, Hersteller-silent/Community-de-facto-standard), depth scaling per QUICK/FULL/AUDIT, and the handoff format to the Cartographer. Keeps SKILL.md under the 500-line ideal via progressive disclosure.
- New rigor duty **GROUND-FIRST** in SKILL.md — named and binding. "No role speaks before both the Hersteller position and the Community position are on the table." Covers both fallbacks: no Hersteller exists (novel / subjective / cross-domain question) → named as such, not skipped; Community unreachable (no web access) → fall back to trained knowledge with cutoff, stated. Silent omission of either source is a contract violation.
- Output template gains a `## Grounding` block with three lines (Manufacturer / Community / Divergence) placed *before* the role findings — a verdict whose grounding slot is empty is structurally an opinion, not a Council finding. Anti-patterns updated accordingly, including a new entry for ungrounded Councils.
- Iteration handles (REBUTTAL / DEEPEN / BRANCH) extended: REBUTTAL citing a new Hersteller or Community source triggers a re-entry to Phase 1 before the role re-runs; DEEPEN can now target a specific grounding question, not only a role or point.
- `skills/council/scripts/grade.py` grows 13 → 17 contract checks: new phase list includes `ground`, `references/ground.md` must exist on disk, both `Hersteller` and `Community` must appear in SKILL.md, `GROUND-FIRST` rigor duty must be named, `## Grounding` + `Manufacturer (Hersteller)` must appear in the output template, and a structural ordering check enforces `ORIENT → GROUND → MAP → COUNCIL → VERDICT` — GROUND cannot silently drift to become an appendix.
- No changes to `plugin-check.py` required — the Layer 1 char-limit assertion added in 0.4.3 covers the slightly longer SKILL.md by default, and the new reference file is picked up automatically by the existing `references/X.md` resolver.

## 0.4.3 — 2026-04-21

- Root cause of the user-reported "council is not recognised when I ask about the plugin" regression traced to the council skill description in 0.4.0–0.4.2: at 1382 characters it sat well over Anthropic's 1024-char hard truncation limit, so Claude only ever saw a clipped fragment. The failure was silent — nothing in Layer 1 flagged it.
- Council description rewritten via the skill-creator description-optimisation loop. `claude -p` was not authenticated inside the sandbox, so the iteration loop was rebuilt manually: 5 new candidate descriptions generated in parallel via subagents, then each graded by a fresh subagent playing Claude's skill-selection mechanism across the 20-query eval set (12 train / 8 test), 3 independent judgments per query. All 5 new candidates saturated at 20/20; the winner was chosen on principled tiebreakers — imperative user-intent framing, distinctive opener ("You're too close to it.") matching the skill's soul, trigger-word density across decision/validation/risk/completeness/strategic phrasings, and headroom under the char limit. Final description: 883 characters. Eval candidates, eval set, and grading results preserved under `/sessions/clever-kind-mayer/council-desc-opt/`.
- New standing principle encoded into the council SKILL.md body: **"Reicht" ist niemals akzeptabel** — a Council verdict never stops at "sufficient" or "acceptable risk" without naming the uncertainty. Stop only when sure, or explicitly name *what would need to become true* for the Council to be sure. "3/5 roles converge, 2/5 inconclusive" is a status report, not a verdict. The principle is written into three load-bearing sections: **Rigor duties** (new VERDICT COMPLETENESS paragraph), **Stopping criteria** (rule #2 strengthened, plus the explicit "Reicht is not a valid terminator" line), and **MECE as active Chairman function** (rule #3 now requires naming the resolution path).
- `skills/council/scripts/grade.py` gains three new contract checks (10 → 13): description rendered length ≤ 1024 chars, the phrases "stop only when sure" and "what would need to become true" present in SKILL.md, and the "3/5 … status report" anti-pattern framing present. These survive future edits — the principle cannot silently decay.
- `skills/neomint-plugin-entwicklung/scripts/plugin-check.py` Layer 1 gains a per-skill assertion: **every** skill's description must fold to ≤ 1024 chars. The 0.4.2 failure mode could have been caught automatically — now it will be.
- Iteration loop this release: Layer 1 + Layer 2 green, plus an independent description regression trace (the silent-truncation bug) resolved. Dogfood count is kept honest by the new Layer 1 char-limit assertion.

## 0.4.2 — 2026-04-21

- Layer 2 of the three-layer iteration loop is now active for every skill. Each skill ships a `scripts/grade.py` contract grader that runs under `plugin-check.py` and returns non-zero on a contract regression:
  - `skills/council/scripts/grade.py` — 10 contract checks: five MECE roles + Chairman named, four phases, three depth modes, three contexts, two-track output, mandatory `Persistence:` line, `Mode: DIAGNOSTIC` header, required sections, references on disk.
  - `skills/pdf-umbenennen/scripts/grade.py` — filename convention, at least three matching examples, umlaut rules, sender short-name categories (Companies/Banks/Persons/Unknown — the categories whose truncation shipped in 0.4.0), subject short-form section, parallel-batch performance contract.
  - `skills/neomint-plugin-entwicklung/scripts/grade.py` — required sections, skill-creator requirement, three layers named, grader script and reference doc bundled, pre-research step, versioning scheme, build-in-`/tmp` rule, self-optimisation step, `plugin-check.py` compiles.
- Writing the council grader immediately caught a latent case-sensitivity assumption (phases appear as `MAP`, `COUNCIL`, `VERDICT` inside a code fence, not in sentence case). The grader was corrected before shipping; the learning is that contract graders must match the form SKILL.md actually uses, not the form the designer intended.
- Layer 1 + Layer 2 dogfood on this release: **43 PASS, 0 FAIL, 0 SKIP**. The 3 previously-SKIPped per-skill eval slots now run real graders.
- New named standard in README: **Build artefacts.** Transient artefacts — intermediate zips, source trees, grader reports, cache folders — go to `/tmp`. Only the canonical `.plugin` shipping archive is permitted at the plugin root. Rule encoded in Layer 1's root-whitelist and reinforced as a block quote at the top of Step 4 in the governance skill. Captures the lesson from 0.3.x–0.4.0 where `.mcpb-cache/` and a stray `zimjorit` archive were shipped inside the plugin.

## 0.4.1 — 2026-04-21

- Governance skill `neomint-plugin-entwicklung` gains a proper plugin-level iteration loop, analogous to skill-creator but at plugin scope.
  - New Step 5 is a three-layer loop: Layer 1 structural checks (runnable), Layer 2 per-skill evals (orchestrated), Layer 3 independent audit subagent (unprimed reasoning pass). The loop closes only when all three layers pass in one complete pass.
  - New `scripts/plugin-check.py` — bundled runnable grader implementing Layer 1 + Layer 2 orchestration. Covers plugin.json validity and completeness, version format, CHANGELOG↔plugin.json consistency, README and SKILL.md mid-sentence truncation heuristic, `_shared` files, stray files at plugin root (whitelist), YAML frontmatter per SKILL.md, Language+Environment blocks per SKILL.md, `references/X.md` resolution (prose-only, ignores backticked placeholders), README↔skills coverage (no missing or ghost skills).
  - New `references/plugin-eval.md` — detailed mechanics of the three layers, how to add Layer 1 assertions, why Layer 3 cannot be replaced by a script.
- Fixed mid-sentence truncation in `skills/pdf-umbenennen/SKILL.md` (section "Sender — short-name rules" stopped at "Companies: short"). Section now completes the sender rules and adds the missing Subject short-form rules. Silent bug caught by the new Layer 1 assertion on its first run.
- `.mcpb-cache/` and stray `zimjorit` archive removed from the plugin root — both were leftover build artefacts that the new root-whitelist check flagged immediately.

## 0.4.0 — 2026-04-21

- New skill `council`: context-aware judgment system with five MECE roles (Analyst, Cartographer, Adversary, Scout, Operator) and a Chairman synthesis. Four structured phases (Orient, Map, Council, Verdict), three depth modes (QUICK, FULL, AUDIT), three environment modes (CODE, DOC, CHAT). Produces a two-track output (operative + management) with visible role attribution. Maintains `COUNCIL.md` persistence at the repo root (Claude Code), user-selected folder (Cowork), or as a downloadable artifact (Web) so follow-up runs are structurally cheaper than the first.
- Reference split: `skills/council/references/roles.md`, `phases.md`, `persistence.md` — progressive disclosure keeps the main SKILL.md under 500 lines.
- Iteration loop run on `council` (skill-creator workflow): 4 test cases × 2 configs (with-skill vs baseline) × 2 iterations. Iteration-2 with-skill result: 34/34 assertions pass (100%); baseline without-skill: 8/34 (24%). Iter-1 → iter-2 edits to SKILL.md: (a) output template gained a mandatory `Persistence:` line so `COUNCIL.md` is never silently skipped; (b) diagnostic-question standard now requires `Mode: DIAGNOSTIC   Context: <…>` as the first line, so branching away from the full Council is visible. Eval report under `skills/council/evals/ITERATION_REPORT.md`.
- `.claude-plugin/plugin.json` rebuilt: the previous file was truncated and invalid JSON. Now complete with all keywords and a valid schema.
- `README.md` rebuilt: the previous file was truncated mid-sentence. Now complete with all three skills documented, full plugin standards section, and the "Adding a new skill" process.
- Governance skill (`neomint-plugin-entwicklung`) improvements triggered by this release:
  - Step 2: documents the correct skill-creator invocation (the `Skill` tool with `skill: "skill-creator"`, not Bash or manual Read).
  - Step 4: changes the packaging workflow to build the zip in `/tmp` and copy into the workspace folder — avoids atomic-rename failures on mounted folders, and adds a `plugin.json` validity check of the archive contents.
  - Step 5a: adds two integrity checks — `plugin.json` must parse as valid JSON, and `README.md` must not end mid-sentence.
- `SKILL_TEMPLATE.md` expanded: the `## Additional references` section now documents when to split SKILL.md into `references/<topic>.md` (Progressive Disclosure pattern, trigger at ~400 lines or multiple independent sub-domains).
- Minor version bumped on explicit user instruction (new standalone skill of significant scope plus governance standard upgrades).

## 0.3.1 — 2026-04-21

- Added `CHANGELOG.md` with versioning scheme documentation
- Versioning rules documented in README and governance skill

## 0.3.0 — 2026-04-21

- Full English translation of all plugin content (README, plugin.json, SKILL_TEMPLATE, all skill SKILL.md files, _shared files)
- New `skills/_shared/language.md` — configurable output language, default: user's language
- Output language rules added to Plugin Standards in README
- Governance skill updated: Language block check added to Step 3 quality checklist, `language.md` added to plugin structure reference

## 0.2.0 — 2026-04-21

- Second skill `neomint-plugin-entwicklung` (governance): enforces skill-creator requirement, mandatory pre-research (Anthropic GitHub + community), iterative consistency check loop, self-optimisation after every change
- Plugin standards documented in README
- Environment compatibility for all three Claude platforms (Claude Code, Cowork, Claude AI Web)
- New `skills/_shared/environments.md` — single source of truth for environment detection logic
- New `SKILL_TEMPLATE.md` — starting point for new skills with all required blocks pre-defined

## 0.1.0 — 2026-04-21

- Initial plugin recovery and repackaging
- Skill `pdf-umbenennen`: automatically renames scanned PDFs based on document content (date, sender, subject)
- Author changed to NeoMINT GmbH
- Sensitive examples removed from skill
