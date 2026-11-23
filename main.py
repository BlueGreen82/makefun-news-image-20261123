#!/usr/bin/env python3
"""The World in One Day - Monday 23 November 2026.

Draws a deterministic newspaper front page (1024x1024 PNG) summing up the
day's world news, using only the Python standard library. No network, no
clock, no randomness: the same input always produces the same bytes
(fixed zlib level, filter-0 scanlines, fixed palette).

Writes entry.png to MAKEFUN_OUTPUT_DIR (default /output).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 230)
INK = (26, 26, 32)
NAVY = (18, 36, 70)
RED = (186, 48, 38)
GOLD = (216, 164, 60)
BLUE = (38, 92, 160)
GREEN = (34, 139, 84)
GRAY = (110, 106, 96)
SKY = (133, 188, 232)
WHITE = (255, 255, 255)
TEAL = (14, 122, 122)
ORANGE = (214, 110, 44)
LIGHT = (232, 226, 210)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, '#' on, '.' off.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#...#", "#....", "#....", "#....", "#...#", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#...#", "#....", ".###.", "....#", "#...#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#..##", "#..##"),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '&': (".###.", "#...#", "#...#", ".#...", "#.#.#", "#..#.", ".##.#"),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
}

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            for b in range(t):
                px(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, fill=True):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        if fill:
            for xx in range(cx - dx, cx + dx + 1):
                px(xx, cy + dy, c)
        else:
            px(cx - dx, cy + dy, c)
            px(cx + dx, cy + dy, c)


def text(s, x, y, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for row in range(7):
            for col in range(5):
                if g[row][col] == '#':
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx - x


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def text_center(s, y, scale, c, x0=0, x1=W):
    w = text_w(s, scale)
    text(s, x0 + (x1 - x0 - w) // 2, y, scale, c)


def wrap(s, scale, maxw):
    words = s.split(' ')
    lines = []
    cur = ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, scale) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(s, x, y, scale, c, maxw, gap=4):
    lines = wrap(s, scale, maxw)
    yy = y
    for ln in lines:
        text(ln, x, yy, scale, c)
        yy += 7 * scale + gap
    return yy


# ---------------------------------------------------------------- icons
def icon_globe(x, y, s, c):
    circle(x + s // 2, y + s // 2, s // 2 - 2, SKY)
    circle(x + s // 2, y + s // 2, s // 2 - 2, BLUE, fill=False)
    circle(x + s // 3, y + s // 3, s // 7, GREEN)
    circle(x + 2 * s // 3, y + 2 * s // 3, s // 6, GREEN)
    rect(x + s // 4, y + s // 2 - 1, s // 2, 2, BLUE)
    rect(x + s // 2 - 1, y + s // 4, 2, s // 2, BLUE)


def icon_flags(x, y, s, c):
    w = s // 3
    cols = (RED, GOLD, BLUE)
    for i in range(3):
        rect(x + i * w + 2, y + 4, w - 4, s // 2, cols[i])
        vline(x + i * w + w // 2, y + 4, s - 6, INK, 2)


def icon_building(x, y, s, c):
    rect(x + 6, y + s // 4, s - 12, 3 * s // 4, GRAY)
    rect(x + 6, y + s // 4, s - 12, 4, INK)
    for r in range(3):
        for col in range(3):
            rect(x + 12 + col * (s // 4), y + s // 3 + r * (s // 5), s // 8, s // 8, GOLD)
    line(x + s // 2, y + s // 4, x + s // 2 - 6, y + s // 2, RED, 3)
    line(x + s // 2 - 6, y + s // 2, x + s // 2 + 4, y + 3 * s // 4, RED, 3)


def icon_ship(x, y, s, c):
    line(x + s // 2, y + 6, x + s // 2, y + s // 2, INK, 3)
    rect(x + s // 2 + 2, y + 8, s // 4, s // 6, RED)
    for i in range(5):
        px(x + 6 + i * 3, y + s // 2 + i, BLUE)
    rect(x + 8, y + s // 2, s - 16, s // 6, NAVY)
    rect(x + 4, y + s // 2 + s // 6, s - 8, s // 8, NAVY)
    for k in range(3):
        xx = x + 6 + k * (s // 3)
        line(xx, y + s - 12, xx + 12, y + s - 12, SKY, 3)
        line(xx + 6, y + s - 7, xx + 18, y + s - 7, SKY, 3)


def icon_chart(x, y, s, c):
    base = y + s - 10
    hs = [s // 2 + 8, s // 3 + 4, s // 5]
    for i, hh in enumerate(hs):
        rect(x + 8 + i * (s // 4), base - hh, s // 6, hh, BLUE if i < 2 else RED)
    line(x + 6, y + 8, x + s - 8, base - 2, RED, 4)


def icon_flame(x, y, s, c):
    circle(x + s // 2, y + 2 * s // 3, s // 4, ORANGE)
    line(x + s // 2, y + 6, x + s // 3, y + 2 * s // 3, ORANGE, 4)
    line(x + s // 2, y + 6, x + 2 * s // 3, y + 2 * s // 3, ORANGE, 4)
    circle(x + s // 2, y + 2 * s // 3, s // 8, GOLD)
    for k in range(3):
        line(x + 6 + k * (s // 3), y + s - 8, x + 18 + k * (s // 3), y + s - 8, SKY, 3)


def icon_ballot(x, y, s, c):
    rect(x + 8, y + s // 3, s - 16, 2 * s // 3 - 4, BLUE)
    rect(x + 8, y + s // 3, s - 16, 6, NAVY)
    rect(x + s // 3, y + s // 3 + 2, s // 3, 3, WHITE)
    line(x + s // 4, y + s // 2, x + s // 2 - 2, y + 2 * s // 3, WHITE, 4)
    line(x + s // 2 - 2, y + 2 * s // 3, x + 3 * s // 4, y + s // 3 + 6, WHITE, 4)


ICONS = {
    'globe': icon_globe,
    'flags': icon_flags,
    'building': icon_building,
    'ship': icon_ship,
    'chart': icon_chart,
    'flame': icon_flame,
    'ballot': icon_ballot,
}

# ---------------------------------------------------------------- stories
LEAD = {
    'kicker': 'CLIMATE  -  ANTALYA, TURKEY',
    'color': RED,
    'headline': 'COP31 COLLAPSES',
    'body': "The climate summit ends with no deal. The EU and about 130 nations reject a final text that leaves out fossil fuels, after two days of overtime talks.",
    'icon': 'globe',
}

GRID = [
    {
        'kicker': 'DIPLOMACY  -  SHENZHEN',
        'color': NAVY,
        'headline': 'TRUMP, PUTIN, XI MEET',
        'body': "A historic trilateral summit agrees a 'Declaration toward Peace' on the sidelines of APEC.",
        'icon': 'flags',
    },
    {
        'kicker': 'WAR  -  UKRAINE',
        'color': RED,
        'headline': 'DYMER STRIKE KILLS 10',
        'body': "A Russian strike hits a home in Dymer. Boy, 7, pulled alive from the rubble after 14 hours.",
        'icon': 'building',
    },
    {
        'kicker': 'WAR  -  LIBYA',
        'color': NAVY,
        'headline': 'RUSSIAN WARSHIP SINKS',
        'body': "The corvette Merkury goes down in Benghazi port after a suspected Ukrainian sea-drone attack.",
        'icon': 'ship',
    },
    {
        'kicker': 'MARKETS  -  ASIA',
        'color': TEAL,
        'headline': 'AI SELL-OFF HITS ASIA',
        'body': "Shares tumble on AI bubble fears: the Nikkei falls 5.06% and the Kospi drops 5%.",
        'icon': 'chart',
    },
    {
        'kicker': 'ENERGY  -  HORMUZ',
        'color': ORANGE,
        'headline': 'TANKERS ABLAZE',
        'body': "Two tankers hit mines and catch fire near the strait. Trump threatens Iranian vessels.",
        'icon': 'flame',
    },
    {
        'kicker': 'POLITICS  -  WASHINGTON',
        'color': BLUE,
        'headline': 'DEMOCRATS WIN HOUSE',
        'body': "The largest House majority since 1992: at least 258 seats after a North Carolina recount.",
        'icon': 'ballot',
    },
]

STRIP = [
    ("SCIENCE", "Riemann proof claimed by an Anthropic mathematician and Claude."),
    ("INDONESIA", "Candy factory fire: dozens missing in Banten, 24 body bags found."),
    ("SPORT", "Liverpool 4-0 Man Utd on Pochettino debut. Verstappen wins in Vegas."),
]

# ---------------------------------------------------------------- draw page
rect(0, 0, W, H, PAPER)
rect(0, 0, W, 6, NAVY)
rect(0, H - 6, W, 6, NAVY)
rect(0, 0, 6, H, NAVY)
rect(W - 6, 0, 6, H, NAVY)

# Masthead
rect(10, 10, W - 20, 118, NAVY)
text_center("THE WORLD IN ONE DAY", 30, 6, WHITE)
hline(60, 92, W - 120, GOLD, 3)
text_center("THE DAY'S WORLD NEWS, IN ONE PICTURE", 104, 2, GOLD)

# Date line
text_center("MONDAY 23 NOVEMBER 2026", 150, 5, RED)
hline(90, 196, 280, NAVY, 2)
hline(W - 370, 196, 280, NAVY, 2)

# Lead story
ly = 222
text("COP31 COLLAPSES", 34, ly + 34, 6, INK)
text(LEAD['kicker'], 34, ly, 2, RED)
para(LEAD['body'], 34, ly + 92, 2, INK, 700, gap=3)
ICONS['globe'](800, ly + 8, 150, None)
hline(34, ly + 158, W - 68, INK, 2)

# Grid of six stories: 2 cols x 3 rows
gx, gy = 34, 410
cw, ch = (W - 68 - 24) // 2, 148
for i, st in enumerate(GRID):
    cx = gx + (i % 2) * (cw + 24)
    cy = gy + (i // 2) * ch
    ICONS[st['icon']](cx, cy + 26, 72, None)
    tx = cx + 84
    text(st['kicker'], tx, cy, 2, st['color'])
    text(st['headline'], tx, cy + 22, 3, INK)
    para(st['body'], tx, cy + 52, 2, INK, cw - 84, gap=3)
    if i % 2 == 0:
        vline(cx + cw + 12, cy + 4, ch - 16, LIGHT, 2)
    if i < 4:
        hline(cx, cy + ch - 8, cw, LIGHT, 2)

# Also-today strip
sy = 868
hline(34, sy, W - 68, INK, 2)
text("ALSO TODAY", 34, sy + 12, 3, RED)
yy = sy + 48
for kicker, line_text in STRIP:
    full = kicker + ": " + line_text
    lines = wrap(full, 2, W - 68)
    first = lines[0]
    kw = text_w(kicker + ": ", 2)
    text(kicker + ": ", 34, yy, 2, NAVY)
    text(first[len(kicker) + 2:], 34 + kw, yy, 2, INK)
    yy += 22
    for extra in lines[1:]:
        text(extra, 34, yy, 2, INK)
        yy += 22

# Footer
hline(34, 984, W - 68, NAVY, 2)
text_center("MONDAY 23 NOVEMBER 2026  -  ONE DAY, ONE PICTURE", 994, 2, GRAY)


# ---------------------------------------------------------------- PNG encode
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    return png


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = encode_png()
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
