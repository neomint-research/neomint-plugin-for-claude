# COUNCIL — The Live-Turn Contract

This document is the single source of truth for how the Council turns into
a live, followable deliberation instead of a single wall-of-text answer.
Read it when in doubt about turn structure, sentinel format, or continuation
tokens. The rules here take precedence if a conflict with phases.md or
SKILL.md arises.

---

## Why turn-gated

A Council delivered as one assistant message is the shape LLMs default to
under pressure — compressed, skimmed, hard to follow, impossible to
interrupt. The user can't tell which role said what, can't push back on
a specific argument without restarting, and can't tell whether the
Chairman actually *listened* to the roles or just summarised the prompt.

Turn-gating solves this by treating each phase as its own assistant
message. The user sees each role speak, one at a time, on the record.
Between any two turns the user can:

- reply NEXT and keep going,
- rebut a specific role's finding,
- deepen any phase on a specific point,
- branch to a new premise, or
- abort cleanly.

The Council behaves like a council chamber, not a report.

---

## The sentinel (exact format)

Every phase message MUST end with exactly this block:

```
=== TURN <N>/<K> COMPLETE — <PHASE NAME> ===
⏸ AWAITING USER. Reply NEXT to run T<N+1> <next phase>.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> · ABORT
```

Field rules:

- `<N>` — the turn number just produced (1-indexed).
- `<K>` — the total turn count for the active mode. K is fixed at T1 and
  may only grow (AUDIT DEEPEN insertions); it never shrinks.
- `<PHASE NAME>` — one of: ORIENT, GROUND, CARTOGRAPHER, ANALYST, ADVERSARY,
  SCOUT, OPERATOR, VERDICT, DIAGNOSTIC (for T1/1 mini-runs), or the QUICK
  equivalents ORIENT+GROUND and COUNCIL.
- For T<K> (the final turn), replace the AWAITING-USER line with:
  `⏸ Council closed. Reply REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> to continue the dialogue.`
  No NEXT option on the final sentinel — there is no next turn in the
  standard sequence.

---

## The turn header (exact format)

Every phase message MUST open with a header line:

```
## Turn <N>/<K> — <PHASE NAME>
```

This pairs with the sentinel to bracket each turn. Any assistant message
that contains two turn headers is a contract violation (two phases collapsed
into one message).

---

## Continuation token semantics

```
NEXT       Run T<N+1> in sequence.
REBUTTAL   "REBUTTAL Analyst <my counter>" — re-run the Analyst's turn
           with the counter as additional input. Only legal after the
           named role has already had a turn.
DEEPEN     "DEEPEN Cartographer <point>" — insert a DEEPEN turn scoped
           to the named role or phase. Can target any phase that has run.
BRANCH     "BRANCH <new premise>" — restart from T1 with the new premise
           established. COUNCIL.md preserves both branches.
ABORT      End the run cleanly. If COUNCIL.md exists, record the abort
           with the partial state.
```

### Free-text interpretation

Users often don't reply with the exact token. Interpret charitably:

- Silence, "ok", "continue", "go on", "ja", "weiter" → NEXT
- "I disagree with the Adversary because …" → REBUTTAL Adversary <content>
- "Can you look harder at X?" or "elaborate on X" → DEEPEN <inferred phase> <X>
- "What if instead we did Y?" or "let's try path B" → BRANCH <Y or B>
- "Stop" / "forget it" / "never mind" → ABORT

When you interpret free text as a token, open the next turn by naming the
interpretation in one line: `*Interpreting "<user text>" as REBUTTAL Adversary
"<distilled counter>".*` The user can correct before the turn's content
begins.

---

## Role turn micro-format (applies to T3–T7 in FULL/AUDIT)

```
## Turn <N>/<K> — <ROLE>
**Axis:** <the role's MECE question, restated>

**Thesis (one sentence):** <the single bet this role is making>

**Finding (hardest-first):**
<2-6 paragraphs of concrete, referenced analysis. The hardest sub-question
is addressed first, not last. File/line refs, named actors, specific events.>

**Cross-reference (mandatory from T4 onward; T3 replaces this with a
"Map integrity" line because no prior role exists to cite):**
- <PriorRole @ T<n>>: "<direct short quote from that role's turn>" —
  <agree / diverge / extend> because <reason grounded in this role's axis>

**Dissent (mandatory from T4 onward):**
<Name one point from a prior role this role disagrees with, and say why.
If there is genuinely nothing to dissent from, the line reads:
"No dissent: I concur with <role> @ T<n> because <reason>". Silence is
not acceptable — either dissent with content, or concurrence with reason.>

**Resolvable?**
<"Finding stands." — OR — "Abstention: not judgeable because <named
missing input>. Resolvable by <concrete action>.">

=== TURN <N>/<K> COMPLETE — <ROLE> ===
⏸ AWAITING USER. Reply NEXT to run T<N+1> <next phase>.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> · ABORT
```

### Why each block earns its keep

- **Thesis** — one-sentence commitment that the rest of the turn has to
  defend. Without it, a role turn can meander and never take a position.
- **Finding, hardest-first** — puts the load-bearing claim in the top of
  the turn, where attention is highest. The old skill had HARDEST-FIRST as
  a rigor rule; the micro-format makes it structural.
- **Cross-reference** — the only mechanism that turns five role turns into
  a compounding deliberation rather than five independent essays. Forcing
  a direct quote creates accountability: the later role has to *read* the
  earlier one.
- **Dissent or reasoned concurrence** — silent agreement across five roles
  is indistinguishable from not reading the prior turns. The dissent line
  forces a stance, even when the stance is "yes, and here's why".
- **Resolvable?** — explicit abstention rule made per-turn. The grader
  can verify each turn either stands or names the gap.

---

## Anti-shortcut enforcement (the #21672 problem)

Claude Code issue #21672 documents a well-known failure where parent skills
invoke sub-skills with "MANDATORY CONTINUATION" directives and Claude stops
anyway after the sub-skill completes. The turn-gated council shape here is
the structural fix, but it has its own failure mode: the model collapsing
two turns into one message under time pressure.

Defenses, in order of strength:

1. **The sentinel is the hard stop.** Once the sentinel is posted, do NOT
   add content after it. If you catch yourself about to append more, stop
   and post. The sentinel is not a decoration — it is the terminator.
2. **Turn headers bracket each turn.** Two `## Turn N/K — <PHASE>` lines in
   a single assistant message means two phases collapsed into one — a
   contract violation visible at a glance.
3. **K is fixed at T1.** If the run started at K=8 (FULL), every sentinel
   must show K=8 (or higher if AUDIT DEEPEN grew it). A silent drop from
   K=8 to K=5 is a NO-DOWNGRADE violation.
4. **The grader (`scripts/grade.py`) asserts the contract statically.** The
   turn headers, sentinels, thesis lines, cross-reference markers, and
   citation blocks are all checked against the SKILL.md body. Contract
   decay surfaces in CI.

---

## Worked example — FULL run skeleton

A FULL run is a sequence of eight assistant messages. The user's NEXT
replies are shown between them. Content is elided; focus on structure.

---

**Assistant (T1):**

```
## Turn 1/8 — ORIENT
Mode: FULL   Context: CODE   Question: [restated]
Turn plan: T1 ORIENT (here) · T2 GROUND · T3 CARTOGRAPHER · T4 ANALYST ·
T5 ADVERSARY · T6 SCOUT · T7 OPERATOR · T8 VERDICT
Cost estimate: ~6 files scanned, 2 web lookups, ~4–6k tokens total.

[one-paragraph restatement of the question and what the Council will judge]

=== TURN 1/8 COMPLETE — ORIENT ===
⏸ AWAITING USER. Reply NEXT to run T2 GROUND.
Alternatives: DEEPEN ORIENT <what to clarify> · BRANCH <different premise> · ABORT
```

**User:** `NEXT`

---

**Assistant (T2):**

```
## Turn 2/8 — GROUND

[WebSearch tool call visible here]
[WebFetch tool call visible here]

**Hersteller (authoritative source):** [source, position, URL]
**Community (practitioner consensus):** [source(s), position, URL(s)]
**Divergence:** [one line]

=== TURN 2/8 COMPLETE — GROUND ===
⏸ AWAITING USER. Reply NEXT to run T3 CARTOGRAPHER.
Alternatives: REBUTTAL Grounding <counter> · DEEPEN GROUND <point> · BRANCH <new premise> · ABORT
```

**User:** `NEXT`

---

**Assistant (T3):**

```
## Turn 3/8 — CARTOGRAPHER
**Axis:** What depends on this?
**Thesis:** [one-sentence bet]
**Finding (hardest-first):** [dependency map, 2-6 paragraphs]
**Map integrity:** Load-bearing nodes: A, B, C. Incidental: D, E.
**Resolvable?** Finding stands.

=== TURN 3/8 COMPLETE — CARTOGRAPHER ===
⏸ AWAITING USER. Reply NEXT to run T4 ANALYST.
Alternatives: REBUTTAL Cartographer <counter> · DEEPEN Cartographer <point> · BRANCH <new premise> · ABORT
```

**User:** `NEXT`

---

**Assistant (T4):**

```
## Turn 4/8 — ANALYST
**Axis:** Is the derivation valid?
**Thesis:** [one-sentence bet]
**Finding (hardest-first):** [2-6 paragraphs]
**Cross-reference:**
- Cartographer @ T3: "[short quote]" — extend because [reason]
**Dissent:** [named disagreement with a prior role OR reasoned concurrence]
**Resolvable?** Finding stands.

=== TURN 4/8 COMPLETE — ANALYST ===
⏸ AWAITING USER. Reply NEXT to run T5 ADVERSARY.
Alternatives: REBUTTAL Analyst <counter> · DEEPEN <phase> <point> · BRANCH <new premise> · ABORT
```

---

T5–T7 follow the same shape, each citing at least one prior role.

---

**Assistant (T8):**

```
## Turn 8/8 — VERDICT
# Council Verdict — [short question restatement]
Mode: FULL   Context: CODE

## Grounding (cited from T2)
**Manufacturer (Hersteller):** [one-line from T2]
**Community:** [one-line from T2]
**Divergence:** [one line from T2]

## Citations
- Cartographer @ T3: "[short quote]"
- Analyst @ T4: "[short quote]"
- Adversary @ T5: "[short quote]"
- Scout @ T6: "[short quote]"
- Operator @ T7: "[short quote]"

## Chairman — MECE check
- Grounding complete: yes/named abstention — blocks publication if incomplete
- Dimensions covered: 5/5 or named gap
- Overlap detected: none / described
- Unjudgeable dimension: none / named
- Cross-reference integrity: all roles T4+ cited, or named exception

## OPERATIVE track
[technical, referenced, grounded in the cited role quotes]

## MANAGEMENT track
[plain language, one recommendation, one first step, risk note]

## Persistence
Writing/updating COUNCIL.md at [path].

=== TURN 8/8 COMPLETE — VERDICT ===
⏸ Council closed. Reply REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> to continue the dialogue.
```

---

## Worked example — QUICK run skeleton (3 turns)

QUICK compresses. Micro-format is lighter, but the sentinels are identical.

**Assistant (T1/3):**

```
## Turn 1/3 — ORIENT + GROUND
Mode: QUICK   Context: CHAT   Question: [restated]
Turn plan: T1 ORIENT+GROUND (here) · T2 COUNCIL · T3 VERDICT
Cost estimate: ~1k tokens.

**Hersteller:** [one reference]
**Community:** [one reference]
**Divergence:** [one line or "aligned"]

=== TURN 1/3 COMPLETE — ORIENT + GROUND ===
⏸ AWAITING USER. Reply NEXT to run T2 COUNCIL.
Alternatives: DEEPEN <phase> <point> · BRANCH <new premise> · ABORT
```

**Assistant (T2/3):**

```
## Turn 2/3 — COUNCIL
**Cartographer** · Thesis / 3-line Finding
**Analyst** · Thesis / 3-line Finding / Dissent
**Adversary** · Thesis / 3-line Finding / Dissent
**Scout** · Thesis / 3-line Finding / Dissent
**Operator** · Thesis / 3-line Finding / Dissent

=== TURN 2/3 COMPLETE — COUNCIL ===
⏸ AWAITING USER. Reply NEXT to run T3 VERDICT.
Alternatives: REBUTTAL <role> <counter> · DEEPEN <role> <point> · BRANCH <new premise> · ABORT
```

**Assistant (T3/3):**

```
## Turn 3/3 — VERDICT
[same Citations / MECE / two-track / Persistence structure as FULL T8]

=== TURN 3/3 COMPLETE — VERDICT ===
⏸ Council closed. Reply REBUTTAL <role> <counter> · DEEPEN <role-or-phase> <point> · BRANCH <new premise> to continue the dialogue.
```

---

## Worked example — DIAGNOSTIC T1/1

When T1 cannot infer enough to plan, it degrades to a 1-turn diagnostic:

```
## Turn 1/1 — DIAGNOSTIC
Mode: DIAGNOSTIC   Context: CHAT   Turns: 1/1

I can't infer [missing dimension] — the [role name] cannot form an
opinion without knowing which of these you mean:

A) [interpretation A, with consequence for the Council]
B) [interpretation B, with consequence for the Council]

Default assumption if you don't specify: [A or B] because [reason].

=== TURN 1/1 COMPLETE — DIAGNOSTIC ===
⏸ AWAITING USER. Pick A or B, or say "default" to run with the stated assumption.
```

When the user picks, the Council restarts from T1 of the appropriate mode
with the chosen interpretation established.

---

## Anti-patterns specific to turn-gating

- **No sentinel.** The message ends and the next turn is expected to be
  "implicit". This is the #21672 pattern — the user has no way to know
  the turn is over, and subsequent turns will not run cleanly.
- **Sentinel then more content.** The sentinel is the terminator. Content
  after it is a contract violation even if it looks helpful.
- **Two turn headers in one message.** Two phases collapsed. Contract
  violation.
- **K changes mid-run silently.** If T1 announced K=8, every sentinel must
  show K=8 (or higher if AUDIT DEEPEN grew it). A silent K=5 is a
  NO-DOWNGRADE violation.
- **Free-text reply treated as ABORT by default.** Ambiguous replies are
  interpreted charitably (NEXT for "ok", REBUTTAL for "I disagree", etc.)
  and the interpretation is named in the next turn's opening line. ABORT
  only fires when the user genuinely signals stop.
- **Bundling multiple role turns under user pressure.** "Just do all five
  roles at once" is a rigor-reduction request; respond by running T<N+1>
  normally and pointing out that the live contract is the point.
