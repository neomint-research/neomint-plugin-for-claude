---
description: Live, turn-gated Council — five MECE roles and a Chairman deliberate a consequential choice, one turn per assistant message, so the user can listen and steer between any two roles.
argument-hint: "[question or topic]"
---

# /council

The user has invoked the Council. Run it exactly as specified in the
council skill — the skill carries the full contract (seven turns, one per
assistant message; Grounding in T1; five MECE roles in T2–T6; adaptive
Verdict in T7).

## What to do now

1. Load the skill: read
   `skills/council/SKILL.md` — this is the contract. Every rule
   about turn shape, grounding, cross-role engagement, and the adaptive
   Verdict lives there. Do not paraphrase it from memory; read it.
2. Apply the shared conventions: `skills/_shared/language.md` for
   output-language rules, `skills/_shared/environments.md` for
   Claude Code / Cowork / Web differences.
3. Decide the shape first using the three observable signals on the
   input — not your own sense of how "sharp" the question feels. The
   exact rule lives under *Scope — the compressed verdict turn → How
   to decide* in `skills/council/SKILL.md`. In short: the question is
   under 30 words, contains no hedging modal verbs (e.g. *should /
   might / could / would*), and explicitly names two or more concrete
   alternatives. **All three signals must fire** for the compressed
   verdict turn to trigger. If any signal fails, fall through to seven
   turns — produce **T1 only** as your response: Read-back + Grounding
   in one message, ending in prose where the thought ends, with the
   steering primer as the final paragraph. Do not run T2 in the same
   message — the seam between turns is the point.
4. Wait for the user's steering reply (`weiter`, `widersprich`,
   `vertiefe`, `abzweig`, `stopp`, or free-text interpreted charitably)
   before producing T2.

## Guardrails the skill already enforces — reminders, not duplication

- **One turn per assistant message.** Always. No exceptions.
- **Grounding in T1, visible tool calls when web access is available.**
  Hersteller + Community + Divergence — named sources or explicit
  abstention.
- **No turn headers and no steering menus under turns.** No
  `## Cartographer · 2/7` headings, no em-dash *"Weiter: Analyst · oder
  widersprich …"* line after any turn except T1's in-prose primer. The
  role identifies itself in the first sentence; the turn ends where
  the thought ends. A council is a group of advisors, not a protocol.
- **No labeled ceremony blocks.** No `**Thesis:**`, `**Finding:**`,
  `**Cross-reference (Pflicht):**`, `**Dissent (Pflicht):**`,
  `**Resolvable?**`, or `=== TURN N/K COMPLETE ===` sentinels. Write
  prose.
- **Adaptive Verdict in T7** — matches the complexity of the question
  (one paragraph / two paragraphs / named-gap abstention), not a
  fixed template.
- **"Reicht" is not a verdict.** Stop only when sure, or name what
  would need to become true for the Council to be sure.

## Triage — when the question doesn't fit seven turns

If the question is too *ambiguous* for T1 (missing dimension, multiple
plausible interpretations), run one single diagnostic turn instead:
name the missing dimension, offer two concrete interpretations, state
the default assumption that would otherwise apply. No menu, no
sentinel — the thought ends where it ends. Do not ask multiple
questions, do not refuse.

If the three observable signals from Step 3 all fire (under 30 words,
no hedging modals, two or more named options), run one compressed
verdict turn instead of seven: brief grounding, five MECE angles in
prose named by role, verdict sentence, first step. Again, no menu, no
sentinel — the thought ends with the first step.

## Now

Produce the right shape for the user's question, following the rules
in `skills/council/SKILL.md`. Wait for steering.
