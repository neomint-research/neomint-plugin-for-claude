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
# *.plugin archives are NEVER permitted at the plugin root.
# Distribution is via GitHub Releases (or equivalent); the build
# artefact lives in /tmp/<plugin-name>-workspace/. This was the policy
# change in 0.6.0 — see references/plugin-eval.md "Workspace path".

# Runtime artefacts that must never appear anywhere in the plugin tree
# or in the repo root next to it. Iteration outputs (eval runs, snapshots,
# eval-viewer HTML, plugin-check reports, council session logs) all live
# in /tmp/<plugin-name>-workspace/.
RUNTIME_ARTEFACT_BASENAMES = {
    "COUNCIL.md",
    "iteration-workspace",
    "skill-snapshot",
}
RUNTIME_ARTEFACT_GLOBS = (
    "*.plugin",
    "*-workspace",
    "eval-viewer-iter*.html",
    "plugin-check-report.json",
)

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


def run_layer1(root: Path, rep: Report, strict_release: bool = False) -> None:
    # --- plugin.json ---
    plugin_json = root / ".claude-plugin" / "plugin.json"
    data = _read_json(plugin_json)
    rep.add("plugin.json exists", 1, plugin_json.exists(), str(plugin_json))
    rep.add("plugin.json valid JSON", 1, data is not None,
            "invalid or unreadable" if data is None else "parsed OK")
    # Trailing newline — POSIX convention, not strictly JSON-required, but
    # tools that diff/append/concatenate JSON files (and some editors)
    # behave better when the file ends in \n. Promoted to Layer 1 in 0.6.2
    # after plugin.json silently lost its trailing newline twice in a row
    # during the 0.6.0/0.6.1 cycles — both times only caught by a manual
    # `tail -c` after the fact. Trivial to enforce.
    if plugin_json.exists():
        try:
            ends_lf = plugin_json.read_bytes().endswith(b"\n")
        except Exception:
            ends_lf = False
        rep.add("plugin.json ends with newline", 1, ends_lf,
                "ok" if ends_lf else "missing trailing \\n")
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
        # Mid-sentence truncation heuristic (promoted to CHANGELOG in 0.6.1
        # after a silent truncation of the 0.4.0 entry — "- `README.md`
        # rebuilt: th" — survived two release cycles because the heuristic
        # only walked README.md and SKILL.md. Extending it here closes that
        # gap; truncated changelog entries are now caught deterministically.)
        rep.add("CHANGELOG not mid-sentence truncated", 1,
                _ends_well(_tail_line(changelog)), _tail_line(changelog)[:80])

    # --- README ---
    readme = root / "README.md"
    rep.add("README.md exists", 1, readme.exists())
    if readme.exists():
        readme_text = readme.read_text()
        rep.add("README not mid-sentence truncated", 1, _ends_well(_tail_line(readme)),
                _tail_line(readme)[:80])
        # Version-reference drift check (promoted to Layer 1 in 0.6.2 after
        # plugin/README.md silently disagreed with plugin.json across two
        # release cycles — every bump required a manual edit to line ~5
        # ("**Current version:** `0.x.y`") and the heuristic "I'll
        # remember" failed. Now deterministic: any backticked version-
        # looking token in README must equal plugin.json's version. We
        # only assert if at least one such token exists, so a README that
        # legitimately omits a version line (e.g. a fresh plugin) is not
        # forced to add one.
        if data and data.get("version"):
            current = str(data["version"])
            readme_versions = re.findall(r"`([0-9]+\.[0-9]+\.[0-9]+)`", readme_text)
            if readme_versions:
                # Every version-looking backticked token must match — drift
                # in any one of them is a defect.
                wrong = sorted({v for v in readme_versions if v != current})
                rep.add(
                    "README version reference matches plugin.json",
                    1,
                    not wrong,
                    f"plugin.json={current}, README has stray: {', '.join(wrong)}"
                    if wrong else f"all instances == {current}",
                )

    # --- SKILL_TEMPLATE ---
    tpl = root / "SKILL_TEMPLATE.md"
    rep.add("SKILL_TEMPLATE.md exists", 1, tpl.exists())

    # --- _shared ---
    shared = root / "skills" / "_shared"
    rep.add("_shared/language.md exists", 1, (shared / "language.md").exists())
    rep.add("_shared/environments.md exists", 1, (shared / "environments.md").exists())

    # --- root stray files ---
    # The plugin root holds source only — the whitelist is the closed set
    # of source entries listed above. No *.plugin archive is permitted at
    # the root (changed in 0.6.0; the build artefact lives in
    # /tmp/<plugin-name>-workspace/ and ships via GitHub Releases). Any
    # entry outside the whitelist is stray, full stop.
    if root.exists():
        extras = sorted(p.name for p in root.iterdir() if p.name not in ROOT_WHITELIST)
        rep.add(
            "No stray files at plugin root",
            1,
            not extras,
            "stray: " + ", ".join(extras) if extras else "clean",
        )

    # --- runtime-artefact sweep across the plugin tree and repo root ---
    # Promoted to Layer 1 in 0.6.0 after iteration-1 of the update-plugin
    # rename surfaced four classes of artefact that had silently lived in
    # the source tree: an iteration workspace, a skill-snapshot folder, a
    # built *.plugin archive, and the council session log COUNCIL.md.
    # The new rule: nothing matching RUNTIME_ARTEFACT_BASENAMES or
    # RUNTIME_ARTEFACT_GLOBS may exist anywhere in the plugin tree, nor
    # one level up at the repo root next to the plugin folder.
    import fnmatch
    def _is_artefact(name: str) -> bool:
        if name in RUNTIME_ARTEFACT_BASENAMES:
            return True
        return any(fnmatch.fnmatch(name, g) for g in RUNTIME_ARTEFACT_GLOBS)

    # Directories that may legitimately contain artefact-looking files
    # at the REPO-ROOT level but must still not produce hits inside them.
    # These are infrastructure / VCS dirs that this check has no business
    # walking. The plugin tree itself is walked in full minus .git.
    REPO_ROOT_SWEEP_SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}

    # `dist/` at the repo root is the official delivery transition zone
    # (added in 0.6.2 after the /tmp-only delivery pattern proved
    # un-savable from inside Cowork on the user's machine). It is
    # gitignored so contents never hit the source history; Layer 1
    # tolerates it provided it contains ONLY *.plugin files (any other
    # leftover — an extracted source tree, a JSON report, a stray html —
    # is still a defect). See references/plugin-eval.md "Delivery —
    # /tmp first, dist/ as documented fallback" for the contract.
    DIST_DIR_NAME = "dist"

    runtime_hits: list[str] = []
    # walk the plugin tree (skip .git for speed and signal hygiene)
    for path in root.rglob("*"):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if rel.parts and rel.parts[0] == ".git":
            continue
        if _is_artefact(path.name):
            runtime_hits.append(str(rel))
    # Repo-root sweep — was shallow iterdir() until 0.6.1. Defect pattern:
    # a build artefact dropped into <repo>/dist/foo.plugin or similar
    # subfolder was silently accepted because iterdir() only saw top-level
    # entries. Switched to rglob so nested artefacts are caught. The
    # plugin/ folder itself is skipped (handled by the plugin-tree walk
    # above), and a short allowlist of infra dirs (VCS, venvs, caches) is
    # not entered — everything else is fair game.
    repo_root = root.parent
    dist_misuse: list[str] = []
    if repo_root != root and repo_root.exists():
        for path in repo_root.rglob("*"):
            try:
                rel = path.relative_to(repo_root)
            except ValueError:
                continue
            # don't re-walk the plugin tree or infra dirs
            if rel.parts and (rel.parts[0] == root.name or rel.parts[0] in REPO_ROOT_SWEEP_SKIP_DIRS):
                continue
            # dist/ is the official delivery transition zone — *.plugin
            # files inside it are tolerated, but any non-*.plugin file or
            # any nested directory is a misuse and raises a separate
            # finding so the artefact-sweep noise stays signal-rich.
            if rel.parts and rel.parts[0] == DIST_DIR_NAME:
                if path.is_dir():
                    if len(rel.parts) > 1:
                        dist_misuse.append(f"../{rel} (nested dir not allowed)")
                    continue
                if path.name.endswith(".plugin"):
                    continue  # the legitimate case
                dist_misuse.append(f"../{rel}")
                continue
            if _is_artefact(path.name):
                runtime_hits.append(f"../{rel}")
    rep.add(
        "No runtime artefacts in plugin tree or repo root",
        1,
        not runtime_hits,
        ("found: " + ", ".join(sorted(runtime_hits))) if runtime_hits else "clean",
    )
    rep.add(
        "dist/ contains only *.plugin files (no nested dirs, no other extensions)",
        1,
        not dist_misuse,
        ("misuse: " + ", ".join(sorted(dist_misuse))) if dist_misuse else "clean or absent",
    )

    # --- .gitignore covers *.plugin repo-wide (added 0.6.3) ---
    # Defect pattern: the dist/ delivery transition zone (0.6.2) relies on
    # *.plugin being gitignored repo-wide so that the staging copy never
    # lands in a commit. If someone edits .gitignore and drops the *.plugin
    # line — or narrows it to a specific subdir like "plugin/*.plugin" — the
    # Layer 1 allowlist keeps the file out of the runtime-artefact sweep,
    # but nothing would prevent the staging copy from being committed.
    # This check asserts that .gitignore (at the repo root) has a pattern
    # that is effectively repo-wide (a bare "*.plugin" line, or a line
    # equivalent to it). Scoped patterns like "dist/*.plugin" or
    # "plugin/*.plugin" are explicitly NOT accepted, because they only
    # cover one directory.
    gi_path = repo_root / ".gitignore"
    if gi_path.exists():
        gi_lines = [
            ln.strip() for ln in gi_path.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        # Accepted: "*.plugin" (bare), "/*.plugin" equivalent at root.
        # Rejected: "dist/*.plugin", "plugin/*.plugin", anything scoped.
        repo_wide = any(ln in {"*.plugin", "/*.plugin"} for ln in gi_lines)
        rep.add(
            ".gitignore covers *.plugin repo-wide",
            1,
            repo_wide,
            "ok" if repo_wide else "no repo-wide '*.plugin' pattern found",
        )
    else:
        rep.add(
            ".gitignore covers *.plugin repo-wide",
            1,
            False,
            f"no .gitignore at repo root ({repo_root})",
        )

    # --- archive shape check for any staged dist/*.plugin (added 0.6.3) ---
    # Defect pattern: Layer 1 validates the source tree and the documented
    # build recipe, but never the built archive itself. A user following
    # the recipe can still end up with a malformed .plugin — plugin.json
    # missing inside, version drift between repo and archive, or runtime
    # artefacts slipped into the zip (historical regressions: .mcpb-cache/
    # in 0.3.x, stray *-workspace/ folders in 0.4.x). The dist/ fallback
    # (0.6.2) makes a staged archive routinely available as a check target;
    # this assertion opens every dist/*.plugin and verifies:
    #   (a) .claude-plugin/plugin.json exists inside
    #   (b) the archive's plugin.json version matches the repo's
    #   (c) no artefact patterns appear anywhere in the archive's entry
    #       list (*-workspace/, skill-snapshot/, .mcpb-cache/, nested
    #       *.plugin, COUNCIL.md, eval-viewer-iter*.html)
    # Extended in 0.6.4 (P10): completeness. Forbidding junk is only half
    # the job — a corrupt build that is MISSING a skill file would pass (c)
    # and (b) but ship a broken archive. (d) now asserts that every
    # skills/<name>/SKILL.md in the source tree appears in the archive,
    # and the _shared bundle files too.
    # The check is skipped gracefully when no dist/*.plugin exists — the
    # /tmp-only delivery path is still valid and we don't want to force
    # users to stage a copy just to satisfy a check.
    import zipfile as _zipfile
    archive_problems: list[str] = []
    archives_found = []
    dist_dir = repo_root / DIST_DIR_NAME
    if dist_dir.is_dir():
        archives_found = sorted(p for p in dist_dir.iterdir() if p.is_file() and p.name.endswith(".plugin"))

    # Collect required archive entries from the source tree. Only files
    # that must ship are listed — evals/, scripts/, references/ are
    # optional per-skill and not universally asserted.
    required_entries: set[str] = set()
    skills_dir = root / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir() and p.name != "_shared"):
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                required_entries.add(f"skills/{skill_dir.name}/SKILL.md")
        shared = skills_dir / "_shared"
        if shared.is_dir():
            for name in ("language.md", "environments.md"):
                if (shared / name).exists():
                    required_entries.add(f"skills/_shared/{name}")
    # Plugin manifest is already required by (a), but also list it as an
    # entry so the "required_entries" diagnostic is self-contained.
    required_entries.add(".claude-plugin/plugin.json")

    if archives_found and data and data.get("version"):
        repo_version = str(data["version"])
        artefact_patterns_in_archive = re.compile(
            r"(^|/)("
            r"[^/]*-workspace/"
            r"|skill-snapshot/"
            r"|\.mcpb-cache/"
            r"|__pycache__/"
            r"|COUNCIL\.md$"
            r"|eval-viewer-iter[^/]*\.html$"
            r"|[^/]+\.plugin$"
            r"|[^/]+\.pyc$"
            r")"
        )
        for arc in archives_found:
            label = f"dist/{arc.name}"
            try:
                with _zipfile.ZipFile(arc) as z:
                    names = z.namelist()
                    names_set = set(names)
                    # (a) plugin.json inside
                    if ".claude-plugin/plugin.json" not in names_set:
                        archive_problems.append(f"{label}: missing .claude-plugin/plugin.json")
                        continue
                    # (b) version match
                    try:
                        arc_data = json.loads(z.read(".claude-plugin/plugin.json"))
                        arc_version = str(arc_data.get("version", ""))
                        if arc_version != repo_version:
                            archive_problems.append(
                                f"{label}: version {arc_version!r} != repo {repo_version!r}"
                            )
                    except Exception as e:
                        archive_problems.append(f"{label}: plugin.json unreadable ({e})")
                    # (c) no artefact patterns in entries
                    bad_entries = [n for n in names if artefact_patterns_in_archive.search(n)]
                    if bad_entries:
                        archive_problems.append(
                            f"{label}: artefact entries inside — {', '.join(sorted(bad_entries)[:3])}"
                        )
                    # (d) completeness — every required source file present
                    missing = sorted(required_entries - names_set)
                    if missing:
                        archive_problems.append(
                            f"{label}: missing entries — {', '.join(missing[:5])}"
                        )
            except _zipfile.BadZipFile:
                archive_problems.append(f"{label}: not a valid zip")
    # P16 (0.6.5): when no staged archive exists, surface a SKIP rather
    # than a silent PASS so the run summary distinguishes "archive valid"
    # from "no archive to check". Prior behaviour was a PASS with detail
    # "no staged archive (ok)" — informationally correct but invisible
    # in the PASS=N count, so a half-finished build that left an empty
    # dist/ looked identical to a clean release. SKIP is the right shape:
    # the assertion was not exercised, not satisfied vacuously.
    if not archives_found:
        rep.skip(
            "dist/*.plugin archive shape (plugin.json present, version matches, no artefacts, all skills included)",
            1,
            "no staged archive in dist/ — check not exercised",
        )
    else:
        rep.add(
            "dist/*.plugin archive shape (plugin.json present, version matches, no artefacts, all skills included)",
            1,
            not archive_problems,
            (
                f"{len(archives_found)} archive(s) checked: clean"
                if not archive_problems
                else "; ".join(archive_problems)
            ),
        )

    # --- dist/ lifecycle: --strict-release requires an empty dist/ (0.6.4) ---
    # Defect pattern: the dist/ transition zone is intentionally transient
    # — a staged archive sits there between "build" and "uploaded as
    # GitHub Release asset". After the release is cut, dist/ is expected
    # to be empty again. Nothing currently enforces that step; a forgotten
    # archive in dist/ after a release survives into the next cycle and
    # quietly contradicts the "permanent home is GitHub Releases" story.
    # The --strict-release flag, used in CI on a release-tag push or
    # invoked manually post-release, FAILs on any *.plugin in dist/. In
    # the default (non-strict) state, a staged archive is tolerated — so
    # the everyday developer workflow is not disrupted.
    if strict_release:
        rep.add(
            "dist/ is empty (strict-release mode)",
            1,
            not archives_found,
            "clean" if not archives_found else (
                "staged archives present: " + ", ".join(a.name for a in archives_found)
            ),
        )

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
            # disable-model-invocation: true requires user-invocable: true.
            # Promoted to Layer 1 in 0.6.1 after a Layer 3 audit found the
            # council skill missing user-invocable despite disable-model-
            # invocation being set. In Claude Code plugin contexts (confirmed
            # on anthropics/claude-code issues #26251 and #22345) a skill
            # with disable-model-invocation: true becomes unreachable via
            # slash command unless user-invocable: true is also present —
            # the flag the governance skill sets on itself and that
            # references/plugin-eval.md documents as mandatory. Skills
            # without disable-model-invocation (auto-triggering or Auto+
            # Command pattern) do not need the flag.
            dmi = fm.get("disable-model-invocation", "").strip().lower() == "true"
            if dmi:
                uinv = fm.get("user-invocable", "").strip().lower() == "true"
                rep.add(
                    f"[{name}] disable-model-invocation implies user-invocable: true",
                    1,
                    uinv,
                    "both set" if uinv
                    else "missing user-invocable: true — slash command would be unreachable",
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
        # Canonical heading for the optional references section. The
        # SKILL_TEMPLATE.md and README plugin-standard both name it
        # "## Additional references". A skill that lists files under a
        # differently-named heading (e.g. "## References") is a drift a
        # wording check can't catch but a structural assertion can.
        # Only assert if the skill actually has a references/ directory
        # with content — otherwise the section is legitimately absent.
        refs_dir = skill_dir / "references"
        has_refs = refs_dir.is_dir() and any(refs_dir.glob("*.md"))
        if has_refs:
            rep.add(
                f"[{name}] has canonical '## Additional references' heading",
                1,
                "## Additional references" in text,
                "references/ exists — heading must be '## Additional references'",
            )
            # Guard against stale legacy name surviving alongside the canonical one.
            rep.add(
                f"[{name}] no stale '## References' heading",
                1,
                not re.search(r"(?m)^## References\s*$", text),
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

    # --- commands/ ↔ skills/ pairing (three legal patterns) ---
    # Introduced in 0.5.0 with the council slash-command refactor. Extended in
    # 0.6.0 to allow a third pattern ("Auto + Command").
    #
    # The standard (README, governance SKILL.md) recognises three legal
    # shapes for a skill:
    #
    #   1. Auto-only:      skills/<name>/SKILL.md (no disable-model-invocation),
    #                      no commands/<name>.md.
    #                      The model decides when to fire; no user-visible command.
    #
    #   2. Command-only:   skills/<name>/SKILL.md with disable-model-invocation: true
    #                      + commands/<name>.md (the only entry point).
    #                      Used when auto-firing would race the user's intent
    #                      (e.g. /council, /update-plugin).
    #
    #   3. Auto + Command: skills/<name>/SKILL.md (auto-trigger) + commands/<name>.md.
    #                      The skill auto-fires on clear intent signals AND the
    #                      user can invoke it explicitly. Used for skills where
    #                      either path is legitimate (e.g. /rename-pdf: the model
    #                      can trigger it on "clean up my scans", and the user
    #                      can also call it directly with a folder argument).
    #
    # The two assertions below enforce the contract:
    #   Forward: every command needs a paired skill (any pattern — 2 or 3).
    #   Reverse: every non-auto skill (pattern 2) needs its command, otherwise
    #            the skill is unreachable in Claude Code / Cowork.
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

    # Forward direction: every commands/<name>.md needs a paired skill
    # (any of the three legal patterns — the command is always an entry
    # into a skill, never standalone)
    for cmd_name, cmd_path in sorted(commands.items()):
        paired_skill_md = skills_dir / cmd_name / "SKILL.md"
        paired_exists = paired_skill_md.exists()
        if paired_exists:
            detail = "paired (auto+command)" if cmd_name not in non_auto_skills else "paired (command-only)"
        else:
            detail = f"missing skills/{cmd_name}/SKILL.md"
        rep.add(
            f"commands/{cmd_name}.md pairs with a skill",
            1, paired_exists, detail,
        )

    # Reverse direction: every non-auto skill needs a paired command file
    # (pattern 2 — command is the only entry point, so the command must exist)
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

# P17 (0.6.6): per-grader assertion floor bands. The verbose summary
# surfaces drift but does not gate on it; --count-strict turns the same
# data into a hard contract so a grader that silently loses checks fails
# the build. The numbers are floors, not exact targets — graders are
# allowed to grow, never shrink. Pin to the count observed at the time
# the band was introduced; bumping a floor is a deliberate act of the
# next release that adds checks. Skills not listed here are not gated.
LAYER2_GRADER_FLOORS: dict[str, int] = {
    "council": 48,
    "rename-pdf": 16,
    "update-plugin": 14,
}


def _archive_forensics(root: Path) -> list[tuple[str, dict[str, int | str]]]:
    """Per-archive forensic stats for verbose mode (P20, 0.6.6).

    Returns a list of (archive_label, stats) tuples for every
    *.plugin in dist/. Stats include skill count, top-level command
    count, total markdown lines, and .py file count. Empty list if
    no archive is staged.

    The check above (archive shape) gates on correctness — does the
    archive contain plugin.json, does the version match, are artefacts
    excluded. Forensics answer a different question: is the archive
    the *expected size and shape*? An archive that drops from 80 to 20
    markdown lines, or loses half its skills, is technically valid but
    obviously broken. Surfacing the numbers in --verbose lets the
    operator (or CI log diff) catch silent shrinkage during build.
    """
    import zipfile as _zipfile
    out: list[tuple[str, dict[str, int | str]]] = []
    dist_dir = root.parent / "dist"
    if not dist_dir.is_dir():
        return out
    archives = sorted(p for p in dist_dir.iterdir() if p.is_file() and p.name.endswith(".plugin"))
    for arc in archives:
        label = f"dist/{arc.name}"
        try:
            with _zipfile.ZipFile(arc) as z:
                names = z.namelist()
        except Exception as e:
            out.append((label, {"error": f"unreadable: {e}"}))
            continue
        skills: set[str] = set()
        commands = 0
        md_lines = 0
        py_files = 0
        for n in names:
            parts = n.split("/")
            if len(parts) >= 2 and parts[0] == "skills" and parts[1] not in ("", "_shared"):
                skills.add(parts[1])
            if len(parts) >= 2 and parts[0] == "commands" and n.endswith(".md") and parts[1]:
                commands += 1
            if n.endswith(".md"):
                try:
                    with _zipfile.ZipFile(arc) as z:
                        md_lines += z.read(n).decode("utf-8", errors="replace").count("\n")
                except Exception:
                    pass
            if n.endswith(".py"):
                py_files += 1
        out.append((label, {
            "skills": len(skills),
            "commands": commands,
            "md_lines": md_lines,
            "py_files": py_files,
            "total_entries": len(names),
        }))
    return out


def _layer2_grader_counts(root: Path) -> list[tuple[str, int | None, str]]:
    """Collect per-skill grader assertion counts via each grader's
    --count-only mode (introduced 0.6.4 / P12). Returns a list of
    (skill_name, count_or_None, detail) tuples in skill-name order.

    A None count means the grader either does not exist, does not
    support --count-only, or failed to produce a parseable integer.
    The detail field carries a short human note for the verbose summary.
    """
    skills_dir = root / "skills"
    out: list[tuple[str, int | None, str]] = []
    if not skills_dir.exists():
        return out
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir() and p.name != "_shared"):
        name = skill_dir.name
        grader: Path | None = None
        for candidate in PER_SKILL_GRADER_CANDIDATES:
            if (skill_dir / candidate).exists():
                grader = skill_dir / candidate
                break
        if grader is None:
            out.append((name, None, "no grader script"))
            continue
        try:
            proc = subprocess.run(
                [sys.executable, str(grader), "--count-only"],
                capture_output=True, text=True, timeout=30,
            )
            raw = (proc.stdout or "").strip().splitlines()
            try:
                count = int(raw[-1]) if raw else None
            except ValueError:
                count = None
            if count is None:
                out.append((name, None, "grader did not return integer"))
            else:
                out.append((name, count, "ok"))
        except Exception as e:
            out.append((name, None, f"grader call failed: {e}"))
    return out


def main() -> int:
    # Minimal CLI — kept in-script (no argparse) to stay dependency-free
    # and readable at a glance. Supported forms:
    #   plugin-check.py [<plugin-root>]
    #   plugin-check.py [<plugin-root>] --strict-release
    #   plugin-check.py [<plugin-root>] --verbose
    # Flags compose freely.
    #
    # --strict-release (0.6.4) enforces the post-release invariant that
    # dist/ must be empty — the GitHub Release asset list is the
    # permanent home, dist/ is only a transient staging area. In
    # non-strict (default) mode, a staged dist/*.plugin is tolerated.
    #
    # --verbose (0.6.5) prints per-skill Layer 2 assertion counts after
    # the standard summary, by calling each grader's --count-only mode.
    # The aggregate "PASS=N" hides per-grader drift; this mode makes
    # the assertion budget per skill visible at a glance, so a grader
    # that silently loses checks (regression in instrumentation, accidental
    # rule deletion) is caught before it ships.
    #
    # --count-strict (0.6.6) turns the same per-grader counts into a
    # hard gate: any grader listed in LAYER2_GRADER_FLOORS that returns
    # fewer assertions than its floor causes the run to fail. This is
    # the deterministic complement to --verbose: --verbose surfaces
    # drift, --count-strict prevents shipping it. Release CI should run
    # both together (--strict-release --verbose --count-strict).
    args = sys.argv[1:]
    strict_release = False
    verbose = False
    count_strict = False
    positional: list[str] = []
    for a in args:
        if a == "--strict-release":
            strict_release = True
        elif a == "--verbose":
            verbose = True
        elif a == "--count-strict":
            count_strict = True
        elif a in ("-h", "--help"):
            print(
                "usage: plugin-check.py [<plugin-root>] "
                "[--strict-release] [--verbose] [--count-strict]"
            )
            return 0
        else:
            positional.append(a)
    root = Path(positional[0] if positional else ".").resolve()
    rep = Report(root=str(root))
    run_layer1(root, rep, strict_release=strict_release)
    run_layer2(root, rep)

    # P17 (0.6.6): per-grader band enforcement. Compute counts once
    # here so both --count-strict (which adds Layer 1 assertions to
    # rep) and --verbose (which prints them below) can reuse the same
    # data without invoking each grader twice.
    grader_counts: list[tuple[str, int | None, str]] | None = None
    if count_strict or verbose:
        grader_counts = _layer2_grader_counts(root)
    if count_strict and grader_counts is not None:
        observed = {name: count for name, count, _ in grader_counts}
        for skill, floor in LAYER2_GRADER_FLOORS.items():
            actual = observed.get(skill)
            if actual is None:
                rep.add(
                    f"--count-strict: {skill} grader assertion floor (>= {floor})",
                    1, False,
                    "grader missing or did not return integer count",
                )
            else:
                rep.add(
                    f"--count-strict: {skill} grader assertion floor (>= {floor})",
                    1, actual >= floor,
                    f"observed {actual} assertions (floor {floor})",
                )

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

    # P13 (0.6.5): verbose summary surfaces per-skill Layer 2 assertion
    # counts via each grader's --count-only mode. The standard summary
    # collapses Layer 2 to a single PASS/FAIL per skill, hiding the
    # assertion budget — so a grader that silently loses checks looks
    # identical to one that genuinely passes everything. Verbose mode
    # exposes the per-grader counts and totals them so drift between
    # runs is visible without diffing JSON reports.
    if verbose:
        print()
        print("Layer 2 grader assertion counts (via --count-only):")
        counts = grader_counts if grader_counts is not None else _layer2_grader_counts(root)
        total = 0
        for name, count, detail in counts:
            if count is None:
                print(f"  [L2] {name}: — ({detail})")
            else:
                floor = LAYER2_GRADER_FLOORS.get(name)
                if floor is not None:
                    marker = "OK" if count >= floor else "BELOW FLOOR"
                    print(f"  [L2] {name}: {count} assertions (floor {floor} — {marker})")
                else:
                    print(f"  [L2] {name}: {count} assertions (no floor pinned)")
                total += count
        if any(c is not None for _, c, _ in counts):
            print(f"  [L2] total Layer 2 assertions: {total}")

        # P20 (0.6.6): archive forensics. The archive-shape assertion
        # above answers "is the archive structurally valid?" — these
        # numbers answer "does the archive look the size and shape we
        # expect?". An archive that loses half its skills or drops 60%
        # of its markdown lines passes shape but is obviously broken;
        # surfacing the counts in --verbose makes silent shrinkage
        # visible in the CI log without diffing extracted trees.
        forensics = _archive_forensics(root)
        if forensics:
            print()
            print("Archive forensics (dist/*.plugin):")
            for label, stats in forensics:
                if "error" in stats:
                    print(f"  {label}: {stats['error']}")
                else:
                    print(
                        f"  {label}: "
                        f"{stats['skills']} skills, "
                        f"{stats['commands']} commands, "
                        f"{stats['md_lines']} md-lines, "
                        f"{stats['py_files']} .py files, "
                        f"{stats['total_entries']} entries"
                    )

    # write JSON report into the plugin's own /tmp workspace to avoid
    # cross-user permission collisions on a shared /tmp.
    plugin_name: str | None = None
    plugin_json_for_report = root / ".claude-plugin" / "plugin.json"
    try:
        if plugin_json_for_report.exists():
            plugin_name = json.loads(plugin_json_for_report.read_text()).get("name")
    except Exception:
        plugin_name = None
    workspace_dir = Path("/tmp") / f"{plugin_name or 'plugin'}-workspace" / "plugin-check"
    try:
        workspace_dir.mkdir(parents=True, exist_ok=True)
        report_path = workspace_dir / "report.json"
        report_path.write_text(json.dumps(rep.to_dict(), indent=2))
        print()
        print(f"Report written: {report_path}")
    except Exception as e:
        print(f"(report write skipped: {e})")

    return 0 if rep.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
