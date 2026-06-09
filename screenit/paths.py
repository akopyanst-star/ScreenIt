"""Filesystem helpers that work both in dev and inside a PyInstaller bundle."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Path to a bundled resource (e.g. the tray icon).

    Works when running from source and when frozen by PyInstaller (where
    bundled data lives under ``sys._MEIPASS``).
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base).joinpath(*parts)
    return Path(__file__).resolve().parent.parent.joinpath(*parts)


def config_dir() -> Path:
    """Per-user config directory: ``%APPDATA%\\ScreenIt``."""
    appdata = os.environ.get("APPDATA") or str(Path.home())
    path = Path(appdata) / "ScreenIt"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_file() -> Path:
    return config_dir() / "config.json"
