#!/usr/bin/env python3
"""grade.py — Contract grader for the council skill (0.5.0+).

Invoked by plugin-check.py Layer 2. Returns exit 0 if the skill's contract
is intact across the new dual-file progressive-disclosure architecture:

    plugin/
    ├── commands/council.md                 (primary entry — slash command)
    └── skills/council/
        ├── SKILL.md                        (web fallback — explicit opt-in)
        └── references/*.md                 (on-demand only)

Most contract assertions pass if the string lives in EITHER the command
file OR SKILL.md — that gives the 0.5.0 architecture room to move content
between the entry points without tripping the grader, while still keeping
the contract anchored. Architecture-specific assertions (frontmatter
shape, required section headers, slash-command presence) are pinned to
their canonical file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent                       # skills/council/
SKILL_MD = SKILL_DIR / "SKILL.md"
PLUGIN_ROOT = SKILL_DIR.parent.parent         # plugin/
COMMAND_MD = PLUGIN_ROOT / "commands" / "council.md"


def load_skill() -> str:
    if not SKILL_MD.exists():
        print(f"FAIL council: SKILL.md missing at {SKILL_MD}")
        sys.exit(1)
    return SKILL_MD.read_text()


def load_command() -> str:
    # commands/council.md is required for 0.5.0+. Failing to find it is a
    # hard fail — the slash-command entry point is the primary way the
    # skill is invoked in Claude Code and Cowork.
    if not COMMAND_MD.exists():
        print(f"FAIL council: commands/council.md missing at {COMMAND_MD}")
        sys.exit(1)
    return COMMAND_MD.read_text()


def contains_all(text: str, needles: list[str]) -> list[str]:
    return [n for n in needles if n not in text]


def main() -> int:
    skill = load_skill()
    cmd = load_command()
    combined = skill + "\n\n" + cmd          # most assertions check this
    failures: list[str] = []

    # 1. Five MECE roles are explicitly named — in either entry point.
    missing_roles = contains_all(combined, ["Analyst", "Cartographer", "Adversary", "Scout", "Operator"])
    if missing_roles:
        failures.append(f"Roles missing from council entry points: {missing_roles}")

    # 2. Chairman synthesis is named.
    if "Chairman" not in combined:
        failures.append("Chairman synthesis not mentioned in either entry point")

    # 3. Phases are named (case-insensitive).
    lower = combined.lower()
    missing_phases = [p for p in ["orient", "ground", "map", "council", "verdict"] if p not in lower]
    if missing_phases:
        failures.append(f"Phases missing: {missing_phases}")

    # 4. Three depth modes.
    missing_depth = contains_all(combined, ["QUICK", "FULL", "AUDIT"])
    if missing_depth:
        failures.append(f"Depth modes missing: {missing_depth}")

    # 5. Three contexts.
    missing_ctx = contains_all(combined, ["CODE-MODE", "DOC-MODE", "CHAT-MODE"])
    if missing_ctx:
        failures.append(f"Context modes missing: {missing_ctx}")

    # 6. Two-track output.
    if not (re.search(r"OPERATIVE", combined) and re.search(r"MANAGEMENT", combined)):
        failures.append("Two-track output (OPERATIVE + MANAGEMENT) not declared")

    # 7. Persistence line in the T8 output template.
    if "Persistence:" not in combined and "## Persistence" not in combined:
        failures.append(
            "Mandatory persistence block missing from output template — "
            "expected 'Persistence:' (inline) or '## Persistence' (section)"
        )
    if "COUNCIL.md" not in combined:
        failures.append("COUNCIL.md persistence file not documented")

    # 8. Diagnostic question standard includes the mode/context header.
    if "Mode: DIAGNOSTIC" not in combined:
        failures.append("Diagnostic question standard missing 'Mode: DIAGNOSTIC' header")

    # 9. Required SKILL.md blocks (pinned to SKILL.md — the web-fallback
    #    contract requires these section anchors so Claude in Web can
    #    find the language/environment/procedure guidance deterministically).
    for header in (
        "## Language",
        "## Environment detection",
        "## Procedure with file access",
        "## Procedure in Claude AI (Web)",
    ):
        if header not in skill:
            failures.append(f"SKILL.md: {header} section missing")

    # 10. References exist on disk (unchanged — progressive disclosure still
    #     ships the detailed refs, just doesn't eagerly read them).
    for ref in ["roles.md", "phases.md", "persistence.md", "ground.md", "turns.md"]:
        if not (SKILL_DIR / "references" / ref).exists():
            failures.append(f"references/{ref} missing")

    # 11. YAML description ≤ 1024 chars (Anthropic hard truncation limit).
    fm_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", skill, re.DOTALL)
    if fm_match:
        body = fm_match.group(1)
        desc_match = re.search(r"description:\s*>?\s*\n((?:[ \t]+.+\n?)+)", body)
        if desc_match:
            raw = desc_match.group(1)
            folded = " ".join(line.strip() for line in raw.splitlines() if line.strip())
            if len(folded) > 1024:
                failures.append(
                    f"description exceeds 1024-char hard limit "
                    f"({len(folded)} chars) — will be truncated by Claude"
                )
        else:
            failures.append("description field missing from SKILL.md frontmatter")
    else:
        failures.append("YAML frontmatter missing from SKILL.md")

    # 11a. SKILL.md must carry disable-model-invocation: true — the 0.5.0
    #      explicit-opt-in rule. Auto-triggering is blocked; /council is
    #      the primary entry in Claude Code / Cowork, and users in Web
    #      must name the skill explicitly.
    if fm_match:
        body = fm_match.group(1)
        if not re.search(r"disable-model-invocation:\s*true", body):
            failures.append(
                "SKILL.md frontmatter missing 'disable-model-invocation: true' "
                "— the 0.5.0 explicit-opt-in rule requires auto-trigger to be "
                "blocked so /council becomes the primary entry point"
            )

    # 11b. SKILL.md description must point at the /council slash-command
    #      entry so a user who lands on this skill knows the proper path.
    if fm_match:
        body = fm_match.group(1)
        desc_match = re.search(r"description:\s*>?\s*\n((?:[ \t]+.+\n?)+)", body)
        if desc_match:
            raw = desc_match.group(1)
            folded = " ".join(line.strip() for line in raw.splitlines() if line.strip())
            if "/council" not in folded and "council" not in folded.lower():
                failures.append(
                    "SKILL.md description should reference '/council' or the "
                    "council skill by name — it is the fallback for explicit "
                    "invocation, so users must be able to identify it"
                )

    # 12. VERDICT COMPLETENESS principle — the "never stop at sufficient"
    #     standard the user set in feedback_standard_not_sufficient.md.
    combined_lower = combined.lower()
    if "stop only when sure" not in combined_lower:
        failures.append(
            "VERDICT COMPLETENESS principle missing: phrase "
            "'stop only when sure' not found in either entry point"
        )
    if "what would need to become true" not in combined_lower:
        failures.append(
            "VERDICT COMPLETENESS principle missing: phrase "
            "'what would need to become true' not found in either entry point"
        )

    # 13. Anti-pattern "3/5 roles converge, 2/5 inconclusive" must be
    #     explicitly rejected as a status report, not a verdict.
    if "3/5" not in combined or "status report" not in combined:
        failures.append(
            "Anti-pattern '3/5 converge, 2/5 inconclusive is a status "
            "report, not a verdict' framing missing from entry points"
        )

    # 14. GROUND phase — Hersteller + Community names must both appear.
    if "Hersteller" not in combined:
        failures.append(
            "GROUND phase missing: 'Hersteller' (authoritative source) "
            "not referenced in either entry point"
        )
    if "Community" not in combined:
        failures.append(
            "GROUND phase missing: 'Community' source not referenced "
            "in either entry point"
        )

    # 15. GROUND-FIRST rigor duty.
    if "GROUND-FIRST" not in combined:
        failures.append(
            "GROUND-FIRST rigor duty missing — principle must be "
            "encoded as a named duty in an entry point"
        )

    # 16. Grounding section in the output template.
    if "## Grounding" not in combined:
        failures.append(
            "'## Grounding' section missing from output template — "
            "Hersteller + Community must be visible in every verdict"
        )
    if "Manufacturer (Hersteller)" not in combined:
        failures.append(
            "Output template must show 'Manufacturer (Hersteller)' "
            "label so the source is explicit to the reader"
        )

    # 17. Sequence contract: T1..T8 turn ordering (pinned to commands/
    #     council.md where the authoritative turn map lives after 0.5.0).
    #     Accept the ordering in either file; the command file is primary,
    #     the skill carries a copy for the web fallback.
    for source_name, source_text in (("commands/council.md", cmd), ("SKILL.md", skill)):
        turn_block = re.search(r"T1\s+ORIENT.*?T8\s+VERDICT", source_text, re.DOTALL)
        if not turn_block:
            continue
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
                f"{source_name}: turn-ordering check failed — missing labels {missing}"
            )
        else:
            ordered = sorted(positions.items(), key=lambda kv: kv[1])
            if [k for k, _ in ordered] != expected_order:
                failures.append(
                    f"{source_name}: turn ordering wrong — expected "
                    f"{expected_order}, got {[k for k, _ in ordered]}. "
                    f"GROUND (T2) must precede CARTOGRAPHER (T3)."
                )
        break  # only one file needs to carry a valid turn map
    else:
        failures.append(
            "Turn block 'T1 ORIENT … T8 VERDICT' not found in either "
            "SKILL.md or commands/council.md — the turn-gated structure "
            "is not declared"
        )

    # 18. ENFORCEMENT, not just presence — GROUND-FIRST must be followed
    #     by the binding sentence.
    gf_idx = combined.find("GROUND-FIRST")
    if gf_idx >= 0:
        nearby = combined[gf_idx : gf_idx + 2000]
        if "No role speaks before both" not in nearby:
            failures.append(
                "GROUND-FIRST named but its binding sentence 'No role "
                "speaks before both the Hersteller position and the "
                "Community position are on the table' is missing nearby"
            )

    # 19. MECE check must treat grounding as a publication gate.
    if "blocks publication" not in combined:
        failures.append(
            "MECE grounding check must include 'blocks publication' "
            "phrasing so the rule is a gate, not a status line"
        )

    # 20. phases.md must name 'T2 grounding block' as Cartographer input.
    phases_path = SKILL_DIR / "references" / "phases.md"
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

    # --- Turn-gated contract assertions (0.4.8 baseline, live-extended) ----

    # 21. Turn-gated deliberation section in an entry point.
    if "Turn-gated deliberation" not in combined:
        failures.append(
            "Turn-gated deliberation section missing from both entry "
            "points — the live-turn contract (one phase per message + "
            "sentinel) is the structural backbone and must be named"
        )

    # 22. Sentinel format with exact marker string.
    if "=== TURN <N>/<K> COMPLETE — <PHASE NAME> ===" not in combined:
        failures.append(
            "Sentinel format template '=== TURN <N>/<K> COMPLETE — "
            "<PHASE NAME> ===' missing from both entry points — "
            "without an exact format turn boundaries cannot be enforced"
        )

    # 23. Continuation tokens.
    missing_tokens = contains_all(combined, ["NEXT", "REBUTTAL", "DEEPEN", "BRANCH", "ABORT"])
    if missing_tokens:
        failures.append(
            f"Continuation tokens missing from entry points: {missing_tokens}"
        )

    # 24. Role turn micro-format components.
    if "**Thesis (one sentence):**" not in combined:
        failures.append(
            "Role turn micro-format missing '**Thesis (one sentence):**' "
            "marker — without it, a role turn can drift without a position"
        )
    if "**Cross-reference" not in combined:
        failures.append(
            "Role turn micro-format missing '**Cross-reference' marker "
            "— cross-reference is how turns compound"
        )
    if "**Dissent" not in combined:
        failures.append(
            "Role turn micro-format missing '**Dissent' marker — "
            "silent agreement is indistinguishable from not listening"
        )
    if "**Resolvable?**" not in combined:
        failures.append(
            "Role turn micro-format missing '**Resolvable?**' marker "
            "— abstention discipline applies per turn"
        )

    # 25. Chairman citation rule and T8 citations section.
    if "Chairman citation rule" not in combined and "## Citations" not in combined:
        failures.append(
            "Chairman citation rule missing from entry points — the "
            "Chairman's job is to listen, visible only through citation"
        )
    if "## Citations" not in combined:
        failures.append(
            "T8 VERDICT output template missing '## Citations' section"
        )

    # 26. GROUND turn must require visible tool calls.
    if "visible tool" not in combined.lower() and "WebSearch" not in combined:
        failures.append(
            "GROUND turn tool-call requirement missing — the user "
            "must see the grounding was performed, not asserted"
        )

    # 27. Turn counts declared: FULL (8 turns), QUICK (3 turns).
    if "FULL (8 turns)" not in combined:
        failures.append(
            "FULL turn count '(8 turns)' missing — the turn plan "
            "must be announced so K is fixed at T1"
        )
    if "QUICK (3 turns)" not in combined:
        failures.append(
            "QUICK turn count '(3 turns)' missing — the compressed "
            "live-turn plan must be declared"
        )

    # 28. NO-DOWNGRADE for K.
    if "K does not change" not in combined and "K is fixed" not in combined:
        failures.append(
            "NO-DOWNGRADE-for-K rule missing — silent turn-count "
            "reduction mid-run is a documented failure mode that "
            "must be ruled out"
        )

    # 29. references/turns.md must exist and carry worked examples.
    turns_md = SKILL_DIR / "references" / "turns.md"
    if not turns_md.exists():
        failures.append("references/turns.md missing — the live-turn contract reference")
    else:
        turns_text = turns_md.read_text()
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
        if "#21672" not in turns_text:
            failures.append(
                "references/turns.md should name Claude Code issue "
                "#21672 — the documented multi-turn-skill failure mode "
                "this contract defends against"
            )

    # 30. Anti-pattern 'Two phases in one assistant message'.
    if "Two phases in one assistant message" not in combined:
        failures.append(
            "Anti-pattern 'Two phases in one assistant message' "
            "missing — the #21672 collapse pattern must be named"
        )

    # 31. Turn header format defined.
    if "## Turn <N>/<K> — <PHASE NAME>" not in combined:
        failures.append(
            "Turn header template '## Turn <N>/<K> — <PHASE NAME>' "
            "missing — the paired header + sentinel bracket each turn"
        )

    # 32. phases.md must be turn-numbered.
    if phases_path.exists():
        pt = phases_path.read_text()
        for label in (
            "## T1 — ORIENT", "## T2 — GROUND",
            "## T3 — CARTOGRAPHER", "## T4 — ANALYST",
            "## T5 — ADVERSARY", "## T6 — SCOUT",
            "## T7 — OPERATOR", "## T8 — VERDICT",
        ):
            if label not in pt:
                failures.append(
                    f"references/phases.md missing turn-numbered section "
                    f"'{label}' — turn-gated shape requires T1..T8 labelling"
                )

    # 33. Stale phase-numbering invariant.
    stale_labels = ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    scope = [SKILL_MD, COMMAND_MD] + sorted((SKILL_DIR / "references").glob("*.md"))
    for md_path in scope:
        if not md_path.exists():
            continue
        body = md_path.read_text()
        for stale in stale_labels:
            for m in re.finditer(re.escape(stale), body):
                window = body[max(0, m.start() - 40): m.end() + 40].lower()
                if any(tag in window for tag in ("old", "legacy", "previous", "pre-0.4.8")):
                    continue
                try:
                    rel = md_path.relative_to(PLUGIN_ROOT)
                except ValueError:
                    rel = md_path.name
                failures.append(
                    f"Stale phase label '{stale}' found in {rel} — "
                    f"post-0.4.8 the convention is T1..T8"
                )
                break

    # --- 0.5.0 progressive-disclosure architecture assertions --------------

    # 34. commands/council.md exists and is not a stub.
    #     (existence was checked at load; here we check substance.)
    if len(cmd) < 2000:
        failures.append(
            f"commands/council.md is too short ({len(cmd)} chars) — "
            "the slash-command entry must carry the turn-gated contract "
            "inline so a standard run does not require reading references"
        )

    # 35. commands/council.md declares itself self-sufficient for a
    #     standard run (so Claude doesn't pre-load all references).
    if "self-sufficient" not in cmd and "load on demand" not in cmd.lower():
        failures.append(
            "commands/council.md should declare the progressive-disclosure "
            "intent (e.g. 'self-sufficient for a standard run' / "
            "'load on demand') — without this, Claude may eagerly read "
            "all references and lose the 0.5.0 token-reduction gain"
        )

    # 36. SKILL.md (web fallback) points to the command file as primary.
    #     Either by /council reference or by explicit file pointer.
    if "/council" not in skill and "commands/council.md" not in skill:
        failures.append(
            "SKILL.md does not point to the primary slash-command entry "
            "('/council' or 'commands/council.md') — users invoking the "
            "skill directly in Claude Code/Cowork should be redirected"
        )

    # 37. commands/council.md has its own YAML frontmatter with a
    #     description (so the slash-command picker can render it).
    cmd_fm = re.search(r"^---\s*\n(.*?)\n---\s*\n", cmd, re.DOTALL)
    if not cmd_fm:
        failures.append(
            "commands/council.md missing YAML frontmatter — the slash "
            "command picker requires it"
        )
    else:
        if "description:" not in cmd_fm.group(1):
            failures.append(
                "commands/council.md frontmatter missing 'description:' "
                "field — slash-command picker needs it"
            )

    # 38. "No role speaks before both" enforcement binding sentence must
    #     live near the GROUND-FIRST label (already covered by #18, but
    #     confirmed here against the *command* file specifically to ensure
    #     the primary entry carries the rule, not just the fallback).
    gf_cmd = cmd.find("GROUND-FIRST")
    if gf_cmd >= 0:
        nearby_cmd = cmd[gf_cmd : gf_cmd + 2000]
        if "No role speaks before both" not in nearby_cmd:
            failures.append(
                "commands/council.md: GROUND-FIRST label present but the "
                "binding sentence is missing nearby — the primary entry "
                "point must carry the rule, not just the label"
            )

    if failures:
        print("FAIL council grader:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS council grader — 38 contract checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
