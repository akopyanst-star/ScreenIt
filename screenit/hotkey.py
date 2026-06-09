"""Parse human hotkey strings and register a Windows global hotkey.

We use ``RegisterHotKey`` bound to the current thread (hwnd = NULL); the
``WM_HOTKEY`` message is then picked up by Qt's event loop through a native
event filter (see :mod:`screenit.app`).
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass

# RegisterHotKey modifier flags.
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY = 0x0312

_MODIFIERS = {
    "ctrl": MOD_CONTROL,
    "control": MOD_CONTROL,
    "alt": MOD_ALT,
    "shift": MOD_SHIFT,
    "win": MOD_WIN,
    "super": MOD_WIN,
    "cmd": MOD_WIN,
}

# Named virtual-key codes for keys that aren't a single printable character.
_NAMED_KEYS = {
    "printscreen": 0x2C,
    "prtscn": 0x2C,
    "prtsc": 0x2C,
    "snapshot": 0x2C,
    "insert": 0x2D,
    "ins": 0x2D,
    "delete": 0x2E,
    "del": 0x2E,
    "home": 0x24,
    "end": 0x23,
    "space": 0x20,
    "enter": 0x0D,
    "return": 0x0D,
    "tab": 0x09,
    "escape": 0x1B,
    "esc": 0x1B,
    "pause": 0x13,
    **{f"f{i}": 0x70 + (i - 1) for i in range(1, 25)},  # F1..F24
}


@dataclass(frozen=True)
class Hotkey:
    modifiers: int
    vk: int


class HotkeyError(ValueError):
    pass


def parse_hotkey(spec: str) -> Hotkey:
    """Parse e.g. ``"Ctrl+Shift+S"`` into modifiers + virtual-key code."""
    parts = [p.strip().lower() for p in spec.split("+") if p.strip()]
    if not parts:
        raise HotkeyError("Empty hotkey")

    modifiers = 0
    key_vk: int | None = None
    for part in parts:
        if part in _MODIFIERS:
            modifiers |= _MODIFIERS[part]
        elif part in _NAMED_KEYS:
            key_vk = _NAMED_KEYS[part]
        elif len(part) == 1:
            key_vk = ord(part.upper())
        else:
            raise HotkeyError(f"Unknown key: {part!r}")

    if key_vk is None:
        raise HotkeyError(f"No main key in hotkey: {spec!r}")

    return Hotkey(modifiers | MOD_NOREPEAT, key_vk)


def register(hotkey_id: int, hotkey: Hotkey) -> bool:
    """Register the hotkey on the current thread. Returns success."""
    return bool(
        ctypes.windll.user32.RegisterHotKey(
            None, hotkey_id, hotkey.modifiers, hotkey.vk
        )
    )


def unregister(hotkey_id: int) -> None:
    ctypes.windll.user32.UnregisterHotKey(None, hotkey_id)
