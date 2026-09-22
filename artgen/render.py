"""Render the artwork with an image or video model.

Providers (chosen with --provider or ARTGEN_PROVIDER):
  dry        write the prompt and an SVG placeholder. No network. Default when no key is set.
  fal        fal.ai queue API.      Needs FAL_KEY.             Models: ARTGEN_FAL_IMAGE_MODEL, ARTGEN_FAL_VIDEO_MODEL
  replicate  Replicate HTTP API.    Needs REPLICATE_API_TOKEN. Models: ARTGEN_REPLICATE_IMAGE_MODEL, ARTGEN_REPLICATE_VIDEO_MODEL
  openai     OpenAI Images API.     Needs OPENAI_API_KEY.      Model:  ARTGEN_OPENAI_IMAGE_MODEL (image only)
"""
import html
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

DEFAULTS = {
    "fal_image": "fal-ai/flux/dev",
    "fal_video": "fal-ai/minimax/hailuo-02/standard/text-to-video",
    "replicate_image": "black-forest-labs/flux-dev",
    "replicate_video": "minimax/video-01",
    "openai_image": "gpt-image-1",
}


class RenderError(RuntimeError):
    pass


def pick_provider(explicit=None):
    if explicit:
        return explicit
    env = os.environ.get("ARTGEN_PROVIDER")
    if env:
        return env
    if os.environ.get("FAL_KEY"):
        return "fal"
    if os.environ.get("REPLICATE_API_TOKEN"):
        return "replicate"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "dry"


def _http(method, url, headers=None, body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            ctype = r.headers.get("Content-Type", "")
            return json.loads(raw) if "json" in ctype else raw
    except urllib.error.HTTPError as e:
        raise RenderError(f"{method} {url} -> HTTP {e.code}: {e.read()[:500].decode(errors='replace')}") from e


def _download(url, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "artgen/0.1"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


# ---------------------------------------------------------------- dry / placeholder

def render_placeholder(spec, prompt, out_dir: Path):
    """Write an SVG that looks like an empty wall with a label. It is also a joke."""
    title = html.escape(spec["title"])
    artist = html.escape(spec["artist"])
    mats = html.escape(", ".join(spec["materials"]))
    dims = html.escape(spec["dimensions"])
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
  <defs>
    <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f4f2ee"/><stop offset="1" stop-color="#e6e2da"/>
    </linearGradient>
    <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#b8b2a6"/><stop offset="1" stop-color="#8f897d"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="720" fill="url(#wall)"/>
  <rect y="720" width="1600" height="280" fill="url(#floor)"/>
  <ellipse cx="800" cy="500" rx="520" ry="240" fill="#fff" opacity="0.35"/>
  <text x="800" y="470" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="22" fill="#9a958c" letter-spacing="6">
    THE WORK IS NOT HERE. THIS IS THE POINT.
  </text>
  <g transform="translate(1180,560)">
    <rect width="340" height="130" fill="#fbfaf7" stroke="#d6d1c7"/>
    <text x="18" y="32" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#222">{artist}</text>
    <text x="18" y="56" font-family="Georgia, serif" font-size="14" font-style="italic" fill="#222">{title[:44]}{'…' if len(title) > 44 else ''}, {spec['year']}</text>
    <text x="18" y="78" font-family="Helvetica, Arial, sans-serif" font-size="11" fill="#555">{mats[:60]}{'…' if len(mats) > 60 else ''}</text>
    <text x="18" y="96" font-family="Helvetica, Arial, sans-serif" font-size="11" fill="#555">{dims[:60]}</text>
    <text x="18" y="116" font-family="Helvetica, Arial, sans-serif" font-size="10" fill="#888">Courtesy of the artist</text>
  </g>
</svg>"""
    path = out_dir / "placeholder.svg"
    path.write_text(svg, encoding="utf-8")
    return path


# ---------------------------------------------------------------- fal.ai

def _fal_run(model, payload):
    key = os.environ.get("FAL_KEY")
    if not key:
        raise RenderError("FAL_KEY is not set")
    headers = {"Authorization": f"Key {key}"}
    sub = _http("POST", f"https://queue.fal.run/{model}", headers, payload)
    status_url = sub["status_url"]
    response_url = sub["response_url"]
    deadline = time.time() + 900
    while time.time() < deadline:
        st = _http("GET", status_url, headers)
        if st.get("status") == "COMPLETED":
            return _http("GET", response_url, headers)
        if st.get("status") in ("FAILED", "CANCELLED"):
            raise RenderError(f"fal job {st.get('status')}: {st}")
        time.sleep(3)
    raise RenderError("fal job timed out")


def render_fal(spec, prompt, out_dir: Path, video=False):
    if video:
        model = os.environ.get("ARTGEN_FAL_VIDEO_MODEL", DEFAULTS["fal_video"])
        res = _fal_run(model, {"prompt": prompt})
        url = res["video"]["url"]
        return _download(url, out_dir / "video.mp4")
    model = os.environ.get("ARTGEN_FAL_IMAGE_MODEL", DEFAULTS["fal_image"])
    res = _fal_run(model, {"prompt": prompt, "image_size": "landscape_16_9", "num_images": 1})
    url = res["images"][0]["url"]
    ext = ".png" if url.split("?")[0].endswith(".png") else ".jpg"
    return _download(url, out_dir / f"image{ext}")


# ---------------------------------------------------------------- Replicate

def _replicate_run(model, inp):
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        raise RenderError("REPLICATE_API_TOKEN is not set")
    headers = {"Authorization": f"Bearer {token}", "Prefer": "wait=60"}
    pred = _http("POST", f"https://api.replicate.com/v1/models/{model}/predictions", headers, {"input": inp})
    deadline = time.time() + 900
    while pred.get("status") not in ("succeeded", "failed", "canceled") and time.time() < deadline:
        time.sleep(3)
        pred = _http("GET", pred["urls"]["get"], {"Authorization": f"Bearer {token}"})
    if pred.get("status") != "succeeded":
        raise RenderError(f"replicate prediction {pred.get('status')}: {pred.get('error')}")
    return pred["output"]


def render_replicate(spec, prompt, out_dir: Path, video=False):
    if video:
        model = os.environ.get("ARTGEN_REPLICATE_VIDEO_MODEL", DEFAULTS["replicate_video"])
        out = _replicate_run(model, {"prompt": prompt})
        url = out if isinstance(out, str) else out[0]
        return _download(url, out_dir / "video.mp4")
    model = os.environ.get("ARTGEN_REPLICATE_IMAGE_MODEL", DEFAULTS["replicate_image"])
    out = _replicate_run(model, {"prompt": prompt, "aspect_ratio": "16:9", "output_format": "jpg"})
    url = out if isinstance(out, str) else out[0]
    return _download(url, out_dir / "image.jpg")


# ---------------------------------------------------------------- OpenAI

def render_openai(spec, prompt, out_dir: Path, video=False):
    import base64
    if video:
        raise RenderError("openai provider supports images only in this tool")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RenderError("OPENAI_API_KEY is not set")
    model = os.environ.get("ARTGEN_OPENAI_IMAGE_MODEL", DEFAULTS["openai_image"])
    res = _http("POST", "https://api.openai.com/v1/images/generations",
                {"Authorization": f"Bearer {key}"},
                {"model": model, "prompt": prompt, "size": "1536x1024", "n": 1})
    item = res["data"][0]
    dest = out_dir / "image.png"
    if item.get("b64_json"):
        dest.write_bytes(base64.b64decode(item["b64_json"]))
        return dest
    return _download(item["url"], dest)


# ---------------------------------------------------------------- dispatcher

def render(spec, prompt, out_dir: Path, provider=None, video=False):
    """Return the path of the rendered file. Always writes prompt.txt first."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / ("video_prompt.txt" if video else "image_prompt.txt")).write_text(prompt + "\n", encoding="utf-8")
    provider = pick_provider(provider)
    if provider == "dry":
        return render_placeholder(spec, prompt, out_dir)
    if provider == "fal":
        return render_fal(spec, prompt, out_dir, video)
    if provider == "replicate":
        return render_replicate(spec, prompt, out_dir, video)
    if provider == "openai":
        return render_openai(spec, prompt, out_dir, video)
    raise RenderError(f"unknown provider: {provider}")
