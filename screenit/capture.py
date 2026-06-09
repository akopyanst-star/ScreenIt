"""Screen capture of the whole virtual desktop, plus a crop helper."""

from __future__ import annotations

from dataclasses import dataclass

import mss
from PIL import Image


@dataclass
class Screenshot:
    image: Image.Image  # full virtual-desktop RGB image (physical pixels)
    left: int           # virtual-desktop origin (can be negative)
    top: int

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    def crop(self, x: int, y: int, w: int, h: int) -> Image.Image:
        """Crop a region given in image-local pixel coordinates."""
        return self.image.crop((x, y, x + w, y + h))


def grab_virtual_screen() -> Screenshot:
    """Grab every monitor as one image spanning the virtual desktop."""
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # index 0 == the full virtual desktop
        raw = sct.grab(monitor)
        image = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
    return Screenshot(image=image, left=monitor["left"], top=monitor["top"])
