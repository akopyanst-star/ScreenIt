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
    p.setBrush(QColor(30, 32, 36))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRect(4, 4, 56, 56), 12, 12)
    # crosshair
    pen = QPen(ACCENT, 4)
    p.setPen(pen)
    p.drawLine(32, 14, 32, 50)
    p.drawLine(14, 32, 50, 32)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRect(QRect(20, 20, 24, 24))
    p.end()
    return QIcon(pm)


def app_icon() -> QIcon:
    ico = resource_path("assets", "icon.ico")
    if ico.exists():
        return QIcon(str(ico))
    return _drawn_icon()
