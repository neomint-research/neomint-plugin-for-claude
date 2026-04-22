#!/usr/bin/env python3
"""grade.py — Contract grader for the council skill.

Invoked by plugin-check.py Layer 2. Returns exit 0 if the skill's SKILL.md
still honours every contract promise, otherwise exit 1 with a summary of
which assertions failed.

Assertions target the skill's advertised contract, not the LLM's runtime
behaviour. Runtime behaviour is graded once per iteration via skill-creator
and captured in evals/ITERATION_REPORT.md — this script protects the
contract itself against silent regressions.

This grader was rewritten for the radically streamlined version of the
skill. The prior grader had 33 assertions that locked the OLD ceremony
(sentinels, labeled Thesis/Finding/Cross-reference/Dissent/Resolvable
blocks, QUICK/FULL/AUDIT mode zoo, Phase 0..4 labels, five reference
files) into the contract. That ceremony was the failure mode the user
asked us to remove. The new grader protects the disciplines — not the
packaging.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_MD = HERE.parent / "SKILL.md"

# Import the shared static-analysis helper. Per-skill graders run as
# standalone scripts, not as part of a Python package, so we have to
# manually extend sys.path before the import. The helper lives one
# level up under `_shared/` (introduced in 0.6.6 / P18).
sys.path.insert(0, str(HERE.parent.parent / "_shared"))
from grader_utils import count_failure_sites  # noqa: E402


def load() -> str:
    if not SKILL_MD.exists():
        print(f"FAIL council: SKILL.md missing at {SKILL_MD}")
        sys.exit(1)
    return SKILL_MD.read_text()


def contains_all(text: str, needles: list[str]) -> list[str]:
    return [n for n in needles if n not in text]


def _self_check_count() -> int:
    """Count distinct assertion sites in this grader by static analysis.

    Added in 0.6.4 (P12) so the grader self-reports its contract size.
    Extracted to `_shared/grader_utils.py` in 0.6.6 (P18) — this
    wrapper now just delegates to the shared helper so future graders
    can adopt the pattern without copy-pasting the implementation.
    """
    return count_failure_sites(Path(__file__))


def main() -> int:
    # --count-only returns just the assertion count (P12).
    if len(sys.argv) > 1 and sys.argv[1] == "--count-only":
        print(_self_check_count())
        return 0

    text = load()
    lower = text.lower()
    failures: list[str] = []
    check_count = _self_check_count()

    # ------------------------------------------------------------------
    # A. Identity and loadability
    # ------------------------------------------------------------------

    # A1. YAML frontmatter is present and parseable.
    fm_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm_match:
        failures.append("YAML frontmatter missing from SKILL.md")
        body = ""
    else:
        body = fm_match.group(1)

    # A2. description field present and ≤ 1024 chars folded (Anthropic's
    #     hard truncation limit for skill descriptions). The 0.4.0-0.4.2
    #     description was 1382 chars and was silently truncated; the
    #     user's complaint "council is not recognized" traced to that.
    if body:
        desc_match = re.search(
            r"description:\s*>?\s*\n((?:[ \t]+.+\n?)+)", body
        )
        if desc_match:
            raw = desc_match.group(1)
            folded = " ".join(
                line.strip() for line in raw.splitlines() if line.strip()
            )
            if len(folded) > 1024:
                failures.append(
                    f"description exceeds 1024-char hard limit "
                    f"({len(folded)} chars) — will be truncated by Claude"
                )
        else:
            failures.append("description field missing from frontmatter")

    # ------------------------------------------------------------------
    # B. Structural sections the skill depends on
    # ------------------------------------------------------------------

    if "## Language" not in text:
        failures.append("## Language section missing")
    if "## Environment detection" not in text:
        failures.append("## Environment detection section missing")
    if "## Core principle" not in text:
        failures.append("## Core principle section missing")

    # ------------------------------------------------------------------
    # C. The five MECE roles + Chairman synthesis
    # ------------------------------------------------------------------

    missing_roles = contains_all(
        text,
        ["Cartographer", "Analyst", "Adversary", "Scout", "Operator"],
    )
    if missing_roles:
        failures.append(
            f"Roles missing from SKILL.md: {missing_roles} — "
            f"the five MECE roles are the substance of the skill"
        )
    if "Chairman" not in text:
        failures.append(
            "Chairman synthesis not mentioned — the Verdict layer "
            "must be named"
        )

    # Each role's MECE axis keyword must appear so the axes can't silently
    # drift. Keep the checks lightweight — substring matches on the
    # distinctive phrasing from references/roles.md.
    for phrase, role in [
        ("What depends on this?", "Cartographer"),
        ("Is the derivation valid?", "Analyst"),
        ("What destroys this?", "Adversary"),
        ("What aren't we seeing?", "Scout"),
        ("What do we actually do?", "Operator"),
    ]:
        if phrase not in text:
            failures.append(
                f"{role}'s MECE axis question '{phrase}' missing "
                f"from SKILL.md — without it the role's dimension "
                f"can silently drift"
            )

    # ------------------------------------------------------------------
    # D. The seven-turn shape (the live-turn contract)
    # ------------------------------------------------------------------

    # D1. "seven turns" or the numbered turn block must be declared.
    if "seven turns" not in lower and "The seven turns" not in text:
        failures.append(
            "The seven-turn shape is not declared in prose — the "
            "live-turn contract must be named explicitly"
        )

    # D2. Each turn T1..T7 is labeled in the turn block.
    for label in (
        "T1  Read-back + Grounding",
        "T2  Cartographer",
        "T3  Analyst",
        "T4  Adversary",
        "T5  Scout",
        "T6  Operator",
        "T7  Verdict",
    ):
        if label not in text:
            failures.append(
                f"Turn label '{label}' missing from turn block — "
                f"the seven-turn shape must be visible as a block"
            )

    # D3. Turn ordering: T1..T7 appear in order.
    turn_block_match = re.search(
        r"T1\s+Read-back.*?T7\s+Verdict", text, re.DOTALL
    )
    if turn_block_match:
        block = turn_block_match.group(0)
        expected_order = [
            "T1  Read-back",
            "T2  Cartographer",
            "T3  Analyst",
            "T4  Adversary",
            "T5  Scout",
            "T6  Operator",
            "T7  Verdict",
        ]
        positions = {label: block.find(label) for label in expected_order}
        if all(p >= 0 for p in positions.values()):
            ordered = sorted(positions.items(), key=lambda kv: kv[1])
            if [k for k, _ in ordered] != expected_order:
                failures.append(
                    f"Turn ordering wrong in the seven-turn block — "
                    f"expected {expected_order}, got "
                    f"{[k for k, _ in ordered]}"
                )

    # D4. One turn per assistant message — the core live-turn rule.
    if "One turn = one assistant message" not in text:
        failures.append(
            "'One turn = one assistant message' rule missing — "
            "the live-turn seam is the point of this skill"
        )

    # ------------------------------------------------------------------
    # E. Advisor-voice register (0.5.4) — no header, no menu
    # ------------------------------------------------------------------

    # E1. The advisor-voice section that forbids turn headers must exist.
    #     Post-0.5.4 the role self-identifies inside the first sentence
    #     of its prose; a heading like `## Cartographer · 2/7` is
    #     explicitly forbidden. The old requirement (template declared)
    #     was inverted.
    if "The voice of a turn" not in text:
        failures.append(
            "'## The voice of a turn — no header, no menu' section "
            "missing — this is the 0.5.4 advisor-voice contract that "
            "replaces the old turn-header template"
        )
    if "identifies itself inside the first sentence" not in text and \
       "identifies itself in the first sentence" not in text:
        failures.append(
            "Rule 'the role identifies itself in the first sentence' "
            "missing — without it the opening-header ceremony can creep "
            "back as a template"
        )

    # E2. Em-dash steering menu is explicitly an anti-pattern.
    if "Steering-menu under any turn except T1" not in text and \
       "Steering menu under any turn except T1" not in text:
        failures.append(
            "Anti-pattern 'Steering-menu under any turn except T1's "
            "close' missing — the em-dash handoff sentinel was removed "
            "in 0.5.4 and must be named as forbidden so it can't creep "
            "back"
        )

    # E3. The compressed verdict turn is declared for sharp questions.
    if "## Scope — the compressed verdict turn" not in text and \
       "compressed verdict turn" not in lower:
        failures.append(
            "'Scope — the compressed verdict turn' section missing — "
            "the downward-triage shape for narrow questions is part of "
            "the 0.5.4 contract (skill shrinks the question but never "
            "simplifies it)"
        )
    if "shrink the question" not in lower and \
       "shrink but never simplify" not in lower:
        failures.append(
            "Scope-reduction rationale ('shrink the question but never "
            "simplify it' / 'shrink but never simplify') missing — "
            "without it the compressed turn devolves into a speed button"
        )

    # E4. The old sentinel block (=== TURN N/K COMPLETE ===) must be
    #     explicitly named as an anti-pattern so it cannot creep back.
    if "=== TURN" in text and "anti-pattern" not in lower and "Anti-pattern" not in text:
        failures.append(
            "Sentinel block '=== TURN ... ===' appears in SKILL.md "
            "outside the anti-pattern context — it must be forbidden, "
            "not demonstrated"
        )

    # ------------------------------------------------------------------
    # F. Grounding discipline (Hersteller + Community + Divergence)
    # ------------------------------------------------------------------

    if "Hersteller" not in text:
        failures.append(
            "GROUND discipline missing: 'Hersteller' (authoritative "
            "source) not referenced in SKILL.md"
        )
    if "Community" not in text:
        failures.append(
            "GROUND discipline missing: 'Community' source not "
            "referenced in SKILL.md"
        )
    if "Divergence" not in text:
        failures.append(
            "GROUND discipline missing: 'Divergence' slot not "
            "declared — a one-line divergence-or-alignment statement "
            "is how Hersteller/Community become a first-class finding"
        )

    # F1. No role speaks before grounding — the binding rule.
    if "No role speaks before the grounding" not in text:
        failures.append(
            "GROUND-FIRST binding rule missing: 'No role speaks "
            "before the grounding is on the table' must appear "
            "verbatim so the rule cannot decay to a header with no body"
        )

    # F2. Visible tool calls required when web access is available.
    if "visible" not in lower or ("WebSearch" not in text and "WebFetch" not in text):
        failures.append(
            "GROUND requirement for visible tool calls (WebSearch / "
            "WebFetch) missing — narrated search without the call in "
            "the transcript is a contract violation and must be named"
        )

    # ------------------------------------------------------------------
    # G. Cross-role engagement + dissent discipline
    # ------------------------------------------------------------------

    # G1. Cross-role engagement requirement: every role from T3 onward
    #     must engage with a prior role by name. The rule stays, the
    #     label "Cross-reference (Pflicht):" is gone.
    if "T3 onward" not in text and "from T3 onward" not in text:
        failures.append(
            "Cross-role engagement obligation ('from T3 onward') "
            "missing — without it, the Council collapses into five "
            "parallel essays"
        )
    # Normalise whitespace so the rule still matches when the line
    # wraps inside a paragraph.
    flat = re.sub(r"\s+", " ", text)
    if "engage with at least one prior role by name" not in flat:
        failures.append(
            "Cross-role engagement rule must state 'engage with at "
            "least one prior role by name' so it is load-bearing prose, "
            "not a paraphrase"
        )

    # G2. CHAIRMAN-VETO — the once-per-role deepen mechanism for silent
    #     concurrence or under-production.
    if "CHAIRMAN-VETO" not in text:
        failures.append(
            "CHAIRMAN-VETO mechanism missing — the once-per-role "
            "deepen mechanism is how silent concurrence / under-"
            "production gets corrected without ballooning the run"
        )

    # ------------------------------------------------------------------
    # H. Adaptive Verdict (T7) — the core user requirement for this rewrite
    # ------------------------------------------------------------------

    if "adaptive" not in lower:
        failures.append(
            "Adaptive Verdict principle missing: the Verdict must be "
            "explicitly described as 'adaptive' / 'scales to the "
            "complexity of the question' — this is the non-negotiable "
            "output-shape requirement from the user"
        )
    if "matches the complexity" not in text:
        failures.append(
            "Adaptive Verdict rule must state that the verdict "
            "'matches the complexity' of the question — otherwise the "
            "template-driven behaviour can creep back"
        )

    # H1. Three complexity regimes are named.
    for regime_phrase, label in [
        ("Narrow question", "narrow"),
        ("Broad question", "broad"),
        ("Roles could not converge", "inconclusive"),
    ]:
        if regime_phrase not in text:
            failures.append(
                f"Adaptive Verdict missing the {label!r} regime "
                f"('{regime_phrase}') — each complexity regime must "
                f"be named so the Chairman knows which shape to pick"
            )

    # H2. Verdict anti-patterns: no restated grounding block, no bulleted
    #     citations, no MECE checklist block, no new findings under the
    #     Chairman's voice.
    for phrase, label in [
        ("bulleted Citations section", "bulleted Citations section"),
        ("MECE-Prüfung checklist as a visible block", "MECE checklist block"),
        ("New findings under the Chairman", "new findings under Chairman"),
    ]:
        if phrase not in text:
            failures.append(
                f"Verdict anti-pattern '{label}' missing — the "
                f"Chairman's output shape needs explicit anti-patterns "
                f"to prevent ceremony creep-back"
            )

    # ------------------------------------------------------------------
    # I. Core principle: 'Reicht' is not a verdict
    # ------------------------------------------------------------------

    if "stop only when sure" not in lower:
        failures.append(
            "Core principle missing: phrase 'stop only when sure' "
            "not found in SKILL.md"
        )
    if "what would need to become true" not in lower:
        failures.append(
            "Core principle missing: phrase 'what would need to "
            "become true' not found in SKILL.md"
        )
    if '"Reicht" is not a verdict' not in text and "'Reicht' is not a verdict" not in text:
        failures.append(
            "Core principle ''Reicht' is not a verdict' missing "
            "verbatim — the user's feedback memory explicitly "
            "anchors this phrasing"
        )

    # I1. Anti-pattern: 3/5 converge is a status report, not a verdict.
    if "3/5" not in text or "status report" not in text:
        failures.append(
            "Anti-pattern '3/5 roles converge, 2/5 inconclusive is a "
            "status report, not a verdict' framing missing from SKILL.md"
        )

    # ------------------------------------------------------------------
    # J. Steering vocabulary + persistence
    # ------------------------------------------------------------------

    # J1. Steering tokens are named (German-first, as the skill uses).
    for token in ("weiter", "widersprich", "vertiefe", "abzweig", "stopp"):
        if token not in text:
            failures.append(
                f"Steering token '{token}' missing from SKILL.md — "
                f"the user-facing vocabulary must be on the record"
            )
    # J2. Steering introduced once, in T1 — explicit rule.
    if "introduced once" not in text and "introduced once, in T1" not in text:
        failures.append(
            "Steering vocabulary rule 'introduced once, in T1' missing "
            "— otherwise the closing line swells into a token zoo"
        )

    # J3. Persistence to COUNCIL.md is declared.
    if "COUNCIL.md" not in text:
        failures.append("COUNCIL.md persistence file not documented")
    if "## Persistence" not in text:
        failures.append(
            "'## Persistence' section missing — the persistence-"
            "payoff contract must be declared"
        )

    # ------------------------------------------------------------------
    # K. Anti-patterns are declared as a block (not just scattered)
    # ------------------------------------------------------------------

    if "## Anti-patterns" not in text:
        failures.append(
            "'## Anti-patterns' section missing — anti-patterns must "
            "be gathered in one readable block so a role can scan them "
            "before posting a turn"
        )

    # Specifically name the old ceremony as forbidden so a future edit
    # cannot quietly reintroduce it.
    for phrase, what in [
        ("**Thesis", "labeled **Thesis:** block"),
        ("**Cross-reference (Pflicht):**", "labeled **Cross-reference (Pflicht):** block"),
        ("**Dissent (Pflicht):**", "labeled **Dissent (Pflicht):** block"),
        ("**Resolvable?**", "labeled **Resolvable?** block"),
        ("=== TURN N/K COMPLETE ===", "sentinel block"),
    ]:
        if phrase not in text:
            failures.append(
                f"Anti-pattern must explicitly forbid the {what} — "
                f"old-ceremony label not named, so it can creep back"
            )

    # 0.5.4 advisor-voice additions — the three new anti-patterns
    # protect the three changes made in this version from silent
    # regression.
    for phrase, what in [
        ("Turn header with position counter", "turn header with position counter (## Cartographer · 2/7)"),
        ("Seven turns for a clearly narrow question", "seven turns for a clearly narrow question"),
    ]:
        if phrase not in text:
            failures.append(
                f"0.5.4 anti-pattern must explicitly forbid '{what}' — "
                f"without the named rule the old packaging can creep back"
            )

    # ------------------------------------------------------------------
    # L. Stopping criteria
    # ------------------------------------------------------------------

    if "## Stopping criteria" not in text:
        failures.append(
            "'## Stopping criteria' section missing — the three legal "
            "terminators (recommendation / explicit abstention / user "
            "stop) must be declared"
        )

    # ------------------------------------------------------------------
    # M. References — only roles.md remains; no stale pointers
    # ------------------------------------------------------------------

    roles_md = HERE.parent / "references" / "roles.md"
    if not roles_md.exists():
        failures.append("references/roles.md missing")

    for stale_ref in ("phases.md", "turns.md", "ground.md", "persistence.md"):
        # These four references were deleted in the streamlining. SKILL.md
        # must not point at them.
        if stale_ref in text:
            failures.append(
                f"SKILL.md points to deleted reference "
                f"'references/{stale_ref}' — stale pointer must be "
                f"removed"
            )
        # And the file itself must indeed be gone.
        if (HERE.parent / "references" / stale_ref).exists():
            failures.append(
                f"references/{stale_ref} still present on disk — "
                f"should have been deleted in the streamlining"
            )

    # ------------------------------------------------------------------
    # N. Old-ceremony legacy tokens must not sit silently in SKILL.md body
    #     outside the anti-patterns section
    # ------------------------------------------------------------------

    # Scan for legacy mode labels used as LIVE labels — not as negations
    # or quoted anti-pattern examples. A live label looks like
    # "CODE-MODE (filesystem access)" or "In QUICK mode, we …".
    # Negations like "no QUICK/FULL/AUDIT mode zoo" and quoted examples
    # like `"…CODE-MODE · Tiefe: FULL"` are legitimate — they *describe*
    # the removed machinery without reinstating it.
    for m in re.finditer(r"\b(CODE-MODE|DOC-MODE|CHAT-MODE)\b", text):
        window = text[max(0, m.start() - 30): m.end() + 30]
        # Skip if it's inside a quoted anti-pattern example.
        if '"' in window and (window.count('"') % 2 == 1 or "Modus:" in window):
            continue
        # Skip if it's a meta-reference to the old machinery.
        if any(
            tag in window.lower()
            for tag in ("no ", "anti-pattern", "removed", "old", "legacy", "no mode", "mode zoo")
        ):
            continue
        # Skip if it's inside the anti-pattern section.
        if "## Anti-patterns" in text and m.start() > text.find("## Anti-patterns"):
            continue
        failures.append(
            f"Legacy mode label '{m.group(0)}' used as a live label "
            f"in SKILL.md (context: ...{window.strip()}...) — the mode "
            f"zoo was removed in the streamlining and must not creep "
            f"back as a live reference"
        )

    # Phase-numbered labels (Phase 0..4) from pre-0.4.8 must not appear
    # anywhere in SKILL.md.
    for stale in ("Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4"):
        if stale in text:
            failures.append(
                f"Stale phase label '{stale}' in SKILL.md — post-"
                f"streamlining convention is T1..T7 only"
            )

    # ------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------

    if failures:
        print(f"FAIL council grader ({len(failures)}/{check_count} failed):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS council grader — streamlined-contract ({check_count} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
