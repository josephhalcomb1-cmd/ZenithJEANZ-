#!/usr/bin/env python3
"""Build index.html from template.html.

Discovers runway clips in media/ (sorted by filename, one model each),
reads looks from brand/products.json, store settings from brand/store.json, and
inlines brand/logo-horizontal.svg. Clips the browser can't play inline (e.g. HEVC)
are transcoded to H.264 MP4. Also writes brand/shopify-products.csv for importing
every piece into Shopify (Products > Import).
"""
import csv
import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / "media"
VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v"}
NAV = [("New arrivals", "new"), ("women", "women"), ("men", "men"),
       ("denim", "denim"), ("shows", "shows")]
CSV_HEADER = ["Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
              "Option1 Name", "Option1 Value", "Variant SKU", "Variant Inventory Tracker",
              "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price",
              "Variant Requires Shipping", "Variant Taxable", "Status"]
FALLBACK = "#DCE3EA"


def codec(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True)
    return out.stdout.strip()


def playable(path):
    """Return a browser-playable version of path, transcoding if needed."""
    if path.suffix.lower() == ".webm" or (path.suffix.lower() in {".mp4", ".m4v"} and codec(path) == "h264"):
        return path
    out = path.with_name(path.stem + ".web.mp4")
    if not out.exists():
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(path),
             "-vf", "scale='if(gt(iw,ih),900,-2)':'if(gt(iw,ih),-2,900)'",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22",
             "-movflags", "+faststart", "-an", str(out)], check=True)
    return out


def fallbacks(video):
    """Animated WebP (plays even where Safari blocks video autoplay) and a still poster."""
    anim = MEDIA / "anim" / (video.stem.replace(".web", "") + ".webp")
    poster = MEDIA / "poster" / (video.stem.replace(".web", "") + ".jpg")
    for out, args in ((anim, ["-vf", "fps=24", "-c:v", "libwebp_anim", "-lossless", "0",
                              "-quality", "75", "-loop", "0", "-an"]),
                      (poster, ["-frames:v", "1", "-q:v", "3"])):
        if not out.exists() or out.stat().st_mtime < video.stat().st_mtime:
            out.parent.mkdir(exist_ok=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), *args, str(out)], check=True)
    return anim, poster


def main():
    videos = []
    if MEDIA.is_dir():
        for p in sorted(MEDIA.iterdir(), key=lambda p: p.name):
            if p.suffix.lower() in VIDEO_EXT and not p.name.endswith(".web.mp4"):
                videos.append(playable(p))

    brand = json.loads((ROOT / "brand" / "products.json").read_text())
    store = json.loads((ROOT / "brand" / "store.json").read_text())
    store.pop("_help", None)
    data = {
        "models": [dict(zip(("src", "anim", "poster"),
                            (f.relative_to(ROOT).as_posix() for f in (v, *fallbacks(v)))))
                   for v in videos],
        "looks": brand["looks"],
        "currency": brand["currency"],
        "sizes": brand["sizes"],
        "defaultSize": brand["defaultSize"],
        "store": store,
    }

    logo = (ROOT / "brand" / "logo-horizontal.svg").read_text().strip()
    logo = re.sub(r'\s+xmlns="[^"]+"', "", logo, count=1)
    nav = "\n      ".join(f'<a href="#" data-filter="{key}">{html.escape(label)}</a>'
                           for label, key in NAV)

    page = (ROOT / "template.html").read_text()
    page = (page.replace("__LOGO__", logo)
                .replace("__NAV__", nav)
                .replace("__FALLBACK__", FALLBACK)
                .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    (ROOT / "index.html").write_text(page)
    pieces = write_shopify_csv(brand)
    mode = "Shopify connected" if store.get("shopDomain") and store.get("storefrontToken") else "demo mode"
    print(f"index.html: {len(videos)} clip(s), {len(brand['looks'])} looks, {mode}")
    print(f"brand/shopify-products.csv: {pieces} pieces x {len(brand['sizes'])} sizes")


def write_shopify_csv(brand):
    """One Shopify product per piece, one variant per size."""
    out = ROOT / "brand" / "shopify-products.csv"
    count = 0
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_HEADER)
        for n, look in enumerate(brand["looks"], 1):
            for piece in look["pieces"]:
                count += 1
                for i, size in enumerate(brand["sizes"]):
                    first = i == 0
                    body = (f"<p>{html.escape(look['description'])}</p>"
                            f"<p>Part of the look: {html.escape(look['name'])}.</p>")
                    tags = ", ".join(look.get("tags", []) + [f"look-{n:02d}", piece["type"].lower()])
                    w.writerow([
                        piece["handle"],
                        piece["name"] if first else "",
                        body if first else "",
                        "Zenith Jeanz" if first else "",
                        piece["type"] if first else "",
                        tags if first else "",
                        "TRUE" if first else "",
                        "Size" if first else "",
                        size,
                        f"{piece['handle']}-{size}".upper(),
                        "",           # no stock tracking until you set inventory in Shopify
                        "deny",
                        "manual",
                        f"{piece['price']:.2f}",
                        "TRUE",
                        "TRUE",
                        "active" if first else "",
                    ])
    return count


if __name__ == "__main__":
    main()
