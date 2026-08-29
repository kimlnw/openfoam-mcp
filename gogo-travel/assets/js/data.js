/* ==========================================================================
   GOGO! Travel — shared data + helpers  (window.GOGO)
   Sample content for a starter site. Swap trips/details for your real catalogue.
   ========================================================================== */
(function () {
  "use strict";
  var GOGO = (window.GOGO = window.GOGO || {});

  /* ---- money ------------------------------------------------------------- */
  GOGO.money = function (n) { return "$" + Math.round(n).toLocaleString(); };

  /* ---- gradient "photo" strings (mirror the .ph--* CSS classes) ---------- */
  GOGO.grad = {
    bali:      "linear-gradient(150deg,#12B39B,#0E7CA8 60%,#F2B33C)",
    kyoto:     "linear-gradient(150deg,#F58FB0,#B65AC0 60%,#5B3E9E)",
    lisbon:    "linear-gradient(150deg,#FFB13C,#FF6A3D 55%,#E23E6B)",
    fjords:    "linear-gradient(150deg,#6FC7E8,#2C7FC4 58%,#243B7A)",
    patagonia: "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#3B4E9E)",
    amalfi:    "linear-gradient(150deg,#FFD36A,#FF8A3D 52%,#3AA6C4)",
    marrakech: "linear-gradient(150deg,#F2A65A,#E0533B 55%,#8E2D6B)",
    porto:     "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#3B7E9E)",
    crete:     "linear-gradient(150deg,#6FD3E8,#2C9FC4 58%,#1E6C8A)"
  };
  GOGO.gradCss = function (name) { return GOGO.grad[name] || GOGO.grad.bali; };

  /* ---- catalogue --------------------------------------------------------- */
  GOGO.trips = [
    { id: "porto", title: "Porto City Weekend", country: "Portugal", region: "Northern Portugal", days: 3, rating: 4.6, price: 540, type: "City", grad: "porto", tags: ["City break", "Wine"], blurb: "Tiled lanes, port-wine cellars and the Douro at golden hour." },
    { id: "crete", title: "Crete Island Hop", country: "Greece", region: "Crete", days: 5, rating: 4.6, price: 760, type: "Beach", grad: "crete", tags: ["Beach", "Boat"], blurb: "Pink-sand coves, mountain villages and long seaside lunches." },
    { id: "marrakech", title: "Marrakech & the Atlas", country: "Morocco", region: "Marrakech", days: 5, rating: 4.6, price: 890, type: "Cultural", grad: "marrakech", tags: ["Culture", "Desert"], blurb: "Souks and riads, then a Berber village in the High Atlas foothills." },
    { id: "lisbon", title: "Lisbon to the Algarve", country: "Portugal", region: "Lisbon & Algarve", days: 6, rating: 4.7, price: 980, type: "City", grad: "lisbon", tags: ["City break", "Coast"], blurb: "Tiled streets, coastal trains and golden-hour miradouros." },
    { id: "bali", title: "Bali & the Nusa Islands", country: "Indonesia", region: "Bali", days: 7, rating: 4.9, price: 1240, type: "Beach", grad: "bali", tags: ["Island-hopping", "Snorkelling"], blurb: "Rice terraces, island-hopping and reef snorkelling on a relaxed loop." },
    { id: "amalfi", title: "Amalfi Coast Escape", country: "Italy", region: "Amalfi Coast", days: 6, rating: 4.8, price: 1560, type: "Beach", grad: "amalfi", tags: ["Coast", "Food"], blurb: "Cliffside villages, lemon groves and long lunches above the sea." },
    { id: "kyoto", title: "Kyoto Temple Trail", country: "Japan", region: "Kyoto", days: 5, rating: 4.8, price: 1690, type: "City", grad: "kyoto", tags: ["Culture", "Food"], blurb: "Historic shrines, tea houses and the lantern-lit Gion district." },
    { id: "fjords", title: "Fjords & Northern Lights", country: "Norway", region: "Norwegian Fjords", days: 8, rating: 4.9, price: 2150, type: "Adventure", grad: "fjords", tags: ["Aurora", "Fjords"], blurb: "Deep fjords by day, aurora hunting by night, above the Arctic line." },
    { id: "patagonia", title: "Patagonia Wild Trek", country: "Chile", region: "Patagonia", days: 10, rating: 4.9, price: 2480, type: "Adventure", grad: "patagonia", tags: ["Trekking", "Glaciers"], blurb: "Granite spires, glacier valleys and the classic W circuit." }
  ];

  GOGO.getTrip = function (id) {
    for (var i = 0; i < GOGO.trips.length; i++) if (GOGO.trips[i].id === id) return GOGO.trips[i];
    return null;
  };

  /* ---- shared detail fragments ------------------------------------------ */
  var INCLUDED = ["Boutique stays, every night", "Daily breakfast", "Private airport transfers", "A local guide on the key days", "24/7 support before and during"];
  var NOT_INCLUDED = ["International flights", "Travel insurance", "Some lunches & dinners"];
  var REVIEWS = [
    { who: "Maya R.", when: "Travelled recently", initials: "MR", grad: "bali", text: "Perfectly paced and zero logistics stress. Our guide knew exactly when to beat the crowds." },
    { who: "Jordan L.", when: "Travelled recently", initials: "JL", grad: "lisbon", text: "The stays were lovely and the price really was the price — no surprise fees. Would book again." }
  ];

  /* ---- rich details for featured trips ---------------------------------- */
  GOGO.details = {
    bali: {
      gallery: [
        { bg: "linear-gradient(150deg,#12B39B,#0E7CA8 60%,#F2B33C)", cap: "Nusa Penida coast" },
        { bg: "linear-gradient(150deg,#F2A65A,#E0533B 55%,#8E2D6B)", cap: "Ubud temples" },
        { bg: "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#2F7E52)", cap: "Tegallalang rice terraces" },
        { bg: "linear-gradient(160deg,#FFC24B,#FF6A3D 50%,#C4326B)", cap: "Uluwatu sunset" },
        { bg: "linear-gradient(150deg,#6FD3E8,#2C9FC4 58%,#1E6C8A)", cap: "Island aerial" }
      ],
      itinerary: [
        { d: 1, t: "Arrive in Bali · settle in Ubud", text: "Airport pickup and a scenic transfer to your rice-paddy villa near Ubud. Welcome dinner in the evening." },
        { d: 2, t: "Ubud culture & terraces", text: "Sacred Monkey Forest, a working art village, and the Tegallalang rice terraces at golden hour." },
        { d: 3, t: "Waterfalls & hidden temples", text: "Jungle waterfalls in the morning, then the water temple at Tirta Empul before a slow valley lunch." },
        { d: 4, t: "Boat to Nusa Penida", text: "Fast boat across for Kelingking viewpoint and an afternoon snorkel with manta rays (season permitting)." },
        { d: 5, t: "Nusa Lembongan", text: "Mangrove kayaking, the Yellow Bridge and easy beach time. Sunset from a clifftop warung." },
        { d: 6, t: "Uluwatu & the south", text: "The Uluwatu clifftop temple, a Kecak fire dance, and fresh seafood on the sand at Jimbaran." },
        { d: 7, t: "Departure", text: "A relaxed breakfast and transfer to the airport — or extend your stay, we can help arrange it." }
      ],
      included: INCLUDED, notIncluded: NOT_INCLUDED, reviews: REVIEWS
    },
    kyoto: {
      gallery: [
        { bg: "linear-gradient(150deg,#F58FB0,#B65AC0 60%,#5B3E9E)", cap: "Fushimi Inari gates" },
        { bg: "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#2F7E52)", cap: "Arashiyama bamboo" },
        { bg: "linear-gradient(160deg,#FFC24B,#FF6A3D 50%,#C4326B)", cap: "Gion at dusk" },
        { bg: "linear-gradient(150deg,#6FC7E8,#2C7FC4 58%,#243B7A)", cap: "Kinkaku-ji" },
        { bg: "linear-gradient(150deg,#F2A65A,#E0533B 55%,#8E2D6B)", cap: "Tea house lane" }
      ],
      itinerary: [
        { d: 1, t: "Arrive in Kyoto", text: "Transfer to a machiya townhouse near the river. Evening stroll through the Pontocho lanes." },
        { d: 2, t: "Southern shrines", text: "The thousand vermilion gates of Fushimi Inari early, then Tofuku-ji and a kaiseki lunch." },
        { d: 3, t: "Arashiyama", text: "Bamboo grove, the Katsura river, and a monkey park with a view over the whole city." },
        { d: 4, t: "Temples & tea", text: "Kinkaku-ji, a guided matcha ceremony, and free time in the Nishiki market." },
        { d: 5, t: "Departure", text: "Morning in the Gion district, then transfer for onward travel." }
      ],
      included: INCLUDED, notIncluded: NOT_INCLUDED, reviews: REVIEWS
    },
    patagonia: {
      gallery: [
        { bg: "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#3B4E9E)", cap: "Torres del Paine" },
        { bg: "linear-gradient(150deg,#6FC7E8,#2C7FC4 58%,#243B7A)", cap: "Grey Glacier" },
        { bg: "linear-gradient(150deg,#FFD36A,#FF8A3D 52%,#3AA6C4)", cap: "Patagonian steppe" },
        { bg: "linear-gradient(150deg,#12B39B,#0E7CA8 60%,#F2B33C)", cap: "Valley trail" },
        { bg: "linear-gradient(160deg,#FFC24B,#FF6A3D 50%,#C4326B)", cap: "Camp at dawn" }
      ],
      itinerary: [
        { d: 1, t: "Arrive in Punta Arenas", text: "Meet the group and transfer north toward the park. First night under big Patagonian skies." },
        { d: 2, t: "Base of the Towers", text: "The classic day hike to the granite towers and their glacial lake." },
        { d: 3, t: "French Valley", text: "Into the heart of the W circuit, with hanging glaciers on every side." },
        { d: 4, t: "Grey Glacier", text: "A boat to the glacier face, then an easy shoreline walk among the icebergs." },
        { d: 5, t: "Rest & steppe wildlife", text: "A slower day: guanacos, condors, and time to recover before the long crossings." }
      ],
      included: INCLUDED, notIncluded: NOT_INCLUDED, reviews: REVIEWS
    }
  };

  /* Build a full detail object for ANY trip (rich if featured, else a sensible fallback). */
  GOGO.buildDetail = function (trip) {
    if (GOGO.details[trip.id]) return GOGO.details[trip.id];
    var base = GOGO.gradCss(trip.grad);
    var gallery = [
      { bg: base, cap: trip.region + " views" },
      { bg: "linear-gradient(150deg,#FFD36A,#FF8A3D 52%,#3AA6C4)", cap: "On the trip" },
      { bg: "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#2F7E52)", cap: "Local life" }
    ];
    var itinerary = [];
    for (var d = 1; d <= trip.days; d++) {
      if (d === 1) itinerary.push({ d: d, t: "Arrive in " + trip.region, text: "Airport pickup, check in, and a relaxed evening to settle in." });
      else if (d === trip.days) itinerary.push({ d: d, t: "Departure", text: "A final breakfast and transfer for onward travel." });
      else itinerary.push({ d: d, t: "Explore " + trip.region, text: "A guided day through the highlights, with free time to wander at your own pace." });
    }
    return { gallery: gallery, itinerary: itinerary, included: INCLUDED, notIncluded: NOT_INCLUDED, reviews: REVIEWS };
  };

  /* ---- wishlist (localStorage, per-viewer) ------------------------------- */
  var WKEY = "gogo:wishlist";
  GOGO.wish = {
    get: function () {
      try { return JSON.parse(localStorage.getItem(WKEY) || "[]"); } catch (e) { return []; }
    },
    has: function (id) { return this.get().indexOf(id) !== -1; },
    toggle: function (id) {
      var list = this.get(), i = list.indexOf(id);
      if (i === -1) list.push(id); else list.splice(i, 1);
      try { localStorage.setItem(WKEY, JSON.stringify(list)); } catch (e) {}
      return this.has(id);
    }
  };

  /* ---- inline SVG icons -------------------------------------------------- */
  GOGO.icon = {
    pinFilled: '<svg width="18" height="18" viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 12.5 7 12.5s7-7.3 7-12.5a7 7 0 0 0-7-7z" fill="#fff"/><circle cx="12" cy="9" r="2.7" fill="#E01F26"/></svg>',
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.4"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    chevron: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>',
    star: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.9 21l1.2-6.8-5-4.9 6.9-1z"/></svg>',
    heart: '<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-.9-1.1a5.5 5.5 0 1 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/></svg>',
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    minus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>',
    clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    shield: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>',
    calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="17" rx="3"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/></svg>',
    list: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>',
    map: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg>'
  };
})();
