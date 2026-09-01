# Destination photos

The site shows a real photo per destination, layered over a colour gradient.
**If a photo is missing, the gradient shows instead** — so the site always looks
complete, and photos "light up" the moment you add them.

## Filenames

Drop landscape JPEGs here (~1200–1600px wide) with these exact names:

```
pattaya.jpg   huahin.jpg   samet.jpg
ayutthaya.jpg amphawa.jpg  bangkok.jpg
kanchanaburi.jpg  khaoyai.jpg  chiangmai.jpg
```

They're used as CSS `background: cover`, so exact dimensions don't matter.

## Get real photos in one command

```bash
cd gogo-travel/assets/img
python3 fetch-photos.py
```

Downloads a freely-licensed photo per destination from **Wikimedia Commons**
(already resized) and writes `CREDITS.md`. Standard-library Python only — no
installs. Re-run any time; edit the `QUERIES` in the script to change a pick.

## Licensing

Wikimedia Commons photos are mostly CC BY / CC BY-SA / public domain — most
require **attribution**, which `fetch-photos.py` records in `CREDITS.md`. Keep
that file with the site. For a commercial launch, prefer photos you have a clear
right to use (your own, or a stock licence from Unsplash / Pexels / Getty).

## Why they aren't already here

This site was built in a sandbox whose network policy blocks image hosts, so the
photos couldn't be downloaded at build time. Everything is wired to use them —
just run the fetcher above (or add your own).
