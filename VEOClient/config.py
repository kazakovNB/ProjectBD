import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_BASE_URL = os.environ.get("VEO_API_URL", "http://127.0.0.1:5000").rstrip("/")

CONFIG_PATH = Path(__file__).with_name("config.json")

def _read_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}

def _write_default_config() -> None:
    try:
        if not CONFIG_PATH.exists():
            CONFIG_PATH.write_text(json.dumps({"base_url": DEFAULT_BASE_URL}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # If we cannot write (e.g., installed under Program Files), we still work via DEFAULT_BASE_URL / env var.
        pass

def get_base_url() -> str:
    _write_default_config()
    cfg = _read_config()
    url = (cfg.get("base_url") if isinstance(cfg, dict) else None) or DEFAULT_BASE_URL
    return str(url).rstrip("/")

def build_url(path: str) -> str:
    base = get_base_url()
    if not path.startswith("/"):
        path = "/" + path
    return base + path
