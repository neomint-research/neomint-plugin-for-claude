# COUNCIL — Grounding Discipline (Phase 1)

The Council never discusses a question before it is grounded. GROUND is
its own phase — not a Scout sub-task, not a background check — because
the moment a role starts reasoning, its findings become context that
crowds out anything surfaced later. If the Hersteller or Community
position shows up only in the verdict, it has already been decontextualised
by everything the roles said first.

Two sources, in this order: **Hersteller first, Community second.** Both
before any role speaks.

---

## What counts as a Hersteller source

"Hersteller" = the authoritative / first-party / standard-setting source
for the question. Whoever, by position in the field, *gets to define* the
right answer.

Concrete examples by question type:

```
Question type                    Hersteller source
─────────────────────────────────────────────────────────────────────
API / library usage              Vendor's official docs, API reference
Protocol / wire format           RFC, W3C spec, ISO standard
Programming language feature     Language spec, official release notes
Cloud service configuration      Provider's docs (AWS / GCP / Azure)
Framework pattern                Framework maintainer's docs
Legal / regulatory question      The primary law, regulator guidance
Medical / clinical question      Guideline body (WHO, AWMF, NICE, …)
Security / compliance standard   NIST, ISO 27001, OWASP official
Financial / accounting rule      IFRS, HGB, regulator (BaFin, SEC)
Architecture question in a repo  The repo's own ADR / design doc / CLAUDE.md
Internal policy question         The organisation's written policy
```

For questions inside a repo, the repo's own decision records are the
Hersteller. Authority is relative to the scope of the question.

### When no Hersteller exists

Some questions don't have one — genuinely novel problems, cross-cutting
judgment calls, subjective prioritisation. In that case: state it.

```
Manufacturer (Hersteller): No authoritative source exists for this
question — it's a [novel / subjective / cross-domain] call. Stated.
```

This is a finding, not a skip. It tells the reader the Council knows no
authority is being contradicted or ignored.

---

## What counts as a Community source

"Community" = the practitioners working the same problem, outside and
around the Hersteller. They carry two kinds of signal:

1. **Where the Hersteller is incomplete or stale** — practitioners see
   edge cases first.
2. **Where the Hersteller is correct but unapplied in the wild** — a gap
   between the doc and the idiomatic practice.

Concrete sources:

```
Domain                 Community sources
─────────────────────────────────────────────────────────────────────
Software engineering   Stack Overflow, GitHub issues/discussions,
                       reddit (r/ClaudeAI, r/programming, framework
                       subs), maintainer blogs, conference talks
Infrastructure / ops   HashiCorp / AWS community forums, LinkedIn
                       engineering posts, DevOps blogs (Gruntwork,
                       Martin Fowler, …)
Security               OWASP community, CVE write-ups, vendor PSIRT
                       advisories, security researcher blogs
Legal / compliance     Specialist blogs (IT-Recht, datenschutz-blog),
                       practitioner forums, bar-association Q&A
Medical                UpToDate (specialist consensus), medical
                       society position papers, case-report literature
Architecture / design  Martin Fowler, Gregor Hohpe, the specific
                       framework's "recipes" / community gallery
```

For questions inside a repo, the Community is the rest of the repo's
commit history, code review comments, and any test suite that has
survived change — lived practice, as opposed to design intent.

### When the Community is unreachable

If web search isn't available and the conversation hasn't provided
community material, state that and fall back to Claude's trained
knowledge with the cutoff:

```
Community: No live community lookup available. Falling back to trained
knowledge as of <YYYY-MM>. Treat as an older snapshot, not as fresh
consensus.
```

Again: a named abstention, not a silent skip.

---

## Divergence — the first-class finding

The most valuable output of GROUND is the *difference* between the two
sources. It's the single place where the Council learns something the
user likely didn't bring into the room.

```
Divergence: Hersteller recommends X with rationale <…>. Community has
largely moved to Y because <empirical reason / edge case the docs
don't cover / simpler ergonomics>. Resolution in the Verdict section
after Cartographer + roles weigh in.
```

Three common divergence patterns:

1. **Hersteller conservative, Community pragmatic.** Docs say "use the
   official pattern A", practitioners all use B because A is verbose.
   The Council's job: decide whether the ergonomics win justifies the
   deviation, given *this* user's situation.

2. **Hersteller current, Community stale.** Docs have moved on to a new
   API, but Stack Overflow answers are dominated by the old one. Risk:
   the user is about to copy-paste a deprecated pattern. The Council's
   job: surface the staleness and point at the current official way.

3. **Hersteller silent, Community has a de-facto standard.** The spec
   doesn't cover the case; the community has converged on a convention.
   The Council's job: say so, and name the convention as the fallback
   authority.

If Hersteller and Community agree, write `Aligned on X` — brief, visible,
no padding.

---

## Depth by mode

GROUND scales with the depth mode, but never disappears.

```
QUICK   At least one authoritative reference AND one community reference.
        One line each is enough. Divergence named in one line or
        "aligned".

FULL    Multiple authoritative references if the question has more than
        one governing body (e.g., a protocol + a regulator). Multiple
        community references with enough breadth to distinguish
        consensus from one loud voice. Divergence analysed in a short
        paragraph.

AUDIT   All authoritative sources that touch the question, with
        version / date / section numbers. Community position traced
        across at least three independent sources to rule out echo.
        Divergence treated as its own structural finding.
```

A FULL run that produces a QUICK-sized grounding section is a regression.
If the budget doesn't allow full grounding, use SCOPE-CUT — narrow the
question — rather than thin the grounding.

---

## Handoff to the Cartographer

GROUND produces a short block that becomes load-bearing context for
every later phase:

```
HERSTELLER: <source, version, one-sentence position>
COMMUNITY:  <source(s), one-sentence position>
DIVERGENCE: <one line>
```

The Cartographer uses DIVERGENCE to decide which dependencies matter;
the four judging roles each see this block in their starting context.
The Chairman's MECE check includes a grounding-completeness line that
must pass before a verdict can be published.

---

## Anti-patterns

- **Grounding after the Council.** Even if the Council happens to be
  right, the grounding section is now a justification, not an input.
  That's the opposite of the contract.
- **One source covers both slots.** "The official docs say X, and
  people on the docs' own forum agree" — that's one source in two
  coats. Community = *independent* of the Hersteller.
- **Aligned-by-default.** Writing "Aligned on X" without actually
  checking is worse than skipping; it's a false guarantee. If the
  alignment wasn't verified, say "alignment not verified".
- **Deep-dive in the Hersteller, nothing in the Community.** An
  imbalanced GROUND biases the whole Council toward the Hersteller's
  framing. Both slots get real content, or both get a named
  abstention.
