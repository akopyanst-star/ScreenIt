"""The tray icon: load the bundled .ico, or draw a fallback at runtime."""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap

from .paths import resource_path

ACCENT = QColor(0, 153, 255)


def _drawn_icon() -> QIcon:
    pm = QPixmap(64, 64)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Full-bleed accent background.
    p.setBrush(ACCENT)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRect(1, 1, 62, 62), 12, 12)
    # Bold white crosshair + selection square.
    p.setPen(QPen(QColor(255, 255, 255), 6))
    p.drawLine(32, 8, 32, 56)
    p.drawLine(8, 32, 56, 32)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRect(QRect(16, 16, 32, 32))
    p.end()
    return QIcon(pm)


def app_icon() -> QIcon:
    ico = resource_path("assets", "icon.ico")
    if ico.exists():
        return QIcon(str(ico))
    return _drawn_icon()
