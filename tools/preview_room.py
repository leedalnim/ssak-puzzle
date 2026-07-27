#!/usr/bin/env python3
"""방 씬 미리보기 — 배경 + 원근 보드 + 타일/장애물/캐릭터 합성.

게임 렌더러(js/game.js)가 캔버스에서 할 일을 브라우저 없이 확인하기 위한 도구.
핵심 규칙 두 가지:
  1. 보드는 평면에서 통짜로 조립한 뒤 **한 번만** 원근 변형한다.
     (타일을 하나씩 변형하면 이음새가 어긋난다)
  2. 오브젝트는 변형하지 않는다. 셀 중심 좌표에 세우고 접지 그림자를 깐다.

    python3 tools/preview_room.py [출력경로]
"""
import sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BG   = "assets/concept/bg_studio_src.png"
OUT  = sys.argv[1] if len(sys.argv) > 1 else "tools/_room.png"
# 보드 사다리꼴 (배경 1024x1536 기준) — CONCEPT.md 6.6 참조
TOPW, BOTW, Y0, Y1 = 680, 760, 556, 1256


def _solve(dst, src):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float))


def homography(src, dst):
    return np.append(_solve(src, dst), 1).reshape(3, 3)


def build_board(grid, board_px=1400):
    """평면 보드 한 장(나무 프레임 + 타일 격자)을 만든다."""
    rows, cols = len(grid), len(grid[0])
    fr = int(board_px * 0.036)
    inner = board_px - fr * 2
    gap = max(2, int(inner * 0.006))
    cw = (inner - gap * (cols - 1)) // cols
    ch = (inner - gap * (rows - 1)) // rows
    bw = fr * 2 + cw * cols + gap * (cols - 1)
    bh = fr * 2 + ch * rows + gap * (rows - 1)

    b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    r = int(fr * 0.9)
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), r, fill=(226, 196, 148, 255))
    for i in range(fr):                                   # 나무 결 그라데이션
        t = i / fr
        d.rounded_rectangle((i, i, bw - 1 - i, bh - 1 - i), max(2, r - i),
                            outline=(int(240 - 32 * t), int(214 - 36 * t), int(170 - 36 * t), 255))
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), r, outline=(184, 148, 102, 255), width=4)
    sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))        # 안쪽 그림자
    ImageDraw.Draw(sh).rounded_rectangle((fr - 4, fr - 4, bw - fr + 3, bh - fr + 3), 12,
                                         outline=(118, 90, 56, 150), width=10)
    b.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))

    tiles = [Image.open(f"assets/room/tiles/tile_{i}.png").convert("RGBA") for i in range(6)]
    for y in range(rows):
        for x in range(cols):
            b.alpha_composite(tiles[grid[y][x]].resize((cw, ch), Image.LANCZOS),
                              (fr + x * (cw + gap), fr + y * (ch + gap)))
    return b, (fr, cw, ch, gap)


def render(grid, obstacles, hero, hero_dir="down"):
    bg = Image.open(BG).convert("RGBA")
    W, H = bg.size
    cx = W / 2
    dst = [(cx - TOPW / 2, Y0), (cx + TOPW / 2, Y0), (cx + BOTW / 2, Y1), (cx - BOTW / 2, Y1)]

    board, (fr, cw, ch, gap) = build_board(grid)
    bw, bh = board.size
    img = bg.copy()

    drop = Image.new("RGBA", (W, H), (0, 0, 0, 0))        # 보드 드롭섀도우
    ImageDraw.Draw(drop).polygon([(x, y + 16) for x, y in dst], fill=(96, 74, 52, 110))
    img.alpha_composite(drop.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(board.transform(
        (W, H), Image.PERSPECTIVE, _solve(dst, [(0, 0), (bw, 0), (bw, bh), (0, bh)]), Image.BICUBIC))

    hm = homography([(0, 0), (1, 0), (1, 1), (0, 1)], dst)

    def project(u, v):
        q = hm @ np.array([u, v, 1.0])
        return q[0] / q[2], q[1] / q[2]

    def cell_uv(c, r):
        return ((fr + c * (cw + gap)) / bw, (fr + r * (ch + gap)) / bh,
                (fr + c * (cw + gap) + cw) / bw, (fr + r * (ch + gap) + ch) / bh)

    def put(png, c, r, scale, anchor=0.55, shadow_w=0.72, shadow_a=125):
        o = Image.open(png).convert("RGBA")
        u0, v0, u1, v1 = cell_uv(c, r)
        cell_h = project((u0 + u1) / 2, v1)[1] - project((u0 + u1) / 2, v0)[1]
        s = cell_h * scale / o.height
        w, h = int(o.width * s), int(o.height * s)
        ox, oy = project((u0 + u1) / 2, (v0 + v1) / 2)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))      # 접지 그림자
        base = oy + h * (1 - anchor) * 0.72
        ImageDraw.Draw(sh).ellipse((ox - w * shadow_w / 2, base - cell_h * 0.10,
                                    ox + w * shadow_w / 2, base + cell_h * 0.10),
                                   fill=(84, 62, 42, shadow_a))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
        img.alpha_composite(o.resize((w, h), Image.LANCZOS), (int(ox - w / 2), int(oy - h * anchor)))

    for (c, r), name in obstacles.items():
        put(f"assets/room/obstacles/obs_{name}.png", c, r, 0.80)
    put(f"assets/room/char/char_{hero_dir}_0.png", *hero, 1.35, anchor=0.62,
        shadow_w=0.55, shadow_a=135)
    return img


if __name__ == "__main__":
    random.seed(11)
    cols = rows = 5
    grid = [[random.choice([0, 0, 1, 1, 2, 2, 3, 4, 5]) for _ in range(cols)] for _ in range(rows)]
    obstacles = {(3, 1): "boxes", (1, 3): "plant", (4, 3): "basket_rd"}
    for c, r in obstacles:
        grid[r][c] = 0
    render(grid, obstacles, hero=(1, 2)).convert("RGB").save(OUT)
    print("saved", OUT)
