from typing import Tuple

DEFAULT_COLOR = 0x00ff88


def hex_to_rgb(hex_val: int) -> Tuple[int, int, int]:
    """Convert hex color int to (r, g, b) tuple."""
    return ((hex_val >> 16) & 0xff, (hex_val >> 8) & 0xff, hex_val & 0xff)


def rgb_to_hex(r: int, g: int, b: int) -> int:
    """Convert (r, g, b) tuple to hex color int."""
    return (min(255, max(0, r)) << 16) | (min(255, max(0, g)) << 8) | min(255, max(0, b))


def shade_tint(hex_val: int, factor: float) -> int:
    """Tint a hex color by brightness factor."""
    r, g, b = hex_to_rgb(hex_val)
    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))
    return rgb_to_hex(r, g, b)


def hex_to_tk_color(hex_val: int) -> str:
    """Convert hex int to tkinter color string."""
    return f'#{hex_val:06x}'
