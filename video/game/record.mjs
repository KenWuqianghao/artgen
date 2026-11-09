// Records one full round of "Art or Artifice?" for the game video. Deterministic: the answers come from
// config.json ("wrong" lists the photographs to miss), every action is scripted, and the time of each
// action is written to recording.json with the text that "Post on X" would post.
// Usage: node video/game/record.mjs   (build.sh starts the local Worker on PORT first)
// The configured host resolves to the local Worker, so the page and its share text show the real address.
import puppeteer from "puppeteer-core";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { roundFor } from "../../worker/src/game.js";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "../..");
const config = JSON.parse(readFileSync(join(here, "config.json"), "utf8"));
const host = config.url.split("/")[0];
const port = process.env.PORT || "8812";
const executablePath = process.env.CHROME || join(homedir(), ".cache/ms-playwright/chromium-1248/chrome-linux64/chrome");

const day = new Date().toISOString().slice(0, 10);
const round = roundFor(JSON.parse(readFileSync(join(root, "worker/src/game_pool.json"), "utf8")), day);
const guesses = round.items.map((item, i) => (item.real !== config.wrong.includes(i) ? "real" : "ai"));

// Phone layout at 2x density: a 1080x1080 recording. Headless Chrome sends screencast frames at the
// density of the screen, not of the emulated viewport, so the density is a launch flag.
const W = 540, H = 540;
mkdirSync(join(here, "raw"), { recursive: true });
const browser = await puppeteer.launch({ executablePath, headless: true, defaultViewport: null,
  args: ["--force-device-scale-factor=2", `--window-size=${W},${H + 200}`, "--hide-scrollbars", "--force-color-profile=srgb",
    "--ignore-certificate-errors", `--host-resolver-rules=MAP ${host} 127.0.0.1:${port}`] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H, deviceScaleFactor: 0 });
  page.on("pageerror", (e) => console.log("pageerror:", e.message.slice(0, 300)));
  page.on("console", (m) => { if (m.type() === "error") console.log("console:", m.text().slice(0, 200)); });

  // a visible finger: a dot that follows the mouse and a ring on every tap
  await page.evaluateOnNewDocument(() => {
    addEventListener("DOMContentLoaded", () => {
      const css = document.createElement("style");
      css.textContent = "#__dot{position:fixed;left:0;top:0;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;background:rgba(20,20,20,.22);border:2px solid #141414;z-index:2147483647;pointer-events:none;transform:translate(-100px,-100px)}" +
        ".__ring{position:fixed;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:3px solid #141414;z-index:2147483646;pointer-events:none;animation:__ring .45s ease-out forwards}" +
        "@keyframes __ring{to{transform:scale(2.6);opacity:0}}";
      document.head.appendChild(css);
      const dot = document.createElement("div");
      dot.id = "__dot";
      document.body.appendChild(dot);
      addEventListener("mousemove", (e) => { dot.style.transform = `translate(${e.clientX}px,${e.clientY}px)`; }, true);
      addEventListener("mousedown", (e) => {
        const ring = document.createElement("div");
        ring.className = "__ring";
        ring.style.left = e.clientX + "px"; ring.style.top = e.clientY + "px";
        document.body.appendChild(ring);
        setTimeout(() => ring.remove(), 600);
      }, true);
    });
  });

  await page.goto(`https://${host}/game`, { waitUntil: "networkidle0", timeout: 120000 });
  await page.waitForFunction(() => document.getElementById("game").dataset.state === "playing" && document.getElementById("photo").complete);
  await page.evaluate(() => document.fonts.ready);
  // a real player never sees the X intent open in this recording; the post text is read from the link instead
  await page.evaluate(() => document.getElementById("post").addEventListener("click", (e) => e.preventDefault()));

  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  let mouse = { x: W * 0.5, y: H * 0.45 };
  const actions = [];
  const recorder = await page.screencast({ path: join(here, "raw", "game.mp4"), format: "mp4", fps: 30 });
  const t0 = Date.now();
  const mark = (name) => { actions.push({ name, t: (Date.now() - t0) / 1000 }); console.log("mark", name, ((Date.now() - t0) / 1000).toFixed(2)); };

  async function moveTo(x, y, steps = 14) {
    for (let i = 1; i <= steps; i++) {
      const k = i / steps, e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      await page.mouse.move(mouse.x + (x - mouse.x) * e, mouse.y + (y - mouse.y) * e);
      await wait(16);
    }
    mouse = { x, y };
  }
  async function scrollTo(selector, block) {
    await page.evaluate((s, b) => document.querySelector(s).scrollIntoView({ block: b, behavior: "smooth" }), selector, block);
    await wait(450);
  }
  async function tap(selector, name, steps) {
    const b = await page.$eval(selector, (n) => { const r = n.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height }; });
    await moveTo(b.x + b.w / 2, b.y + b.h / 2, steps);
    await wait(90);
    await page.mouse.down(); mark(name); await wait(70); await page.mouse.up();
  }
  const state = (s) => page.waitForFunction((v) => document.getElementById("game").dataset.state === v, {}, s);

  await wait(600);
  for (let i = 0; i < guesses.length; i++) {
    const slow = i < 2;
    await page.waitForFunction(() => document.getElementById("photo").complete);
    await scrollTo("#guess-real", "end");
    if (slow) await wait(700);
    await tap(guesses[i] === "real" ? "#guess-real" : "#guess-ai", `answer${i}`, slow ? 14 : 6);
    await state("revealed");
    await wait(slow ? 350 : 120);
    await scrollTo("#next", "end");
    if (slow) { mark(`label${i}`); await wait(2000); }
    await tap("#next", `next${i}`, slow ? 14 : 6);
    await wait(slow ? 250 : 100);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await state("finished");
  await page.waitForFunction(() => /average/.test(document.getElementById("score-line").textContent));
  mark("result");
  await wait(1800);
  await tap("#post", "post");
  await wait(900);
  mark("end");
  await recorder.stop();

  const share = await page.$eval("#post", (a) => new URL(a.href).searchParams.get("text"));
  const score = await page.$eval("#score", (n) => n.textContent);
  writeFileSync(join(here, "recording.json"), JSON.stringify({ day, number: round.number, score, share, real: round.items.map((i) => i.real), guesses, actions }, null, 1) + "\n");
  console.log(`recorded round ${round.number} (${day}): ${score}, ${actions.length} actions, ${actions.at(-1).t.toFixed(1)} s`);
} finally {
  await browser.close();
}
