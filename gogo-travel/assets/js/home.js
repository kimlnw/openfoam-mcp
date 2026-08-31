/* ==========================================================================
   GOGO! Travel — home page
   ========================================================================== */
(function () {
  "use strict";
  var GOGO = window.GOGO, $ = function (id) { return document.getElementById(id); };

  /* ---- icons in static markup ------------------------------------------- */
  $("whoDec").innerHTML = GOGO.svg("minus", 16);
  $("whoInc").innerHTML = GOGO.svg("plus", 16);
  $("searchIcon").innerHTML = GOGO.svg("search", 19);
  $("trust-rating").innerHTML =
    '<span style="display:inline-flex;align-items:center;gap:7px">' +
    '<span style="display:inline-flex;width:15px;height:15px;color:#FFC24B">' + GOGO.svg("star", 15) + "</span>4.9 average rating</span>";

  var benefitIcons = [
    GOGO.svg("check", 24),
    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    GOGO.svg("clock", 24)
  ];
  document.querySelectorAll(".benefit__ic").forEach(function (el, i) { el.innerHTML = benefitIcons[i] || ""; });

  /* ---- destination dropdown --------------------------------------------- */
  var DESTS = ["Anywhere", "Bangkok", "Chiang Mai", "Chiang Rai", "Pai", "Phuket", "Krabi", "Koh Phi Phi", "Koh Samui", "Koh Pha Ngan", "Hua Hin", "Pattaya", "Koh Samet", "Ayutthaya", "Khao Yai", "Sukhothai"];
  var dest = "Anywhere";
  var destBtn = $("destBtn"), destPanel = $("destPanel"), destVal = $("destVal");
  destPanel.innerHTML = DESTS.map(function (d) { return '<button class="dd__item" type="button" data-dest="' + d + '">' + d + "</button>"; }).join("");

  function setDest(d) {
    dest = d;
    destVal.childNodes[0].nodeValue = d + " ";
    destVal.classList.toggle("is-empty", d === "Anywhere");
    closeDest();
  }
  function openDest() { destPanel.hidden = false; destBtn.setAttribute("aria-expanded", "true"); }
  function closeDest() { destPanel.hidden = true; destBtn.setAttribute("aria-expanded", "false"); }
  destBtn.addEventListener("click", function (e) { e.stopPropagation(); destPanel.hidden ? openDest() : closeDest(); });
  destPanel.addEventListener("click", function (e) { var b = e.target.closest("[data-dest]"); if (b) setDest(b.getAttribute("data-dest")); });
  document.addEventListener("click", function (e) { if (!e.target.closest(".dd")) closeDest(); });

  /* ---- when cycle -------------------------------------------------------- */
  var WHEN = ["This weekend", "Next week", "In two weeks", "I’m flexible"];
  var wi = 0, whenVal = $("whenVal");
  $("whenBtn").addEventListener("click", function () { wi = (wi + 1) % WHEN.length; whenVal.textContent = WHEN[wi]; });

  /* ---- travelers stepper ------------------------------------------------- */
  var who = 2, whoVal = $("whoVal");
  function renderWho() { whoVal.textContent = who + (who === 1 ? " traveler" : " travelers"); }
  $("whoDec").addEventListener("click", function () { who = Math.max(1, who - 1); renderWho(); });
  $("whoInc").addEventListener("click", function () { who = Math.min(12, who + 1); renderWho(); });

  /* ---- submit search ----------------------------------------------------- */
  $("search-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var p = new URLSearchParams();
    if (dest !== "Anywhere") p.set("dest", dest);
    p.set("who", who);
    p.set("when", WHEN[wi]);
    location.href = "search.html?" + p.toString();
  });

  /* ---- trending grid + category filter ---------------------------------- */
  var CATS = ["All", "Beach", "City", "Adventure", "Cultural"];
  var cat = "All", filters = $("catFilters"), grid = $("trendingGrid"), count = $("trendingCount");
  filters.innerHTML = CATS.map(function (c) {
    return '<button class="pill" type="button" data-cat="' + c + '"' + (c === "All" ? ' aria-pressed="true"' : "") + ">" + c + "</button>";
  }).join("");

  function renderTrending() {
    var list = GOGO.trips.filter(function (t) { return cat === "All" || t.type === cat; });
    grid.innerHTML = list.map(GOGO.tripCardHTML).join("");
    count.textContent = "Showing " + list.length + " of " + GOGO.trips.length + " trips";
    GOGO.refreshHearts(grid);
  }
  filters.addEventListener("click", function (e) {
    var b = e.target.closest("[data-cat]"); if (!b) return;
    cat = b.getAttribute("data-cat");
    filters.querySelectorAll(".pill").forEach(function (p) { p.setAttribute("aria-pressed", p === b ? "true" : "false"); });
    renderTrending();
  });

  renderWho();
  renderTrending();
})();
