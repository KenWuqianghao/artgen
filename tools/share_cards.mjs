// Link preview cards for "Art or BS?": artgen/studio_static/share/<score>.jpg (0 to 10) and card.jpg,
// and the icon: artgen/studio_static/icon.svg, apple-touch-icon.png and icon-512.png.
// Run: node tools/share_cards.mjs   (needs Chrome: set CHROME, or install Chrome or Chromium)
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import puppeteer from "puppeteer-core";

const ROOT = new URL("..", import.meta.url).pathname;
const STATIC = join(ROOT, "artgen/studio_static");
const OUT = join(STATIC, "share");
const TOTAL = 10;

// Only artgen's own images: the real photographs in game/real/ belong to their artists.
const PHOTOS = {
  card: "festival-lights-v0-fd85c53f",
  0: "red-room-v0-6c999207",
  1: "hanging-stones-v0-f2a93d5b",
  2: "bronze-procession-v0-a36894e5",
  3: "glass-megaphones-v1-7c33b646",
  4: "greenhouse-pavilion-v0-65d6c48c",
  5: "flower-garlands-v1-15730a98",
  6: "ceremonial-suit-v0-cadac78d",
  7: "sonic-kinetic-v0-16cc27a2",
  8: "bricks-and-plants-v1-c575cebb",
  9: "woven-canopy-v1-ec2d0b2c",
  10: "altar-v1-d06ba2ec",
};

// A picture frame with a question mark. The frame is on a 4-unit grid, so at 16 px every edge is on a whole pixel.
const ICON = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect x="4" y="4" width="56" height="56" fill="#141414"/><rect x="12" y="12" width="40" height="40" fill="#fff"/>
<path d="M25 26c0-4.6 3.1-7.5 7-7.5s7 2.7 7 6.7c0 6.2-7 5.9-7 12" fill="none" stroke="#141414" stroke-width="6" stroke-linecap="round"/>
<circle cx="32" cy="45.5" r="3.7" fill="#141414"/>
</svg>
`;

const ROOMS = "Some rooms are real art. AI made the rest.";
const HOOK = {
  0: "Every room fooled me.<b>Can you call BS?</b>",
  10: "Called it every time.<b>Can you match it?</b>",
};

function chrome() {
  if (process.env.CHROME) return process.env.CHROME;
  for (const name of ["google-chrome", "chromium", "chromium-browser"]) {
    try { return execFileSync("which", [name], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim(); } catch {}
  }
  for (const [dir, sub] of [[".cache/ms-playwright", "chrome-linux64/chrome"], [".cache/puppeteer/chrome", "chrome-linux64/chrome"]]) {
    const base = join(homedir(), dir);
    if (!existsSync(base)) continue;
    for (const v of readdirSync(base).sort().reverse()) if (existsSync(join(base, v, sub))) return join(base, v, sub);
  }
  throw new Error("No Chrome found. Set CHROME to the path of a Chrome or Chromium binary.");
}

function photo(id) {
  const lib = JSON.parse(readFileSync(join(ROOT, "library/index.json"), "utf8")).entries;
  if (!lib.some((e) => e.id === id)) throw new Error(`${id} is not in library/index.json`);
  return "data:image/jpeg;base64," + readFileSync(join(ROOT, "library/media", `${id}.jpg`)).toString("base64");
}

const pips = (score) => Array.from({ length: TOTAL }, (_, i) => `<i class="${i < score ? "on" : ""}"></i>`).join("");

function page(key) {
  const text = key === "card"
    ? `<p class="ask">Art or BS?</p>
       <p class="hook">${ROOMS}<b>Can you call BS?</b></p>`
    : `<p class="kicker">Art or BS?</p>
       <p class="score">${key}<span>/${TOTAL}</span></p>
       <div class="pips">${pips(key)}</div>
       <p class="hook">${HOOK[key] || `${ROOMS}<b>Can you call BS?</b>`}</p>`;
  return `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@500;700&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=block">
<style>
  * { box-sizing: border-box; margin: 0; }
  body { width: 1200px; height: 630px; overflow: hidden; display: grid; grid-template-columns: 540px 660px;
    background: #fff; color: #141414; font-family: "Schibsted Grotesk", sans-serif; }
  .text { padding: 0 48px 0 56px; display: flex; flex-direction: column; justify-content: center; }
  img { width: 660px; height: 630px; object-fit: cover; display: block; }
  .kicker { font-size: 44px; font-weight: 700; letter-spacing: -.01em; }
  .score { font-family: "Newsreader", serif; font-weight: 500; font-size: 230px; line-height: .84; margin: 18px 0 30px -6px; letter-spacing: -.03em; }
  .score span { font-size: 110px; color: #8a8a86; letter-spacing: 0; }
  .ask { font-family: "Newsreader", serif; font-size: 150px; line-height: .9; margin: 0 0 36px -6px; letter-spacing: -.02em; }
  .pips { display: flex; gap: 8px; margin-bottom: 30px; }
  .pips i { width: 36px; height: 36px; border-radius: 4px; border: 3px solid #d6d6d1; }
  .pips i.on { background: #1f7a4d; border-color: #1f7a4d; }
  .hook { font-size: 34px; line-height: 1.22; color: #4a4a48; }
  .hook b { display: block; color: #141414; font-weight: 700; }
</style></head><body><div class="text">${text}</div><img src="${photo(PHOTOS[key])}"></body></html>`;
}

mkdirSync(OUT, { recursive: true });
const browser = await puppeteer.launch({ executablePath: chrome(), headless: true });
const tab = await browser.newPage();
await tab.setViewport({ width: 1200, height: 630 });
for (const key of Object.keys(PHOTOS)) {
  await tab.setContent(page(key), { waitUntil: "load" });
  await tab.evaluate(() => document.fonts.ready);
  const path = join(OUT, `${key}.jpg`);
  await tab.screenshot({ path, type: "jpeg", quality: 80 });
  console.log(`${path}  ${Math.round(statSync(path).size / 1024)} KB`);
}

writeFileSync(join(STATIC, "icon.svg"), ICON);
const mark = "data:image/svg+xml;base64," + Buffer.from(ICON).toString("base64");
for (const [name, size] of [["apple-touch-icon.png", 180], ["icon-512.png", 512]]) {
  await tab.setViewport({ width: size, height: size });
  // opaque, with room around the frame for the rounded corners that phones cut
  await tab.setContent(`<body style="margin:0;background:#fff;display:grid;place-items:center;height:100vh"><img src="${mark}" width="${Math.round(size * 0.8)}"></body>`, { waitUntil: "load" });
  const path = join(STATIC, name);
  await tab.screenshot({ path, type: "png" });
  console.log(`${path}  ${Math.round(statSync(path).size / 1024)} KB`);
}
await browser.close();
