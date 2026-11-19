#!/usr/bin/env python3
"""Build meme.png (1080x1080) for the gta6-meme-x-01 v3 entry: '13-Year Wait'.

A 2x2 timeline (2013 / 2018 / 2023 / 2026). In every panel the SAME make.fun
ghost appears with the SAME magenta coin -- the coin is the constant while the
ghost's life changes around it. Everything is drawn with PIL shapes so the
ghost stays identical and recognisable in all four panels:

  * white body, thick black outline, rounded dome, scalloped bottom (3 bumps)
  * two black four-pointed sparkle eyes
  * a small round little hand (white circle, black outline)
  * a magenta coin (#EC008C) with a white five-pointed star in the middle
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "meme.png")

W = H = 1080
HEADER_H = 148
PANEL_W = W // 2            # 540
PANEL_H = (H - HEADER_H) // 2  # 466
BORDER = 6

MAGENTA = (236, 0, 140)
BLACK = (10, 10, 12)
WHITE = (255, 255, 255)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def star_points(cx, cy, r_outer, r_inner, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r_outer if i % 2 == 0 else r_inner
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sparkle_points(cx, cy, r):
    """A four-pointed sparkle: tall diamond with concave sides."""
    inner = r * 0.22
    pts = []
    tips = [(cx, cy - r), (cx + r * 0.62, cy), (cx, cy + r), (cx - r * 0.62, cy)]
    mids = [
        (cx + inner, cy - inner),
        (cx + inner, cy + inner),
        (cx - inner, cy + inner),
        (cx - inner, cy - inner),
    ]
    for i in range(4):
        pts.append(tips[i])
        pts.append(mids[i])
    return pts


def draw_coin(d, cx, cy, r):
    """The make.fun coin: magenta disc, black outline, white star."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MAGENTA, outline=BLACK, width=max(4, r // 7))
    d.polygon(star_points(cx, cy, r * 0.58, r * 0.24), fill=WHITE)


def make_ghost(height):
    """Render THE ghost, supersampled, and return an RGBA image.

    Design note (second-opinion consult, applied): the ghost's design is
    byte-identical in all four panels -- same body, same sparkle eyes, same
    smile -- and every panel calls this with the same height. The ghost is
    never aged, shrunk, dressed up or given a new expression; the years pass
    only through the props and the setting around it (backpack, school
    books, coffee and office, game case and beach).
    """
    ss = 3
    h = int(height * ss)
    w = int(height * 0.80 * ss)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(3, int(0.030 * h))

    pad = lw * 2
    left, right = pad, w - pad
    dome_cy = pad + (right - left) / 2
    base = h - pad - int(0.055 * h)          # bottom edge of the straight sides
    wave = int(0.055 * h)                    # scallop depth

    # Body outline: dome arc, straight sides, three-bump scalloped bottom.
    pts = []
    steps = 60
    for i in range(steps + 1):               # dome, left -> right over the top
        a = math.pi + i * math.pi / steps
        pts.append((w / 2 + (right - left) / 2 * math.cos(a),
                    dome_cy + (right - left) / 2 * math.sin(a)))
    pts.append((right, base))
    for i in range(1, 49):                   # bottom, right -> left, 3 bumps
        t = i / 48
        x = right - (right - left) * t
        y = base + wave * abs(math.sin(math.pi * 3 * t)) - wave
        pts.append((x, y + wave))
    pts.append((left, base))
    d.polygon(pts, fill=WHITE, outline=BLACK, width=lw)

    # Sparkle eyes -- the ghost's signature, identical in every panel.
    eye_y = int(0.40 * h)
    eye_r = int(0.115 * h)
    for ex in (int(0.36 * w), int(0.64 * w)):
        d.polygon(sparkle_points(ex, eye_y, eye_r), fill=BLACK)

    # Mouth: one gentle smile, the same in every panel.
    mx, my = w // 2, int(0.56 * h)
    mw = int(0.10 * w)
    d.arc([mx - mw, my - mw, mx + mw, my + mw], 15, 165, fill=BLACK, width=lw)

    img = img.resize((int(height * 0.80), int(height)), Image.LANCZOS)
    return img


def paste_ghost(panel, ghost, cx, bottom):
    panel.paste(ghost, (int(cx - ghost.width / 2), int(bottom - ghost.height)),
                ghost)


def draw_hand(panel, cx, cy, r=20):
    d = ImageDraw.Draw(panel)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=BLACK, width=5)


def outlined_text(d, xy, text, fnt, anchor="mm", fill=WHITE, stroke=5):
    d.text(xy, text, font=fnt, anchor=anchor, fill=fill,
           stroke_width=stroke, stroke_fill=BLACK)


def year_label(panel, year, tag, tag_fill=(20, 20, 24)):
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle([16, 14, 196, 92], radius=14, fill=BLACK)
    d.text((106, 53), year, font=font(56), anchor="mm", fill=WHITE)
    tw = d.textlength(tag, font=font(27))
    d.rounded_rectangle([16, PANEL_H - 58, 16 + tw + 30, PANEL_H - 12],
                        radius=12, fill=tag_fill)
    d.text((31, PANEL_H - 35), tag, font=font(27), anchor="lm", fill=WHITE)


def panel_2013():
    """2013 -- bedroom, GTA V poster on the wall, backpack, coin raised."""
    p = Image.new("RGB", (PANEL_W, PANEL_H), (43, 52, 96))
    d = ImageDraw.Draw(p)
    d.rectangle([0, PANEL_H - 92, PANEL_W, PANEL_H], fill=(24, 26, 44))  # floor
    # Window with a moon.
    d.rounded_rectangle([356, 92, 500, 238], radius=10, fill=(16, 20, 46),
                        outline=WHITE, width=4)
    d.ellipse([440, 112, 484, 156], fill=(245, 240, 200))
    # GTA V poster vibe: green block, big V, palm stripes.
    d.rectangle([36, 96, 196, 252], fill=(88, 168, 92), outline=BLACK, width=4)
    d.rectangle([36, 96, 196, 138], fill=(20, 20, 24))
    d.text((116, 117), "GTA V", font=font(30), anchor="mm", fill=WHITE)
    d.text((116, 196), "V", font=font(88), anchor="mm", fill=WHITE,
           stroke_width=3, stroke_fill=BLACK)
    # Bed block low in the corner, clear of the ghost's body.
    d.rounded_rectangle([352, 384, 528, 442], radius=12, fill=(150, 60, 90))
    d.rounded_rectangle([360, 364, 440, 398], radius=10, fill=WHITE)

    # The 2013 prop: a school backpack standing on the floor beside the
    # ghost (the ghost itself is NOT dressed up or shrunk -- same ghost).
    d.rounded_rectangle([40, 306, 128, 424], radius=16, fill=(64, 110, 200),
                        outline=BLACK, width=5)
    d.rounded_rectangle([58, 344, 110, 396], radius=10, fill=MAGENTA,
                        outline=BLACK, width=4)
    d.arc([52, 282, 116, 330], 180, 360, fill=BLACK, width=6)

    ghost = make_ghost(300)
    paste_ghost(p, ghost, 264, 440)
    # Raised little hand + the coin, held up hopefully.
    draw_hand(p, 382, 206, 21)
    draw_coin(d, 420, 162, 46)
    year_label(p, "2013", "DAY ONE BELIEVER")
    return p


def panel_2018():
    """2018 -- teen ghost at a school desk, books stacked, coin on the desk."""
    p = Image.new("RGB", (PANEL_W, PANEL_H), (38, 92, 82))
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, PANEL_W, 300], fill=(52, 118, 104))
    # Chalkboard with a hopeful scrawl.
    d.rectangle([300, 92, 512, 216], fill=(24, 54, 46), outline=(210, 190, 150), width=6)
    d.text((406, 132), "GTA 6", font=font(36), anchor="mm", fill=(235, 235, 220))
    d.text((406, 178), "when??", font=font(30), anchor="mm", fill=(235, 235, 220))

    ghost = make_ghost(300)
    paste_ghost(p, ghost, 252, 398)

    # Desk across the bottom, drawn over the ghost's base.
    d.rectangle([0, 348, PANEL_W, PANEL_H], fill=(122, 82, 48))
    d.rectangle([0, 348, PANEL_W, 362], fill=(160, 110, 66))
    # School books stacked on the desk.
    for i, (bw, col) in enumerate([(96, (196, 70, 70)), (84, (70, 110, 196)),
                                   (70, (230, 180, 60))]):
        y = 348 - 26 * (i + 1)
        d.rounded_rectangle([36, y, 36 + bw, y + 24], radius=4, fill=col,
                            outline=BLACK, width=3)
    # The coin waits on the desk, right by the ghost's hand -- same big
    # coin as every other panel (radius 46 everywhere).
    draw_hand(p, 380, 342, 21)
    draw_coin(d, 434, 326, 46)
    year_label(p, "2018", "STILL WAITING...")
    return p

def panel_2023():
    """2023 -- adult ghost in an office, coffee, keyboard, coin beside it."""
    p = Image.new("RGB", (PANEL_W, PANEL_H), (74, 86, 108))
    d = ImageDraw.Draw(p)
    # Window with blinds behind.
    d.rectangle([318, 88, 514, 268], fill=(150, 180, 205), outline=BLACK, width=4)
    for y in range(112, 262, 26):
        d.line([318, y, 514, y], fill=(110, 140, 165), width=5)
    # Wall calendar, still not launch day.
    d.rectangle([30, 96, 178, 238], fill=WHITE, outline=BLACK, width=4)
    d.rectangle([30, 96, 178, 132], fill=(196, 60, 60))
    d.text((104, 114), "2023", font=font(26), anchor="mm", fill=WHITE)
    for r in range(4):
        for c in range(5):
            d.rectangle([44 + c * 26, 146 + r * 22, 62 + c * 26, 160 + r * 22],
                        outline=(170, 170, 170), width=2)
    d.line([44, 146, 164, 224], fill=(196, 60, 60), width=4)
    d.line([164, 146, 44, 224], fill=(196, 60, 60), width=4)

    ghost = make_ghost(300)
    paste_ghost(p, ghost, 240, 400)

    # Office desk across the bottom.
    d.rectangle([0, 352, PANEL_W, PANEL_H], fill=(58, 60, 70))
    d.rectangle([0, 352, PANEL_W, 366], fill=(84, 86, 98))
    # Coffee cup -- fuel for the wait.
    d.rounded_rectangle([36, 372, 96, 424], radius=8, fill=WHITE, outline=BLACK, width=4)
    d.arc([84, 384, 118, 414], -80, 80, fill=BLACK, width=4)
    d.rectangle([42, 380, 90, 392], fill=(96, 58, 30))
    # Keyboard in front of the ghost.
    d.rounded_rectangle([150, 384, 372, 430], radius=8, fill=(22, 22, 28),
                        outline=BLACK, width=3)
    for r in range(2):
        for c in range(7):
            d.rounded_rectangle([164 + c * 28, 392 + r * 16, 184 + c * 28, 402 + r * 16],
                                radius=2, fill=(90, 92, 104))
    # The coin, patient as ever, right beside the keyboard.
    draw_hand(p, 388, 360, 21)
    draw_coin(d, 442, 340, 46)
    year_label(p, "2023", "STILL WAITING...")
    return p


def make_game_case():
    """A little GTA 6 game case the ghost finally gets to hold up."""
    case = Image.new("RGBA", (128, 172), (0, 0, 0, 0))
    d = ImageDraw.Draw(case)
    d.rounded_rectangle([4, 4, 124, 168], radius=8, fill=(24, 16, 44),
                        outline=BLACK, width=5)
    for i, col in enumerate([(255, 120, 90), (255, 170, 80), (236, 0, 140)]):
        d.rectangle([12, 18 + i * 16, 116, 30 + i * 16], fill=col)
    d.text((64, 92), "GTA", font=font(34), anchor="mm", fill=WHITE)
    d.text((64, 132), "VI", font=font(48), anchor="mm", fill=WHITE,
           stroke_width=2, stroke_fill=BLACK)
    return case.rotate(14, expand=True, resample=Image.BICUBIC)


def palm(d, x, y, s=1.0, flip=1):
    """A simple palm: curved trunk made of segments plus thick fronds."""
    pts = []
    for i in range(13):
        t = i / 12
        pts.append((x + flip * 34 * s * t * t, y - 150 * s * t))
    d.line(pts, fill=(110, 74, 40), width=int(13 * s))
    tx, ty = pts[-1]
    for ang in (-160, -115, -70, -25, 15):
        ex = tx + flip * 74 * s * math.cos(math.radians(ang))
        ey = ty + 52 * s * math.sin(math.radians(ang)) - 8 * s
        d.line([tx, ty, (tx + ex) / 2, ty - 26 * s, ex, ey],
               fill=(34, 130, 70), width=int(9 * s))


def panel_2026():
    """2026 -- Leonida beach at sunset. GTA 6 in one hand, coin in the other."""
    p = Image.new("RGB", (PANEL_W, PANEL_H), (255, 140, 90))
    d = ImageDraw.Draw(p)
    # Sunset sky gradient.
    top, mid = (255, 110, 110), (255, 186, 96)
    for y in range(0, 250):
        t = y / 250
        d.line([0, y, PANEL_W, y],
               fill=tuple(int(top[i] + (mid[i] - top[i]) * t) for i in range(3)))
    d.ellipse([232, 108, 322, 198], fill=(255, 226, 130))       # low sun
    d.rectangle([0, 238, PANEL_W, 322], fill=(38, 150, 170))    # the sea
    for x in range(10, PANEL_W, 64):
        d.line([x, 262, x + 34, 262], fill=(140, 220, 225), width=4)
        d.line([x + 22, 292, x + 52, 292], fill=(140, 220, 225), width=4)
    d.rectangle([0, 322, PANEL_W, PANEL_H], fill=(238, 203, 140))  # sand
    palm(d, 30, 452, 1.25, 1)
    palm(d, 516, 446, 1.15, -1)

    ghost = make_ghost(300)
    paste_ghost(p, ghost, 270, 442)

    # Coin raised high in the left hand -- it waited too.
    draw_hand(p, 140, 208, 21)
    draw_coin(d, 102, 160, 46)
    # ...and finally, the game itself, raised in the right hand.
    case = make_game_case()
    p.paste(case, (382, 96), case)
    draw_hand(p, 386, 238, 21)
    year_label(p, "2026", "FINALLY!", tag_fill=MAGENTA)
    return p


def build():
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)

    # Header caption: one bold line, sized to fit, white on black.
    text = "13 YEARS. THE COIN WAITED TOO."
    size = 66
    while size > 30 and d.textlength(text, font=font(size)) > W - 48:
        size -= 2
    outlined_text(d, (W // 2, HEADER_H // 2 + 2), text, font(size), stroke=6)

    panels = [panel_2013(), panel_2018(), panel_2023(), panel_2026()]
    for i, p in enumerate(panels):
        x = (i % 2) * PANEL_W
        y = HEADER_H + (i // 2) * PANEL_H
        img.paste(p, (x, y))

    # Thin white borders between and around the panels.
    d = ImageDraw.Draw(img)
    for i in range(2):
        for j in range(2):
            x, y = i * PANEL_W, HEADER_H + j * PANEL_H
            d.rectangle([x, y, x + PANEL_W - 1, y + PANEL_H - 1],
                        outline=WHITE, width=BORDER)
    d.rectangle([0, 0, W - 1, H - 1], outline=WHITE, width=BORDER)

    img.save(OUT)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    build()

