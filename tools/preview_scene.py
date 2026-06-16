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
IMG["window"] = load("window.png")
for _n in ("plant", "cat", "fridge", "shelf", "coffee", "breadcase", "table", "bed"):
    IMG[_n] = load(f"{_n}.png")

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
    # 스테이지별 소품(왼/오)
    sps = 2.3
    def place(name, left):
        im = IMG[name]
        w, h = int(im.width * sps), int(im.height * sps)
        x = 4 if left else VW - w - 4
        y = VH - h - 4
        gd2 = ImageDraw.Draw(img)
        gd2.ellipse((x + w / 2 - w * 0.42, y + h - 8, x + w / 2 + w * 0.42, y + h + 2), fill=(70, 50, 30, 40))
        img.alpha_composite(im.resize((w, h), Image.NEAREST), (x, y))
    pr = stage.get("props", ["plant", "cat"])
    if len(pr) > 0:
        place(pr[0], True)
    if len(pr) > 1:
        place(pr[1], False)

    # 보드 매트(크림 + 파스텔 테두리)
    pad = round(S * 3)
    bx, by = boardX - pad, boardY - pad
    bw, bh = cols * tilePx + pad * 2, rows * tilePx + pad * 2
    rrect(d, (bx, by + 5, bx + bw, by + 5 + bh), 10, (80, 60, 40, 36))
    rrect(d, (bx, by, bx + bw, by + bh), 10, shade(stage["wall"], -8) + (255,))
    rrect(d, (bx + 2, by + 2, bx + bw - 2, by + bh - 2), 8, (255, 250, 242, 255))

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
    # 8개 스테이지 전부 합성(4x2)
    sv = 2
    imgs = []
    for st in stages:
        hx, hy = st["start"]["x"], st["start"]["y"]
        imgs.append((st["theme"], render(st, 0.45, (hx, hy), scale_view=sv)))
    cols_n = 4
    gap = 14
    cellw = imgs[0][1].width
    cellh = imgs[0][1].height + 22
    rows_n = (len(imgs) + cols_n - 1) // cols_n
    W = gap + cols_n * (cellw + gap)
    H = gap + rows_n * (cellh + gap)
    m = Image.new("RGBA", (W, H), (236, 230, 238, 255))
    dd = ImageDraw.Draw(m)
    for idx, (name, im) in enumerate(imgs):
        cx = gap + (idx % cols_n) * (cellw + gap)
        cy = gap + (idx // cols_n) * (cellh + gap)
        m.alpha_composite(im, (cx, cy))
        dd.text((cx + 4, cy + im.height + 4), f"{idx+1}. {name}", fill=(60, 50, 60))
    out = os.path.join(os.path.dirname(__file__), "_scene.png")
    m.save(out)
    print("scene preview:", out)
