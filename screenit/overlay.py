"""Full-screen selection overlay with a pixel-accurate magnifier loupe."""

from __future__ import annotations

import ctypes

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QImage,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QWidget

from .capture import Screenshot
from .cursor import capture_cursor

ACCENT = QColor(0, 153, 255)
MIN_SELECTION = 3  # px; smaller drags are treated as a cancel/click


class SelectionOverlay(QWidget):
    """Covers the whole virtual desktop and lets the user drag a rectangle.

    Emits :attr:`regionSelected` with a :class:`QRect` in image-local pixel
    coordinates, or :attr:`cancelled` if the user backs out.
    """

    regionSelected = Signal(QRect)
    cancelled = Signal()

    def __init__(self, shot: Screenshot, magnifier_size: int, magnifier_zoom: int):
        super().__init__()
        self._shot = shot
        self._image = QImage(
            shot.image.tobytes("raw", "RGB"),
            shot.width,
            shot.height,
            3 * shot.width,
            QImage.Format.Format_RGB888,
        ).copy()  # copy so it owns the buffer
        self._pixmap = QPixmap.fromImage(self._image)
        self._mag_size = magnifier_size
        self._mag_zoom = max(2, magnifier_zoom)

        self._origin: QPoint | None = None
        self._cursor = QPoint(0, 0)
        self._selecting = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setCursor(capture_cursor())
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setGeometry(shot.left, shot.top, shot.width, shot.height)

    def show_overlay(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        # Force the overlay above the taskbar so the tray/taskbar area is also
        # selectable (a plain stay-on-top window can sit behind the taskbar).
        try:
            HWND_TOPMOST = -1
            SWP_SHOWWINDOW = 0x0040
            ctypes.windll.user32.SetWindowPos(
                int(self.winId()), HWND_TOPMOST,
                self.x(), self.y(), self.width(), self.height(), SWP_SHOWWINDOW,
            )
        except Exception:  # noqa: BLE001 - best effort, not fatal
            pass

    # ------------------------------------------------------------------ events
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin = event.position().toPoint()
            self._selecting = True
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancelled.emit()
            self.close()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._cursor = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._origin is None:
            return
        rect = self._selection_rect()
        self._selecting = False
        if rect.width() < MIN_SELECTION or rect.height() < MIN_SELECTION:
            self.cancelled.emit()
        else:
            self.regionSelected.emit(rect)
        self.close()

    # ------------------------------------------------------------------ helpers
    def _selection_rect(self) -> QRect:
        if self._origin is None:
            return QRect()
        # Build from an explicit size so a 200px drag yields exactly 200px.
        # (QRect(p1, p2) treats both corners as inclusive -> off by one.)
        x1, y1 = self._origin.x(), self._origin.y()
        x2, y2 = self._cursor.x(), self._cursor.y()
        left, top = min(x1, x2), min(y1, y2)
        return QRect(left, top, abs(x2 - x1), abs(y2 - y1)).intersected(self.rect())

    # ------------------------------------------------------------------ paint
    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        # Screenshot at full brightness — no dimming.
        painter.drawPixmap(0, 0, self._pixmap)

        if self._selecting and self._origin is not None:
            rect = self._selection_rect()
            painter.setPen(QPen(ACCENT, 1))
            painter.drawRect(rect.adjusted(0, 0, -1, -1))

        self._draw_magnifier(painter)
        painter.end()

    def _draw_magnifier(self, painter: QPainter) -> None:
        cx, cy = self._cursor.x(), self._cursor.y()
        box = self._mag_size
        panel_h = 44
        margin = 24

        # The hand cursor (with its target ring) marks the point; no reticle.

        # Loupe sits in the top-left corner by default and only moves to the
        # bottom-right while the cursor is over that top-left area.
        total_h = box + panel_h
        tl = QRect(margin, margin, box, total_h)
        if tl.adjusted(-margin, -margin, margin, margin).contains(self._cursor):
            bx = self.width() - margin - box
            by = self.height() - margin - total_h
        else:
            bx, by = margin, margin
        box_rect = QRect(bx, by, box, box)

        sample = max(2, box // self._mag_zoom)
        scale = box / sample
        src_left = min(max(cx - sample // 2, 0), max(self._image.width() - sample, 0))
        src_top = min(max(cy - sample // 2, 0), max(self._image.height() - sample, 0))

        # Zoomed, non-smoothed pixels.
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.drawImage(box_rect, self._image, QRect(src_left, src_top, sample, sample))

        # Highlight the exact pixel under the cursor + crosshair at its centre.
        hx = bx + (cx - src_left) * scale
        hy = by + (cy - src_top) * scale
        painter.setPen(QPen(QColor(255, 255, 255, 200), 1))
        painter.drawRect(int(hx), int(hy), int(scale), int(scale))
        center_x = int(hx + scale / 2)
        center_y = int(hy + scale / 2)
        painter.setPen(QPen(ACCENT, 1))
        painter.drawLine(bx, center_y, bx + box, center_y)
        painter.drawLine(center_x, by, center_x, by + box)

        # Frame.
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setPen(QPen(QColor(255, 255, 255, 230), 2))
        painter.drawRect(box_rect)

        self._draw_readout(painter, bx, by + box, box, panel_h, cx, cy, src_left, src_top)

    def _draw_readout(self, painter, x, y, w, h, cx, cy, src_left, src_top) -> None:
        painter.fillRect(QRect(x, y, w, h), QColor(20, 20, 20, 230))
        painter.setPen(QColor(235, 235, 235))
        font = QFont("Consolas")
        font.setPointSize(10)
        painter.setFont(font)

        color = self._image.pixelColor(
            min(cx, self._image.width() - 1), min(cy, self._image.height() - 1)
        )
        hex_color = f"#{color.red():02X}{color.green():02X}{color.blue():02X}"

        # Desktop coordinates (account for a negative virtual-screen origin).
        dx, dy = cx + self._shot.left, cy + self._shot.top
        line1 = f"{dx}, {dy}   {hex_color}"
        if self._selecting and self._origin is not None:
            rect = self._selection_rect()
            line2 = f"{rect.width()} x {rect.height()} px"
        else:
            line2 = "drag to select  -  Esc to cancel"

        painter.drawText(QRect(x + 8, y + 5, w - 16, 18), Qt.AlignmentFlag.AlignLeft, line1)
        painter.drawText(QRect(x + 8, y + 23, w - 16, 18), Qt.AlignmentFlag.AlignLeft, line2)
