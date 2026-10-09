#!/usr/bin/env python3
"""Build index.html from template.html.

Discovers runway clips in media/ (sorted by filename, one model each),
reads product copy from brand/products.json and inlines brand/logo-horizontal.svg.
Clips the browser can't play inline (e.g. HEVC) are transcoded to H.264 MP4.
"""
import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / "media"
VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v"}
NAV = ["New arrivals", "women", "men", "denim", "shows"]
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


def main():
    videos = []
    if MEDIA.is_dir():
        for p in sorted(MEDIA.iterdir(), key=lambda p: p.name):
            if p.suffix.lower() in VIDEO_EXT and not p.name.endswith(".web.mp4"):
                videos.append(playable(p))

    brand = json.loads((ROOT / "brand" / "products.json").read_text())
    data = {
        "models": [{"src": v.relative_to(ROOT).as_posix()} for v in videos],
        "products": brand["products"],
        "currency": brand["currency"],
        "sizes": brand["sizes"],
        "defaultSize": brand["defaultSize"],
    }

    logo = (ROOT / "brand" / "logo-horizontal.svg").read_text().strip()
    logo = re.sub(r'\s+xmlns="[^"]+"', "", logo, count=1)
    nav = "\n      ".join(f'<a href="#">{html.escape(n)}</a>' for n in NAV)

    page = (ROOT / "template.html").read_text()
    page = (page.replace("__LOGO__", logo)
                .replace("__NAV__", nav)
                .replace("__FALLBACK__", FALLBACK)
                .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    (ROOT / "index.html").write_text(page)
    print(f"index.html: {len(videos)} clip(s), {len(brand['products'])} product entries")


if __name__ == "__main__":
    main()
