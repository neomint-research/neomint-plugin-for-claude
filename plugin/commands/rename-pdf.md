---
description: Rename PDF files in a folder based on document content — yyyy-mm-dd_Sender_Subject-short.pdf.
argument-hint: "[folder path, optional]"
---

# /rename-pdf

**Output language:** respond in the language the user wrote in. German
in → German out, English in → English out. If the user has set an
explicit language preference earlier in the conversation, respect that
instead. This rule applies from your first response, before any skill
file is read. (Full rule: `skills/_shared/language.md`.)

The user has invoked the PDF-rename skill explicitly. Run it exactly as specified in
the `rename-pdf` skill — the skill carries the full contract (filename convention,
parallel batch reading, edge-case handling, sender and subject short-name rules, and
the Web fallback).

## What to do now

1. Load the skill: read `skills/rename-pdf/SKILL.md` — this is the contract.
   Every rule about the filename convention, batching, edge cases (multi-document
   scans, events, receipts), and the Claude-AI-Web fallback lives there. Do not
   paraphrase it from memory; read it.
2. Apply the shared conventions: `skills/_shared/language.md` for output-language
   rules, `skills/_shared/environments.md` for Claude Code / Cowork / Web
   differences.
3. If a folder path was passed as an argument, use it directly. Otherwise: ask the
   user which folder to process — or in Claude AI (Web), ask them to upload the
   PDFs into the chat.
4. From there, follow the skill verbatim.

## Guardrails the skill already enforces — reminders, not duplication

- **Document date, not scan date.** The filename segment is the date *on* the
  document (invoice date, letter date, notice date), not the date from the scan
  filename. Read the PDF content to get it right.
- **Parallel batches of 6–8.** Not one by one, not all at once.
- **Mapping first, rename second.** Show the user the full old → new mapping
  before executing any `mv`. Conflicts are resolved before renaming, not after.
- **Atomic rename.** All `mv` commands in a single Bash call, chained with `&&`,
  so a mid-run failure is visible and undoable.
- **`Unknown` / `Unbenannt` for unknowns.** Never guess a sender or subject.
  If the document does not support a confident read, the skill says so explicitly.

## Now

Follow `skills/rename-pdf/SKILL.md`.
