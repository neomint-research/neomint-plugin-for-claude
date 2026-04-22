#!/usr/bin/env python3
"""grade.py — Contract grader for the rename-pdf skill.

Invoked by plugin-check.py Layer 2. Validates the skill's filename convention
and that the short-name rules it promises (sender, subject) are actually
complete in SKILL.md. This grader was inherited from the previous
pdf-umbenennen skill and renamed along with the skill in 0.6.0, because the
underlying failure mode it was built to catch — a silent mid-sentence
truncation in the sender rules slipping into a release — is independent of
the skill's name.
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
    # --count-only returns just the assertion count, so external tools
    # (plugin-check.py, docs generators) can link to the current number
    # without re-implementing the grader. Added 0.6.4 (P12) to replace
    # the 0.6.1 "counts drift" hedge with a self-reporting structure.
    count_only = len(sys.argv) > 1 and sys.argv[1] == "--count-only"

    if not SKILL_MD.exists():
        if count_only:
            print(0)
            return 0
        print(f"FAIL rename-pdf: SKILL.md missing at {SKILL_MD}")
        return 1
    text = SKILL_MD.read_text()
    failures: list[str] = []
    # Assertion-count is the number of individual checks attempted. Each
    # `checks += 1` below marks one logical assertion (loop iterations
    # count because each iteration is an independent check).
    checks = 0

    # 1. Filename convention is declared verbatim
    checks += 1
    if "yyyy-mm-dd_Sender_Subject-short.pdf" not in text:
        failures.append("Filename convention 'yyyy-mm-dd_Sender_Subject-short.pdf' not present")

    # 2. At least three concrete filename examples that match the convention
    checks += 1
    matches = FILENAME_RE.findall(text)
    if len(matches) < 3:
        failures.append(f"Fewer than 3 concrete filename examples ({len(matches)} found)")

    # 3. Umlaut rule is present
    for rule in ["ä→ae", "ö→oe", "ü→ue", "ß→ss"]:
        checks += 1
        if rule not in text:
            failures.append(f"Umlaut rule '{rule}' missing")

    # 4. Sender short-name rules cover the core categories
    #    (the 0.4.0 truncation stopped after "Companies: short" — these checks
    #    guarantee all four/five categories survive)
    for keyword in ["Companies", "Banks", "Persons", "Unknown"]:
        checks += 1
        if not re.search(rf"\b{keyword}\b", text):
            failures.append(f"Sender short-name category '{keyword}' missing")

    # 5. Subject short-form section exists (added in 0.4.1 fix)
    checks += 1
    if "Subject" not in text:
        failures.append("Subject short-form rules section missing")

    # 6. Required skill blocks
    checks += 1
    if "## Language" not in text:
        failures.append("## Language section missing")
    checks += 1
    if "## Environment detection" not in text:
        failures.append("## Environment detection section missing")
    checks += 1
    if "## Procedure with file access" not in text:
        failures.append("## Procedure with file access section missing")
    checks += 1
    if "## Procedure in Claude AI (Web)" not in text:
        failures.append("## Procedure in Claude AI (Web) section missing")

    # 7. Parallel-batch guidance (the skill's performance contract)
    checks += 1
    if not re.search(r"parallel.*batch", text, re.IGNORECASE):
        failures.append("Parallel-batch guidance missing (performance contract)")

    if count_only:
        print(checks)
        return 0

    if failures:
        print(f"FAIL rename-pdf grader ({len(failures)}/{checks} failed):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS rename-pdf grader — contract intact ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
