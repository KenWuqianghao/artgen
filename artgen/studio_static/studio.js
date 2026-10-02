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

  function generate() {
    writeHash();
    var base = location.href.split("#")[0].replace(/[^/]*$/, "");
    result = JSON.parse(studio.run(JSON.stringify(state), base));
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
    navStack = [];
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
  }

  // a pasted or edited link changes only the hash: reload the state from it
  window.addEventListener("hashchange", function () {
    if (!studio) return;
    state = readHash(); current = "page/index"; rebuild();
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
