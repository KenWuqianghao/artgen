// artgen Studio backend: serves the static Studio and renders a few live images per visitor on the owner's OpenAI key.
//
//   GET  /api/status        how many free renders this visitor has left today
//   POST /api/render        {prompt} -> {url, cached, remaining}
//   GET  /api/image/<id>    a rendered JPEG
//
// It also runs the daily guessing game "Real or artgen?" (rules in game.js):
//
//   GET  /api/game/round?player=       today's ten images and this player's answers so far
//   POST /api/game/answer              {player, day, index, guess} -> the truth about the image at index
//   POST /api/game/name                {player, name} -> a row on today's leaderboard
//   GET  /api/game/leaderboard?day=    the top 50 of a day
//
// One Durable Object holds the counters, the images and the game, so the daily limits are exact and nothing else needs provisioning.
import { DurableObject } from "cloudflare:workers";
import { BOARD_SIZE, NAMES_PER_VISITOR, cleanName, crowdOf, isDay, isGuess, isPlayer, isRight, roundFor, roundNumber, scoreOf }
  from "./game.js";
import pool from "./game_pool.json";

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

// Only the Studio itself may spend the owner's money: same-origin requests, plus localhost for development.
function allowedOrigin(request) {
  const origin = request.headers.get("origin");
  if (!origin) return false;
  try {
    const o = new URL(origin), here = new URL(request.url);
    return o.host === here.host;
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
  async gameOpen(day, player, imgs) {
    const p = (await this.ctx.storage.get(`gp:${day}:${player}`)) || newPlayer();
    const seen = imgs.slice(0, p.guesses.length).map((img) => `gi:${img}`);
    const got = await this.ctx.storage.get([...seen, `gl:${day}`]);
    return { p, stats: seen.map((k) => got.get(k)), rank: rankOf(got.get(`gl:${day}`), player) };
  }

  async gameAnswer(day, player, index, guess, items) {
    const key = `gp:${day}:${player}`, sKey = `gs:${day}`;
    const p = (await this.ctx.storage.get(key)) || newPlayer();
    if (p.guesses.length >= items.length) return { refused: "finished" };
    if (index !== p.guesses.length) return { refused: "stale" };
    const iKey = `gi:${items[index].img}`;
    const got = await this.ctx.storage.get([iKey, sKey]);
    const stat = got.get(iKey) || { seen: 0, right: 0 };
    stat.seen += 1;
    if (isRight(items[index], guess)) stat.right += 1;
    p.guesses.push(guess);
    const puts = { [key]: p, [iKey]: stat };
    if (p.guesses.length === items.length) {
      p.doneMs = Date.now() - p.start;
      const sum = got.get(sKey) || { players: 0, scoreSum: 0 };
      puts[sKey] = { players: sum.players + 1, scoreSum: sum.scoreSum + scoreOf(items, p.guesses) };
    }
    await this.ctx.storage.put(puts);
    return { index, stat, p };
  }

  async gameName(day, player, name, visitor, items) {
    const key = `gp:${day}:${player}`, lKey = `gl:${day}`, nKey = `gn:${day}:${visitor}`;
    const got = await this.ctx.storage.get([key, lKey, nKey]);
    const p = got.get(key);
    if (!p || p.doneMs === null) return { refused: "unfinished" };
    let board = got.get(lKey) || [];
    if (p.name !== name) {
      const used = got.get(nKey) || 0;
      if (used >= NAMES_PER_VISITOR) return { refused: "limit" };
      p.name = name;
      board = board.filter((e) => e.player !== player);
      board.push({ player, name, score: scoreOf(items, p.guesses), ms: p.doneMs });
      board = board.sort((a, b) => b.score - a.score || a.ms - b.ms).slice(0, BOARD_SIZE);
      await this.ctx.storage.put({ [key]: p, [lKey]: board, [nKey]: used + 1 });
    }
    return { rank: rankOf(board, player) };
  }

  async gameBoard(day) {
    const got = await this.ctx.storage.get([`gl:${day}`, `gs:${day}`]);
    return { board: got.get(`gl:${day}`) || [], sum: got.get(`gs:${day}`) || { players: 0, scoreSum: 0 } };
  }

  // Yesterday's counters and rounds are dead weight; drop them once a day. Leaderboards and image statistics stay.
  async sweep(day) {
    const last = await this.ctx.storage.get("swept");
    if (last === day) return;
    for (const prefix of ["v:", "g:", "gp:", "gn:"]) {
      for (;;) {
        const old = await this.ctx.storage.list({ prefix, end: `${prefix}${day}`, limit: 1000 });
        if (!old.size) break;
        const dead = [...old.keys()];
        for (let i = 0; i < dead.length; i += 128) await this.ctx.storage.delete(dead.slice(i, i + 128));
      }
    }
    await this.ctx.storage.put("swept", day);
  }
}

const newPlayer = () => ({ start: Date.now(), guesses: [], doneMs: null, name: null });

function rankOf(board, player) {
  const at = (board || []).findIndex((e) => e.player === player);
  return at < 0 ? null : at + 1;
}

async function visitorId(request, env) {
  const ip = request.headers.get("cf-connecting-ip") || "local";
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
  if (!allowedOrigin(request)) return json({ error: "Open the Studio to render." }, 403);
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

const answerView = (item, guess, stat) => ({ guess, real: item.real, reveal: item.reveal, crowd: crowdOf(stat) });

const GAME = {
  "GET round": async ({ url, store, day, round }) => {
    const player = url.searchParams.get("player");
    if (!isPlayer(player)) return json({ error: "Bad player token." }, 400);
    const { p, stats, rank } = await store.gameOpen(day, player, round.items.map((i) => i.img));
    return json({
      day, number: round.number, images: round.items.map((i) => `/game/media/${i.img}.jpg`),
      answers: p.guesses.map((g, i) => answerView(round.items[i], g, stats[i])),
      done: p.doneMs !== null, score: scoreOf(round.items, p.guesses), ms: p.doneMs, name: p.name, rank,
    });
  },
  "POST answer": async ({ body, store, day, round }) => {
    if (!isPlayer(body.player)) return json({ error: "Bad player token." }, 400);
    if (!isGuess(body.guess)) return json({ error: "A guess is \"real\" or \"ai\"." }, 400);
    if (!Number.isInteger(body.index)) return json({ error: "Bad image index." }, 400);
    if (body.day !== day) return json({ error: "A new round began." }, 409);
    const items = round.items.map((i) => ({ img: i.img, real: i.real }));
    const res = await store.gameAnswer(day, body.player, body.index, body.guess, items);
    if (res.refused === "stale") return json({ error: "Your answer to that photograph is already saved." }, 409);
    if (res.refused === "finished") return json({ error: "You answered all ten images today." }, 409);
    const { real, reveal, crowd } = answerView(round.items[res.index], body.guess, res.stat);
    return json({
      index: res.index, real, reveal, crowd,
      done: res.p.doneMs !== null, score: scoreOf(round.items, res.p.guesses), ms: res.p.doneMs,
    });
  },
  "POST name": async ({ request, env, body, store, day, round }) => {
    if (!isPlayer(body.player)) return json({ error: "Bad player token." }, 400);
    const name = cleanName(body.name);
    if (!name) return json({ error: "A name has 1 to 20 characters." }, 400);
    const items = round.items.map((i) => ({ img: i.img, real: i.real }));
    const res = await store.gameName(day, body.player, name, await visitorId(request, env), items);
    if (res.refused === "unfinished") return json({ error: "Finish today's round first." }, 409);
    if (res.refused === "limit") return json({ error: "Too many names from this address today." }, 429);
    return json({ rank: res.rank, name });
  },
  "GET leaderboard": async ({ url, store, day: now }) => {
    const day = url.searchParams.get("day") || now;
    if (!isDay(day) || roundNumber(day) < 1) return json({ error: "No round on this day." }, 400);
    const { board, sum } = await store.gameBoard(day);
    return json({
      day, number: roundNumber(day), players: sum.players,
      average: sum.players ? Math.round((10 * sum.scoreSum) / sum.players) / 10 : null,
      entries: board.slice(0, BOARD_SIZE).map((e) => ({ name: e.name, score: e.score, ms: e.ms })),
    });
  },
};

async function game(request, env, ctx, url) {
  const handler = GAME[`${request.method} ${url.pathname.slice("/api/game/".length)}`];
  if (!handler) return json({ error: "Not found." }, 404);
  if (request.method === "POST" && !allowedOrigin(request)) return json({ error: "Open the game to play." }, 403);
  const day = today(), round = roundFor(pool, day);
  if (!round) return json({ error: "The game is not open yet. It needs at least six real photographs and six artgen images." }, 503);
  let body = null;
  if (request.method === "POST") {
    try { body = await request.json(); } catch { body = null; }
    if (!body || typeof body !== "object") return json({ error: "Bad request." }, 400);
  }
  const store = env.STORE.get(env.STORE.idFromName("main"));
  ctx.waitUntil(store.sweep(day));
  return handler({ request, env, url, body, store, day, round });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/game/")) return game(request, env, ctx, url);
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
