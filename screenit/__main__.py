"""Entry point. Run with ``python -m screenit`` (or the built ScreenIt.exe)."""

from __future__ import annotations

import ctypes
import os
import sys

ERROR_ALREADY_EXISTS = 183


def _ensure_single_instance() -> None:
    """Exit silently if another ScreenIt is already running."""
    ctypes.windll.kernel32.CreateMutexW(None, False, "ScreenIt_SingleInstance_Mutex")
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        sys.exit(0)


def _setup_dpi() -> None:
    """Make the process DPI-aware and keep Qt at 1:1 physical pixels.

    With per-monitor-v2 awareness mss reads true physical pixels, and disabling
    Qt's auto scaling means Qt coordinates equal those pixels — so the selection
    rectangle maps directly onto the captured image. (Mixed-DPI multi-monitor
    setups are a known v1 limitation.)
    """
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "0")
    os.environ.setdefault("QT_SCALE_FACTOR", "1")
    user32 = ctypes.windll.user32
    try:
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:  # noqa: BLE001
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:  # noqa: BLE001
            user32.SetProcessDPIAware()


def main() -> int:
    _ensure_single_instance()
    _setup_dpi()
    from .app import ScreenItApp

    return ScreenItApp().run()


if __name__ == "__main__":
    raise SystemExit(main())
