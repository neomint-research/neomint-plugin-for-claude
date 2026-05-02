# File Templates — session-docs

These templates define the structure for each documentation file.
When creating a file from scratch, use the template, fill in what is
known from context, and mark unknowns with `<!-- TODO: fill in -->`.

---

## KNOWN_ISSUES.md

```markdown
# Known Issues — [Projektname]

> **Pflicht:** Diese Datei wird von Claude vor jedem Planungsschritt gelesen.
> Jede neue Erkenntnis wird sofort hier eingetragen — bevor andere Aktionen folgen.

---

## Offene Issues

<!-- Add issues as KI-NNN entries. Use the format below. -->

<!--
### KI-001 · [Komponente]: [Kurztitel]
**Status:** Aktiver Blocker | Niedrige Priorität | In Bearbeitung
**Symptom:** Was ist sichtbar?
**Ursache:** Was ist die Ursache (falls bekannt)?
**Fix:** Was ist der Fix (falls bekannt)?
**Befunde:**
- Run #NNN: [Befund]
-->

---

## Erledigte Issues (Archiv)

| ID | Titel | Erledigt |
|----|-------|----------|

---

*Zuletzt aktualisiert: YYYY-MM-DD*
```

---

## HANDOVER.md

```markdown
# Übergabe — [Projektname]

> **Verwendung:** Diese Datei als erste Nachricht in den neuen Chat einfügen.
> Claude liest sie und startet direkt mit dem nächsten Schritt.

---

## PFLICHTREGELN FÜR CLAUDE

**REGEL 1 — KNOWN_ISSUES.md ist immer aktuell zu halten:**
Nach jeder neuen Erkenntnis: ZUERST KNOWN_ISSUES.md aktualisieren, DANN weitere Aktionen.

**REGEL 2 — [Projekt-spezifische Regel]:**
<!-- TODO: fill in -->

---

## Aktiver Blocker

**[Titel des Blockers]**

<!-- TODO: fill in — was ist konkret blockiert, was ist der nächste Schritt? -->

### Was bereits geklärt ist

- <!-- TODO: fill in -->

### Das konkrete Problem

<!-- TODO: fill in — Symptom, Befunde, Hypothesen -->

### Nächster Schritt

<!-- TODO: fill in — konkret und spezifisch -->

---

## Arbeitsmodus

<!-- TODO: fill in — wie greift Claude auf Systeme zu? SSH? API? Browser? -->

---

## Infrastruktur-Referenz

| Was | Wert |
|---|---|
| <!-- TODO | fill in --> |

---

## Danach wartende Aufgaben

1. **[Aktiver Blocker]** ← aktiv (siehe oben)
2. <!-- TODO: fill in -->

---

## Projektdokumentation

```
[Projektordner]/
├── KNOWN_ISSUES.md  ← Aktive + erledigte Issues — IMMER aktuell halten!
├── HANDOVER.md      ← Diese Datei
└── <!-- TODO: weitere Dateien -->
```

---

*Stand: YYYY-MM-DD — [Ein-Satz-Zusammenfassung des aktuellen Stands]*
```

---

## Memory file — feedback_*.md

```markdown
---
name: [Kurzer Name]
description: [Einzeiler — wird für Relevanz-Entscheidungen genutzt]
type: feedback
---

[Die Regel oder Präferenz — prägnant formuliert]

**Why:** [Warum gilt diese Regel — Hintergrund aus dem Gespräch]

**How to apply:** [Wann und wo diese Regel greift — damit Randfälle beurteilbar sind]
```

---

## Memory file — project_*.md

```markdown
---
name: [Kurzer Name]
description: [Einzeiler — wird für Relevanz-Entscheidungen genutzt]
type: project
---

[Der Fakt oder die Entscheidung — prägnant]

**Why:** [Motivation — Constraint, Deadline, Stakeholder-Anforderung]

**How to apply:** [Wie dieser Fakt zukünftige Entscheidungen beeinflusst]
```

---

## Memory file — reference_*.md

```markdown
---
name: [Kurzer Name]
description: [Einzeiler — wo findet man was]
type: reference
---

[Pointer auf die externe Ressource und ihren Zweck]
```

---

## MEMORY.md index entry format

```
- [Title](file.md) — one-line hook that makes the entry's purpose clear at a glance
```

Max 150 characters per line. The index is loaded every session — keep it scannable.
