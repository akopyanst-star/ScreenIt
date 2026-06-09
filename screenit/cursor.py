"""Capture cursor — loads the user's hand/loupe PNG from assets/cursor.png.

The PNG is scaled down to a normal cursor size; the hotspot is placed at the
centre of the "+" inside the loupe (measured at ~25%/20% of the image). Falls
back to a plain crosshair cursor if the asset is missing.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QPixmap

from .paths import resource_path

# Centre of the "+" as a fraction of the source image (assets/cursor.png).
_HOT_FX, _HOT_FY = 0.252, 0.204


def capture_cursor(height: int = 46) -> QCursor:
    png = resource_path("assets", "cursor.png")
    if png.exists():
        pm = QPixmap(str(png))
        if not pm.isNull():
            pm = pm.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
            return QCursor(pm, round(_HOT_FX * pm.width()), round(_HOT_FY * pm.height()))
    return QCursor(Qt.CursorShape.CrossCursor)
