# GOGO! Travel — website

A small, real travel-booking website for **GOGO!** — built as plain HTML, CSS
and vanilla JavaScript with **no build step**, so it hosts anywhere and is easy
for developers to read and extend.

It is the coded version of the GOGO! design system: the red brand, the
badge-and-pin logo, the Raleway type, and four working screens.

## Pages

| File | Page | What works |
| --- | --- | --- |
| `index.html` | Home | Search widget (destination, dates, travellers), category filter, trending grid, wishlist |
| `search.html` | Search results | Price / type / duration / rating filters, sort, list ⇄ map view, empty state |
| `trip.html` | Trip detail | Photo gallery, Overview / Itinerary / Reviews tabs, day accordion, booking widget with live total |
| `planner.html` | Budget planner | Set budget + travellers + nights → best-fit trip, spend breakdown, alternatives |
| `surprise.html` | Surprise Me | A mystery-weekend generator — pick a vibe + budget and it spins up a weekend that fits |

Real navigation ties them together (Home → Search → Trip; the planner links
straight to a trip). The wishlist persists per browser via `localStorage`.

### Signature features (things the big travel sites don't do)

- **Surprise Me** (`surprise.html`) — a playful mystery-weekend generator that
  weights its pick by how much time you'd actually get away.
- **Usable weekend hours** — every trip shows the hours you really get at the
  destination once the round trip from Bangkok is subtracted (a Fri 18:00 →
  Sun 20:00 window), plus a plain-language verdict. See `GOGO.usableHours()`
  and `GOGO.driveLabel()` in `assets/js/data.js`.

## Run it locally

No install, no build. Either:

- **Open `index.html` directly** in a browser, or
- Serve the folder (nicer for clean URLs):

  ```bash
  cd gogo-travel
  python3 -m http.server 8000
  # visit http://localhost:8000
  ```

## Host it

It is a static site — deploy the `gogo-travel/` folder to any static host
(Netlify, Vercel, GitHub Pages, S3, Cloudflare Pages). No server code required.

## Project structure

```
gogo-travel/
├─ index.html · search.html · trip.html · planner.html
├─ assets/
│  ├─ favicon.svg
│  ├─ css/styles.css        # design tokens + every component
│  └─ js/
│     ├─ data.js            # trip catalogue, details, wishlist store, icons
│     ├─ site.js            # shared header/footer, card + toast helpers
│     ├─ home.js · search.js · trip.js · planner.js
```

## Customising

- **Trips** — edit the `GOGO.trips` array and `GOGO.details` in
  `assets/js/data.js`. Everything (home, search, planner, trip pages) reads
  from there.
- **Brand colour & type** — the CSS variables at the top of
  `assets/css/styles.css` (`--red`, neutrals, radii, shadows). Change `--red`
  to reshade the whole site.
- **Photography** — each destination shows a real photo layered over a gradient
  fallback (the `.ph--*` classes). Add photos to `assets/img/`, or run
  `python3 assets/img/fetch-photos.py` to pull freely-licensed ones — see
  `assets/img/README.md`. A missing photo simply falls back to the gradient, so
  nothing looks broken before you add them.

## Notes for developers

- Vanilla JS, no dependencies, no bundler. Each page loads `data.js`, then
  `site.js`, then its own page script.
- Trip prices are **per person**; the planner works in **group totals**
  (price × travellers).
- Trips are **Thailand weekend getaways**. Destinations and hotel names (in each
  trip's `stays`) are **real places**, but nightly rates, prices and ratings are
  **representative sample values** for the demo. For live figures, wire `stays`
  and prices to an **Agoda** or **Trip.com** partner/affiliate API (needs an
  account + a small backend proxy) — direct scraping of those sites isn't
  permitted and their content changes constantly.
- Other content (itineraries, reviews) is sample data too — replace it with your
  catalogue and a real booking backend.
- Auth, payments and a live search API are intentionally not included — the
  "Sign up", "Book now" and form actions are front-end stubs ready to wire up.
