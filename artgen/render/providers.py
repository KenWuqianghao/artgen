"""Image providers. Each one takes a prompt and a destination path and writes one image file.

  dry        no network; writes an SVG placeholder of an empty gallery wall
  openai     OpenAI Images API, needs OPENAI_API_KEY. Model: ARTGEN_OPENAI_MODEL (default gpt-image-2.5-flare)
  fal        fal.ai queue API, needs FAL_KEY. Model: ARTGEN_FAL_MODEL
  replicate  Replicate HTTP API, needs REPLICATE_API_TOKEN. Model: ARTGEN_REPLICATE_MODEL
"""
from __future__ import annotations

import base64
import html
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


class RenderError(RuntimeError):
    def __init__(self, message: str, status: int | None = None, retry_after: float | None = None):
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after


SAFE_SUFFIX = (" All people depicted, painted or sculpted are fully clothed adults or children in everyday clothes; "
               "nothing violent or graphic is shown.")


def _http(method: str, url: str, headers: dict | None = None, body: dict | None = None, timeout: int = 300):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return json.loads(raw) if "json" in r.headers.get("Content-Type", "") else raw
    except urllib.error.HTTPError as e:
        retry = e.headers.get("retry-after")
        raise RenderError(f"{method} {url} -> HTTP {e.code}: {e.read()[:400].decode(errors='replace')}",
                          status=e.code, retry_after=float(retry) if retry else None) from e
    except urllib.error.URLError as e:
        raise RenderError(f"{method} {url} -> {e.reason}") from e


def _download(url: str, dest: Path) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": "artgen/2"})
    with urllib.request.urlopen(req, timeout=300) as r:
        dest.write_bytes(r.read())
    return dest


def available() -> list[str]:
    names = ["dry"]
    if os.environ.get("OPENAI_API_KEY"):
        names.append("openai")
    if os.environ.get("FAL_KEY"):
        names.append("fal")
    if os.environ.get("REPLICATE_API_TOKEN"):
        names.append("replicate")
    return names


def default_provider() -> str:
    env = os.environ.get("ARTGEN_PROVIDER")
    if env:
        return env
    for name in ("openai", "fal", "replicate"):
        if name in available():
            return name
    return "dry"


# ------------------------------------------------------------------ dry

def dry(prompt: str, dest: Path, caption: str = "") -> Path:
    cap = html.escape(caption[:90])
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024">
  <rect width="1536" height="700" fill="#e9e8e4"/>
  <rect y="700" width="1536" height="324" fill="#b9b6ae"/>
  <rect y="698" width="1536" height="4" fill="#d8d6d0"/>
  <g transform="translate(1150,520)">
    <rect width="250" height="96" fill="#f7f7f5" stroke="#cfcdc7"/>
    <rect x="16" y="18" width="150" height="9" fill="#55534e"/>
    <rect x="16" y="36" width="200" height="7" fill="#8b8982"/>
    <rect x="16" y="50" width="170" height="7" fill="#8b8982"/>
    <rect x="16" y="64" width="120" height="7" fill="#8b8982"/>
  </g>
  <text x="768" y="380" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="20" letter-spacing="5" fill="#9c9a93">THE WORK IS NOT HERE. THIS IS THE POINT.</text>
  <text x="768" y="980" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="14" fill="#6f6d67">{cap}</text>
</svg>"""
    dest = dest.with_suffix(".svg")
    dest.write_text(svg, encoding="utf-8")
    return dest


# ------------------------------------------------------------------ openai

def openai(prompt: str, dest: Path, caption: str = "") -> Path:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RenderError("OPENAI_API_KEY is not set")
    model = os.environ.get("ARTGEN_OPENAI_MODEL", "gpt-image-2.5-flare")
    body = {
        "model": model,
        "prompt": prompt,
        "size": os.environ.get("ARTGEN_OPENAI_SIZE", "1536x1024"),
        "quality": os.environ.get("ARTGEN_OPENAI_QUALITY", "medium"),
        "n": 1,
        "output_format": "jpeg",
        "output_compression": 86,
    }
    res = None
    for attempt in range(7):
        try:
            res = _http("POST", "https://api.openai.com/v1/images/generations", {"Authorization": f"Bearer {key}"}, body)
            break
        except RenderError as e:
            if e.status == 429 and attempt < 6:
                time.sleep(e.retry_after or min(90, 8 * 2 ** attempt))
                continue
            if e.status == 400 and "moderation" in str(e) and not body["prompt"].endswith(SAFE_SUFFIX):
                body["prompt"] += SAFE_SUFFIX
                continue
            raise
    item = res["data"][0]
    dest = dest.with_suffix(".jpg")
    if item.get("b64_json"):
        dest.write_bytes(base64.b64decode(item["b64_json"]))
        return dest
    return _download(item["url"], dest)


# ------------------------------------------------------------------ fal

def fal(prompt: str, dest: Path, caption: str = "") -> Path:
    key = os.environ.get("FAL_KEY")
    if not key:
        raise RenderError("FAL_KEY is not set")
    model = os.environ.get("ARTGEN_FAL_MODEL", "fal-ai/flux/dev")
    headers = {"Authorization": f"Key {key}"}
    sub = _http("POST", f"https://queue.fal.run/{model}", headers,
                {"prompt": prompt, "image_size": "landscape_4_3", "num_images": 1})
    deadline = time.time() + 600
    while time.time() < deadline:
        st = _http("GET", sub["status_url"], headers)
        if st.get("status") == "COMPLETED":
            res = _http("GET", sub["response_url"], headers)
            url = res["images"][0]["url"]
            return _download(url, dest.with_suffix(".png" if ".png" in url else ".jpg"))
        if st.get("status") in ("FAILED", "CANCELLED"):
            raise RenderError(f"fal job {st.get('status')}")
        time.sleep(3)
    raise RenderError("fal job timed out")


# ------------------------------------------------------------------ replicate

def replicate(prompt: str, dest: Path, caption: str = "") -> Path:
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        raise RenderError("REPLICATE_API_TOKEN is not set")
    model = os.environ.get("ARTGEN_REPLICATE_MODEL", "black-forest-labs/flux-dev")
    auth = {"Authorization": f"Bearer {token}"}
    pred = _http("POST", f"https://api.replicate.com/v1/models/{model}/predictions", {**auth, "Prefer": "wait=60"},
                 {"input": {"prompt": prompt, "aspect_ratio": "3:2", "output_format": "jpg"}})
    deadline = time.time() + 600
    while pred.get("status") not in ("succeeded", "failed", "canceled") and time.time() < deadline:
        time.sleep(3)
        pred = _http("GET", pred["urls"]["get"], auth)
    if pred.get("status") != "succeeded":
        raise RenderError(f"replicate prediction {pred.get('status')}: {pred.get('error')}")
    out = pred["output"]
    return _download(out if isinstance(out, str) else out[0], dest.with_suffix(".jpg"))


PROVIDERS = {"dry": dry, "openai": openai, "fal": fal, "replicate": replicate}
