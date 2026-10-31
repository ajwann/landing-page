"""Generate the site's derived images from aw.png.

Writes, at the repo root:
  aw-200.webp, aw-200.jpg  200x200 avatar (shown at 100x100, 2x for retina), each under 20 KB
  og-image.jpg             1200x630 social preview card on the Solarized dark background

Setup (once), from the repo root:
  python3 -m venv tools/.venv && tools/.venv/bin/pip install pillow

Run:
  tools/.venv/bin/python tools/make-images.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "aw.png"

# Solarized, matching tokens.css.
BASE03 = (0x00, 0x2B, 0x36)
BASE02 = (0x07, 0x36, 0x42)
BASE1 = (0x93, 0xA1, 0xA1)
BASE2 = (0xEE, 0xE8, 0xD5)
CYAN = (0x2A, 0xA1, 0x98)

AVATAR_SIZE = 200
AVATAR_MAX_BYTES = 20_000
OG_SIZE = (1200, 630)
OG_PHOTO = 300

NAME = "Adam Wanninger"
TITLE = "Technology & Product Leader"
FONTS = ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial Unicode.ttf"]


def square_crop(im: Image.Image) -> Image.Image:
    """Centre-crop to a square, the same crop CSS object-fit: cover makes."""
    side = min(im.size)
    left = (im.width - side) // 2
    top = (im.height - side) // 2
    return im.crop((left, top, left + side, top + side))


def flatten(im: Image.Image, background: tuple[int, int, int]) -> Image.Image:
    """Composite any transparency onto a solid colour and return RGB."""
    rgba = im.convert("RGBA")
    canvas = Image.new("RGBA", rgba.size, background + (255,))
    return Image.alpha_composite(canvas, rgba).convert("RGB")


def save_under(im: Image.Image, path: Path, fmt: str, max_bytes: int) -> None:
    """Save at the highest quality that fits under max_bytes."""
    for quality in range(90, 30, -5):
        im.save(path, fmt, quality=quality, optimize=True, **({"method": 6} if fmt == "WEBP" else {}))
        if path.stat().st_size <= max_bytes:
            print(f"{path.name}: {path.stat().st_size} bytes at q={quality}")
            return
    raise SystemExit(f"{path.name} still over {max_bytes} bytes at the lowest quality tried")


def font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in FONTS:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    raise SystemExit(f"None of these fonts exist: {FONTS}")


def make_avatar(square: Image.Image) -> None:
    # The avatar sits on the card (base02); flatten onto that so any
    # transparent edge reads the same as the PNG did.
    avatar = flatten(square, BASE02).resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)
    save_under(avatar, ROOT / "aw-200.webp", "WEBP", AVATAR_MAX_BYTES)
    save_under(avatar, ROOT / "aw-200.jpg", "JPEG", AVATAR_MAX_BYTES)


def make_og_image(square: Image.Image) -> None:
    card = Image.new("RGB", OG_SIZE, BASE03)
    draw = ImageDraw.Draw(card)

    # Supersample the circular mask so its edge is smooth.
    scale = 4
    mask = Image.new("L", (OG_PHOTO * scale, OG_PHOTO * scale), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, OG_PHOTO * scale - 1, OG_PHOTO * scale - 1), fill=255)
    mask = mask.resize((OG_PHOTO, OG_PHOTO), Image.LANCZOS)
    photo = flatten(square, BASE03).resize((OG_PHOTO, OG_PHOTO), Image.LANCZOS)

    x = 110
    y = (OG_SIZE[1] - OG_PHOTO) // 2
    ring = 6
    draw.ellipse((x - ring, y - ring, x + OG_PHOTO + ring, y + OG_PHOTO + ring), fill=BASE02)
    card.paste(photo, (x, y), mask)

    text_x = x + OG_PHOTO + 70
    name_font = font(76)
    title_font = font(40)
    name_box = draw.textbbox((0, 0), NAME, font=name_font)
    title_box = draw.textbbox((0, 0), TITLE, font=title_font)
    gap = 28
    block = (name_box[3] - name_box[1]) + gap + (title_box[3] - title_box[1])
    top = (OG_SIZE[1] - block) // 2
    draw.text((text_x, top - name_box[1]), NAME, font=name_font, fill=BASE2)
    title_top = top + (name_box[3] - name_box[1]) + gap
    draw.text((text_x, title_top - title_box[1]), TITLE, font=title_font, fill=BASE1)
    draw.rectangle((text_x, title_top + (title_box[3] - title_box[1]) + 30,
                    text_x + 90, title_top + (title_box[3] - title_box[1]) + 36), fill=CYAN)

    path = ROOT / "og-image.jpg"
    card.save(path, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"{path.name}: {path.stat().st_size} bytes")


def main() -> None:
    square = square_crop(Image.open(SOURCE))
    make_avatar(square)
    make_og_image(square)


if __name__ == "__main__":
    main()
