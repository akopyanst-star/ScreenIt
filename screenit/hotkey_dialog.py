"""Dialog that captures a hotkey by pressing it, instead of typing text."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

_MOD_KEYS = {Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta}

_SPECIAL = {
    Qt.Key.Key_Print: "PrintScreen",
    Qt.Key.Key_Insert: "Insert",
    Qt.Key.Key_Delete: "Delete",
    Qt.Key.Key_Home: "Home",
    Qt.Key.Key_End: "End",
    Qt.Key.Key_Space: "Space",
    Qt.Key.Key_Return: "Enter",
    Qt.Key.Key_Enter: "Enter",
    Qt.Key.Key_Tab: "Tab",
    Qt.Key.Key_Pause: "Pause",
}


def _key_token(key: int) -> str | None:
    """Map a Qt key code to a token that ``hotkey.parse_hotkey`` understands."""
    if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
        return chr(key)
    if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
        return chr(key)
    if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F24:
        return f"F{key - Qt.Key.Key_F1 + 1}"
    return _SPECIAL.get(Qt.Key(key))


def _modifiers(mods: Qt.KeyboardModifier) -> list[str]:
    out = []
    if mods & Qt.KeyboardModifier.ControlModifier:
        out.append("Ctrl")
    if mods & Qt.KeyboardModifier.AltModifier:
        out.append("Alt")
    if mods & Qt.KeyboardModifier.ShiftModifier:
        out.append("Shift")
    if mods & Qt.KeyboardModifier.MetaModifier:
        out.append("Win")
    return out


class HotkeyCaptureDialog(QDialog):
    """Press a combination; it shows up; click OK. Esc cancels."""

    def __init__(self, current: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ScreenIt — горячая клавиша")
        self.setModal(True)
        self.combo: str | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Нажмите нужное сочетание клавиш:"))

        self._display = QLabel(current)
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._display.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 16px;"
            "border: 1px solid #888; border-radius: 6px; min-width: 240px;"
        )
        layout.addWidget(self._display)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        # NoFocus so Tab/Space reach our key capture instead of pressing buttons.
        for btn in self._buttons.buttons():
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        self._ok = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok.setEnabled(False)
        layout.addWidget(self._buttons)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.reject()
            return

        mods = _modifiers(event.modifiers())
        if key in _MOD_KEYS:
            # Only modifiers held so far — show them as a hint, wait for a key.
            self._display.setText("+".join(mods) + "+…" if mods else "…")
            return

        token = _key_token(key)
        if token is None:
            return  # unsupported key, ignore

        self.combo = "+".join(mods + [token])
        self._display.setText(self.combo)
        self._ok.setEnabled(True)
