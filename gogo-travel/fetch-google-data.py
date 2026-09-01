#!/usr/bin/env python3
"""
Enrich GOGO! hotels with REAL Google Maps data via SerpApi.

Google Maps ratings/reviews/addresses aren't reachable without a provider, so
this uses SerpApi's Google Maps engine. It needs an API key (free tier = 100
searches/month; we query ~80 real hotels, so it fits):

    SERPAPI_KEY=xxxxx python3 fetch-google-data.py

For each real hotel it looks up the place on Google Maps and records the real
rating, review count, address, coordinates and a Maps link into
assets/data/google.json. gen-data.py then folds that into data.js so the site
shows the real numbers with a "View on Google Maps" link. Prices are NOT on
Google Maps (they come from booking partners), so those stay as sample values.

Idempotent: hotels already in google.json are skipped (saves quota) unless you
pass --refresh or delete their entry. Standard library only.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_JS = os.path.join(HERE, "assets", "js", "data.js")
OUT = os.path.join(HERE, "assets", "data", "google.json")
ENDPOINT = "https://serpapi.com/search.json"
KEY = os.environ.get("SERPAPI_KEY", "").strip()
REFRESH = "--refresh" in sys.argv
PAUSE = 0.5


def hotels_from_data_js():
    """(name, area) for every real stay in data.js (placeholders skipped)."""
    txt = open(DATA_JS, encoding="utf-8").read()
    out, seen = [], set()
    for m in re.finditer(r'\{ name: "([^"]+)", kind: "[^"]+", area: "([^"]+)"', txt):
        name, area = m.group(1), m.group(2)
        if "(representative)" in name or name in seen:
            continue
        seen.add(name)
        out.append((name, area))
    return out


def serp(query):
    q = urllib.parse.urlencode({
        "engine": "google_maps", "type": "search", "q": query,
        "hl": "en", "gl": "th", "api_key": KEY,
    })
    for i in range(4):
        try:
            req = urllib.request.Request(ENDPOINT + "?" + q, headers={"User-Agent": "GOGO-Travel-demo/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < 3:
                time.sleep(2 ** i + 1); continue
            body = e.read().decode("utf-8", "replace")[:200]
            raise RuntimeError("HTTP %s %s" % (e.code, body))
        except urllib.error.URLError:
            if i < 3:
                time.sleep(2 ** i + 1); continue
            raise
    return {}


def extract(resp):
    """Pull the best place out of a SerpApi google_maps response."""
    place = resp.get("place_results")
    if not place:
        loc = resp.get("local_results") or []
        place = loc[0] if loc else None
    if not place:
        return None
    g = place.get("gps_coordinates") or {}
    pid = place.get("place_id")
    rating = place.get("rating")
    if rating is None:
        return None
    return {
        "matched": place.get("title", ""),
        "rating": rating,
        "reviews": place.get("reviews", 0),
        "address": place.get("address", ""),
        "lat": g.get("latitude"),
        "lng": g.get("longitude"),
        "place_id": pid,
        "maps": ("https://www.google.com/maps/place/?q=place_id:" + pid) if pid else "",
    }


def main():
    if not KEY:
        sys.exit("SERPAPI_KEY is not set. Get a key at https://serpapi.com and export SERPAPI_KEY.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    store = {"source": "SerpApi Google Maps", "hotels": {}}
    if os.path.exists(OUT):
        try:
            store = json.load(open(OUT, encoding="utf-8"))
            store.setdefault("hotels", {})
        except Exception:
            store = {"source": "SerpApi Google Maps", "hotels": {}}

    hotels = hotels_from_data_js()
    got = 0
    for name, area in hotels:
        if not REFRESH and name in store["hotels"]:
            print("  = kept", name); continue
        try:
            data = extract(serp("%s, %s, Thailand" % (name, area)))
            if not data:
                print("  ! no match for", name); continue
            store["hotels"][name] = data
            got += 1
            print("  ✓ %s  → %s (%s★, %s reviews)" % (name, data["matched"], data["rating"], data["reviews"]))
        except Exception as e:
            print("  ! failed", name, "-", e)
        time.sleep(PAUSE)

    store["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    print("\nWrote %s (%d hotels total, %d new). Now run: python3 gen-data.py && python3 build-app.py"
          % (os.path.relpath(OUT, HERE), len(store["hotels"]), got))


if __name__ == "__main__":
    main()
