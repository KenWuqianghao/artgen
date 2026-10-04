// artgen Studio backend: serves the static Studio and renders a few live images per visitor on the owner's OpenAI key.
//
//   GET  /api/status        how many free renders this visitor has left today
//   POST /api/render        {prompt} -> {url, cached, remaining}
//   GET  /api/image/<id>    a rendered JPEG
//
// One Durable Object holds the counters and the images, so the daily limits are exact and nothing else needs provisioning.
import { DurableObject } from "cloudflare:workers";

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

  // Yesterday's counters are dead weight; drop them once a day.
  async sweep(day) {
    const last = await this.ctx.storage.get("swept");
    if (last === day) return;
    for (const prefix of ["v:", "g:"]) {
      const old = await this.ctx.storage.list({ prefix, limit: 1000 });
      const dead = [...old.keys()].filter((k) => !k.startsWith(`${prefix}${day}`));
      for (let i = 0; i < dead.length; i += 128) await this.ctx.storage.delete(dead.slice(i, i + 128));
    }
    await this.ctx.storage.put("swept", day);
  }
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

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
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
