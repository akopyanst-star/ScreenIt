"""Register/unregister ScreenIt to run at Windows logon (HKCU Run key)."""

from __future__ import annotations

import sys
import winreg
from pathlib import Path

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_VALUE = "ScreenIt"


def _launch_command() -> str:
    """Command Windows should run at startup.

    When frozen (PyInstaller) that's just the .exe; from source we relaunch
    with pythonw so no console window appears.
    """
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    exe = Path(sys.executable)
    pythonw = exe.with_name("pythonw.exe")  # replace only the file name
    launcher = pythonw if pythonw.exists() else exe
    return f'"{launcher}" -m screenit'


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            winreg.QueryValueEx(key, _VALUE)
            return True
    except OSError:
        return False


def set_enabled(enabled: bool) -> None:
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        if enabled:
            winreg.SetValueEx(key, _VALUE, 0, winreg.REG_SZ, _launch_command())
        else:
            try:
                winreg.DeleteValue(key, _VALUE)
            except OSError:
                pass
