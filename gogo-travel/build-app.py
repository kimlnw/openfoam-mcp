#!/usr/bin/env python3
"""Bundle the multi-file GOGO! site into ONE self-contained gogo-app.html.

Reads the real source files (assets/css, assets/js, the five *.html pages) and
emits a single standalone page with a tiny hash router, so the whole site can
be hosted from one file or opened directly with file://. Run:  python3 build-app.py

The multi-file site is the source of truth; this file is generated. Re-run after
editing any page, script, style, or data so the bundle can't drift.
"""
import re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
OUT  = ROOT / "gogo-app.html"

def rd(p): return (ROOT / p).read_text(encoding="utf-8")

def must(cond, msg):
    if not cond:
        print("BUILD ERROR:", msg); sys.exit(1)

# ---------------------------------------------------------------- CSS --------
# .ph--<id> : embed a real photo (downscaled) as a data URI when present so the
# single file is self-contained; otherwise drop the layer and show the gradient.
IMGDIR = ROOT / "assets/img"
import base64, io
def _data_uri(fid):
    p = IMGDIR / (fid + ".jpg")
    if not p.exists() or p.stat().st_size < 1000:   # skip missing/empty/partial
        return None
    try:
        from PIL import Image
        im = Image.open(p).convert("RGB")
        w, h = im.size
        if w > 1000:
            im = im.resize((1000, round(h * 1000 / w)), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=72, optimize=True)
        raw = buf.getvalue()
    except Exception:
        raw = p.read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode()
_embedded = []
def _embed(m):
    d = _data_uri(m.group(1))
    if d: _embedded.append(m.group(1)); return "url(" + d + ") center/cover no-repeat, "
    return ""
css = rd("assets/css/styles.css")
css = re.sub(r"url\('\.\./img/([a-z]+)\.jpg'\) center/cover no-repeat, ", _embed, css)
must("url('../img/" not in css, "photo url() layers still present in CSS")

font_import = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Cormorant+Garamond:wght@500;600;700&"
    "family=Jost:wght@300;400;500;600;700;800&display=swap');\n"
)
spa_css = (
    "\n/* ---- single-page routing + ground ---- */\n"
    ".route[hidden]{display:none!important}\n"
    "#app{min-height:40vh}\n"
    # Commit to one warm-ivory world; paint the root so it holds on any host.
    "html{background:var(--bg)}\n"
)

# ---------------------------------------------------------------- HTML --------
def main_inner(fname):
    html = rd(fname)
    m = re.search(r"<main\b[^>]*>(.*)</main>", html, re.S)
    must(m, f"no <main> found in {fname}")
    return m.group(1).strip()

sections = "\n".join([
    f'<div class="route" data-route="home">\n{main_inner("index.html")}\n</div>',
    f'<div class="route wrap" data-route="search" hidden>\n{main_inner("search.html")}\n</div>',
    f'<div class="route wrap" data-route="trip" id="trip-root" hidden>\n{main_inner("trip.html")}\n</div>',
    f'<div class="route wrap" data-route="planner" style="padding-top:34px;padding-bottom:52px" hidden>\n{main_inner("planner.html")}\n</div>',
    f'<div class="route wrap" data-route="surprise" style="padding:44px 0 60px" hidden>\n{main_inner("surprise.html")}\n</div>',
])

# --------------------------------------------------------------- SCRIPTS ------
data_js = rd("assets/js/data.js")
site_js = rd("assets/js/site.js")

def to_init(fname, init_name):
    js = rd(fname)
    js2 = js.replace("(function () {", f"window.GOGO.{init_name} = function () {{", 1)
    must(js2 != js, f"could not open-wrap {fname}")
    idx = js2.rfind("})();")
    must(idx != -1, f"could not find IIFE close in {fname}")
    return js2[:idx] + "};" + js2[idx + len("})();"):]

home_js = to_init("assets/js/home.js", "initHome").replace(
    'location.href = "search.html?" + p.toString();',
    'location.hash = "#/search?" + p.toString();')
must('location.hash = "#/search?"' in home_js, "home search-submit not rewired to hash")

search_js   = to_init("assets/js/search.js",   "initSearch")
planner_js  = to_init("assets/js/planner.js",  "initPlanner")
surprise_js = to_init("assets/js/surprise.js", "initSurprise")

# trip.js -> re-runnable GOGO._runTrip(id); no bundled photos (gradient only)
trip_js = rd("assets/js/trip.js")
trip_js = trip_js.replace("(function () {", "window.GOGO._runTrip = function (id) {", 1)
trip_js = trip_js.replace('var trip = GOGO.getTrip(GOGO.params().get("id"));',
                          'var trip = GOGO.getTrip(id);')
trip_js = trip_js.replace(
    'var photoLayer = "url(\'assets/img/" + trip.id + ".jpg\') center/cover no-repeat, ";',
    'var photoLayer = "";')
_idx = trip_js.rfind("})();")
must(_idx != -1, "trip IIFE close not found")
trip_js = trip_js[:_idx] + "};" + trip_js[_idx + len("})();"):]
must("GOGO._runTrip = function (id)" in trip_js, "trip not wrapped")
must("GOGO.getTrip(id)" in trip_js, "trip id not wired")

router_js = r"""
(function () {
  "use strict";
  var GOGO = window.GOGO;
  var routes = ["home", "search", "trip", "planner", "surprise"];
  var titles = {
    home: "GOGO! — Go somewhere good", search: "Search trips — GOGO!",
    trip: "Trip — GOGO!", planner: "Budget planner — GOGO!",
    surprise: "Surprise me — GOGO!"
  };
  var TRIP_TEMPLATE = null;

  function parseHash() {
    var h = location.hash.replace(/^#\/?/, "");
    var path = h, q = "", qi = h.indexOf("?");
    if (qi >= 0) { path = h.slice(0, qi); q = h.slice(qi + 1); }
    if (!path) path = "home";
    return { path: path, params: new URLSearchParams(q) };
  }

  function setActiveNav(path) {
    var header = document.getElementById("site-header"); if (!header) return;
    header.querySelectorAll(".site-nav a").forEach(function (a) { a.removeAttribute("aria-current"); });
    var map = { search: "search.html", surprise: "surprise.html" }, want = map[path];
    if (want) { var l = header.querySelector('.site-nav a[href="' + want + '"]'); if (l) l.setAttribute("aria-current", "page"); }
  }

  function show() {
    var r = parseHash();
    var path = routes.indexOf(r.path) >= 0 ? r.path : "home";
    routes.forEach(function (name) {
      var el = document.querySelector('[data-route="' + name + '"]');
      if (el) el.hidden = (name !== path);
    });
    document.title = titles[path] || titles.home;
    if (path === "trip") {
      var root = document.getElementById("trip-root");
      if (root && TRIP_TEMPLATE != null) root.innerHTML = TRIP_TEMPLATE;
      GOGO._runTrip(r.params.get("id"));
    }
    if (path === "search" && GOGO.searchSetDest) GOGO.searchSetDest(r.params.get("dest"));
    setActiveNav(path);
    var active = document.querySelector('[data-route="' + path + '"]');
    if (active) active.querySelectorAll(".reveal").forEach(function (e) { e.classList.add("in"); });
    if (GOGO.refreshHearts) GOGO.refreshHearts(document);
    window.scrollTo(0, 0);
  }

  document.addEventListener("click", function (e) {
    if (e.defaultPrevented) return;
    var a = e.target.closest && e.target.closest("a[href]"); if (!a) return;
    var href = a.getAttribute("href"); if (!href) return;
    if (href.charAt(0) === "#") { if (href === "#") e.preventDefault(); return; }
    var m = href.match(/^(index|search|trip|planner|surprise)\.html(?:\?(.*))?$/);
    if (!m) return;
    e.preventDefault();
    var page = m[1] === "index" ? "home" : m[1];
    var q = m[2] ? ("?" + m[2]) : "";
    var target = "#/" + (page === "home" ? "" : page) + q;
    if (location.hash === target) show(); else location.hash = target;
  });

  window.addEventListener("hashchange", show);

  function boot() {
    var tripRoot = document.getElementById("trip-root");
    if (tripRoot) TRIP_TEMPLATE = tripRoot.innerHTML;
    if (GOGO.initHome) GOGO.initHome();
    if (GOGO.initSearch) GOGO.initSearch();
    if (GOGO.initPlanner) GOGO.initPlanner();
    if (GOGO.initSurprise) GOGO.initSurprise();
    show();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
"""

# --------------------------------------------------------------- ASSEMBLE -----
def script(js): return "<script>\n" + js.strip() + "\n</script>"

body = "\n".join([
    '<header id="site-header"></header>',
    '<main id="app">',
    sections,
    "</main>",
    '<footer id="site-footer"></footer>',
    "",
    script(data_js), script(site_js), script(home_js), script(search_js),
    script(trip_js), script(planner_js), script(surprise_js), script(router_js),
])

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GOGO! Travel — Go somewhere good</title>
<meta name="description" content="GOGO! — handpicked Thailand weekend getaways, priced honestly. Search, plan by budget, or let Surprise Me pick your weekend.">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<style>
{font_import}{css}{spa_css}</style>
</head>
<body>
{body}
</body>
</html>
"""

OUT.write_text(doc, encoding="utf-8")
print("WROTE", OUT.relative_to(ROOT), len(doc), "bytes", "| embedded photos:", len(_embedded))
print("routes:", re.findall(r'data-route="(\w+)"', sections))
