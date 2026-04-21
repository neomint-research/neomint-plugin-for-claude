---
name: council
description: >
  Invoke this skill ONLY when the user explicitly asks for the Council —
  by name ("use the council", "run council", "council skill") or by the
  `/council` convention. Do NOT auto-trigger on general decision language
  — in Claude Code and Cowork the user invokes the Council via the
  `/council` slash command, not via automatic skill matching. This skill
  exists primarily as a Claude AI (Web) fallback where slash commands
  are unavailable. Five MECE roles (Analyst, Cartographer, Adversary,
  Scout, Operator) synthesised by a Chairman, delivered turn by turn —
  one phase per message, ending in a sentinel so the user can follow and
  intervene. Do not use for: factual lookup, code generation, file
  transforms, or single-voice answers.
disable-model-invocation: true
---

# COUNCIL — Turn-Gated Context-Aware Judgment (Web Fallback)

A judgment skill that never evaluates an isolated question, only a question in
the state of its environment. Five MECE roles, one Chairman synthesis, and a
turn-gated deliberation protocol so the user can actually *listen* to the
Council — every phase is a separate assistant message that stops at a visible
sentinel and waits for the user to continue, rebut, deepen, branch, or abort.

**Primary entry point (Claude Code & Cowork): `/council`.** This SKILL.md is
the web fallback and is only invoked when the user explicitly names the skill
(the `disable-model-invocation: true` frontmatter blocks auto-triggering so the
Council does not fire on general decision language). The full contract and
turn-by-turn instructions live in `../../commands/council.md` — read that file
first when this skill is invoked, then follow it.

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

---

## Turn-gated deliberation — the live contract

**One phase = one assistant message.** Never two. Never half.

**Every phase message MUST end with exactly this sentinel block:**

```
=== TURN <N>/<K> COMPLETE — <PHASE NAME> ===
⏸ AWAITING USER. Reply NEXT to run T<N+1> <next phase>.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> · ABORT
```

**Every phase message MUST open with a turn header:** `## Turn <N>/<K> — <PHASE NAME>`

For T<K> (the final turn), replace the AWAITING-USER line with:
`⏸ Council closed. Reply REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> to continue the dialogue.`

**Continuation tokens:** NEXT, REBUTTAL, DEEPEN, BRANCH, ABORT. Interpret free-text charitably and name the interpretation in the next turn's opening line.

### Anti-shortcut enforcement

- Sentinel is the only legal ending for a phase message.
- Two `## Turn <N>/<K>` headers in one message = two phases collapsed. Violation.
- `K` is fixed at T1 and does not change mid-run silently (AUDIT DEEPEN may grow K). A silent drop is a NO-DOWNGRADE violation.

---

## Step 0 — Orient silently, then announce the turn count

```
Filesystem / repo access   →  CODE-MODE
Files attached / uploaded  →  DOC-MODE
Text only                  →  CHAT-MODE
```

Depth inference (three AND-linked signals):

```
QUICK   Closed question + ≤1 doc or ≤200 lines + no dependency signals   → 3 turns
FULL    Decision language + ≥2 docs or structured area + ≥1 dependency   → 8 turns
AUDIT   Completeness/gap question + subject is the repo/doc itself       → 8+ turns
```

If signals are unclear, run a T1/1 DIAGNOSTIC with `Mode: DIAGNOSTIC` on the
first line. Default to FULL when substantive-but-ambiguous.

---

## Turn map — one phase per message

### FULL (8 turns)

```
T1  ORIENT       Mode, context, restated question, turn plan, cost
T2  GROUND       Hersteller (authoritative) + Community (practitioner)
T3  CARTOGRAPHER Dependency map, load-bearing markers, optional SCOPE-CUT
T4  ANALYST      Derivation validity
T5  ADVERSARY    Failure modes against the map
T6  SCOUT        Blind spots against the map
T7  OPERATOR     Concrete execution plan
T8  VERDICT      Chairman MECE check + two-track output + iteration handles
```

### QUICK (3 turns)

```
T1  ORIENT + GROUND   Mode/context/restated/turn plan + 1 Hersteller + 1 Community ref
T2  COUNCIL           All five roles in one message, compressed
T3  VERDICT           Chairman synthesis + two-track output + handles
```

### AUDIT (8+ turns)

Same backbone as FULL; Chairman may insert DEEPEN turns between phases.

---

## The five roles (MECE)

```
CARTOGRAPHER  Internal, dynamic   What depends on this?
ANALYST       Internal, static    Is the derivation valid?
ADVERSARY     External, dynamic   What destroys this?
SCOUT         External, static    What aren't we seeing?
OPERATOR      Operational         What do we actually do?
```

For method, deliverable, failure modes, and abstention triggers per role, read
`references/roles.md` only if a role turn is under-producing.

---

## Role turn micro-format (T3–T7)

```
## Turn <N>/<K> — <ROLE>
**Axis:** <the role's MECE question, restated>

**Thesis (one sentence):** <the single bet this role is making>

**Finding (hardest-first):**
<2-6 paragraphs of concrete, referenced analysis, hardest sub-question first>

**Cross-reference (mandatory from T4 onward):**
- <PriorRole @ T<n>>: "<direct short quote>" — <agree / diverge / extend>
  because <reason grounded in this role's axis>

**Dissent (mandatory from T4 onward):**
<Either a substantive disagreement with a prior role, or
"No dissent: I concur with <role> @ T<n> because <reason>". Silence is not acceptable.>

**Resolvable?**
<"Finding stands." — OR — "Abstention: not judgeable because <missing input>.
Resolvable by <concrete action>.">

=== TURN <N>/<K> COMPLETE — <ROLE> ===
⏸ AWAITING USER. Reply NEXT to run T<N+1> <next phase>.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> · ABORT
```

T3 CARTOGRAPHER has no prior role — replace Cross-reference/Dissent with a **Map integrity** line listing load-bearing vs. incidental nodes.

---

## T2 GROUND — visible tool calls, not narration

When web access is available, T2 MUST contain at least one actual `WebSearch`
and/or `WebFetch` tool invocation — visible in the conversation. Narrating "I
searched for X" without the call is a contract violation.

Offline: open with `Web access unavailable — falling back to trained knowledge with cutoff <YYYY-MM>.`

Grounding block (both slots must be named or explicitly abstained on):

```
**Hersteller (authoritative source):** <source, date/version, one-line position>
**Community (practitioner consensus):** <source(s), one-line position>
**Divergence:** <one line, or "Aligned on X">
```

For source taxonomy and depth-by-mode scaling, read `references/ground.md`.

---

## T8 VERDICT output template

```
## Turn <K>/<K> — VERDICT
# Council Verdict — <short question restatement>
Mode: <QUICK | FULL | AUDIT>   Context: <CODE | DOC | CHAT>

## Grounding (cited from T2)
**Manufacturer (Hersteller):** <one-line from T2>
**Community:** <one-line from T2>
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
- Overlap detected: <none / describe>
- Unjudgeable dimension: <none / named>
- Cross-reference integrity: <each T4+ cited, or exception>

## OPERATIVE track
<technical recommendation with references and follow-ups>

## MANAGEMENT track
<plain-language recommendation + first step + risk note>

## Persistence
<one of: "Writing/updating COUNCIL.md at <path>" (CODE-MODE) |
 "Proposing COUNCIL.md for this decision — see <path>" (DOC-MODE / Web) |
 "Skipping COUNCIL.md (CHAT-MODE, no persistence surface)">

=== TURN <K>/<K> COMPLETE — VERDICT ===
⏸ Council closed. Reply REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> to continue the dialogue.
```

**Chairman citation rule** — every role turn is quoted. Chairman adds NO new findings under its own voice. For persistence schema: `references/persistence.md`.

---

## Rigor duties

- **TURN-GATED** — one phase per message.
- **GROUND-FIRST** — No role speaks before both the Hersteller position and the Community position are on the table. Silent omission of either source is a contract violation.
- **HARDEST-FIRST** — hardest sub-question addressed first, not last.
- **NO-DOWNGRADE** — K is fixed at T1. Use SCOPE-CUT inside T3 instead of silent dilution.
- **CHAIRMAN-VETO** — one named rejection of a role that produces a platitude; inserts a DEEPEN turn.
- **EXPLICIT ABSTENTION** — either a finding, or "Not judgeable because X is missing. Resolvable by Y."
- **DISSENT OR REASONED CONCURRENCE** — silent agreement is indistinguishable from not listening.
- **VERDICT COMPLETENESS** — Stop only when sure, or explicitly name what would need to become true for the Council to be sure. "3/5 roles converge, 2/5 inconclusive" is a status report, not a verdict.

---

## Anti-patterns

- **Two phases in one assistant message.** Contract violation.
- A message that ends without the sentinel.
- Changing K mid-run silently.
- A role turn without Thesis / Cross-reference / Dissent / Resolvable?.
- GROUND without visible tool calls when web access is available.
- A Chairman verdict that doesn't cite each role by quote.
- A Chairman verdict that introduces a new finding under its own voice.
- Skipping COUNCIL.md because "the user didn't ask".

---

## Stopping criteria — no silent stops

1. Chairman issues a recommendation with one first step in T8.
2. Chairman explicitly abstains — naming each unjudgeable dimension, what input would resolve it, and the consequence.
3. User triggers ABORT.

Stop only when sure, or name what would need to become true for the Council to
be sure. "Reicht" — "good enough" — is not a valid terminator.

---

## Procedure with file access (Claude Code & Cowork)

Use `/council` — the slash-command form is the primary entry point in these
environments. This SKILL.md is a fallback and its `disable-model-invocation`
setting blocks the auto-match. If the user types the slash command, the
instructions in `../../commands/council.md` are authoritative.

If the user explicitly invokes this skill (by name) in Claude Code or Cowork:
read `../../commands/council.md` first and follow it to produce T1 ORIENT. Do
not replicate the contract here — it would drift.

---

## Procedure in Claude AI (Web)

Web has no slash-command mechanism, so this SKILL.md IS the entry point when
the user explicitly invokes the Council by name ("use the council", "run
council", etc.). The turn-gated contract above applies unchanged. Web-specific
handling:

1. **T1 ORIENT** — detect DOC-MODE vs CHAT-MODE from what the user provided. If the user references a repo but didn't upload it, run a T1/1 diagnostic.
2. **T2 GROUND via web search.** Use live search if available. Otherwise fall back to trained knowledge with cutoff caveat.
3. **T3–T7** run the full role sequence, one phase per message, each ending in the sentinel. The user drives NEXT.
4. **T8 Persistence as a download.** Offer `COUNCIL.md` as a downloadable markdown artifact. Tell the user: paste it back next session and the Council picks up where it left off.
5. **Cost transparency** still applies — T1 shows K once.

Web does not reduce rigor or weaken the live-turn contract. It only changes
persistence from "write to disk" to "offer as download".

---

## Additional references (load on demand only)

The `../../commands/council.md` file is self-sufficient for a standard run.
Read a reference only when the current turn genuinely needs detail not in that
file or in this SKILL.md:

- `references/roles.md` — full method, deliverable, failure modes, abstention triggers per role.
- `references/ground.md` — Hersteller/Community source taxonomy, divergence patterns, depth-by-mode scaling.
- `references/persistence.md` — `COUNCIL.md` schema, update rules, cross-environment handling.
- `references/turns.md` — live-turn contract in detail, anti-shortcut enforcement, worked FULL/QUICK/DIAGNOSTIC example skeletons.
- `references/phases.md` — detailed phase mechanics per turn (T1 through T8), hand-off formats.

Do not read references up front. Progressive disclosure is the point.
