#!/usr/bin/env python3
"""grade.py — Contract grader for the council skill.

Invoked by plugin-check.py Layer 2. Returns exit 0 if the skill's SKILL.md
still honours every contract promise, otherwise exit 1 with a summary of
which assertions failed.

Assertions target the skill's advertised contract, not the LLM's runtime
behaviour. Runtime behaviour is graded once per iteration via skill-creator
and captured in evals/ITERATION_REPORT.md — this script protects the
contract itself against silent regressions.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_MD = HERE.parent / "SKILL.md"


def load() -> str:
    if not SKILL_MD.exists():
        print(f"FAIL council: SKILL.md missing at {SKILL_MD}")
        sys.exit(1)
    return SKILL_MD.read_text()


def contains_all(text: str, needles: list[str]) -> list[str]:
    return [n for n in needles if n not in text]


def main() -> int:
    text = load()
    failures: list[str] = []

    # 1. Five MECE roles are explicitly named
    missing_roles = contains_all(text, ["Analyst", "Cartographer", "Adversary", "Scout", "Operator"])
    if missing_roles:
        failures.append(f"Roles missing from SKILL.md: {missing_roles}")

    # 2. Chairman synthesis is named
    if "Chairman" not in text:
        failures.append("Chairman synthesis not mentioned")

    # 3. Five phases are named (case-insensitive — SKILL.md uses both Orient/ORIENT)
    #    Ground was added in 0.4.4 as a mandatory pre-discussion phase.
    lower = text.lower()
    missing_phases = [p for p in ["orient", "ground", "map", "council", "verdict"] if p not in lower]
    if missing_phases:
        failures.append(f"Phases missing: {missing_phases}")

    # 4. Three depth modes
    missing_depth = contains_all(text, ["QUICK", "FULL", "AUDIT"])
    if missing_depth:
        failures.append(f"Depth modes missing: {missing_depth}")

    # 5. Three contexts
    missing_ctx = contains_all(text, ["CODE-MODE", "DOC-MODE", "CHAT-MODE"])
    if missing_ctx:
        failures.append(f"Context modes missing: {missing_ctx}")

    # 6. Two-track output
    if not (re.search(r"OPERATIVE", text) and re.search(r"MANAGEMENT", text)):
        failures.append("Two-track output (OPERATIVE + MANAGEMENT) not declared")

    # 7. Persistence line is declared in the output template
    #    (this regression got caught in iteration-1 of the skill-creator loop)
    #    After 0.4.8 it may appear as a heading '## Persistence' in the T8
    #    VERDICT template rather than the old inline 'Persistence:' label —
    #    accept either form.
    if "Persistence:" not in text and "## Persistence" not in text:
        failures.append(
            "Mandatory persistence block missing from output template — "
            "expected 'Persistence:' (inline) or '## Persistence' (section)"
        )
    if "COUNCIL.md" not in text:
        failures.append("COUNCIL.md persistence file not documented")

    # 8. Diagnostic question standard includes the mode/context header
    #    (second iter-1 regression the eval loop caught)
    if "Mode: DIAGNOSTIC" not in text:
        failures.append("Diagnostic question standard missing 'Mode: DIAGNOSTIC' header")

    # 9. Required skill blocks
    if "## Language" not in text:
        failures.append("## Language section missing")
    if "## Environment detection" not in text:
        failures.append("## Environment detection section missing")
    if "## Procedure with file access" not in text:
        failures.append("## Procedure with file access section missing")
    if "## Procedure in Claude AI (Web)" not in text:
        failures.append("## Procedure in Claude AI (Web) section missing")

    # 10. References exist on disk
    for ref in ["roles.md", "phases.md", "persistence.md", "ground.md"]:
        if not (HERE.parent / "references" / ref).exists():
            failures.append(f"references/{ref} missing")

    # 11. Description (YAML folded scalar, rendered single-line) must be
    #     ≤ 1024 chars — Anthropic's hard truncation limit for skill
    #     descriptions. The 0.4.0–0.4.2 description was 1382 chars and
    #     silently truncated; the user's complaint in 0.4.2 ("council is
    #     not recognized when I ask about the plugin") traces directly
    #     to this. This assertion ensures a regression can't land again.
    fm_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if fm_match:
        body = fm_match.group(1)
        desc_match = re.search(r"description:\s*>?\s*\n((?:[ \t]+.+\n?)+)", body)
        if desc_match:
            raw = desc_match.group(1)
            # fold: collapse consecutive indented lines to single spaces,
            # matching how YAML `>` renders the value Claude actually sees.
            folded = " ".join(line.strip() for line in raw.splitlines() if line.strip())
            if len(folded) > 1024:
                failures.append(
                    f"description exceeds 1024-char hard limit "
                    f"({len(folded)} chars) — will be truncated by Claude"
                )
        else:
            failures.append("description field missing from frontmatter")
    else:
        failures.append("YAML frontmatter missing from SKILL.md")

    # 12. VERDICT COMPLETENESS principle — the "never stop at sufficient"
    #     standard the user set in feedback_standard_not_sufficient.md.
    #     Must appear in SKILL.md body so it cannot silently decay across
    #     future edits. Case-insensitive to survive a sentence-start "Stop".
    text_lower = text.lower()
    if "stop only when sure" not in text_lower:
        failures.append(
            "VERDICT COMPLETENESS principle missing: phrase "
            "'stop only when sure' not found in SKILL.md"
        )
    if "what would need to become true" not in text_lower:
        failures.append(
            "VERDICT COMPLETENESS principle missing: phrase "
            "'what would need to become true' not found in SKILL.md"
        )

    # 13. Anti-pattern "3/5 roles converge, 2/5 inconclusive" must be
    #     explicitly rejected as a status report, not accepted as a
    #     verdict. Concrete framing the user cited.
    if "3/5" not in text or "status report" not in text:
        failures.append(
            "Anti-pattern '3/5 converge, 2/5 inconclusive is a status "
            "report, not a verdict' framing missing from SKILL.md"
        )

    # 14. GROUND phase — the 0.4.4 principle: "what does the Hersteller
    #     say, what does the community say, and only THEN does the
    #     Council discuss." Both source names must appear in SKILL.md
    #     so the contract cannot silently decay.
    if "Hersteller" not in text:
        failures.append(
            "GROUND phase missing: 'Hersteller' (authoritative source) "
            "not referenced in SKILL.md"
        )
    if "Community" not in text:
        failures.append(
            "GROUND phase missing: 'Community' source not referenced "
            "in SKILL.md"
        )

    # 15. GROUND-FIRST rigor duty — the principle must be stated as a
    #     non-negotiable rigor rule, not buried in an example.
    if "GROUND-FIRST" not in text:
        failures.append(
            "GROUND-FIRST rigor duty missing from SKILL.md — "
            "principle must be encoded as a named duty"
        )

    # 16. Grounding section in the output template — a verdict without
    #     a grounding slot is structurally an opinion, not a Council
    #     finding.
    if "## Grounding" not in text:
        failures.append(
            "'## Grounding' section missing from output template — "
            "Hersteller + Community must be visible in every verdict"
        )
    if "Manufacturer (Hersteller)" not in text:
        failures.append(
            "Output template must show 'Manufacturer (Hersteller)' "
            "label so the source is explicit to the reader"
        )

    # 17. Sequence contract: GROUND precedes the map phase (T3
    #     CARTOGRAPHER) and the other judging roles. The user's rule:
    #     "erst das wird diskutiert" — grounding must come BEFORE the
    #     Cartographer and before the other judging roles, not as an
    #     appendix. After 0.4.8 the phase block is turn-numbered
    #     (T1 ORIENT … T8 VERDICT), so check the turn ordering.
    turn_block = re.search(
        r"T1\s+ORIENT.*?T8\s+VERDICT", text, re.DOTALL
    )
    if turn_block:
        block = turn_block.group(0)
        expected_order = [
            "T1  ORIENT",
            "T2  GROUND",
            "T3  CARTOGRAPHER",
            "T4  ANALYST",
            "T5  ADVERSARY",
            "T6  SCOUT",
            "T7  OPERATOR",
            "T8  VERDICT",
        ]
        positions = {label: block.find(label) for label in expected_order}
        if any(p < 0 for p in positions.values()):
            missing = [k for k, v in positions.items() if v < 0]
            failures.append(
                f"Turn-ordering check failed: missing labels {missing} "
                f"in the FULL turn map"
            )
        else:
            ordered = sorted(positions.items(), key=lambda kv: kv[1])
            if [k for k, _ in ordered] != expected_order:
                failures.append(
                    f"Turn ordering wrong — expected {expected_order}, got "
                    f"{[k for k, _ in ordered]}. GROUND (T2) must precede "
                    f"CARTOGRAPHER (T3)."
                )
    else:
        failures.append(
            "Turn block 'T1 ORIENT … T8 VERDICT' not found in SKILL.md — "
            "the turn-gated structure is not declared"
        )

    # 18. ENFORCEMENT, not just presence — GROUND-FIRST must be followed
    #     by the binding sentence that a well-behaved Claude will actually
    #     read as a rule, not a label. The Layer 3 auditor explicitly
    #     flagged that a future edit could keep "GROUND-FIRST" as a
    #     header while silently gutting the rule.
    gf_idx = text.find("GROUND-FIRST")
    if gf_idx >= 0:
        nearby = text[gf_idx : gf_idx + 2000]
        if "No role speaks before both" not in nearby:
            failures.append(
                "GROUND-FIRST named but its binding sentence 'No role "
                "speaks before both the Hersteller position and the "
                "Community position are on the table' is missing "
                "nearby — rule without enforcement text"
            )

    # 19. The MECE check must treat grounding as a publication gate,
    #     not as a status line. The auditor's concern: 'Grounding
    #     complete' could decay from a gate to an optional field while
    #     passing the presence check. Require the explicit blocker
    #     phrasing in SKILL.md body.
    if "blocks publication" not in text:
        failures.append(
            "MECE grounding check must include 'blocks publication' "
            "phrasing so the rule is a gate, not a status line"
        )

    # 20. The T3 CARTOGRAPHER phase must name the grounding block as
    #     input in prose — a future reorder that drops this coupling
    #     would silently decouple the map from GROUND and restore pre-0.4.4
    #     behaviour. After 0.4.8 the MAP phase is T3 CARTOGRAPHER in the
    #     turn-numbered phase block.
    phases_path = HERE.parent / "references" / "phases.md"
    if phases_path.exists():
        phases_text = phases_path.read_text()
        t3_match = re.search(
            r"## T3 — CARTOGRAPHER.*?(?=## T4)", phases_text, re.DOTALL
        )
        if not t3_match:
            failures.append(
                "references/phases.md missing '## T3 — CARTOGRAPHER' "
                "section — T3 structure cannot be verified"
            )
        else:
            t3_block = t3_match.group(0)
            if "T2 grounding block" not in t3_block and "T2 grounding" not in t3_block:
                failures.append(
                    "T3 CARTOGRAPHER must name 'T2 grounding block' as "
                    "input — coupling to GROUND is not enforced in prose"
                )
    else:
        failures.append("references/phases.md missing")

    # --- Turn-gated contract assertions (added in 0.4.8) -------------------
    # The live-turn contract is the structural fix to the old "single wall
    # of text Council" failure mode. These assertions lock the contract
    # into SKILL.md so no future edit can silently dilute it back to a
    # monolithic response.

    # 21. Turn-gated deliberation section must exist in SKILL.md body.
    if "## Turn-gated deliberation" not in text:
        failures.append(
            "Turn-gated deliberation section missing — the live-turn "
            "contract (one phase per message + sentinel) is the 0.4.8 "
            "backbone and must be declared explicitly"
        )

    # 22. Sentinel format must be defined with its exact marker string so
    #     both the model and the grader can lock on the same terminator.
    if "=== TURN <N>/<K> COMPLETE — <PHASE NAME> ===" not in text:
        failures.append(
            "Sentinel format template '=== TURN <N>/<K> COMPLETE — "
            "<PHASE NAME> ===' missing — without an exact format the "
            "turn boundaries cannot be enforced"
        )

    # 23. Continuation tokens NEXT / REBUTTAL / DEEPEN / BRANCH / ABORT
    #     must all be named in SKILL.md so the user-facing protocol is
    #     on the record.
    missing_tokens = contains_all(text, ["NEXT", "REBUTTAL", "DEEPEN", "BRANCH", "ABORT"])
    if missing_tokens:
        failures.append(
            f"Continuation tokens missing from SKILL.md: {missing_tokens}"
        )

    # 24. Role turn micro-format components — Thesis, Cross-reference,
    #     Dissent, Resolvable? — must be declared. These are how a role
    #     turn compounds with prior turns and how the grader (and the
    #     Chairman) verify the role actually listened.
    if "**Thesis (one sentence):**" not in text:
        failures.append(
            "Role turn micro-format missing '**Thesis (one sentence):**' "
            "marker — without it, a role turn can drift without taking "
            "a position"
        )
    if "**Cross-reference" not in text:
        failures.append(
            "Role turn micro-format missing '**Cross-reference' marker "
            "— the cross-reference obligation is how turns compound "
            "rather than staying five independent essays"
        )
    if "**Dissent" not in text:
        failures.append(
            "Role turn micro-format missing '**Dissent' marker — "
            "silent agreement is indistinguishable from not listening"
        )
    if "**Resolvable?**" not in text:
        failures.append(
            "Role turn micro-format missing '**Resolvable?**' marker "
            "— abstention discipline applies per turn"
        )

    # 25. Chairman citation rule: every role turn must be quoted in the
    #     verdict. This is how the Chairman shows it listened.
    if "Chairman citation rule" not in text and "## Citations" not in text:
        failures.append(
            "Chairman citation rule missing from SKILL.md — the "
            "Chairman's job is to listen, and listening is visible "
            "only through citation of each role turn"
        )
    if "## Citations" not in text:
        failures.append(
            "T8 VERDICT output template missing '## Citations' section "
            "— per-role quoted citations are the Chairman citation rule"
        )

    # 26. GROUND turn must require visible tool calls, not narrated search.
    #     The phrase appears in the T2 GROUND section of SKILL.md.
    if "visible tool" not in text.lower() and "WebSearch" not in text:
        failures.append(
            "GROUND turn tool-call requirement missing — the user "
            "must see the grounding was performed, not asserted"
        )

    # 27. Turn counts declared: FULL (8 turns), QUICK (3 turns).
    #     AUDIT is 8+ so we only check "8" appears together with "FULL".
    if "FULL (8 turns)" not in text:
        failures.append(
            "FULL turn count '(8 turns)' missing — the turn plan "
            "must be announced so K is fixed at T1"
        )
    if "QUICK (3 turns)" not in text:
        failures.append(
            "QUICK turn count '(3 turns)' missing — the compressed "
            "live-turn plan must be declared"
        )

    # 28. NO-DOWNGRADE for K — explicit rule that K does not change
    #     mid-run silently.
    if "K does not change" not in text and "K is fixed" not in text:
        failures.append(
            "NO-DOWNGRADE-for-K rule missing — silent turn-count "
            "reduction mid-run is a documented failure mode that "
            "must be ruled out in SKILL.md body"
        )

    # 29. references/turns.md must exist (new reference file for the
    #     live-turn contract).
    turns_md = HERE.parent / "references" / "turns.md"
    if not turns_md.exists():
        failures.append("references/turns.md missing — the live-turn contract reference")
    else:
        turns_text = turns_md.read_text()
        # Worked examples anchor the contract to concrete turns
        if "## Worked example — FULL run skeleton" not in turns_text:
            failures.append(
                "references/turns.md missing FULL-run worked example "
                "— concrete turn-by-turn skeleton is how readers "
                "internalise the contract"
            )
        if "## Worked example — QUICK run skeleton" not in turns_text:
            failures.append(
                "references/turns.md missing QUICK-run worked example"
            )
        # Anti-shortcut enforcement section must name #21672
        if "#21672" not in turns_text:
            failures.append(
                "references/turns.md should name Claude Code issue "
                "#21672 — the documented multi-turn-skill failure "
                "mode this contract defends against"
            )

    # 30. Anti-pattern: two phases in one message must be called out as
    #     a contract violation.
    if "Two phases in one assistant message" not in text:
        failures.append(
            "Anti-pattern 'Two phases in one assistant message' "
            "missing from SKILL.md — the #21672 collapse pattern "
            "must be named to block it"
        )

    # 31. Turn header format defined: '## Turn <N>/<K> — <PHASE NAME>'.
    if "## Turn <N>/<K> — <PHASE NAME>" not in text:
        failures.append(
            "Turn header template '## Turn <N>/<K> — <PHASE NAME>' "
            "missing — the paired header + sentinel bracket each turn"
        )

    # 32. phases.md must be turn-numbered (T1 ORIENT through T8 VERDICT).
    #     This verifies the 0.4.8 re-shape: phase numbering moved from
    #     Phase 0..4 to T1..T8.
    if phases_path.exists():
        pt = phases_path.read_text()
        for label in ("## T1 — ORIENT", "## T2 — GROUND",
                      "## T3 — CARTOGRAPHER", "## T4 — ANALYST",
                      "## T5 — ADVERSARY", "## T6 — SCOUT",
                      "## T7 — OPERATOR", "## T8 — VERDICT"):
            if label not in pt:
                failures.append(
                    f"references/phases.md missing turn-numbered section "
                    f"'{label}' — turn-gated shape requires T1..T8 labelling"
                )

    # 33. Stale phase-numbering invariant — promoted from Layer 3 audit on
    #     0.4.8. After the turn-gated redesign, every mention of phases
    #     across SKILL.md and references/*.md must use the T1..T8
    #     convention; the old "Phase 0".."Phase 4" labels are drift
    #     signals. The auditor caught three instances in persistence.md
    #     that would have false-PASSed the other 32 assertions because
    #     none of them look at persistence.md's body text.
    stale_labels = ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    scope = [SKILL_MD] + sorted((HERE.parent / "references").glob("*.md"))
    for md_path in scope:
        if not md_path.exists():
            continue
        body = md_path.read_text()
        for stale in stale_labels:
            # Match the exact legacy label — allow "T3 (Phase 2 in the
            # old numbering)" type migration notes by requiring the stale
            # label to appear WITHOUT an adjacent "old" / "legacy" /
            # "previous" disambiguation in the surrounding 30 chars.
            for m in re.finditer(re.escape(stale), body):
                window = body[max(0, m.start() - 40): m.end() + 40].lower()
                if any(tag in window for tag in ("old", "legacy", "previous", "pre-0.4.8")):
                    continue
                failures.append(
                    f"Stale phase label '{stale}' found in "
                    f"{md_path.relative_to(HERE.parent)} — post-0.4.8 "
                    f"the convention is T1..T8; label it as 'legacy' / "
                    f"'old' in prose if the historical reference is "
                    f"intentional"
                )
                break  # one failure per (file, label) is enough

    if failures:
        print("FAIL council grader:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS council grader — 33 contract checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
