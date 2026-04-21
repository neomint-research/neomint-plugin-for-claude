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
  Cartographer, Adversary, Scout, Operator) synthesised by a Chairman
  and delivered turn by turn — one phase per message, ending in a
  sentinel so the user can follow and intervene. The skill carries
  the orientation burden. Do not use for: factual lookup, pure code
  generation, mechanical file transforms, or single-voice answers.
---

# COUNCIL — Turn-Gated Context-Aware Judgment System

A judgment skill that never evaluates an isolated question, only a question in
the state of its environment. Five MECE roles, one Chairman synthesis, and a
turn-gated deliberation protocol so the user can actually *listen* to the
Council — every phase is a separate assistant message that stops at a visible
sentinel and waits for the user to continue, rebut, deepen, branch, or abort.
The skill carries the orientation burden — never the user.

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
> No phase is ever merged to save time.

This is the one idea the rest of the skill serves. Read it again when tempted
to cut corners. In particular: the live-turn contract below exists so the user
can hear each role speak on its own before any Chairman synthesis — collapsing
two phases into one assistant message is a rigor reduction, not a scope cut.

---

## Turn-gated deliberation — the live contract

This is the backbone of the skill. A Council that ran all its phases inside a
single assistant message would be impossible to follow, impossible to interrupt,
and trivial to shortcut. The user must be able to *witness* each step and step
in at any point — like sitting in an actual council chamber, not reading the
minutes afterwards.

**One phase = one assistant message.** Never two. Never half.

**Every phase message ends with a sentinel line** — a visible stop that tells
the user which turn just finished, which turn is next, and what continuation
tokens are accepted. Without the sentinel the live contract is broken.

### Sentinel format

Every phase message MUST end with exactly this block:

```
=== TURN <N>/<K> COMPLETE — <PHASE NAME> ===
⏸ AWAITING USER. Reply NEXT to run T<N+1> <next phase>.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> · ABORT
```

Where `<N>` is the turn just produced, `<K>` is the total turn count for the
chosen mode, and `<PHASE NAME>` is the phase label (ORIENT / GROUND /
CARTOGRAPHER / ANALYST / ADVERSARY / SCOUT / OPERATOR / VERDICT, or the QUICK
equivalents).

The sentinel is a hard stop. After producing it, do NOT continue with the next
turn in the same assistant message, even if it feels more efficient or the
user's prompt implied "do everything". The user needs the seam — that's the
whole point of the live contract.

### Continuation tokens

```
NEXT        Run the next turn in sequence.
REBUTTAL    Re-run a specific role's turn with the user's counterargument
            as additional input. Only legal after that role's turn has run.
DEEPEN      Re-run a specific role or phase scoped to a named point, with
            more depth. Legal after the named turn has run.
BRANCH      Start a fresh Council from T1 with the user's new premise
            established. The previous verdict is preserved in COUNCIL.md.
ABORT       End the run cleanly; record the abort in COUNCIL.md if present.
```

If the user replies with free text instead of a token, interpret it:
recognisable rebuttal language → REBUTTAL; "go deeper on X" → DEEPEN;
"what if instead we did Y" → BRANCH; silence or "go on" → NEXT. Do not
restart the whole run because of token ambiguity — match the intent, name
your interpretation in the next turn's opening line, and continue.

### Anti-shortcut enforcement

The main failure mode of turn-gated skills is the model compressing two phases
into one message under time pressure (documented: Claude Code issue #21672 and
siblings). Defenses:

- The sentinel is the only legal ending for a phase message. A message that
  ends without `=== TURN <N>/<K> COMPLETE ===` is malformed and breaks the
  contract. If you catch yourself about to append more content after a
  sentinel, stop and post.
- Each turn MUST open with its header line `## Turn <N>/<K> — <PHASE NAME>`
  so both the user and the grader can verify one-phase-per-message.
- A single assistant message containing two phase headers is a contract
  violation and must be avoided even if it looks like a cost saving.
- The turn count `<K>` is fixed at T1 by the mode inference and does not
  change mid-run. Adjusting K silently to skip turns is forbidden.

---

## Step 0 — Orient silently, then announce turn count

Detect context from available signals. No switch, no announcement of *internals* —
the skill behaves, it does not explain itself. But the turn plan IS announced,
because it is part of the contract the user is about to witness.

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
        → 3 turns total

FULL    Decision language
        + Context ≥ 2 documents or a structured area
        + At least one dependency signal
        → 8 turns total

AUDIT   Completeness / consistency / gap question
        + Subject is the repo or document itself
        + No new decision embedded
        → 8 turns minimum; Chairman may insert DEEPEN turns as needed
```

If the three signals are unclear, ask one diagnostic question (see Input Logic
below) — that diagnostic question itself is T1, counted against K=1 (a
one-turn diagnostic "mini-run"). If the user's question is substantive but
ambiguous, default to FULL — never downgrade to QUICK just because full rigor
is harder.

The **first turn (T1 ORIENT)** always announces: inferred mode, inferred
context, the restated question, the total turn count K, and an honest cost
estimate. The user reads the plan and decides to continue.

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

## Turn map — one phase per message

Sequence is structural, not stylistic. Nothing is discussed before it is
grounded; the Cartographer's map is informed by the grounding; the four
remaining judging roles share both; the Chairman may only cite what has
already been said on the record.

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
T1  ORIENT + GROUND   Combined: mode/context/restated question/turn plan,
                      plus one Hersteller reference and one Community reference.
                      Still named sources, still on the record, just compressed.
T2  COUNCIL           All five roles in one message, each in a compressed
                      Thesis + 3-line Finding + Dissent block. The live-turn
                      contract is weakened here because QUICK is QUICK —
                      a user who wants to listen role-by-role picks FULL.
T3  VERDICT           Chairman synthesis + two-track output + handles
```

### AUDIT (8 turns minimum)

Same structure as FULL. The Chairman may insert DEEPEN turns between any two
phases when a finding warrants extra depth — e.g. T3b CARTOGRAPHER DEEPEN. Each
inserted turn gets its own sentinel and the remaining turn indices are
renumbered in the next sentinel (`T4/9` instead of `T4/8`) so the user can
always see how many turns remain.

Why GROUND is its own turn and not a Scout sub-task: a Council that reasons
in a vacuum either rediscovers settled knowledge or silently contradicts
authoritative guidance. Putting the manufacturer's position and the community's
position on the table *before* any role speaks stops the Council from
re-arguing a question the field has already settled — and makes any genuine
divergence visible as a first-class finding, not as a footnote buried inside
one role's write-up.

Detailed phase mechanics — the Hersteller / Community discipline, how the
Chairman moderates each role's turn, and the hand-off format — live in
`references/phases.md`, `references/turns.md`, and `references/ground.md`.

---

## Role turn micro-format (FULL and AUDIT)

Each role turn (T3 CARTOGRAPHER through T7 OPERATOR) MUST follow this exact
structure. The micro-format exists so the grader can verify each dimension was
actually produced — not just named — and so the Chairman has unambiguous
material to cite in T8.

```
## Turn <N>/<K> — <ROLE>
**Axis:** <the role's MECE question, restated>

**Thesis (one sentence):** <the single bet this role is making>

**Finding (hardest-first):**
<2-6 paragraphs of concrete, referenced analysis. The hardest sub-question is
addressed first, not last. File/line refs, named actors, specific events.>

**Cross-reference (mandatory from T4 onward):**
- <PriorRole @ T<n>>: "<direct short quote from that role's turn>" —
  <agree / diverge / extend> because <reason grounded in this role's axis>

**Dissent (mandatory):**
<Name one point from a prior role this role disagrees with, and say why.
If there is genuinely nothing to dissent from, the line reads:
"No dissent: I concur with <role> @ T<n> because <reason>". Silence is not
acceptable — either dissent with content, or concurrence with reason.>

**Resolvable?**
<"Finding stands." — OR — "Abstention: not judgeable because <named missing
input>. Resolvable by <concrete action>.">

=== TURN <N>/<K> COMPLETE — <ROLE> ===
⏸ AWAITING USER. Reply NEXT to run T<N+1> <next phase>.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> · ABORT
```

**Why cross-reference is mandatory from T4 onward.** T3 is the Cartographer and
has no prior role to cite; from T4 on, each role has real prior material on the
record. Forcing a cross-reference is how the turns compound — without it, the
five roles drift into five independent essays and the Chairman can only sum
them, not synthesize. The cross-reference can agree, diverge, or extend — what
it cannot do is stay silent.

**Why dissent is mandatory even when there's nothing to dissent from.** The
dissent line forces every role to test its findings against the existing
record. Polite concurrence without reason is indistinguishable from not
reading the prior turns. If the dissent line is "No dissent because …", the
"because …" is doing the work.

---

## GROUND turn — visible tool calls, not narrated search

T2 GROUND has a specific requirement: when web access is available (Claude
Code, Cowork, most Web sessions), the turn MUST contain at least one actual
tool invocation — `WebSearch` and/or `WebFetch` — visible in the conversation.
Narrating "I searched for X and found Y" without the actual tool call is a
contract violation. The user needs to see that the grounding was *performed*,
not asserted.

When web access is genuinely unavailable (sandboxed environment, offline),
the turn opens with: `Web access unavailable — falling back to trained
knowledge with cutoff <YYYY-MM>.` This is a legitimate abstention for the
Community slot; the Hersteller slot may still be satisfied from trained
knowledge if the authoritative source is stable and well-known (an RFC, a
long-standing API, a primary regulation).

The GROUND turn produces the grounding block:

```
**Hersteller (authoritative source):** <named source, date/version, one-line
position, URL if live-fetched>
**Community (practitioner consensus):** <named source(s), one-line position,
URL(s) if live-fetched>
**Divergence:** <one line: where Hersteller and Community disagree, or
"Aligned on X">
```

Both sources must be named or explicitly abstained on. A blank slot is a
contract violation.

---

## VERDICT turn — Chairman citation rule

T8 (or T3 in QUICK) is the Chairman's turn. The Chairman is not a sixth role;
it is the synthesis layer. Its output MUST:

1. **Cite each preceding role turn by quoted phrase.** For every role that ran
   (Cartographer, Analyst, Adversary, Scout, Operator), the verdict contains
   a direct short quote from that role's turn and names the turn number. This
   is how the Chairman *listens* — by repeating what was said, on the record.
2. **Add no new findings.** If the Chairman notices something none of the five
   roles caught, that is a signal a role under-produced. The Chairman invokes
   CHAIRMAN-VETO (one re-invocation of that role as a DEEPEN turn) or
   explicitly flags the gap in the MECE check — but does not introduce a
   finding under its own voice.
3. **Run the MECE check as a publication gate.** Incomplete grounding, uncited
   role, missing axis, or unresolved overlap blocks the verdict; the Chairman
   inserts a DEEPEN turn instead of papering over.
4. **Produce the two-track output** (OPERATIVE + MANAGEMENT) with role
   attribution preserved.
5. **Append iteration handles** (REBUTTAL / DEEPEN / BRANCH) and the final
   sentinel. After T8, the next sentinel format shifts: it no longer offers
   NEXT (there is no next turn), only the iteration handles.

---

## Input logic

The skill accepts anything: fragment, question, dump, upload, repository.
It carries the orientation burden.

```
Sufficiently clear     →  run (T1 announces the plan)
One ambiguity          →  one diagnostic question (T1 IS the diagnostic; K=1)
No answer to question  →  state the assumption explicitly, run anyway
```

### Diagnostic question standard

A diagnostic question is itself a Council artifact produced as T1. It must:

1. Announce `Mode: DIAGNOSTIC   Context: <CODE | DOC | CHAT>   Turns: 1/1` on
   the first line, so the user can see immediately that the skill is branching
   to a question-before-work path — not silently skipping the Council.
2. Name the missing dimension (which of the five roles cannot form an
   opinion without this information, and why).
3. Offer two concrete interpretations for the user to choose between.
4. Document which assumption would otherwise apply by default.
5. End with the diagnostic sentinel:
   `=== TURN 1/1 COMPLETE — DIAGNOSTIC ===` followed by
   `⏸ AWAITING USER. Pick interpretation A or B, or say "default" to run with the stated assumption.`

Asking more than one question at a time breaks the orientation burden
contract — the skill must be willing to run with partial information under
stated assumptions.

---

## Rigor duties — the block against laziness

These rules exist because LLMs under pressure default to surface-level
responses. Read them as the commitments that separate a Council from a
chat-bot opinion.

**TURN-GATED.** One phase per assistant message, always, ending in the
sentinel. Why: a Council produced in a single burst is impossible to follow
and trivial to shortcut. Live-turn structure is how the user listens.

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
don't secretly dilute. Mid-run: K does not change. A silent turn-count
reduction is a contract violation.

**CHAIRMAN-VETO.** If a role produces a platitude, skims the surface,
or dodges — the Chairman rejects it once with the specific gap named and
inserts a DEEPEN turn for that role. Why once and not twice: repeated
rejection consumes tokens without new signal; one named rejection forces
the role to either produce or explicitly abstain.

**EXPLICIT ABSTENTION.** No vague role output. Either a finding, or:
"Not judgeable because X is missing." Vague reassurance is worse than a
clean abstention — the user can act on "missing X", not on hedge words.

**DISSENT OR REASONED CONCURRENCE.** Every role from T4 onward states
either a substantive dissent from a named prior role, or a reasoned
concurrence ("No dissent because …"). Silent agreement is a failure to
listen.

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

**MODE DISCIPLINE.** QUICK/FULL/AUDIT determine turn count and depth. The
inference from Step 0 is hard — don't re-label a FULL as QUICK mid-flight.

**SCOPE-CUT.** The Cartographer (T3) is allowed to shrink the question —
"only Part A, not A+B+C" — when justified and announced. A shrunken
question judged fully is worth more than a full question judged thinly.
The scope-cut appears in T3 and is carried through T4–T8.

**COST TRANSPARENCY.** T1 announces the inferred mode, context, turn count K,
and an honest cost estimate.

**PERSISTENCE PAYOFF.** COUNCIL.md (in CODE-MODE) saves the repo scan and
prior verdicts on follow-up runs. The second run is structurally cheaper
than the first.

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

Every role stays visible in the output, turn by turn — not only the synthesis.
The reader must be able to see *how* the Council arrived at the verdict, role
by role. The turn-gated structure gives this for free: each role's message is
its own artifact. The Chairman's T8 simply points back at those artifacts by
quoted citation.

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
- Grounding complete: <Hersteller + Community both on the table, or name
  which was abstained on and why> — **blocks publication if incomplete**
- Dimensions covered: <5/5 or list the gap>
- Overlap detected: <none / describe / what it reveals>
- Unjudgeable dimension: <none / which one / what's missing>
- Cross-reference integrity: <each role from T4+ cited a prior role, or name
  the one that didn't>

## OPERATIVE track
<technical recommendation with references and follow-ups, grounded in the
cited role quotes above>

## MANAGEMENT track
<plain-language recommendation + first step + risk note>

## Persistence
<one of:
 - "Writing/updating COUNCIL.md at <path>" (CODE-MODE, after write)
 - "Proposing COUNCIL.md for this decision — see <path> / attached download"
   (DOC-MODE or Web)
 - "Skipping COUNCIL.md (CHAT-MODE, no persistence surface)" (CHAT-MODE)>

=== TURN <K>/<K> COMPLETE — VERDICT ===
⏸ Council closed. Reply REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> to continue the dialogue.
```

The **Persistence** line is mandatory in the T8 output. It is the visible
enforcement of the PERSISTENCE-PAYOFF contract — a verdict that silently
skips `COUNCIL.md` breaks the follow-up cheapness guarantee.

---

## MECE as active Chairman function

MECE isn't just a role layout — it's a live check the Chairman performs in
T8 before publishing the verdict:

1. Was GROUND complete? Both Hersteller and Community must be on the
   table from T2 — each either named with a concrete reference, or
   explicitly abstained on with the reason. A missing slot blocks
   publication; the Chairman does not synthesize a verdict on top of empty
   grounding. Instead it inserts a DEEPEN turn to re-run GROUND.
2. Were all five dimensions covered? (T3–T7 each produced a finding or a
   named abstention.)
3. Was there overlap? Overlap is a signal of structural unclarity — name it.
4. Is any dimension unjudgeable? Name which, what's missing, and what
   would resolve it.
5. Did each role from T4+ cross-reference a prior role? If not, name the
   one that didn't — the cross-reference is how the turns compound, and a
   silent omission reduces the Council to five parallel essays.

Gaps are named, never hidden. A Council that publishes a 5/5 when
only 3/5 were judgeable is worse than a Council that publishes 3/5
and names the other two — because the user can't repair an invisible
gap. Incomplete verdicts (e.g., "3/5 roles converge, 2/5 inconclusive")
must explicitly name the path to resolution for each inconclusive role,
or stop and ask the user for the missing input before proceeding.

---

## Stopping criteria

Silent stop is forbidden. Every run terminates in one of these three ways:

1. **Chairman issues a recommendation with one first step in T8.**
2. **Chairman explicitly abstains** — naming each unjudgeable dimension,
   what input would resolve it, and the consequence of leaving it
   unresolved. Partial convergence without resolution paths is not an
   abstention; it is an incomplete verdict. Stop only when sure, or when
   you can explicitly state what would need to become true for the
   Council to be sure.
3. **User triggers ABORT** (at any sentinel).

Either a complete verdict, a named resolvable abstention, or a user abort.
No other ending. "Reicht" — "good enough" — is not a valid terminator.

---

## Persistence

In CODE-MODE (filesystem access) maintain `COUNCIL.md` at the repo root to
make follow-up runs cheaper and trace accountable over time. See
`references/persistence.md` for the full file schema, update rules, and
cross-environment handling (Cowork: write to user-selected folder; Web:
offer as a download). When `COUNCIL.md` already exists, read it first —
the Cartographer uses it in T3 to skip already-mapped dependencies, and
the Chairman cites prior verdicts in T8 when relevant.

---

## Iteration — the Council as dialogue partner

After any turn's sentinel, the user can branch the Council without restarting:

```
REBUTTAL   "The Adversary is wrong — here's why." → Adversary's turn reruns
           with the counterargument as input. Legal after T5.
DEEPEN     "Cartographer, go deeper on point X." → Single-role rerun as a
           new DEEPEN turn inserted in-sequence.
BRANCH     "If we take path B, new Council." → Full new run from T1 with
           path B as the established premise.
ABORT      Close cleanly; record in COUNCIL.md if present.
```

The Council is a dialogue partner, not a request-response endpoint. The
sentinel on every turn makes this explicit — there is always a next action
offered, always a way for the user to intervene without starting over.

---

## Procedure with file access (Claude Code & Cowork)

Produce one turn per assistant message, each ending in the sentinel. Do NOT
bundle turns. Even if the user's prompt says "do the whole thing", the live
contract is the point — honor it.

**T1 ORIENT** — detect CODE-MODE (Bash + repo structure) vs DOC-MODE
(attached files) vs CHAT-MODE (text only). In Cowork, if the user hasn't
selected a folder yet, call `mcp__cowork__request_cowork_directory` first.
Read `COUNCIL.md` if present. Infer QUICK/FULL/AUDIT. Announce: mode,
context, restated question, turn count K, cost estimate. Post the
T1 sentinel.

**T2 GROUND** — perform at least one visible `WebSearch` and/or `WebFetch`
tool call when web access is available. Otherwise open with the offline
declaration. Produce the grounding block (Hersteller + Community + Divergence).
Post the T2 sentinel.

**T3 CARTOGRAPHER** — produce the dependency map alone. Role micro-format
applies; cross-reference is not required (no prior role to cite), but the
dissent line is not applicable either — replace it with a "Map integrity"
line naming the load-bearing nodes. Post the T3 sentinel.

**T4 ANALYST** — role micro-format with mandatory cross-reference (to T3
at minimum) and mandatory dissent or reasoned concurrence. Post the T4
sentinel.

**T5 ADVERSARY / T6 SCOUT / T7 OPERATOR** — same micro-format, each with
cross-reference and dissent obligations. Post each sentinel.

**T8 VERDICT** — Chairman synthesis with cited quotes from each prior role
turn, MECE check, two-track output, persistence note, iteration handles.
Write the `COUNCIL.md` entry (repo root in Claude Code; selected folder in
Cowork). Post the closing sentinel (no NEXT option, only iteration handles).

---

## Procedure in Claude AI (Web)

Web has no direct filesystem access, but the live-turn framework still runs.
The sentinel is exactly the same. Web-specific handling:

1. **T1 ORIENT** — detect DOC-MODE vs CHAT-MODE from what the user provided.
   If the user references a repo but didn't upload it, ask one diagnostic
   question as a T1/1 diagnostic run: "Should I work from your description,
   or can you paste/upload the relevant parts?"
2. **T2 GROUND via web search.** The Web environment usually has live search
   available — use it to surface the Hersteller and Community. If search is
   unavailable, say so and fall back to trained knowledge with cutoff.
3. **T3–T7** run the full role sequence on whatever material is in context,
   each in its own message with its sentinel. The user drives NEXT.
4. **T8 Persistence as a download.** At the end of the verdict, offer
   `COUNCIL.md` (or an updated version, if the user pastes in a prior
   one) as a downloadable markdown artifact. Tell the user: paste the
   file back in next session and the Council picks up where it left off.
5. **Cost transparency** still applies — T1 shows the turn count K and
   estimated depth once.

Web does not reduce rigor or weaken the live-turn contract. It only changes
persistence from "write to disk" to "offer as download".

---

## Anti-patterns (read before publishing any turn)

- Two phases in one assistant message. → Contract violation. Even if the
  user's prompt reads like "do everything", split across turns.
- A message that ends without the sentinel block. → Contract violation. The
  sentinel is how the user knows the turn is finished and what to type next.
- Changing K mid-run, or silently skipping a turn index. → NO-DOWNGRADE
  violation. If the work needs SCOPE-CUT, do it inside T3 explicitly.
- A role turn without a Thesis line, or without the cross-reference/dissent
  block (T4+). → The micro-format is how the grader and the Chairman
  verify the role actually listened. Re-run the turn.
- GROUND without visible tool calls when web access is available. → The
  user needs to see the grounding was performed, not asserted.
- A Chairman verdict that doesn't cite each role by quote. → The Chairman's
  job is to *listen*, and listening is visible only through citation.
- A Chairman verdict that introduces a new finding under its own voice. →
  Signal that a role under-produced. Insert a DEEPEN turn instead.
- Five short bullet points with no actual finding per role. → Use EXPLICIT
  ABSTENTION instead; vagueness across all five dimensions is a sign the
  mode was inferred too high — but *do not downgrade*; ask for the missing
  input or abstain.
- Skipping COUNCIL.md because "the user didn't ask for it". → They didn't
  ask because they don't know it exists. It's the persistence-payoff
  contract — honor it.

---

## Additional references

- `references/roles.md` — Full method, deliverable, and failure modes
  for each of the five roles.
- `references/phases.md` — Detailed phase mechanics and hand-off formats,
  organised by turn number.
- `references/turns.md` — The live-turn contract in detail: sentinel
  format, continuation tokens, micro-format per role turn, anti-shortcut
  enforcement, and worked examples.
- `references/ground.md` — Hersteller / Community grounding discipline:
  what counts as a Hersteller source, what counts as a community source,
  how to handle divergence, and how to scale grounding depth per mode.
- `references/persistence.md` — `COUNCIL.md` schema, update rules,
  cross-environment handling.
