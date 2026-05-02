# Target tool families

Reference for the `prompt-master` skill. Loaded on demand when the pipeline
needs to confirm a target tool or fill defaults.

Adapted from the open-source `prompt-master` skill by Nidhin Joseph Nelson
(MIT-licensed). Reorganised to fit the NeoMINT plugin standard.

---

## Chat models — general

**Members:** Claude (3.5 Sonnet, 3.7 Sonnet, 4 family), GPT-4o, GPT-4.1,
Gemini 1.5 Pro, Gemini 2.0 Flash, Mistral Large, Llama 3.x, MiniMax.

**Distinguishing features:**
- Multi-turn capable, but a single prompt is the unit of work here.
- Respond well to role + constraints + format + task structure.
- Few-shot examples improve consistency when the task has a pattern.
- XML or fenced-block structure helps when the prompt mixes data and
  instructions.

**Defaults to fill if user did not specify:** output language matches input
language, output length proportional to task, structured output (markdown
headings or JSON) when the user implies a downstream consumer.

**Works:** role assignment, few-shot, structured input/output, grounding
anchors for closed-book tasks.

**Fails:** Chain-of-Thought scaffolding adds nothing on these models if the
task is not actually reasoning-heavy; it just inflates output. Universal
self-consistency cannot be emulated in one prompt.

---

## Reasoning-native models

**Members:** o1, o3, o4, o4-mini, DeepSeek-R1, Qwen3 in thinking mode, Claude
with extended thinking enabled.

**Distinguishing features:** these models reason internally before responding.
The visible "thinking" is real, not a prompted artefact. They are paid for
the reasoning, not for repeating it.

**Defaults:** state the goal cleanly, state the constraints, state the output
format. Stop.

**Works:** clear problem statement, explicit acceptance criteria, real
examples.

**Fails:** "think step by step", "show your reasoning", role-play scaffolding,
artificial CoT structure. All of these degrade the output. The model is
already thinking; telling it to think harder confuses the budget.

---

## Coding agents

**Members:** Claude Code, Cursor, Windsurf, GitHub Copilot, Devin, Bolt, v0,
Lovable, Replit Agent.

**Distinguishing features:**
- Operate inside a repository or workspace. Project context is implicit.
- Care about acceptance criteria, file scope, and what counts as done.
- Some (Claude Code, Cursor in agent mode, Devin) execute multi-step plans;
  others (Copilot inline) edit at cursor.

**Defaults to fill if user did not specify:** the agent's working directory
is the repo root, the language and framework are inferred from the file
context, the change is local unless cross-cutting is named.

**Works:** explicit file paths or file scope, acceptance criteria stated as
"done when ...", references to existing patterns ("follow the style of
`auth/login.ts`"), small surface area.

**Fails:** vague verbs ("clean up", "improve"), undefined success ("make it
better"), implicit cross-cutting ("update everything that uses this"),
re-stating well-known framework conventions the agent already knows.

---

## Image generators

**Members:** Midjourney v6/v7, DALL-E 3, Stable Diffusion (SD3, SDXL, Flux),
ComfyUI workflows, Adobe Firefly, Ideogram.

**Distinguishing features:**
- Each has its own prompt grammar. Midjourney accepts comma-separated
  descriptive phrases plus parameters (`--ar 16:9 --style raw`). Stable
  Diffusion accepts weighted tokens (`(masterpiece:1.2)`) and supports
  negative prompts. DALL-E 3 prefers natural-language sentences and rewrites
  prompts internally.
- The composition–style–technical separation is universal even if grammar
  differs.

**Defaults to fill if user did not specify:** aspect ratio matches use case
(16:9 for landscape, 1:1 for icon, 9:16 for vertical), style anchored to a
named genre or named photographer rather than left blank, lighting and lens
named explicitly for photographic targets.

**Works:**
- **Midjourney:** subject (specific) + composition (framing, angle) + style
  (genre or named artist) + technical (lighting, lens, render quality) +
  parameters at the end. Example: `samurai standing in the rain at night,
  low-angle shot, cinematic noir, neon reflections on wet pavement, 35mm
  Kodak Portra, soft rim light --ar 9:16 --style raw --v 7`.
- **Stable Diffusion:** weighted tokens, explicit negative prompt
  (`Negative: blurry, low quality, watermark, deformed`), model-appropriate
  resolution.
- **DALL-E 3:** complete sentences describing the scene; the model rewrites
  the prompt internally, so terseness does not help.

**Fails:** abstract concepts without anchoring ("beautiful", "amazing"),
contradictory style mixes, requests for text inside the image without
calling out the exact text in quotes.

---

## Video generators

**Members:** Sora, Runway Gen-3 / Gen-4, Pika, Kling, Luma Dream Machine,
Veo.

**Distinguishing features:**
- Time-aware: motion, camera move, duration matter.
- Subject consistency across frames is the hard problem; explicit anchoring
  helps.

**Defaults:** duration named (5s, 10s), camera move named (static, dolly-in,
pan-left), subject described once and then referred to consistently.

**Works:** clear single subject, simple camera move, named lighting.

**Fails:** multiple distinct subjects with separate motions, dialogue
generation (audio is separate), long durations beyond the model's range.

---

## Audio and voice

**Members:** ElevenLabs (TTS, voice cloning), Suno, Udio, MusicGen.

**Distinguishing features:** TTS prompts are text-with-direction; music
prompts are genre + instrumentation + mood + structure.

**Defaults:** for TTS, name the emotional tone and pacing; for music, name
the BPM range, instrumentation, and structural sections (intro, verse,
chorus).

**Works:** explicit emotional direction with brackets in TTS
(`[whispered] [excited]`), genre anchoring with two reference artists in
music.

**Fails:** abstract emotional descriptors without bracketed direction in TTS,
genre-stacking beyond two anchors in music.

---

## Automation and orchestration

**Members:** Zapier AI Actions, Make, n8n with AI nodes, custom LangChain or
LlamaIndex pipelines.

**Distinguishing features:** the prompt runs inside a step, not a chat. Input
and output schema matter more than tone. JSON output is usually required.

**Defaults:** structured output (JSON with named keys), explicit failure mode
("if the input is missing X, return `{\"error\": \"missing X\"}`").

**Works:** strict schema, named keys, explicit error contract.

**Fails:** prose output, undefined behaviour on missing input, mixing
explanation with the structured payload.
