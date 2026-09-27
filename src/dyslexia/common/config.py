from pathlib import Path
from typing import Any
import yaml
from .paths import CONFIGS


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML config and merge it over configs/config.yaml."""
    base = yaml.safe_load((CONFIGS / "config.yaml").read_text(encoding="utf-8"))
    override = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return _deep_merge(base, override)


def _deep_merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out
