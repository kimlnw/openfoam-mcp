/* ==========================================================================
   GOGO! Travel — search results
   ========================================================================== */
(function () {
  "use strict";
  var GOGO = window.GOGO, money = GOGO.money, $ = function (id) { return document.getElementById(id); };

  var state = { dest: "", zones: {}, maxPrice: 10000, types: {}, duration: "Any", minRating: false, sort: "rec", view: "list" };

  /* ---- destination match (search a place -> show that place) ------------- */
  function words(s) { return (s || "").toLowerCase().replace(/[^a-z0-9 ]/g, " ").replace(/\b(koh|ko)\b/g, " ").split(/\s+/).filter(Boolean); }
  function destMatch(t, dest) {
    var d = words(dest); if (!d.length) return true;
    var set = {}; words(t.title + " " + t.region + " " + t.id + " " + t.country).forEach(function (w) { set[w] = 1; });
    return d.every(function (tok) { return tok.length < 2 || set[tok] === 1; });   // whole-word, not substring
  }
  function setTitle() {
    $("results-title").textContent = state.dest ? ("Trips in " + state.dest) : "All trips";
  }

  /* ---- header from query (multi-file site reads ?dest=...) --------------- */
  state.dest = (GOGO.params().get("dest") || "").trim();
  if (state.dest) setTitle();

  /* ---- filter data ------------------------------------------------------- */
  var TYPES = ["Beach", "City", "Adventure", "Cultural"];
  var DURS = ["Any", "2 days", "3 days", "4+ days"];
  var ZONES = ["North", "Isan", "Central", "East", "Gulf", "Andaman"];
  function inDur(days, d) {
    if (d === "Any") return true;
    if (d === "2 days") return days === 2;
    if (d === "3 days") return days === 3;
    return days >= 4;
  }
  function filtered() {
    var anyType = Object.keys(state.types).length > 0;
    var anyZone = Object.keys(state.zones).length > 0;
    var list = GOGO.trips.filter(function (t) {
      if (state.dest && !destMatch(t, state.dest)) return false;
      if (anyZone && !state.zones[t.zone]) return false;
      if (t.price > state.maxPrice) return false;
      if (anyType && !state.types[t.type]) return false;
      if (!inDur(t.days, state.duration)) return false;
      if (state.minRating && t.rating < 4.8) return false;
      return true;
    });
    if (state.sort === "price") list = list.slice().sort(function (a, b) { return a.price - b.price; });
    else if (state.sort === "rating") list = list.slice().sort(function (a, b) { return b.rating - a.rating; });
    return list;
  }

  /* ---- controls ---------------------------------------------------------- */
  var SORTS = [{ k: "rec", label: "Recommended" }, { k: "price", label: "Price" }, { k: "rating", label: "Rating" }];
  $("sortToggle").innerHTML = SORTS.map(function (s) {
    return '<button type="button" data-sort="' + s.k + '"' + (s.k === state.sort ? ' class="is-active"' : "") + ">" + s.label + "</button>";
  }).join("");
  $("viewToggle").innerHTML =
    '<button type="button" data-view="list" class="is-active">' + GOGO.svg("list", 15) + "List</button>" +
    '<button type="button" data-view="map">' + GOGO.svg("map", 15) + "Map</button>";
  $("zoneChips").innerHTML = ZONES.map(function (z) { return '<button class="pill" type="button" data-zone="' + z + '">' + z + "</button>"; }).join("");
  $("typeChips").innerHTML = TYPES.map(function (t) { return '<button class="pill" type="button" data-type="' + t + '">' + t + "</button>"; }).join("");
  $("durChips").innerHTML = DURS.map(function (d) { return '<button class="pill" type="button" data-dur="' + d + '"' + (d === "Any" ? ' aria-pressed="true"' : "") + ">" + d + "</button>"; }).join("");
  $("ratingChip").innerHTML = '<button class="pill" type="button" id="ratingBtn" style="display:inline-flex;align-items:center;gap:6px"><span style="display:inline-flex;width:14px;height:14px">' + GOGO.svg("star", 14) + "</span>4.8 &amp; up</button>";

  function setTrack() {
    var pct = Math.round((state.maxPrice - 2000) / 8000 * 100);
    $("priceRange").style.background = "linear-gradient(90deg,var(--red) 0%,var(--red) " + pct + "%,var(--line) " + pct + "%,var(--line) 100%)";
    $("priceVal").textContent = money(state.maxPrice);
  }

  /* ---- render ------------------------------------------------------------ */
  function resultCard(t) {
    return '<a class="result-card lift" href="trip.html?id=' + t.id + '">' +
      '<div class="result-card__img ph ph--' + t.grad + '"><span class="loc">' + t.country + "</span></div>" +
      '<div class="result-card__body">' +
        '<div class="tcard__rating"><span class="star" style="display:inline-flex;width:13px;height:13px">' + GOGO.svg("star", 13) + "</span><b style=\"color:var(--ink)\">" + t.rating + "</b> · " + t.days + " days · " + t.type + "</div>" +
        "<h3>" + t.title + "</h3>" +
        '<p style="font-size:.9rem;color:var(--ink-soft);margin-top:6px;max-width:46ch">' + t.blurb + "</p>" +
        '<div class="result-card__tags"><span class="tag-pill tag-pill--teal">Free cancellation</span><span class="tag-pill tag-pill--violet">Small group</span></div>' +
      "</div>" +
      '<div class="result-card__side">' +
        '<button class="heart" type="button" data-wish="' + t.id + '" aria-pressed="false" aria-label="Save ' + t.title + '">' + GOGO.svg("heart", 18) + "</button>" +
        '<div style="text-align:right"><div class="filter-label" style="margin:0">From</div><div class="price-lg">' + money(t.price) + '</div><div style="font-size:.74rem;color:var(--faint)">per person</div>' +
        '<span class="btn btn--primary" style="margin-top:10px;font-size:.86rem;padding:9px 18px">View trip</span></div>' +
      "</div></a>";
  }

  function mapView(list) {
    var xs = ["22%", "58%", "36%", "72%", "14%", "50%"], ys = ["30%", "24%", "60%", "52%", "70%", "76%"];
    var pins = list.slice(0, 6).map(function (t, i) {
      return '<div class="mappin" style="left:' + xs[i] + ";top:" + ys[i] + '"><span>' + money(t.price) + "</span><i></i></div>";
    }).join("");
    return '<div class="mapview"><div class="mapview__grid"></div>' +
      '<div style="position:absolute;left:-8%;top:30%;width:52%;height:44%;background:#BFD6C4;border-radius:44% 56% 60% 40%;opacity:.75"></div>' +
      '<div style="position:absolute;right:2%;top:14%;width:40%;height:38%;background:#C9DCB9;border-radius:56% 44% 40% 60%;opacity:.7"></div>' +
      pins +
      '<div style="position:absolute;left:20px;bottom:20px;background:rgba(255,255,255,.94);border-radius:12px;padding:10px 16px;font-weight:700;font-size:.86rem;box-shadow:0 8px 20px -8px rgba(0,0,0,.3)">' + list.length + " trips in view</div></div>";
  }

  function render() {
    var list = filtered();
    $("results-sub").innerHTML = "<b style=\"color:var(--ink)\">" + list.length + "</b>" + (list.length === 1 ? " trip matches" : " trips match") + " your filters";
    var area = $("resultsArea");
    if (state.view === "map") { area.innerHTML = mapView(list); return; }
    if (!list.length) {
      area.innerHTML = '<div class="empty"><div class="empty__ic">' + GOGO.svg("search", 26) + "</div>" +
        "<h3 style=\"font-size:1.2rem\">No trips match these filters</h3>" +
        '<p style="font-size:.94rem;color:var(--ink-soft);margin-top:6px">Try raising your max price or clearing a filter.</p>' +
        '<button class="btn btn--primary" type="button" id="emptyClear" style="margin-top:16px">Clear all filters</button></div>';
      $("emptyClear").addEventListener("click", clearAll);
      return;
    }
    area.innerHTML = '<div style="display:flex;flex-direction:column;gap:16px">' + list.map(resultCard).join("") + "</div>";
    GOGO.refreshHearts(area);
  }

  /* ---- events ------------------------------------------------------------ */
  $("priceRange").addEventListener("input", function (e) { state.maxPrice = parseInt(e.target.value, 10); setTrack(); render(); });
  $("sortToggle").addEventListener("click", function (e) {
    var b = e.target.closest("[data-sort]"); if (!b) return;
    state.sort = b.getAttribute("data-sort");
    $("sortToggle").querySelectorAll("button").forEach(function (x) { x.classList.toggle("is-active", x === b); });
    render();
  });
  $("viewToggle").addEventListener("click", function (e) {
    var b = e.target.closest("[data-view]"); if (!b) return;
    state.view = b.getAttribute("data-view");
    $("viewToggle").querySelectorAll("button").forEach(function (x) { x.classList.toggle("is-active", x === b); });
    render();
  });
  $("zoneChips").addEventListener("click", function (e) {
    var b = e.target.closest("[data-zone]"); if (!b) return;
    var z = b.getAttribute("data-zone");
    if (state.zones[z]) delete state.zones[z]; else state.zones[z] = true;
    b.setAttribute("aria-pressed", state.zones[z] ? "true" : "false");
    render();
  });
  $("typeChips").addEventListener("click", function (e) {
    var b = e.target.closest("[data-type]"); if (!b) return;
    var t = b.getAttribute("data-type");
    if (state.types[t]) delete state.types[t]; else state.types[t] = true;
    b.setAttribute("aria-pressed", state.types[t] ? "true" : "false");
    render();
  });
  $("durChips").addEventListener("click", function (e) {
    var b = e.target.closest("[data-dur]"); if (!b) return;
    state.duration = b.getAttribute("data-dur");
    $("durChips").querySelectorAll(".pill").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    render();
  });
  $("ratingChip").addEventListener("click", function (e) {
    if (!e.target.closest("#ratingBtn")) return;
    state.minRating = !state.minRating;
    $("ratingBtn").setAttribute("aria-pressed", state.minRating ? "true" : "false");
    render();
  });

  function clearAll() {
    state.maxPrice = 10000; state.types = {}; state.zones = {}; state.duration = "Any"; state.minRating = false;
    $("priceRange").value = 10000;
    $("zoneChips").querySelectorAll(".pill").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
    $("typeChips").querySelectorAll(".pill").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
    $("durChips").querySelectorAll(".pill").forEach(function (x) { x.setAttribute("aria-pressed", x.getAttribute("data-dur") === "Any" ? "true" : "false"); });
    $("ratingBtn").setAttribute("aria-pressed", "false");
    setTrack(); render();
  }
  $("clearFilters").addEventListener("click", clearAll);

  /* ---- single-page hook: the router calls this when you land on search --- */
  window.GOGO.searchSetDest = function (dest) {
    state.dest = (dest || "").trim();
    setTitle();
    render();
  };

  setTrack();
  render();
})();
