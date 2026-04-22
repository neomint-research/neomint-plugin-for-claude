---
name: rename-pdf
description: >
  Renames PDF documents in a folder automatically based on their content — date, sender,
  and subject — following the convention yyyy-mm-dd_Sender_Subject-short.pdf. Use this
  skill whenever the user has a folder of PDFs with cryptic or auto-generated names
  (e.g. 2026-04-15.pdf, scan_001.pdf, IMG_003.pdf) and wants human-readable filenames.
  Trigger signals in either English or German: mention of a scanner or scan folder
  (ScanSnap, Fujitsu, inbox, archive, Scan-Ordner); desire for content-based filenames
  ("rename scans", "by date and sender", "proper names", "self-explanatory",
  "recognise without opening", "clean up folder", "Scans umbenennen",
  "ordentlich benennen", "nach Datum und Absender"); or simply a folder of PDFs to
  rename. Also trigger when the user does not say "rename" but clearly describes a
  folder of scans with unreadable filenames. Also runs when the user invokes
  `/rename-pdf` explicitly. Do not use for: merging PDFs, converting, full-text search,
  or sequential numbering.
---

# Rename PDF — Automatically name scanned documents

This skill renames all PDF files in a folder based on their document content.
The goal: an archive that explains itself — date, sender, and topic at a glance,
without opening the file.

---

## Language

Read `../_shared/language.md` and apply the output language rules defined there.

## Environment detection

Read `../_shared/environments.md` and handle accordingly.
The web fallback for this skill is described below under "Procedure in Claude AI (Web)".

---

## Filename convention

```
yyyy-mm-dd_Sender_Subject-short.pdf
```

**Three segments separated by underscores:**
- `yyyy-mm-dd` — document date (invoice date, letter date, notice date — NOT the scan date from the filename)
- `Sender` — short name of the sender, words joined with hyphens
- `Subject-short` — topic/content in concise form, words joined with hyphens

**Character rules:**
- No spaces
- Replace umlauts: ä→ae, ö→oe, ü→ue, ß→ss
- No special characters (brackets, slashes, dots in the name)
- Dots only before `.pdf`

**Examples:**
```
2026-03-14_Sender-A_DocumentType-AdditionalInfo.pdf
2026-01-18_Sender-B_DocumentType-AdditionalInfo.pdf
2025-10-22_Sender-C_DocumentType-AdditionalInfo.pdf
```

---

## Procedure with file access (Claude Code & Cowork)

### 1. List files

```bash
ls /path/to/folder/*.pdf | sort
```

Inventory all existing PDF files before renaming anything.

### 2. Read PDFs in parallel — batches of 6–8

Read multiple PDFs simultaneously using the `Read` tool. Batches of 6–8 are optimal —
not one by one (too slow), not all at once (overwhelms context).

For each PDF extract:
- **Date**: The actual document date — e.g. invoice date, letter date, issue date, notice
  date. The scan filename (e.g. `2026-01-14.pdf`) contains the scan date, which almost
  always differs from the document date.
- **Sender**: Short form — company name, authority, or institution. Not the full legal
  name, but what anyone immediately recognises.
- **Subject**: Topic or content in concise form. Add distinguishing details: contract
  numbers, persons affected (for family documents), addresses (for property documents),
  amounts (if significant).

### 3. Handle edge cases cleanly

**Multi-document scan** (two letters scanned together):
Use the primary/more significant document as the basis for the filename. The older date
is usually primary. If both are equal, choose the chronologically earlier one.

**No exact date** (only month/year given, e.g. "November 2025"):
Use the first of the month as placeholder: `2025-11-01`

**Event tickets**:
Use the event date, not the purchase date — that date is more relevant for archiving.

**Receipts/cash register slips**:
Use the transaction date.

**Hospitality receipts**:
Use the restaurant date. Mention the persons hosted or the occasion in the subject if
legible.

**Family post** (multiple people in the household):
If the document concerns a specific person, include their surname or an initial in the
subject to distinguish documents from different people.

**Same-name documents** (multiple files with same date and sender):
Add distinguishing details to the subject, e.g. contract number, person, address.

### 4. Prepare and verify renaming

Before running `mv` commands:
- Check all target filenames for conflicts (no filename may appear twice)
- Create the complete mapping list and briefly present it to the user

### 5. Execute all renames at once

```bash
cd /path/to/folder && \
mv "old-name.pdf" "new-name.pdf" && \
mv "old-name2.pdf" "new-name2.pdf" && \
echo "Done"
```

Everything in a single Bash call — making the rename atomic and easy to undo if
something goes wrong.

### 6. Verify result

```bash
ls *.pdf | sort
```

Show the result and briefly summarise: how many files renamed, what time period covered.

---

## Procedure in Claude AI (Web)

No direct file access — the user must upload the PDFs into the chat.

**If no PDFs have been uploaded yet:**
Ask the user to upload the PDFs directly into the chat. Example:
> "Please upload the PDFs directly here — I'll read them and create a rename list."

**Once PDFs are available (as uploads in context):**

1. Read all uploaded PDFs and extract date, sender, subject
2. Create and show a mapping table for confirmation:

```
Current name            → New name
invoice_scan.pdf        → 2026-03-14_Sender-A_DocumentType.pdf
letter_2026.pdf         → 2026-02-05_Sender-B_DocumentType.pdf
```

3. After confirmation: provide a shell script the user can run locally:

```bash
#!/bin/bash
# PDF rename — run this in the folder containing the PDFs
mv "invoice_scan.pdf" "2026-03-14_Sender-A_DocumentType.pdf"
mv "letter_2026.pdf" "2026-02-05_Sender-B_DocumentType.pdf"
echo "Done — $(ls *.pdf | wc -l) PDFs renamed"
```

The user runs the script locally. This way the actual renaming stays on their machine,
even without direct file access.

---

## Typical German document types and their date fields

| Document type | Date field |
|---|---|
| Invoice | Invoice date |
| Notice / Assessment | Notice date |
| Bank statement | Creation date or cutoff date |
| Letter / Correspondence | Letter date |
| Hospitality receipt | Transaction date |
| Cash register receipt | Receipt date |
| Annual information | Letter date |
| Document without exact date | First of the stated month |

---

## Sender — short-name rules

- Authorities: short name of the authority, with location if needed — `Authority-City`
- Companies: short, commonly used brand form of the company name (e.g. `Amazon`, `Shell`, `Vodafone`). Drop legal suffixes like GmbH, AG, KG, Ltd, Inc.
- Banks / insurers: short institution name, without legal suffix (e.g. `DKB`, `Allianz`, `Barmenia`). If the sender is a specific product line, append it with a hyphen (e.g. `Allianz-Rechtsschutz`).
- Persons: surname only; if the surname is ambiguous, add a first-name initial after a hyphen (`Meyer-K`).
- Self / own organisation: fixed short label of the own organisation (e.g. `NeoMINT`).

If the sender cannot be determined from the document content, use `Unknown` rather than guessing.

---

## Subject — short-form rules

- 2–4 words, hyphen-separated, lowercase where it does not change meaning.
- Describe what the document *is about*, not what it *is* (prefer `vertrag-kfz` over `document`).
- Avoid redundant information already in the sender field.
- If the subject cannot be derived with confidence, use `Unbenannt`.
