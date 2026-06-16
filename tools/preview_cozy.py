#!/usr/bin/env python3
"""코지 스타일-업 데모: 나무 마루 + 벽 몰딩/베이스보드 + 러그.
LimeZu Modern Interiors 분위기를 픽셀로 옮긴 한 장면(내 방)을 크게 렌더."""
import os, json, random
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..")
A = os.path.join(ROOT, "assets")
VW, VH, TILE = 216, 384, 16
load = lambda n: Image.open(os.path.join(A, n)).convert("RGBA")
IMG = {f"tile{d}": load(f"tile_{d}.png") for d in range(4)}
for n in ("hero_idle", "trashbag", "plant", "window", "cat", "bed"):
    IMG[n] = load(f"{n}.png")

def hexrgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
def sh(c, a): return tuple(max(0, min(255, v + a)) for v in c)

def wood_floor(d, y0, y1, base):
    """가로 마루널 + 결 + 엇갈린 세로 이음새."""
    rnd = random.Random(7)
    plank_h = 11
    row = 0
    for py in range(y0, y1, plank_h):
        tone = sh(base, rnd.randint(-10, 8))
        d.rectangle((0, py, VW, min(py + plank_h - 1, y1)), fill=tone + (255,))
        # 결(은은한 가로 줄)
        for gy in range(py + 2, py + plank_h - 1, 3):
            d.line((0, gy, VW, gy), fill=sh(tone, -6) + (90,))
        # 널 사이 어두운 이음새
        d.line((0, py, VW, py), fill=sh(base, -34) + (200,))
        d.line((0, py + 1, VW, py + 1), fill=sh(base, 14) + (70,))
        # 세로 이음새(엇갈리게)
        off = 0 if row % 2 == 0 else 36
        for vx in range(off, VW + 72, 72):
            d.line((vx, py, vx, py + plank_h - 1), fill=sh(base, -30) + (150,))
        row += 1

def render():
    with open(os.path.join(ROOT, "stages", "stages.json"), encoding="utf-8") as f:
        st = json.load(f)[0]
    wall = hexrgb(st["wall"]); floor = (216, 176, 124)
    img = Image.new("RGBA", (VW, VH), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    WALL_H = 96

    # ---- 벽 ----
    d.rectangle((0, 0, VW, WALL_H), fill=wall + (255,))
    # 벽지 세로 스트라이프(은은)
    for x in range(0, VW, 12):
        d.line((x, 0, x, WALL_H - 12), fill=sh(wall, 8) + (90,))
    # 상단 몰딩(crown)
    d.rectangle((0, 0, VW, 5), fill=sh(wall, 18) + (255,))
    d.line((0, 6, VW, 6), fill=sh(wall, -22) + (200,))
    # 채어레일 몰딩
    rail = WALL_H - 26
    d.rectangle((0, rail, VW, rail + 3), fill=sh(wall, 20) + (255,))
    d.line((0, rail - 1, VW, rail - 1), fill=sh(wall, -18) + (160,))
    d.line((0, rail + 4, VW, rail + 4), fill=sh(wall, -24) + (160,))
    # 베이스보드(걸레받이)
    d.rectangle((0, WALL_H - 9, VW, WALL_H), fill=(245, 240, 233, 255))
    d.line((0, WALL_H - 9, VW, WALL_H - 9), fill=sh(wall, -30) + (200,))
    d.rectangle((0, WALL_H, VW, WALL_H + 2), fill=(150, 120, 90, 255))

    # 창문
    ww, wh = 72, 60
    wx, wy = (VW - ww) // 2, 12
    d.rectangle((wx - 3, wy - 3, wx + ww + 2, wy + wh + 2), fill=sh(wall, -20) + (255,))
    img.alpha_composite(IMG["window"].resize((ww, wh), Image.NEAREST), (wx, wy))

    # ---- 나무 마루 ----
    wood_floor(d, WALL_H + 2, VH, floor)

    # 따뜻한 빛(창에서)
    glow = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.polygon([(wx, wy + wh), (wx + ww, wy + wh), (wx + ww + 50, VH), (wx - 50, VH)],
               fill=(255, 244, 206, 40))
    img.alpha_composite(glow)

    # ---- 러그(보드 밑) ----
    cols, rows = 3, 3
    S = 4; tilePx = TILE * S
    boardX = (VW - cols * tilePx) // 2
    boardY = (VH - rows * tilePx) // 2 + 12
    pad = 14
    rx0, ry0 = boardX - pad, boardY - pad
    rx1, ry1 = boardX + cols * tilePx + pad, boardY + rows * tilePx + pad
    d.rounded_rectangle((rx0, ry0 + 4, rx1, ry1 + 4), 12, fill=(80, 60, 40, 50))
    d.rounded_rectangle((rx0, ry0, rx1, ry1), 12, fill=(228, 196, 196, 255))   # 러그 본체(연핑크)
    d.rounded_rectangle((rx0 + 4, ry0 + 4, rx1 - 4, ry1 - 4), 9, outline=(245, 226, 226, 255), width=2)
    d.rounded_rectangle((rx0 + 8, ry0 + 8, rx1 - 8, ry1 - 8), 7, fill=(250, 244, 238, 255))

    # ---- 타일(보드) ----
    pip = {3: (240, 214, 110), 2: (159, 182, 224)}
    for gy in range(rows):
        for gx in range(cols):
            v = st["grid"][gy][gx]
            if v == 0: continue
            t = IMG[f"tile{v}"].resize((tilePx, tilePx), Image.NEAREST)
            img.alpha_composite(t, (boardX + gx * tilePx, boardY + gy * tilePx))
            if (gx + gy) & 1:
                ov = Image.new("RGBA", (tilePx, tilePx), (60, 40, 30, 16))
                img.alpha_composite(ov, (boardX + gx * tilePx, boardY + gy * tilePx))

    # ---- 소품 ----
    bs = 2.6
    bed = IMG["bed"]; bw, bh = int(bed.width * bs), int(bed.height * bs)
    img.alpha_composite(bed.resize((bw, bh), Image.NEAREST), (2, VH - bh - 4))
    cs = 2.4
    cat = IMG["cat"]; cw, ch = int(cat.width * cs), int(cat.height * cs)
    img.alpha_composite(cat.resize((cw, ch), Image.NEAREST), (VW - cw - 4, VH - ch - 6))

    # ---- 히어로 ----
    hs = S
    hx, hy = 1, 1
    baseX = boardX + hx * tilePx + tilePx // 2
    footY = boardY + hy * tilePx + tilePx
    d.ellipse((baseX - tilePx * 0.32, footY - hs * 2 - tilePx * 0.13,
               baseX + tilePx * 0.32, footY - hs * 2 + tilePx * 0.13), fill=(0, 0, 0, 60))
    hero = IMG["hero_idle"].resize((16 * hs, 24 * hs), Image.NEAREST)
    img.alpha_composite(hero, (int(baseX - 16 * hs / 2), int(footY - 24 * hs + hs * 2)))

    out = os.path.join(os.path.dirname(__file__), "_cozy.png")
    big = img.resize((VW * 3, VH * 3), Image.NEAREST)
    big.save(out)
    print("cozy demo:", out)

if __name__ == "__main__":
    render()
