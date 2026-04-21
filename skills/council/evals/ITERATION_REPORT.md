# COUNCIL skill — iteration report

## Scoring summary

| Eval | Iter 1 with-skill | Iter 1 baseline | Iter 2 with-skill |
|------|:-:|:-:|:-:|
| full-code-auth-extraction | 8 / 9 | 1 / 9 | **9 / 9** |
| quick-chat-slo-breaker | 9 / 9 | 2 / 9 | **9 / 9** |
| audit-doc-policy-gaps | 9 / 9 | 3 / 9 | **9 / 9** |
| ambiguity-diagnostic-question | 5 / 7 | 2 / 7 | **7 / 7** |
| **TOTAL** | **31 / 34 (91%)** | **8 / 34 (24%)** | **34 / 34 (100%)** |

Baseline (same prompt, no skill loaded) confirms the skill is what
drives the structure — without it the model answers ad-hoc with no
mode/context, no MECE, no two-track output, no diagnostic discipline
on ambiguous input.

## Iter-1 → iter-2 changes (SKILL.md)

Two targeted gaps closed:

1. **COUNCIL.md was implicit only in a procedure step.** The subagent
   skipped it in the output. Fix: added a mandatory `Persistence:` line
   to the output template with three explicit values (write / propose-
   as-download / skip). Visible in the published verdict, not hidden
   in a procedure paragraph.

2. **Diagnostic-question path bypassed mode/context announcement.**
   The response asked a clean A/B question with default — good — but
   the user couldn't see the skill had deliberately branched away from
   the full Council. Fix: the diagnostic-question standard now
   requires `Mode: DIAGNOSTIC   Context: <CODE | DOC | CHAT>` as the
   first line.

Both fixes are visible-in-output contracts, so the next grader (human
or script) can see them directly.

## What the grading script checks

Structural checks are regex/keyword-based and deterministic. Semantic
checks (e.g. "verdict rejects the claim", "at least 3 gaps named") use
keyword hit-counts against the known gap list for the eval, so they're
reproducible. Script lives at `../../../../council-workspace/grade.py`
(outside the plugin).

## Next step

Plugin governance re-runs Steps 3-5:
- version bump retained at 0.4.0 (same feature release, no external
  behaviour change beyond iter-2 polish)
- re-run consistency loop
- repackage .plugin
