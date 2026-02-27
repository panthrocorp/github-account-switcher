from __future__ import annotations

import colorsys
import hashlib
from pathlib import Path

import platformdirs
from PIL import Image, ImageDraw, ImageFont

ICON_SIZE = 64
BORDER_WIDTH = 4
ACTIVE_BORDER_COLOUR = (40, 200, 80, 255)
CACHE_DIR = Path(platformdirs.user_cache_dir("gh-switcher")) / "icons"


def icon_path(username: str, active: bool) -> Path:
    suffix = "-active" if active else ""
    return CACHE_DIR / f"{username}{suffix}.png"


def generate_icon(username: str, active: bool) -> Path:
    """Return path to a (possibly cached) icon for *username*."""
    path = icon_path(username, active)
    if path.exists():
        return path

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    bg_colour = _username_colour(username)
    initials = _initials(username)

    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), bg_colour)
    draw = ImageDraw.Draw(img)

    if active:
        draw.ellipse(
            [0, 0, ICON_SIZE - 1, ICON_SIZE - 1],
            outline=ACTIVE_BORDER_COLOUR,
            width=BORDER_WIDTH,
        )

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26
        )
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), initials, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (ICON_SIZE - text_w) // 2 - bbox[0]
    y = (ICON_SIZE - text_h) // 2 - bbox[1]
    draw.text((x, y), initials, fill=(255, 255, 255, 255), font=font)

    img.save(path, "PNG")
    return path


def invalidate_cache(username: str) -> None:
    """Remove cached icons for *username* so they are regenerated."""
    for suffix in ("", "-active"):
        p = CACHE_DIR / f"{username}{suffix}.png"
        p.unlink(missing_ok=True)


def _initials(username: str) -> str:
    parts = username.replace("-", " ").replace("_", " ").split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return username[:2].upper()


def _username_colour(username: str) -> tuple[int, int, int, int]:
    digest = hashlib.md5(username.encode(), usedforsecurity=False).digest()
    hue_byte = digest[0]
    # Map 0-255 to a hue, then convert HSV to RGB (S=0.6, V=0.75)
    h = hue_byte / 255.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.6, 0.75)
    return (int(r * 255), int(g * 255), int(b * 255), 255)
