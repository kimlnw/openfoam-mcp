/* ==========================================================================
   GOGO! Travel — shared site chrome + helpers
   Injects the header/footer, wires wishlist hearts, exposes card + toast utils.
   ========================================================================== */
(function () {
  "use strict";
  var GOGO = (window.GOGO = window.GOGO || {});
  var money = GOGO.money, icon = GOGO.icon;

  /* return an icon string with an explicit pixel size */
  GOGO.svg = function (name, size) {
    var s = icon[name] || "";
    return s.replace("<svg ", '<svg width="' + size + '" height="' + size + '" ');
  };

  /* brand lockup markup (logo A: red badge + filled pin + wordmark) */
  GOGO.brandHTML = function (small) {
    return '<a class="brand ' + (small ? "brand--sm" : "") + '" href="index.html" aria-label="GOGO! home">' +
      '<span class="brand__badge">' + GOGO.svg("pinFilled", small ? 16 : 18) + "</span>" +
      '<span class="brand__word">GOGO<b>!</b></span></a>';
  };

  var NAV = [
    { label: "Destinations", href: "search.html" },
    { label: "Experiences", href: "search.html" },
    { label: "Deals", href: "#" },
    { label: "About", href: "#" }
  ];

  function headerHTML() {
    var links = NAV.map(function (n) { return '<a href="' + n.href + '">' + n.label + "</a>"; }).join("");
    return '<div class="wrap site-header__inner">' +
      GOGO.brandHTML(false) +
      '<nav class="site-nav">' + links + "</nav>" +
      '<div class="site-header__cta">' +
        '<a class="site-header__signin" href="#">Sign in</a>' +
        '<a class="btn btn--primary" href="#">Sign up</a>' +
      "</div></div>";
  }

  function footerHTML() {
    function col(title, items) {
      return '<div class="foot-col"><h4>' + title + "</h4>" +
        items.map(function (t) { return '<a href="#">' + t + "</a>"; }).join("") + "</div>";
    }
    return '<div class="wrap"><div class="site-footer__grid">' +
      "<div>" + GOGO.brandHTML(true) +
        '<p class="tag">Small-group and independent trips, priced honestly. Go somewhere good.</p></div>' +
      col("Explore", ["Destinations", "Experiences", "Deals", "Travel guides"]) +
      col("Company", ["About", "Careers", "Sustainability", "Contact"]) +
      col("Support", ["Help centre", "Cancellation", "Safety", "Terms"]) +
      "</div>" +
      '<p class="wrap site-footer__legal" style="padding:0">© 2026 GOGO! Travel — [YOUR COMPANY DETAILS]</p></div>';
  }

  /* ---- trip card --------------------------------------------------------- */
  GOGO.tripCardHTML = function (t) {
    return '<a class="tcard lift" href="trip.html?id=' + t.id + '">' +
      '<div class="tcard__img ph ph--' + t.grad + '">' +
        '<button class="heart img-heart" type="button" data-wish="' + t.id + '" aria-pressed="false" aria-label="Save ' + t.title + '">' + GOGO.svg("heart", 19) + "</button>" +
        '<span class="loc">' + t.country + "</span></div>" +
      '<div class="tcard__body"><div class="tcard__title">' + t.title + "</div>" +
        '<div class="tcard__meta">' +
          '<span class="tcard__rating"><span class="star" style="display:inline-flex;width:13px;height:13px">' + GOGO.svg("star", 13) + "</span>" + t.rating + " · " + t.days + " days</span>" +
          '<span class="tcard__price">' + money(t.price) + "</span>" +
        "</div></div></a>";
  };

  /* ---- wishlist hearts (delegated) -------------------------------------- */
  GOGO.refreshHearts = function (root) {
    (root || document).querySelectorAll("[data-wish]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", GOGO.wish.has(btn.getAttribute("data-wish")) ? "true" : "false");
    });
  };
  function onHeartClick(e) {
    var btn = e.target.closest("[data-wish]");
    if (!btn) return;
    e.preventDefault(); e.stopPropagation();
    var on = GOGO.wish.toggle(btn.getAttribute("data-wish"));
    btn.setAttribute("aria-pressed", on ? "true" : "false");
  }

  /* ---- toast ------------------------------------------------------------- */
  var toastEl, toastTimer;
  GOGO.toast = function (msg) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.className = "toast";
      document.body.appendChild(toastEl);
    }
    toastEl.innerHTML = GOGO.svg("check", 18) + "<span>" + msg + "</span>";
    void toastEl.offsetWidth;
    toastEl.classList.add("is-show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-show"); }, 3800);
  };

  /* ---- query string helper ---------------------------------------------- */
  GOGO.params = function () { return new URLSearchParams(location.search); };

  /* ---- reveal on scroll -------------------------------------------------- */
  function initReveal() {
    var els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) { els.forEach(function (e) { e.classList.add("in"); }); return; }
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: .12 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* ---- mount ------------------------------------------------------------- */
  function mount() {
    document.documentElement.classList.remove("no-js");
    var h = document.getElementById("site-header");
    var f = document.getElementById("site-footer");
    if (h) { h.className = "site-header"; h.innerHTML = headerHTML(); }
    if (f) { f.className = "site-footer"; f.innerHTML = footerHTML(); }

    // highlight active nav
    var page = document.body.getAttribute("data-page");
    if (page === "search" && h) {
      var first = h.querySelector('.site-nav a[href="search.html"]');
      if (first) first.setAttribute("aria-current", "page");
    }

    document.addEventListener("click", onHeartClick);
    GOGO.refreshHearts(document);
    initReveal();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
})();
