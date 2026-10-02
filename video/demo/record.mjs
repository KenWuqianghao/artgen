// Records the real artgen Studio for the demo video. Deterministic: Math.random is seeded,
// every action is scripted, and the time of each action is written to actions.json.
// Usage: node video/demo/record.mjs [url]   (serve the Studio first: python3 -m artgen studio serve)
import puppeteer from "puppeteer-core";
import { writeFileSync, mkdirSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const url = process.argv[2] || "http://127.0.0.1:8780/#seed=5150&works=14";
const chromeDir = join(homedir(), ".cache/puppeteer/chrome");
const build = readdirSync(chromeDir).filter((d) => d.startsWith("mac")).sort().pop();
const executablePath = join(chromeDir, build, "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing");

const W = 1280, H = 720;   // recorded at 1.5x density: a 1920x1080 video where the UI reads at 150%
mkdirSync(join(here, "raw"), { recursive: true });
const browser = await puppeteer.launch({ executablePath, headless: true, defaultViewport: { width: W, height: H, deviceScaleFactor: 1.5 },
  args: ["--hide-scrollbars", "--force-color-profile=srgb"] });
const page = await browser.newPage();
page.on("pageerror", (e) => console.log("pageerror:", e.message.slice(0, 300)));
page.on("console", (m) => { if (m.type() === "error") console.log("console:", m.text().slice(0, 200)); });

// seeded random + a visible cursor that follows real mouse events
await page.evaluateOnNewDocument(() => {
  let a = 20271;
  Math.random = () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  addEventListener("DOMContentLoaded", () => {
    const c = document.createElement("div");
    c.id = "__cursor";
    c.style.cssText = "position:fixed;left:0;top:0;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:rgba(20,20,20,.18);border:2px solid #141414;z-index:2147483647;pointer-events:none;transition:transform .12s;transform:translate(-100px,-100px)";
    document.body.appendChild(c);
    const move = (x, y) => { c.style.transform = `translate(${x}px,${y}px)`; };
    addEventListener("mousemove", (e) => move(e.clientX, e.clientY), true);
    addEventListener("mousedown", () => { c.style.background = "rgba(20,20,20,.45)"; }, true);
    addEventListener("mouseup", () => { c.style.background = "rgba(20,20,20,.18)"; }, true);
    window.__moveCursor = move;
  });
});

await page.goto(url, { waitUntil: "domcontentloaded", timeout: 120000 });
await page.waitForFunction(() => document.getElementById("boot").hidden === true, { timeout: 60000 });
await page.waitForFunction(() => /artists from/.test(document.getElementById("summary").textContent));
await new Promise((r) => setTimeout(r, 2500));       // let the first images load

let mouse = { x: W * 0.62, y: H * 0.55 };
const actions = [];
const recorder = await page.screencast({ path: join(here, "raw", "studio.mp4"), format: "mp4", scale: process.env.REC_SCALE ? Number(process.env.REC_SCALE) : 1, fps: 30 });
const t0 = Date.now();
const mark = (name) => { actions.push({ name, t: (Date.now() - t0) / 1000 }); console.log("mark", name, ((Date.now() - t0) / 1000).toFixed(2)); };
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

async function moveTo(x, y, steps = 18) {
  for (let i = 1; i <= steps; i++) {
    const k = i / steps, e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    const px = mouse.x + (x - mouse.x) * e, py = mouse.y + (y - mouse.y) * e;
    await page.mouse.move(px, py);
    await page.evaluate((a, b) => window.__moveCursor && window.__moveCursor(a, b), px, py);
    await wait(16);
  }
  mouse = { x, y };
}
async function box(selector, text) {
  const handle = text
    ? await page.evaluateHandle((s, t) => [...document.querySelectorAll(s)].find((el) => el.textContent.trim().startsWith(t) || el.textContent.includes(t)), selector, text)
    : await page.$(selector);
  const el = handle.asElement();
  if (!el) throw new Error(`not found: ${selector} ${text || ""}`);
  await el.evaluate((n) => n.scrollIntoView({ block: "center", behavior: "instant" }));
  await wait(120);
  return el.boundingBox();
}
async function click(selector, text, name) {
  const b = await box(selector, text);
  await moveTo(b.x + Math.min(b.width / 2, 60), b.y + b.height / 2);
  await wait(120);
  await page.mouse.down(); await wait(70); await page.mouse.up();
  mark(name || `click ${text || selector}`);
}
async function typeInto(selector, text, name) {
  const b = await box(selector);
  await moveTo(b.x + 40, b.y + b.height / 2);
  await page.mouse.click(b.x + 40, b.y + b.height / 2, { clickCount: 3 });
  mark(name);
  for (const ch of text) { await page.keyboard.type(ch); await wait(85); }
}
async function scrollPreview(dy, times, name) {
  await moveTo(W * 0.66, H * 0.62);
  mark(name);
  for (let i = 0; i < times; i++) { await page.mouse.wheel({ deltaY: dy }); await wait(60); }
}

await wait(700);
await click("#dice", null, "roll"); await wait(1100);
await click("#hosts .opt", "Lisbon", "city"); await wait(1100);
await click("#themes .opt", "Water and tides", "theme"); await wait(1100);
await click("#presets .preset", "No video, please", "forms"); await wait(900);
await click("#forms .chip", "Painting", "chip"); await wait(900);
await click('.seg[data-key="rediscovered"] button', "Many", "lineup"); await wait(900);
await click('.seg[data-key="jargon"] button', "Unbearable", "jargon"); await wait(900);
await click("#identities .swatch", "Brick", "identity"); await wait(1100);
await typeInto("#title", "Everything Is Water", "title"); await wait(1300);
await scrollPreview(110, 12, "scroll"); await wait(1300);
const tile = await page.evaluate(() => {
  const f = document.querySelector(".viewport iframe.front"); const r = f.getBoundingClientRect();
  const t = f.contentDocument.querySelector(".tile"); const b = t.getBoundingClientRect();
  return { x: r.x + b.x + b.width / 2, y: r.y + b.y + Math.min(b.height / 2, 140) };
});
await moveTo(tile.x, tile.y); await wait(150);
await page.mouse.click(tile.x, tile.y); mark("work"); await wait(1500);
await scrollPreview(80, 9, "work-scroll"); await wait(1900);
await click("#back", null, "back"); await wait(900);
await click("#surprise", null, "surprise"); await wait(3000);
mark("end");

await recorder.stop();
writeFileSync(join(here, "actions.json"), JSON.stringify(actions, null, 1));
await browser.close();
console.log(`recorded ${actions.length} actions, ${actions.at(-1).t.toFixed(1)} s`);
