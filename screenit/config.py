"""Tiny JSON-backed settings store."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass

from .paths import config_file

DEFAULT_HOTKEY = "Ctrl+Shift+S"


@dataclass
class Config:
    hotkey: str = DEFAULT_HOTKEY
    # Side length (px) of the magnifier box and how many times it zooms in.
    magnifier_size: int = 280
    magnifier_zoom: int = 3

    @classmethod
    def load(cls) -> "Config":
        path = config_file()
        if not path.exists():
            cfg = cls()
            cfg.save()
            return cfg
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return cls()
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})

    def save(self) -> None:
        # Write to a temp file then atomically replace, so a crash mid-write
        # can't leave a half-written (corrupt) config.
        path = config_file()
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        os.replace(tmp, path)
