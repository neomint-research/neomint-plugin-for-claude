#!/usr/bin/env python3
"""grade.py — Contract grader for the video-preview skill.

Invoked by plugin-check.py Layer 2. Protects the key technical and
structural contracts of video-preview that must not silently disappear:
viewport standard, Signal-compatibility flag, and output naming convention.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
REF_PUPPETEER = SKILL_DIR / "references" / "puppeteer-patterns.md"


def main() -> int:
    count_only = len(sys.argv) > 1 and sys.argv[1] == "--count-only"

    failures: list[str] = []

    if not SKILL_MD.exists():
        if count_only:
            print(0)
            return 0
        print(f"FAIL: SKILL.md missing at {SKILL_MD}")
        return 1

    text = SKILL_MD.read_text()
    checks = 0

    # 1. Required skill structure blocks
    for section in ["## Language", "## Environment detection"]:
        checks += 1
        if section not in text:
            failures.append(f"{section} section missing")

    # 2. Viewport standard is documented (1080×1920 or 1080x1920)
    checks += 1
    if "1080" not in text or "1920" not in text:
        failures.append(
            "Viewport standard (1080×1920) not documented in SKILL.md"
        )

    # 3. Signal-compatibility flag documented
    checks += 1
    if "-movflags +faststart" not in text and "movflags" not in text:
        failures.append(
            "ffmpeg -movflags +faststart flag not documented "
            "(required for instant Signal/WhatsApp playback)"
        )

    # 4. Output naming convention documented
    checks += 1
    if "yyyy-mm-dd" not in text:
        failures.append(
            "Output naming convention (yyyy-mm-dd) not documented in SKILL.md"
        )

    # 5. Web fallback section present
    checks += 1
    if "## Procedure in Claude AI (Web)" not in text:
        failures.append("Web fallback section missing")

    # 6. Puppeteer patterns reference file is bundled
    checks += 1
    if not REF_PUPPETEER.exists():
        failures.append("references/puppeteer-patterns.md missing")

    if count_only:
        print(checks)
        return 0

    if failures:
        print(f"FAIL video-preview grader ({len(failures)}/{checks} failed):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(
        f"PASS video-preview grader — technical contract intact ({checks} checks)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
