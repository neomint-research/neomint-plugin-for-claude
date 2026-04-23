---
name: video-preview
description: >
  Creates a short MP4 preview video of a website, web app, dashboard, or static HTML/CSS page
  using Puppeteer (headless browser) and ffmpeg. The video simulates how a real user would
  interact with the page — scrolling, clicking through navigation, zooming into key areas —
  and outputs a compressed video ready to send via Signal, Slack, or email.
  Use this skill whenever the user wants to record a website or web UI as a video, create a
  screen-capture demo, make a preview clip of a prototype or dashboard, produce a short
  walkthrough video for sharing, or show off a web project without a live call.
  Trigger even if the user doesn't say "video" explicitly — phrases like "zeig das als Clip",
  "mach einen kurzen Preview", "record the page", or "ich will das schnell teilen können"
  are all good trigger signals.
---

# video-preview — Web UI to shareable MP4

## Language

Read `../_shared/language.md` and apply the output language rules defined there.

## Environment detection

Read `../_shared/environments.md` and handle accordingly.

---

## Invocation model

**Pattern 1 — Auto-only.** No `disable-model-invocation` flag. The skill fires when
the user describes wanting to record a web page or share a UI as a video clip —
no explicit `/video-preview` command needed. The intent is unambiguous enough that
auto-firing does not race the user's wish.

---

## What this skill does

It turns a URL (or local HTML file) into a short, compressed MP4 by:

1. Opening the page in a headless Chromium browser via Puppeteer
2. Executing a click-demo script: navigating, clicking, scrolling as instructed
3. Capturing frames as screenshots at a defined interval
4. Stitching frames into a video with ffmpeg, encoded for mobile sharing

Default output: `1080×1920` (9:16 portrait), ~15–30s, H.264, optimized for Signal/WhatsApp.

---

## Quick-start checklist

Before writing any code, collect:

- [ ] **URL or file path** — what page to record
- [ ] **Interaction script** — what to click/scroll (or "just scroll top to bottom")
- [ ] **Duration** — target length in seconds (default: 20s)
- [ ] **Resolution** — default is `1080x1920` (9:16); override if needed
- [ ] **Output path** — where to save the `.mp4`

If any of these are missing, ask before proceeding. A bad interaction script wastes the
whole render cycle.

---

## Environment behavior

### Claude Code / Cowork (Bash tool available)

Full pipeline runs locally. Requires:
- `node` + `puppeteer` npm package
- `ffmpeg` installed and on PATH

Check availability first:
```bash
node -e "require('puppeteer')" 2>&1 && ffmpeg -version 2>&1 | head -1
```

If missing, install and tell the user:
```bash
npm install puppeteer
# ffmpeg: brew install ffmpeg (macOS) / apt install ffmpeg (Ubuntu)
```

### Claude AI Web (no Bash tool)

No direct execution possible. Deliver:
1. A ready-to-run Node.js script (`record.js`) the user can run locally
2. An ffmpeg one-liner to stitch frames
3. Clear instructions for how to run both steps

---

## Procedure with file access (Claude Code & Cowork)

### Pipeline — step by step

### Step 1: Write the Puppeteer capture script

Generate `record.js` based on the user's interaction requirements.
See `references/puppeteer-patterns.md` for copy-paste patterns:
- scroll-through
- click navigation
- highlight-zoom

**Key settings for 9:16 mobile viewport:**
```js
const viewport = { width: 1080, height: 1920 };
```

Save screenshots to a temp folder: `/tmp/preview-frames/frame-%04d.png`

Frame rate: 10 fps (one screenshot every 100ms) is a good default.
For a 20s video → 200 frames. Adjust the interaction script timing accordingly.

### Step 2: Run the capture

```bash
node record.js
```

Verify frames were written:
```bash
ls /tmp/preview-frames/ | wc -l
```

If frame count is 0 or the page didn't load: check the URL, check for JS errors in
Puppeteer's `page.on('console', ...)` output, and look for network timeouts.

### Step 3: Stitch with ffmpeg

Standard Signal-optimized encode (9:16, H.264, ~2 Mbps, fast decode):

```bash
ffmpeg -framerate 10 \
  -i /tmp/preview-frames/frame-%04d.png \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
  -c:v libx264 \
  -preset slow \
  -crf 23 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  output.mp4
```

`-movflags +faststart` is important — it moves the MP4 metadata to the front so the
video plays immediately in messaging apps without fully downloading first.

After encoding, report the file size:
```bash
du -sh output.mp4
```

Target: under 15 MB for Signal. If larger, increase `-crf` (try 26–28) or reduce
the frame rate.

### Step 4: Deliver

- In Cowork: save to the user's workspace folder and provide a `computer://` link
- In Claude Code: tell the user the output path
- In Web: provide the ffmpeg command as a code block

---

## Interaction script patterns

Read `references/puppeteer-patterns.md` for full code.

**Click-demo** (most common): define a sequence of `[selector, delay_ms]` pairs.
The script clicks each element, waits, then captures frames. Example:
```
nav a[href="/dashboard"]  → wait 1500ms → capture 30 frames
button.show-details       → wait 800ms  → capture 20 frames
```

Ask the user for the click sequence if not specified. Even a rough description works:
"click the top menu, then the first card, then scroll down" is enough to write the script.

**Scroll-through**: simple autopilot — scroll from top to bottom at a constant speed.
Good default if the user just wants to show the page content.

**Highlight-zoom**: zoom into a specific element mid-video for emphasis.
Use CSS transform on the element or Puppeteer's `page.evaluate()`.

---

## Common issues and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Blank / white frames | Page not loaded yet | Add `await page.waitForNetworkIdle()` before capture |
| Font/CSS missing | Local file path issue | Use `file://` absolute path or serve locally with `npx serve` |
| Video too dark | Dark mode / OS theme | Force light mode: `page.emulateMediaFeatures([{name:'prefers-color-scheme',value:'light'}])` |
| File > 15 MB | Too many frames or low CRF | Increase `-crf` to 26, reduce capture duration |
| Signal won't play | Missing faststart | Add `-movflags +faststart` to ffmpeg command |

---

## Output naming convention

```
yyyy-mm-dd_<short-description>_preview.mp4
```

Example: `2026-04-23_neomint-dashboard_preview.mp4`

This makes it easy to find the right file after several iterations.

---

## Procedure in Claude AI (Web)

When Bash is not available, produce three files:

1. **`record.js`** — complete Puppeteer script, ready to run with `node record.js`
2. **`stitch.sh`** — the ffmpeg one-liner as a shell script
3. **`README.md`** — two-step instructions: install deps → run record.js → run stitch.sh

Put all three in a single code block or zip for easy download.

---

## Additional references

- `references/puppeteer-patterns.md` — ready-to-use Puppeteer code for all three
  interaction patterns (scroll-through, click-demo, highlight-zoom), base script
  setup, local file loading, and debugging tips. Read when writing `record.js`.
