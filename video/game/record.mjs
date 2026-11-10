// Records one set of "Art or BS?" for the game video. Deterministic: the player and the answers come from
// config.json, every action is scripted, and the time of each action is written to recording.json with the
// text that "Post on X" would post.
// Every player gets the photographs in the same order, so the video records a late set (config "set"):
// a fresh player answers the sets before it through the API first, off camera.
// Usage: node video/game/record.mjs   (build.sh starts the local Worker on PORT first)
// The configured host resolves to the local Worker, so the page and its share text show the real address.
import puppeteer from "puppeteer-core";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { orderOf, SET_SIZE } from "../../worker/src/game.js";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "../..");
const config = JSON.parse(readFileSync(join(here, "config.json"), "utf8"));
const host = config.url.split("/")[0];
const port = process.env.PORT || "8812";
const executablePath = process.env.CHROME || join(homedir(), ".cache/ms-playwright/chromium-1248/chrome-linux64/chrome");

const order = orderOf(JSON.parse(readFileSync(join(root, "worker/src/game_pool.json"), "utf8")));
// the same answers are wrong in every set: config "wrong" lists positions in a set
const guessAt = (i) => (order[i].real !== config.wrong.includes(i % SET_SIZE) ? "real" : "ai");
const first = (config.set - 1) * SET_SIZE;
if (first + SET_SIZE > order.length) throw new Error(`set ${config.set} is not a full set of the ${order.length} photographs`);
const player = "video-" + "0".repeat(10) + config.set;

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

  // off camera: the player answers the sets before the recorded set, from the page's own origin
  await page.goto(`https://${host}/game`, { waitUntil: "networkidle0", timeout: 120000 });
  const answered = await page.evaluate(async (player, guesses) => {
    localStorage.setItem("artgen-game-player", player);
    for (let index = 0; index < guesses.length; index++) {
      const res = await fetch("/api/game/answer", { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ player, index, guess: guesses[index] }) });
      if (res.status !== 200) throw new Error(`answer ${index}: ${res.status} ${await res.text()}`);
    }
    return (await (await fetch("/api/game/state?player=" + player)).json()).answered;
  }, player, Array.from({ length: first }, (_, i) => guessAt(i)));
  if (answered !== first) throw new Error(`the player has ${answered} answers, not ${first}`);

  // the page opens on the checkpoint of the set before; "Next set" starts the recorded set
  const state = (s) => page.waitForFunction((v) => document.getElementById("game").dataset.state === v, {}, s);
  await page.reload({ waitUntil: "networkidle0" });
  if (first > 0) { await state("checkpoint"); await page.click("#next-set"); }
  await state("playing");
  await page.waitForFunction(() => document.getElementById("photo").complete);
  await page.evaluate(() => document.fonts.ready);
  // a real player never sees the X intent open in this recording; the post text is read from the link instead
  await page.evaluate(() => document.getElementById("post").addEventListener("click", (e) => e.preventDefault()));

  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  let mouse = { x: W * 0.5, y: H * 0.45 };
  const actions = [];
  // The video starts at the first screencast frame, which comes later than the call returns; its wall-clock
  // timestamp is the zero of the action times, so the actions line up with the video.
  let start = null;
  page.mainFrame().client.on("Page.screencastFrame", (e) => { if (start === null && e.metadata.timestamp) start = e.metadata.timestamp; });
  const recorder = await page.screencast({ path: join(here, "raw", "game.mp4"), format: "mp4", fps: 30 });
  const called = Date.now() / 1000;
  const mark = (name) => { actions.push({ name, at: Date.now() / 1000 }); console.log("mark", name); };

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

  await wait(600);
  for (let i = 0; i < SET_SIZE; i++) {
    const slow = i < 2;
    await page.waitForFunction(() => document.getElementById("photo").complete);
    await scrollTo("#guess-real", "end");
    if (slow) await wait(700);
    await tap(guessAt(first + i) === "real" ? "#guess-real" : "#guess-ai", `answer${i}`, slow ? 14 : 6);
    await state("revealed");
    await wait(slow ? 350 : 120);
    await scrollTo("#next", "end");
    if (slow) { mark(`label${i}`); await wait(2000); }
    await tap("#next", `next${i}`, slow ? 14 : 6);
    await wait(slow ? 250 : 100);
  }
  await state("checkpoint");
  await page.waitForFunction(() => / players? · /.test(document.getElementById("score-line").textContent));
  mark("result");
  await wait(1600);
  if (await page.$eval("#post", (n) => n.getBoundingClientRect().bottom > innerHeight)) await scrollTo("#post", "center");
  await tap("#post", "post");
  await wait(900);
  mark("end");
  await recorder.stop();
  if (start === null) throw new Error("no screencast frame arrived");
  console.log(`first frame ${(start - called).toFixed(3)} s after the screencast call`);
  for (const a of actions) { a.t = +(a.at - start).toFixed(3); delete a.at; }

  const share = await page.$eval("#post", (a) => new URL(a.href).searchParams.get("text"));
  const score = await page.$eval("#score", (n) => n.textContent);
  const scoreLine = await page.$eval("#score-line", (n) => n.textContent);
  const items = order.slice(first, first + SET_SIZE);
  writeFileSync(join(here, "recording.json"), JSON.stringify({ set: config.set, positions: [first + 1, first + SET_SIZE], score, scoreLine, share,
    real: items.map((i) => i.real), guesses: items.map((_, k) => guessAt(first + k)), actions }, null, 1) + "\n");
  console.log(`recorded set ${config.set} (positions ${first + 1}-${first + SET_SIZE}): ${score}, ${scoreLine}, ${actions.length} actions, ${actions.at(-1).t.toFixed(1)} s`);
} finally {
  await browser.close();
}
