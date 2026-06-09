# PyInstaller spec — builds a single windowed ScreenIt.exe.
# Build with:  pyinstaller ScreenIt.spec
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ["app_entry.py"],
    pathex=[],
    binaries=[],
    datas=[("assets/icon.ico", "assets"), ("assets/cursor.png", "assets")],
    hiddenimports=collect_submodules("win32"),
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ScreenIt",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/icon.ico",
)
