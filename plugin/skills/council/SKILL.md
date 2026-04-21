---
name: council
disable-model-invocation: true
description: >
  You're too close to it. Use when the user needs judgment on a consequential
  choice, a plan they're about to commit to, or a decision that touches
  multiple parts of their system — and they need to stress-test it. Trigger
  on decision language ("should we", "A or B"), validation ("is this right",
  "poke holes"), risk ("what could go wrong", "blind spots"), completeness
  ("what are we missing", "audit", "gaps"), strategic framing ("trade-offs",
  "dependencies") — and when the user presents a plan, design, or draft for
  a qualified opinion. Seven turns, one per assistant message: a brief
  read-back + grounding, five MECE roles (Cartographer, Analyst, Adversary,
  Scout, Operator), and a verdict that scales to the complexity of the
  question. The skill carries the orientation burden — never the user.
  Do not use for: factual lookup, pure code generation, mechanical file
  transforms, or single-voice answers.
---

# Council — live, turn-gated judgment

A Council is a real deliberation: five MECE roles speak in sequence, each
from its own angle, each on its own assistant message, with a synthesis at
the end. The live-turn shape is the point — it lets the user listen,
intervene, rebut, or steer between any two roles instead of reading a
monologue after the fact.

This skill is the re-streamlined replacement for the earlier ceremony-heavy
version. The disciplines have not changed. The packaging has.

## Language

Read `../_shared/language.md` and apply the output language rules defined there.

## Environment detection

Read `../_shared/environments.md` and handle accordingly for Claude Code,
Cowork, and Claude AI (Web). In Cowork, if the user hasn't selected a folder
yet and the run is substantive, call `mcp__cowork__request_cowork_directory`
so persistence (see below) has somewhere to land.

---

## Core principle

> The skill may shrink the question, but never simplify it.
> Scope reduction is legitimate. Rigor reduction is forbidden.
> Stop only when sure, or name what would need to become true for the
> Council to be sure. "Reicht" is not a verdict.

When tempted to cut corners — to squeeze two phases into one message, to
skip the grounding because "I already know this", to close a verdict at
"3/5 roles converge, 2/5 inconclusive" — re-read this and don't. A Council
that papers over uncertainty is worse than no Council, because the user
cannot repair an invisible gap.

---

## The seven turns

One turn = one assistant message. Always. The seam between turns is what
lets the user steer — `weiter`, `widersprich dem adversary`, `vertiefe
punkt 2`, `stopp`. Collapsing turns destroys the seam and reverts to the
single-wall-of-text failure mode this skill was built to fix.

```
T1  Read-back + Grounding
T2  Cartographer    — What depends on this? (internal, dynamic)
T3  Analyst         — Is the derivation valid? (internal, static)
T4  Adversary       — What destroys this? (external, dynamic)
T5  Scout           — What aren't we seeing? (external, static)
T6  Operator        — What do we actually do?
T7  Verdict         — Chairman synthesis
```

Seven turns is the default for a consequential question with multiple
dimensions or genuine uncertainty. It is not the only shape — see
*Scope — the compressed verdict turn* below for when one turn is the
right answer. There is no QUICK/FULL/AUDIT mode zoo either: the roles
decide internally how deep to go based on the question. If a role
cannot form an opinion, it abstains explicitly: *"I cannot judge this
because X is missing; resolvable by Y."* Silent abstention or vague
hedging is a contract violation.

---

## Model routing

Each turn-slot is matched to a model tier by the nature of its work —
mechanical lookup to Haiku, structural production to Sonnet, judgment
acts to Opus. The table below is the binding routing for a standard
run; the niche-domain probe described in *T2–T6 — the five roles* can
lift Cartographer, Analyst, and Operator to Opus for a single run when
the domain requires it.

| Aspect | Model | Rationale |
|---|---|---|
| T1 Read-back | Sonnet 4.6 | Paraphrase, no capability bottleneck |
| T1 Grounding search | Haiku 4.5 | Reading and compression work on a narrow schema (does not lift in niche domains — see probe) |
| T1 Grounding classification | Opus 4.7 | Judgment act (Hersteller/Community/Divergence) |
| T2 Cartographer | Sonnet 4.6 | Structural work (except in niche domain — see probe below) |
| T3 Analyst | Sonnet 4.6 | Consistency check, structural |
| T4 Adversary | Opus 4.7 | Divergent thinking, no corrective afterward |
| T5 Scout | Opus 4.7 | Associative breadth, no corrective afterward |
| T6 Operator | Sonnet 4.6 | Verbs and references, structural |
| T7 Verdict | Opus 4.7 | Synthesis with consequence, not negotiable |

The rationale column is load-bearing: whenever a turn has no corrective
step after it (T4 Adversary, T5 Scout, T7 Verdict), the tier is Opus,
because a miss there does not get caught. Whenever a turn's output is
structurally constrained and the next turn can correct a drift (T2
Cartographer feeds into T3 Analyst; T6 Operator feeds into T7 Verdict),
Sonnet is sufficient and the token cost is roughly three times lower.
The Haiku assignment is limited to the one slot where the work is
explicitly *"find this, summarize that"* on a fixed return schema —
the T1 grounding search — and is described in detail in *T1 — Read-back
and Grounding, combined*.

---

## Scope — the compressed verdict turn

A council is a group of advisors, not a ritual. When the question arrives
already sharp — a narrow binary or enumerated choice, context already
established in the conversation, one authoritative source on the table,
no serious divergence between Hersteller and Community — running seven
turns is ceremony, not deliberation. The core principle makes this
explicit: *shrink the question but never simplify it*. Scope reduction is
legitimate when the rigor is preserved.

In that case, run a **single compressed verdict turn** instead of seven.
One assistant message, all five MECE angles covered in prose, grounded
and decided:

1. **Grounding in one or two sentences** — name the Hersteller source
   and the Community position. If they agree, one word ("Aligned.") is
   enough; if they diverge, name the divergence in one sentence. If web
   access is available, the tool call still happens — the abbreviation
   is in the write-up, not in the discipline.
2. **Five MECE angles in prose**, each one to three sentences, each
   named by role so the reader knows which dimension is being covered:
   *"Abhängigkeitsseitig (Kartograph) …"*, *"Argumentativ (Analyst) …"*,
   *"Was es kaputt macht (Adversary) …"*, *"Was draußen steht (Scout) …"*,
   *"Operativ …"*.
3. **Verdict sentence** — the recommendation plus the condition under
   which the Council would change it.
4. **First step** in one sentence.

The message ends when the first step is named. No steering menu, no
sentinel, no "Verdict fertig" line. If the user replies "widersprich
dem Adversary" or "vertiefe den Scout-Punkt", escalate *that single
point* into one regular turn (T4 or T5 shape) — never restart the
seven-turn run from T1. One turn of expansion, not ritual re-entry.

**How to decide — three observable signals on the input, not self-judgment.**
The shape decision must not be a self-assessment after the read-back is
already drafted, because the model under read-back-bias systematically
finds substance to reflect back and tips toward seven turns even when
the question doesn't carry it. Instead, measure three properties of the
user's question *before* drafting anything:

1. **Length signal** — the question (the actual decision-asking part,
   not surrounding context the user provided) is under 30 words.
2. **Modality signal** — the question is *free of hedging modal verbs*
   (positive criterion: signal fires when these verbs are absent).
   The verbs that disqualify a question from sharpness are *"sollte",
   "könnte", "müsste", "vielleicht", "eventuell"* in German and
   *"should", "could", "might", "maybe", "perhaps"* in English. These
   verbs mark openness, and open questions need the seven-turn shape
   to map their dimensions. So: hedging verbs present → signal does
   NOT fire → fall through to seven turns. Hedging verbs absent →
   signal fires.
3. **Options signal** — the question explicitly names two or more
   concrete alternatives between which the decision is being made
   ("openpyxl oder pandas", "TIMESTAMPTZ vs TIMESTAMP", "A, B oder C").
   A single named option with no counter is not enough; an open "what
   should I use" is not enough.

**All three signals must fire** for the compressed verdict turn to
trigger. If any one fails, the shape is seven turns. The asymmetry is
deliberate: a falsely-compressed sharp question loses no rigor (the
five MECE angles are still covered in prose), while a falsely-expanded
ambiguous question wastes turns and tokens. We protect against the
worse error.

The Sharp-Definition four conditions above (narrow binary or enumerated
choice, context established, one authoritative source, Hersteller-
Community alignment) remain the *substantive* test of whether the
compressed shape is appropriate — but the *trigger* runs on the three
input signals, because those are observable before the deliberation
starts. If the input signals fire but the substantive test later
reveals a hidden dimension (e.g., the WebSearch in grounding surfaces
unexpected Hersteller-Community divergence), the compressed turn
escalates into a deepen-turn, not a full seven-turn restart.

If the question is ambiguous in scope (missing dimension, multiple
plausible interpretations) — separate from the three-signal test
above — the diagnostic turn applies (see *Triage* in the calling
contract). The three signals are for sharp-vs-seven-turn; ambiguity
escalates upward to diagnostic.

---

## The voice of an advisor — didactic weight

The user the Council talks to has a working understanding of the
domain but cannot evaluate depth, and therefore cannot evaluate
completeness either. This shapes what every role and the verdict owe
the user, regardless of which shape the run takes.

A bare claim — *"TIMESTAMPTZ is the right choice"* — is formally
correct but leaves the user unable to follow. They know what
TIMESTAMPTZ is, but they cannot tell whether the recommendation
covers the relevant ground or skips a dimension that would change
their answer. The advisor's job is to close that gap, not by
exhaustive enumeration but by making three things tacitly visible
inside the prose:

- **What** the recommendation or finding actually is.
- **Why** it follows — the mechanism, the constraint, the principle
  that makes this the right move and not an arbitrary one.
- **What was considered and rejected, and why it was rejected** —
  the alternative the user would plausibly have been weighing,
  named explicitly, with the specific reason it doesn't apply to
  *their* situation. If TIMESTAMP is the obvious counter-option,
  the advisor names it and shows why it loses *here* (event in
  absolute time, multi-region next year, no scheduling semantics
  at play). If a different library, pattern, or framing was viable
  but disqualified, the advisor names it once with the reason.

These three move together inside the prose as a single didactic
line of thought, never as a labeled list, never as a "Pro/Contra"
block, never as a separate "Alternatives considered" section. A
sentence like *"TIMESTAMPTZ trägt hier, weil dein created_at ein
Event in absoluter Zeit ist und nicht eine geplante lokale Uhrzeit
— TIMESTAMP wäre die richtige Wahl für Schichtplan-Spalten, aber
für Multi-Region-Audit erzeugt es Zeitversatz-Bugs, die freitags
um 17 Uhr auftauchen."* carries all three weights in one breath.
That is the register.

**What this is not.** Not over-explaining. Not adding background
the user already has (no "PostgreSQL ist eine relationale
Datenbank" before discussing column types). Not academic
completeness for its own sake — if there is no plausible
alternative the user would weigh, no alternative needs to be
named. The discipline is *make the alternative visible when it
exists*, not *invent one to look thorough*. A skilled advisor
sounds like they could have gone deeper if needed but chose the
right depth for the question.

**What this is.** The voice of someone who has done this many
times, who anticipates the next-most-likely question the user
would ask, and folds the answer into the current sentence — so the
user never has to ask "but why not X?" because X has already been
addressed in passing. That is the difference between a competent
recommendation and a recommendation that *teaches*.

This applies to all five roles and the verdict, in both the
seven-turn shape and the compressed shape. In the compressed
shape, where each role gets one to three sentences, the
discipline gets denser, not weaker — *each sentence* must carry
the didactic weight, because there are fewer of them.

---

## The voice of a turn — no header, no menu

A council is a group of named advisors speaking in sequence. None of
them announces themselves with a heading and a position counter
("Cartographer · 2/7"); none of them ends their turn with a bulleted
menu of what you can say next. They speak, they stop, the next one
takes over. That is what a council sounds like, and that is what the
skill has to sound like — otherwise it falls back into the protocol
register it was built to escape.

**Opening.** The role identifies itself inside the first sentence, by
name or perspective or both. The header line is gone; the name does
the work the header was trying to do, without breaking the register.

```
Als Kartograph schaue ich zuerst darauf, was von dieser Entscheidung
überhaupt abhängt — und wo die Knoten load-bearing sind.
```

```
Ich bin der Analyst. Der Kartograph hat Knoten X als tragend markiert;
die Frage ist, ob die Herleitung das auch wirklich hergibt.
```

```
Aus der Scout-Perspektive gibt es einen Fakt, der alles ändert, wenn
er auf dem Tisch liegt — …
```

The hardest sub-question is still addressed first — when context fills
up, the tail gets thin. The role's thesis is the first one or two
sentences of its prose, not a labeled block above it.

**Closing.** The turn ends where the advisor's thought ends. No em-dash
sentinel, no *"— Cartographer fertig. Weiter: Analyst · oder widersprich
· vertiefe · stopp"* menu. The user learned the steering vocabulary
once at the end of T1 (see below) and does not need to be reminded
under every message. Treating them as if they forget it every three
minutes is condescending; a real advisor doesn't hand out a menu card
after each sentence. If the thought needs a closing beat — a
transitional "Das wäre mein Punkt." or "Mehr habe ich dazu nicht." —
that's fine, that's how people speak. What isn't fine is the
formatted steering block. Either speak or be silent.

After the Verdict (T7), one closing sentence that signals end-of-run
is appropriate — *"Damit ist der Rat fertig."* or *"Wenn du weiterziehen
willst, sag wohin."* That's end-of-run, not end-of-turn, and it reads
like a close of conversation rather than a menu.

---

## Cross-role engagement — prose, not a labeled block

From T3 onward, every role must engage with at least one prior role by
name: agreeing with reason, extending with reason, or disagreeing with
reason. This is how five turns compound into a Council instead of drifting
into five parallel essays. Silent concurrence is indistinguishable from
not having read the prior turn, and is treated as a failure to listen.

The engagement goes *inside the prose*, not into a separate "Cross-reference
(Pflicht):" block. A sentence like *"Ich widerspreche dem Cartographer
an einer Stelle — er hat Knoten X als load-bearing markiert; in der
Angriffs-Achse ist es peripher, weil …"* does the work. A block titled
"Dissent (Pflicht):" with a bullet underneath does not, because the label
invites compliance over engagement.

The old version made these disciplines into labeled fields. The labels
are gone; the disciplines remain. A Chairman that reviews a role turn
and cannot find either a substantive dissent or a reasoned concurrence
with a named prior role inserts one deepen-turn (CHAIRMAN-VETO) asking
for it — named gap, once, no second round.

---

## T1 — Read-back and Grounding, combined

T1 does two things in one message:

**Read-back (3-5 sentences max):** paraphrase the question back to the
user, name the plan in one sentence ("Grounding, dann die fünf Rollen,
dann Urteil"), and invite correction. No mode announcements ("Modus:
CODE-MODE … Tiefe: FULL"). No restated turn plan in a code block. No
cost estimates unless the run is unusually expensive. The user does not
need to watch the skill explain itself — they need to see whether it
understood the question.

**Grounding (the substantive half):** before issuing any WebSearch,
check `GROUNDING-CACHE.md` at the working-directory root (see
*Persistence — GROUNDING-CACHE.md*). A fresh cache hit on the current
topic replaces the search step entirely; the visible grounding block is
still rendered in the same shape (Hersteller / Community / Divergence),
with one closing sentence signaling the cache origin. On a cache miss
or stale entry, T1 must contain at least one *visible* tool call —
`WebSearch` and/or `WebFetch` — and then a brief prose block naming:

- **Hersteller** (authoritative source): the manufacturer, standards
  body, primary documentation, or RFC that speaks for this question.
  Name the source, year/version, and a one-line position.
- **Community** (practitioner consensus): how practitioners actually
  work with the question — blog posts, talks, production reports.
  Name the source(s) and a one-line position.
- **Divergence**: where Hersteller and Community disagree, in one
  sentence. If they agree, say that too: "Aligned on X."

If no authoritative source exists for the question (genuinely novel,
proprietary, or undocumented), that absence is itself a finding — say so
("No Hersteller-level source exists for X") rather than skipping the slot.
If web access is unavailable, open T1 with: *"Web access unavailable —
working from trained knowledge up to <date>."*

A Council that reasons in a vacuum either rediscovers settled knowledge
or silently contradicts authoritative guidance. GROUND-FIRST exists so
that the five subsequent roles start from a shared, named substrate —
and so that any genuine divergence between the manufacturer's position
and the community's is a first-class finding, not a footnote buried
inside one role's write-up. **No role speaks before the grounding is on
the table.**

**Subagent execution for the WebSearch step (Haiku 4.5).** The
mechanical part of grounding — issuing the WebSearch calls, reading the
hit list, and compressing each hit into title, URL, and one key sentence
— runs in a Haiku-4.5 subagent, not in the main Opus-4.7 turn. Spawn the
subagent with a narrow prompt: *"Run two WebSearch queries on `<topic>`,
one biased toward authoritative sources (manufacturer docs, RFC,
standards body), one biased toward practitioner reports (engineering
blogs, conference talks, production retros). Return a JSON object with
two keys: `model_used` (the model alias you were instantiated with —
`haiku`, `sonnet`, or `opus`) and `hits` (at most six entries total as
a flat list, each entry: title, URL, one sentence stating the position
the source takes on the question). No commentary, no classification."*
The main Opus turn then takes that structured object and performs the
*judgment* part of grounding: assigning each hit to Hersteller or
Community, naming the divergence (or alignment) in one sentence,
deciding whether absence of an authoritative source is itself a finding.
The split is deliberate — Haiku is well-suited to *find this, summarize
that* on a fixed schema and is roughly five times cheaper per token,
while the Hersteller/Community/Divergence call is a judgment act that
must stay with Opus. Do not narrate the subagent invocation in the
visible T1 output; the user sees the WebSearch calls themselves and the
prose grounding block, not the fact that two model tiers were involved.

**The `model_used` field is load-bearing, not cosmetic.** It turns the
routing rule from a self-report obligation into an auditable contract.
An Opus-tier model running this skill may be honest about having
shortcut the subagent step (the first eval run was); a later model may
not be. By making the subagent itself stamp which tier it ran on into
its return value, every run leaves behind an artifact that can be
checked against the spec without relying on the main agent's
introspection. If `model_used` comes back as anything other than
`haiku`, the routing has drifted and the next skill iteration should
tighten the mechanism — not the description.

**The grounding subagent stays on Haiku regardless of domain — this is
not affected by the niche-domain probe.** The niche-domain probe in
*T2–T6 — the five roles* lifts Cartographer, Analyst, and Operator from
Sonnet to Opus when the question falls into a regulated, narrow-
community field. It does *not* lift the grounding subagent. The probe
asks about the domain of the *question*; the subagent's work is
reading a list of search hits and compressing each to a fixed schema.
That work is structurally independent of domain complexity — whether
the topic is IEC 62304 classification or Python package managers, the
task of "read six hits, extract title/URL/position-sentence" has the
same shape and the same narrow return contract. Haiku 4.5 is the
right tier for it in both cases. The judgment step that follows —
Hersteller/Community/Divergence — is what picks up the domain weight,
and that step is already on Opus by default. Lifting the grounding
subagent to Opus in niche domains would double-count the upgrade and
waste exactly the token budget this split was designed to free.

**T1's close — the steering primer, once.** The final paragraph of T1
explains in prose how the user steers, because they will need the
vocabulary over the next six turns and this is the only place it gets
introduced. Something like:

> *Gleich spricht der Kartograph, dann die anderen vier, dann das
> Urteil. Du kannst jederzeit dazwischen rufen: "weiter" für den
> nächsten, "widersprich [Rolle]" wenn dir ein Punkt nicht passt,
> "vertiefe [Punkt]" für einen zusätzlichen Takt, "abzweig" für einen
> Neustart mit anderer Prämisse, "stopp" wenn es reicht. Zwischenrufe
> lese ich großzügig.*

After T1 this primer is never repeated. Not as a reminder, not as a
shortened list, not inside any turn's closing line. One introduction,
then the user is trusted to remember.

---

## T2–T6 — the five roles

**Before T2 — the niche-domain probe (Chairman, Opus).** Immediately
before the Cartographer speaks, the Chairman runs one internal check,
not rendered in visible output: *"Does this decision fall into a field
where expert knowledge from a narrow community carries the answer —
medicine, law, regulated standards, rare technical niches?"* The probe
is one sentence, one judgment, one token investment. If the answer is
**yes**, Cartographer, Analyst, and Operator are lifted from Sonnet to
Opus for this run — the standard Sonnet tier assumes the structural
slots do not need the deepest model, but in a niche domain the
difference between Sonnet and Opus is the difference between a map that
looks coherent and a map that is actually correct against a body of
domain knowledge only a handful of practitioners hold. Adversary, Scout,
and Verdict are already Opus (see *Model routing*) and stay there. If
the answer is **no**, the standard routing from the table applies and
T2 proceeds on Sonnet. The probe is asymmetric on purpose: the cost of
a wrong *no* is a silent quality regression the user has no way to see;
the cost of a wrong *yes* is a modest extra token bill on one run.

The probe lifts only the three structural role slots. It does *not*
touch the grounding subagent in T1 — that stays on Haiku 4.5 in every
run, regardless of domain (see *T1 — Read-back and Grounding, combined*
for why). The domain-weight in grounding is carried by the judgment
step, which is already on Opus; the subagent's mechanical read-and-
compress task is domain-independent.

Each role holds exactly one MECE axis. Read `references/roles.md` for
the method, deliverable, and failure modes of each role before speaking
as that role. The short form:

- **Cartographer** (T2, internal-dynamic): dependency map. Names
  load-bearing nodes vs incidental ones. May propose a scope-cut if the
  question is too large for one Council run. No cross-reference
  obligation (no prior role yet).
- **Analyst** (T3, internal-static): derivation validity. Logical
  consistency, definitional consistency, completeness of the argument
  as written. Engages with the Cartographer's map by name.
- **Adversary** (T4, external-dynamic): what active force, actor, or
  dynamic in the environment breaks this? Specific failure vectors,
  not generic "it could fail". Engages with a prior role by name.
- **Scout** (T5, external-static): what standing fact about the world
  would change the conclusion if surfaced? Existing solutions, prior
  decisions, regulatory constraints, technical standards already settled.
  Not active threats — that is the Adversary's axis. Engages with a
  prior role by name.
- **Operator** (T6, operational): concrete next step, follow-up
  obligations, stop/rollback conditions. Verbs and references, not
  principles. Takes the other four role outputs as given. Engages
  with at least one prior role by name.

Role-level abstention is legitimate and preferred over vague output:
*"Not judgeable because <specific missing input>. Resolvable by <concrete
action>."* A role that under-produces (platitude, skim, dodge) is re-run
as one deepen-turn by the Chairman with the specific gap named —
CHAIRMAN-VETO, once per role, not twice.

---

## T7 — Verdict, adaptive to the question

The Verdict is the Chairman's turn. The Chairman is not a sixth role;
it is the synthesis layer.

A Council verdict matches the complexity of what it is judging.

- **Narrow question, converging roles** → one paragraph of prose that
  names the recommendation, weaves in the key role findings by natural
  reference (*"Wie der Adversary gezeigt hat, …"* — not a bulleted
  citations list).
- **Broad question, real tension between technical and management
  framing** → two paragraphs. One operative/technical, with file-level
  or named-action specificity. One for decision-makers, with risk and
  one first step in plain language. Both are prose.
- **Roles could not converge** → a paragraph that names the remaining
  uncertainty, the roles that abstained, and what would need to become
  true for the Council to be sure. *"3/5 roles converge, 2/5
  inconclusive"* is a status report, not a verdict. A real verdict
  names the inconclusive roles and what would resolve each.

Every Verdict closes with concrete next moves — a short numbered
list, two to five imperative steps, each naming the specific
artifact, command, or file. The plan is not optional: the point of a
Council run is that the user leaves with an answer *and* with the
first moves clear. A narrow question gets two or three steps; a
broad one up to five. If the roles could not converge, the plan is
the smallest step that would produce the missing information
(*"48-h-Spike auf X, dann öffnen wir den Council neu mit Zahlen"*).
No bullets of advice or options — the plan is what happens next, in
order.

**Never label the two parts of the Verdict.** No "Antwort:" / "Plan:"
headings, no "Umsetzbarer Plan" sub-header, no "TL;DR:" line. The
answer flows into the plan the way a conversation does: a paragraph
(or two, if the question is broad) that lands on the recommendation,
then a numbered list. The reader recognises what's what from the
form, not from a label. Label-headings in a Verdict sound like a
memo template and break the advisor register the rest of the skill
is built around.

**Tone inside the Verdict.** Prose, not bullet-stacks. Allow the
sentences to breathe — a recommendation that lands well is not the
same as a recommendation crammed into the fewest possible words. The
Turn-length-discipline's 30 % rule applies to the advisor turns
(T1-T6), *not* to T7; the Verdict is the product, and it is allowed
to take the space the decision requires. Conversational register,
contractions where they would fall naturally, one or two connecting
phrases between thoughts rather than period-period-period. If the
draft reads cramped, the recommendation itself will read cramped —
rewrite.

What the Verdict does *not* contain:

- A restated Grounding block (already in T1; don't repeat).
- A bulleted Citations section (weave quotes into the prose by natural
  reference).
- A MECE-Prüfung checklist as a visible block. The Chairman still runs
  the MECE check internally — grounding complete? five dimensions
  covered? overlap? unjudgeable dimensions? cross-reference integrity? —
  but only surfaces a gap if one exists, as a sentence: *"Scout hat
  [X] als Lücke benannt; kein Operator-Schritt schließt sie.
  Empfehlung steht unter Vorbehalt von [Y]."* A clean run has no
  visible MECE section because there is nothing to report.
- New findings under the Chairman's own voice. If the Chairman notices
  something none of the roles caught, that is a signal a role
  under-produced — the Chairman invokes a single deepen-turn on the
  relevant role instead.

Persistence is a single line at the end of T7 in environments with file
access: *"Verdict written to COUNCIL.md in <path>."* In chat-only
environments, skip the persistence line.

Stop the Verdict only when sure, or when you can explicitly state what
would need to become true for the Council to be sure. Never stop at
"reicht", "sufficient", "acceptable risk" — name the uncertainty or
resolve it.

---

## Steering vocabulary — reference for the skill, not for every turn

The vocabulary below is what the skill recognizes from the user.
It is introduced to the user exactly once, in prose, at the end of
T1 (see *T1 — Read-back and Grounding*). After that, it never
appears in output again — not as a reminder, not as a shortened
list in an em-dash line, not as a bullet under a turn. The section
below is documentation *for the skill about how to parse input*,
not a template for what the skill renders.

- **weiter / ok / go / next** — run the next turn.
- **widersprich <rolle> <gegenargument>** — rerun that role with the
  counter as additional input (legal after the role's turn has run).
- **vertiefe <punkt>** — insert a deepen-turn on the named point.
- **abzweig <neue prämisse> / branch** — restart from T1 with the new
  premise established.
- **stopp / abbruch** — end cleanly.

Interpret free-text charitably. "Mach mal weiter" → next. "Der Adversary
übertreibt, aber …" → rebuttal. "Was wäre mit Ansatz B?" → branch. Do
*not* announce the interpretation ("Interpretation: 'ewiter' → 'weiter'
→ NEXT") as its own paragraph — act on the charitable reading, and if
the next turn's opening sentence happens to clarify what was run, that's
enough. The old version's meta-announcements were pure noise.

---

## Persistence — COUNCIL.md

With filesystem access (Claude Code, or Cowork with a selected folder),
append the Verdict to `COUNCIL.md` at the working-directory root after
T7. One entry per run, concise:

```markdown
## <YYYY-MM-DD> — <short question restatement>

**Grounding:** <Hersteller one-liner> · <Community one-liner> · <Divergence>

**Key findings:**
- Cartographer: <one-liner>
- Analyst: <one-liner>
- Adversary: <one-liner>
- Scout: <one-liner>
- Operator: <one-liner>

**Verdict:** <2-3 sentences>

**First step:** <one-liner>
```

When `COUNCIL.md` already exists, read it first in T1 so the Cartographer
can skip already-mapped dependencies and the Chairman can cite prior
verdicts in T7 when relevant. This is the persistence-payoff that makes
follow-up runs structurally cheaper than first runs.

**Read-rule — visible output stays one-line per prior verdict.** T1
reads the existing `COUNCIL.md` from disk, but the visible output never
quotes prior verdicts in full. Each relevant prior verdict is
acknowledged in one line only — date, two- to four-word question
restatement, the operative recommendation as a single clause:
*"Verdict 2026-04-21: Council-Architektur konditional, Caching-Messung
vor Bauen."* The full verdict text remains on disk, not in the chat
context. This protects the run's token budget, which on a long Council
day fills quickly with prior-run material the live deliberation does
not need verbatim. The Cartographer (T2) and any later role that
genuinely needs the full text of a prior verdict reads it on demand
from `COUNCIL.md` via the file system, not by scrolling back through
the chat. The principle is: the chat is the *live* substrate, the file
is the *persistent* substrate; turning the file's content back into
chat content collapses that distinction and inflates every subsequent
turn.

Skip persistence in chat-only environments — there is no file system
surface. Never promise a COUNCIL.md write you cannot perform.

---

## Persistence — GROUNDING-CACHE.md

COUNCIL.md captures verdicts. GROUNDING-CACHE.md captures the *grounding
substrate* itself — the Hersteller source, Community position, and
Divergence that T1 establishes before any role speaks. Verdicts and
grounding persist separately because they decay on different clocks and
serve different readers. A verdict is a decision a user committed to on
a specific day; a grounding block is a reusable fact about the world
that typically stays valid for weeks or months.

With filesystem access (Claude Code, or Cowork with a selected folder),
T1 reads `GROUNDING-CACHE.md` at the working-directory root *before*
issuing any WebSearch. If an entry exists whose topic-slug matches the
current question and whose timestamp is fresh enough (see TTL below),
T1 uses that cached block in place of a new search. If no match or the
match is stale, T1 runs the Haiku grounding subagent as normal, then
appends the result to `GROUNDING-CACHE.md`:

```markdown
## <YYYY-MM-DD> — <topic-slug>

**Hersteller:** <source, year/version, one-line position>
**Community:** <source(s), one-line position>
**Divergence:** <one sentence, or "Aligned on X.">

**Source hits (for audit):**
- <title> — <URL> — <position-sentence>
- <title> — <URL> — <position-sentence>
```

**TTL rule.** Entries are considered fresh for 30 days for Hersteller-
anchored topics (standards, manufacturer docs, regulatory text) and for
7 days for Community-anchored topics (production blog posts, model-
version-specific practitioner consensus). If unclear which anchor
dominates, use 7 days. An entry past its TTL is still read — the
Hersteller source and URL are often still valid — but the Community
position and Divergence are re-fetched. This is a partial refresh, not
a blind discard, because the source list itself is usually stable even
when the interpretation moves.

**Topic-slug matching.** The slug is the normalized form of the
substantive noun phrase in the user's question — not the full question.
*"Soll ich TIMESTAMPTZ oder TIMESTAMP nehmen?"* → slug `timestamptz-vs-
timestamp`. *"Wie reduziere ich Token-Kosten im Council?"* → slug
`council-token-cost-reduction`. Matching is substring-based on the slug,
not fuzzy — if a new question doesn't match an existing slug cleanly,
treat it as a new topic. The cost of a false miss (one redundant search)
is far lower than the cost of a false hit (stale grounding applied to a
different question).

**Read-rule — the cache is read, the payoff is shown minimally.** When a
cache hit occurs, T1's visible grounding block still names Hersteller,
Community, and Divergence in one sentence each — the same shape as a
fresh search. What the user does *not* see is the full JSON hit list
from the subagent, because that already exists in the cache file and
does not need to be re-rendered into chat context. The grounding block
closes with one sentence signaling the cache hit: *"Grounding aus
GROUNDING-CACHE.md vom 2026-04-14, unverändert gültig."* This preserves
the user's ability to verify the substrate without inflating the turn.

**Why this is separate from Model Routing and COUNCIL.md.** Model
Routing cuts the *per-token* cost of a grounding run by assigning Haiku
to the search step. GROUNDING-CACHE.md cuts the *frequency* of grounding
runs — a cached hit avoids the search entirely. The two hebel compose
multiplicatively: Haiku on fresh searches, no search at all on cache
hits. COUNCIL.md is a different mechanism entirely (verdict persistence
for the Cartographer), and the two cache files live side by side
without interaction. A Council run reads both at T1 and writes to both
at T7 when appropriate.

Skip GROUNDING-CACHE.md in chat-only environments, same rule as
COUNCIL.md. In web environments the user carries the grounding block
themselves between sessions, same as the web verdict fallback.

---

## Token economy — which hebel lives where

A question that recurs often enough to deserve its own section: *"where
do I actually push to reduce the cost of a Council run?"* The hebel are
in three places, and conflating them produces double work or missed
savings. The skill itself implements three of them; two live on the
surrounding infrastructure and need to be configured once per
environment, not per run.

**Inside this skill (already implemented).** Model Routing assigns each
turn-slot to the cheapest tier that still carries the work — Haiku for
the grounding search, Sonnet for structural turns (Cartographer,
Analyst, Operator, T1 Read-back), Opus for the turns with no corrective
downstream (Adversary, Scout, Verdict, grounding classification). The
compressed-verdict-turn scope logic cuts a sharp question from seven
turns to one, roughly a 5-7x reduction on the whole run. Persistence —
COUNCIL.md for verdicts, GROUNDING-CACHE.md for the substrate — lets
follow-up runs skip work the previous run already did. These three are
load-bearing and live in the skill; no environment configuration
changes them.

**On the Anthropic API / plugin-configuration layer (requires setup).**
Prompt Caching places a cache breakpoint on the stable prefix (systems
prompt + SKILL.md + `_shared` files + `references/roles.md`), so the
prefix is read at 10% of the base input price from turn 2 onward.
Cache writes cost 1.25x (5-minute TTL) or 2x (1-hour TTL). Extended
cache is the right choice for Council runs with user-interaction
pauses between turns, because the 5-minute default silently breaks
when the user steps away. Context Editing automatically clears
older tool results (the WebSearch hits from T1 are the main target)
from the context window after a configurable number of turns,
cutting the linear-accumulation cost the Cartographer flagged as
load-bearing. Neither of these is a skill-logic change — they are
API or plugin-configuration toggles that the skill itself cannot
set. When running Council outside a fully Anthropic-managed
environment, verify both are enabled before accepting baseline cost
numbers.

**On the environment layer (mostly out of reach).** Whether Cowork or
Claude Code applies per-turn model selection, whether the system
prompt it constructs qualifies for caching, and whether Context
Editing is surfaced to the running skill — these are decided by the
host, not by the skill. In Cowork specifically, per-turn model
selection is not exposed to the skill as of this writing; Model
Routing inside this skill falls back to the single-model default
the session is running on, which is why the routing table is
documented as *intent* rather than *guarantee*. If the host later
exposes per-turn model selection, the routing table activates
without further change.

**What this means in practice.** If a Council run feels expensive,
check the three layers in order: (1) is the question sharp enough
to trigger the compressed-verdict turn and you missed the trigger?
(2) is Prompt Caching with extended TTL actually active in the
current environment? (3) is GROUNDING-CACHE.md being read at T1
and not duplicating prior searches? The first is a skill-logic
question, the second is an infrastructure question, the third is
a persistence question — and they cost roughly in that order of
magnitude to fix, with the skill-logic fix being by far the
biggest lever.

---

## Turn length discipline — the 30 % rule

Every turn before the Verdict (T1 through T6, including T1 grounding
and any rerun or deepen-turn) must be as short as it can be without
losing information or voice. As a concrete budget: aim for a 30 %
reduction in tokens against what would feel "comfortable" to write.

What to cut:

- Scene-setting sentences that restate what the user already said.
- Hedges that repeat themselves (*"es kommt darauf an, im Prinzip,
  grundsätzlich"* stacked in one sentence).
- Transitional paragraphs whose only job is to announce the next
  paragraph.
- Re-statements of the grounding when the role is not grounding.
- Soft-opener phrases (*"Das ist eine interessante Frage …"*) and
  soft-closer phrases (*"Soweit mein Gedanke."*).
- Parenthetical asides that restate the main clause in other words.

What **not** to cut:

- The role's identifying first sentence (*"Als Analyst …"*).
- The specific evidence, number, file-name, or constraint that the
  role is contributing.
- A cross-reference to a prior role when it is load-bearing.
- The Hersteller / Community / Divergenz block in T1.
- The steering primer in T1's close.
- Anything in the Verdict. T7 expands if needed — T7 is where the
  user actually takes the answer home, and is allowed to be as long
  as the decision requires.

The rule applies to the advisor turns because they are conversational
scaffolding. It does not apply to T7, which is the product.

If a turn feels thin after cutting, the role probably did not have
enough to contribute — that is a signal to collapse the turn into a
shorter, denser statement, not to re-inflate it. A role that has
genuinely little to add should say so in one or two sentences and
yield.

---

## Anti-patterns — read before publishing any turn

- **Two turns in one assistant message.** Destroys the seam. Even if
  the user's prompt reads like "do everything", split.
- **Turn header with position counter** — `## Cartographer · 2/7`,
  `## Analyst · 3/7`, etc. The role identifies itself inside the
  first sentence of its prose. A heading above that sentence is
  redundant structure that makes the council sound like a process
  instead of a group of advisors.
- **Steering-menu under any turn except T1's close.** The em-dash
  sentinel *"— Cartographer fertig. Weiter: Analyst · oder widersprich
  · vertiefe · stopp"* under each turn is exactly the protocol
  register this skill was built to avoid. The vocabulary is
  introduced once, in prose, at the end of T1; after that, every
  re-appearance is a register break. The turn ends where the
  advisor's thought ends.
- **Seven turns for a clearly narrow question.** When the question
  arrives sharp and the read-back has nothing substantive to reflect
  back, the right shape is one compressed verdict turn (see *Scope
  — the compressed verdict turn*). Ritualising a one-dimensional
  decision is a failure of scope judgment, not depth of deliberation.
- **Labeled ceremony blocks** — `**Thesis (one sentence):**`,
  `**Finding (hardest-first):**`, `**Cross-reference (Pflicht):**`,
  `**Dissent (Pflicht):**`, `**Resolvable?**`, or a block sentinel
  `=== TURN N/K COMPLETE ===`. The disciplines stay; the labels were
  interrupting reading without enforcing anything. Write prose.
- **Grounding asserted, not performed.** When web access is available,
  T1 must contain visible tool calls. Narrated "I searched for X and
  found Y" without the call in the transcript is a contract violation.
- **Grounding slot left blank or one-sided.** Either a named source
  or an explicit abstention — silence in the Hersteller or Community
  slot breaks GROUND-FIRST.
- **Meta-announcement of interpretation.** "Interpretation: 'ewiter' →
  'weiter' → NEXT. Korrigiere bitte, falls nicht gemeint." Act on the
  charitable reading. If misread, the user will correct.
- **Mode / context announcement in T1.** "Modus: CODE-MODE · Tiefe:
  FULL · Kosten ~60k Tokens." Hide the internals. The skill behaves;
  it does not explain itself.
- **A verdict that matches a template rather than the question.** A
  narrow question gets a paragraph. A broad one gets two. An
  inconclusive one names the gap.
- **A verdict citations block.** Weave the role references into prose
  by natural sentence reference, not a bulleted list.
- **A verdict that introduces new findings under the Chairman's own
  voice.** Insert a deepen-turn on the role that under-produced instead.
- **"Reicht" / "sufficient" / "acceptable risk" as a terminator.**
  Name the uncertainty or resolve it.

---

## Stopping criteria

Silent stop is forbidden. Every run terminates in one of three ways:

1. **Chairman issues a recommendation with one first step in T7.**
2. **Chairman explicitly abstains** — naming each unjudgeable dimension,
   what input would resolve it, and the consequence of leaving it
   unresolved. Partial convergence without resolution paths is an
   incomplete verdict, not an abstention.
3. **User triggers stopp/abbruch** at any turn boundary.

---

## Procedure with file access (Claude Code & Cowork)

The structural rules above are identical across environments with file
access. The only thing that changes is where persistence lands.

**Claude Code.** Full Bash + filesystem. T1 grounding uses `WebSearch` /
`WebFetch` freely. Persistence writes to `./COUNCIL.md` at the working-
directory root.

**Cowork.** Same as Claude Code, but if no folder is selected yet,
call `mcp__cowork__request_cowork_directory` during T1 so persistence
has somewhere to land. Persistence writes to the selected folder's
root as `COUNCIL.md`.

In both environments, read `COUNCIL.md` during T1 if it already exists
— this is the persistence payoff that makes follow-up runs structurally
cheaper than first runs. Append the Verdict (see the `## Persistence`
section above for the entry schema) at the end of T7.

## Procedure in Claude AI (Web)

The web environment has no filesystem and no Bash. The seven-turn shape,
the five MECE roles, the Grounding discipline, and the adaptive Verdict
all still apply — only the grounding and persistence mechanics differ.

**Grounding.** Use web search if it is available in the session;
otherwise open T1 with *"Web access unavailable — working from trained
knowledge up to <date>"* and proceed. Do not narrate searches that did
not happen.

**Persistence.** There is no `COUNCIL.md` to write. Offer the Verdict
as a downloadable markdown artifact at the end of T7, formatted using
the schema from the `## Persistence` section, and add a one-line
instruction to the user: *"paste this back in at the start of the next
Council run so the Cartographer can skip already-mapped dependencies
and the Chairman can cite prior verdicts."* This is the web fallback
for the persistence payoff — the user carries the state themselves
between sessions.

**Steering.** The steering vocabulary (`weiter`, `widersprich`,
`vertiefe`, `abzweig`, `stopp`) and the turn-gating discipline are
identical to file-access environments. Never collapse two turns into
one message because the web feels "lighter" — the seam is what lets
the user steer, and that is environment-independent.

---

## Additional references

- `references/roles.md` — method, deliverable, failure modes, and
  abstention triggers for each of the five roles. Read this whenever
  you're about to speak as a role and want to pressure-check your own
  output before posting.
