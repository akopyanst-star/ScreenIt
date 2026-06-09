"""Generate assets/icon.ico (run once; output is committed to the repo)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ACCENT = (0, 153, 255, 255)
WHITE = (255, 255, 255, 255)


def draw(size: int) -> Image.Image:
    """Bold, full-bleed glyph so it reads large in the tray."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 64
    # Background fills almost the whole canvas (small margin only).
    d.rounded_rectangle([1 * s, 1 * s, 63 * s, 63 * s], radius=12 * s, fill=ACCENT)
    lw = max(2, int(6 * s))
    # White crosshair, edge to edge.
    d.line([32 * s, 8 * s, 32 * s, 56 * s], fill=WHITE, width=lw)
    d.line([8 * s, 32 * s, 56 * s, 32 * s], fill=WHITE, width=lw)
    # White selection square.
    d.rectangle([16 * s, 16 * s, 48 * s, 48 * s], outline=WHITE, width=lw)
    return img


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
    out.parent.mkdir(parents=True, exist_ok=True)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    base = draw(256)
    base.save(out, sizes=[(s, s) for s in sizes])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
