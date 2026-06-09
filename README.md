# ScreenIt

A tiny Windows tray app that does one thing well: **press a hotkey, drag a
rectangle, and the selected region lands straight on your clipboard.** No files,
no editor, no save dialogs — just region capture, on its own.

While selecting you get a **pixel-accurate magnifier loupe** next to the cursor
showing the zoomed pixels, a crosshair, live coordinates, the selection size and
the pixel colour under the cursor — so you can hit the exact edge.

- **Hotkey:** `Ctrl+Shift+S` by default (changeable from the tray menu)
- **Esc / right-click:** cancel
- Runs quietly in the system tray, optionally at startup
- Works across multiple monitors

## Install (no Python needed)

Run this in PowerShell:

```powershell
irm https://github.com/akopyanst-star/ScreenIt/raw/master/install.ps1 | iex
```

It downloads the latest `ScreenIt.exe`, adds a Start Menu shortcut, enables
run-at-startup and launches it.

Prefer to do it by hand? Download `ScreenIt.exe` from the
[latest release](https://github.com/akopyanst-star/ScreenIt/releases/latest) and run it.

## Run from source (for development)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m screenit
```

## Build the .exe yourself

```powershell
pip install pyinstaller
python tools\generate_icon.py   # only needed if assets/icon.ico is missing
pyinstaller ScreenIt.spec        # output: dist\ScreenIt.exe
```

Pushing a `vX.Y.Z` git tag triggers the GitHub Actions workflow, which builds
the exe and attaches it to a release automatically.

## How it works

| Step | Component |
|------|-----------|
| Global hotkey (`WM_HOTKEY` via Qt's native event filter) | `screenit/hotkey.py`, `app.py` |
| Freeze + capture the whole virtual desktop | `screenit/capture.py` (`mss`) |
| Dimmed overlay, selection, magnifier loupe | `screenit/overlay.py` (`PySide6`) |
| Copy the crop to the clipboard as a DIB | `screenit/clipboard.py` (`pywin32`) |
| Tray icon, settings, autostart | `screenit/app.py`, `autostart.py`, `config.py` |

Settings live in `%APPDATA%\ScreenIt\config.json`.

## Known limitations

- Windows only.
- Mixed-DPI multi-monitor setups (different scaling per screen) may misalign the
  selection; uniform scaling and single monitors are exact.

## Author

Created by **Giroes**.

## License

MIT — see [LICENSE](LICENSE).
