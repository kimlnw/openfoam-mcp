/* ==========================================================================
   GOGO! Travel — budget planner
   Finds trips that fit a total budget for N travellers, and breaks down the spend.
   ========================================================================== */
(function () {
  "use strict";
  var GOGO = window.GOGO, money = GOGO.money, $ = function (id) { return document.getElementById(id); };

  var st = { budget: 3000, persons: 2, nights: 7, style: "Any", selectedId: "" };
  var STYLES = ["Any", "Beach", "City", "Adventure", "Cultural"];
  var PARTS = [
    { label: "Stays & rooms", pct: 0.42, color: "var(--red)" },
    { label: "Transport & transfers", pct: 0.24, color: "var(--gold)" },
    { label: "Guided activities", pct: 0.24, color: "var(--teal)" },
    { label: "GOGO! service", pct: 0.10, color: "var(--violet)" }
  ];

  function group(t) { return t.price * st.persons; }
  function nightsText(d) { return d + (d === 1 ? " night" : " nights"); }

  /* ---- style pills ------------------------------------------------------- */
  $("styleChips").innerHTML = STYLES.map(function (s) {
    return '<button class="pill" type="button" data-style="' + s + '"' + (s === st.style ? ' aria-pressed="true"' : "") + ">" + s + "</button>";
  }).join("");
  $("styleChips").addEventListener("click", function (e) {
    var b = e.target.closest("[data-style]"); if (!b) return;
    st.style = b.getAttribute("data-style"); st.selectedId = "";
    $("styleChips").querySelectorAll(".pill").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    render();
  });

  /* ---- inputs ------------------------------------------------------------ */
  $("pDec").innerHTML = GOGO.svg("minus", 16);
  $("pInc").innerHTML = GOGO.svg("plus", 16);
  $("budgetRange").addEventListener("input", function (e) { st.budget = parseInt(e.target.value, 10); st.selectedId = ""; render(); });
  $("nightsRange").addEventListener("input", function (e) { st.nights = parseInt(e.target.value, 10); render(); });
  $("pDec").addEventListener("click", function () { st.persons = Math.max(1, st.persons - 1); st.selectedId = ""; render(); });
  $("pInc").addEventListener("click", function () { st.persons = Math.min(12, st.persons + 1); st.selectedId = ""; render(); });

  function tracks() {
    var bp = Math.round((st.budget - 500) / 9500 * 100);
    $("budgetRange").style.background = "linear-gradient(90deg,var(--red) 0%,var(--red) " + bp + "%,var(--line) " + bp + "%,var(--line) 100%)";
    var np = Math.round((st.nights - 2) / 12 * 100);
    $("nightsRange").style.background = "linear-gradient(90deg,var(--red) 0%,var(--red) " + np + "%,var(--line) " + np + "%,var(--line) 100%)";
    $("budgetVal").textContent = money(st.budget);
    $("perPerson").textContent = money(st.budget / st.persons) + " / person";
    $("pVal").textContent = st.persons + (st.persons === 1 ? " traveler" : " travelers");
    $("pNum").textContent = st.persons;
    $("nightsVal").textContent = nightsText(st.nights);
  }

  /* ---- render ------------------------------------------------------------ */
  function render() {
    tracks();

    var styleTrips = GOGO.trips.filter(function (t) { return st.style === "Any" || t.type === st.style; });
    var fits = styleTrips.filter(function (t) { return group(t) <= st.budget; });
    var ranked = fits.slice().sort(function (a, b) {
      var da = Math.abs(a.days - st.nights), db = Math.abs(b.days - st.nights);
      if (da !== db) return da - db;
      return group(b) - group(a);
    });
    var best = null, i;
    if (st.selectedId) for (i = 0; i < fits.length; i++) if (fits[i].id === st.selectedId) best = fits[i];
    if (!best) best = ranked[0] || null;

    var out = $("planResults");

    if (!best) {
      var cheapest = styleTrips.slice().sort(function (a, b) { return group(a) - group(b); })[0];
      var cg = cheapest ? group(cheapest) : 0;
      var styleWord = st.style === "Any" ? "" : (st.style.toLowerCase() + " ");
      out.innerHTML =
        '<div class="card" style="padding:40px 28px;text-align:center;border-style:dashed">' +
          '<div class="empty__ic" style="background:var(--red-soft);color:var(--red)"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4M12 17h.01M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg></div>' +
          '<h3 style="font-size:1.2rem">That budget is a little tight</h3>' +
          '<p style="font-size:.94rem;color:var(--ink-soft);margin:8px auto 0;max-width:46ch">The most affordable ' + styleWord + "trip for " + st.persons + (st.persons === 1 ? " traveler" : " travelers") + ' is <b>' + money(cg) + "</b>. Raise your budget, drop a traveller, or widen the style.</p>" +
          '<button class="btn btn--primary" type="button" id="setCheapest" style="margin-top:18px">Set budget to ' + money(cg) + "</button></div>";
      var sc = $("setCheapest");
      if (sc) sc.addEventListener("click", function () { st.budget = Math.min(10000, cg); $("budgetRange").value = st.budget; render(); });
      return;
    }

    var g = group(best), left = st.budget - g, usedPct = Math.min(100, Math.round(g / st.budget * 100));
    var others = ranked.filter(function (t) { return t.id !== best.id; }).sort(function (a, b) { return group(b) - group(a); }).slice(0, 3);

    var breakdown = PARTS.map(function (part) {
      return '<div class="bd-row"><div class="bd-row__top"><span style="color:#2B3040">' + part.label + '</span><span style="font-weight:800" class="tnum">' + money(g * part.pct) + "</span></div>" +
        '<div class="bd-tk"><i style="width:' + Math.round(part.pct * 100) + "%;background:" + part.color + '"></i></div></div>';
    }).join("");

    var othersHTML = others.length ?
      '<div><span class="filter-label">Other trips that fit</span><div style="display:flex;flex-direction:column;gap:10px">' +
      others.map(function (t) {
        var gg = group(t);
        return '<div class="card other-fit"><div class="other-fit__sw ph--' + t.grad + '"></div>' +
          '<div style="flex:1"><div style="font-weight:800;font-size:1rem">' + t.title + '</div><div style="font-size:.82rem;color:var(--ink-soft)">' + t.country + " · " + nightsText(t.days) + "</div></div>" +
          '<div style="text-align:right"><div style="font-weight:800" class="tnum">' + money(gg) + '</div><div style="font-size:.72rem;color:var(--teal);font-weight:700">' + money(st.budget - gg) + " under</div></div>" +
          '<button class="btn btn--ghost" type="button" data-use="' + t.id + '" style="flex:none;font-size:.82rem;padding:9px 15px">Use this</button></div>';
      }).join("") + "</div></div>" : "";

    out.innerHTML =
      // fit meter
      '<div class="card" style="padding:22px 24px"><div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px">' +
        '<span style="font-weight:800;font-size:.96rem">Budget used by your best match</span><span style="font-weight:800;color:var(--red)">' + usedPct + "% used</span></div>" +
        '<div class="fit-meter"><i style="width:' + usedPct + '%"></i></div>' +
        '<div style="display:flex;justify-content:space-between;font-size:.86rem;margin-top:10px"><span style="color:var(--ink-soft)">' + money(g) + ' on the trip</span><span style="color:var(--teal);font-weight:800">' + money(left) + " left over</span></div></div>" +
      // best plan
      '<div class="card" style="overflow:hidden"><div class="plan-banner ph--' + best.grad + '"><div class="plan-banner__scrim"></div>' +
        '<span class="filter-label" style="position:absolute;left:16px;top:14px;margin:0;color:#fff;background:rgba(0,0,0,.4);padding:5px 10px;border-radius:999px">Best value in budget</span>' +
        '<div style="position:absolute;left:18px;bottom:13px;color:#fff"><div style="font-weight:800;font-size:1.2rem;text-shadow:0 1px 8px rgba(0,0,0,.5)">' + best.title + '</div><div style="font-size:.82rem;opacity:.92">' + best.country + " · " + nightsText(best.days) + "</div></div></div>" +
        '<div style="padding:22px 24px"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;flex-wrap:wrap;gap:10px">' +
          '<div><span class="filter-label" style="margin:0">Group total · ' + st.persons + (st.persons === 1 ? " traveler" : " travelers") + '</span><div style="font-weight:800;font-size:1.5rem;margin-top:6px" class="tnum">' + money(g) + "</div></div>" +
          '<span class="tag-pill tag-pill--teal" style="font-size:.78rem">' + money(left) + " under budget</span></div>" +
          '<span class="filter-label">Where the money goes</span>' + breakdown +
          '<div style="display:flex;align-items:center;gap:9px;margin-top:18px;background:#F0FBF8;border:1px solid #C7ECE4;border-radius:12px;padding:12px 15px">' + GOGO.svg("shield", 18).replace("currentColor", "#0E9F8F") + '<span style="font-size:.9rem;color:#0B7A6E"><b>' + money(left) + "</b> left for food, extras &amp; a buffer.</span></div>" +
          '<a class="btn btn--primary btn--block btn--lg" href="trip.html?id=' + best.id + '" style="margin-top:16px">View this trip</a></div></div>' +
      othersHTML;

    out.querySelectorAll("[data-use]").forEach(function (b) {
      b.addEventListener("click", function () { st.selectedId = b.getAttribute("data-use"); render(); });
    });
  }

  render();
})();
