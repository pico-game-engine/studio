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


def rgb565_to_rgb888(c: int) -> int:
    """Convert 16-bit RGB565 color to 24-bit RGB888. Input is masked to 16 bits."""
    c &= 0xFFFF
    r5 = (c >> 11) & 0x1F
    g6 = (c >> 5) & 0x3F
    b5 = c & 0x1F
    r8 = (r5 << 3) | (r5 >> 2)
    g8 = (g6 << 2) | (g6 >> 4)
    b8 = (b5 << 3) | (b5 >> 2)
    return (r8 << 16) | (g8 << 8) | b8


def rgb888_to_rgb565(c: int) -> int:
    """Convert 24-bit RGB888 color to 16-bit RGB565."""
    r8 = (c >> 16) & 0xFF
    g8 = (c >> 8) & 0xFF
    b8 = c & 0xFF
    r5 = r8 >> 3
    g6 = g8 >> 2
    b5 = b8 >> 3
    return (r5 << 11) | (g6 << 5) | b5
