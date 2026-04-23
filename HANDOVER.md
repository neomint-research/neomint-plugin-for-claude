# Übergabe — NeoMINT Toolkit Plugin

> **Verwendung:** Diese Datei als erste Nachricht in den neuen Chat einfügen.
> Claude liest sie und startet direkt mit dem nächsten Schritt.

---

## ⚠️ PFLICHTREGELN FÜR CLAUDE

**REGEL 1 — KNOWN_ISSUES.md ist immer aktuell zu halten:**
Nach jeder neuen Erkenntnis: ZUERST KNOWN_ISSUES.md aktualisieren, DANN weitere Aktionen.

**REGEL 2 — Versioning: nur fix-Ebene automatisch:**
Claude darf nur die fix-Nummer hochzählen. minor und major bleiben dem Nutzer vorbehalten — wenn eine Änderung subjektiv major/minor verdient, fix-bump liefern und nachfragen.

**REGEL 3 — skill-creator zuerst, dann Governance:**
Jede Skill-Inhaltsänderung läuft zuerst durch den skill-creator-Iterations-Loop (Evals, Grading). Erst danach: plugin-level Konsistenzprüfung und Repackaging via `update-plugin`-Skill.

**REGEL 4 — Git immer HTTPS, nicht SSH:**
Alle git-Befehle mit https://-URLs, niemals git@-Form.

**REGEL 5 — Windows PowerShell:**
Nutzer arbeitet mit PowerShell 5.x — kein `&&`-Chaining, Befehle als einzelne Zeilen zum Einfügen.

---

## Aktueller Stand

**Plugin-Version:** 0.6.15 (2026-04-23)

Das Plugin ist stabil. Housekeeping-Pass 0.6.14–0.6.15: KI-003 geschlossen (video-preview Layer-2-Grader), session-docs Grader `--count-only` nachgerüstet, alle 5 Skills mit gepinnten LAYER2_GRADER_FLOORS (total 106 Assertions), environments.md Wording fix, README commands-Frontmatter dokumentiert. Layer 1+2 PASS 125/125.

### Was bereits erledigt ist

- **Fünf Skills:** `council`, `rename-pdf`, `session-docs`, `update-plugin`, `video-preview` — alle mit Layer-2-Grader und gepinntem Floor
- **Vier Slash-Commands:** `/council`, `/rename-pdf`, `/session-docs`, `/update-plugin`
- Dreischichtiger Governance-Loop: Layer 1 (plugin-check.py, 124 Assertions), Layer 2 (pro Skill grade.py), Layer 3 (unprimed Audit-Subagent)
- CI via `.github/workflows/plugin-check.yml` + `release.yml`
- `dist/`-Lifecycle als Staging-Zone für Release-Archive
- Plugin-Archiv 0.6.13 gebaut und in `dist/` gestagt (147 KB)

### Offene Aufgaben (aus KNOWN_ISSUES.md)

1. **KI-001** — Council-Skill: automatische Rekursionen (nächste Council-Überarbeitung)
2. **KI-002** — Token-/Kontext-Optimierungsmuster als Standard in `update-plugin`-Skill
3. ~~KI-003~~ — erledigt in 0.6.14

---

## Nächster Schritt

Plugin 0.6.15 bereit für GitHub Release:
1. GitHub-Repo mit den Änderungen dieser Session synchronisieren (git add + commit + push)
2. GitHub Release 0.6.15 erstellen und `dist/neomint-toolkit.plugin` als Asset hochladen
3. Nach Upload: `dist/` leeren (`rm dist/neomint-toolkit.plugin`)

---

## Arbeitsmodus

- Cowork (Desktop-App) mit gemountetem Workspace: `/sessions/.../mnt/NeoMINT-plugin/`
- Plugin-Quellcode liegt unter `plugin/` im Workspace
- Release-Archive landen in `plugin/dist/` (Staging), dann als GitHub Release Asset
- Plugin wird per Cowork-Dateilink geliefert (`computer://`-Link)

---

## Infrastruktur-Referenz

| Was | Wert |
|---|---|
| Plugin-Quellverzeichnis | `plugin/` |
| Plugin-Check-Script | `plugin/skills/update-plugin/scripts/plugin-check.py` |
| Layer-2-Grader Council | `plugin/skills/council/scripts/grade.py` |
| Layer-2-Grader rename-pdf | `plugin/skills/rename-pdf/scripts/grade.py` |
| Layer-2-Grader update-plugin | `plugin/skills/update-plugin/scripts/grade.py` |
| Shared-Lib Grader-Utils | `plugin/skills/_shared/grader_utils.py` |
| CI Workflow | `.github/workflows/plugin-check.yml` |
| Release Workflow | `.github/workflows/release.yml` |
| Staging-Zone | `plugin/dist/` |

---

## Danach wartende Aufgaben

1. **KI-001 — Council automatische Rekursionen** ← offen
2. **KI-002 — Token-Optimierungsmuster in update-plugin** ← offen

---

## Projektdokumentation

```
NeoMINT-plugin/
├── KNOWN_ISSUES.md  ← Aktive + erledigte Issues — IMMER aktuell halten!
├── HANDOVER.md      ← Diese Datei
├── README.md        ← Repo-Level README (Forschungs-Angle + Plugin-Pointer)
├── plugin/          ← Plugin-Quellverzeichnis
│   ├── CHANGELOG.md
│   ├── plugin.json  ← Versionierung (aktuell: 0.6.13)
│   ├── commands/    ← Slash-Command-Einstiegspunkte
│   ├── skills/      ← Skill-Inhalte + Grader + Evals
│   └── dist/        ← Staging-Zone für Release-Archive
└── .github/         ← CI-Workflows
```

---

*Stand: 2026-04-23 — Plugin 0.6.15 stabil; Housekeeping-Pass: KI-003 geschlossen, alle Grader wired, 106 Layer-2-Assertions; zwei offene Punkte im Backlog (Council-Rekursionen, Token-Optimierungsmuster)*
