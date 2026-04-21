#!/usr/bin/env python3
"""grade.py — Contract grader for the pdf-umbenennen skill.

Invoked by plugin-check.py Layer 2. Validates the skill's filename convention
and that the short-name rules it promises (sender, subject) are actually
complete in SKILL.md. This grader exists because a silent mid-sentence
truncation in the sender rules slipped into 0.4.0 and was only caught by
the generic truncation heuristic — a skill-specific contract check closes
that hole.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_MD = HERE.parent / "SKILL.md"

FILENAME_RE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}_[A-Za-z0-9\-]+_[A-Za-z0-9\-]+\.pdf\b"
)


def main() -> int:
    if not SKILL_MD.exists():
        print(f"FAIL pdf-umbenennen: SKILL.md missing at {SKILL_MD}")
        return 1
    text = SKILL_MD.read_text()
    failures: list[str] = []

    # 1. Filename convention is declared verbatim
    if "yyyy-mm-dd_Sender_Subject-short.pdf" not in text:
        failures.append("Filename convention 'yyyy-mm-dd_Sender_Subject-short.pdf' not present")

    # 2. At least three concrete filename examples that match the convention
    matches = FILENAME_RE.findall(text)
    if len(matches) < 3:
        failures.append(f"Fewer than 3 concrete filename examples ({len(matches)} found)")

    # 3. Umlaut rule is present
    for rule in ["ä→ae", "ö→oe", "ü→ue", "ß→ss"]:
        if rule not in text:
            failures.append(f"Umlaut rule '{rule}' missing")

    # 4. Sender short-name rules cover the core categories
    #    (the 0.4.0 truncation stopped after "Companies: short" — these checks
    #    guarantee all four/five categories survive)
    for keyword in ["Companies", "Banks", "Persons", "Unknown"]:
        if not re.search(rf"\b{keyword}\b", text):
            failures.append(f"Sender short-name category '{keyword}' missing")

    # 5. Subject short-form section exists (added in 0.4.1 fix)
    if "Subject" not in text:
        failures.append("Subject short-form rules section missing")

    # 6. Required skill blocks
    if "## Language" not in text:
        failures.append("## Language section missing")
    if "## Environment detection" not in text:
        failures.append("## Environment detection section missing")
    if "## Procedure with file access" not in text:
        failures.append("## Procedure with file access section missing")
    if "## Procedure in Claude AI (Web)" not in text:
        failures.append("## Procedure in Claude AI (Web) section missing")

    # 7. Parallel-batch guidance (the skill's performance contract)
    if not re.search(r"parallel.*batch", text, re.IGNORECASE):
        failures.append("Parallel-batch guidance missing (performance contract)")

    if failures:
        print("FAIL pdf-umbenennen grader:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS pdf-umbenennen grader — contract intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
