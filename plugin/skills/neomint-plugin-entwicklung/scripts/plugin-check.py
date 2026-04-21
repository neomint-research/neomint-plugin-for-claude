#!/usr/bin/env python3
"""plugin-check.py — Structural + per-skill evaluator for the NeoMINT plugin.

Layers:
  1. Structural assertions on the plugin root (Layer 1).
  2. Orchestration of per-skill eval scripts (Layer 2).

Layer 3 (independent subagent audit) is NOT implemented here — it is run by
the governance skill itself inside a Claude session, because it requires a
reasoning agent, not a deterministic check.

Usage:
  python3 plugin-check.py [PLUGIN_ROOT]

Exit code: 0 if all assertions pass, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Files/folders allowed at the plugin root. Anything else → flagged as stray.
ROOT_WHITELIST = {
    ".claude-plugin",
    "skills",
    "commands",
    "README.md",
    "CHANGELOG.md",
    "SKILL_TEMPLATE.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".github",
    ".gitignore",
    ".git",
}
# *.plugin archives at the root are tolerated; they are what we ship.

# Per-skill subdirectories/files that may exist but are not shipped.
# If the grading script lives at skills/<x>/scripts/grade.py, Layer 2 picks it up.
PER_SKILL_GRADER_CANDIDATES = [
    Path("scripts/grade.py"),
    Path("evals/grade.py"),
]

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

# -----------------------------------------------------------------------------
# Assertion framework
# -----------------------------------------------------------------------------

@dataclass
class Result:
    name: str
    layer: int
    verdict: str  # PASS / FAIL / SKIP
    detail: str = ""

@dataclass
class Report:
    root: str
    results: list[Result] = field(default_factory=list)

    def add(self, name: str, layer: int, ok: bool, detail: str = "") -> None:
        self.results.append(Result(name, layer, "PASS" if ok else "FAIL", detail))

    def skip(self, name: str, layer: int, detail: str) -> None:
        self.results.append(Result(name, layer, "SKIP", detail))

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.verdict == "PASS")

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.verdict == "FAIL")

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.verdict == "SKIP")

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "summary": {
                "pass": self.passed,
                "fail": self.failed,
                "skip": self.skipped,
                "total": len(self.results),
            },
            "results": [
                {"name": r.name, "layer": r.layer, "verdict": r.verdict, "detail": r.detail}
                for r in self.results
            ],
        }


# -----------------------------------------------------------------------------
# Layer 1 — structural assertions
# -----------------------------------------------------------------------------

def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None

def _tail_line(path: Path) -> str:
    try:
        lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
        return lines[-1] if lines else ""
    except Exception:
        return ""

def _ends_well(last_line: str) -> bool:
    """Mid-sentence-truncation heuristic: last non-empty line should end with
    punctuation, a URL, a closing bracket, a code-fence, or a section boundary."""
    if not last_line:
        return False
    last_line = last_line.rstrip()
    if not last_line:
        return False
    # obvious terminal tokens
    if last_line.endswith((".", "!", "?", ")", "]", "*", "`", ">")):
        return True
    # section boundary / YAML / markdown horizontal rule
    if last_line in ("---", "```"):
        return True
    # url-ending (url shouldn't end mid-word)
    if re.search(r"https?://\S+$", last_line):
        return True
    return False

def _yaml_frontmatter(path: Path) -> dict | None:
    try:
        text = path.read_text()
    except Exception:
        return None
    m = re.match(r"---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    body = m.group(1)
    fields: dict[str, str] = {}
    current_key: str | None = None
    for line in body.splitlines():
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_\-]*\s*:", line):
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip().strip(">").strip()
            current_key = k.strip()
        elif current_key and line.startswith((" ", "\t")):
            fields[current_key] = (fields.get(current_key, "") + " " + line.strip()).strip()
    return fields


def run_layer1(root: Path, rep: Report) -> None:
    # --- plugin.json ---
    plugin_json = root / ".claude-plugin" / "plugin.json"
    data = _read_json(plugin_json)
    rep.add("plugin.json exists", 1, plugin_json.exists(), str(plugin_json))
    rep.add("plugin.json valid JSON", 1, data is not None,
            "invalid or unreadable" if data is None else "parsed OK")
    if data:
        rep.add("plugin.json has name", 1, bool(data.get("name")), str(data.get("name")))
        rep.add("plugin.json has version", 1, bool(data.get("version")), str(data.get("version")))
        rep.add("plugin.json has description", 1, bool(data.get("description")))
        rep.add("plugin.json has author", 1, bool(data.get("author")))
        version = str(data.get("version", ""))
        rep.add("version matches major.minor.fix", 1, bool(VERSION_RE.match(version)), version)

    # --- CHANGELOG / version consistency ---
    changelog = root / "CHANGELOG.md"
    rep.add("CHANGELOG.md exists", 1, changelog.exists())
    if changelog.exists() and data:
        text = changelog.read_text()
        # find the first "## <version>" line
        m = re.search(r"^##\s+([0-9]+\.[0-9]+\.[0-9]+)\b", text, re.MULTILINE)
        top_version = m.group(1) if m else None
        rep.add("CHANGELOG top entry matches plugin.json version", 1,
                top_version == data.get("version"),
                f"CHANGELOG top={top_version} vs plugin.json={data.get('version')}")

    # --- README ---
    readme = root / "README.md"
    rep.add("README.md exists", 1, readme.exists())
    if readme.exists():
        readme_text = readme.read_text()
        rep.add("README not mid-sentence truncated", 1, _ends_well(_tail_line(readme)),
                _tail_line(readme)[:80])

    # --- SKILL_TEMPLATE ---
    tpl = root / "SKILL_TEMPLATE.md"
    rep.add("SKILL_TEMPLATE.md exists", 1, tpl.exists())

    # --- _shared ---
    shared = root / "skills" / "_shared"
    rep.add("_shared/language.md exists", 1, (shared / "language.md").exists())
    rep.add("_shared/environments.md exists", 1, (shared / "environments.md").exists())

    # --- root stray files ---
    # The ONE permitted *.plugin archive is `<plugin-name>.plugin`, where
    # plugin-name comes from plugin.json. Any other *.plugin (e.g. a
    # test-*.plugin or versioned artefact like neomint-toolkit-0.4.5.plugin)
    # is stray build state — the canonical build procedure overwrites the
    # single named file. This rule was tightened when a stray
    # `test-neomint-toolkit.plugin` was found during the 0.4.6 cycle; the
    # old rule tolerated any file ending in ".plugin" and the archive-
    # cleanliness assertion picked `plugins[-1]` alphabetically, so the
    # wrong file was being validated.
    canonical_archive_name: str | None = None
    if isinstance(data, dict) and isinstance(data.get("name"), str):
        canonical_archive_name = f"{data['name']}.plugin"
    if root.exists():
        extras = []
        for p in root.iterdir():
            name = p.name
            if name in ROOT_WHITELIST:
                continue
            if name.endswith(".plugin"):
                if canonical_archive_name and name == canonical_archive_name:
                    continue
                # any other *.plugin is stray
            extras.append(name)
        rep.add("No stray files at plugin root", 1, not extras,
                "stray: " + ", ".join(extras) if extras else "clean")

    # --- shipping archive contents match root whitelist ---
    # If a *.plugin archive is present at the plugin root, its top-level
    # entries must be a subset of (ROOT_WHITELIST ∪ known shipped items).
    # This catches build-time mistakes that pack sibling folders by
    # accident — e.g. zipping from /tmp instead of from the plugin root.
    # The 0.4.4 → 0.4.5 cycle surfaced exactly this failure: a snapshot
    # folder leaked into the archive and only got caught manually.
    import zipfile
    # Validate the CANONICAL archive (<plugin-name>.plugin) specifically,
    # not "whichever .plugin sorts last". The previous implementation used
    # `plugins[-1]` and silently validated a stray test artefact when two
    # .plugin files coexisted — the canonical-archive rule now prevents
    # that coexistence, but this assertion is belt-and-braces.
    archive: Path | None = None
    if canonical_archive_name:
        candidate = root / canonical_archive_name
        if candidate.exists():
            archive = candidate
    if archive is None:
        rep.skip("Shipping archive contents are clean", 1,
                 f"no {canonical_archive_name or '*.plugin'} at plugin root")
    else:
        try:
            with zipfile.ZipFile(archive) as zf:
                top_level = set()
                for member in zf.namelist():
                    m = member
                    # strip a single leading "./" prefix if present.
                    # NOT lstrip — that would also eat a leading "." from
                    # ".claude-plugin" and corrupt the top-level name.
                    if m.startswith("./"):
                        m = m[2:]
                    if not m:
                        continue
                    head = m.split("/", 1)[0]
                    top_level.add(head)
            # Allowed top-level entries inside the archive: the root
            # whitelist minus entries that are never shipped (.git,
            # repo-publication files), plus nothing else. Any extra
            # entry is build-time leakage.
            never_shipped = {
                ".git",
                ".gitignore",
                ".github",
                "CONTRIBUTING.md",
            }
            allowed = (ROOT_WHITELIST - never_shipped)
            stray_in_archive = sorted(top_level - allowed)
            rep.add(
                "Shipping archive contents are clean",
                1,
                not stray_in_archive,
                f"archive={archive.name}; "
                + ("stray entries: " + ", ".join(stray_in_archive)
                   if stray_in_archive else "clean"),
            )
        except zipfile.BadZipFile:
            rep.add("Shipping archive contents are clean", 1, False,
                    f"{archive.name} is not a valid zip archive")

    # --- documented build commands match never_shipped design ---
    # Promoted from Layer 3 (0.4.5 → 0.4.6 cycle). Defect pattern: a build
    # command in README.md or CONTRIBUTING.md excludes a file (via `-x`)
    # that is actually supposed to ship inside the .plugin bundle, or
    # forgets to exclude a file that never_shipped says must not ship.
    # Either way the documented procedure produces an archive that
    # disagrees with the coded design — Layer 1 would currently false-PASS
    # because the archive check only catches EXTRA content, not MISSING
    # content. This assertion catches both halves before the archive is
    # ever built.
    #
    # Design assumption: LICENSE, SECURITY.md (and any other root file in
    # ROOT_WHITELIST minus never_shipped, minus pure transients) must NOT
    # appear in any documented -x exclusion. Every name in never_shipped
    # that exists as a real root entry MUST appear in every documented
    # build command's exclusion list.
    import fnmatch
    never_shipped_design = {".git", ".gitignore", ".github", "CONTRIBUTING.md"}
    ships_at_root = ROOT_WHITELIST - never_shipped_design - {".git", ".gitignore"}
    for doc_name in ("README.md", "CONTRIBUTING.md"):
        doc_path = root / doc_name
        if not doc_path.exists():
            continue
        doc_text = doc_path.read_text()
        # extract -x "foo" and -x 'foo' patterns — zip glob patterns
        raw_patterns = [
            m.group(1)
            for m in re.finditer(r"""-x\s+["']([^"']+)["']""", doc_text)
        ]
        # For exact-match checks (did the doc mention this literal file?),
        # normalise trailing /* off e.g. "*.github/*" → "*.github" then
        # strip the leading "*" so ".github" is recognised as intended.
        literal_exclusions = set()
        for p in raw_patterns:
            q = p
            if q.endswith("/*"):
                q = q[:-2]
            if q.startswith("*") and len(q) > 1:
                q = q[1:]
            literal_exclusions.add(q)
        def excluded_by_patterns(name: str) -> bool:
            """True if any raw zip-glob pattern matches this root filename."""
            return any(fnmatch.fnmatch(name, pat) for pat in raw_patterns)
        # check: every ships_at_root file is NOT excluded (neither by
        # literal name in the exclusion list nor by a glob that matches it)
        wrongly_excluded = sorted(
            name for name in ships_at_root
            if name in literal_exclusions or excluded_by_patterns(name)
        )
        rep.add(
            f"[{doc_name}] build cmd does not exclude shipped root files",
            1,
            not wrongly_excluded,
            ("wrongly excludes: " + ", ".join(wrongly_excluded))
            if wrongly_excluded else "clean",
        )
        # check: every never_shipped file present at root IS excluded
        # (we only demand the check if the file actually exists — an
        # absent .gitignore in a fresh clone shouldn't force a mention)
        missing_exclusions = sorted(
            name for name in never_shipped_design
            if (root / name).exists()
            and name not in literal_exclusions
            and not excluded_by_patterns(name)
        )
        rep.add(
            f"[{doc_name}] build cmd excludes every never-shipped root file",
            1,
            not missing_exclusions,
            ("missing exclusions: " + ", ".join(missing_exclusions))
            if missing_exclusions else "clean",
        )

    # --- per-skill SKILL.md checks ---
    skills_dir = root / "skills"
    if not skills_dir.exists():
        rep.add("skills/ exists", 1, False)
        return
    readme_text = (root / "README.md").read_text() if (root / "README.md").exists() else ""
    skill_names: list[str] = []
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir() and p.name != "_shared"):
        name = skill_dir.name
        skill_names.append(name)
        skill_md = skill_dir / "SKILL.md"
        rep.add(f"[{name}] SKILL.md exists", 1, skill_md.exists())
        if not skill_md.exists():
            continue
        fm = _yaml_frontmatter(skill_md)
        rep.add(f"[{name}] YAML frontmatter parses", 1, fm is not None)
        if fm:
            rep.add(f"[{name}] frontmatter.name present", 1, bool(fm.get("name")), fm.get("name", ""))
            rep.add(f"[{name}] frontmatter.description present", 1, bool(fm.get("description")))
            # description ≤ 1024 chars — Anthropic truncates longer ones.
            # The parser folds continuation lines with single spaces,
            # which matches what Claude sees from a YAML `>` scalar.
            desc = fm.get("description", "")
            desc_len = len(desc)
            rep.add(
                f"[{name}] description ≤ 1024 chars",
                1,
                desc_len <= 1024,
                f"{desc_len} chars ({'OK' if desc_len <= 1024 else 'will be truncated'})",
            )
        text = skill_md.read_text()
        rep.add(f"[{name}] references _shared/language.md", 1,
                "_shared/language.md" in text)
        rep.add(f"[{name}] references _shared/environments.md", 1,
                "_shared/environments.md" in text)
        rep.add(f"[{name}] SKILL.md not mid-sentence truncated", 1,
                _ends_well(_tail_line(skill_md)), _tail_line(skill_md)[:80])
        # Required-block check: every SKILL.md must declare the two canonical
        # procedure sections defined by the plugin standard (README
        # "Plugin standards" and SKILL_TEMPLATE.md). Promoted to Layer 1 in
        # 0.5.1 after a Layer 3 audit found the governance skill itself
        # silently missing both headings — the kind of drift a wording check
        # can't catch but a structural assertion can.
        rep.add(
            f"[{name}] has '## Procedure with file access (Claude Code & Cowork)'",
            1,
            "## Procedure with file access (Claude Code & Cowork)" in text,
        )
        rep.add(
            f"[{name}] has '## Procedure in Claude AI (Web)'",
            1,
            "## Procedure in Claude AI (Web)" in text,
        )
        # check referenced files under references/ actually exist — but only
        # references mentioned in *prose*. Strip fenced code blocks and
        # backticked spans first so placeholders like `references/X.md` or
        # `references/<topic>.md` inside documentation examples don't trip
        # the check.
        prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        prose = re.sub(r"`[^`]*`", "", prose)
        for rel in re.findall(r"references/([\w\-./]+\.md)", prose):
            # skip obvious placeholders that slipped through
            if any(ch in rel for ch in ("<", ">")):
                continue
            ref_path = skill_dir / "references" / rel
            rep.add(f"[{name}] references/{rel} exists", 1, ref_path.exists())

    # --- README mentions every skill, no ghost skills ---
    if readme_text and skill_names:
        for s in skill_names:
            rep.add(f"README mentions skill '{s}'", 1, s in readme_text)
        # ghost skill check: look for skill-like headings in README that don't exist on disk
        # conservative: only flag backticked skill names `foo` that look like skills
        mentioned = set(re.findall(r"`([a-z][a-z0-9\-]+)`", readme_text))
        suspicious = {m for m in mentioned if "-" in m or m in skill_names}
        # Known external skill/tool names legitimately referenced by README —
        # not ghosts. If the README cites an Anthropic-provided skill (like
        # `skill-creator`) or a well-known third-party tool name, we allow
        # it without requiring the skill to live inside this plugin tree.
        KNOWN_EXTERNAL = {
            "skill-creator",
            "claude-plugins-official",
            "claude-code",
        }
        # YAML frontmatter field names legitimately quoted in README as
        # part of the plugin standard — they are not skills and must not
        # be flagged as ghosts. Add new field names here as they appear.
        KNOWN_FRONTMATTER_FIELDS = {
            "disable-model-invocation",
            "argument-hint",
            "allowed-tools",
        }
        ghosts = [m for m in suspicious if m and m not in skill_names and m not in {
            "neomint-toolkit", "plugin.json", "SKILL.md", "README.md", "CHANGELOG.md",
            "SKILL_TEMPLATE.md", "language.md", "environments.md",
        } and m not in KNOWN_EXTERNAL
        and m not in KNOWN_FRONTMATTER_FIELDS
        and not m.endswith(".md") and not m.endswith(".json") and not m.endswith(".plugin")
        and m not in {"major", "minor", "fix"}]
        # filter out anything that looks like a path component or file
        ghosts = [g for g in ghosts if "/" not in g and "." not in g]
        # heuristic threshold: only flag if it plausibly looks like a skill name
        ghosts = [g for g in ghosts if g.startswith(tuple("abcdefghijklmnopqrstuvwxyz")) and len(g) > 3]
        rep.add("README has no ghost-skill references", 1, not ghosts,
                ("ghosts: " + ", ".join(ghosts)) if ghosts else "clean")

    # --- commands/ ↔ skills/ pairing (explicit-invocation contract) ---
    # Introduced in 0.5.0 with the council slash-command refactor.
    # The standard (README, governance SKILL.md) says: the `commands/` directory
    # is relevant ONLY for explicit-invocation skills, and the pairing is
    # bidirectional:
    #
    #   commands/<name>.md  ⇔  skills/<name>/SKILL.md with disable-model-invocation: true
    #
    # This assertion catches both halves of the contract going silently out of
    # sync — e.g. a command added without its skill being marked non-auto
    # (so the skill would still auto-fire and race the command), or a skill
    # marked non-auto without its command (so the skill is unreachable in
    # Claude Code / Cowork). The Layer 3 audit on 0.5.0 surfaced the gap; this
    # assertion promotes it into a Layer 1 assertion so the standard is
    # enforced going forward, not just for council.
    commands_dir = root / "commands"
    commands: dict[str, Path] = {}
    if commands_dir.exists() and commands_dir.is_dir():
        for cmd_file in commands_dir.iterdir():
            if cmd_file.is_file() and cmd_file.suffix == ".md":
                commands[cmd_file.stem] = cmd_file

    # Collect skills with disable-model-invocation: true
    non_auto_skills: set[str] = set()
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir() and p.name != "_shared"):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = _yaml_frontmatter(skill_md)
        if fm and fm.get("disable-model-invocation", "").strip().lower() == "true":
            non_auto_skills.add(skill_dir.name)

    # Forward direction: every commands/<name>.md needs a paired non-auto skill
    for cmd_name, cmd_path in sorted(commands.items()):
        paired_skill_md = skills_dir / cmd_name / "SKILL.md"
        paired_exists = paired_skill_md.exists()
        paired_non_auto = cmd_name in non_auto_skills
        ok = paired_exists and paired_non_auto
        if not paired_exists:
            detail = f"missing skills/{cmd_name}/SKILL.md"
        elif not paired_non_auto:
            detail = f"skills/{cmd_name}/SKILL.md missing disable-model-invocation: true"
        else:
            detail = "paired"
        rep.add(
            f"commands/{cmd_name}.md pairs with a non-auto skill",
            1, ok, detail,
        )

    # Reverse direction: every non-auto skill needs a paired command file
    for skill_name in sorted(non_auto_skills):
        has_cmd = skill_name in commands
        rep.add(
            f"[{skill_name}] disable-model-invocation skill has a paired command",
            1, has_cmd,
            "paired" if has_cmd
            else f"missing commands/{skill_name}.md — skill would be unreachable in Claude Code / Cowork",
        )


# -----------------------------------------------------------------------------
# Layer 2 — per-skill evals
# -----------------------------------------------------------------------------

def run_layer2(root: Path, rep: Report) -> None:
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir() and p.name != "_shared"):
        name = skill_dir.name
        grader: Path | None = None
        for candidate in PER_SKILL_GRADER_CANDIDATES:
            if (skill_dir / candidate).exists():
                grader = skill_dir / candidate
                break
        if grader is None:
            rep.skip(f"[{name}] per-skill eval", 2, "no grader script found (skipping)")
            continue
        try:
            proc = subprocess.run(
                [sys.executable, str(grader)],
                capture_output=True, text=True, timeout=120,
            )
            ok = proc.returncode == 0
            tail = (proc.stdout or "").strip().splitlines()[-3:]
            rep.add(f"[{name}] per-skill eval passes", 2, ok,
                    " | ".join(tail) or proc.stderr[:200])
        except Exception as e:
            rep.add(f"[{name}] per-skill eval runs", 2, False, str(e))


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    rep = Report(root=str(root))
    run_layer1(root, rep)
    run_layer2(root, rep)

    # print human summary
    print(f"Plugin check: {rep.root}")
    print(f"  Layer 1 (structural) + Layer 2 (per-skill evals)")
    print(f"  PASS={rep.passed}  FAIL={rep.failed}  SKIP={rep.skipped}  TOTAL={len(rep.results)}")
    print()
    if rep.failed:
        print("Failures:")
        for r in rep.results:
            if r.verdict == "FAIL":
                print(f"  [L{r.layer}] {r.name}")
                if r.detail:
                    print(f"        → {r.detail}")
    if rep.skipped:
        print()
        print("Skipped (informational):")
        for r in rep.results:
            if r.verdict == "SKIP":
                print(f"  [L{r.layer}] {r.name} — {r.detail}")

    # write JSON report outside the plugin root to avoid polluting it
    report_path = Path("/tmp") / "plugin-check-report.json"
    try:
        report_path.write_text(json.dumps(rep.to_dict(), indent=2))
        print()
        print(f"Report written: {report_path}")
    except Exception as e:
        print(f"(report write skipped: {e})")

    return 0 if rep.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
