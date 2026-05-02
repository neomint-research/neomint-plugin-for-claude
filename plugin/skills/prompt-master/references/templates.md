# Paste-ready templates

Reference for the `prompt-master` skill. Loaded only when a target-and-task
combination matches a pre-built skeleton — the pipeline fills the slots and
delivers, without re-deriving the architecture.

Adapted from the open-source `prompt-master` skill by Nidhin Joseph Nelson
(MIT-licensed). Reduced to the highest-leverage skeletons; full upstream is
broader.

Each skeleton names the target tool, the fillable slots in `{curly braces}`,
and the architecture used (so a reviewer can trace why this skeleton fits).

---

## T1 — Claude / GPT-4o: structured analysis from a document

**Architecture:** Pattern A (role + constraints + format + task).

```
You are {role: e.g. "a senior policy analyst"}.

Constraints:
- {audience constraint, e.g. "writing for non-specialists"}
- {length constraint, e.g. "max 400 words"}
- {style constraint, e.g. "no jargon without inline definition"}

Read the document below and produce {output: e.g. "a structured summary
with three sections: findings, implications, recommended next steps"}.

<document>
{paste document content here}
</document>
```

---

## T2 — Reasoning-native (o3, o4-mini, R1, Claude extended thinking): hard problem

**Architecture:** Pattern D (bare goal).

```
{one-paragraph problem statement, including all data the model needs}.

Constraints: {hard constraints, e.g. "integer solutions only", "must run in
O(n log n)", "memory budget 16 MB"}.

Acceptance: {what counts as a correct answer, e.g. "a complete enumeration
with one verified example"}.
```

No "think step by step". No role-play. No example-of-reasoning prefix.

---

## T3 — Claude Code / Cursor: targeted change with acceptance criteria

**Architecture:** Pattern B (context + scope + acceptance + format).

```
Context: {one or two sentences — what the project is and why this change
matters}.

Scope:
- Files: {list specific files}
- Out of scope: {explicitly name what not to touch}

Acceptance — done when:
- {criterion 1, observable}
- {criterion 2, observable}
- {existing tests still pass; new tests cover {case}}

Reference style: {point to an existing file or pattern, e.g. "follow the
shape of `auth/login.ts`"}.

Output: PR-ready diff with commit message.
```

---

## T4 — Coding agent: bug investigation from a stack trace

**Architecture:** Pattern B with Pattern F embedded (data fence).

```
Context: {short description of the system and where this trace came from}.

<stack-trace>
{paste full stack trace, including the failing assertion or exception}
</stack-trace>

Scope: identify the root cause, propose the minimal fix, and produce the
patch.

Acceptance — done when:
- the cause is named explicitly (file, line, condition)
- the fix is the smallest change that resolves the cause without touching
  unrelated code
- if the fix needs a new test, add it; if the existing test should have
  caught this, say so explicitly

Output: cause statement (1-3 sentences), patch as a unified diff, optional
new test.
```

---

## T5 — Midjourney: photographic image

**Architecture:** Pattern C (subject + composition + style + technical).

```
{subject — specific noun phrase with one distinctive detail},
{composition — framing and angle, e.g. "low-angle wide shot"},
{style — named genre or named photographer, e.g. "cinematic noir, Blade
Runner colour palette"},
{technical — lighting, lens, render, e.g. "35mm Kodak Portra, soft rim
light, shallow depth of field"}
--ar {aspect ratio, e.g. 16:9 or 9:16} --style raw --v 7
```

---

## T6 — Midjourney: illustration (non-photographic)

**Architecture:** Pattern C, technical slot reframed for illustration.

```
{subject},
{composition},
{style — named illustrator or art movement, e.g. "in the style of Moebius",
"art nouveau poster"},
{technical — line work, palette, texture, e.g. "ink and watercolour, muted
palette, visible paper grain"}
--ar {aspect} --style raw --v 7
```

---

## T7 — Stable Diffusion / Flux: image with negative prompt

**Architecture:** Pattern C with explicit negative slot.

```
{subject}, {composition}, {style}, {technical}, (key emphasis:1.2)

Negative: blurry, low quality, watermark, deformed anatomy, extra fingers,
text artefacts, {plus any task-specific negatives}
```

---

## T8 — DALL-E 3: scene description in natural language

**Architecture:** Pattern C, but as full sentences (DALL-E 3 rewrites
internally, so terseness does not help).

```
A {composition phrase} of {subject with two distinctive details}.
{Style sentence — genre, era, references}. {Technical sentence — lighting,
medium, atmosphere}. The image is {aspect orientation, e.g. "in landscape
orientation"}.
```

---

## T9 — Sora / Runway / Pika: short video clip

**Architecture:** Pattern C extended with motion and duration.

```
{subject — single clear subject},
{camera — static / dolly-in / pan-left / orbit},
{motion — what the subject does, in one verb phrase},
{environment — lighting, weather, time of day},
{style — cinematic / documentary / animated, with one anchor},
{duration: 5s | 10s}
```

---

## T10 — ElevenLabs TTS: read with direction

**Architecture:** plain text with bracketed direction.

```
[{emotional tone, e.g. "warm" or "concerned"}] [{pacing, e.g. "measured"}]
{the text to read, written as it should sound — punctuation drives pauses}
```

For voice-cloning targets, add the source-voice anchor in the metadata line
(`🎯 Target: ElevenLabs · Voice: <name>`) rather than in the prompt itself.

---

## T11 — Suno / Udio: original song

**Architecture:** genre + instrumentation + structure + mood.

```
[Genre] {primary genre, anchored to one or two reference artists}
[Instrumentation] {lead instrument(s), rhythm section, any distinctive
texture}
[Structure] Intro - Verse - Chorus - Verse - Chorus - Bridge - Chorus - Outro
[Mood] {single mood word}, {single energy descriptor, e.g. "driving" or
"contemplative"}
[BPM] {number}

[Lyrics]
{verse 1}
...
```

---

## T12 — Zapier / Make / n8n: AI step inside a workflow

**Architecture:** strict-schema output, explicit error contract.

```
You are an extraction step in a workflow. Read the input and return a JSON
object with exactly these keys:

{
  "{key1}": "{type and meaning}",
  "{key2}": "{type and meaning}",
  "error": "string or null"
}

If the input is missing required information, do not guess. Set "error" to
a one-line description of what is missing and leave the other keys as null.

Input:
{input variable from the upstream step}
```

The workflow's downstream step is responsible for branching on `error`. The
prompt does not produce prose — only the JSON object.

---

## T13 — Fix-existing-prompt: any tool

**Architecture:** Pattern E.

```
{user's original prompt — pasted by user}
```

Operate on the original. Strip redundant words, add missing structural
elements, correct fabrication-prone techniques, return the new prompt in the
same shape the original implied. The metadata line names the defect that was
repaired.
