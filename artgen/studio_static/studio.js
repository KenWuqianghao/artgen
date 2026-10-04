// artgen Studio: runs the real artgen Python package in the browser with Pyodide.
(function () {
  "use strict";

  var PYODIDE = "https://cdn.jsdelivr.net/npm/pyodide@314.0.7/";
  var APP = "/home/pyodide/app";
  var MIX = [["none", "None"], ["some", "Some"], ["many", "Many"]];
  var JARGON = [[1, "Plain"], [2, "Usual"], [3, "Unbearable"]];
  var JARGON_HINT = {
    1: "Essays describe the work and cite one theorist.",
    2: "Essays cite three theorists, with page numbers.",
    3: "Essays add a paragraph of stacked theory and two more footnotes.",
  };

  var defaults = { seed: 5150, works: 16, host: "", theme: "", title: "", forms: [],
                   rediscovered: "some", collectives: "some", emerging: "some", jargon: 2, identity: "" };
  var state = readHash();
  var py = null, studio = null, choices = null, result = null;
  var loadToken = 0, navStack = [], current = "page/index", timer = null;

  // live images: prompt -> image address. Free renders come from this site's own backend and are remembered;
  // renders made with the visitor's own key are blob addresses and live only as long as the tab.
  var MODEL = "gpt-image-2.5-flare";
  var SAFE = " All people depicted, painted or sculpted are fully clothed adults or children in everyday clothes; nothing violent or graphic is shown.";
  var live = loadLive(), api = { enabled: false, remaining: 0, limit: 0 }, userKey = "";
  var busy = {}, busyTick = null, batch = null, lastError = "";

  var $ = function (id) { return document.getElementById(id); };

  // ------------------------------------------------------------ state <-> URL
  function readHash() {
    var s = Object.assign({}, defaults);
    var q = new URLSearchParams(location.hash.slice(1));
    q.forEach(function (v, k) {
      if (!(k in s)) return;
      if (k === "forms") s.forms = v ? v.split(",") : [];
      else if (k === "seed" || k === "works" || k === "jargon") s[k] = parseInt(v, 10) || defaults[k];
      else s[k] = v;
    });
    return s;
  }
  function writeHash() {
    var q = new URLSearchParams();
    Object.keys(state).forEach(function (k) {
      var v = k === "forms" ? state.forms.join(",") : String(state[k]);
      if (v !== (k === "forms" ? defaults.forms.join(",") : String(defaults[k]))) q.set(k, v);
    });
    window.history.replaceState(null, "", "#" + q.toString());
  }

  // ------------------------------------------------------------ boot
  var STEPS = ["Fetching Python", "Unpacking the generator", "Hanging 76 kinds of work", "Writing the wall texts"];
  function step(i) {
    var ol = $("boot-steps");
    if (!ol.children.length) STEPS.forEach(function (t) { var li = document.createElement("li"); li.textContent = t; ol.appendChild(li); });
    for (var k = 0; k < ol.children.length; k++) ol.children[k].className = k < i ? "done" : "";
  }

  function loadScript(src) {
    return new Promise(function (ok, fail) {
      var s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = fail; document.head.appendChild(s);
    });
  }

  async function boot() {
    step(0);
    await loadScript(PYODIDE + "pyodide.js");
    py = await window.loadPyodide({ indexURL: PYODIDE });
    step(1);
    var bundle = await (await fetch("app.json")).json();
    Object.keys(bundle).forEach(function (rel) {
      var path = APP + "/" + rel;
      py.FS.mkdirTree(path.slice(0, path.lastIndexOf("/")));
      py.FS.writeFile(path, bundle[rel]);
    });
    step(2);
    py.runPython("import sys; sys.path.insert(0, '" + APP + "')");
    studio = py.pyimport("artgen.studio");
    choices = JSON.parse(studio.choices());
    await checkApi(true);
    buildControls();
    step(3);
    generate();
    $("boot").hidden = true;
  }

  // ------------------------------------------------------------ controls
  function option(name, sub, checked, onPick) {
    var b = document.createElement("button");
    b.type = "button"; b.className = "opt"; b.setAttribute("role", "radio"); b.setAttribute("aria-checked", checked);
    b.innerHTML = '<span class="dot"></span><span class="name"></span>' + (sub ? '<span class="sub"></span>' : "");
    b.querySelector(".name").textContent = name;
    if (sub) b.querySelector(".sub").textContent = sub;
    b.addEventListener("click", onPick);
    return b;
  }

  function radioList(el, items, key) {
    el.innerHTML = "";
    items.forEach(function (it) {
      el.appendChild(option(it.name, it.sub, state[key] === it.id, function () {
        state[key] = it.id; syncRadios(el, key, items); changed();
      }));
    });
  }
  function syncRadios(el, key, items) {
    Array.prototype.forEach.call(el.children, function (b, i) { b.setAttribute("aria-checked", state[key] === items[i].id); });
  }

  function seg(el, items, key) {
    el.innerHTML = "";
    items.forEach(function (it) {
      var b = document.createElement("button");
      b.type = "button"; b.textContent = it[1]; b.setAttribute("aria-pressed", state[key] === it[0]);
      b.addEventListener("click", function () {
        state[key] = it[0];
        Array.prototype.forEach.call(el.children, function (c, i) { c.setAttribute("aria-pressed", state[key] === items[i][0]); });
        if (key === "jargon") $("jargon-hint").textContent = JARGON_HINT[state.jargon];
        changed();
      });
      el.appendChild(b);
    });
  }

  var hostItems, themeItems;
  function buildControls() {
    $("seed").value = state.seed;
    $("works").value = state.works; $("works-out").textContent = state.works;
    $("title").value = state.title;

    hostItems = [{ id: "", name: "Let the seed decide", sub: "Any of the five host cities" }].concat(choices.hosts.map(function (h) {
      return { id: h.id, name: h.city + ", " + h.country, sub: h.venues.join(", ") };
    }));
    radioList($("hosts"), hostItems, "host");

    themeItems = [{ id: "", name: "Let the seed decide", sub: "One of seven metaphors" }].concat(choices.themes.map(function (t) {
      return { id: t.id, name: t.label, sub: "“" + t.titles[0] + "”, “" + t.titles[1] + "”" };
    }));
    radioList($("themes"), themeItems, "theme");

    var presets = $("presets");
    choices.presets.forEach(function (p) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "preset"; b.textContent = p.label; b.dataset.forms = p.forms.join(",");
      b.addEventListener("click", function () { state.forms = p.forms.slice(); syncForms(); changed(); });
      presets.appendChild(b);
    });
    var forms = $("forms");
    choices.forms.forEach(function (f) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "chip"; b.dataset.id = f.id;
      b.innerHTML = '<span></span><span class="n"></span>';
      b.firstChild.textContent = f.label; b.lastChild.textContent = f.count;
      b.addEventListener("click", function () {
        var all = choices.forms.map(function (x) { return x.id; });
        var on = state.forms.length ? state.forms.slice() : all.slice();
        var i = on.indexOf(f.id);
        if (i >= 0) on.splice(i, 1); else on.push(f.id);
        state.forms = on.length === all.length ? [] : on;
        if (!on.length) state.forms = [f.id === all[0] ? all[1] : all[0]];  // never allow an empty exhibition
        syncForms(); changed();
      });
      forms.appendChild(b);
    });
    syncForms();

    document.querySelectorAll(".seg[data-key]").forEach(function (el) {
      var key = el.dataset.key;
      seg(el, key === "jargon" ? JARGON : MIX, key);
    });
    $("jargon-hint").textContent = JARGON_HINT[state.jargon];

    var sw = $("identities");
    var idItems = [{ name: "", accent: "#141414", ground: "#ffffff", font: "Seed" }].concat(choices.identities);
    idItems.forEach(function (it) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "swatch"; b.setAttribute("role", "radio");
      b.style.setProperty("--sw-accent", it.accent); b.style.setProperty("--sw-ground", it.ground);
      b.innerHTML = '<span class="aa">Aa</span><span class="nm"></span>';
      b.querySelector(".nm").textContent = it.name ? it.name[0].toUpperCase() + it.name.slice(1) : "Seed decides";
      b.setAttribute("aria-checked", state.identity === it.name);
      b.addEventListener("click", function () {
        state.identity = it.name;
        Array.prototype.forEach.call(sw.children, function (c, i) { c.setAttribute("aria-checked", state.identity === idItems[i].name); });
        changed();
      });
      sw.appendChild(b);
    });
  }

  function syncForms() {
    var on = state.forms;
    document.querySelectorAll("#forms .chip").forEach(function (c) {
      c.setAttribute("aria-pressed", !on.length || on.indexOf(c.dataset.id) >= 0);
    });
    document.querySelectorAll("#presets .preset").forEach(function (p) {
      p.setAttribute("aria-pressed", p.dataset.forms === on.join(","));
    });
    var n = on.length ? on.length : choices.forms.length;
    $("forms-hint").textContent = n === choices.forms.length ? "All " + n + " forms are allowed." : n + " of " + choices.forms.length + " forms are allowed.";
  }

  // ------------------------------------------------------------ generate + show
  function changed(delay) {
    clearTimeout(timer);
    timer = setTimeout(generate, delay === undefined ? 120 : delay);
  }

  function generate(keepNav) {
    writeHash();
    var base = location.href.split("#")[0].replace(/[^/]*$/, "");
    result = JSON.parse(studio.run(JSON.stringify(state), base, JSON.stringify(live)));
    var s = result.summary;
    document.documentElement.style.setProperty("--accent", s.accent);
    $("title").placeholder = s.theme_title;
    $("summary").innerHTML = "";
    var line = document.createElement("span");
    line.innerHTML = "<strong></strong>, <em></em>. ";
    line.querySelector("strong").textContent = s.edition;
    line.querySelector("em").textContent = s.title;
    $("summary").appendChild(line);
    $("summary").appendChild(document.createTextNode(
      s.artists + " artists from " + s.countries + " countries in " + s.venues + " venues in " + s.city +
      ". " + s.rediscovered + " rediscovered, " + s.collectives + (s.collectives === 1 ? " collective" : " collectives") +
      ". Artistic Director: " + s.director + "."));
    $("cli").textContent = result.cli;
    var keep = result.pages[current] ? current : "page/index";
    if (keepNav === true) navStack = navStack.filter(function (k) { return result.pages[k]; });
    else navStack = [];
    show(keep, true);
  }

  function show(key, replace) {
    if (!result || !result.pages[key]) return;
    if (!replace && current) navStack.push(current);
    current = key;
    // double buffer: load the new page in the hidden frame, swap when it has painted, so nothing flashes
    var token = ++loadToken;
    var front = document.querySelector(".viewport iframe.front");
    var back = front.id === "siteA" ? $("siteB") : $("siteA");
    back.onload = function () {
      if (token !== loadToken) return;
      back.classList.add("front"); back.removeAttribute("aria-hidden"); back.removeAttribute("tabindex");
      front.classList.remove("front"); front.setAttribute("aria-hidden", "true"); front.setAttribute("tabindex", "-1");
    };
    back.srcdoc = result.pages[key];
    $("back").disabled = navStack.length === 0;
    var label = key.startsWith("work/") ? "Work page" : key.slice(5).replace(/^./, function (c) { return c.toUpperCase(); });
    $("where").textContent = label === "Index" ? "Exhibition home" : label;
    lastError = "";
    liveUI();
  }

  // ------------------------------------------------------------ live images
  function loadLive() {
    try { return JSON.parse(localStorage.getItem("artgen.live") || "{}"); } catch (e) { return {}; }
  }
  function saveLive() {
    var keep = {};
    Object.keys(live).filter(function (p) { return live[p].indexOf("blob:") !== 0; }).slice(-150).forEach(function (p) { keep[p] = live[p]; });
    try { localStorage.setItem("artgen.live", JSON.stringify(keep)); } catch (e) { /* storage full or blocked: fine */ }
  }

  async function checkApi(boot) {
    try {
      var r = await fetch("api/status", { cache: "no-store" });
      var d = r.ok && (r.headers.get("content-type") || "").indexOf("json") >= 0 ? await r.json() : null;
      if (d && d.enabled) { api = { enabled: true, remaining: d.remaining, limit: d.limit }; MODEL = d.model || MODEL; return; }
    } catch (e) { /* a plain static host has no backend */ }
    if (boot) { api = { enabled: false, remaining: 0, limit: 0 }; live = {}; }   // remembered addresses point at a backend that is not here
  }

  function currentWork() {
    if (!result || current.indexOf("work/") !== 0) return null;
    var slug = current.slice(5);
    return result.works.filter(function (w) { return w.slug === slug; })[0] || null;
  }

  function freeLine() {
    if (!api.enabled) return "";
    if (api.remaining <= 0) return "No free renders left today.";
    return api.remaining + " free " + (api.remaining === 1 ? "render" : "renders") + " left today.";
  }

  function liveUI() {
    var hint = "Every photograph here is a preset from the image library. ";
    if (userKey) hint += "Open a work to render it live for this edition with your key, or render every work.";
    else if (api.enabled) hint += "Open a work to render it live for this edition. " + freeLine();
    else hint += "To render a work live for this edition, use your own OpenAI key.";
    $("live-hint").textContent = hint;
    $("key-forget").disabled = !userKey;
    var todo = result ? result.works.filter(function (w) { return !w.live; }).length : 0;
    $("render-all").disabled = !userKey || (!batch && !todo);
    $("render-all").textContent = batch ? "Stop" : todo && result && todo < result.works.length ? "Render the other " + todo : "Render every work";

    var btn = $("render"), status = $("live-status"), w = currentWork();
    status.className = lastError ? "bad" : "";
    if (batch) {
      btn.hidden = true;
      status.textContent = lastError || "Rendering " + batch.done + " of " + batch.total + "…";
      return;
    }
    if (!w) { btn.hidden = true; status.textContent = lastError; return; }
    if (w.live) { btn.hidden = true; status.textContent = "Rendered live for this edition."; return; }
    if (busy[w.prompt]) {
      btn.hidden = false; btn.disabled = true;
      btn.textContent = "Rendering… " + Math.round((Date.now() - busy[w.prompt]) / 1000) + " s";
      status.textContent = "This takes about 20 seconds.";
      return;
    }
    if (!userKey && !api.enabled) { btn.hidden = true; status.textContent = lastError || "Preset photograph."; return; }
    btn.hidden = false;
    btn.disabled = !userKey && api.remaining <= 0;
    btn.textContent = userKey ? "Render with your key" : "Render this work live";
    status.textContent = lastError || (userKey ? "Preset photograph." : api.remaining > 0 ? freeLine() : "No free renders left today. Use your own key.");
  }

  async function renderFree(prompt) {
    var r = await fetch("api/render", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ prompt: prompt }) });
    var d = {};
    try { d = await r.json(); } catch (e) { /* not JSON */ }
    if (typeof d.remaining === "number") api.remaining = d.remaining;
    if (!r.ok) throw new Error(d.error || "The render failed.");
    return new URL(d.url, location.href).href;
  }

  async function renderOwn(prompt) {
    var body = { model: MODEL, prompt: prompt, size: "1536x1024", quality: "medium", n: 1, output_format: "jpeg", output_compression: 82 };
    for (var attempt = 0; attempt < 2; attempt++) {
      var r;
      try {
        r = await fetch("https://api.openai.com/v1/images/generations", {
          method: "POST", headers: { authorization: "Bearer " + userKey, "content-type": "application/json" }, body: JSON.stringify(body),
        });
      } catch (e) {   // OpenAI sends a refused key back without browser access headers, so it looks like a network failure
        throw new Error("OpenAI did not answer. Check the key and your connection.");
      }
      var d = {};
      try { d = await r.json(); } catch (e) { /* not JSON */ }
      if (r.ok && d.data && d.data[0] && d.data[0].b64_json) {
        var blob = await (await fetch("data:image/jpeg;base64," + d.data[0].b64_json)).blob();
        return URL.createObjectURL(blob);
      }
      var msg = (d.error && d.error.message) || "OpenAI answered " + r.status + ".";
      if (r.status === 400 && /moderation|safety/i.test(msg) && attempt === 0) { body.prompt = prompt + SAFE; continue; }
      if (r.status === 401) msg = "OpenAI did not accept this key.";
      throw new Error(msg);
    }
  }

  async function renderWork(w) {
    if (busy[w.prompt]) return false;
    busy[w.prompt] = Date.now(); lastError = "";
    if (!busyTick) busyTick = setInterval(liveUI, 1000);
    liveUI();
    var ok = false;
    try {
      live[w.prompt] = await (userKey ? renderOwn(w.prompt) : renderFree(w.prompt));
      saveLive();
      ok = true;
    } catch (err) {
      lastError = err.message.slice(0, 160);
    }
    delete busy[w.prompt];
    if (!Object.keys(busy).length) { clearInterval(busyTick); busyTick = null; }
    if (ok) { var e = lastError; generate(true); lastError = e; }
    liveUI();
    return ok;
  }

  $("render").addEventListener("click", function () { var w = currentWork(); if (w) renderWork(w); });

  $("key").addEventListener("input", function () {
    userKey = this.value.trim(); lastError = ""; liveUI();
  });
  $("key-forget").addEventListener("click", function () {
    userKey = ""; $("key").value = ""; if (batch) batch.stop = true; liveUI();
  });
  $("render-all").addEventListener("click", async function () {
    if (batch) { batch.stop = true; return; }
    var todo = result.works.filter(function (w) { return !w.live; });
    batch = { done: 0, total: todo.length, stop: false };
    for (var i = 0; i < todo.length && !batch.stop && userKey; i++) {
      batch.done = i + 1; liveUI();
      if (!(await renderWork(todo[i]))) break;   // a refused key or a rate limit will fail every time: stop
    }
    batch = null; liveUI();
  });

  // a pasted or edited link changes only the hash: reload the state from it
  window.addEventListener("hashchange", function () {
    if (!studio) return;
    state = readHash(); current = "page/index"; rebuild();
  });
  window.addEventListener("focus", function () {   // the daily allowance may have changed in another tab
    if (studio && api.enabled) checkApi().then(liveUI);
  });

  window.addEventListener("message", function (e) {
    if (e.data && typeof e.data.artgenNav === "string") show(e.data.artgenNav);
  });
  $("back").addEventListener("click", function () {
    if (!navStack.length) return;
    var prev = navStack.pop(); show(prev, true); $("back").disabled = navStack.length === 0;
  });

  // ------------------------------------------------------------ inputs
  $("seed").addEventListener("change", function () { state.seed = Math.max(1, parseInt(this.value, 10) || 1); changed(); });
  $("dice").addEventListener("click", function () {
    state.seed = 1 + Math.floor(Math.random() * 99999); $("seed").value = state.seed; current = "page/index"; changed();
  });
  $("works").addEventListener("input", function () { state.works = parseInt(this.value, 10); $("works-out").textContent = state.works; changed(); });
  $("title").addEventListener("input", function () { state.title = this.value; changed(0); });  // the headline types along

  $("surprise").addEventListener("click", function () {
    var pickOne = function (a) { return a[Math.floor(Math.random() * a.length)]; };
    state.seed = 1 + Math.floor(Math.random() * 99999);
    state.host = pickOne(hostItems).id;
    state.theme = pickOne(themeItems).id;
    state.forms = pickOne(choices.presets).forms.slice();
    state.rediscovered = pickOne(MIX)[0]; state.collectives = pickOne(MIX)[0]; state.emerging = pickOne(MIX)[0];
    state.jargon = pickOne(JARGON)[0];
    state.identity = pickOne(choices.identities).name;
    state.title = "";
    current = "page/index";
    rebuild();
  });

  function rebuild() {
    ["hosts", "themes", "presets", "forms", "identities"].forEach(function (id) { $(id).innerHTML = ""; });
    buildControls();
    generate();
  }

  $("share").addEventListener("click", function () { copy(location.href, this, "Link copied"); });
  $("copy-cli").addEventListener("click", function () { copy(result ? result.cli : "", this, "Copied"); });
  $("download").addEventListener("click", function () {
    if (!result) return;
    var blob = new Blob([JSON.stringify(result.exhibition, null, 2)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "exhibition.json"; a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  });
  function copy(text, btn, done) {
    var label = btn.textContent;
    (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () {
      btn.textContent = done; setTimeout(function () { btn.textContent = label; }, 1400);
    }, function () { window.prompt("Copy this:", text); });
  }

  boot().catch(function (err) {
    $("summary").textContent = "The Studio could not start: " + err.message + ". Check your connection and reload.";
    console.error(err);
  });
})();
