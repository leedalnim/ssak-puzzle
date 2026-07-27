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


def _contact_shadow(img, cx, base_y, obj_w, cell_h, alpha=150):
    """접지 그림자 — 오브젝트 바로 밑에 좁고 진한 코어 + 넓고 옅은 확산.
    코어를 base_y보다 살짝 위(밑면과 겹치게)에 둬야 '붙어' 보인다.
    (코어 없이 넓은 타원만 깔면 오브젝트가 둥둥 떠 보임)"""
    cx, base_y, obj_w, cell_h = (float(v) for v in (cx, base_y, obj_w, cell_h))
    W, H = img.size
    # 넓고 옅은 확산
    far = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(far).ellipse((cx - obj_w * 0.46, base_y - cell_h * 0.10,
                                 cx + obj_w * 0.46, base_y + cell_h * 0.13),
                                fill=(84, 62, 42, int(alpha * 0.45)))
    img.alpha_composite(far.filter(ImageFilter.GaussianBlur(cell_h * 0.10)))
    # 좁고 진한 코어 — 밑면과 겹치도록 위로 올림
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse((cx - obj_w * 0.30, base_y - cell_h * 0.085,
                                  cx + obj_w * 0.30, base_y + cell_h * 0.045),
                                 fill=(62, 44, 28, alpha))
    img.alpha_composite(core.filter(ImageFilter.GaussianBlur(cell_h * 0.030)))


def build_board(grid, board_px=1400):
    """평면 보드 한 장(나무 프레임 + 타일 격자)을 만든다."""
    rows, cols = len(grid), len(grid[0])
    fr = int(board_px * 0.040)
    inner = board_px - fr * 2
    gap = max(1, int(inner * 0.0028))          # 갭 축소 → 타일이 붙어 보이게
    cw = (inner - gap * (cols - 1)) // cols
    ch = (inner - gap * (rows - 1)) // rows
    bw = fr * 2 + cw * cols + gap * (cols - 1)
    bh = fr * 2 + ch * rows + gap * (rows - 1)

    b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    r = int(fr * 0.85)
    # 우드 트레이 — 목업의 따뜻한 미디엄 오크
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), r, fill=(198, 154, 100, 255))
    for gy in range(4, bh - 4, max(7, fr // 5)):          # 나무 결
        d.line((4, gy, bw - 5, gy), fill=(176, 132, 82, 90))
    # 바깥쪽 밝은 베벨 → 안쪽으로 갈수록 어둡게 (입체감)
    for i in range(fr):
        t = i / fr
        d.rounded_rectangle((i, i, bw - 1 - i, bh - 1 - i), max(2, r - i),
                            outline=(int(226 - 66 * t), int(190 - 68 * t), int(138 - 60 * t), 190))
    d.rounded_rectangle((2, 2, bw - 3, bh - 3), r, outline=(240, 214, 172, 200), width=4)  # 상단 하이라이트
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), r, outline=(138, 100, 60, 255), width=5)   # 외곽선

    sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))        # 안쪽 그림자(AO)
    ImageDraw.Draw(sh).rounded_rectangle((fr - 5, fr - 5, bw - fr + 4, bh - fr + 4), 14,
                                         outline=(96, 68, 40, 195), width=15)
    b.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))

    tiles = [Image.open(f"assets/room/tiles/tile_{i}.png").convert("RGBA") for i in range(6)]
    for y in range(rows):
        for x in range(cols):
            px, py = fr + x * (cw + gap), fr + y * (ch + gap)
            cell = tiles[grid[y][x]].resize((cw, ch), Image.LANCZOS)
            # 타일 접지 AO — 아래쪽에 얇은 그늘
            ao = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            ImageDraw.Draw(ao).rounded_rectangle((2, int(ch * 0.70), cw - 3, ch - 2),
                                                 int(cw * 0.10), fill=(120, 94, 62, 46))
            cell.alpha_composite(ao.filter(ImageFilter.GaussianBlur(cw * 0.05)))
            b.alpha_composite(cell, (px, py))
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
    dd = ImageDraw.Draw(drop)
    for off, a in ((26, 70), (16, 80), (8, 70)):
        dd.polygon([(x, y + off) for x, y in dst], fill=(88, 66, 44, a))
    img.alpha_composite(drop.filter(ImageFilter.GaussianBlur(22)))
    img.alpha_composite(board.transform(
        (W, H), Image.PERSPECTIVE, _solve(dst, [(0, 0), (bw, 0), (bw, bh), (0, bh)]), Image.BICUBIC))

    hm = homography([(0, 0), (1, 0), (1, 1), (0, 1)], dst)

    def project(u, v):
        q = hm @ np.array([u, v, 1.0])
        return q[0] / q[2], q[1] / q[2]

    def cell_uv(c, r):
        return ((fr + c * (cw + gap)) / bw, (fr + r * (ch + gap)) / bh,
                (fr + c * (cw + gap) + cw) / bw, (fr + r * (ch + gap) + ch) / bh)

    def put(png, c, r, scale, base_off=0.18, shadow_w=0.66, shadow_a=130):
        """오브젝트는 **밑면**을 셀 중앙에 놓고 위로 세운다.
        (바운딩박스 중앙 정렬이면 공중에 뜬 것처럼 보임)"""
        o = Image.open(png).convert("RGBA")
        u0, v0, u1, v1 = cell_uv(c, r)
        cell_h = float(project((u0 + u1) / 2, v1)[1] - project((u0 + u1) / 2, v0)[1])
        s = cell_h * scale / o.height
        w, h = int(o.width * s), int(o.height * s)
        ox, oy = (float(v) for v in project((u0 + u1) / 2, (v0 + v1) / 2))
        base_y = oy + cell_h * base_off          # 접지선 = 셀 중앙보다 살짝 아래
        _contact_shadow(img, ox, base_y, w * shadow_w, cell_h, shadow_a)
        img.alpha_composite(o.resize((w, h), Image.LANCZOS), (int(ox - w / 2), int(base_y - h)))

    for (c, r), name in obstacles.items():
        put(f"assets/room/obstacles/obs_{name}.png", c, r, 1.05)
    put(f"assets/room/char/char_{hero_dir}_0.png", *hero, 1.85,
        base_off=0.16, shadow_w=0.42, shadow_a=140)
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
