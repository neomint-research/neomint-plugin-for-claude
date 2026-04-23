# Known Issues — NeoMINT Toolkit Plugin

> **Pflicht:** Diese Datei wird von Claude vor jedem Planungsschritt gelesen.
> Jede neue Erkenntnis wird sofort hier eingetragen — bevor andere Aktionen folgen.

---

## Offene Issues

### KI-001 · Council-Skill: Automatische Rekursionen fehlen
**Status:** Niedrige Priorität (nächste Council-Überarbeitung)
**Symptom:** Bei substantiellem Widerspruch einer Rolle gegen eine frühere muss der Nutzer manuell "übergib zurück" sagen — das Skill kennt keinen automatischen Rückgriff.
**Ursache:** Das Skill kennt nur linearen Pfad T1→T7, CHAIRMAN-VETO und Nutzer-Steering, aber keine automatische Rollenrekursion.
**Fix:** Rekursionsmuster einbauen — Trigger-Definition (was ist "substantieller Widerspruch"), Shape (voller Turn vs. Interstitial), Abbruch-Regel (max. 1 Rekursion), Pfad-Rerun nach Rekursion (vollständig ab rekurrierter Rolle). Kostenmuster aus project_council_optimization_pattern mitdenken.
**Befunde:**
- 2026-04-21: Beim Council-Lauf über Council-Optimierung musste der Nutzer manuell "übergib zurück an den Kartographen" anstoßen.

---

### KI-002 · Plugin-Standard: Token-/Kontext-Optimierungsmuster nicht im Governance-Skill
**Status:** Niedrige Priorität (bei nächster update-plugin-Skill-Überarbeitung)
**Symptom:** Das Subagent/Caching/Modellwahl-Muster, das am Council erarbeitet wurde, ist nicht als Standard-Prüfschritt im `update-plugin`-Skill verankert.
**Ursache:** Muster wurde Council-spezifisch erarbeitet, nie als allgemeinen Skill-Standard aufgenommen.
**Fix:** Abschnitt "Token- und Kontext-Optimierung" mit Checkliste in `update-plugin/SKILL.md` einbauen — Subagent-Auslagerung, Prompt-Caching, gemischte Modellwahl, Mess-Mechanismus.

---

### ~~KI-003 · video-preview: Kein Layer-2-Grader vorhanden~~ — ERLEDIGT 0.6.14

---

## Erledigte Issues (Archiv)

| ID | Titel | Erledigt |
|----|-------|----------|
| KI-003 | video-preview: Layer-2-Grader fehlte | 0.6.14 (2026-04-23) |

---

*Zuletzt aktualisiert: 2026-04-23 (0.6.15)*
