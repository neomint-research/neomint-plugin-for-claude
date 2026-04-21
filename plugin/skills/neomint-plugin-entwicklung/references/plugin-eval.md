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
- No stray files at the plugin root (whitelist: `.claude-plugin/`,
  `skills/`, `README.md`, `CHANGELOG.md`, `SKILL_TEMPLATE.md`,
  `.gitignore`, `.git/`, plus `*.plugin` archives).
- Every skill directory under `skills/` (excluding `_shared`) has a
  `SKILL.md` with valid YAML frontmatter carrying `name` and
  `description`, and the file is not mid-sentence truncated.
- Every skill references `_shared/language.md` and
  `_shared/environments.md`.
- Every file referenced as `references/X.md` inside a SKILL.md actually
  exists on disk.
- README mentions every skill present on disk.
- README does not mention ghost-skills (names that look like skills but
  don't exist on disk).

Run:

```
python3 skills/neomint-plugin-entwicklung/scripts/plugin-check.py <plugin-root>
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

Mechanics:

1. Spawn a subagent with a clean, minimal prompt: "Here is a plugin at
   `<path>`. Inspect it without preconditioning. Report: (a) standards
   compliance gaps, (b) skill-quality concerns, (c) documentation
   mismatches, (d) anything surprising. Stay under 400 words."
2. Collect the subagent's findings.
3. Cross-check against the Layer 1 report:
   - Findings the script already caught → confirmation that both signals
     agree.
   - Findings the script missed → candidate new Layer 1 assertions. The
     Step 5e self-optimisation proposal should name these.
   - Script-only findings → the subagent may have missed something the
     script caught (tolerate; deterministic checks don't need the
     subagent's approval).
4. Triage which findings are real issues vs. false positives. Fix the
   real issues.

The audit subagent is intentionally unprimed. The point is to catch
blind spots that the assertion set doesn't know to look for — the same
reason skill-creator runs a baseline "without-skill" subagent.

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

## What Layer 3 cannot be replaced by

A structural check asserts a known truth. An audit subagent asserts an
*unknown-unknown* — it looks at the plugin fresh and reports whatever
seems off. That's structurally different from the assertion set. A 100%
Layer 1 pass does not mean "the plugin is good"; it means "the plugin
satisfies the assertions we currently know to write". Layer 3 is how
the assertion set grows over time.
