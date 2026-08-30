/* ==========================================================================
   GOGO! Travel — Surprise Me (mystery weekend generator)
   Picks a weekend that fits your vibe + budget, weighted by "usable hours".
   ========================================================================== */
(function () {
  "use strict";
  var GOGO = window.GOGO, money = GOGO.money, $ = function (id) { return document.getElementById(id); };

  var VIBES = [
    { k: "Any", label: "Anything", type: null },
    { k: "Beach", label: "Beach", type: "Beach" },
    { k: "Culture", label: "Culture", type: "Cultural" },
    { k: "Nature", label: "Nature", type: "Adventure" },
    { k: "City", label: "City", type: "City" }
  ];
  var BUDGETS = [
    { v: 3000, label: "฿3,000" },
    { v: 5000, label: "฿5,000" },
    { v: 8000, label: "฿8,000" },
    { v: 999999, label: "Any" }
  ];
  var st = { vibe: "Any", budget: 999999, who: 2 };
  var stage = $("spinStage"), spinBtn = $("spinBtn");

  /* ---- controls ---------------------------------------------------------- */
  $("vibeRow").innerHTML = VIBES.map(function (v) {
    return '<button class="pill" type="button" data-vibe="' + v.k + '"' + (v.k === st.vibe ? ' aria-pressed="true"' : "") + ">" + v.label + "</button>";
  }).join("");
  $("budgetRow").innerHTML = BUDGETS.map(function (b) {
    return '<button class="pill" type="button" data-budget="' + b.v + '"' + (b.v === st.budget ? ' aria-pressed="true"' : "") + ">" + b.label + "</button>";
  }).join("");
  $("sDec").innerHTML = GOGO.svg("minus", 16);
  $("sInc").innerHTML = GOGO.svg("plus", 16);
  spinBtn.innerHTML = GOGO.svg("dice", 22) + "Surprise me!";

  $("vibeRow").addEventListener("click", function (e) {
    var b = e.target.closest("[data-vibe]"); if (!b) return;
    st.vibe = b.getAttribute("data-vibe");
    $("vibeRow").querySelectorAll(".pill").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
  });
  $("budgetRow").addEventListener("click", function (e) {
    var b = e.target.closest("[data-budget]"); if (!b) return;
    st.budget = parseInt(b.getAttribute("data-budget"), 10);
    $("budgetRow").querySelectorAll(".pill").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
  });
  function renderWho() { $("sWho").textContent = st.who + (st.who === 1 ? " traveller" : " travellers"); }
  $("sDec").addEventListener("click", function () { st.who = Math.max(1, st.who - 1); renderWho(); });
  $("sInc").addEventListener("click", function () { st.who = Math.min(12, st.who + 1); renderWho(); });

  /* ---- selection --------------------------------------------------------- */
  function vibeType() { for (var i = 0; i < VIBES.length; i++) if (VIBES[i].k === st.vibe) return VIBES[i].type; return null; }
  function pool(ignoreBudget) {
    var v = vibeType();
    return GOGO.trips.filter(function (t) {
      if (v && t.type !== v) return false;
      if (!ignoreBudget && t.price > st.budget) return false;
      return true;
    });
  }
  function pick(list) {
    var total = 0, i;
    for (i = 0; i < list.length; i++) total += GOGO.usableHours(list[i]);
    var r = Math.random() * total, acc = 0;
    for (i = 0; i < list.length; i++) { acc += GOGO.usableHours(list[i]); if (r <= acc) return list[i]; }
    return list[list.length - 1];
  }
  function reduced() { return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches; }
  function verdict(uh) { return uh >= 44 ? "Loads of time" : uh >= 34 ? "Plenty of time" : "Tight but doable"; }

  /* ---- render ------------------------------------------------------------ */
  function spinningCard() {
    return '<div class="spin-card is-spinning"><div class="spin-card__img ph--' + GOGO.trips[0].grad + '">' +
      '<div class="scrim"></div><span class="spin-card__eyebrow">Rolling the dice…</span>' +
      '<div class="spin-card__place">…</div></div></div>';
  }
  function reveal(t, relaxed) {
    var uh = GOGO.usableHours(t);
    stage.innerHTML =
      '<div class="spin-card spin-reveal"><div class="spin-card__img ph--' + t.grad + '">' +
        '<div class="scrim"></div><span class="spin-card__eyebrow">Your mystery weekend</span>' +
        '<div class="spin-card__place">' + t.title + "</div></div>" +
        '<div class="spin-card__body">' +
          (relaxed ? '<p style="font-size:.86rem;color:var(--faint);margin-bottom:12px">Nothing fit that budget exactly — here’s the closest match.</p>' : "") +
          '<div class="spin-why">' +
            '<div class="weekfit__item">' + GOGO.svg(t.fly ? "plane" : "car", 18) + "<span>" + GOGO.driveLabel(t) + "</span></div>" +
            '<div class="weekfit__item">' + GOGO.svg("clock", 18) + "<b>~" + uh + " hrs</b><span>at the destination</span></div>" +
            '<div class="weekfit__item">' + GOGO.svg("check", 18) + "<b>" + verdict(uh) + "</b></div>" +
          "</div>" +
          '<div style="display:flex;align-items:baseline;gap:8px;margin-bottom:16px"><span class="filter-label" style="margin:0">From</span><span style="font-weight:800;font-size:1.6rem">' + money(t.price) + '</span><span style="color:var(--faint);font-size:.86rem">/ person · ' + t.days + ' days · ' + t.region + "</span></div>" +
          '<div class="spin-card__actions"><a class="btn btn--primary btn--lg" href="trip.html?id=' + t.id + '">See this trip →</a>' +
            '<button class="btn btn--ghost btn--lg" type="button" id="spinAgain">Spin again</button></div>' +
      "</div></div>";
    var again = $("spinAgain");
    if (again) again.addEventListener("click", spin);
  }

  function spin() {
    var relaxed = false;
    var list = pool(false);
    if (!list.length) { list = pool(true); relaxed = list.length > 0; }
    if (!list.length) { stage.innerHTML = '<div class="spin-idle">No weekend matches that vibe yet — try “Anything”.</div>'; return; }
    var final = pick(list);
    spinBtn.disabled = true;
    if (reduced()) { reveal(final, relaxed); spinBtn.disabled = false; return; }

    stage.innerHTML = spinningCard();
    var placeEl = stage.querySelector(".spin-card__place");
    var imgEl = stage.querySelector(".spin-card__img");
    var elapsed = 0, delay = 70;
    (function tick() {
      var c = list[Math.floor(Math.random() * list.length)];
      placeEl.textContent = c.region;
      imgEl.className = "spin-card__img ph--" + c.grad;
      elapsed += delay; delay += 9;
      if (elapsed < 1350) setTimeout(tick, delay);
      else { reveal(final, relaxed); spinBtn.disabled = false; }
    })();
  }

  spinBtn.addEventListener("click", spin);
  renderWho();
})();
