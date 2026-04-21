#!/usr/bin/env python3
"""grade.py — Contract grader for the update-plugin (governance) skill.

Invoked by plugin-check.py Layer 2. Protects the governance skill's own
contract — specifically the three-layer iteration loop, the skill-creator
requirement, and the repackaging rules that must never silently disappear.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
PLUGIN_CHECK = HERE / "plugin-check.py"
REF_PLUGIN_EVAL = SKILL_DIR / "references" / "plugin-eval.md"


def main() -> int:
    failures: list[str] = []

    if not SKILL_MD.exists():
        print(f"FAIL: SKILL.md missing at {SKILL_MD}")
        return 1
    text = SKILL_MD.read_text()

    # 1. Required skill blocks
    for section in ["## Language", "## Environment detection"]:
        if section not in text:
            failures.append(f"{section} section missing")

    # 2. Skill-creator requirement is explicit
    if "skill-creator" not in text:
        failures.append("skill-creator requirement not mentioned")

    # 3. Three-layer loop contract
    for layer in ["Layer 1", "Layer 2", "Layer 3"]:
        if layer not in text:
            failures.append(f"{layer} not referenced in SKILL.md")

    # 4. Layer 1 grader script is bundled
    if not PLUGIN_CHECK.exists():
        failures.append("scripts/plugin-check.py missing (Layer 1 grader not bundled)")

    # 5. Reference doc on the three-layer mechanics is bundled
    if not REF_PLUGIN_EVAL.exists():
        failures.append("references/plugin-eval.md missing")

    # 6. Pre-research is mandatory (Step 0)
    if not re.search(r"Pre[- ]research", text, re.IGNORECASE):
        failures.append("Pre-research step missing from governance")
    if "anthropics/skills" not in text:
        failures.append("Anthropic GitHub reference missing from pre-research")

    # 7. Versioning scheme
    if "major.minor.fix" not in text and "major/minor/fix" not in text:
        failures.append("Versioning scheme (major.minor.fix) not documented")

    # 8. Repackaging rule — build in /tmp, copy into workspace
    #    (this was added in 0.4.0 after a mount-rename failure)
    if "/tmp" not in text:
        failures.append("Build-in-/tmp rule missing from repackaging step")

    # 9. Self-optimisation step
    if "Self-optimisation" not in text and "self-optimisation" not in text.lower():
        failures.append("Self-optimisation step missing")

    # 10. plugin-check.py itself is importable-ish (smoke test: valid Python)
    if PLUGIN_CHECK.exists():
        src = PLUGIN_CHECK.read_text()
        try:
            compile(src, str(PLUGIN_CHECK), "exec")
        except SyntaxError as e:
            failures.append(f"scripts/plugin-check.py has SyntaxError: {e}")

    if failures:
        print("FAIL update-plugin grader:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS update-plugin grader — governance contract intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
