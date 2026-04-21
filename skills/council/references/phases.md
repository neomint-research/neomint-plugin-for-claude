# COUNCIL — Phase Mechanics in Detail

The five phases exist because a Council without structure collapses into
opinion-mixing. Each phase has a fixed input, a fixed output, and a fixed
hand-off. Sequence is structural.

For the grounding discipline in Phase 1, see `ground.md`. This document
covers mechanics; `ground.md` covers what counts as a valid Hersteller
or Community source, how to scale depth per mode, and how to handle
divergence.

---

## Phase 0 — ORIENT

**Purpose:** Capture the environment so every later judgment is anchored
in real context, not in the user's framing alone.

**Input:** Whatever the user provided (repo access, uploads, text) plus
the ambient environment (Claude Code / Cowork / Web).

**Activity:**
- Detect CODE-MODE / DOC-MODE / CHAT-MODE from signals.
- In CODE-MODE, check for `COUNCIL.md` at the repo root and read it if
  present — prior Council state is load-bearing context.
- Infer QUICK / FULL / AUDIT from the three hard signals.
- If ambiguous: ask exactly one diagnostic question (format defined in
  SKILL.md).

**Output to next phase:** A short orientation note — inferred mode,
inferred context, a one-sentence restatement of the question the Council
will judge.

**Silent stop condition:** None. ORIENT always produces something, even
if it's "Running CHAT-MODE QUICK with assumption X because the user's
message doesn't expose more."

---

## Phase 1 — GROUND

**Purpose:** Put the Hersteller (authoritative / first-party source) and
the Community (practitioner consensus) on the table *before* any role
speaks. A Council that reasons without grounding rediscovers settled
knowledge or silently contradicts it; either way it wastes the user's
time on a question the field has already answered. See `ground.md` for
what counts as each kind of source and how depth scales per mode.

**Input:** Phase 0 orientation note and the question itself.

**Activity:**
- Surface the Hersteller position first. Live lookup if web access is
  available; otherwise fall back to trained knowledge with cutoff.
- Surface the Community position second. At least one independent
  source in QUICK; multiple in FULL / AUDIT.
- Identify divergence, if any, between Hersteller and Community.

**Output to next phase:** A short grounding block —

```
HERSTELLER: <source, version, one-sentence position>
COMMUNITY:  <source(s), one-sentence position>
DIVERGENCE: <one line; or "Aligned on X">
```

The Cartographer uses DIVERGENCE to weight dependencies; the four
judging roles each see the full block in their starting context; the
Chairman's MECE check includes a grounding-completeness line.

**Silent stop condition:** None. If no Hersteller exists, state it
("No authoritative source for this question; stated.") — that is a
finding, not a skip. If Community is unreachable, state it with the
cutoff. Both must appear in the output, either as a source or as a
named abstention.

---

## Phase 2 — MAP

**Purpose:** Produce the dependency graph that Phase 3 shares as common
substrate. If Phase 3 had to each derive their own map, their findings
would talk past each other.

**Input:** Phase 0 orientation note, Phase 1 grounding block, and the
available material.

**Activity:** The Cartographer works alone. Nothing else runs in parallel.

**Output:**
- Upstream / downstream dependency list.
- Load-bearing markers.
- Optional SCOPE-CUT proposal if the full question is too large for a
  single Council run. A scope-cut is not a downgrade — it's a legitimate
  narrowing of the question while preserving rigor on the narrower slice.

**Silent stop condition:** If the Cartographer abstains ("no artifact
surface"), the Chairman decides whether to:
- proceed with an explicit "no map available" marker in Phase 2, or
- pause and ask the user for the missing surface.

Default: proceed with the marker. Better to have a Council with a flagged
gap than a stalled Council.

---

## Phase 3 — COUNCIL

**Purpose:** Four independent dimensional judgments against a shared
grounding and a shared map.

**Input:** Phase 0 + Phase 1 + Phase 2 outputs. Every role sees all three.

**Activity:** Analyst, Adversary, Scout, Operator work in parallel
(conceptually — in single-LLM reasoning this means each role is treated
as a separate pass with its own axis commitment, not four roles mixed in
one paragraph).

**Hand-off format:** Each role produces its finding in the structure:

```
## <ROLE> — <axis question>
Finding: <specific, referenced>
— OR —
Not judgeable because: <named missing input>
```

**Chairman moderation during Phase 2:**
- If a role output is vague, platitudinal, or ducks the axis — apply
  CHAIRMAN-VETO once with the specific gap named, and re-invoke that
  role.
- After the single rejection, accept either a finding or an explicit
  abstention — but not a second round of hedging.

**Silent stop condition:** None. All four roles must produce either a
finding or an explicit abstention before Phase 4 can begin.

---

## Phase 4 — VERDICT

**Purpose:** Chairman synthesis with MECE self-validation.

**Input:** Phase 1 grounding block + all role outputs from Phase 3.

**Activity:**
1. MECE check:
   - Grounding complete — Hersteller + Community each named or named as
     explicit abstention. A missing slot blocks publication.
   - 5 dimensions covered, or name the gap(s) explicitly.
   - Overlap between roles → flag as structural unclarity.
   - Unjudgeable dimension(s) → name what's missing.
2. Produce the two-track output (OPERATIVE + MANAGEMENT).
3. Preserve role attribution — the reader must see who said what.
4. Append iteration handles: REBUTTAL, DEEPEN, BRANCH.
5. In CODE-MODE / Cowork: write a new entry to `COUNCIL.md`. In Web:
   offer an updated `COUNCIL.md` artifact as download.

**Stopping criteria (one of three, never silent):**
- Recommendation with one first step.
- Explicit abstention on a named dimension with what's needed.
- User-triggered abort.

---

## Iteration phases (after the first verdict)

When the user invokes REBUTTAL / DEEPEN / BRANCH, the phase layout changes:

**REBUTTAL**
- Re-enter Phase 3 for the specific role only, with the user's
  counterargument as additional input.
- Chairman re-runs Phase 4 MECE check including the revised finding.
- If the rebuttal cites a Hersteller or Community source the original
  grounding missed, re-enter Phase 1 to update the grounding block
  first, then re-run the role.

**DEEPEN**
- Re-enter Phase 1 scoped to a named grounding question (if the user
  wants a specific source verified).
- Or re-enter Phase 2 scoped to the named point (if Cartographer).
- Or re-enter Phase 3 scoped to the named role and point.
- Chairman re-runs Phase 4 with the deeper finding folded in.

**BRANCH**
- Full new Council: Phase 0 → Phase 4 with the user's new premise as
  the established context. COUNCIL.md records both branches — the
  original verdict is not overwritten, the branch is appended.

---

## Why the serial Cartographer matters

The most common Council failure is four roles each building an implicit
mental map, and their findings drift apart because the maps differed.
Making the Cartographer explicit and serial forces a shared substrate.
The cost is one extra pass; the payoff is that Adversary and Scout can
point at the same nodes in the same graph and the Chairman can check
coverage against the map instead of against four private worldviews.

When the question is trivially small (QUICK mode with a single-file
context), the Cartographer's output may be one sentence — but it still
runs. The phase structure is not negotiable by mode.
