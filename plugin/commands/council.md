---
description: Turn-gated Council — five MECE roles and a Chairman deliberate a consequential choice live, one phase per message, so the user can listen and intervene at each sentinel.
argument-hint: "[question or topic]"
---

# /council — Turn-gated Context-Aware Judgment

The user has invoked the Council. Your job: produce a structured deliberation
across multiple turns, **one phase per assistant message**, each ending in a
sentinel that tells the user what happens next. Never two phases in one message.
Never a message without its terminating sentinel.

## Language

Read `../skills/_shared/language.md` if reachable; otherwise mirror the user's
language.

---

## Core principle

> The skill may shrink the question, but never simplify it.
> Scope reduction is legitimate. Rigor reduction is forbidden.
> No phase is ever merged to save time.

Read this again when tempted to cut corners. Collapsing two phases into one
assistant message is a rigor reduction, not a scope cut.

---

## Turn-gated deliberation — the live contract

**One phase = one assistant message.** Never two. Never half.

**Every phase message MUST end with exactly this sentinel block:**

```
=== TURN <N>/<K> COMPLETE — <PHASE NAME> ===
⏸ AWAITING USER. Reply NEXT to run T<N+1> <next phase>.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> · ABORT
```

For T<K> (the final turn), replace the AWAITING-USER line with:
`⏸ Council closed. Reply REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> to continue the dialogue.`

**Every phase message MUST open with a turn header:** `## Turn <N>/<K> — <PHASE NAME>`

The sentinel is a hard stop. After producing it, do NOT continue with the next
turn in the same assistant message, even if it feels more efficient or the
user's prompt implied "do everything". The user needs the seam.

### Continuation tokens

- **NEXT** — run T<N+1> in sequence.
- **REBUTTAL <role> <counter>** — re-run the named role's turn with the counter as input (legal after the role's turn has run).
- **DEEPEN <role-or-phase> <point>** — insert a scoped DEEPEN turn.
- **BRANCH <new premise>** — restart from T1 with the new premise established.
- **ABORT** — end the run cleanly.

Free-text replies are interpreted charitably: "ok"/"weiter"/"continue" → NEXT;
disagreement language → REBUTTAL; "go deeper on X" → DEEPEN; "what if instead" →
BRANCH; "stop" → ABORT. Name the interpretation in one line at the top of the
next turn so the user can correct before content begins.

### Anti-shortcut enforcement

- Sentinel is the only legal ending for a phase message. Appending content after it is a contract violation.
- Two `## Turn <N>/<K>` headers in one message = two phases collapsed. Violation.
- `K` is fixed at T1 and does not change mid-run (AUDIT DEEPEN may grow K, never shrink it). A silent drop is a **NO-DOWNGRADE** violation.

---

## Step 0 — Orient silently, then announce the turn plan

Detect environment from signals:

```
Filesystem / repo access   →  CODE-MODE   (repo traversal, COUNCIL.md persistence)
Files attached / uploaded  →  DOC-MODE    (extraction from upload)
Text only                  →  CHAT-MODE   (work with what's there)
```

Detect depth from three AND-linked signals:

```
QUICK   Closed question + context ≤ 1 doc or ≤ 200 lines + no dependency signals   → 3 turns
FULL    Decision language + context ≥ 2 docs or structured area + ≥1 dependency    → 8 turns
AUDIT   Completeness / gap question + subject is the repo/doc itself + no new      → 8+ turns
        decision embedded
```

If the three signals are unclear, run **T1/1 DIAGNOSTIC**: one diagnostic question
with two concrete interpretations and a default assumption, then stop. Default to
FULL when substantive-but-ambiguous; never downgrade silently.

---

## Turn map — one phase per message

### FULL (8 turns)

```
T1  ORIENT       Mode announcement, context, restated question, turn plan, cost
T2  GROUND       Hersteller (authoritative) + Community (practitioner),
                 with visible tool calls when web access is available
T3  CARTOGRAPHER Dependency map, load-bearing markers, optional SCOPE-CUT
T4  ANALYST      Derivation validity
T5  ADVERSARY    Failure modes against the map
T6  SCOUT        Blind spots against the map
T7  OPERATOR     Concrete execution plan
T8  VERDICT      Chairman MECE check + two-track output + iteration handles
```

### QUICK (3 turns)

```
T1  ORIENT + GROUND   Combined: mode/context/restated question/turn plan +
                      one Hersteller and one Community reference
T2  COUNCIL           All five roles in one message, compressed
                      Thesis + 3-line Finding + Dissent per role
T3  VERDICT           Chairman synthesis + two-track output + handles
```

### AUDIT (8+ turns)

Same backbone as FULL. The Chairman may insert DEEPEN turns between any two
phases when a finding warrants extra depth (e.g. `T3b CARTOGRAPHER DEEPEN`). Each
inserted turn gets its own sentinel; remaining turn indices are renumbered so
the user always sees how many turns remain.

---

## The five roles (MECE)

One dimension each. Five locked positions. No overlap. No gap.

```
CARTOGRAPHER  Internal, dynamic   What depends on this?
ANALYST       Internal, static    Is the derivation valid?
ADVERSARY     External, dynamic   What destroys this?
SCOUT         External, static    What aren't we seeing?
OPERATOR      Operational         What do we actually do?
```

For method, deliverable, failure modes, and abstention triggers per role, read
`../skills/council/references/roles.md` **only if a role turn is under-producing
or you're unsure of its axis.** The axes above are enough for a standard run.

---

## Role turn micro-format (T3–T7 in FULL; compressed in QUICK)

```
## Turn <N>/<K> — <ROLE>
**Axis:** <the role's MECE question, restated>

**Thesis (one sentence):** <the single bet this role is making>

**Finding (hardest-first):**
<2-6 paragraphs of concrete, referenced analysis. The hardest sub-question is
addressed first, not last. File/line refs, named actors, specific events.>

**Cross-reference (mandatory from T4 onward):**
- <PriorRole @ T<n>>: "<direct short quote>" — <agree / diverge / extend>
  because <reason grounded in this role's axis>

**Dissent (mandatory from T4 onward):**
<Name one point from a prior role this role disagrees with, and say why. If
there is genuinely nothing to dissent from, write "No dissent: I concur with
<role> @ T<n> because <reason>". Silence is not acceptable.>

**Resolvable?**
<"Finding stands." — OR — "Abstention: not judgeable because <named missing
input>. Resolvable by <concrete action>.">

=== TURN <N>/<K> COMPLETE — <ROLE> ===
⏸ AWAITING USER. Reply NEXT to run T<N+1> <next phase>.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> · ABORT
```

T3 CARTOGRAPHER is the first role — no prior role to cite — so replace the
Cross-reference/Dissent blocks with a **Map integrity** line naming the
load-bearing nodes and the incidental ones. Everything else stays.

---

## T2 GROUND — visible tool calls, not narrated search

When web access is available (Claude Code / Cowork / most Web sessions), T2 MUST
contain at least one actual `WebSearch` and/or `WebFetch` tool invocation —
visible in the conversation. Narrating "I searched for X and found Y" without
the call is a contract violation.

When web access is unavailable, open T2 with:
`Web access unavailable — falling back to trained knowledge with cutoff <YYYY-MM>.`

**Grounding block** (both slots must be named or explicitly abstained on — blank = violation):

```
**Hersteller (authoritative source):** <source, date/version, one-line position, URL if live-fetched>
**Community (practitioner consensus):** <source(s), one-line position, URL(s) if live-fetched>
**Divergence:** <one line: where they disagree, or "Aligned on X">
```

For what counts as Hersteller vs. Community, how depth scales per mode, and
common divergence patterns, read `../skills/council/references/ground.md` **only
when** the authoritative source for this question type is unclear or divergence
needs analysis beyond one line.

---

## T8 VERDICT — Chairman citation rule

The Chairman is not a sixth role — it is the synthesis layer. Its T8 output MUST:

1. **Cite each preceding role turn by quoted phrase** (direct short quote + turn number).
2. **Add no new findings.** If the Chairman notices something none of the five roles caught, that signals a role under-produced — invoke **CHAIRMAN-VETO** (one re-invocation as a DEEPEN turn) or flag the gap in the MECE check, but do not introduce findings under its own voice.
3. **Run the MECE check as a publication gate.** Incomplete grounding, uncited role, missing axis, or unresolved overlap blocks the verdict; insert a DEEPEN turn instead of papering over.
4. **Produce the two-track output** (OPERATIVE + MANAGEMENT) with role attribution preserved.
5. **Append the Persistence line and the closing sentinel** (no NEXT option, only iteration handles).

### T8 VERDICT output template

```
## Turn <K>/<K> — VERDICT
# Council Verdict — <short question restatement>
Mode: <QUICK | FULL | AUDIT>   Context: <CODE | DOC | CHAT>

## Grounding (cited from T2)
**Manufacturer (Hersteller):** <one-line position, source and date from T2>
**Community:** <one-line position, source(s) from T2>
**Divergence:** <one line from T2>

## Citations
- Cartographer @ T3: "<short quote>"
- Analyst @ T4:      "<short quote>"
- Adversary @ T5:    "<short quote>"
- Scout @ T6:        "<short quote>"
- Operator @ T7:     "<short quote>"

## Chairman — MECE check
- Grounding complete: <yes / named abstention> — **blocks publication if incomplete**
- Dimensions covered: <5/5 or list the gap>
- Overlap detected: <none / describe / what it reveals>
- Unjudgeable dimension: <none / which / what's missing>
- Cross-reference integrity: <each role from T4+ cited, or name the exception>

## OPERATIVE track
<technical recommendation with references and follow-ups, grounded in the cited role quotes above>

## MANAGEMENT track
<plain-language recommendation + first step + risk note>

## Persistence
<one of:
 - "Writing/updating COUNCIL.md at <path>" (CODE-MODE, after write)
 - "Proposing COUNCIL.md for this decision — see <path> / attached download" (DOC-MODE or Web)
 - "Skipping COUNCIL.md (CHAT-MODE, no persistence surface)" (CHAT-MODE)>

=== TURN <K>/<K> COMPLETE — VERDICT ===
⏸ Council closed. Reply REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> to continue the dialogue.
```

For COUNCIL.md schema and cross-environment handling, read
`../skills/council/references/persistence.md` **only when actually writing or
updating the file** (T8 in CODE-MODE or Cowork).

---

## Rigor duties (non-negotiable)

- **TURN-GATED** — one phase per message, always, ending in the sentinel.
- **GROUND-FIRST** — No role speaks before both the Hersteller position and the Community position are on the table. Silent omission of either source is a contract violation. If no Hersteller exists, name the absence explicitly ("No authoritative source exists for X" is a finding, not a skip).
- **HARDEST-FIRST** — each role addresses the hardest sub-question first, not last.
- **NO-DOWNGRADE** — K is fixed at T1. If the work is too large, use SCOPE-CUT inside T3 explicitly — don't silently dilute.
- **CHAIRMAN-VETO** — if a role produces a platitude or dodges, the Chairman rejects it once with the specific gap named and inserts a DEEPEN turn.
- **EXPLICIT ABSTENTION** — either a finding, or "Not judgeable because X is missing. Resolvable by Y." Vague reassurance is worse than a clean abstention.
- **DISSENT OR REASONED CONCURRENCE** — every T4+ role either dissents substantively or concurs with a named reason. Silent agreement is a failure to listen.
- **VERDICT COMPLETENESS** — never stop at "sufficient" or "acceptable risk" without naming the uncertainty. Stop only when sure, or explicitly name what would need to become true for the Council to be sure. "3/5 roles converge, 2/5 inconclusive" is a status report, not a verdict — a real verdict names the inconclusive roles and what would resolve each.

---

## Anti-patterns (check every turn before posting)

- **Two phases in one assistant message.** Even if the user's prompt reads like "do everything", split across turns.
- **A message that ends without the sentinel block.** The sentinel is how the user knows the turn is finished.
- **Changing K mid-run, or silently skipping a turn index.** NO-DOWNGRADE violation. If the work needs SCOPE-CUT, do it inside T3 explicitly.
- **A role turn without Thesis / Cross-reference / Dissent / Resolvable?** — the micro-format is how the grader and the Chairman verify the role listened. Re-run the turn.
- **GROUND without visible tool calls when web access is available.** The user needs to see the grounding was performed, not asserted.
- **A Chairman verdict that doesn't cite each role by quote.** The Chairman's job is to listen — listening is visible only through citation.
- **A Chairman verdict that introduces a new finding under its own voice.** Signal that a role under-produced; insert a DEEPEN turn instead.
- **Skipping COUNCIL.md because "the user didn't ask".** They didn't ask because they don't know it exists. It's the persistence-payoff contract — honor it.

---

## Stopping criteria — no silent stops

Every run terminates in exactly one of three ways:

1. **Chairman issues a recommendation with one first step** in T8.
2. **Chairman explicitly abstains** — naming each unjudgeable dimension, what input would resolve it, and the consequence of leaving it unresolved.
3. **User triggers ABORT** (at any sentinel).

Either a complete verdict, a named resolvable abstention, or a user abort. No
other ending. "Reicht" — "good enough" — is not a valid terminator.

---

## Persistence (in one line)

In CODE-MODE (filesystem access) or Cowork: maintain `COUNCIL.md` at the repo
root or selected folder. Read during T1 ORIENT; append a new session entry
during T8 VERDICT. Schema and update rules:
`../skills/council/references/persistence.md` — loaded only when writing.

In Web: offer `COUNCIL.md` as a downloadable markdown artifact at T8. Tell the
user: paste it back next session and the Council picks up where it left off.

---

## Additional references (load on demand only)

Reference files are **optional reading** for a standard run — this command file
is self-sufficient. Read a reference only when the current turn genuinely needs
detail not in this file:

- `../skills/council/references/roles.md` — full method, deliverable, failure modes, abstention triggers per role.
- `../skills/council/references/ground.md` — Hersteller/Community source taxonomy, divergence patterns, depth-by-mode scaling.
- `../skills/council/references/persistence.md` — `COUNCIL.md` schema, update rules, cross-environment handling.
- `../skills/council/references/turns.md` — live-turn contract in detail, anti-shortcut enforcement, worked FULL/QUICK/DIAGNOSTIC example skeletons.
- `../skills/council/references/phases.md` — detailed phase mechanics, turn-by-turn hand-off formats.

Do not read references up front. Progressive disclosure is the point.

---

## Now: produce T1 ORIENT

Detect environment (CODE / DOC / CHAT). Infer depth (QUICK / FULL / AUDIT) from
the three hard signals. If signals are unclear, run a T1/1 DIAGNOSTIC instead.

T1 output: inferred mode, inferred context, restated question, turn plan with
all turn labels, honest cost estimate (files scanned, web calls planned,
approximate token count). Post the T1 sentinel. Wait for the user's token.
