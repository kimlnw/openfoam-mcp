/* ==========================================================================
   GOGO! Travel — trip detail
   ========================================================================== */
(function () {
  "use strict";
  var GOGO = window.GOGO, money = GOGO.money, $ = function (id) { return document.getElementById(id); };

  var trip = GOGO.getTrip(GOGO.params().get("id"));
  if (!trip) {
    $("trip-root").innerHTML = '<div class="empty" style="margin:60px 0"><h3 style="font-size:1.3rem">Trip not found</h3>' +
      '<p style="color:var(--ink-soft);margin-top:8px">That trip isn’t available. <a href="search.html">Browse all trips →</a></p></div>';
    return;
  }
  var detail = GOGO.buildDetail(trip);

  var st = { img: 0, tab: "overview", openDay: 1, travelers: 2, dateIndex: 0 };
  var DATES = ["12–19 Mar 2026", "2–9 Apr 2026", "7–14 May 2026"];

  document.title = trip.title + " — GOGO!";

  /* ---- crumb + gallery --------------------------------------------------- */
  $("crumb").textContent = trip.country + " · " + trip.region;

  function renderGallery() {
    var g = detail.gallery;
    $("gMain").style.background = g[st.img].bg;
    $("gCap").textContent = g[st.img].cap;
    $("thumbs").innerHTML = g.map(function (im, i) {
      return '<button class="thumb' + (i === st.img ? " is-active" : "") + '" type="button" data-i="' + i + '" style="background:' + im.bg + '" aria-label="Photo ' + (i + 1) + '"></button>';
    }).join("");
  }
  $("thumbs").addEventListener("click", function (e) {
    var b = e.target.closest("[data-i]"); if (!b) return;
    st.img = parseInt(b.getAttribute("data-i"), 10); renderGallery();
  });

  /* ---- title + meta + actions ------------------------------------------- */
  $("tripTitle").textContent = trip.title;
  $("tripMeta").innerHTML =
    '<span><span class="star" style="display:inline-flex;width:15px;height:15px;color:var(--gold)">' + GOGO.svg("star", 15) + "</span><b style=\"color:var(--ink)\">" + trip.rating + "</b> · 218 reviews</span>" +
    "<span>" + GOGO.svg("pin", 15) + trip.region + ", " + trip.country + "</span>" +
    "<span>" + GOGO.svg("clock", 15) + trip.days + " days</span>";

  var saved = GOGO.wish.has(trip.id);
  $("tripActions").innerHTML =
    '<button class="heart" type="button" id="saveBtn" aria-pressed="' + saved + '">' + GOGO.svg("heart", 17) + '<span id="saveLabel">' + (saved ? "Saved" : "Save") + "</span></button>" +
    '<button class="heart" type="button" id="shareBtn" style="color:var(--ink-soft)"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>Share</button>';
  $("saveBtn").addEventListener("click", function () {
    var on = GOGO.wish.toggle(trip.id);
    this.setAttribute("aria-pressed", on ? "true" : "false");
    $("saveLabel").textContent = on ? "Saved" : "Save";
  });
  $("shareBtn").addEventListener("click", function () {
    try { if (navigator.clipboard) navigator.clipboard.writeText(location.href); } catch (e) {}
    GOGO.toast("Link copied to clipboard");
  });

  /* ---- tabs -------------------------------------------------------------- */
  var TABS = [{ k: "overview", label: "Overview" }, { k: "itinerary", label: "Itinerary" }, { k: "reviews", label: "Reviews" }];
  $("tabs").innerHTML = TABS.map(function (t) {
    return '<button class="tab' + (t.k === st.tab ? " is-active" : "") + '" type="button" data-tab="' + t.k + '">' + t.label + "</button>";
  }).join("");
  $("tabs").addEventListener("click", function (e) {
    var b = e.target.closest("[data-tab]"); if (!b) return;
    st.tab = b.getAttribute("data-tab");
    $("tabs").querySelectorAll(".tab").forEach(function (x) { x.classList.toggle("is-active", x === b); });
    ["overview", "itinerary", "reviews"].forEach(function (k) { $("panel-" + k).hidden = (k !== st.tab); });
  });

  /* ---- overview panel ---------------------------------------------------- */
  function inclRow(text, yes) {
    return '<span class="incl-row ' + (yes ? "yes" : "no") + '">' + GOGO.svg(yes ? "check" : "x", 19) + "<span>" + text + "</span></span>";
  }
  $("panel-overview").innerHTML =
    '<p style="font-size:1.05rem;color:#2B3040">' + trip.blurb + "</p>" +
    '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:18px">' +
      trip.tags.concat(["Small group · max 12"]).map(function (tg) {
        return '<span style="font-size:.82rem;font-weight:700;color:var(--ink-soft);background:var(--surface);border:1px solid var(--line);padding:7px 13px;border-radius:999px">' + tg + "</span>";
      }).join("") +
    "</div>" +
    '<div class="incl-grid">' +
      '<div><h3 style="font-size:1.15rem;margin-bottom:14px">What’s included</h3><div class="incl">' + detail.included.map(function (t) { return inclRow(t, true); }).join("") + "</div></div>" +
      '<div><h3 style="font-size:1.15rem;margin-bottom:14px">Not included</h3><div class="incl">' + detail.notIncluded.map(function (t) { return inclRow(t, false); }).join("") + "</div></div>" +
    "</div>" +
    '<div style="position:relative;height:180px;border-radius:16px;overflow:hidden;margin-top:28px;border:1px solid var(--line);background:linear-gradient(160deg,#DCE9E4,#CFE0EC 55%,#E7E1D6)">' +
      '<div class="mapview__grid"></div>' +
      '<div style="position:absolute;left:38%;top:46%;transform:translate(-50%,-100%)"><div style="background:var(--red);width:30px;height:30px;border-radius:50% 50% 50% 2px;transform:rotate(45deg);box-shadow:0 8px 16px -6px rgba(0,0,0,.5)"></div></div>' +
      '<span style="position:absolute;right:16px;bottom:14px;background:rgba(255,255,255,.94);font-weight:700;font-size:.82rem;padding:7px 13px;border-radius:10px">' + trip.region + "</span></div>";

  /* ---- itinerary panel --------------------------------------------------- */
  function renderItinerary() {
    $("panel-itinerary").innerHTML =
      '<div class="card" style="padding:6px 22px">' + detail.itinerary.map(function (d) {
        var open = d.d === st.openDay;
        return '<div class="day' + (open ? " is-open" : "") + '">' +
          '<button class="day-head" type="button" data-day="' + d.d + '"><span class="day-num">Day ' + d.d + '</span><span class="day-title">' + d.t + "</span>" + GOGO.svg("chevron", 18) + "</button>" +
          (open ? '<p class="day-body">' + d.text + "</p>" : "") +
        "</div>";
      }).join("") + "</div>";
  }
  $("panel-itinerary").addEventListener("click", function (e) {
    var b = e.target.closest("[data-day]"); if (!b) return;
    var d = parseInt(b.getAttribute("data-day"), 10);
    st.openDay = (st.openDay === d ? 0 : d);
    renderItinerary();
  });

  /* ---- reviews panel ----------------------------------------------------- */
  var barW = ["86%", "10%", "3%", "1%", "0%"];
  $("panel-reviews").innerHTML =
    '<div class="rating-summary"><div><div class="rating-big">' + trip.rating + '</div>' +
      '<div style="display:flex;gap:2px;justify-content:center;margin-top:4px;color:var(--gold)">' + Array(5).join(0).split("").map(function () { return '<span style="width:15px;height:15px;display:inline-flex">' + GOGO.svg("star", 15) + "</span>"; }).join("") + "</div>" +
      '<div style="font-size:.8rem;color:var(--faint);margin-top:6px;text-align:center">218 reviews</div></div>' +
      '<div class="bars">' + [5, 4, 3, 2, 1].map(function (n, i) {
        return '<div class="bar-row"><span class="filter-label" style="margin:0;width:14px">' + n + '</span><div class="bar-tk"><i style="width:' + barW[i] + '"></i></div></div>';
      }).join("") + "</div></div>" +
    '<div style="display:flex;flex-direction:column;gap:14px">' + detail.reviews.map(function (r) {
      return '<div class="review"><div class="review__who"><div class="review__av ph--' + r.grad + '">' + r.initials + "</div>" +
        '<div><div style="font-weight:800;font-size:.94rem">' + r.who + '</div><div class="filter-label" style="margin:0">' + r.when + "</div></div></div>" +
        '<p style="font-size:.94rem;color:#2B3040;margin-top:11px">' + r.text + "</p></div>";
    }).join("") + "</div>";

  /* ---- booking widget ---------------------------------------------------- */
  function renderBooking() {
    var subtotal = trip.price * st.travelers;
    $("booking").innerHTML =
      '<div class="booking__card">' +
        '<div class="booking__from"><span class="filter-label" style="margin:0">From</span><span class="booking__price">' + money(trip.price) + '</span><span style="font-size:.86rem;color:var(--faint)">/ person</span></div>' +
        '<div style="margin-top:18px;display:flex;flex-direction:column;gap:10px">' +
          '<button class="field" type="button" id="dateField">' + GOGO.svg("calendar", 18) + '<span style="flex:1"><span class="k">Dates</span><span class="v">' + DATES[st.dateIndex] + "</span></span>" + GOGO.svg("chevron", 15) + "</button>" +
          '<div class="field field--row"><span><span class="k">Travelers</span><span class="v">' + st.travelers + (st.travelers === 1 ? " traveler" : " travelers") + "</span></span>" +
            '<span style="display:flex;align-items:center;gap:12px"><button class="step fx" type="button" id="bDec">' + GOGO.svg("minus", 15) + '</button><button class="step fx" type="button" id="bInc">' + GOGO.svg("plus", 15) + "</button></span></div>" +
        "</div>" +
        '<div style="margin-top:18px;display:flex;flex-direction:column;gap:9px"><div class="brk"><span>' + money(trip.price) + " × " + st.travelers + '</span><span class="tnum">' + money(subtotal) + '</span></div>' +
          '<div class="brk"><span>Taxes &amp; fees</span><span style="color:var(--teal);font-weight:700">Included</span></div></div>' +
        '<hr class="divider" style="margin:14px 0">' +
        '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:16px"><span style="font-weight:800">Total</span><span class="booking__price tnum" style="font-size:1.5rem">' + money(subtotal) + "</span></div>" +
        '<button class="btn btn--primary btn--block btn--lg" type="button" id="bookBtn">Book now</button>' +
        '<p style="display:flex;align-items:center;justify-content:center;gap:7px;font-size:.82rem;color:var(--ink-soft);margin-top:12px">' + GOGO.svg("shield", 14) + "Free cancellation up to 48h</p>" +
      "</div>";
    $("dateField").addEventListener("click", function () { st.dateIndex = (st.dateIndex + 1) % DATES.length; renderBooking(); });
    $("bDec").addEventListener("click", function () { st.travelers = Math.max(1, st.travelers - 1); renderBooking(); });
    $("bInc").addEventListener("click", function () { st.travelers = Math.min(12, st.travelers + 1); renderBooking(); });
    $("bookBtn").addEventListener("click", function () {
      GOGO.toast("Trip held — " + st.travelers + (st.travelers === 1 ? " traveler" : " travelers") + " · " + money(trip.price * st.travelers) + ". We’ll email your itinerary.");
    });
  }

  renderGallery();
  renderItinerary();
  renderBooking();
})();
