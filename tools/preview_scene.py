#!/usr/bin/env python3
"""js/game.js 렌더러를 그대로 흉내 내어 '실제 게임 화면'을 PNG로 합성.
브라우저 없이 그래픽 완성도를 눈으로 검증하기 위함."""
import json, os, math
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), "..")
A = os.path.join(ROOT, "assets")
VW, VH, TILE = 216, 384, 16

def load(n): return Image.open(os.path.join(A, n)).convert("RGBA")
IMG = {f"tile{d}": load(f"tile_{d}.png") for d in range(4)}
IMG["hero_idle"] = load("hero_idle.png")
IMG["trashbag"] = load("trashbag.png")
IMG["plant"] = load("plant.png")
IMG["window"] = load("window.png")
IMG["cat"] = load("cat.png")

def shade(h, amt):
    c = [max(0, min(255, v + amt)) for v in hexrgb(h)]
    return tuple(c)

def hexrgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
def lerp(a, b, t): return a + (b - a) * t
def hexlerp(h1, h2, t):
    a, b = hexrgb(h1), hexrgb(h2)
    return tuple(int(lerp(a[i], b[i], t)) for i in range(3))

def vgrad(w, h, top, bot):
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(lerp(top[i], bot[i], t)) for i in range(3))
        for x in range(w):
            px[x, y] = c + (255,)
    return img

def rrect(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)

def render(stage, progress, hero_cell, scale_view=3):
    rows, cols = len(stage["grid"]), len(stage["grid"][0])
    availW, availH = VW - 24, VH - 96
    S = max(2, min(6, int(min(availW / (cols * TILE), availH / (rows * TILE)))))
    tilePx = TILE * S
    boardX = round((VW - cols * tilePx) / 2)
    boardY = round((VH - rows * tilePx) / 2) + 8

    # ---- 픽셀 방 배경 ----
    WALL_H = 92
    img = Image.new("RGBA", (VW, VH), shade(stage["floor"], 0) + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, VW, WALL_H), fill=hexrgb(stage["wall"]) + (255,))
    for r, yy in enumerate(range(10, WALL_H - 12, 14)):
        for xx in range(8 + (9 if r % 2 else 0), VW, 18):
            d.rectangle((xx, yy, xx + 1, yy + 1), fill=(255, 255, 255, 70))
    # 창문
    ww, wh = 70, 60
    wx, wy = (VW - ww) // 2, 14
    win = IMG["window"].resize((ww, wh), Image.NEAREST)
    img.alpha_composite(win, (wx, wy))
    # 베이스보드
    d.rectangle((0, WALL_H - 7, VW, WALL_H), fill=shade(stage["wall"], -26) + (255,))
    d.rectangle((0, WALL_H + 3, VW, VH), fill=hexrgb(stage["floor"]) + (255,))
    for xx in range(int((VW / 2) % 24), VW, 24):
        d.line((xx, WALL_H + 3, xx, VH), fill=(120, 86, 54, 26))
    for yy in range(WALL_H + 3, VH, 24):
        d.line((0, yy, VW, yy), fill=(120, 86, 54, 26))
    # 따뜻한 빛
    glow = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((VW / 2 - 150, WALL_H - 60, VW / 2 + 150, VH + 60),
               fill=(255, 238, 198, int((0.05 + 0.18 * progress) * 255)))
    img.alpha_composite(glow)
    # 소품
    ps = 2.3
    plant = IMG["plant"].resize((int(16 * ps), int(20 * ps)), Image.NEAREST)
    img.alpha_composite(plant, (4, int(VH - 20 * ps - 2)))
    cs = 2.1
    cat = IMG["cat"].resize((int(16 * cs), int(16 * cs)), Image.NEAREST)
    img.alpha_composite(cat, (int(VW - 16 * cs - 4), int(VH - 16 * cs - 6)))

    # 보드 러그
    pad = round(S * 3)
    bx, by = boardX - pad, boardY - pad
    bw, bh = cols * tilePx + pad * 2, rows * tilePx + pad * 2
    rrect(d, (bx + 1, by + 5, bx + 1 + bw, by + 5 + bh), 8, (70, 50, 30, 46))
    rrect(d, (bx, by, bx + bw, by + bh), 8, shade(stage["floor"], -34) + (255,))
    rrect(d, (bx + 2, by + 2, bx + bw - 2, by + bh - 2), 6, shade(stage["floor"], -14) + (255,))

    # 현재 내구도(진행 반영: progress 비율만큼 무작위로 닦였다고 가정 — 데모용으로 일부만)
    dur = [r[:] for r in stage["grid"]]

    # 타일 + 핍
    pip_col = {3: (240, 214, 110), 2: (159, 182, 224), 1: (231, 225, 210)}
    for y in range(rows):
        for x in range(cols):
            if stage["grid"][y][x] == 0:
                continue
            v = dur[y][x]
            t = IMG[f"tile{v}"].resize((tilePx, tilePx), Image.NEAREST)
            img.alpha_composite(t, (boardX + x * tilePx, boardY + y * tilePx))
            if (x + y) & 1:
                ov = Image.new("RGBA", (tilePx, tilePx), (60, 40, 30, 18))
                img.alpha_composite(ov, (boardX + x * tilePx, boardY + y * tilePx))
            if v >= 2:
                r = max(1.5, S * 0.9); gap = r * 2.4
                tw = (v - 1) * gap
                cx = boardX + x * tilePx + tilePx / 2 - tw / 2
                cy = boardY + y * tilePx + tilePx - r * 2.2
                for i in range(v):
                    d.ellipse((cx + i * gap - r, cy - r, cx + i * gap + r, cy + r), fill=(0, 0, 0, 115))
                    rr = r * 0.7
                    d.ellipse((cx + i * gap - rr, cy - 0.5 - rr, cx + i * gap + rr, cy - 0.5 + rr), fill=pip_col[v])

    # 장식(쓰레기)
    for dec in stage.get("decor", []):
        if dec["x"] < cols and dec["y"] < rows and stage["grid"][dec["y"]][dec["x"]] > 0:
            t = IMG[dec["type"]].resize((tilePx, tilePx), Image.NEAREST)
            img.alpha_composite(t, (boardX + dec["x"] * tilePx, boardY + dec["y"] * tilePx - round(S * 4)))

    # 히어로
    hx, hy = hero_cell
    baseX = boardX + hx * tilePx + tilePx / 2
    footY = boardY + hy * tilePx + tilePx
    d.ellipse((baseX - tilePx * 0.32, footY - S * 2 - tilePx * 0.13,
               baseX + tilePx * 0.32, footY - S * 2 + tilePx * 0.13), fill=(0, 0, 0, 64))
    hero = IMG["hero_idle"].resize((16 * S, 24 * S), Image.NEAREST)
    img.alpha_composite(hero, (int(baseX - 16 * S / 2), int(footY - 24 * S + S * 2)))

    big = img.resize((VW * scale_view, VH * scale_view), Image.NEAREST)
    return big

if __name__ == "__main__":
    with open(os.path.join(ROOT, "stages", "stages.json"), encoding="utf-8") as f:
        stages = json.load(f)
    by_id = {s["id"]: s for s in stages}
    shots = [
        (by_id[1], 0.25, (1, 1)),
        (by_id[6], 0.55, (0, 2)),
        (by_id[8], 0.8, (3, 1)),
    ]
    imgs = [render(st, p, h) for st, p, h in shots]
    gap = 16
    W = sum(i.width for i in imgs) + gap * (len(imgs) + 1)
    H = max(i.height for i in imgs) + gap * 2
    m = Image.new("RGBA", (W, H), (24, 22, 30, 255))
    x = gap
    for i in imgs:
        m.alpha_composite(i, (x, gap)); x += i.width + gap
    out = os.path.join(os.path.dirname(__file__), "_scene.png")
    m.save(out)
    print("scene preview:", out)
