#!/usr/bin/env python3
"""
Layer 2 grader for session-docs skill.
Checks structural assertions about the skill's SKILL.md and references.
Exit 0 = PASS, Exit 1 = FAIL.
"""
import sys
import os

skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
skill_md = os.path.join(skill_dir, "SKILL.md")
templates_md = os.path.join(skill_dir, "references", "templates.md")

count_only = len(sys.argv) > 1 and sys.argv[1] == "--count-only"

passes = []
failures = []

def check(condition, name):
    if condition:
        passes.append(name)
    else:
        failures.append(name)

# Read SKILL.md
with open(skill_md) as f:
    skill_content = f.read()

# Read templates.md
with open(templates_md) as f:
    templates_content = f.read()

# Structural assertions
check("name: session-docs" in skill_content, "frontmatter: name field present")
check("description:" in skill_content, "frontmatter: description field present")
check("Do NOT use for" in skill_content, "description: negative scope present")
check("_shared/language.md" in skill_content, "language block references _shared/language.md")
check("_shared/environments.md" in skill_content, "environment block references _shared/environments.md")
check("Procedure in Claude AI (Web)" in skill_content, "web fallback section present")
check("READ MODE" in skill_content, "read mode section present")
check("WRITE MODE" in skill_content, "write mode section present")
check("SESSION CLOSE" in skill_content, "session close section present")
check("FILE CREATION" in skill_content, "file creation / templates section present")
check("never repeat" in skill_content.lower() or "Never repeat" in skill_content, "security: credential rule present")
check("references/templates.md" in skill_content, "references/templates.md referenced from SKILL.md")

# Four triggers present
check("Trigger 1" in skill_content, "trigger 1: new finding → KNOWN_ISSUES")
check("Trigger 2" in skill_content, "trigger 2: direction change → HANDOVER")
check("Trigger 3" in skill_content, "trigger 3: user correction → Memory")
check("Trigger 4" in skill_content, "trigger 4: task step → task list")

# Templates assertions
check("KNOWN_ISSUES.md" in templates_content, "templates: KNOWN_ISSUES.md template present")
check("HANDOVER.md" in templates_content, "templates: HANDOVER.md template present")
check("feedback_" in templates_content, "templates: feedback memory template present")
check("project_" in templates_content, "templates: project memory template present")
check("MEMORY.md index" in templates_content, "templates: MEMORY.md index format present")

# Report
total = len(passes) + len(failures)
if count_only:
    print(total)
    sys.exit(0)
print(f"session-docs grader: PASS={len(passes)} FAIL={len(failures)} TOTAL={total}")
if failures:
    for f in failures:
        print(f"  FAIL: {f}")
    sys.exit(1)
else:
    print("  All assertions passed.")
    sys.exit(0)
