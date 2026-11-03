#!/usr/bin/env python3
"""Draws the marathi theme's wallpapers from nothing but code: a Sahyadri fort on a flat-topped Deccan
plateau, with stone bastions (buruj), a gate and a saffron bhagwa flag, in four lights. No photos,
artwork or fonts are used, so the pictures are original (CC0) and can be redrawn by anyone.

    python3 make_wallpapers.py          # needs Pillow and NumPy; writes wallpapers/*.jpg

Kept dark on purpose (see themes/README.md, Wallpapers): the clock sits top left and the dock band
across the bottom third, so the top-left corner and the bottom stay close to black.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
S = 2
w, h = W * S, H * S
OUT = Path(__file__).resolve().parent / "wallpapers"

BHAGWA = (255, 122, 20)


def gradient(stops):
    ys = np.linspace(0, 1, h)
    img = np.zeros((h, w, 3))
    for c in range(3):
        col = np.interp(ys, [p for p, _ in stops], [s[c] for _, s in stops])
        img[:, :, c] = col[:, None]
    return img


def glow(img, cx, cy, radius, colour, strength):
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.25) ** 2) / radius
    a = np.clip(1 - d, 0, 1) ** 2.2 * strength
    for c in range(3):
        img[:, :, c] = img[:, :, c] * (1 - a) + colour[c] * a
    return img


def ridge(rng, base, rough, mesas, x_scale=1.0):
    """A Sahyadri skyline: smooth noise, then flat tops cut where the line rises (Deccan trap mesas)."""
    xs = np.arange(w)
    y = np.full(w, base, dtype=float)
    for octave in range(5):
        f = (octave + 1) * 1.7 / w * x_scale
        amp = rough / (octave + 1) ** 1.3
        y += amp * np.sin(xs * f * 2 * math.pi + rng.uniform(0, 6.28))
    for cx, half, top in mesas:
        cx, half = cx * w, half * w
        edge = half * 0.22
        d = np.abs(xs - cx)
        lift = np.clip((half + edge - d) / edge, 0, 1)
        lift = lift * lift * (3 - 2 * lift)
        target = top * h + 6 * S * np.sin(xs / (40 * S))
        y = y * (1 - lift) + np.minimum(y, target) * lift
    return y


def fill_below(img, profile, colour, haze=None, haze_amt=0.0):
    yy = np.arange(h)[:, None]
    mask = yy >= profile[None, :]
    col = np.array(colour, dtype=float)
    if haze is not None:
        col = col * (1 - haze_amt) + np.array(haze) * haze_amt
    img[mask] = col
    return img


def mist(img, y0, y1, colour, amount):
    ys = np.arange(h)
    band = np.clip(1 - np.abs(ys - (y0 + y1) / 2) / ((y1 - y0) / 2), 0, 1) ** 1.5 * amount
    for c in range(3):
        img[:, :, c] = img[:, :, c] * (1 - band[:, None]) + colour[c] * band[:, None]
    return img


def fort(draw, top_y, x0, x1, stone, lights=None, rng=None):
    """Curtain wall with crenellations, round bastions and a gate, along the mesa top."""
    wall_h = 34 * S
    y = top_y
    draw.rectangle([x0, y - wall_h, x1, y + 8 * S], fill=stone)
    step = 14 * S
    for x in range(int(x0), int(x1) - step, step * 2):
        draw.rectangle([x, y - wall_h - 9 * S, x + step, y - wall_h], fill=stone)
    n = 5
    for i in range(n):
        bx = x0 + (x1 - x0) * (i + 0.5) / n
        r = 26 * S
        bh = wall_h + 22 * S
        draw.rectangle([bx - r, y - bh, bx + r, y + 8 * S], fill=stone)
        draw.ellipse([bx - r, y - bh - r * 0.35, bx + r, y - bh + r * 0.35], fill=stone)
        for k in range(-2, 3):
            draw.rectangle([bx + k * 10 * S - 3 * S, y - bh - r * 0.35 - 8 * S, bx + k * 10 * S + 3 * S,
                            y - bh], fill=stone)
        if lights:
            draw.ellipse([bx - 3 * S, y - bh * 0.55 - 3 * S, bx + 3 * S, y - bh * 0.55 + 3 * S], fill=lights)
    gx = x0 + (x1 - x0) * 0.6
    gw, gh = 44 * S, 70 * S
    draw.rectangle([gx - gw, y - gh, gx + gw, y + 8 * S], fill=stone)
    draw.ellipse([gx - gw, y - gh - gw * 0.5, gx + gw, y - gh + gw * 0.5], fill=stone)
    arch = (int(stone[0] * 0.45), int(stone[1] * 0.45), int(stone[2] * 0.45))
    if lights:
        arch = lights
    draw.rectangle([gx - 14 * S, y - 30 * S, gx + 14 * S, y + 8 * S], fill=arch)
    draw.ellipse([gx - 14 * S, y - 44 * S, gx + 14 * S, y - 16 * S], fill=arch)
    if lights and rng is not None:
        for _ in range(26):
            lx = rng.uniform(x0 + 10 * S, x1 - 10 * S)
            ly = y - rng.uniform(6, 26) * S
            draw.ellipse([lx - 2 * S, ly - 2 * S, lx + 2 * S, ly + 2 * S], fill=lights)
    # The bhagwa: a pole on the tallest bastion with the double-pointed saffron pennant.
    fx = x0 + (x1 - x0) * (2.5 / n)
    fy = y - wall_h - 22 * S - 26 * S * 0.35
    pole_top = fy - 120 * S
    draw.rectangle([fx - 2 * S, pole_top, fx + 2 * S, fy], fill=stone)
    fw, fh = 78 * S, 58 * S
    draw.polygon([(fx + 2 * S, pole_top), (fx + fw, pole_top + fh * 0.32), (fx + fw * 0.55, pole_top + fh * 0.42),
                  (fx + fw * 0.92, pole_top + fh * 0.8), (fx + 2 * S, pole_top + fh)], fill=BHAGWA)
    return fx, pole_top


def birds(draw, rng, n, region, colour):
    x0, y0, x1, y1 = region
    for _ in range(n):
        x, y = rng.uniform(x0, x1) * w, rng.uniform(y0, y1) * h
        s = rng.uniform(5, 10) * S
        draw.line([(x - s, y - s * 0.4), (x, y), (x + s, y - s * 0.4)], fill=colour, width=max(2, int(1.3 * S)))


def stars(img, rng, n, ymax):
    for _ in range(n):
        x, y = int(rng.uniform(0, w)), int(rng.uniform(0, ymax * h))
        b = rng.uniform(120, 255) * (1 - y / (ymax * h)) ** 0.6
        r = 1 if rng.random() < 0.85 else 2
        img[max(0, y - r):y + r, max(0, x - r):x + r] = np.maximum(img[max(0, y - r):y + r, max(0, x - r):x + r], b)
    return img


def akash_kandil(draw, cx, top, colour, string_colour):
    """A star-shaped Diwali sky lantern hanging from a string."""
    r = 34 * S
    cy = top + 120 * S
    draw.line([(cx, 0), (cx, cy - r)], fill=string_colour, width=2 * S)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=colour)
    for k in range(5):
        x = cx - 14 * S + k * 7 * S
        draw.line([(x, cy + r * 0.6), (x, cy + r * 0.6 + 40 * S)], fill=colour, width=2 * S)


SCENES = {
    # name: sky stops, sun/moon, mist, ridge colours, stone, extras
    "01-pahat": dict(  # dawn (पहाट)
        sky=[(0, (8, 10, 22)), (0.35, (40, 36, 70)), (0.55, (190, 110, 90)), (0.62, (245, 170, 110))],
        orb=(0.78, 0.60, 260, (255, 200, 140), 0.55), mist=(0.58, 0.72, (210, 150, 130), 0.55),
        layers=[(60, 46, 70), (40, 30, 48), (22, 16, 26)], stone=(14, 10, 16), birds=0, night=False,
        caption="पहाट · सह्याद्री"),
    "02-sandhyakal": dict(  # golden dusk (संध्याकाळ)
        sky=[(0, (6, 6, 14)), (0.30, (52, 20, 30)), (0.52, (210, 90, 40)), (0.62, (255, 160, 60))],
        orb=(0.30, 0.61, 300, (255, 190, 90), 0.75), mist=(0.60, 0.70, (200, 90, 50), 0.35),
        layers=[(70, 30, 30), (42, 18, 22), (20, 8, 12)], stone=(12, 6, 8), birds=9, night=False,
        caption="संध्याकाळ · गडावर"),
    "03-ratra": dict(  # night (रात्र)
        sky=[(0, (2, 3, 10)), (0.45, (8, 12, 34)), (0.62, (22, 26, 58))],
        orb=(0.47, 0.17, 70, (240, 236, 220), 0.9), mist=(0.60, 0.70, (30, 36, 70), 0.3),
        layers=[(22, 26, 48), (12, 14, 30), (5, 6, 14)], stone=(4, 4, 10), birds=0, night=True,
        caption="रात्र · चांदणे"),
    "04-diwali": dict(  # Diwali night (दिवाळी)
        sky=[(0, (4, 2, 10)), (0.45, (24, 8, 30)), (0.62, (70, 24, 40))],
        orb=None, mist=(0.60, 0.70, (120, 50, 40), 0.3),
        layers=[(40, 18, 34), (22, 10, 22), (8, 4, 10)], stone=(6, 3, 8), birds=0, night=True,
        diwali=True, caption="दिवाळी · आकाशकंदील"),
}


def render(name, sc, seed):
    rng = np.random.default_rng(seed)
    img = gradient(sc["sky"] + [(1.0, sc["layers"][-1])])
    if sc["night"]:
        img = stars(img, rng, 900, 0.62)
    if sc["orb"]:
        ox, oy, rad, col, st = sc["orb"]
        img = glow(img, ox * w, oy * h, rad * S * 2.4, col, st * 0.55)
        if sc["night"]:
            yy, xx = np.mgrid[0:h, 0:w]
            d = np.sqrt((xx - ox * w) ** 2 + (yy - oy * h) ** 2)
            img[d < 34 * S] = col
        else:
            img = glow(img, ox * w, oy * h, rad * S * 0.5, col, st)
    far = ridge(rng, 0.63 * h, 30 * S, [(0.18, 0.08, 0.585), (0.55, 0.05, 0.60), (0.9, 0.07, 0.59)])
    img = fill_below(img, far, sc["layers"][0])
    img = mist(img, sc["mist"][0] * h, sc["mist"][1] * h, sc["mist"][2], sc["mist"][3])
    mid = ridge(rng, 0.70 * h, 40 * S, [(0.35, 0.06, 0.655), (0.80, 0.09, 0.64)])
    img = fill_below(img, mid, sc["layers"][1])
    near = ridge(rng, 0.80 * h, 26 * S, [(0.66, 0.17, 0.545)], x_scale=0.7)
    img = fill_below(img, near, sc["layers"][2])
    # Black foreground so the dock band reads on it.
    fg = ridge(rng, 0.90 * h, 18 * S, [])
    img = fill_below(img, fg, (2, 2, 4))
    yy = np.arange(h)[:, None]
    shade = np.clip((yy / h - 0.80) / 0.2, 0, 1) * 0.85
    img = img * (1 - shade[..., None])
    # Keep the clock's corner dark.
    yy, xx = np.mgrid[0:h, 0:w]
    corner = np.clip(1 - np.sqrt((xx / (0.45 * w)) ** 2 + (yy / (0.32 * h)) ** 2), 0, 1) ** 1.4 * 0.55
    img = img * (1 - corner[..., None])

    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(pil)
    top = int(0.545 * h)
    lights = (255, 190, 90) if sc["night"] else None
    fort(draw, top, 0.66 * w - 0.13 * w, 0.66 * w + 0.13 * w, sc["stone"], lights=lights, rng=rng)
    if sc["birds"]:
        birds(draw, rng, sc["birds"], (0.40, 0.30, 0.62, 0.45), (20, 8, 10))
    if sc.get("diwali"):
        # Below the top bar's pills (top right) and right of the clock (top left).
        for cx, t, col in [(0.44, 0.20, (255, 150, 40)), (0.52, 0.24, (240, 70, 90)), (0.88, 0.24, (255, 200, 60))]:
            akash_kandil(draw, cx * w, t * h, col, (60, 40, 30))
    pil = pil.filter(ImageFilter.GaussianBlur(0.6 * S)).resize((W, H), Image.LANCZOS)
    return pil


def main():
    OUT.mkdir(exist_ok=True)
    captions = []
    for i, (name, sc) in enumerate(SCENES.items()):
        img = render(name, sc, 1674 + i)
        img.save(OUT / f"{name}.jpg", quality=88, optimize=True, progressive=True)
        captions.append(f"{name}.jpg\t{sc['caption']}")
        print("wrote", OUT / f"{name}.jpg")
    (OUT / "captions.txt").write_text("\n".join(captions) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
