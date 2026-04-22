"""grader_utils.py — Shared helpers for per-skill Layer 2 graders.

Layer 2 graders self-report their assertion count via `--count-only`
(introduced 0.6.4 / P12). Two patterns coexist:

  - Explicit instrumentation: each assertion site has a sibling
    `checks += 1` line. Works fine for small graders (rename-pdf has
    16, update-plugin has 14) where annotation cost is negligible.
  - Static analysis: count `failures.append(` sites in the grader's
    own source. The right choice when the grader has so many sites
    that maintaining `checks += 1` lines becomes a meaningful tax
    (council has 50+, spread across labelled and unlabelled blocks).
    Originally implemented inline in `council/scripts/grade.py`.

P18 (0.6.6) extracts the static-analysis helper here so any future
grader can adopt the same pattern without copy-pasting the
implementation. Keeping it in `_shared/` matches the existing
convention for `language.md` and `environments.md` — single source of
truth, no per-skill duplication.

Usage:

    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_shared"))
    from grader_utils import count_failure_sites

    def _self_check_count() -> int:
        return count_failure_sites(Path(__file__))

The sys.path insertion is necessary because per-skill graders are
invoked as standalone scripts (not part of a package). The helper
above lives one directory up under `_shared/`. The pattern is verbose
but explicit — preferable to packaging the plugin as a Python module,
which would conflict with how Claude Code installs plugins read-only.
"""

from __future__ import annotations

from pathlib import Path


def count_failure_sites(source_path: Path) -> int:
    """Count distinct assertion sites in a grader by static analysis.

    Returns the number of `failures.append(` literal occurrences in
    the source file. Each occurrence corresponds to one place a check
    can fail, so the count is the grader's contract size.

    Caveats: a `for` loop containing a single `failures.append(...)`
    inside a conditional counts as ONE site, not one-per-iteration.
    The number is therefore a lower bound on the number of distinct
    assertions, but it is self-reporting and travels with the file —
    which is the property the 0.6.1 hedge "counts drift" was asking
    for: the binding number is whatever the grader script actually
    asserts in source.

    Returns 0 if the file cannot be read; callers should treat 0 as
    "unknown" rather than "no assertions".
    """
    try:
        src = source_path.read_text()
    except Exception:
        return 0
    return src.count("failures.append(")
