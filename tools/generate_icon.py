"""Generate assets/icon.ico (run once; output is committed to the repo)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ACCENT = (0, 153, 255, 255)
BG = (30, 32, 36, 255)


def draw(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 64
    d.rounded_rectangle([4 * s, 4 * s, 60 * s, 60 * s], radius=12 * s, fill=BG)
    lw = max(1, int(4 * s))
    d.line([32 * s, 14 * s, 32 * s, 50 * s], fill=ACCENT, width=lw)
    d.line([14 * s, 32 * s, 50 * s, 32 * s], fill=ACCENT, width=lw)
    d.rectangle([20 * s, 20 * s, 44 * s, 44 * s], outline=ACCENT, width=lw)
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
