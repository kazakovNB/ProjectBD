import json
import os
from pathlib import Path
from typing import Any, Dict
import sys

DEFAULT_BASE_URL = os.environ.get("VEO_API_URL", "http://127.0.0.1:5000").rstrip("/")

# Primary config path next to this file (VEOClient/config.py -> VEOClient/config.json)
CONFIG_PATH = Path(__file__).with_name("config.json")

# Additional locations to check (executable directory when frozen, parent 'Client' folder when installed)
EXEC_DIR_CONFIG = (Path(sys.executable).resolve().parent / "config.json") if getattr(sys, 'frozen', False) else (Path(sys.argv[0]).resolve().parent / "config.json")
PARENT_CLIENT_CONFIG = Path(__file__).resolve().parents[1] / "Client" / "config.json" if len(Path(__file__).resolve().parents) > 1 else Path("config.json")


def _read_config_from_path(p: Path) -> Dict[str, Any]:
    try:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    return {}


def _read_config() -> Dict[str, Any]:
    # Try multiple locations in order of preference
    candidates = [CONFIG_PATH, EXEC_DIR_CONFIG, PARENT_CLIENT_CONFIG]
    for p in candidates:
        cfg = _read_config_from_path(p)
        if cfg:
            return cfg
    return {}


def _write_default_config(path: Path | str = CONFIG_PATH) -> None:
    try:
        p = Path(path)
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"base_url": DEFAULT_BASE_URL}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # If we cannot write (e.g., installed under Program Files), we still work via DEFAULT_BASE_URL / env var.
        pass


def get_base_url() -> str:
    # Environment variable takes precedence
    env_url = os.environ.get("VEO_API_URL")
    if env_url:
        return str(env_url).rstrip("/")

    # Try config files
    _write_default_config()
    cfg = _read_config()
    url = (cfg.get("base_url") if isinstance(cfg, dict) else None) or DEFAULT_BASE_URL
    return str(url).rstrip("/")


def build_url(path: str) -> str:
    base = get_base_url()
    if not path.startswith("/"):
        path = "/" + path
    return base + path
