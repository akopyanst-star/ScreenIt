"""Put a PIL image onto the Windows clipboard as a device-independent bitmap."""

from __future__ import annotations

import io

import win32clipboard
from PIL import Image


def copy_image(image: Image.Image) -> None:
    """Copy ``image`` to the clipboard in CF_DIB format.

    A BMP file is a 14-byte file header followed by the DIB; the clipboard
    wants just the DIB, so we strip the first 14 bytes.
    """
    with io.BytesIO() as buffer:
        image.convert("RGB").save(buffer, "BMP")
        dib = buffer.getvalue()[14:]

    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, dib)
    finally:
        win32clipboard.CloseClipboard()
