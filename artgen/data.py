import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "elements.json"

_CACHE = None


def load():
    global _CACHE
    if _CACHE is None:
        with open(DATA_PATH, encoding="utf-8") as f:
            _CACHE = json.load(f)
    return _CACHE


def load_dotenv():
    """Read KEY=VALUE lines from a .env file in the project root into os.environ.
    Existing variables win. Lines starting with # are ignored."""
    import os
    env_path = DATA_PATH.parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip(); v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v
