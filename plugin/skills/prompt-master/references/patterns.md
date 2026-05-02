# Prompt architectures

Reference for the `prompt-master` skill. Loaded only when the architecture
choice is non-obvious. The pipeline picks exactly one and applies it
silently — the architecture is never named in the user-facing output.

Adapted from the open-source `prompt-master` skill by Nidhin Joseph Nelson
(MIT-licensed). Restructured for the NeoMINT plugin standard.

---

## Pattern A — Role + Constraints + Format + Task

**When to use.** Chat-model task with a clear stance and a specific output
shape. Most copywriting, analysis, summary, and review tasks.

**Skeleton.**
```
You are <role>.

Constraints:
- <constraint 1>
- <constraint 2>

Output format: <format>.

Task: <one-sentence task with the actual content>.
```

**Example.**
```
You are a senior security engineer writing for non-technical executives.

Constraints:
- one page maximum
- no jargon without inline definition
- name the worst-case scenario in plain language

Output format: a memo with three sections — what happened, what it means,
what we do next.

Task: Summarise the attached incident report for the board meeting tomorrow.
```

---

## Pattern B — Context + Scope + Acceptance + Format

**When to use.** Coding agents. The model is operating inside a repo and needs
to know where to act and when to stop.

**Skeleton.**
```
Context: <one or two sentences about the project and why this change>.

Scope: <which files, which directories, which tests>.

Acceptance criteria — done when:
- <criterion 1>
- <criterion 2>

Output: <PR-ready diff, single file, inline edit, etc.>.
```

**Example.**
```
Context: Auth module currently uses session cookies; we are migrating to JWT
with refresh-token rotation.

Scope: `auth/login.ts`, `auth/refresh.ts`, and the matching tests under
`auth/__tests__/`. Do not touch `auth/legacy/` — that is a separate phase.

Acceptance criteria — done when:
- login returns access token (15-min expiry) and refresh token (7-day expiry)
- refresh endpoint rotates the refresh token on every use
- existing tests still pass; new tests cover the rotation case

Output: PR-ready diff with commit message.
```

---

## Pattern C — Subject + Composition + Style + Technical (+ Negative)

**When to use.** Image generators. Order matters in some grammars (Midjourney
weights earlier tokens more), but the shape is the same across tools.

**Skeleton (Midjourney syntax).**
```
<subject — specific>, <composition — framing and angle>, <style — genre or
named anchor>, <technical — lighting, lens, render>, <parameters>
```

**Skeleton (Stable Diffusion syntax).**
```
<subject>, <composition>, <style>, <technical>, (key emphasis:1.2)
Negative: <what must not appear>
```

**Example (Midjourney).**
```
samurai standing in the rain at night, low-angle wide shot,
cinematic noir with Blade Runner colour palette,
35mm Kodak Portra, soft rim light from neon signs,
shallow depth of field --ar 9:16 --style raw --v 7
```

---

## Pattern D — Bare goal (reasoning-native models)

**When to use.** o-series, R1-class, Claude with extended thinking. The model
reasons internally; scaffolding hurts.

**Skeleton.**
```
<one-paragraph problem statement>.

Constraints: <hard constraints if any>.
Acceptance: <what counts as a correct answer>.
```

**Example.**
```
Three integers a, b, c satisfy a + b + c = 30 and a² + b² + c² = 338.
Find all integer triples (a, b, c) with a ≤ b ≤ c.

Constraints: integers only, ordered triples, all triples enumerated.
Acceptance: a complete list with a brief verification of one triple.
```

What is *not* in this prompt: "think step by step", "show your work", "first
do X, then Y", role assignment. None of these helps a reasoning-native model.

---

## Pattern E — Fix-existing-prompt

**When to use.** User pastes a prompt and asks for repair, sharpening, or
adaptation.

**Procedure.**
1. Read the user's prompt for *intent*. The intent is usually correct; the
   execution is the problem.
2. Identify the actual defect: redundant words, missing structural elements,
   wrong target tool, contradictory constraints, fabrication-prone technique.
3. Produce the repaired prompt in the same shape the user implied. Do not
   switch architectures unless the original architecture was the defect.
4. The metadata line names the defect that was fixed
   (e.g. `Note: Removed three redundant clauses and added the missing acceptance
   criterion.`).

The repaired prompt is the deliverable — not a critique of the original.

---

## Pattern F — Embedded data + instructions

**When to use.** The user supplies data (a paragraph, a table, a code block,
an image description) and wants the AI to operate on it.

**Skeleton.**
```
<short instruction stating what to do>.

<data fenced or XML-tagged>

<output requirement>.
```

**Example.**
```
Extract every named person and their stated role from the text below.

<text>
... long passage ...
</text>

Output as JSON: [{"name": "...", "role": "..."}, ...]. If a role is not
stated, use null.
```

The fence or XML tag prevents the model from confusing data with instructions
and reduces injection risk if the data is user-supplied.
