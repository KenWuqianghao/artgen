export const SET_SIZE = 10;
export const LADDER_SHOWN = 50;
const LADDER_KEPT = 100;
export const NAMES_PER_VISITOR = 20;
const CROWD_MIN = 5;

export const isPlayer = (text) => typeof text === "string" && /^[A-Za-z0-9_-]{16,64}$/.test(text);
export const isGuess = (text) => text === "real" || text === "ai";
export const isRight = (item, guess) => (guess === "real") === item.real;

export function cleanName(raw) {
  if (typeof raw !== "string") return null;
  const name = raw.replace(/\s+/g, " ").replace(/[\p{Cc}\p{Cf}<>]/gu, "").replace(/ +/g, " ").trim();
  const length = [...name].length;
  return length >= 1 && length <= 20 ? name : null;
}

// One order for every player, by image name. The name is an HMAC, so the order looks random,
// and a new photograph takes its own place without moving the others.
export function orderOf(pool) {
  const tag = (kind) => pool[kind].map((e) => ({ img: e.img, real: kind === "real", reveal: e.reveal }));
  return [...tag("real"), ...tag("ai")].sort((a, b) => (a.img < b.img ? -1 : 1));
}

// answers: [[img, guess], ...] in the order the player gave them
export function unanswered(order, answers) {
  const seen = new Set(answers.map(([img]) => img));
  return order.filter((item) => !seen.has(item.img));
}

// The set that holds the last answer; set 1 before the first answer.
export function currentSet(answers) {
  const number = Math.max(1, Math.ceil(answers.length / SET_SIZE));
  return { number, answers: answers.slice((number - 1) * SET_SIZE) };
}

export const setOneDone = (answered, total) => answered >= Math.min(SET_SIZE, total);

// hist[c] is the number of players with c correct answers. A player counts from the first answer (from = null).
export function moveInHist(hist, from, to) {
  const next = hist.slice();
  while (next.length <= to) next.push(0);
  if (from !== null) next[from] -= 1;
  next[to] += 1;
  return next;
}

export const playersIn = (hist) => hist.reduce((a, b) => a + b, 0);

// Players with the same number correct share a rank.
export function rankIn(hist, correct) {
  let above = 0;
  for (let c = correct + 1; c < hist.length; c++) above += hist[c];
  return above + 1;
}

// The stored ladder: named players, most correct first, then fewer answers, then the earlier last answer.
export function onLadder(ladder, entry) {
  return [...ladder.filter((e) => e.player !== entry.player), entry]
    .sort((a, b) => b.correct - a.correct || a.answered - b.answered || a.at - b.at)
    .slice(0, LADDER_KEPT);
}

export function crowdOf(stat) {
  return stat && stat.seen >= CROWD_MIN ? Math.round((100 * stat.right) / stat.seen) : null;
}
