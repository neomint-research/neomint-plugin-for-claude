# Puppeteer Capture Patterns

## Base script (all patterns share this setup)

```js
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const FRAMES_DIR = '/tmp/preview-frames';
const VIEWPORT = { width: 1080, height: 1920 };
const FRAME_INTERVAL_MS = 100; // 10 fps

if (!fs.existsSync(FRAMES_DIR)) fs.mkdirSync(FRAMES_DIR, { recursive: true });

let frameIndex = 0;
async function captureFrames(page, count) {
  for (let i = 0; i < count; i++) {
    const pad = String(frameIndex).padStart(4, '0');
    await page.screenshot({ path: path.join(FRAMES_DIR, `frame-${pad}.png`) });
    frameIndex++;
    await new Promise(r => setTimeout(r, FRAME_INTERVAL_MS));
  }
}

(async () => {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: VIEWPORT,
  });
  const page = await browser.newPage();

  // Force light mode (avoids dark-mode surprises)
  await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'light' }]);

  // --- INSERT PATTERN BELOW ---

  await browser.close();
})();
```

---

## Pattern 1: Click-demo

Replace the `--- INSERT PATTERN BELOW ---` section with:

```js
  await page.goto('https://your-url.com', { waitUntil: 'networkidle2' });
  await captureFrames(page, 30); // ~3s on landing page

  // Click sequence: [selector, frames_to_capture_after_click]
  const clicks = [
    ['nav a[href="/features"]', 40],
    ['button.show-demo',        30],
    ['.card:first-child',       25],
  ];

  for (const [selector, frames] of clicks) {
    await page.waitForSelector(selector, { timeout: 5000 }).catch(() => {
      console.warn(`Selector not found: ${selector} — skipping`);
    });
    await page.click(selector).catch(() => {});
    await page.waitForNetworkIdle({ idleTime: 500 }).catch(() => {});
    await captureFrames(page, frames);
  }
```

**Tip:** Adjust `frames` per click based on how long the animation/transition takes.
300ms transition → 3 frames at 10fps is enough; 1s transition → 10 frames.

---

## Pattern 2: Scroll-through

```js
  await page.goto('https://your-url.com', { waitUntil: 'networkidle2' });

  // Get total scroll height
  const scrollHeight = await page.evaluate(() => document.body.scrollHeight);
  const steps = 60; // total number of scroll steps
  const stepSize = scrollHeight / steps;

  for (let i = 0; i <= steps; i++) {
    await page.evaluate((y) => window.scrollTo({ top: y, behavior: 'instant' }), i * stepSize);
    await captureFrames(page, 3); // 3 frames per scroll step → smooth
  }
```

---

## Pattern 3: Highlight-zoom

```js
  await page.goto('https://your-url.com', { waitUntil: 'networkidle2' });
  await captureFrames(page, 20); // show full page first

  // Zoom into a specific element
  await page.evaluate((selector) => {
    const el = document.querySelector(selector);
    if (!el) return;
    el.style.transition = 'transform 0.5s ease';
    el.style.transform = 'scale(2)';
    el.style.transformOrigin = 'top left';
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, '.metric-card.highlight');

  await captureFrames(page, 30); // capture zoomed state

  // Zoom back out
  await page.evaluate((selector) => {
    const el = document.querySelector(selector);
    if (el) el.style.transform = 'scale(1)';
  }, '.metric-card.highlight');

  await captureFrames(page, 15);
```

---

## Local HTML file

Replace `page.goto(url)` with:

```js
  const filePath = path.resolve('./index.html');
  await page.goto(`file://${filePath}`, { waitUntil: 'load' });
```

If the HTML loads external assets (fonts, images) via relative paths, serve it locally:
```bash
npx serve . -p 3000
```
Then use `http://localhost:3000` as the URL.

---

## Debugging tips

```js
// Log browser console output
page.on('console', msg => console.log('[browser]', msg.text()));

// Log failed network requests
page.on('requestfailed', req => console.warn('[failed]', req.url()));

// Take a single debug screenshot
await page.screenshot({ path: '/tmp/debug.png', fullPage: true });
```
