# Changelog

All notable changes to the NeoMINT Toolkit are documented here.
The most recent change is always at the top.

Format: `major.minor.fix`
- **major** — incremented only on explicit user instruction
- **minor** — incremented only on explicit user instruction
- **fix** — incremented automatically for every change

---

## 0.5.10 — 2026-04-22

New explicit-invocation governance skill `update-plugin` added alongside
`neomint-plugin-entwicklung`. The new skill generalises the governance
contract so it applies to any Claude plugin (not just this toolkit) and
is bound to the `/update-plugin` slash command via
`plugin/commands/update-plugin.md`; in Claude AI (Web) where slash
commands are unavailable, its pushy description triggers the same
contract. The old `neomint-plugin-entwicklung` skill stays in place for
this release so existing references (CI workflow, internal tooling,
prior CHANGELOG entries) keep working — it is marked for removal in a
later release once the migration is complete.

- `plugin/skills/update-plugin/` — SKILL.md, scripts/grade.py,
  scripts/plugin-check.py, references/plugin-eval.md, evals/evals.json.
  Contract covers pre-research, skill-creator workflow, three-layer
  iteration loop, repackaging, and self-optimisation — the same five
  mechanics the NeoMINT-specific predecessor enforces, phrased for a
  generic plugin. `disable-model-invocation: true` in the frontmatter
  prevents auto-triggering so the user remains in charge of when it
  fires.
- `plugin/commands/update-plugin.md` — slash-command entry that
  delegates to the skill's contract inline.
- `plugin/README.md` — new section under *What's inside* for
  `update-plugin`, positioning it as the generalised successor and
  naming `neomint-plugin-entwicklung` as kept-for-transition.
- **Structural fixes before shipping:** the skill-creator workspace
  that produced `update-plugin` (`iteration-1/`, `skill-snapshot/`,
  benchmark data) had been placed at `plugin/skills/update-plugin-
  workspace/` — a non-skill directory inside the skills tree, which
  Layer 1's "SKILL.md exists per skill" assertion correctly rejected.
  The workspace has been moved to `iteration-workspace/update-plugin/`
  at the repo root (gitignored) so the content is preserved but out
  of the plugin tree. The `update-plugin` SKILL.md description was
  also trimmed from 1076 to 990 characters to fit under Anthropic's
  1024-character truncation limit — purely a length fix, no semantic
  change. Both fixes are structural, not content-level; a subsequent
  pass through skill-creator is expected to produce the canonical
  description.
- **.gitignore:** `/eval-*.html` and `/iteration-workspace/` added to
  the runtime-state block, following the same pattern already in place
  for `/council-*.html` and `/skill-creator-*/`.

---

## 0.5.9 — 2026-04-21

Zwei kleine, aber register-kritische Edits am `council` skill nach
User-Feedback: der Verdict wirkte in v0.5.8 "gecrampted" und war
durch explizite Labels wie *Antwort:* / *Umsetzbarer Plan:*
unnötig strukturiert.

- **`council` skill — Verdict-Sektion verbietet explizit
  Ordnungs-Labels.** Keine *Antwort:* / *Plan:* Headings, keine
  *Umsetzbarer Plan*-Sub-Header, kein *TL;DR:*. Der Verdict fließt
  als Prosa in die nummerierte Schritt-Liste; der Leser erkennt
  Antwort und Plan an der Form, nicht an einem Label. Label-
  Headings klingen nach Memo-Template und brechen das Advisor-
  Register.
- **`council` skill — Tone-Hinweis für den Verdict.** Prosa, nicht
  Bullet-Stapel. Sätze dürfen atmen. Die 30 %-Turn-Length-Discipline
  gilt **nicht** für T7: der Verdict ist das Produkt und darf den
  Raum nehmen, den die Entscheidung verlangt. Konversationelles
  Register, Kontraktionen, ein oder zwei verbindende Phrasen
  zwischen Gedanken — statt Punkt-Punkt-Punkt.

---

## 0.5.8 — 2026-04-21

Zwei Edits, direkt aus dem User-Feedback nach dem ersten v0.5.7-Review.

- **`council` skill — T7 Verdict enthält verbindlich einen umsetzbaren
  Plan im Chat.** Die bisherige "ein Fett-Satz als First Step"-Form ist
  durch eine kurze, nummerierte Plan-Liste (zwei bis fünf Schritte,
  imperativ, jeder mit konkretem Artefakt / Befehl / Datei) ersetzt.
  Bei einer schmalen Frage zwei bis drei Schritte, bei einer breiten
  bis zu fünf, bei nicht-konvergenten Rollen der kleinste Schritt, der
  die fehlende Information produziert. Dokumentiert in *T7 — Verdict,
  adaptive to the question*.
- **`council` skill — neue Sektion *Turn length discipline — the 30 %
  rule*.** Jede Turn-Ausgabe vor dem Verdict (T1–T6, inkl. Grounding,
  Rerun, Deepen-Turn) zielt auf 30 % Token-Reduktion gegenüber dem
  "bequemen" Draft. Was zu kürzen ist (Szene-Sätze, Stapel-Hedges,
  Übergangsparagraphen, Soft-Opener, Paraphrasen-Klammern) und was
  **nicht** (Rollen-Identifikation, spezifische Evidenz, Cross-Reference
  wenn tragend, Grounding-Block in T1, Steering-Primer, **Verdict als
  Ganzes**) ist explizit gelistet. Der Verdict darf so lang sein wie
  die Entscheidung verlangt — das Budget gilt nur für das Scaffolding.
- **governance skill (`neomint-plugin-entwicklung`) — neue Sektion
  *Assertion schema — eval_metadata.json* in `references/plugin-eval.md`.**
  Standardisiert die Assertion-Grammatik für Layer-2-Graders und
  skill-creator-Iterations-Metadaten: `type` (regex_absent, regex_all,
  regex_count, regex_any, file_exists), `target`, `rationale`,
  `patterns` / `expected_min` / `expected_max`. Legacy-Aliase
  (`check_type`, `target_file`) werden weiter toleriert. Dadurch wird
  der Grader über alle Skills und Iterations wiederverwendbar, statt
  pro Change ad-hoc gebaut zu werden. (Dies ist der Step-5e-
  Selbst-Optimierungs-Vorschlag aus dem v0.5.7-Review, direkt in den
  Standard integriert.)

---

## 0.5.7 — 2026-04-21

Drei strukturell regressionsfreie Hebel zur Token-Kostenreduktion im
`council` skill, aus dem Council-Verdict vom 2026-04-21 (siehe
`COUNCIL.md`, Eintrag zur minimalen Token-Kosten-Senkung ohne messbare
Qualitäts-Regression).

- **`council` skill — neue Sektion *Persistence — GROUNDING-CACHE.md*.**
  Dokumentiert einen persistenten Grounding-Substrat-Cache im Working-
  Directory mit TTL-Regeln (30 Tage Hersteller-anchored, 7 Tage
  Community-anchored, 1 Tag Fluss-Topics), Topic-Slug-Matching und
  deutlicher Trennung zu `COUNCIL.md` (Entscheidungsgedächtnis) und zur
  Model-Routing-Tabelle (Konfiguration). Schema: `## <date> — <slug>`
  mit Hersteller/Community/Divergenz + Source-Hits.
- **`council` skill — T1 Grounding prüft Cache vor WebSearch.** Im
  Abschnitt *T1 — Read-back and Grounding, combined* ergänzt: vor jeder
  WebSearch erst `GROUNDING-CACHE.md` am Working-Directory-Root prüfen.
  Bei Cache-Hit Rendering im gleichen Hersteller/Community/Divergenz-
  Block, abschließend mit einer Origin-Sentence („Grounding aus
  GROUNDING-CACHE.md vom <datum>, unverändert gültig.") damit Nutzer
  Fresh von Cached unterscheiden können.
- **`council` skill — neue Sektion *Token economy — which hebel lives
  where*.** Dokumentiert in drei Layern, welcher Hebel an welcher
  Stelle wirkt: (a) im Skill selbst (Model Routing bereits implementiert,
  GROUNDING-CACHE neu), (b) auf API/Plugin-Config-Ebene (Prompt Caching
  der Skill-Prefix mit 90 % Reduktion bei Hit; Context Editing / Memory-
  Tool mit 84 % Reduktion in langen Workflows), (c) auf Environment-
  Ebene (Modellwahl-Caveats, wenn ein Caller kleinere Modelle erzwingt).

Verifiziert über sechs Eval-Cases (zwei neue Delta-Tests für Cache-
Miss-Write und Cache-Hit-Reuse, vier Regressionstests für die
bestehende Shape/Voice-Disziplin), jeweils gegen v0.5.6-Baseline. Keine
Shape-Regressionen, Cache-Mechanik in beiden Pfaden End-to-End
funktionsfähig. Skill-Prefix wächst um ~9 %; die Einsparung kommt aus
wiederholten Topic-Anfragen (Cache-Hits überspringen WebSearch
vollständig) und aus Prompt Caching der Skill-Prefix über API-Calls
hinweg.

---

## 0.5.6 — 2026-04-21

Vier Edits am `council` skill, alle aus dem Council-Verdict vom
2026-04-21 (siehe `COUNCIL.md`, Eintrag zur aggressiven Senkung von
Chat-Footprint und Tokenkosten ohne Qualitätsregression) und der
nachgelagerten Operationalisierung in
`COUNCIL-OPTIMIZATION-NEXT-STEPS.md`.

- **`council` skill — Grounding-Subagent (Haiku 4.5) für die WebSearch-
  Mechanik in T1.** Im Abschnitt *T1 — Read-back and Grounding,
  combined* dokumentiert, dass der mechanische Teil der Grounding-Suche
  (WebSearch ausführen, Treffer in Titel/URL/Kernsatz komprimieren) in
  einem Haiku-4.5-Subagent läuft, während die Einordnung in
  Hersteller/Community/Divergenz im Opus-Haupt-Agent bleibt. Der
  Subagent muss ein `model_used`-Feld zurückgeben, damit die Routing-
  Disziplin auditierbar ist und nicht auf freiwilligem Eingeständnis
  ruht. **Konditional aktiv — wird in v0.5.7 entfernt, falls die noch
  ausstehende Caching-Messung (siehe NEXT-STEPS Schritt 1) ergibt, dass
  Anthropic-Workspace-Caching den expliziten Subagent-Pfad überflüssig
  macht.**
- **`council` skill — verbindliche Modellwahl-Tabelle als neuer
  Abschnitt *Model routing*.** Pro Turn-Slot ein Modell-Tier: T1 Read-
  back Sonnet, T1 Grounding-Suche Haiku, T1 Grounding-Einordnung Opus,
  T2 Cartographer/T3 Analyst/T6 Operator Sonnet (strukturell, mit
  Korrektiv danach), T4 Adversary/T5 Scout/T7 Verdict Opus
  (divergentes Denken bzw. Synthese, ohne nachgelagertes Korrektiv).
  Die Begründungs-Spalte ist tragend, nicht dekorativ — sie macht das
  Routing-Prinzip lesbar: Korrektiv vorhanden → Sonnet reicht; kein
  Korrektiv → Opus.
- **`council` skill — Komplexitäts-Probe vor T2 (Niche-Domain-Probe).**
  Eine einzelne interne Chairman-Frage vor dem Cartographer-Turn:
  *"Fällt diese Entscheidung in ein Feld, in dem Expertenwissen einer
  schmalen Community die Antwort trägt — Medizin, Recht, regulierte
  Standards, seltene technische Nischen?"* Bei *ja* werden
  Cartographer, Analyst und Operator für diesen Lauf von Sonnet auf
  Opus gehoben. Asymmetrisches Risiko: Kosten eines falschen *nein* ist
  stille Qualitätsregression, Kosten eines falschen *ja* ist eine
  modeste Token-Mehrausgabe. Die Probe lässt den Grounding-Subagent
  bewusst auf Haiku — die "Nische" ist eine Eigenschaft der
  Fragestellung, nicht der Rechercheausführung; das Domänen-Gewicht
  trägt der Einordnungs-Schritt, der ohnehin schon auf Opus ist.
- **`council` skill — `COUNCIL.md` als Lauf-Entlaster, nicht als
  Chat-Inhalt.** Im Abschnitt *Persistence — COUNCIL.md* die Lese-
  Regel verschärft: T1 liest die Datei wie bisher, *zitiert* aber
  jeden vorherigen Verdict im sichtbaren Output nur noch einzeilig
  (Datum + Zwei-bis-vier-Wort-Frage + operative Empfehlung als ein
  Satz). Der vollständige Verdict-Text bleibt auf Platte; Cartographer
  und nachfolgende Rollen lesen Details bei Bedarf direkt aus der
  Datei, statt sie aus dem Chat-Kontext zu rekonstruieren. Trennt das
  *live*-Substrat (Chat) sauber vom *persistenten* Substrat (Datei)
  und schützt das Token-Budget gegen Vorlauf-Inflation.

---

## 0.5.5 — 2026-04-21

- **`council` skill — externe Sharp-Heuristik ersetzt Selbstbeurteilung
  im Shape-Entscheid.** Der Trigger, ob ein Lauf komprimiert (ein Turn)
  oder sieben-turn läuft, hing in 0.5.4 an einer Selbstbeurteilung des
  Modells nach dem Read-back ("wenn der Read-back nichts Substanzielles
  hinzufügt, komprimiere"). Unter Read-back-Bias findet das Modell
  fast immer Substanz und kippt systematisch zur teuren Sieben-Turn-
  Form — eine self-fulfilling Prüfung, die ein eigener Council-Lauf
  aufgedeckt hat. Die Entscheidung wandert jetzt auf drei *messbare
  Signale an der Eingabe*, geprüft vor jedem Read-back: (1) Frage
  unter 30 Wörter, (2) frei von Hedging-Modalverben (*sollte, könnte,
  vielleicht* / *should, could, might*), (3) zwei oder mehr explizit
  benannte Optionen. Alle drei müssen feuern für den komprimierten
  Shape — sonst Sieben-Turn-Default. Die vier Substanz-Bedingungen aus
  *Scope — the compressed verdict turn* bleiben als nachgelagerte
  Validierung; der Trigger-Entscheid läuft jetzt auf Input-
  Eigenschaften, nicht auf Selbstwahrnehmung.
- **`council` skill — didaktische Voice-Disziplin für alle Rollen und
  das Verdict.** Ein neuer Abschnitt *The voice of an advisor —
  didactic weight* formalisiert, was erfahrene Berater tun: jede
  Aussage trägt *Was, Warum, und die verworfene Alternative mit
  Grund* als fließenden Gedanken — nicht als Aufzählung, nicht als
  Pro/Contra-Block, nicht als separate "Alternativen betrachtet"-
  Sektion. Der Nutzer, der Grundverständnis mitbringt aber Tiefe
  nicht selbst bewerten kann, bekommt damit die Mitdenk-Spur, die
  formal korrekte aber bare Empfehlungen unterschlagen. Die Regel
  gilt für alle fünf Rollen und für das Verdict, in beiden Shapes;
  im komprimierten Shape wird die Disziplin dichter, nicht weicher,
  weil jeder Satz didaktisches Gewicht trägt. Eingeführt nach einem
  echten Eval-Lauf, in dem der alte Output zwar formal alle MECE-
  Achsen abdeckte, sich aber wie "abgehandelt" las statt wie
  "beraten".

---

## 0.5.4 — 2026-04-21

- **`council` skill — advisor-voice register.** Three changes landed
  as a coherent fix, closing a register gap the 0.5.2 streamlining
  did not fully resolve. User feedback after a live run: *"meine
  berater würden niemals so antworten"* — the skill still read like
  a protocol, not like a circle of advisors. Concretely:
  (1) **Turn headers removed.** `## Cartographer · 2/7`,
  `## Analyst · 3/7`, etc. are gone. The role now identifies itself
  inside the first sentence of its prose (*"Als Kartograph schaue
  ich …"*, *"Ich bin der Analyst …"*). A heading above that sentence
  was redundant structure that made the council sound like a process
  instead of a group of people.
  (2) **Steering menu removed from every turn.** The em-dash
  sentinel *"— Cartographer fertig. Weiter: Analyst · oder widersprich
  · vertiefe · stopp"* was posted under every turn as if the user
  forgot the vocabulary every three minutes. Now the steering primer
  appears exactly once, as prose, at the end of T1 — then the user
  is trusted to remember. A turn ends where the advisor's thought
  ends, full stop.
  (3) **Compressed verdict turn added for sharp questions.** New
  `## Scope — the compressed verdict turn` section: when the question
  arrives narrow, context is already on the table, and Hersteller +
  Community align, the skill runs *one* message (brief grounding,
  five MECE angles in prose named by role, verdict sentence, first
  step) instead of seven. Scope reduction is legitimate when the
  rigor is preserved — the core principle says *shrink the question
  but never simplify it*. Seven turns for a one-dimensional decision
  is ceremony, not deliberation. Upward triage (ambiguous question
  → one diagnostic turn) stays unchanged; now there is downward
  triage too.
- **Anti-pattern section extended** with the three new forbidden
  shapes: turn header with position counter, steering-menu under any
  turn except T1's close, seven turns for a clearly narrow question.
  The Layer 2 grader now asserts each of these by name so the 0.5.2
  class of drift — disciplines preserved, register reintroduced —
  can't recur silently.
- **Skill-creator iteration loop ran to closure.** Four evals (sharp
  Postgres question, broad auth-extraction question, mid-run
  steering, ambiguous-diagnostic). 0.5.4 draft scored 27/27 (100%)
  against structural assertions targeting the three changes; 0.5.3
  baseline scored 16/27 (59%) — exactly at the anti-patterns the
  refactor removed. Iteration report and per-run transcripts in
  `skills/council/evals/`.
- **Governance delta.** Layer 2 grader (`scripts/grade.py`) rewritten
  for the new contract: asserts `## The voice of a turn — no header,
  no menu`, the compressed-verdict section, the advisor-voice rule
  (*role identifies itself in the first sentence*), and the three
  new anti-patterns. Assertions that required the old turn-header
  template and em-dash handoff template were inverted — they now
  assert those shapes are *forbidden*, not required.

---

## 0.5.3 — 2026-04-21

- **Agent-binding versioning rule — explicit in both the governance
  skill and the README plugin standard.** The rule `major` and `minor`
  only on explicit user instruction was already documented, but was
  stated in voice-neutral form ("incremented only on explicit user
  instruction") and not sharp enough to prevent an agent from
  unilaterally proposing a minor bump when a refactor felt large.
  Added a binding agent-rule block in both places: an agent may only
  ever bump `fix`; if a change subjectively warrants more, deliver the
  fix bump and *ask* — never the other direction. Semantic judgment
  belongs to the user; mechanical increment belongs to the agent.
  Codified after the agent proposed 0.6.0 for the pending council
  advisor-voice refactor; the user corrected the mistake and anchored
  the rule so it cannot recur.

---

## 0.5.2 — 2026-04-21

- **`council` skill — radical streamlining.** The skill was
  overengineered: labeled ceremony blocks (`**Thesis:**`,
  `**Cross-reference (Pflicht):**`, `**Dissent (Pflicht):**`,
  `**Resolvable?**`), the QUICK/FULL/AUDIT/DIAGNOSTIC mode zoo, and
  sentinel blocks (`=== TURN N/K COMPLETE ===`) made runs hard to
  read and made the skill look more like a form than a
  deliberation. All three were removed. The disciplines they
  enforced — turn-gating, grounding, cross-role engagement, dissent,
  Chairman synthesis, adaptive verdict — remain, now carried by
  prose rather than labels. `SKILL.md` shrank from 721 → ~390 lines;
  four of five reference files (`phases.md`, `turns.md`, `ground.md`,
  `persistence.md`) were consolidated into `SKILL.md` body or
  dropped, leaving only `references/roles.md`. The seven-turn shape
  is now: T1 Read-back + Grounding, T2 Cartographer, T3 Analyst,
  T4 Adversary, T5 Scout, T6 Operator, T7 Verdict. Each turn opens
  with a single header line (`## Cartographer  ·  2/7`) and closes
  with a single em-dash handoff line (`— Cartographer fertig.
  Weiter: Analyst · oder *widersprich* · *vertiefe <punkt>* ·
  *stopp*`). The Verdict is adaptive: narrow question → one
  paragraph; broad question → two paragraphs (operative +
  management); inconclusive → paragraph naming the gap and what
  would resolve it. Core principle ("*Reicht* is not a verdict")
  is preserved verbatim.
- **`commands/council.md` — slimmed from 344 → ~50 lines.** The
  command file now delegates the full contract to `SKILL.md` rather
  than duplicating phase mechanics, sentinel formats, and turn
  micro-formats inline. This ends the double-maintenance burden
  where every ceremony rule had to be edited in both files.
- **`skills/council/evals/evals.json` — rewritten for the new
  contract.** The obsolete `mode_expected` and `context_expected`
  fields were dropped (modes are gone). Four evals retained
  (code-auth-extraction, chat-slo-circuit-breaker, doc-policy-gap-audit,
  ambiguous-diagnostic-turn); each `expected_output` now names the
  streamlined turn shape, the adaptive-verdict regime that fits,
  and the anti-patterns that must not appear.
- **`skills/council/scripts/grade.py` — rewritten as
  discipline-protector rather than ceremony-locker.** The prior
  grader had 33 assertions that locked the old ceremony into the
  contract (sentinel strings, labeled blocks, mode tokens, five
  reference files, `Mode: DIAGNOSTIC` header). All 33 would have
  failed against the streamlined `SKILL.md`, even though the skill
  is strictly better. The new grader protects the load-bearing
  disciplines — five MECE roles with their axis questions, seven-turn
  ordering, one-turn-per-message rule, GROUND-FIRST with its binding
  sentence verbatim, cross-role engagement rule, CHAIRMAN-VETO,
  adaptive Verdict with its three regimes named, "*Reicht* is not
  a verdict" principle, steering vocabulary — and explicitly rejects
  the old ceremony by requiring the anti-pattern section to forbid
  each removed label by name. The old ceremony cannot creep back
  silently.
- **Layer 1 — `commands/` added to `ROOT_WHITELIST`.** The 0.5.0
  release ratified `commands/<name>.md` as the canonical entry
  point for explicit-invocation skills but forgot to update
  `plugin-check.py`'s root whitelist, so every Layer 1 run from
  0.5.0 onward flagged `commands` as a stray folder. Fixed.
- **Layer 1 — ghost-skill filter ignores YAML frontmatter field
  names.** `disable-model-invocation`, `argument-hint`, and
  `allowed-tools` are YAML frontmatter keys that the README
  legitimately quotes when documenting the invocation-model
  standard. The ghost-skill heuristic was matching them as
  suspected skill names (hyphenated, lowercase, > 3 chars). Added
  them to the exclusion set.
- **README — role order corrected in council description.** The
  short description in the "What's inside" section had the first
  two roles inverted ("Analyst, Cartographer, …"), conflicting with
  the canonical T2→T6 order defined in `SKILL.md`, `CHANGELOG.md`,
  and the grader. Restored to "Cartographer, Analyst, Adversary,
  Scout, Operator". Pure WORDING fix, caught by Layer 3.
- **`skills/council/SKILL.md` — canonical heading restored.** The
  references section was titled `## References`, but
  `SKILL_TEMPLATE.md` and the plugin standard specify
  `## Additional references`. Renamed to match. A Layer 1 assertion
  was added to lock this: if a skill has a non-empty `references/`
  directory, the canonical heading must be present and the legacy
  `## References` form must not appear. Caught as a STRUCTURE
  finding by Layer 3 and promoted to Layer 1 per the Step 5c rule.
- **Why this is a patch bump (0.5.1 → 0.5.2), not minor.** The
  council streamlining is large in line count but is strictly a
  refinement: same seven-role MECE backbone, same grounding
  discipline, same turn-gating, same "*Reicht* is not a verdict"
  principle. No new capability, no new skill, no archive-layout
  change. The Layer 1 fixes close real gaps that the standard
  already ratified. Patch is the right call.

---

## 0.5.1 — 2026-04-21

- **`SKILL_TEMPLATE.md` — "Invocation model" decision up front.** The
  template now opens (before Language, before Environment, before any
  procedure) with an explicit auto-trigger vs explicit-invocation
  decision: the rule is "would firing this without asking surprise
  the user?". For *yes*, the template spells out the bidirectional
  pairing contract (`commands/<name>.md` + `disable-model-invocation: true`
  in frontmatter + SKILL.md serves as Web fallback) and notes that
  Layer 1 enforces it. For *no*, nothing special. The frontmatter now
  carries a commented-out `disable-model-invocation: true` line that
  authors uncomment when needed. This change prevents a recurrence of
  the 0.5.0 situation, where `council` had to be refactored from
  auto-trigger to explicit-invocation post-hoc — the decision is now
  surfaced at the start of authoring, not after the first eval loop.
- **Layer 3 audit prompt — STRUCTURE vs WORDING kind split.**
  `skills/neomint-plugin-entwicklung/SKILL.md` now asks the unprimed
  auditor to classify each finding along two orthogonal axes: category
  (a-e, unchanged) *and* kind (STRUCTURE — a contract is violated; or
  WORDING — text is merely inconsistent or unclear). Severity is
  applied after kind, because a pure wording drift is almost never
  HIGH and a structural violation is almost always at least MEDIUM.
  The Step 5c resolution path splits accordingly: STRUCTURE findings
  that Layer 1 missed get fixed AND promoted into a new Layer 1
  assertion; WORDING findings get fixed but do NOT get promoted —
  wording drift would require fuzzy matching to automate, produces
  false positives, and Layer 3 catches it cheaply on the next pass.
  The rationale is documented inline so future iterations of the
  governance skill understand why the split exists.
- **Layer 1 — required Procedure headings promoted to an assertion.**
  The 0.5.1 Layer 3 audit (the first run of the new
  STRUCTURE/WORDING-classified prompt) flagged a real STRUCTURE gap:
  `skills/neomint-plugin-entwicklung/SKILL.md` was silently missing
  both `## Procedure with file access (Claude Code & Cowork)` and
  `## Procedure in Claude AI (Web)` — the two canonical sections the
  standard has required since 0.4.x. Layer 1 was not checking for
  them. Per Step 5c, both were fixed in the governance skill (Steps
  0–5 now live under the canonical `Procedure with file access`
  heading; a dedicated `Procedure in Claude AI (Web)` section defines
  the web fallback) AND promoted into two new Layer 1 assertions in
  `scripts/plugin-check.py`. Six new structural checks (2 per skill
  × 3 skills) now run on every build; the full Layer 1+2 pass count
  is 59/59.
- **Why this is a patch bump (0.5.0 → 0.5.1), not minor.** All three
  changes are refinements to how authoring and auditing are framed
  and enforced — no new capability, no behavioural change to any
  skill at runtime, no archive-layout change. Per the versioning
  scheme, patch is the right call.

---

## 0.5.0 — 2026-04-21

- `council` skill: progressive-disclosure refactor and slash-command
  conversion. Before this change, the Council auto-triggered on any
  decision-language signal and loaded the full `SKILL.md` body (721
  lines) into context the moment it fired. In practice that shape
  invited Claude to also read every file listed under "Additional
  references" — `roles.md`, `phases.md`, `turns.md`, `ground.md`,
  `persistence.md` — roughly another 1200 lines. The result was a
  per-run token floor around 77 KB (~19 k tokens) before any turn had
  executed. The user's observation — "wie reduzieren wir die Token-
  Kosten vom council skill ohne Qualitätsverlust (ZERO REGRESSION) um
  80%? außerdem: der council skill sollte direkt aufgerufen werden und
  nicht automatisch triggern (vielleicht mit slash council?)" —
  identified both defects. This release addresses both.
  - **Primary entry is now `/council`.** The new `commands/council.md`
    file carries the full turn-gated contract inline: sentinel format,
    continuation tokens, the FULL/QUICK/AUDIT turn maps, the five MECE
    roles, the role-turn micro-format, the T2 GROUND requirement for
    visible tool calls, the T8 VERDICT Chairman template, the eight
    rigor duties, the anti-pattern list, and the three stopping
    criteria. A standard run completes without reading a single
    reference file — the command file is self-sufficient by design.
  - **`skills/council/SKILL.md` becomes the explicit web fallback.**
    The frontmatter gains `disable-model-invocation: true`, the
    description is rewritten to name `/council` as the primary entry
    and to bind the skill's auto-triggering pool to explicit
    invocations only ("use the council", "run council"). In Claude AI
    (Web), where slash commands are unavailable, this SKILL.md remains
    the usable entry point and carries enough of the contract inline
    to run a Council without reading references.
  - **References move to on-demand-only.** `references/roles.md`,
    `ground.md`, `phases.md`, `turns.md`, and `persistence.md` ship
    unchanged, but the entry points now explicitly instruct Claude
    NOT to pre-load them — they are read only when a specific turn
    needs detail the entry point does not carry. This is the
    progressive-disclosure pattern Anthropic's `skills/skill-creator`
    documents as a first-class practice.
  - **Token-reduction measurement.** Old per-run load
    (`SKILL.md` + all references eagerly read): 77 004 bytes,
    approximately 19 251 tokens. New per-run load for a standard
    /council invocation (`commands/council.md` alone): 15 920 bytes,
    approximately 3 980 tokens. Empirical reduction: **79.3 %** — on
    target for the user's 80 % goal. ZERO REGRESSION is structurally
    enforced: every contract string the 0.4.9 grader checked (33
    assertions) is either preserved in the new entry points or
    explicitly ported, and the grader is extended to 38 assertions
    covering the new architecture.
  - **Layer-2 grader rewrite (`scripts/grade.py`).** The old grader
    scanned only `SKILL.md`. The new grader scans both
    `commands/council.md` and `SKILL.md`, treating most contract
    strings as "must appear in at least one entry point". Five new
    assertions cover the 0.5.0 shape: `commands/council.md` exists
    and has substance (≥ 2 000 chars); the command file declares
    progressive-disclosure intent ("self-sufficient" / "load on
    demand"); `SKILL.md` frontmatter carries
    `disable-model-invocation: true`; `SKILL.md` points at `/council`
    or `commands/council.md` as the primary entry; the command file
    carries the full GROUND-FIRST binding sentence, not just the
    label. Total: 38 contract checks, all passing.
  - **Why minor bump (0.4.9 → 0.5.0) rather than patch.** The skill
    gains a new entry point (`/council`), its auto-triggering
    behaviour changes, and the reference-loading discipline flips
    from eager to lazy. That is a user-visible behavioural shape
    change, not a bugfix — minor is the honest versioning call and
    the user explicitly approved it ("ok") when the plan was
    presented.
- **Plugin-standard update — `commands/` as an explicit-invocation
  contract.** `commands/` is now named in `ROOT_WHITELIST` and
  documented in both `README.md` and the governance skill's plugin
  structure reference. The wording is deliberately conditional: the
  directory is relevant ONLY for explicit-invocation skills (skills
  the user fires by name rather than have Claude auto-trigger on
  context). For such a skill the pairing is mandatory and
  bidirectional: `commands/<name>.md` carries the full contract
  inline, and its paired `skills/<name>/SKILL.md` must set
  `disable-model-invocation: true` and also serves as the Claude AI
  (Web) fallback. Auto-triggering skills
  (`pdf-umbenennen`, `neomint-plugin-entwicklung`) deliberately have
  no command file and no flag — that is correct, not a deficiency.
- **Layer 3 → Layer 1 promotion — bidirectional pairing assertion.**
  The unprimed audit on this release flagged the command/skill
  pairing as unenforced (Layer 1 had no check for it). Per the
  governance Step 5c protocol — "missed by Layer 1 but real → fix
  it AND add a new Layer 1 assertion" — two new assertions ship in
  `scripts/plugin-check.py`: *"commands/X.md pairs with a non-auto
  skill"* (forward direction: a command without a paired
  non-auto skill would race the skill's auto-trigger) and *"[X]
  disable-model-invocation skill has a paired command"* (reverse
  direction: a non-auto skill without a command would be
  unreachable in Claude Code / Cowork). Both pass on 0.5.0. Total
  Layer 1 + Layer 2 checks: 53, all green.
- **Governance skill — negative scope and explicit-invocation
  guidance.** `skills/neomint-plugin-entwicklung/SKILL.md` gains a
  *do NOT trigger for* clause in its description (general coding,
  work in unrelated plugins, consuming rather than authoring the
  plugin's skills), closing a Layer 3 MEDIUM. Its plugin-structure
  reference now documents when to choose the explicit-invocation
  pairing and when to stay auto-triggering, with the decision rule
  "would firing this without asking surprise the user?".
- **Ghost-skill heuristic refinement (`plugin-check.py`).** Added a
  `KNOWN_FRONTMATTER_FIELDS` exclusion set so YAML field names
  quoted in prose (`disable-model-invocation`, `argument-hint`,
  `allowed-tools`) are no longer misread as candidate ghost skills.

---

## 0.4.9 — 2026-04-21

- Repository restructure: plugin sources moved from the repo root into a
  dedicated `plugin/` subdirectory, and the repository gains its own
  top-level `README.md` distinct from the plugin's. The motivation: the
  repo is both a shipping vehicle for the plugin and a record of the
  governance research that produced it. Those two audiences want
  different entry points. The repo-level README introduces the research
  angle (Ground-Before-Discuss, three-layer iteration loop,
  unprimed-audit workflow) and points at `plugin/` for the shipping
  artefact. The plugin's own README is untouched in substance — it still
  documents install, skills, and plugin standards — but its build
  command now runs from inside `plugin/` instead of from the repo root.
  `LICENSE` and `SECURITY.md` live both at the repo root (for GitHub
  discovery) and inside `plugin/` (so the `.plugin` bundle remains
  Apache-2.0 §4-compliant for redistribution). The CI workflow at
  `.github/workflows/plugin-check.yml` now invokes `plugin-check.py`
  with `plugin` as the explicit root argument; per-skill graders are
  addressed via `plugin/skills/…` paths.

---

## 0.4.8 — 2026-04-21

- `council` skill: turn-gated live deliberation. Previously the Council
  could render the entire five-phase judgment as a single wall-of-text
  assistant message, which made the deliberation impossible to follow
  live, impossible to interrupt at a specific role, and trivial to
  shortcut under token pressure. The user's observation — "der user
  muss die Diskussion live mitverfolgen können … wie einem council
  wirklich zuzuhören" — identified this as the core defect that
  remained after 0.4.7. The fix reshapes the skill around a one-phase-
  per-assistant-message contract:
  - **Turn map.** FULL now runs as eight turns (T1 ORIENT · T2 GROUND ·
    T3 CARTOGRAPHER · T4 ANALYST · T5 ADVERSARY · T6 SCOUT · T7 OPERATOR
    · T8 VERDICT). QUICK compresses to three turns. AUDIT uses FULL as
    a baseline and the Chairman may insert DEEPEN turns on the fly;
    K grows visibly, never silently.
  - **Sentinel contract.** Every phase message ends with exactly
    `=== TURN <N>/<K> COMPLETE — <PHASE NAME> ===` followed by an
    AWAITING-USER line listing the accepted continuation tokens
    (`NEXT`, `REBUTTAL`, `DEEPEN`, `BRANCH`, `ABORT`). The sentinel is
    the hard stop — content after it is a contract violation. This is
    the structural fix to the Claude-Code multi-phase-workflow failure
    mode documented in `anthropics/claude-code` issue #21672.
  - **Role turn micro-format.** Each role turn opens with an Axis
    line, a one-sentence Thesis, a hardest-first Finding, a mandatory
    Cross-reference (from T4 onward: a direct quote from a prior role),
    a mandatory Dissent or reasoned concurrence, and a Resolvable? line.
    The micro-format forces the turns to compound instead of staying
    five parallel essays, and gives the grader structural anchors.
  - **Visible tool calls in GROUND.** T2 requires at least one real
    `WebSearch` / `WebFetch` invocation when web access is available.
    Narrating "I searched for X" without the actual tool call is a
    contract violation — the user must see the grounding was performed,
    not asserted.
  - **Chairman citation rule.** T8 VERDICT now contains a mandatory
    `## Citations` block with a short direct quote from each of T3–T7,
    attributed by turn number. The Chairman adds no new findings under
    its own voice — if a gap is visible, a DEEPEN turn is inserted
    instead. This is how the Chairman visibly *listens* rather than
    summarising.
  - **References.** `references/turns.md` added as the single source of
    truth for the live-turn contract, including exact sentinel format,
    continuation-token semantics, role-turn micro-format, worked FULL
    and QUICK examples, and anti-shortcut enforcement. `references/
    phases.md` rewritten with turn-numbered section headers (T1..T8).
  - **Layer 2 grader.** `skills/council/scripts/grade.py` extended from
    20 to 33 assertions, all enforcing the new contract: turn-gated
    section present, sentinel template exact, continuation tokens
    present, role micro-format markers present, Chairman citation
    block present, turn counts declared (FULL=8, QUICK=3), NO-DOWNGRADE
    for K declared, `turns.md` exists with worked examples and
    references #21672, anti-pattern "two phases in one message" called
    out, turn-header template exact, `references/phases.md` carries
    T1..T8 labels. Two legacy assertions (Persistence line format,
    phase-block ordering) were updated to accept the new turn-numbered
    form without loosening their intent.
  - **Layer 3 finding → Layer 2 assertion (self-optimisation).** The
    first 0.4.8 audit pass returned `HOLD` on one MEDIUM: the 32-
    assertion grader had locked the *phase-numbering convention* in
    `SKILL.md` and `phases.md` but did not scan the other reference
    files. `references/persistence.md` still used "Phase 0" / "Phase 3"
    from the pre-0.4.8 shape in three places, and `references/ground.md`
    had "Phase 1" in its title — both would have decoupled the reference
    corpus from the skill body without any grader firing. Fix was
    twofold: correct the four stale labels, and add assertion #33 — a
    stale-phase scanner that forbids `Phase 0`..`Phase 4` across
    `SKILL.md` and every `references/*.md`, with an escape hatch
    (nearby "old" / "legacy" / "previous" / "pre-0.4.8" prose) for
    intentional historical references. A negative test (injecting
    `Phase 0` into persistence.md with no qualifier) confirms the new
    assertion fires. Total: 33/33 PASS.
  - **Description rewrite.** The YAML folded-scalar description now
    names the live-turn contract explicitly — "delivered turn by turn
    — one phase per message, ending in a sentinel so the user can
    follow and intervene" — so the trigger signals include the
    deliberation shape, not just the role roster. The full phrase
    "turn-gated live deliberation" remains in the body heading at
    line 21. The description has been trimmed to stay under the
    1024-char hard limit (995 chars).
- No changes to `pdf-umbenennen` or `neomint-plugin-entwicklung` in this
  cycle. The governance skill's Step 2 exception does **not** apply here
  — this is a content change of a skill, so `skill-creator` was used for
  the redesign.

---

## 0.4.7 — 2026-04-21

- `SECURITY.md`: security-report contact changed from the placeholder
  `security@neomint.com` to `info@neomint.com`. A short explanatory
  sentence was added so readers understand the general mailbox is the
  monitored destination and that no dedicated security alias exists.
  No other behaviour changes; per the governance skill's Step 2
  exception, this is a pure metadata change and does not require the
  `skill-creator` workflow.

---

## 0.4.6 — 2026-04-21

- Repository-publication layer added so the plugin can ship as the public
  `neomint-research/claude-neomint-plugin` repository on GitHub.
  - New root files: `LICENSE` (Apache 2.0), `SECURITY.md`, `CONTRIBUTING.md`,
    `.gitignore`.
  - New `.github/` scaffolding: `workflows/plugin-check.yml` runs Layer 1
    and every per-skill grader on every PR and push to `main`; PR template
    enforces the governance checklist; three issue templates (bug, skill
    proposal, standard update).
- `README.md` rewritten for GitHub-first reading: install block at the top,
  Open Research positioning, explicit link to `CONTRIBUTING.md`. Plugin
  standards section preserved verbatim — it is the substance.
- Layer 1 (`plugin-check.py`) updated so the new root files don't register
  as stray, and so `.github/` and `CONTRIBUTING.md` are explicitly excluded
  from the shipping archive's allowed top-level set. `LICENSE` and
  `SECURITY.md` DO ship — users of the `.plugin` bundle see the license
  and the security policy without needing the repo.
- No content changes to any skill. `skill-creator` was therefore not
  required for this cycle (repackage-and-publication-only change). The
  governance skill's Step 2 exception applies.
- **Layer 3 finding → Layer 1 assertion.** The first 0.4.6 audit pass
  returned `HOLD`: the documented build commands in `README.md` and
  `CONTRIBUTING.md` excluded `LICENSE` and `SECURITY.md` via `-x`, even
  though the `never_shipped` design requires those files to ship inside
  the `.plugin` bundle. Layer 1's archive-cleanliness check only
  catches *extra* content, not *missing* content, so it would have
  false-PASSed. Fix was twofold: correct both build commands, and add
  two new Layer 1 assertions per documentation file — "build cmd does
  not exclude shipped root files" and "build cmd excludes every
  never-shipped root file" — using `fnmatch` so zip globs like
  `*.git*` match `.gitignore` correctly. A negative test confirms the
  new assertions fire on the exact defect pattern. Layer 1 now totals
  51 checks (up from 47); post-fix: 51/51 PASS.
- CI workflow (`.github/workflows/plugin-check.yml`) tightened: the
  `if: always()` flag was removed from Layer 2 grader steps so the
  pipeline fails fast on Layer 1 failure rather than reporting mixed
  signals. Comment added explaining the design choice.
- `CONTRIBUTING.md` license clause clarified: "submitting" is defined
  as PR, patch on an issue, or code posted in a discussion; inbound-
  equals-outbound Apache 2.0 explicitly named.
- **Canonical archive rule tightened.** While preparing the repo for
  publication, a stray `test-neomint-toolkit.plugin` from an earlier
  session was found at the plugin root. The old "No stray files at
  plugin root" rule tolerated *any* file ending in `.plugin`, and the
  "Shipping archive contents are clean" rule picked `plugins[-1]`
  alphabetically — so with two archives present, the wrong one was
  being validated. Now: only `<plugin-name>.plugin` (read from
  `plugin.json`) is permitted at the root, and the archive-cleanliness
  check targets that canonical name specifically. Negative test
  confirms the tightened rule catches the stray-archive case.

---

## 0.4.5 — 2026-04-21

- Three self-optimisation upgrades from the 0.4.4 cycle, each addressing a manual call that should have been a standard.
- **Ground-Before-Discuss** named as a plugin-wide standard in README. Both the governance skill's Step 0 pre-research (Anthropic GitHub first, Community second) and the council skill's new Phase 1 GROUND (Hersteller first, Community second) already follow this shape; the README now names the shared principle so the parallel is visible and future skills inherit it. Silent omission of either source is a contract violation; if a source doesn't exist or isn't reachable, the absence is stated as a finding.
- **Layer 1 validates the shipping archive.** `plugin-check.py` gains a new assertion *Shipping archive contents are clean* that opens the `*.plugin` at the plugin root and verifies its top-level entries are a subset of the root whitelist. Catches the 0.4.4 failure automatically — zipping from the wrong directory, snapshot folders leaking into the archive, stray build trees. Skipped when no `.plugin` exists at the root.
- **Step 4 of the governance skill gains an explicit warning block** about zipping from a clean source copy rather than from `/tmp` itself, including the concrete failure mode: `cd /tmp && zip -r ….plugin .` silently packs every sibling folder in `/tmp` into the archive. The warning references today's Layer 1 assertion as the safety net — but the discipline is to get it right the first time. Also names the `zip -r` append-to-existing-archive trap (delete the target `.plugin` before running zip).
- Layer 1 + Layer 2 dogfood on this release: 47 PASS, 0 FAIL, 0 SKIP (one more assertion than 0.4.4's 46 — the new archive-contents check).

## 0.4.4 — 2026-04-21

- Council skill gains a mandatory **GROUND** phase between ORIENT and MAP. The user's principle: "Der erste Schritt muss immer sein: Was sagt der Hersteller. Der zweite: Was sagt die Community. Erst das wird diskutiert." Before any of the five roles speaks, two sources must be on the table — the authoritative / first-party position (Hersteller: vendor docs, RFC, ISO, primary law, repo's own ADR) and the practitioner consensus (Community: Stack Overflow, forums, maintainer blogs, peer analyses). Divergence between the two is a first-class finding, not a footnote.
- Phase count grows 4 → 5: **ORIENT → GROUND → MAP → COUNCIL → VERDICT**. MAP's input now includes the GROUND block; the four judging roles each see it in their starting context; the Chairman's MECE check now gates on grounding completeness before publication.
- New reference `skills/council/references/ground.md` — what counts as a Hersteller source by question type (vendor docs / RFC / primary law / guideline body / repo ADR), what counts as a Community source (practitioner forums, issue trackers, peer analyses, the repo's own commit history), how to handle divergence (three named patterns: Hersteller-conservative/Community-pragmatic, Hersteller-current/Community-stale, Hersteller-silent/Community-de-facto-standard), depth scaling per QUICK/FULL/AUDIT, and the handoff format to the Cartographer. Keeps SKILL.md under the 500-line ideal via progressive disclosure.
- New rigor duty **GROUND-FIRST** in SKILL.md — named and binding. "No role speaks before both the Hersteller position and the Community position are on the table." Covers both fallbacks: no Hersteller exists (novel / subjective / cross-domain question) → named as such, not skipped; Community unreachable (no web access) → fall back to trained knowledge with cutoff, stated. Silent omission of either source is a contract violation.
- Output template gains a `## Grounding` block with three lines (Manufacturer / Community / Divergence) placed *before* the role findings — a verdict whose grounding slot is empty is structurally an opinion, not a Council finding. Anti-patterns updated accordingly, including a new entry for ungrounded Councils.
- Iteration handles (REBUTTAL / DEEPEN / BRANCH) extended: REBUTTAL citing a new Hersteller or Community source triggers a re-entry to Phase 1 before the role re-runs; DEEPEN can now target a specific grounding question, not only a role or point.
- `skills/council/scripts/grade.py` grows 13 → 17 contract checks: new phase list includes `ground`, `references/ground.md` must exist on disk, both `Hersteller` and `Community` must appear in SKILL.md, `GROUND-FIRST` rigor duty must be named, `## Grounding` + `Manufacturer (Hersteller)` must appear in the output template, and a structural ordering check enforces `ORIENT → GROUND → MAP → COUNCIL → VERDICT` — GROUND cannot silently drift to become an appendix.
- No changes to `plugin-check.py` required — the Layer 1 char-limit assertion added in 0.4.3 covers the slightly longer SKILL.md by default, and the new reference file is picked up automatically by the existing `references/X.md` resolver.

## 0.4.3 — 2026-04-21

- Root cause of the user-reported "council is not recognised when I ask about the plugin" regression traced to the council skill description in 0.4.0–0.4.2: at 1382 characters it sat well over Anthropic's 1024-char hard truncation limit, so Claude only ever saw a clipped fragment. The failure was silent — nothing in Layer 1 flagged it.
- Council description rewritten via the skill-creator description-optimisation loop. `claude -p` was not authenticated inside the sandbox, so the iteration loop was rebuilt manually: 5 new candidate descriptions generated in parallel via subagents, then each graded by a fresh subagent playing Claude's skill-selection mechanism across the 20-query eval set (12 train / 8 test), 3 independent judgments per query. All 5 new candidates saturated at 20/20; the winner was chosen on principled tiebreakers — imperative user-intent framing, distinctive opener ("You're too close to it.") matching the skill's soul, trigger-word density across decision/validation/risk/completeness/strategic phrasings, and headroom under the char limit. Final description: 883 characters. Eval candidates, eval set, and grading results preserved under `/sessions/clever-kind-mayer/council-desc-opt/`.
- New standing principle encoded into the council SKILL.md body: **"Reicht" ist niemals akzeptabel** — a Council verdict never stops at "sufficient" or "acceptable risk" without naming the uncertainty. Stop only when sure, or explicitly name *what would need to become true* for the Council to be sure. "3/5 roles converge, 2/5 inconclusive" is a status report, not a verdict. The principle is written into three load-bearing sections: **Rigor duties** (new VERDICT COMPLETENESS paragraph), **Stopping criteria** (rule #2 strengthened, plus the explicit "Reicht is not a valid terminator" line), and **MECE as active Chairman function** (rule #3 now requires naming the resolution path).
- `skills/council/scripts/grade.py` gains three new contract checks (10 → 13): description rendered length ≤ 1024 chars, the phrases "stop only when sure" and "what would need to become true" present in SKILL.md, and the "3/5 … status report" anti-pattern framing present. These survive future edits — the principle cannot silently decay.
- `skills/neomint-plugin-entwicklung/scripts/plugin-check.py` Layer 1 gains a per-skill assertion: **every** skill's description must fold to ≤ 1024 chars. The 0.4.2 failure mode could have been caught automatically — now it will be.
- Iteration loop this release: Layer 1 + Layer 2 green, plus an independent description regression trace (the silent-truncation bug) resolved. Dogfood count is kept honest by the new Layer 1 char-limit assertion.

## 0.4.2 — 2026-04-21

- Layer 2 of the three-layer iteration loop is now active for every skill. Each skill ships a `scripts/grade.py` contract grader that runs under `plugin-check.py` and returns non-zero on a contract regression:
  - `skills/council/scripts/grade.py` — 10 contract checks: five MECE roles + Chairman named, four phases, three depth modes, three contexts, two-track output, mandatory `Persistence:` line, `Mode: DIAGNOSTIC` header, required sections, references on disk.
  - `skills/pdf-umbenennen/scripts/grade.py` — filename convention, at least three matching examples, umlaut rules, sender short-name categories (Companies/Banks/Persons/Unknown — the categories whose truncation shipped in 0.4.0), subject short-form section, parallel-batch performance contract.
  - `skills/neomint-plugin-entwicklung/scripts/grade.py` — required sections, skill-creator requirement, three layers named, grader script and reference doc bundled, pre-research step, versioning scheme, build-in-`/tmp` rule, self-optimisation step, `plugin-check.py` compiles.
- Writing the council grader immediately caught a latent case-sensitivity assumption (phases appear as `MAP`, `COUNCIL`, `VERDICT` inside a code fence, not in sentence case). The grader was corrected before shipping; the learning is that contract graders must match the form SKILL.md actually uses, not the form the designer intended.
- Layer 1 + Layer 2 dogfood on this release: **43 PASS, 0 FAIL, 0 SKIP**. The 3 previously-SKIPped per-skill eval slots now run real graders.
- New named standard in README: **Build artefacts.** Transient artefacts — intermediate zips, source trees, grader reports, cache folders — go to `/tmp`. Only the canonical `.plugin` shipping archive is permitted at the plugin root. Rule encoded in Layer 1's root-whitelist and reinforced as a block quote at the top of Step 4 in the governance skill. Captures the lesson from 0.3.x–0.4.0 where `.mcpb-cache/` and a stray `zimjorit` archive were shipped inside the plugin.

## 0.4.1 — 2026-04-21

- Governance skill `neomint-plugin-entwicklung` gains a proper plugin-level iteration loop, analogous to skill-creator but at plugin scope.
  - New Step 5 is a three-layer loop: Layer 1 structural checks (runnable), Layer 2 per-skill evals (orchestrated), Layer 3 independent audit subagent (unprimed reasoning pass). The loop closes only when all three layers pass in one complete pass.
  - New `scripts/plugin-check.py` — bundled runnable grader implementing Layer 1 + Layer 2 orchestration. Covers plugin.json validity and completeness, version format, CHANGELOG↔plugin.json consistency, README and SKILL.md mid-sentence truncation heuristic, `_shared` files, stray files at plugin root (whitelist), YAML frontmatter per SKILL.md, Language+Environment blocks per SKILL.md, `references/X.md` resolution (prose-only, ignores backticked placeholders), README↔skills coverage (no missing or ghost skills).
  - New `references/plugin-eval.md` — detailed mechanics of the three layers, how to add Layer 1 assertions, why Layer 3 cannot be replaced by a script.
- Fixed mid-sentence truncation in `skills/pdf-umbenennen/SKILL.md` (section "Sender — short-name rules" stopped at "Companies: short"). Section now completes the sender rules and adds the missing Subject short-form rules. Silent bug caught by the new Layer 1 assertion on its first run.
- `.mcpb-cache/` and stray `zimjorit` archive removed from the plugin root — both were leftover build artefacts that the new root-whitelist check flagged immediately.

## 0.4.0 — 2026-04-21

- New skill `council`: context-aware judgment system with five MECE roles (Analyst, Cartographer, Adversary, Scout, Operator) and a Chairman synthesis. Four structured phases (Orient, Map, Council, Verdict), three depth modes (QUICK, FULL, AUDIT), three environment modes (CODE, DOC, CHAT). Produces a two-track output (operative + management) with visible role attribution. Maintains `COUNCIL.md` persistence at the repo root (Claude Code), user-selected folder (Cowork), or as a downloadable artifact (Web) so follow-up runs are structurally cheaper than the first.
- Reference split: `skills/council/references/roles.md`, `phases.md`, `persistence.md` — progressive disclosure keeps the main SKILL.md under 500 lines.
- Iteration loop run on `council` (skill-creator workflow): 4 test cases × 2 configs (with-skill vs baseline) × 2 iterations. Iteration-2 with-skill result: 34/34 assertions pass (100%); baseline without-skill: 8/34 (24%). Iter-1 → iter-2 edits to SKILL.md: (a) output template gained a mandatory `Persistence:` line so `COUNCIL.md` is never silently skipped; (b) diagnostic-question standard now requires `Mode: DIAGNOSTIC   Context: <…>` as the first line, so branching away from the full Council is visible. Eval report under `skills/council/evals/ITERATION_REPORT.md`.
- `.claude-plugin/plugin.json` rebuilt: the previous file was truncated and invalid JSON. Now complete with all keywords and a valid schema.
- `README.md` rebuilt: the previous file was truncated mid-sentence. Now complete with all three skills documented, full plugin standards section, and the "Adding a new skill" process.
- Governance skill (`neomint-plugin-entwicklung`) improvements triggered by this release:
  - Step 2: documents the correct skill-creator invocation (the `Skill` tool with `skill: "skill-creator"`, not Bash or manual Read).
  - Step 4: changes the packaging workflow to build the zip in `/tmp` and copy into the workspace folder — avoids atomic-rename failures on mounted folders, and adds a `plugin.json` validity check of the archive contents.
  - Step 5a: adds two integrity checks — `plugin.json` must parse as valid JSON, and `README.md` must not end mid-sentence.
- `SKILL_TEMPLATE.md` expanded: the `## Additional references` section now documents when to split SKILL.md into `references/<topic>.md` (Progressive Disclosure pattern, trigger at ~400 lines or multiple independent sub-domains).
- Minor version bumped on explicit user instruction (new standalone skill of significant scope plus governance standard upgrades).

## 0.3.1 — 2026-04-21

- Added `CHANGELOG.md` with versioning scheme documentation
- Versioning rules documented in README and governance skill

## 0.3.0 — 2026-04-21

- Full English translation of all plugin content (README, plugin.json, SKILL_TEMPLATE, all skill SKILL.md files, _shared files)
- New `skills/_shared/language.md` — configurable output language, default: user's language
- Output language rules added to Plugin Standards in README
- Governance skill updated: Language block check added to Step 3 quality checklist, `language.md` added to plugin structure reference

## 0.2.0 — 2026-04-21

- Second skill `neomint-plugin-entwicklung` (governance): enforces skill-creator requirement, mandatory pre-research (Anthropic GitHub + community), iterative consistency check loop, self-optimisation after every change
- Plugin standards documented in README
- Environment compatibility for all three Claude platforms (Claude Code, Cowork, Claude AI Web)
- New `skills/_shared/environments.md` — single source of truth for environment detection logic
- New `SKILL_TEMPLATE.md` — starting point for new skills with all required blocks pre-defined

## 0.1.0 — 2026-04-21

- Initial plugin recovery and repackaging
- Skill `pdf-umbenennen`: automatically renames scanned PDFs based on document content (date, sender, subject)
- Author changed to NeoMINT GmbH
- Sensitive examples removed from skill
