"""Custom capture cursor: a pinch-gesture hand with a "+" crosshair.

Reproduces the reference icon — index/thumb pinch loop (with a hole and a small
dot), three curled fingers, palm/wrist, and a separate crosshair whose centre is
the exact point being selected (the cursor hotspot). A thin dark outline keeps
the otherwise all-white shape visible over light screen content.
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

_OUTLINE = QColor(40, 40, 45)
_FILL = QColor(255, 255, 255)
# Crosshair centre in the 100x100 design space — used as the hotspot.
_HOT = (19.0, 30.0)


def _stroke(points, width: float) -> QPainterPath:
    path = QPainterPath(QPointF(*points[0]))
    for pt in points[1:]:
        path.lineTo(QPointF(*pt))
    stroker = QPainterPathStroker()
    stroker.setWidth(width)
    stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
    stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return stroker.createStroke(path)


def _cap(x, y, w, h, u) -> QPainterPath:
    p = QPainterPath()
    r = w / 2 * u
    p.addRoundedRect(QRectF(x * u, y * u, w * u, h * u), r, r)
    return p


def _hand_pixmap(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    u = size / 100.0
    pen = QPen(_OUTLINE, max(1.2, size * 0.035), Qt.PenStyle.SolidLine,
               Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(QBrush(_FILL))

    hand = QPainterPath()
    hand.addEllipse(QPointF(50 * u, 46 * u), 13 * u, 13 * u)               # pinch loop
    hand.addRoundedRect(QRectF(43 * u, 50 * u, 42 * u, 47 * u), 15 * u, 15 * u)  # palm+wrist
    hand = hand.united(_cap(60, 28, 8.5, 36, u))                          # middle finger
    hand = hand.united(_cap(69.5, 31, 8.5, 34, u))                        # ring finger
    hand = hand.united(_cap(79, 36, 8, 29, u))                           # pinky
    hand = hand.united(_stroke([(43 * u, 40 * u), (40 * u, 36 * u)], 6.5 * u))  # pinch tip
    hand = hand.simplified()
    hole = QPainterPath()
    hole.addEllipse(QPointF(50 * u, 46 * u), 8 * u, 8 * u)
    hand = hand.subtracted(hole)
    p.drawPath(hand)

    p.drawEllipse(QPointF(54 * u, 48 * u), 2.2 * u, 2.2 * u)              # dot in the hole

    cx, cy, th, arm, gap = _HOT[0], _HOT[1], 8, 11, 3.5
    for r in (
        QRectF((cx - th / 2) * u, (cy - gap - arm) * u, th * u, arm * u),
        QRectF((cx - th / 2) * u, (cy + gap) * u, th * u, arm * u),
        QRectF((cx - gap - arm) * u, (cy - th / 2) * u, arm * u, th * u),
        QRectF((cx + gap) * u, (cy - th / 2) * u, arm * u, th * u),
    ):
        bar = QPainterPath()
        bar.addRoundedRect(r, th / 2 * u, th / 2 * u)
        p.drawPath(bar)

    p.end()
    return pm


def capture_cursor(size: int = 48) -> QCursor:
    u = size / 100.0
    return QCursor(_hand_pixmap(size), round(_HOT[0] * u), round(_HOT[1] * u))
