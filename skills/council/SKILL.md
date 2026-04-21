---
name: council
description: >
  You're too close to it. Use when you need judgment on a consequential
  choice, a plan you're about to commit to, or a decision that touches
  multiple parts of your system — and you need to defend it to a
  skeptical audience or worry you're missing something. Trigger on
  decision language ("should we", "better to A or B"), validation ("is
  this correct", "poke holes"), risk ("what could go wrong", "blind
  spots"), completeness ("what are we missing", "audit", "gaps"), or
  strategic framing ("trade-offs", "implications", "dependencies") —
  also when the user presents a plan, design, or draft for a qualified
  opinion. Context-aware judgment with five MECE roles (Analyst,
  Cartographer, Adversary, Scout, Operator) synthesised by a Chairman.
  The skill carries the orientation burden — never the user. Do not
  use for: factual lookup, pure code generation, mechanical file
  transforms, or tasks where the user explicitly wants a single-voice
  answer.
---

# COUNCIL — Context-Aware Judgment System

A judgment skill that never evaluates an isolated question, only a question in
the state of its environment. Five MECE roles, five structured phases
(including a mandatory grounding pass against Hersteller and Community
sources), one Chairman synthesis. The skill carries the orientation burden —
never the user.

---

## Language

Read `../_shared/language.md` and apply the output language rules defined there.

## Environment detection

Read `../_shared/environments.md` and handle accordingly for Claude Code,
Cowork, and Claude AI (Web). The web fallback is defined below in the
"Procedure in Claude AI (Web)" section.

---

## Core principle

> The skill may shrink the question, but never simplify it.
> Scope reduction is legitimate. Rigor reduction is forbidden.

This is the one idea the rest of the skill serves. Read it again when tempted
to cut corners.

---

## Step 0 — Orient silently

Detect context from available signals. No switch, no announcement — the skill
behaves, it does not explain itself.

```
Filesystem / repo access   →  CODE-MODE   (repo traversal, COUNCIL.md persistence)
Files attached / uploaded  →  DOC-MODE    (extraction from upload)
Text only                  →  CHAT-MODE   (work with what's there)
```

Then infer the depth variant from three hard signals, AND-linked:

```
QUICK   Closed question
        + Context ≤ 1 document or ≤ 200 lines of code
        + No dependency signals

FULL    Decision language
        + Context ≥ 2 documents or a structured area
        + At least one dependency signal

AUDIT   Completeness / consistency / gap question
        + Subject is the repo or document itself
        + No new decision embedded
```

If the three signals are unclear, ask one diagnostic question (see Input Logic
below). If the user's question is substantive but ambiguous, default to FULL —
never downgrade to QUICK just because full rigor is harder.

Before a FULL run: show the estimated cost once (rough "this will involve
~N role passes, ~X files scanned") — visibly, but non-blocking. The user can
interrupt; the skill doesn't ask for permission.

---

## The five roles (MECE)

One dimension. Five positions. No overlap. No gap. Each role has a single
axis assignment so the Chairman can verify coverage structurally, not
rhetorically.

```
ANALYST       Internal, static     Is the derivation valid?
CARTOGRAPHER  Internal, dynamic    What depends on this?
ADVERSARY     External, dynamic    What destroys this?
SCOUT         External, static    What aren't we seeing?
OPERATOR      Operational          What do we actually do?
```

Why MECE matters here: a judgment fails more often by *missing a dimension*
than by reasoning wrong within one. Five locked positions let the Chairman
check coverage as a checklist, not as gut feel. Read `references/roles.md`
for each role's method, deliverable, and failure modes.

---

## The five phases

Sequence is structural, not stylistic. Nothing is discussed before it is
grounded; the Cartographer's map is informed by the grounding; the four
judging roles share both.

```
0  ORIENT     Capture context (repo-based or input-based)
1  GROUND     Authoritative source (Hersteller) first, then the community
              position. Neither is discussed before both are on the table.
2  MAP        Cartographer alone — dependency graph, informed by GROUND
3  COUNCIL    Analyst, Adversary, Scout, Operator in parallel, each seeing
              the context, the GROUND record, AND the Cartographer's map
4  VERDICT    Chairman synthesis with MECE self-validation
```

Why GROUND is its own phase and not a Scout sub-task: a Council that
reasons in a vacuum either rediscovers settled knowledge or silently
contradicts authoritative guidance. Putting the manufacturer's position
and the community's position on the table *before* any role speaks stops
the Council from re-arguing a question the field has already settled —
and makes any genuine divergence between the two sources visible as a
first-class finding, not as a footnote buried inside one role's write-up.

Detailed phase mechanics — including what each phase produces, the
Hersteller / Community discipline, how the Chairman moderates Phase 3,
and the hand-off format — are in `references/phases.md` and
`references/ground.md`.

---

## Input logic

The skill accepts anything: fragment, question, dump, upload, repository.
It carries the orientation burden.

```
Sufficiently clear     →  run
One ambiguity          →  one diagnostic question
No answer to question  →  state the assumption explicitly, run anyway
```

### Diagnostic question standard

A diagnostic question is itself a Council artifact. It must:

1. Announce `Mode: DIAGNOSTIC   Context: <CODE | DOC | CHAT>` on the first
   line, so the user can see immediately that the skill is branching to a
   question-before-work path — not silently skipping the Council.
2. Name the missing dimension (which of the five roles cannot form an
   opinion without this information, and why).
3. Offer two concrete interpretations for the user to choose between.
4. Document which assumption would otherwise apply by default.

Asking more than one question at a time breaks the orientation burden
contract — the skill must be willing to run with partial information under
stated assumptions.

---

## Rigor duties — the block against laziness

These rules exist because LLMs under pressure default to surface-level
responses. Read them as the commitments that separate a Council from a
chat-bot opinion.

**GROUND-FIRST.** No role speaks before both the Hersteller position and
the Community position are on the table. Why: a Council that reasons in a
vacuum either rediscovers settled knowledge or quietly contradicts it. If
no Hersteller exists for the question (genuinely novel or proprietary
context), name that absence explicitly — "No authoritative source exists
for X" is a finding, not a skip. If the Community position is unreachable
(no web access, no precedent), say so and fall back to Claude's trained
knowledge with a cutoff caveat. Silent omission of either source breaks
the contract. Depth of the grounding scales with the depth mode (QUICK: at
least one authoritative and one community reference; FULL / AUDIT:
multi-source, with divergences named).

**HARDEST-FIRST.** Each role addresses the hardest sub-question *first*,
not last. Why: if the hardest part is at the end, it gets thin treatment
when context fills up. Hardest-first forces full attention on what matters
most.

**NO-DOWNGRADE.** No downgrade from FULL to QUICK because it gets hard.
Depth is set by the signals in Step 0, not by how tired the reasoning
gets. If the work is too large for one session, use SCOPE-CUT (below) —
don't secretly dilute.

**CHAIRMAN-VETO.** If a role produces a platitude, skims the surface,
or dodges — the Chairman rejects it once with the specific gap named.
Why once and not twice: repeated rejection consumes tokens without new
signal; one named rejection forces the role to either produce or
explicitly abstain.

**EXPLICIT ABSTENTION.** No vague role output. Either a finding, or:
"Not judgeable because X is missing." Vague reassurance is worse than a
clean abstention — the user can act on "missing X", not on hedge words.

**VERDICT COMPLETENESS.** A Council verdict never stops at "sufficient"
or "acceptable risk" without naming the uncertainty. Stop only when sure,
or explicitly name what would need to become true for the Council to be
sure. "3/5 roles converge, 2/5 inconclusive" is a status report, not a
verdict — a real verdict names the inconclusive roles and what would
resolve each (another data pull, another document, another decision
upstream). Uncertainty that is silent decays; uncertainty that is named
can be acted on.

---

## Cost discipline — without losing rigor

Rigor and cost are reconciled by the core principle: shrink the question,
don't simplify it.

**MODE DISCIPLINE.** QUICK/FULL/AUDIT determine breadth and depth. The
inference from Step 0 is hard — don't re-label a FULL as QUICK mid-flight.

**SCOPE-CUT.** The Cartographer is allowed to shrink the question —
"only Part A, not A+B+C" — when justified and announced. A shrunken
question judged fully is worth more than a full question judged thinly.

**COST TRANSPARENCY.** Before every FULL run: show the estimated cost
once, visibly, non-blocking.

**PERSISTENCE PAYOFF.** COUNCIL.md (in CODE-MODE) saves the repo scan on
follow-up runs. The second run is structurally cheaper than the first.

---

## Output — always two tracks

Both tracks, always. Management-only strips nuance the Operator needs;
operative-only strips the framing Management needs.

```
OPERATIVE    Technical, direct, with file/line references and
             follow-up obligations. The operator can act from it.
MANAGEMENT   Plain language, risk-assessed, one recommendation with
             one first step. The decision-maker can decide from it.
```

Every role stays visible in the output — not only the synthesis. The
reader must be able to see *how* the Council arrived at the verdict,
role by role. If only the Chairman's voice appears, the user loses the
ability to contest any single dimension.

### Output template

```
# Council Verdict — <short question restatement>
Mode: <QUICK | FULL | AUDIT>   Context: <CODE | DOC | CHAT>

## Grounding
**Manufacturer (Hersteller):** <authoritative source — vendor docs, primary
law, regulator, ISO / RFC, first-party API reference — with name, date, and
version — or "No authoritative source exists for this; stated.">
**Community:** <practitioners' position — battle-tested patterns from
forums, issue trackers, peer analyses, Stack Overflow consensus — with at
least one concrete reference — or "No community position reachable;
stated, falling back to trained knowledge with cutoff <YYYY-MM>.">
**Divergence:** <one line: where Hersteller and Community disagree, or
"aligned on X">

## Cartographer — dependency map
<findings, or "Not judgeable because …">

## Analyst — derivation validity
<findings, or "Not judgeable because …">

## Adversary — failure modes
<findings, or "Not judgeable because …">

## Scout — blind spots
<findings, or "Not judgeable because …">

## Operator — actual execution
<findings, or "Not judgeable because …">

## Chairman — verdict
MECE check:
- Grounding complete: <Hersteller + Community both on the table, or name
  which was abstained on and why>
- Dimensions covered: <5/5 or list the gap>
- Overlap detected: <none / describe / what it reveals>
- Unjudgeable dimension: <none / which one / what's missing>

OPERATIVE track:
<technical recommendation with references and follow-ups>

MANAGEMENT track:
<plain-language recommendation + first step + risk note>

Persistence:
<one of:
 - "Writing/updating COUNCIL.md at <path>" (CODE-MODE, after write)
 - "Proposing COUNCIL.md for this decision — see <path> / attached download"
   (DOC-MODE or Web)
 - "Skipping COUNCIL.md (CHAT-MODE, no persistence surface)" (CHAT-MODE)>
```

The **Persistence** line is mandatory in the output. It is the visible
enforcement of the PERSISTENCE-PAYOFF contract — a verdict that silently
skips `COUNCIL.md` breaks the follow-up cheapness guarantee.

---

## MECE as active Chairman function

MECE isn't just a role layout — it's a live check the Chairman performs
before publishing:

1. Was GROUND complete? Both Hersteller and Community must be on the
   table — each either named with a concrete reference, or explicitly
   abstained on with the reason. A missing slot blocks publication; the
   Chairman does not synthesize a verdict on top of empty grounding.
2. Were all five dimensions covered?
3. Was there overlap? Overlap is a signal of structural unclarity — name it.
4. Is any dimension unjudgeable? Name which, what's missing, and what
   would resolve it.

Gaps are named, never hidden. A Council that publishes a 5/5 when
only 3/5 were judgeable is worse than a Council that publishes 3/5
and names the other two — because the user can't repair an invisible
gap. Incomplete verdicts (e.g., "3/5 roles converge, 2/5 inconclusive")
must explicitly name the path to resolution for each inconclusive role,
or stop and ask the user for the missing input before proceeding.

---

## Stopping criteria

Silent stop is forbidden. Every run terminates in one of these three ways:

1. **Chairman issues a recommendation with one first step.**
2. **Chairman explicitly abstains** — naming each unjudgeable dimension,
   what input would resolve it, and the consequence of leaving it
   unresolved. Partial convergence without resolution paths is not an
   abstention; it is an incomplete verdict. Stop only when sure, or when
   you can explicitly state what would need to become true for the
   Council to be sure.
3. **User triggers abort.**

Either a complete verdict or a named, resolvable abstention. No other
ending. "Reicht" — "good enough" — is not a valid terminator.

---

## Persistence

In CODE-MODE (filesystem access) maintain `COUNCIL.md` at the repo root to
make follow-up runs cheaper and trace accountable over time. See
`references/persistence.md` for the full file schema, update rules, and
cross-environment handling (Cowork: write to user-selected folder; Web:
offer as a download). When `COUNCIL.md` already exists, read it first —
the Cartographer uses it to skip already-mapped dependencies.

---

## Iteration — the Council as dialogue partner

After a verdict, the user can branch the Council without restarting Step 0:

```
REBUTTAL   "The Adversary is wrong — here's why." → Adversary reruns
           with the counterargument as input.
DEEPEN     "Cartographer, go deeper on point X." → Single-role rerun
           scoped to the named point.
BRANCH     "If we take path B, new Council." → Full new run with path B
           as the established premise.
```

The Council is a dialogue partner, not a request-response endpoint. Always
surface these three options at the end of a verdict so the user knows the
Council stays open.

---

## Procedure with file access (Claude Code & Cowork)

1. **Orient silently** — detect CODE-MODE (Bash + repo structure) vs
   DOC-MODE (attached files) vs CHAT-MODE (text only).
2. **Read COUNCIL.md** if present. In Cowork, if the user hasn't selected
   a folder yet, call `mcp__cowork__request_cowork_directory` first.
3. **Infer mode** (QUICK/FULL/AUDIT) from the three signals. Announce the
   inferred mode in one line. For FULL: show cost estimate once.
4. **GROUND.** Before the Cartographer runs: surface the Hersteller
   position (authoritative / first-party source) and the Community
   position (practitioner consensus). Prefer live lookup when web access is
   available; otherwise state the fallback and cutoff. Both go into the
   verdict's Grounding section, together with any divergence.
5. **Run phases 2-4** as defined. Cartographer serial; Analyst / Adversary
   / Scout / Operator can run as parallel sub-reasoning passes.
6. **Publish the verdict** using the output template. Write an entry to
   `COUNCIL.md` (repo root in Claude Code; selected folder in Cowork).
7. **Offer iteration handles** (REBUTTAL / DEEPEN / BRANCH).

---

## Procedure in Claude AI (Web)

Web has no direct filesystem access, but the full framework still runs.
Web-specific handling:

1. **Detect DOC-MODE vs CHAT-MODE** from what the user provided. If the
   user references a repo but didn't upload it, ask one diagnostic
   question: "Should I work from your description, or can you paste/
   upload the relevant parts?"
2. **GROUND via web search.** The Web environment usually has live search
   available — use it to surface the Hersteller (official docs / vendor /
   standards body) and the Community (forums, issue trackers, peer
   analyses). If search is unavailable, say so and fall back to trained
   knowledge with cutoff.
3. **Run the full five phases** on whatever material is in context.
4. **Persistence as a download.** At the end of the verdict, offer
   `COUNCIL.md` (or an updated version, if the user pastes in a prior
   one) as a downloadable markdown artifact. Tell the user: paste the
   file back in next session and the Council picks up where it left off.
5. **Cost transparency** still applies — before a FULL run, show the
   estimated depth once.

Web does not reduce rigor. It only changes persistence from
"write to disk" to "offer as download".

---

## Anti-patterns (read before publishing a verdict)

- Five short bullet points with no actual finding per role. → Use EXPLICIT
  ABSTENTION instead; vagueness across all five dimensions is a sign the
  mode was inferred too high — but *do not downgrade*; ask for the missing
  input or abstain.
- A Chairman synthesis that doesn't name which role said what. → The
  verdict becomes unfalsifiable. Keep role attribution visible.
- Skipping COUNCIL.md because "the user didn't ask for it". → They didn't
  ask because they don't know it exists. It's the persistence-payoff
  contract — honor it.
- Answering without running the Cartographer first when the question
  touches more than one part of the system. → Dependency-blind verdicts
  are the #1 Council failure mode.
- Running the Council before GROUND is on the table. → Context-blind.
  Even QUICK does a GROUND pass: at least one authoritative reference and
  one community reference, or a named abstention for each. A verdict whose
  grounding section is empty is structurally an opinion, not a Council
  finding.

---

## Additional references

- `references/roles.md` — Full method, deliverable, and failure modes
  for each of the five roles.
- `references/phases.md` — Detailed phase mechanics, hand-off formats,
  and Chairman moderation.
- `references/ground.md` — Hersteller / Community grounding discipline:
  what counts as a Hersteller source, what counts as a community source,
  how to handle divergence, and how to scale grounding depth per mode.
- `references/persistence.md` — `COUNCIL.md` schema, update rules,
  cross-environment handling.
