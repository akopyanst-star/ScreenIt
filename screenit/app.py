"""Tray application: global hotkey -> selection overlay -> clipboard."""

from __future__ import annotations

import ctypes
import logging
from ctypes import wintypes

from PySide6.QtCore import QAbstractNativeEventFilter, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
)

from . import __version__, autostart, clipboard, hotkey
from .capture import grab_virtual_screen
from .config import Config
from .hotkey_dialog import HotkeyCaptureDialog
from .icon import app_icon
from .overlay import SelectionOverlay

HOTKEY_ID = 1


class _HotkeyFilter(QAbstractNativeEventFilter):
    """Catches WM_HOTKEY out of Qt's Windows message pump."""

    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def nativeEventFilter(self, event_type, message):
        if event_type == b"windows_generic_MSG":
            msg = ctypes.cast(int(message), ctypes.POINTER(wintypes.MSG)).contents
            if msg.message == hotkey.WM_HOTKEY and msg.wParam == HOTKEY_ID:
                self._callback()
        return False, 0


class ScreenItApp:
    def __init__(self) -> None:
        self.config = Config.load()
        self.qt = QApplication.instance() or QApplication([])
        self.qt.setQuitOnLastWindowClosed(False)
        self.qt.setApplicationName("ScreenIt")

        self._overlay: SelectionOverlay | None = None
        self._icon = app_icon()

        self._build_tray()

        self._filter = _HotkeyFilter(self.capture)
        self.qt.installNativeEventFilter(self._filter)
        self._register_hotkey(initial=True)

    # ------------------------------------------------------------------ tray
    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(self._icon)
        self.tray.setToolTip(f"ScreenIt {__version__}")

        menu = QMenu()
        self._capture_action = menu.addAction(f"Снять область  ({self.config.hotkey})")
        self._capture_action.triggered.connect(self.capture)
        menu.addSeparator()

        self._startup_action = menu.addAction("Запускать при старте Windows")
        self._startup_action.setCheckable(True)
        self._startup_action.setChecked(autostart.is_enabled())
        self._startup_action.toggled.connect(autostart.set_enabled)

        menu.addAction("Сменить горячую клавишу…").triggered.connect(self._change_hotkey)
        menu.addSeparator()
        menu.addAction("Выход").triggered.connect(self.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.capture()

    # ------------------------------------------------------------------ hotkey
    def _register_hotkey(self, initial: bool = False) -> bool:
        try:
            hk = hotkey.parse_hotkey(self.config.hotkey)
        except hotkey.HotkeyError as exc:
            self.tray.showMessage("ScreenIt", f"Bad hotkey: {exc}", self._icon, 4000)
            return False

        hotkey.unregister(HOTKEY_ID)
        if hotkey.register(HOTKEY_ID, hk):
            return True

        msg = (
            f"Could not register {self.config.hotkey} "
            "(another app may be using it). Use the tray menu to capture."
        )
        self.tray.showMessage("ScreenIt", msg, self._icon, 5000)
        return False

    def _change_hotkey(self) -> None:
        dialog = HotkeyCaptureDialog(self.config.hotkey)
        if dialog.exec() != QDialog.DialogCode.Accepted or not dialog.combo:
            return
        old = self.config.hotkey
        self.config.hotkey = dialog.combo
        if self._register_hotkey():
            self.config.save()
            self._capture_action.setText(f"Снять область  ({self.config.hotkey})")
        else:
            self.config.hotkey = old
            self._register_hotkey()

    # ------------------------------------------------------------------ capture
    def capture(self) -> None:
        if self._overlay is not None:
            return
        try:
            logging.info("capture: grabbing screen")
            shot = grab_virtual_screen()
            self._overlay = SelectionOverlay(
                shot, self.config.magnifier_size, self.config.magnifier_zoom
            )
            self._overlay.regionSelected.connect(self._on_region)
            self._overlay.cancelled.connect(self._clear_overlay)
            self._overlay.destroyed.connect(self._clear_overlay)
            self._overlay.show_overlay()
            logging.info("capture: overlay shown %sx%s", shot.width, shot.height)
        except Exception:
            logging.exception("capture failed")
            self._overlay = None
            self.tray.showMessage(
                "ScreenIt", "Ошибка захвата экрана — см. screenit.log", self._icon, 4000
            )

    def _on_region(self, rect) -> None:
        assert self._overlay is not None
        image = self._overlay._shot.crop(
            rect.x(), rect.y(), rect.width(), rect.height()
        )
        try:
            clipboard.copy_image(image)
            self.tray.showMessage(
                "ScreenIt", f"Copied {rect.width()} x {rect.height()} px to clipboard",
                self._icon, 1500,
            )
        except Exception as exc:  # noqa: BLE001 - surface any clipboard failure
            QMessageBox.warning(None, "ScreenIt", f"Copy failed: {exc}")

    def _clear_overlay(self, *_args) -> None:
        self._overlay = None

    # ------------------------------------------------------------------ lifecycle
    def quit(self) -> None:
        hotkey.unregister(HOTKEY_ID)
        self.tray.hide()
        self.qt.quit()

    def _greet(self) -> None:
        self.tray.showMessage(
            "ScreenIt запущен",
            f"{self.config.hotkey} — снимок области в буфер обмена.\n"
            "Иконка в трее (нажми стрелку ^, если её не видно).",
            self._icon,
            5000,
        )

    def run(self) -> int:
        # Fire once the event loop is up, so the balloon actually shows.
        QTimer.singleShot(700, self._greet)
        return self.qt.exec()
