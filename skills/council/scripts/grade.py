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
    if "Persistence:" not in text:
        failures.append("Mandatory 'Persistence:' line missing from output template")
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

    # 17. Sequence contract: GROUND precedes MAP and COUNCIL in the
    #     phase list. The user's rule: "erst das wird diskutiert" —
    #     grounding must come BEFORE the Cartographer and before the
    #     judging roles, not as an appendix.
    #     Detect by checking the phase block ordering.
    phase_block = re.search(
        r"0\s+ORIENT.*?4\s+VERDICT", text, re.DOTALL
    )
    if phase_block:
        block = phase_block.group(0)
        # All four must appear and in order
        positions = {
            label: block.find(label)
            for label in ("ORIENT", "GROUND", "MAP", "COUNCIL", "VERDICT")
        }
        if any(p < 0 for p in positions.values()):
            failures.append(
                "Phase ordering check failed: one of "
                "ORIENT/GROUND/MAP/COUNCIL/VERDICT missing from phase block"
            )
        else:
            ordered = sorted(positions.items(), key=lambda kv: kv[1])
            expected = ["ORIENT", "GROUND", "MAP", "COUNCIL", "VERDICT"]
            if [k for k, _ in ordered] != expected:
                failures.append(
                    f"Phase ordering wrong — expected {expected}, got "
                    f"{[k for k, _ in ordered]}. GROUND must come "
                    f"between ORIENT and MAP."
                )
    else:
        failures.append(
            "Phase block '0 ORIENT … 4 VERDICT' not found in SKILL.md — "
            "the five-phase structure is not declared"
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

    # 20. The MAP phase (Phase 2) must name the grounding block as
    #     input in prose — a future reorder that drops this coupling
    #     would silently decouple MAP from GROUND and restore pre-0.4.4
    #     behaviour.
    phases_path = HERE.parent / "references" / "phases.md"
    if phases_path.exists():
        phases_text = phases_path.read_text()
        map_match = re.search(
            r"## Phase 2 — MAP.*?(?=## Phase 3)", phases_text, re.DOTALL
        )
        if not map_match:
            failures.append(
                "references/phases.md missing '## Phase 2 — MAP' "
                "section — Phase 2 structure cannot be verified"
            )
        else:
            map_block = map_match.group(0)
            if "grounding block" not in map_block and "Phase 1" not in map_block:
                failures.append(
                    "Phase 2 MAP must name 'grounding block' or "
                    "'Phase 1' as input — coupling to GROUND is not "
                    "enforced in prose"
                )
    else:
        failures.append("references/phases.md missing")

    if failures:
        print("FAIL council grader:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS council grader — 20 contract checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
