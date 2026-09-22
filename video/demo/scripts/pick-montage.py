#!/usr/bin/env python3
"""Pick three installation/painting renders from out/ and wire them into the demo montage.
Copies image.png -> video/demo/assets/work{1,2,3}.jpg (converted with ffmpeg) and fills the captions.
Usage: python3 video/demo/scripts/pick-montage.py [out_dir]
"""
import json, re, subprocess, sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "out"
demo = root / "video" / "demo"
works = []
for spec_path in sorted(out.glob("*/spec.json")):
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    img = spec_path.parent / "image.png"
    if img.exists() and spec["kind"] != "video":
        works.append((spec, img))
works = works[:3]
assert len(works) == 3, f"need 3 non-video renders, found {len(works)}"

html = (demo / "index.html").read_text(encoding="utf-8")
for i, (spec, img) in enumerate(works, 1):
    dest = demo / "assets" / f"work{i}.jpg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(img), "-vf", "scale=1920:-2", "-q:v", "3", str(dest)], check=True)
    cap = f'<b>{spec["artist"]}</b>, <i>{spec["title"]}</i>, {spec["year"]}. {spec["form"].capitalize()}; {", ".join(spec["materials"])}.'
    html = re.sub(rf'(<div class="cap" id="m{i}-cap">).*?(</div>)', rf'\g<1>{cap}\g<2>', html, flags=re.S)
    print(f"work{i}: {spec['artist']} — {spec['title']}")
(demo / "index.html").write_text(html, encoding="utf-8")
print("captions written")
