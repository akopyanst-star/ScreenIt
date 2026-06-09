"""Custom capture cursor: a pointing hand with a target ring at the fingertip.

Replaces the plain reticle; the ring marks the exact point being selected and
its centre is the cursor hotspot. Sized like a normal mouse cursor.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QCursor, QPainter, QPainterPath, QPen, QPixmap

_OUTLINE = QColor(35, 35, 40)
_FILL = QColor(245, 245, 248)
# Ring centre in the 48x48 design space — used as the hotspot.
_HOT = (18.7, 8.0)


def _hand_pixmap(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    u = size / 48.0
    p.setPen(QPen(_OUTLINE, 2 * u, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.setBrush(QBrush(_FILL))

    hand = QPainterPath()
    hand.addRoundedRect(QRectF(13 * u, 23 * u, 24 * u, 20 * u), 8 * u, 8 * u)   # fist
    hand.addRoundedRect(QRectF(15 * u, 7 * u, 7.5 * u, 22 * u), 3.8 * u, 3.8 * u)  # index
    for fx in (25.5, 31, 36):                                                   # knuckles
        hand.addEllipse(QPointF(fx * u, 24 * u), 3.3 * u, 3.8 * u)
    p.drawPath(hand.simplified())

    ring = QPainterPath()
    ring.addEllipse(QPointF(_HOT[0] * u, _HOT[1] * u), 5 * u, 5 * u)
    ring.addEllipse(QPointF(_HOT[0] * u, _HOT[1] * u), 2.2 * u, 2.2 * u)
    p.drawPath(ring)
    p.end()
    return pm


def capture_cursor(size: int = 40) -> QCursor:
    u = size / 48.0
    return QCursor(_hand_pixmap(size), round(_HOT[0] * u), round(_HOT[1] * u))
