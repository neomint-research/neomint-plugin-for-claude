# Plugin-level iteration loop — mechanics

This skill owns the plugin-level analogue of the skill-creator's test-and-
improve loop. Where skill-creator grades a single SKILL.md against prompts,
this loop grades the *plugin as a whole* across three independent layers.

The loop is not optional. Every plugin change — new skill, modified skill,
changed standard — runs through all three layers until they all close in
one complete pass.

---

## Layer 1 — Structural (runnable, deterministic)

Owner: `scripts/plugin-check.py` inside this skill.

The script takes the plugin root and runs deterministic assertions. These
must all pass before proceeding:

- `plugin.json` exists, parses as JSON, carries `name`, `version`,
  `description`, `author`.
- `version` matches `major.minor.fix`.
- CHANGELOG top entry's version matches `plugin.json` version.
- README exists and is not mid-sentence truncated (last non-empty line
  ends with terminal punctuation, a closing bracket, a URL, a fenced
  code block, or a section boundary).
- SKILL_TEMPLATE.md exists.
- `skills/_shared/language.md` and `skills/_shared/environments.md` exist.
- No stray files at the plugin root. Whitelist: `.claude-plugin/`,
  `skills/`, `commands/`, `README.md`, `CHANGELOG.md`,
  `SKILL_TEMPLATE.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`,
  `.github/`, `.gitignore`, `.git/`. **No `*.plugin` archives are
  permitted at the plugin root** — shipping artefacts live in
  `/tmp/<plugin-name>-workspace/` and are distributed via GitHub
  Releases (or equivalent), never committed.
- No runtime artefacts anywhere inside the plugin tree or one level up
  at the repo root: `*.plugin`, `*-workspace/`, `iteration-workspace/`,
  `skill-snapshot/`, `eval-viewer-iter*.html`, `COUNCIL.md`. These are
  outputs of the iteration loop and belong in `/tmp/<plugin-name>-workspace/`.
- Every skill directory under `skills/` (excluding `_shared`) has a
  `SKILL.md` with valid YAML frontmatter carrying `name` and
  `description`, and the file is not mid-sentence truncated.
- Every skill references `_shared/language.md` and
  `_shared/environments.md`.
- Every skill's SKILL.md has `## Language` and `## Environment detection`
  as dedicated section headings (not just inline prose). Rationale: a bare
  `Read ../_shared/language.md` line in the body satisfies the reference
  check but is invisible to progressive-disclosure tooling and human
  reviewers who scan for section headings. The heading is the structural
  contract; the reference inside it is the runtime instruction. Requiring
  both is the conservative choice that prevents the two from drifting apart.
  Promoted to a Layer 1 assertion in 0.6.11 after a Layer 3 audit found
  a new skill satisfying the reference check but missing the heading.
- Every file referenced as `references/X.md` inside a SKILL.md actually
  exists on disk.
- README mentions every skill present on disk.
- README does not mention ghost-skills (names that look like skills but
  don't exist on disk).

Run:

```
python3 skills/update-plugin/scripts/plugin-check.py <plugin-root>
```

The script exits 0 if all Layer 1 assertions pass, 1 otherwise. A JSON
report is written to `/tmp/plugin-check-report.json`.

---

## Layer 2 — Per-skill evals

The skill-creator iteration loop runs at skill granularity — each skill
has (or should have) its own eval suite. Layer 2 is the plugin asking:
"did every skill's own eval loop close?"

The plugin-check script looks for a per-skill grader at either:

- `skills/<name>/scripts/grade.py`
- `skills/<name>/evals/grade.py`

If found, it runs the script (120 s timeout) and records PASS/FAIL based
on exit code. If neither exists, Layer 2 records SKIP for that skill —
informational only, not a failure.

Adding a grader for a skill is the recommended path after the first
skill-creator iteration. Once the script exists, every future plugin
change re-runs it for free.

---

## Layer 3 — Independent audit subagent

Owner: the governance skill running inside a Claude session. Not a
script — this requires a reasoning agent.

### The audit brief

The subagent is unprimed: it sees no context about what changed or
why. It reads the current state of the repository and reports real
defects. The brief below is the reproducible contract — use it
verbatim (substituting the repo path) so findings are comparable
across runs and across reviewers. It was codified in 0.6.1 after the
ad-hoc 0.6.0 brief produced good findings but could not be replayed
deterministically.

Seven categories the subagent must check:

1. **Forward-facing references to non-existent skills, paths, or
   commands.** Every referenced skill must exist at
   `plugin/skills/<name>/SKILL.md`; every referenced command at
   `plugin/commands/<name>.md`; every referenced script path must
   resolve. Grep the entire repo — `.github/`, root `README.md`,
   `plugin/README.md`, `plugin/CONTRIBUTING.md`,
   `plugin/SKILL_TEMPLATE.md`, every SKILL.md, every command .md,
   every script, every workflow.
2. **Cross-document consistency.** The three invocation patterns
   (Auto-only / Command-only / Auto+Command) must agree across
   `plugin/README.md`, `plugin/SKILL_TEMPLATE.md`,
   `plugin/skills/update-plugin/SKILL.md`, and the actual skill
   frontmatters.
3. **Version consistency.** `plugin/.claude-plugin/plugin.json`, the
   top entry of `plugin/CHANGELOG.md`, and the version reference in
   `plugin/README.md` must all agree.
4. **CI workflows reference files that exist.** Every path under
   `.github/workflows/*.yml`.
5. **Delivery end-to-end.** This is a cross-artefact axis: the
   delivery story is only correct when docs, Layer 1, CHANGELOG, and
   the archive-on-disk all agree simultaneously. Promoted from a
   one-line "distribution story coherence" bullet in 0.6.2 after that
   cycle demonstrated a single delivery change can touch all four
   surfaces at once. The subagent must walk the end-to-end path and
   answer each of these explicitly:
   - Does `plugin/skills/update-plugin/SKILL.md` Step 4 document a
     build recipe whose output location is openable for the user in
     the environment currently in scope (typically `/tmp` or
     `dist/`)?
   - Does the documented fallback path (`dist/<plugin-name>.plugin`)
     match what Layer 1's `dist/` allowlist actually permits? If
     SKILL.md says `dist/` is legal but Layer 1 rejects it, that is a
     contradiction even if both individually "pass".
   - Does `.gitignore` cover `*.plugin` in a way that prevents the
     staged copy from landing in a commit? Scoped patterns like
     `dist/*.plugin` are explicitly *not* sufficient — repo-wide
     coverage only.
   - Does the top CHANGELOG entry mention delivery if delivery
     changed, with the same terminology the docs use (same
     directory name, same fallback semantics)?
   - If a `dist/*.plugin` is staged, does its `plugin.json.version`
     match the repo's `plugin.json.version`? A version drift between
     repo and archive is a shipped-defect waiting to happen.
   - Is `dist/` described consistently as a *transition zone* (not a
     permanent home, not tracked in git), or does any doc imply a
     different lifecycle?
   - Does Layer 1's `--strict-release` flag (added 0.6.4) get
     mentioned wherever the lifecycle is documented (SKILL.md Step 4,
     CHANGELOG, the release CI workflow), and does CI actually use it
     on tag pushes? The flag is the deterministic enforcement of "no
     stale archive in `dist/` at release time"; if it exists in code
     but no doc points to it and no CI step invokes it, the
     enforcement is theoretical and the lifecycle is back to "trust
     the developer". Cross-reference verified by grepping for
     `--strict-release` in `plugin/skills/update-plugin/SKILL.md`,
     `plugin/CHANGELOG.md`, and `.github/workflows/release.yml`.
   This category deliberately overlaps with Layer 1 — the point is
   that the same fact is checked from a different angle, so a crack
   between "the assertion fires" and "the docs describe what the
   assertion enforces" becomes visible.
6. **Pattern conformance.** Every skill with
   `disable-model-invocation: true` must also have
   `user-invocable: true` (the slash command is unreachable
   otherwise).
7. **File truncation.** For every top-level prose doc (root
   README.md, plugin/README.md, plugin/CHANGELOG.md,
   plugin/CONTRIBUTING.md, every SKILL.md, every command .md), the
   last few bytes must be a complete sentence with closing
   punctuation. The subagent uses `tail -c 200 <path>` to verify —
   the Read tool alone can combine lines visually and miss
   truncation.

For each finding the subagent reports: severity (BLOCKER / MAJOR /
MINOR), file + line, the offending quote, and one sentence of
rationale. It ends with a single verdict line: **VERDICT: SHIP** if
no BLOCKER or MAJOR findings; **VERDICT: HOLD** otherwise. The
report stays under 500 words.

### Triage

1. Collect the subagent's findings.
2. Cross-check against the Layer 1 report:
   - Findings the script already caught → confirmation that both
     signals agree.
   - Findings the script missed → candidate new Layer 1 assertions.
     The Step 5e self-optimisation proposal should name these.
   - Script-only findings → the subagent may have missed something
     the script caught (tolerate; deterministic checks don't need the
     subagent's approval).
3. Triage real issues vs. false positives. Fix the real issues in
   the same cycle.

The audit subagent is intentionally unprimed. The point is to catch
blind spots that the assertion set doesn't know to look for — the
same reason skill-creator runs a baseline "without-skill" subagent.
The codified seven-category brief exists to make the *coverage*
reproducible; the *findings* within each category are still the
subagent's own judgment.

---

## The loop

```
do:
    run Layer 1 (plugin-check.py)
    run Layer 2 (per-skill graders picked up automatically)
    run Layer 3 (audit subagent)
    if any layer has real failures:
        fix them
        continue
    else:
        loop closes
```

The loop closes only when a single complete pass has zero real
failures across all three layers.

---

## Adding a new Layer 1 assertion

When a plugin change surfaces a gap the script didn't catch:

1. Add the check as a new line in `run_layer1()` of
   `scripts/plugin-check.py`.
2. Give it a clear name (the string shown in the output).
3. Re-run the script — the new check should PASS on the fixed plugin
   and would have FAILED on the state the change was fixing.
4. Note the addition in the Step 5e self-optimisation proposal so the
   user sees the standard has grown.

### Defect-injection verification — use a tempdir, never git checkout

A new assertion is only credible if you can show it FAILs on the
defect it claims to catch. The honest way to verify is to inject the
defect, run the check, observe FAIL, then revert. **Never** revert
via `git checkout` on the source tree — if the change being released
is uncommitted, the checkout silently destroys the in-flight work.
This rule is here because the 0.6.1 cycle nearly lost an entire
release that way; the release survived only because the conversation
context retained enough to rebuild the deleted CHANGELOG entries by
hand.

The safe pattern:

```bash
# 1. Copy the plugin tree to a scratch location
cp -r plugin/ /tmp/inject-test/

# 2. Inject the defect inside the copy
python3 -c "from pathlib import Path; p = Path('/tmp/inject-test/CHANGELOG.md'); p.write_text(p.read_text().rstrip().rstrip('.') + ' th')"

# 3. Run plugin-check against the copy — it should FAIL on your new check
python3 plugin/skills/update-plugin/scripts/plugin-check.py /tmp/inject-test

# 4. Throw the copy away
rm -rf /tmp/inject-test
```

The source tree is never touched. No git operation is required.
Verification is reproducible across machines because it doesn't
depend on what is or isn't committed.

---

## Assertion schema — eval_metadata.json

Per-skill graders (Layer 2) and ad-hoc structural checks written during
a skill-creator iteration must produce an `eval_metadata.json` per run
using the schema below. The schema is deliberately narrow: one grammar,
one grader, no dialects.

### Top-level fields

```json
{
  "eval_id": 0,
  "eval_name": "slug",
  "variant": "with_skill" | "old_skill" | "without_skill" | "new_skill",
  "status": "ready_for_grading",
  "shape_under_test": "short-name",
  "note": "optional — context the grader cannot derive",
  "assertions": [ ... ]
}
```

`variant` names are free-form but must match the subdirectory name
under `eval-N/` (the aggregator discovers config names dynamically).

### Assertion types

Every assertion has an `id`, a `type`, a `target` (file path relative
to the run dir, e.g. `outputs/transcript.md`), and a `rationale`
(one sentence explaining what failure the check is designed to catch).

| `type` | Required fields | Semantics |
|---|---|---|
| `regex_absent` | `pattern` | Fails if the pattern matches anywhere in `target`. Use for forbidden shapes. |
| `regex_all` | `patterns` (list) | Fails if any one pattern is missing. Use for required landmarks. |
| `regex_count` | `pattern`, `expected_min` and/or `expected_max` | Fails if match count is outside the band. Use for "at least once" or "exactly once" constraints. |
| `regex_any` | `patterns` (list) | Fails if none of the patterns match. Use when there are multiple acceptable vocabularies. |
| `file_exists` | (none) | Passes if `target` exists. Use to prove a side effect happened (file was written). |

All regex checks are case-insensitive. Use `(a|b|c)` alternation to
accept vocabulary variation instead of forcing one specific wording.

### Legacy aliases (tolerated)

Older metadata may use `check_type` instead of `type` and
`target_file` instead of `target`. The grader accepts both, but new
metadata must use the canonical field names. A `check_type` of
`"regex"` is treated as `regex_any` with a single pattern.

### Why this matters

Without a common schema, each iteration invents its own grammar and
graders become one-off scripts. With this schema, one grader script
runs across all skills and all iterations, and the assertion set
becomes a reusable library — which is what makes the loop sustainable
instead of one-shot work.

---

## Slash-command / SKILL.md pairing — frontmatter contract

For an explicit-invocation skill (one paired with a `commands/<name>.md`
entry), the SKILL.md must carry both flags:

```yaml
disable-model-invocation: true
user-invocable: true
```

`disable-model-invocation: true` alone is not sufficient in current
Claude Code. Upstream issues
[anthropics/claude-code#26251](https://github.com/anthropics/claude-code/issues/26251)
and [#43875](https://github.com/anthropics/claude-code/issues/43875)
describe the regression: when the flag is set in isolation, Claude
treats the skill as unreachable even when the user types the matching
slash command. Adding `user-invocable: true` is the documented
workaround that preserves slash-command access.

Layer 1 enforces both flags whenever a `commands/<name>.md` exists for
a skill. If you see a Layer 1 FAIL for "explicit-invocation skill X
missing user-invocable: true", add the flag — do not strip
`disable-model-invocation`, or the skill will silently auto-trigger
again.

---

## Workspace path — `/tmp/<plugin-name>-workspace/` is the only legal location

Every artefact produced during a plugin update — eval runs, subagent
transcripts, prior-version snapshots, eval-viewer HTML, plugin-check
reports, intermediate zips, the shipping `.plugin` itself — lives
under `/tmp/<plugin-name>-workspace/`. The plugin source repo never
contains any of these.

This is enforced by Layer 1 with two complementary assertions:

1. **Plugin-root whitelist** — only the small fixed set of source files
   listed above is allowed at the plugin root. No `*.plugin` archive,
   no scratch folder.
2. **Repo-tree purity** — recursively, nowhere under the repo (or one
   level up at the user's checkout root) may there be a `*.plugin`,
   `*-workspace/`, `iteration-workspace/`, `skill-snapshot/`,
   `eval-viewer-iter*.html`, or `COUNCIL.md`. These are unmistakably
   runtime artefacts.

The previous rule kept "the canonical shipping `*.plugin` archive at
the plugin root" as an allowed exception. That exception was retired
in 0.6.0 because it conflicted with the read-only-installation reality
(plugins are mounted read-only, so no skill could update an in-tree
artefact) and forced a special-case whitelist entry that fought every
other consistency check. The new rule is uniform: source in the repo,
artefacts in `/tmp`, distribution via GitHub Releases.

When a Layer 1 FAIL names one of these patterns: do not silence by
extending the whitelist. Move the file to `/tmp/<plugin-name>-workspace/`
and re-run.

---

## Delivery — `/tmp` first, `dist/` as documented fallback

The standard delivery path for a built `.plugin` is a `computer://`
link into `/tmp/<plugin-name>-workspace/<plugin-name>.plugin`. Every
repackage writes to that location, and that location is all the build
recipe in `SKILL.md` Step 4 documents.

In Cowork a `/tmp` path is not always addressable as a downloadable
resource: the computer:// link resolves, but the user's "Save" dialog
can refuse a tmpfs source. The 0.6.1 cycle hit this in practice —
the release package lived at the advertised path and still could not
be saved by the user. The ad-hoc fix was to copy the archive to
`dist/` inside the repo. That worked for the user but broke Layer 1's
runtime-artefact sweep (which correctly rejected a `.plugin` under the
repo tree), turning the delivery workaround into a plugin-standard
violation.

0.6.2 resolves the tension by giving `dist/` a narrow, explicit role
and a narrow, explicit allowlist:

- **`dist/` is the only directory in the repo where a `.plugin` file
  is tolerated.** Nothing else. No nested subdirectories, no README,
  no `.gitkeep` — only `*.plugin` files at the top of `dist/`.
- **Layer 1 now encodes this as an allowlist in the repo-root sweep.**
  Files of the form `dist/*.plugin` are skipped. Anything else under
  `dist/` (wrong extension, nested directory) produces a new
  `dist/ contains only *.plugin files` FAIL — same noise level as the
  other runtime-artefact assertions.
- **`dist/*.plugin` is still a transition zone, not a permanent
  home.** Every release asset belongs on GitHub Releases. A file in
  `dist/` is a staging copy the user can open from Cowork's file
  browser *on the way to* uploading it as a release asset; after the
  release is cut, `dist/` is expected to be empty again. The
  `--strict-release` flag on `plugin-check.py` (added 0.6.4) is the
  deterministic enforcement of that lifecycle: in default mode a
  staged archive is tolerated, but with `--strict-release` Layer 1
  FAILs unless `dist/` is empty. The release CI workflow
  (`.github/workflows/release.yml`) invokes the check with
  `--strict-release` on tag-pushes, so a release that forgot to
  clean `dist/` cannot be published.
- **`.gitignore` covers `*.plugin` repo-wide** (not just inside
  `dist/`) so the staging copy never lands in a commit by accident.
  The `dist/` directory is materialised on demand when the fallback is
  needed and is not tracked in git — the Layer 1 allowlist gracefully
  reports "clean or absent" when it doesn't exist yet.

When the `/tmp` path is openable for the user, use it — nothing else
is required. When it is not (Cowork "Save As" refuses the source),
fall back to `cp /tmp/<plugin-name>-workspace/<plugin-name>.plugin
<repo>/dist/` and share the `dist/` path. Both paths are legal; the
`dist/` path is explicitly second-choice and documented as such so it
doesn't quietly become the default.

## What Layer 3 cannot be replaced by

A structural check asserts a known truth. An audit subagent asserts an
*unknown-unknown* — it looks at the plugin fresh and reports whatever
seems off. That's structurally different from the assertion set. A 100%
Layer 1 pass does not mean "the plugin is good"; it means "the plugin
satisfies the assertions we currently know to write". Layer 3 is how
the assertion set grows over time.
