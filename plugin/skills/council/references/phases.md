# COUNCIL — Phase Mechanics in Detail (turn-numbered)

The Council is produced as a sequence of turns — one phase per assistant
message, each ending in the sentinel defined in `turns.md`. Every phase has
a fixed input, a fixed output, and a fixed hand-off. Sequence is structural,
not stylistic. This document describes each phase's mechanics; `turns.md`
describes the live-turn contract that wraps them; `ground.md` describes the
Hersteller/Community discipline for T2.

FULL has 8 turns (T1–T8). QUICK compresses to 3 turns (T1 merges ORIENT+GROUND,
T2 merges the five roles, T3 is VERDICT). AUDIT uses FULL as a baseline and
the Chairman may insert DEEPEN turns between phases as needed.

---

## T1 — ORIENT

**Purpose:** Capture the environment and post the turn plan so the user
can see what they are about to witness, intervene before any work starts,
and verify the skill's inference.

**Input:** Whatever the user provided (repo access, uploads, text) plus
the ambient environment (Claude Code / Cowork / Web).

**Activity:**
- Detect CODE-MODE / DOC-MODE / CHAT-MODE from signals.
- In CODE-MODE, check for `COUNCIL.md` at the repo root and read it if
  present — prior Council state is load-bearing context.
- Infer QUICK / FULL / AUDIT from the three hard signals.
- If ambiguous: run a T1/1 diagnostic (format in SKILL.md).

**Output:**
- One-line mode/context header.
- Restated question.
- Turn plan (T1..TK with phase names).
- Cost estimate (rough: files scanned, web calls planned, approximate
  token count).

**Sentinel:** `=== TURN 1/<K> COMPLETE — ORIENT ===`

---

## T2 — GROUND

**Purpose:** Put the Hersteller (authoritative / first-party source) and
the Community (practitioner consensus) on the table *before* any role
speaks. A Council that reasons without grounding rediscovers settled
knowledge or silently contradicts it; either way it wastes the user's
time on a question the field has already answered. See `ground.md` for
what counts as each kind of source and how depth scales per mode.

**Input:** T1 orientation note and the question itself.

**Activity:**
- Surface the Hersteller position first. When web access is available,
  perform at least one visible `WebSearch` or `WebFetch` tool call — the
  user sees the grounding was done, not asserted. Otherwise open with
  "Web access unavailable — falling back to trained knowledge with cutoff
  <YYYY-MM>." and proceed.
- Surface the Community position second. At least one independent
  source in QUICK; multiple in FULL / AUDIT.
- Identify divergence, if any, between Hersteller and Community.

**Output — the grounding block:**

```
**Hersteller (authoritative source):** <source, date/version, one-line
position, URL if live-fetched>
**Community (practitioner consensus):** <source(s), one-line position,
URL(s) if live-fetched>
**Divergence:** <one line; or "Aligned on X">
```

Both slots must be named or explicitly abstained on. A blank slot is a
contract violation.

**Sentinel:** `=== TURN 2/<K> COMPLETE — GROUND ===`

---

## T3 — CARTOGRAPHER (Map)

**Purpose:** Produce the dependency graph that the remaining role turns
(T4–T7) will share as common substrate. If each role had to derive its
own map, their findings would talk past each other.

**Input:** T1 orientation + T2 grounding block + the available material.

**Activity:** The Cartographer works alone. No other roles run in this
turn.

**Output (role micro-format with adaptations):**
- Axis line, Thesis line, Finding block (hardest-first).
- Upstream / downstream dependency list with file/module names.
- Load-bearing markers — which dependencies carry the decision.
- Optional SCOPE-CUT proposal if the full question is too large.
- "Map integrity" line replacing the cross-reference/dissent block (no
  prior role to cite).
- Resolvable? line.

**Silent stop condition:** If the Cartographer abstains ("no artifact
surface"), the Chairman decides in T8 whether to proceed with an explicit
"no map available" marker or insert a DEEPEN turn to re-scope. Default:
proceed with the marker. Better a Council with a flagged gap than a
stalled Council.

**Sentinel:** `=== TURN 3/<K> COMPLETE — CARTOGRAPHER ===`

---

## T4 — ANALYST

**Purpose:** Judge whether the derivation on the page is valid — internal
logical consistency, definitional consistency, argument completeness. The
Analyst operates on what is written, not on the world.

**Input:** T1 orientation + T2 grounding + T3 map + the material.

**Output — role micro-format with full cross-reference and dissent block:**
- Axis, Thesis, Finding (hardest-first).
- Cross-reference: at least one quote from T3 Cartographer with agree /
  diverge / extend.
- Dissent or reasoned concurrence.
- Resolvable?

**Sentinel:** `=== TURN 4/<K> COMPLETE — ANALYST ===`

---

## T5 — ADVERSARY

**Purpose:** What destroys this? External active forces — competitor moves,
regulatory changes, load spikes, adversarial inputs, political counter-moves.
Concrete failure vectors, not generic "it could fail".

**Input:** T1 + T2 + T3 + T4 + the material.

**Output — role micro-format:**
- Axis, Thesis, Finding (hardest-first, ranked by severity × likelihood).
- Cross-reference: at least one quote from T3 or T4.
- Dissent or reasoned concurrence.
- Resolvable?

**Sentinel:** `=== TURN 5/<K> COMPLETE — ADVERSARY ===`

---

## T6 — SCOUT

**Purpose:** What aren't we seeing? Static facts about the world that
would change the conclusion if surfaced — existing solutions, precedents,
regulatory constraints, cultural norms, technical standards, prior
internal decisions that bind this one.

**Input:** T1 + T2 + T3 + T4 + T5 + the material.

**Output — role micro-format:**
- Axis, Thesis, Finding (hardest-first, with concrete pointers).
- Cross-reference: at least one quote from any prior role turn.
- Dissent or reasoned concurrence.
- Resolvable?

**Sentinel:** `=== TURN 6/<K> COMPLETE — SCOUT ===`

---

## T7 — OPERATOR

**Purpose:** Translate the other four roles into concrete action. What is
the next step, by whom, under what condition, using which tools. Verbs and
references, not principles.

**Input:** T1 + T2 + T3 + T4 + T5 + T6 + the material.

**Output — role micro-format:**
- Axis, Thesis.
- Finding: first step, follow-up obligations, stop/rollback conditions.
- Cross-reference: at least one quote from any prior role turn — must
  show the Operator is acting on those findings, not ignoring them.
- Dissent or reasoned concurrence.
- Resolvable?

**Sentinel:** `=== TURN 7/<K> COMPLETE — OPERATOR ===`

---

## T8 — VERDICT (Chairman)

**Purpose:** Chairman synthesis with MECE self-validation and the Chairman
citation rule — every prior role turn must be quoted.

**Input:** T1 + T2 + T3 + T4 + T5 + T6 + T7.

**Activity:**
1. MECE check (publication gate):
   - Grounding complete — Hersteller + Community each named or named as
     explicit abstention. A missing slot blocks publication.
   - 5 dimensions covered (T3–T7), or name the gap(s) explicitly.
   - Overlap between roles → flag as structural unclarity.
   - Unjudgeable dimension(s) → name what's missing.
   - Cross-reference integrity — each role from T4+ cited a prior role,
     or name the one that didn't.
2. Produce Citations section: direct short quote from each of T3–T7
   with turn-number attribution.
3. Produce the two-track output (OPERATIVE + MANAGEMENT).
4. Add NO new findings under Chairman's own voice. If a gap is visible,
   insert a DEEPEN turn instead.
5. Append iteration handles and the closing sentinel (no NEXT, only
   REBUTTAL / DEEPEN / BRANCH / ABORT).
6. In CODE-MODE / Cowork: write a new entry to `COUNCIL.md`. In Web:
   offer an updated `COUNCIL.md` artifact as download.

**Stopping criteria (one of three, never silent):**
- Recommendation with one first step.
- Explicit abstention on a named dimension with what's needed.
- User-triggered abort.

**Sentinel:** `=== TURN <K>/<K> COMPLETE — VERDICT ===` (closing form,
no NEXT offered).

---

## Iteration turns (after T8)

When the user invokes REBUTTAL / DEEPEN / BRANCH from the closing
sentinel, the turn layout changes:

**REBUTTAL**
- A new turn is produced running the specific role only, with the user's
  counterargument as additional input. The turn numbers continue
  sequentially: T9 if the original run ended at T8.
- If the rebuttal cites a Hersteller or Community source the original
  grounding missed, the Chairman may insert a GROUND DEEPEN turn first
  to update the grounding block, then re-run the role.
- T8 is re-issued (as a new T10/11/etc.) with the revised finding folded
  in. The prior T8 is preserved in COUNCIL.md — not overwritten.

**DEEPEN**
- A new turn is produced scoped to the named point. If it targets a role,
  the role's micro-format applies. If it targets GROUND, the grounding
  block is extended, not replaced.
- A follow-up Chairman turn re-runs the MECE check.

**BRANCH**
- A full new Council runs T1 → T8 with the user's new premise as the
  established context. COUNCIL.md records both branches — the original
  verdict is preserved, the branch is appended.

---

## QUICK mode (3 turns)

QUICK compresses the eight-phase sequence because the inferred question is
narrow enough that role-by-role live listening is overkill. The live-turn
contract is weakened here by design — a user who wants full live listening
picks FULL.

**T1 — ORIENT + GROUND** (one message)
- Mode/context/restated question/turn plan/cost.
- One Hersteller reference and one Community reference with at least a
  one-line divergence note. If web access is available, one visible
  tool call still belongs here.
- Sentinel.

**T2 — COUNCIL** (one message containing all five roles in compressed form)
- For each role: Axis / Thesis / 3-line Finding / Dissent. Cross-reference
  is optional in QUICK but encouraged where it sharpens the finding.
- Sentinel.

**T3 — VERDICT**
- Chairman citation rule still applies (short quote per role).
- MECE check still applies.
- Two-track output, persistence note, iteration handles.
- Closing sentinel.

---

## AUDIT mode (8+ turns)

AUDIT uses the FULL 8-turn baseline. The Chairman is empowered — and expected
— to insert DEEPEN turns between role turns whenever a finding warrants extra
depth. Each inserted DEEPEN turn:

- Gets its own turn number (renumbering the remaining turns in the next
  sentinel).
- Follows the role micro-format with the DEEPEN scope named in the Thesis.
- Is fed back into the subsequent turns' context.

The total K can grow from 8 to 10, 12, or more. The user always sees the
updated K in each sentinel, so the cost is visible, never hidden.

---

## Why the serial Cartographer matters

The most common Council failure is four roles each building an implicit
mental map, and their findings drift apart because the maps differed.
Making the Cartographer explicit and serial (T3, before any other role
runs) forces a shared substrate. The cost is one extra turn; the payoff
is that Adversary, Scout, and Operator can point at the same nodes in
the same graph, and the Chairman can check coverage against the map
instead of against four private worldviews.

When the question is trivially small (QUICK mode with a single-file
context), the Cartographer's contribution may be one sentence — but it
still runs, folded into T1 inside QUICK, because the phase structure
is not negotiable by mode.
