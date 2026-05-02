---
description: Generate a sharp, copy-ready prompt for any AI tool — chat, reasoning-native, coding, image, video, audio, automation.
argument-hint: "[target tool and goal, optional]"
---

# /prompt-master

The user has invoked the prompt-master skill explicitly. Run it exactly as
specified in the `prompt-master` skill — the skill carries the full contract
(identity, hard rules, the nine-dimension extraction, the architecture
selection, the token-efficiency audit, and the Web fallback).

## What to do now

1. Load the skill: read `skills/prompt-master/SKILL.md` — this is the
   contract. The identity, the never-embed list, the reasoning-native rule,
   the three-question ceiling, and the output format all live there. Do not
   paraphrase from memory; read it.
2. Apply the shared conventions: `skills/_shared/language.md` for output
   language, `skills/_shared/environments.md` for Claude Code / Cowork / Web
   differences (this skill is chat-only — file access is optional).
3. If the user passed a target tool and goal as an argument
   (`/prompt-master Cursor — refactor my auth module`), parse it and skip
   the "what is the target tool" question. Otherwise, ask the target tool
   first if it is not obvious.
4. Follow the skill verbatim from there: detect target → extract intent →
   select architecture from `references/patterns.md` → fill from
   `references/templates.md` if a skeleton matches → audit → deliver.

## Guardrails the skill already enforces — reminders, not duplication

- **Never embed fabrication-prone techniques.** Mixture-of-Experts,
  Tree-of-Thought, Graph-of-Thought, Universal Self-Consistency, layered
  prompt-chaining-as-single-prompt — none of these belong in the output.
  The skill's grader fails if these are removed from the hard-rules list.
- **No Chain-of-Thought on reasoning-native models.** o-series,
  DeepSeek-R1, Qwen3 thinking mode, Claude with extended thinking. CoT
  scaffolding degrades these models. The model already reasons.
- **Three questions maximum.** If the third answer would still leave
  critical uncertainty, ship with the assumption named and offer a
  follow-up version. Never loop.
- **Single copyable block.** The output is one prompt block plus the
  metadata line (`🎯 Target: ...` and `💡 ...`). No five-variant menus,
  no "let me know if you want changes", no recap of what was done.
- **The architecture is silent.** The user never sees "I used Pattern A"
  or "I selected the role-constraints-format-task scaffold". The label is
  for internal reasoning; the prompt is what ships.

## Now

Follow `skills/prompt-master/SKILL.md`.
