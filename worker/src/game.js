// "Real or artgen?": the rules of the daily round. Pure functions, no Cloudflare, so node can run them.

const FIRST_DAY = "2026-10-06";
const PER_KIND = 6;
const ROUND_SIZE = 10;
export const BOARD_SIZE = 100;
export const NAMES_PER_VISITOR = 20;
const CROWD_MIN = 5;

export const isDay = (text) => /^\d{4}-\d{2}-\d{2}$/.test(text) && !Number.isNaN(Date.parse(text));
export const isPlayer = (text) => typeof text === "string" && /^[A-Za-z0-9_-]{16,64}$/.test(text);
export const isGuess = (text) => text === "real" || text === "ai";

export const roundNumber = (day) => Math.round((Date.parse(day) - Date.parse(FIRST_DAY)) / 86400000) + 1;

// A leaderboard name: plain text, one line, 1 to 20 characters. Returns null for a name that cannot be used.
export function cleanName(raw) {
  if (typeof raw !== "string") return null;
  const name = raw.replace(/\s+/g, " ").replace(/[\p{Cc}\p{Cf}<>]/gu, "").replace(/ +/g, " ").trim();
  const length = [...name].length;
  return length >= 1 && length <= 20 ? name : null;
}

function seeded(text) {
  let h = 2166136261;
  for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 16777619);
  let a = h >>> 0;
  return () => {          // mulberry32
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffled(list, random) {
  const out = list.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

// The round of one UTC day: [{img, real, reveal}] x 10, or null when the pool is too small or the day is before the first round.
// An epoch walks through each shuffled list six at a time, so no image comes back before the epoch ends.
// Two of the twelve are then dropped, so a player cannot count on five of each.
export function roundFor(pool, day) {
  const number = roundNumber(day);
  const perEpoch = Math.floor(Math.min(pool.real.length, pool.ai.length) / PER_KIND);
  if (perEpoch < 1 || number < 1) return null;
  const epoch = Math.floor((number - 1) / perEpoch), slot = (number - 1) % perEpoch;
  const six = (kind) => shuffled(pool[kind], seeded(`epoch:${epoch}:${kind}`))
    .slice(slot * PER_KIND, (slot + 1) * PER_KIND)
    .map((e) => ({ img: e.img, real: kind === "real", reveal: e.reveal }));
  const items = shuffled([...six("real"), ...six("ai")], seeded(`day:${day}`)).slice(0, ROUND_SIZE);
  return { number, items };
}

export const isRight = (item, guess) => (guess === "real") === item.real;
export const scoreOf = (items, guesses) => guesses.filter((g, i) => isRight(items[i], g)).length;

// Percent of all players who got an image right; null until enough players saw it.
export function crowdOf(stat) {
  return stat && stat.seen >= CROWD_MIN ? Math.round((100 * stat.right) / stat.seen) : null;
}
