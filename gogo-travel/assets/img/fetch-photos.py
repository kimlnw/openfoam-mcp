#!/usr/bin/env python3
"""
Fetch real destination photos for the GOGO! website from Wikimedia Commons.

Run it on a machine with normal internet access:

    cd gogo-travel/assets/img
    python3 fetch-photos.py

It downloads one freely-licensed photo per destination (already resized by
Commons) into this folder as <id>.jpg, and writes CREDITS.md with the author,
licence and source page for each. Most Commons photos require attribution, so
keep CREDITS.md with the site.

Standard library only — no pip installs. Re-run any time to refresh. Prefer your
own photos? Just drop <id>.jpg files here with these names and skip the script.
"""
import json, os, re, urllib.parse, urllib.request

WIDTH = 1400
UA = "GOGO-Travel-demo/1.0 (educational sample site)"
API = "https://commons.wikimedia.org/w/api.php"

# id -> Commons search term (iconic, well-photographed subjects)
QUERIES = {
    "pattaya":      "Pattaya Beach Thailand",
    "huahin":       "Hua Hin beach Thailand",
    "samet":        "Ko Samet beach",
    "ayutthaya":    "Ayutthaya historical park temple",
    "amphawa":      "Amphawa floating market",
    "chiangmai":    "Wat Phra That Doi Suthep Chiang Mai",
    "kanchanaburi": "Bridge over the River Kwai Kanchanaburi",
    "khaoyai":      "Khao Yai National Park landscape",
    "bangkok":      "Wat Arun Bangkok",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def strip_html(s):
    return re.sub("<[^>]+>", "", s or "").strip()


def find_image(term):
    q = {
        "action": "query", "format": "json",
        "generator": "search", "gsrsearch": term + " filetype:bitmap",
        "gsrnamespace": "6", "gsrlimit": "1",
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": str(WIDTH),
    }
    data = json.loads(get(API + "?" + urllib.parse.urlencode(q)))
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None
    info = list(pages.values())[0]["imageinfo"][0]
    meta = info.get("extmetadata", {})
    return {
        "thumb": info.get("thumburl") or info.get("url"),
        "page": info.get("descriptionurl", ""),
        "artist": strip_html(meta.get("Artist", {}).get("value", "")) or "Unknown",
        "license": (meta.get("LicenseShortName", {}) or {}).get("value", "see source"),
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    credits = ["# Photo credits\n",
               "Destination photos from Wikimedia Commons. Keep attribution with the site.\n"]
    ok = 0
    for tid, term in QUERIES.items():
        try:
            img = find_image(term)
            if not img or not img["thumb"]:
                print("  ! no result for", tid)
                continue
            with open(os.path.join(here, tid + ".jpg"), "wb") as f:
                f.write(get(img["thumb"]))
            credits.append("- **%s.jpg** — %s · %s · %s" % (tid, img["artist"], img["license"], img["page"]))
            print("  ✓ %s.jpg  (%s)" % (tid, img["license"]))
            ok += 1
        except Exception as e:
            print("  ! failed", tid, "-", e)
    with open(os.path.join(here, "CREDITS.md"), "w") as f:
        f.write("\n".join(credits) + "\n")
    print("\nDone: %d/%d photos. Wrote CREDITS.md." % (ok, len(QUERIES)))
    if ok < len(QUERIES):
        print("Tip: tweak the QUERIES terms, or drop your own <id>.jpg files here.")


if __name__ == "__main__":
    main()
