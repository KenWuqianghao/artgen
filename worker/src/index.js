// artgen Studio backend: serves the static Studio and renders a few live images per visitor on the owner's OpenAI key.
//
//   GET  /api/status        how many free renders this visitor has left today
//   POST /api/render        {prompt} -> {url, cached, remaining}
//   GET  /api/image/<id>    a rendered JPEG
//
// It also runs the guessing game "Art or BS?" (rules in game.js). Every player answers the same photographs
// in the same order, in sets of ten, and climbs one all-time ladder:
//
//   GET  /api/game/state?player=     this player's standing, next photograph and current set
//   POST /api/game/answer            {player, index, guess} -> the truth about the next photograph
//   POST /api/game/name              {player, name} -> a row on the ladder, after the first set
//   GET  /api/game/ladder?player=    the top 50 named players; the player's own row has me: true
//
// Link previews for social posts:
//
//   GET  /s/<score>    a page with the preview card of a score from 0 to 10 for crawlers; it sends people on to /game
//   GET  /game         the game page, with its preview tags made absolute for the public host (PUBLIC_HOST)
//   GET  /studio       the Studio, because the public host shows the game at /
//
// One Durable Object holds the counters, the images and the game, so the daily limits are exact and nothing else needs provisioning.
import { DurableObject } from "cloudflare:workers";
import { LADDER_SHOWN, NAMES_PER_VISITOR, cleanName, crowdOf, currentSet, isGuess, isPlayer, isRight, moveInHist, onLadder,
  orderOf, playersIn, rankIn, setOneDone, unanswered } from "./game.js";
import pool from "./game_pool.json";

const ORDER = orderOf(pool);
const BY_IMG = new Map(ORDER.map((item) => [item.img, item]));

const PREFIX = "Installation view photograph from the press kit of an international contemporary art biennial. Room:";
const SUFFIX = "No watermark.";
const SAFE_SUFFIX = " All people depicted, painted or sculpted are fully clothed adults or children in everyday clothes; " +
  "nothing violent or graphic is shown.";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
});
const int = (v, d) => { const n = parseInt(v, 10); return Number.isFinite(n) ? n : d; };
const today = () => new Date().toISOString().slice(0, 10);

async function sha(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function decodeBase64(b64) {
  if (typeof Uint8Array.fromBase64 === "function") return Uint8Array.fromBase64(b64);
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function limits(env) {
  return { visitor: int(env.FREE_PER_VISITOR, 3), global: int(env.FREE_PER_DAY, 60) };
}

// Only the site itself may spend the owner's money: its own host, or the public host that proxies to it.
function allowedOrigin(request, env) {
  const origin = request.headers.get("origin");
  if (!origin) return false;
  try {
    const o = new URL(origin), here = new URL(request.url);
    return o.host === here.host || o.host === env.PUBLIC_HOST;
  } catch { return false; }
}

export class Store extends DurableObject {
  // Reserve one render for a visitor. Exact, because a Durable Object handles one call at a time.
  async reserve(visitor, day, perVisitor, perDay) {
    const vKey = `v:${day}:${visitor}`, gKey = `g:${day}`;
    const got = await this.ctx.storage.get([vKey, gKey]);
    const v = got.get(vKey) || 0, g = got.get(gKey) || 0;
    if (v >= perVisitor) return { ok: false, reason: "visitor", remaining: 0 };
    if (g >= perDay) return { ok: false, reason: "global", remaining: 0 };
    await this.ctx.storage.put({ [vKey]: v + 1, [gKey]: g + 1 });
    return { ok: true, remaining: Math.min(perVisitor - v - 1, perDay - g - 1) };
  }

  async refund(visitor, day) {
    const vKey = `v:${day}:${visitor}`, gKey = `g:${day}`;
    const got = await this.ctx.storage.get([vKey, gKey]);
    await this.ctx.storage.put({ [vKey]: Math.max(0, (got.get(vKey) || 0) - 1), [gKey]: Math.max(0, (got.get(gKey) || 0) - 1) });
  }

  async remaining(visitor, day, perVisitor, perDay) {
    const vKey = `v:${day}:${visitor}`, gKey = `g:${day}`;
    const got = await this.ctx.storage.get([vKey, gKey]);
    return Math.max(0, Math.min(perVisitor - (got.get(vKey) || 0), perDay - (got.get(gKey) || 0)));
  }

  async hasImage(id) { return (await this.ctx.storage.get(`i:${id}`)) !== undefined; }
  async putImage(id, bytes) { await this.ctx.storage.put(`i:${id}`, bytes); }
  async getImage(id) { return (await this.ctx.storage.get(`i:${id}`)) || null; }

  // Each method is one call, so its read-modify-write is exact.
  async gameState(player) {
    const key = `pl:${player}`;
    const got = await this.ctx.storage.get([key, "hist"]);
    const p = got.get(key) || newPlayer();
    const set = currentSet(p.answers);
    const stats = set.answers.length ? await this.ctx.storage.get(set.answers.map(([img]) => `gi:${img}`)) : new Map();
    return { p, hist: got.get("hist") || [], set, stats: set.answers.map(([img]) => stats.get(`gi:${img}`)) };
  }

  async gameAnswer(player, index, guess) {
    const key = `pl:${player}`;
    const got = await this.ctx.storage.get([key, "hist", "ladder"]);
    const p = got.get(key) || newPlayer();
    const left = unanswered(ORDER, p.answers);
    if (!left.length) return { refused: "finished" };
    if (index !== p.answers.length) return { refused: "stale" };
    const item = left[0], iKey = `gi:${item.img}`, right = isRight(item, guess);
    const stat = (await this.ctx.storage.get(iKey)) || { seen: 0, right: 0 };
    stat.seen += 1;
    if (right) stat.right += 1;
    const from = p.answers.length ? p.correct : null;
    p.answers.push([item.img, guess]);
    if (right) p.correct += 1;
    p.at = Date.now();
    const hist = moveInHist(got.get("hist") || [], from, p.correct);
    const puts = { [key]: p, [iKey]: stat, hist };
    if (p.name) puts.ladder = onLadder(got.get("ladder") || [], ladderEntry(player, p));
    await this.ctx.storage.put(puts);
    return { item, stat, p, hist, next: left[1] || null };
  }

  async gameName(player, name, visitor, day) {
    const key = `pl:${player}`, nKey = `gn:${day}:${visitor}`;
    const got = await this.ctx.storage.get([key, "hist", "ladder", nKey]);
    const p = got.get(key);
    if (!p || !setOneDone(p.answers.length, ORDER.length)) return { refused: "early" };
    if (p.name !== name) {
      const used = got.get(nKey) || 0;
      if (used >= NAMES_PER_VISITOR) return { refused: "limit" };
      p.name = name;
      await this.ctx.storage.put({ [key]: p, ladder: onLadder(got.get("ladder") || [], ladderEntry(player, p)), [nKey]: used + 1 });
    }
    return { rank: rankIn(got.get("hist") || [], p.correct) };
  }

  async gameLadder() {
    const got = await this.ctx.storage.get(["hist", "ladder"]);
    return { hist: got.get("hist") || [], ladder: got.get("ladder") || [] };
  }

  // Yesterday's counters are dead weight; drop them once a day. The keys of the old daily game go too.
  async sweep(day) {
    const last = await this.ctx.storage.get("swept");
    if (last === day) return;
    const drop = async (options) => {
      for (;;) {
        const old = await this.ctx.storage.list({ ...options, limit: 1000 });
        if (!old.size) break;
        const dead = [...old.keys()];
        for (let i = 0; i < dead.length; i += 128) await this.ctx.storage.delete(dead.slice(i, i + 128));
      }
    };
    for (const prefix of ["v:", "g:", "gn:"]) await drop({ prefix, end: `${prefix}${day}` });
    for (const prefix of ["gp:", "gl:", "gs:"]) await drop({ prefix });
    await this.ctx.storage.put("swept", day);
  }
}

const newPlayer = () => ({ start: Date.now(), answers: [], correct: 0, name: null, at: null });
const ladderEntry = (player, p) => ({ player, name: p.name, correct: p.correct, answered: p.answers.length, at: p.at });

async function visitorId(request, env) {
  // Behind the Vercel proxy every request comes from a Vercel address; Vercel puts the player's address here.
  const ip = request.headers.get("x-vercel-proxied-for") || request.headers.get("cf-connecting-ip") || "local";
  return (await sha(`${env.VISITOR_SALT || "artgen"}:${ip}`)).slice(0, 24);
}

async function generate(env, prompt) {
  const base = (env.OPENAI_BASE || "https://api.openai.com").replace(/\/$/, "");
  const body = {
    model: env.OPENAI_MODEL || "gpt-image-2.5-flare", prompt, size: "1536x1024", quality: env.OPENAI_QUALITY || "medium",
    n: 1, output_format: "jpeg", output_compression: 82,
  };
  for (let attempt = 0; attempt < 2; attempt++) {
    const res = await fetch(`${base}/v1/images/generations`, {
      method: "POST",
      headers: { authorization: `Bearer ${env.OPENAI_API_KEY}`, "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      const data = await res.json();
      const b64 = data && data.data && data.data[0] && data.data[0].b64_json;
      if (!b64) throw Object.assign(new Error("The image model returned no image."), { status: 502 });
      return decodeBase64(b64);
    }
    const text = (await res.text()).slice(0, 400);
    if (res.status === 400 && /moderation|safety/i.test(text) && attempt === 0) { body.prompt = prompt + SAFE_SUFFIX; continue; }
    if (res.status === 400 && /moderation|safety/i.test(text)) throw Object.assign(new Error("The image model refused this work."), { status: 422 });
    if (res.status === 429) throw Object.assign(new Error("The image model is busy. Try again in a minute."), { status: 503 });
    console.log("openai error", res.status, text);
    throw Object.assign(new Error("The image model failed."), { status: 502 });
  }
}

async function render(request, env) {
  if (!allowedOrigin(request, env)) return json({ error: "Open the Studio to render." }, 403);
  if (!env.OPENAI_API_KEY) return json({ error: "Free renders are not set up on this Studio.", reason: "disabled" }, 503);
  let prompt;
  try { prompt = String((await request.json()).prompt || ""); } catch { return json({ error: "Bad request." }, 400); }
  // The Studio only ever sends artgen's own installation-view prompts; refuse anything else.
  if (prompt.length < 400 || prompt.length > 2400 || !prompt.startsWith(PREFIX) || !prompt.endsWith(SUFFIX)) {
    return json({ error: "This is not an artgen work." }, 400);
  }
  const lim = limits(env), day = today(), visitor = await visitorId(request, env);
  const store = env.STORE.get(env.STORE.idFromName("main"));
  const id = (await sha(`${env.OPENAI_MODEL || "gpt-image-2.5-flare"}\n${prompt}`)).slice(0, 32);
  const url = `/api/image/${id}.jpg`;
  if (await store.hasImage(id)) {      // somebody already rendered this exact work: free
    return json({ url, cached: true, remaining: await store.remaining(visitor, day, lim.visitor, lim.global), limit: lim.visitor });
  }
  const slot = await store.reserve(visitor, day, lim.visitor, lim.global);
  if (!slot.ok) {
    return json({
      error: slot.reason === "visitor" ? `You used your ${lim.visitor} free renders for today.` : "Today's free renders are all used.",
      reason: slot.reason, remaining: 0, limit: lim.visitor,
    }, 429);
  }
  try {
    const bytes = await generate(env, prompt);
    await store.putImage(id, bytes);
  } catch (err) {
    await store.refund(visitor, day);
    return json({ error: err.message || "The render failed.", remaining: slot.remaining + 1, limit: lim.visitor }, err.status || 502);
  }
  return json({ url, cached: false, remaining: slot.remaining, limit: lim.visitor });
}

// Photographs come straight from the Worker's own host, so they do not use the proxy's transfer allowance.
const imageUrl = (origin, item) => (item ? `${origin}/game/media/${item.img}.jpg` : null);

// A photograph can leave the pool after a player answered it; its truth is then unknown.
function answerView(origin, [img, guess], stat) {
  const item = BY_IMG.get(img);
  if (!item) return { guess, image: null, real: null, reveal: null, crowd: null };
  return { guess, image: imageUrl(origin, item), real: item.real, reveal: item.reveal, crowd: crowdOf(stat) };
}

const standing = (p, hist) => ({
  answered: p.answers.length, correct: p.correct, rank: p.answers.length ? rankIn(hist, p.correct) : null, players: playersIn(hist),
});

const GAME = {
  "GET state": async ({ url, store }) => {
    const player = url.searchParams.get("player");
    if (!isPlayer(player)) return json({ error: "Bad player token." }, 400);
    const { p, hist, set, stats } = await store.gameState(player);
    const left = unanswered(ORDER, p.answers);
    return json({
      total: p.answers.length + left.length, ...standing(p, hist), name: p.name, next: imageUrl(url.origin, left[0]),
      set: { number: set.number, answers: set.answers.map((a, i) => answerView(url.origin, a, stats[i])) },
    });
  },
  "POST answer": async ({ url, body, store }) => {
    if (!isPlayer(body.player)) return json({ error: "Bad player token." }, 400);
    if (!isGuess(body.guess)) return json({ error: "A guess is \"real\" or \"ai\"." }, 400);
    if (!Number.isInteger(body.index)) return json({ error: "Bad answer index." }, 400);
    const res = await store.gameAnswer(body.player, body.index, body.guess);
    if (res.refused === "stale") return json({ error: "Your answer to that photograph is already saved." }, 409);
    if (res.refused === "finished") return json({ error: "You answered every photograph." }, 409);
    const { real, reveal, crowd } = answerView(url.origin, [res.item.img, body.guess], res.stat);
    return json({ index: body.index, real, reveal, crowd, ...standing(res.p, res.hist), next: imageUrl(url.origin, res.next) });
  },
  "POST name": async ({ request, env, body, store, day }) => {
    if (!isPlayer(body.player)) return json({ error: "Bad player token." }, 400);
    const name = cleanName(body.name);
    if (!name) return json({ error: "A name has 1 to 20 characters." }, 400);
    const res = await store.gameName(body.player, name, await visitorId(request, env), day);
    if (res.refused === "early") return json({ error: "Finish the first set to go on the ladder." }, 409);
    if (res.refused === "limit") return json({ error: "Too many names from this address today." }, 429);
    return json({ rank: res.rank, name });
  },
  "GET ladder": async ({ url, store }) => {
    const player = url.searchParams.get("player");
    const { hist, ladder } = await store.gameLadder();
    return json({
      players: playersIn(hist),
      entries: ladder.slice(0, LADDER_SHOWN).map((e) => ({
        rank: rankIn(hist, e.correct), name: e.name, correct: e.correct, answered: e.answered, ...(e.player === player && { me: true }),
      })),
    });
  },
};

const SHARE_HOOK = { 0: "Every room fooled me.", 10: "Called it every time." };

// Links that people see and share name the public host; the Worker's own host serves it behind the proxy.
const siteOf = (env, url) => (env.PUBLIC_HOST ? `https://${env.PUBLIC_HOST}` : url.origin);

function sharePage(url, env) {
  const m = url.pathname.match(/^\/s\/(10|\d)$/);
  if (!m) return new Response(null, { status: 302, headers: { location: "/game" } });
  const site = siteOf(env, url), score = Number(m[1]), here = `${site}/s/${score}`, image = `${site}/share/${score}.jpg`;
  const title = `I scored ${score}/10 on Art or BS?`;
  const text = `${SHARE_HOOK[score] || ""} Some rooms are real art. AI made the rest. Can you call BS?`.trim();
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${title}</title>
<meta name="description" content="${text}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Art or BS?">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${text}">
<meta property="og:url" content="${here}">
<meta property="og:image" content="${image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="${image}">
<meta http-equiv="refresh" content="0; url=/game">
</head>
<body><a href="/game">Play Art or BS?</a></body>
</html>
`;
  return new Response(html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=3600" } });
}

// Crawlers need absolute image addresses, and the static page does not know its host.
function absoluteTags(page, origin) {
  return new HTMLRewriter().on('meta[content^="/"]', {
    element(e) { e.setAttribute("content", origin + e.getAttribute("content")); },
  }).transform(page);
}

async function game(request, env, ctx, url) {
  const handler = GAME[`${request.method} ${url.pathname.slice("/api/game/".length)}`];
  if (!handler) return json({ error: "Not found." }, 404);
  if (request.method === "POST" && !allowedOrigin(request, env)) return json({ error: "Open the game to play." }, 403);
  if (!ORDER.length) return json({ error: "The game is not open yet. It has no photographs." }, 503);
  const day = today();
  let body = null;
  if (request.method === "POST") {
    try { body = await request.json(); } catch { body = null; }
    if (!body || typeof body !== "object") return json({ error: "Bad request." }, 400);
  }
  const store = env.STORE.get(env.STORE.idFromName("main"));
  ctx.waitUntil(store.sweep(day));
  return handler({ request, env, url, body, store, day });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/game/")) return game(request, env, ctx, url);
    if (url.pathname.startsWith("/s/")) return sharePage(url, env);
    if (url.pathname === "/game") return absoluteTags(await env.ASSETS.fetch(request), siteOf(env, url));
    if (url.pathname === "/studio") return env.ASSETS.fetch(new Request(new URL("/", url), request));
    if (url.pathname === "/api/status" && request.method === "GET") {
      const lim = limits(env), day = today();
      if (!env.OPENAI_API_KEY) return json({ enabled: false, remaining: 0, limit: lim.visitor });
      const store = env.STORE.get(env.STORE.idFromName("main"));
      ctx.waitUntil(store.sweep(day));
      return json({ enabled: true, remaining: await store.remaining(await visitorId(request, env), day, lim.visitor, lim.global),
                    limit: lim.visitor, model: env.OPENAI_MODEL || "gpt-image-2.5-flare" });
    }
    if (url.pathname === "/api/render" && request.method === "POST") return render(request, env);
    const m = url.pathname.match(/^\/api\/image\/([0-9a-f]{32})\.jpg$/);
    if (m && request.method === "GET") {
      const bytes = await env.STORE.get(env.STORE.idFromName("main")).getImage(m[1]);
      if (!bytes) return new Response("Not found", { status: 404 });
      return new Response(bytes, { headers: { "content-type": "image/jpeg", "cache-control": "public, max-age=31536000, immutable" } });
    }
    if (url.pathname.startsWith("/api/")) return json({ error: "Not found." }, 404);
    return env.ASSETS.fetch(request);
  },
};
