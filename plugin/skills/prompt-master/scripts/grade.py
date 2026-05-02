#!/usr/bin/env python3
"""grade.py — Contract grader for the prompt-master skill.

Invoked by plugin-check.py Layer 2. Protects the load-bearing contracts of
the prompt-master skill that must not silently regress:

- Required skill blocks (Language, Environment, Web procedure).
- Identity and hard-rule list — the rules that prevent fabrication-prone
  techniques and the "no CoT on reasoning-native models" rule.
- Output format contract — single copy-ready block plus the metadata line
  with target and one-line strategy.
- Reference coverage — tools.md, patterns.md, templates.md exist and are
  named from SKILL.md.
- Pattern-3 wiring — the paired commands/prompt-master.md exists.

The "never embed" anti-pattern list is the highest-leverage assertion:
that list is exactly why this skill produces working prompts instead of
the slop that other prompt-generators ship.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"
PLUGIN_ROOT = SKILL_DIR.parent.parent
COMMAND_FILE = PLUGIN_ROOT / "commands" / "prompt-master.md"


def main() -> int:
    count_only = len(sys.argv) > 1 and sys.argv[1] == "--count-only"

    if not SKILL_MD.exists():
        if count_only:
            print(0)
            return 0
        print(f"FAIL prompt-master: SKILL.md missing at {SKILL_MD}")
        return 1

    text = SKILL_MD.read_text()
    failures: list[str] = []
    checks = 0

    # 1. Required skill-structure blocks (NeoMINT plugin standard)
    for section in [
        "## Language",
        "## Environment detection",
        "## Procedure in Claude AI (Web)",
        "## Procedure with file access",
    ]:
        checks += 1
        if section not in text:
            failures.append(f"{section} section missing")

    # 2. Frontmatter has name and description (Anthropic Skills spec)
    checks += 1
    if not re.search(r"^name:\s*prompt-master\s*$", text, re.MULTILINE):
        failures.append("Frontmatter 'name: prompt-master' missing or wrong")
    checks += 1
    if not re.search(r"^description:", text, re.MULTILINE):
        failures.append("Frontmatter 'description:' missing")

    # 3. Description has trigger signals AND negative scope (NeoMINT
    #    SKILL_TEMPLATE.md requirement, enforced by plugin-check.py).
    #    The negative-scope check accepts any of several lexical forms —
    #    promoted from a single phrase ("Do not use for") to a semantic
    #    set in 0.6.16 after Layer 3 audit found the rigid form silently
    #    broke when skill-creator iterated the description's wording.
    checks += 1
    if "Trigger signals" not in text and "trigger" not in text.lower()[:2000]:
        failures.append("Description missing trigger-signal language")
    checks += 1
    negative_scope_markers = [
        "Do not use for",
        "Does not trigger",
        "Do not trigger",
        "do not fire",
        "must not fire",
        "Internally declines",
        "Decline",
    ]
    if not any(m.lower() in text.lower() for m in negative_scope_markers):
        failures.append(
            "Description missing negative-scope clause "
            f"(none of {negative_scope_markers} present)"
        )

    # 4. The "never embed" anti-pattern list — the single most load-bearing
    #    contract of this skill. These techniques produce fabrication when
    #    emulated in a single prompt; the skill exists in part to refuse
    #    them. Each must survive any future edit.
    for technique in [
        "Mixture-of-Experts",
        "Tree-of-Thought",
        "Graph-of-Thought",
        "Universal Self-Consistency",
    ]:
        checks += 1
        if technique not in text:
            failures.append(
                f"Anti-pattern '{technique}' missing from hard-rules list"
            )

    # 5. The reasoning-native-models rule (no CoT on o-series / R1 /
    #    extended thinking). Without this rule the skill ships prompts
    #    that actively degrade output on the most expensive models.
    checks += 1
    if not re.search(
        r"reasoning[- ]native", text, re.IGNORECASE
    ):
        failures.append("Reasoning-native-models rule missing")
    checks += 1
    if not re.search(
        r"Chain[- ]of[- ]Thought|CoT", text
    ):
        failures.append(
            "Chain-of-Thought reference missing (rule cannot exist "
            "without naming the technique it forbids)"
        )

    # 6. Three-question ceiling (prevents the failure mode where the
    #    skill loops on clarifying questions instead of shipping)
    checks += 1
    if not re.search(r"more than\s*(three|3)", text, re.IGNORECASE):
        failures.append("Three-question ceiling missing")

    # 7. Output format contract — single copy-ready block + metadata line
    checks += 1
    if "🎯 Target" not in text and "Target:" not in text:
        failures.append("Output metadata line ('🎯 Target:') missing")
    checks += 1
    if "💡" not in text and "one sentence" not in text.lower():
        failures.append("Output strategy-note line missing")

    # 8. Nine dimensions of intent — the extraction step is the reason
    #    the skill produces sharper prompts than ad-hoc rewrites
    checks += 1
    if "nine dimensions" not in text.lower() and "9 dimensions" not in text:
        failures.append("Nine-dimensions extraction step missing")

    # 9. Reference files exist and are named from SKILL.md
    for ref_name in ["tools.md", "patterns.md", "templates.md"]:
        checks += 1
        if not (REFERENCES / ref_name).exists():
            failures.append(f"references/{ref_name} missing")
        checks += 1
        if ref_name not in text:
            failures.append(f"references/{ref_name} not referenced from SKILL.md")

    # 10. Pattern 3 wiring — paired command file must exist
    checks += 1
    if not COMMAND_FILE.exists():
        failures.append(
            "Paired commands/prompt-master.md missing (Pattern 3 requires it)"
        )

    # 11. MIT attribution preserved (Apache-2.0 §4: notices accompanying
    #     the work must be retained)
    checks += 1
    if "Nidhin Joseph Nelson" not in text and "nidhinjs" not in text:
        failures.append(
            "Upstream MIT attribution to Nidhin Joseph Nelson / nidhinjs "
            "missing from SKILL.md"
        )

    # 12. Architecture-silent rule (MINOR-1 from Layer-3-lite audit, 0.6.16).
    #     The skill must keep stating that the prompt architecture is never
    #     exposed to the user. Without this rule, the skill regresses to
    #     leaking framework labels ("I used Pattern A") into output —
    #     exactly the mode the upstream prompt-master skill avoids.
    checks += 1
    text_lower = text.lower()
    if (
        "never named in the output" not in text_lower
        and "architecture is silent" not in text_lower
        and "never expose" not in text_lower
        and "is never named" not in text_lower
    ):
        failures.append(
            "Architecture-silent rule missing — output must not expose "
            "Pattern A/B/C/D/E/F labels to the user"
        )

    if count_only:
        print(checks)
        return 0

    if failures:
        print(f"FAIL prompt-master grader ({len(failures)}/{checks} failed):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS prompt-master grader — contract intact ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
