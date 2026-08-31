#!/usr/bin/env python3
"""
Fetch real, place-matched destination photos for the GOGO! website from
Wikimedia Commons (freely licensed, mostly CC-BY / public domain).

Run it on a machine with normal internet access (NOT inside a locked-down
sandbox — Commons must be reachable):

    cd gogo-travel/assets/img
    python3 fetch-photos.py

For each destination it searches Commons for the iconic subject, prefers a
landscape photo, downloads it (already resized by Commons) as <id>.jpg, and
writes CREDITS.md with author, licence and source page. Most Commons photos
require attribution — keep CREDITS.md with the site.

Then, to see the photos:
  • Multi-file site (index.html, GitHub Pages, ...): nothing else to do — the
    CSS already layers assets/img/<id>.jpg over each gradient, and the trip
    hero picks it up too.
  • Single-file build / hosted artifact: re-run `python3 ../../build-app.py`,
    which embeds any photos found here straight into gogo-app.html.

Standard library only — no pip installs. Re-run any time to refresh. Prefer your
own photos? Just drop <id>.jpg files here with these names and skip the script.
"""
import json, os, re, urllib.parse, urllib.request

WIDTH = 1400
MIN_W = 900
UA = "GOGO-Travel-demo/1.0 (educational sample site)"
API = "https://commons.wikimedia.org/w/api.php"

# id -> ordered list of Commons search terms (iconic, well-photographed, and
# specific to the place). The first term that returns a good landscape photo
# wins; the rest are fallbacks so a single miss doesn't leave a blank card.
QUERIES = {
    "amphawa":       ["Amphawa floating market", "Amphawa canal Samut Songkhram", "Maeklong railway market"],
    "ayutthaya":     ["Wat Chaiwatthanaram Ayutthaya", "Ayutthaya historical park temple", "Wat Mahathat Ayutthaya"],
    "pattaya":       ["Pattaya Beach aerial", "Pattaya Beach Thailand", "Pattaya city viewpoint"],
    "bangkok":       ["Wat Arun Bangkok", "Bangkok Chao Phraya river skyline", "Grand Palace Bangkok"],
    "kanchanaburi":  ["Bridge over the River Kwai Kanchanaburi", "Erawan Falls Kanchanaburi", "River Kwai Kanchanaburi"],
    "samet":         ["Sai Kaew Beach Ko Samet", "Ko Samet beach", "Koh Samet island Thailand"],
    "huahin":        ["Hua Hin Railway Station", "Hua Hin beach Thailand", "Hua Hin Prachuap Khiri Khan"],
    "chiangmai":     ["Wat Phra That Doi Suthep Chiang Mai", "Wat Chedi Luang Chiang Mai", "Chiang Mai old city temple"],
    "khaoyai":       ["Haew Suwat Waterfall Khao Yai", "Khao Yai National Park viewpoint", "Khao Yai National Park landscape"],
    "lopburi":       ["Phra Prang Sam Yot Lopburi", "Lopburi monkey temple", "Lopburi sunflower field"],
    "kohchang":      ["Koh Chang Thailand beach", "White Sand Beach Koh Chang", "Koh Chang island viewpoint"],
    "kohkood":       ["Koh Kood island beach", "Ko Kut Thailand", "Koh Kood waterfall"],
    "chanthaburi":   ["Chanthaburi Cathedral", "Chanthaburi old town riverfront", "Namtok Phlio waterfall"],
    "chiangrai":     ["Wat Rong Khun White Temple Chiang Rai", "Wat Rong Suea Ten Blue Temple", "Chiang Rai Singha Park"],
    "pai":           ["Pai Canyon Mae Hong Son", "Pai valley Thailand", "Pai bamboo bridge Boon Ko Ku So"],
    "nan":           ["Wat Phumin Nan", "Wat Phra That Khao Noi Nan", "Nan province Thailand landscape"],
    "sukhothai":     ["Sukhothai Historical Park Wat Mahathat", "Wat Si Chum Sukhothai", "Sukhothai Buddha statue"],
    "ubon":          ["Sam Phan Bok Ubon Ratchathani", "Pha Taem National Park", "Ubon Ratchathani candle festival"],
    "chiangkhan":    ["Chiang Khan Walking Street Loei", "Chiang Khan Mekong river", "Phu Thok Chiang Khan"],
    "samui":         ["Koh Samui beach Thailand", "Big Buddha Koh Samui", "Chaweng Beach Samui"],
    "phangan":       ["Koh Phangan beach", "Than Sadet waterfall Koh Phangan", "Koh Phangan viewpoint"],
    "kohtao":        ["Koh Nang Yuan", "Koh Tao island viewpoint", "Koh Tao beach Thailand"],
    "khaosok":       ["Khao Sok National Park Cheow Lan Lake", "Khao Sok limestone", "Khao Sok rainforest"],
    "phuket":        ["Phuket Old Town", "Kata Beach Phuket", "Phuket Big Buddha viewpoint"],
    "krabi":         ["Railay Beach Krabi", "Phra Nang Beach Krabi", "Krabi Thailand limestone"],
    "phiphi":        ["Koh Phi Phi viewpoint", "Maya Bay Phi Phi", "Phi Phi islands Thailand"],
    "phangnga":      ["James Bond Island Phang Nga", "Phang Nga Bay Thailand", "Koh Panyee"],
    "kholanta":      ["Koh Lanta beach Thailand", "Koh Lanta old town", "Mu Ko Lanta lighthouse"],
    "khaolak":       ["Khao Lak beach Thailand", "Similan Islands", "Khao Lak sunset"],
    "lipe":          ["Koh Lipe beach Thailand", "Sunrise Beach Koh Lipe", "Koh Lipe Andaman"],
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def strip_html(s):
    return re.sub("<[^>]+>", "", s or "").strip()


def search(term, limit=8):
    """Return a list of candidate image-info dicts for one search term."""
    q = {
        "action": "query", "format": "json",
        "generator": "search", "gsrsearch": term + " filetype:bitmap",
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": str(WIDTH),
    }
    data = json.loads(get(API + "?" + urllib.parse.urlencode(q)))
    pages = data.get("query", {}).get("pages", {})
    # search results come back keyed by page id; sort by the search index
    ordered = sorted(pages.values(), key=lambda p: p.get("index", 1e9))
    out = []
    for p in ordered:
        ii = p.get("imageinfo")
        if ii:
            out.append(ii[0])
    return out


def pick(term):
    """Best candidate for a term: first landscape >= MIN_W wide, else first."""
    cands = search(term)
    for info in cands:
        w, h = info.get("width", 0), info.get("height", 1)
        if w >= MIN_W and w >= h:            # decent, landscape
            return info
    return cands[0] if cands else None


def find_image(terms):
    for term in terms:
        try:
            info = pick(term)
        except Exception as e:
            print("    (term failed:", term, "-", e, ")")
            info = None
        if info and (info.get("thumburl") or info.get("url")):
            meta = info.get("extmetadata", {})
            return {
                "thumb": info.get("thumburl") or info.get("url"),
                "page": info.get("descriptionurl", ""),
                "artist": strip_html(meta.get("Artist", {}).get("value", "")) or "Unknown",
                "license": (meta.get("LicenseShortName", {}) or {}).get("value", "see source"),
                "term": term,
            }
    return None


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    credits = ["# Photo credits\n",
               "Destination photos from Wikimedia Commons. Keep attribution with the site.\n"]
    ok = 0
    for tid, terms in QUERIES.items():
        try:
            img = find_image(terms)
            if not img:
                print("  ! no result for", tid)
                continue
            with open(os.path.join(here, tid + ".jpg"), "wb") as f:
                f.write(get(img["thumb"]))
            credits.append("- **%s.jpg** — %s · %s · %s" % (tid, img["artist"], img["license"], img["page"]))
            print("  ✓ %s.jpg  (%s)  [%s]" % (tid, img["license"], img["term"]))
            ok += 1
        except Exception as e:
            print("  ! failed", tid, "-", e)
    with open(os.path.join(here, "CREDITS.md"), "w") as f:
        f.write("\n".join(credits) + "\n")
    print("\nDone: %d/%d photos. Wrote CREDITS.md." % (ok, len(QUERIES)))
    if ok < len(QUERIES):
        print("Tip: tweak the QUERIES terms, or drop your own <id>.jpg files here.")
    else:
        print("Next: multi-file site shows them as-is; for the single file run  python3 ../../build-app.py")


if __name__ == "__main__":
    main()
