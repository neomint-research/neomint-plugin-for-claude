# Output Language — NeoMINT Plugin Standard

## Default behavior

Always respond in the language the user is writing in. If the user writes in German,
respond in German. If they write in English, respond in English. Detect the language
from their message and match it automatically.

## User-configured override

If the user has explicitly stated a language preference in the current conversation
(e.g. "always respond in English" or "antworte immer auf Deutsch"), respect that
preference for all subsequent responses, regardless of the language they write in.

## Skill content vs. output language

The internal skill instructions (this file and all SKILL.md files) are written in
English for optimal LLM performance. This has no effect on the output language —
Claude always responds to the user in their language.
