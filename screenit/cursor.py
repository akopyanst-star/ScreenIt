"""Custom capture cursor: a pinching hand with a crosshair at the fingertip.

Mirrors the hand cursor the user asked for — index/thumb pinch (with a hole),
curled fingers, and a small "+" at the tip which marks the exact point being
selected (its centre is the cursor hotspot). Sized like a normal mouse cursor.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPixmap,
)

_OUTLINE = QColor(35, 35, 40)
_FILL = QColor(245, 245, 248)
# Crosshair centre in the 64x64 design space — used as the hotspot.
_HOT = (20.0, 13.0)


def _stroke(points, width: float) -> QPainterPath:
    path = QPainterPath(QPointF(*points[0]))
    for pt in points[1:]:
        path.lineTo(QPointF(*pt))
    stroker = QPainterPathStroker()
    stroker.setWidth(width)
    stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
    stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return stroker.createStroke(path)


def _hand_pixmap(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    u = size / 64.0

    hand = QPainterPath()
    hand.addRoundedRect(QRectF(27 * u, 26 * u, 25 * u, 31 * u), 12 * u, 12 * u)  # fingers+palm
    hand = hand.united(_stroke([(31 * u, 32 * u), (25 * u, 23 * u), (20 * u, 15 * u)], 10 * u))   # index
    hand = hand.united(_stroke([(31 * u, 43 * u), (24 * u, 33 * u), (19 * u, 25 * u)], 8.5 * u))  # thumb
    hand = hand.simplified()
    hole = QPainterPath()
    hole.addEllipse(QPointF(23.5 * u, 25 * u), 4.6 * u, 6 * u)  # pinch hole
    hand = hand.subtracted(hole)

    p.setPen(QPen(_OUTLINE, 2 * u, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.setBrush(QBrush(_FILL))
    p.drawPath(hand)

    p.setPen(QPen(_OUTLINE, 1.3 * u))  # knuckle separation lines
    for lx in (35, 41, 47):
        p.drawLine(QPointF(lx * u, 27 * u), QPointF(lx * u, 34 * u))

    cx, cy, arm = _HOT[0] * u, _HOT[1] * u, 6 * u  # crosshair "+"
    p.setPen(QPen(_FILL, 4 * u, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(cx - arm, cy), QPointF(cx + arm, cy))
    p.drawLine(QPointF(cx, cy - arm), QPointF(cx, cy + arm))
    p.setPen(QPen(_OUTLINE, 1.4 * u))
    p.drawLine(QPointF(cx - arm, cy), QPointF(cx + arm, cy))
    p.drawLine(QPointF(cx, cy - arm), QPointF(cx, cy + arm))
    p.end()
    return pm


def capture_cursor(size: int = 44) -> QCursor:
    u = size / 64.0
    return QCursor(_hand_pixmap(size), round(_HOT[0] * u), round(_HOT[1] * u))
