#!/usr/bin/env python3
"""
슥삭퍼즐 픽셀아트 에셋 생성기.

손으로 그린 픽셀맵(문자 그리드)과 절차적 셰이딩을 합쳐
게임에서 바로 쓰는 PNG 스프라이트를 만든다.
PNG가 곧 에셋의 원본(single source) → 게임은 PNG만 로드.

사용:
  python3 tools/gen_assets.py          # assets/*.png 생성
  python3 tools/gen_assets.py preview  # tools/_preview.png 미리보기 합성본도 생성
"""
import sys, os, random, math
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
TOOLS = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# 팔레트 — 코지한 제한 팔레트. 따뜻한 톤 + 차분한 보조색.
# ---------------------------------------------------------------------------
PAL = {
    ".": None,                 # 투명
    "X": (38, 28, 44, 255),    # 진한 외곽선 (검정 대신 보라빛 다크)
    "o": (58, 46, 66, 255),    # 부드러운 외곽선/그림자
    # 머리카락
    "h": (94, 62, 52, 255),
    "H": (124, 86, 66, 255),
    "d": (66, 42, 38, 255),    # 머리 진한부분
    # 피부
    "k": (245, 200, 158, 255),
    "K": (214, 160, 120, 255),
    "r": (236, 150, 120, 255), # 볼터치
    "e": (54, 38, 46, 255),    # 눈
    # 후드(상의)
    "u": (92, 142, 138, 255),
    "U": (62, 104, 102, 255),
    "L": (126, 176, 170, 255),
    # 바지
    "p": (74, 88, 120, 255),
    "P": (52, 62, 92, 255),
    # 신발
    "s": (238, 232, 220, 255),
    "S": (196, 188, 174, 255),
    # 손(피부 같지만 구분용)
    "n": (245, 200, 158, 255),
    # 밀대 자루
    "m": (176, 124, 70, 255),
    "M": (134, 92, 48, 255),
    # 밀대 솔
    "w": (224, 230, 238, 255),
    "W": (170, 182, 196, 255),
    # 고양이
    "c": (60, 54, 72, 255),    # 검은고양이 몸
    "C": (84, 76, 100, 255),   # 고양이 하이라이트
    "y": (240, 214, 110, 255), # 고양이 눈/마법 노랑
    "f": (250, 246, 238, 255), # 흰 포인트
    # 쓰레기봉투
    "g": (70, 74, 86, 255),
    "G": (92, 98, 112, 255),   # 비닐 하이라이트
    "t": (120, 110, 80, 255),  # 봉투 묶음끈
}

def grid_to_img(rows, pal=PAL):
    h = len(rows); w = max(len(r) for r in rows)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            col = pal.get(ch)
            if col:
                px[x, y] = col
    return img

# ---------------------------------------------------------------------------
# 주인공 — 밀대 걸레를 든 청년. 16x24, 정면.
# 밀대는 캐릭터 오른쪽(뷰어 기준 왼쪽 col1~2)에 세로로.
# ---------------------------------------------------------------------------
HERO_IDLE = [
    "................",
    ".....XXXXXX.....",
    "....XdhhhhdX....",
    "...XdhhhhhhdX...",
    "...XhHHHHHHhX...",
    "...XhkkkkkkhX...",
    "...XhkkkkkkhX...",
    "...XhkekkekhX...",  # 눈
    "...XhkrkkrkhX...",  # 볼터치
    "...XhkkookkhX...",  # 작은 입
    "....XKkkkkKX....",
    "....XKkkkkKX....",
    ".....XnnnnX.....",  # 목
    "...XuuuuuuuuX...",
    "..XuLLuuuuLLuX..",
    "..XuLuuuuuuLuX..",
    "..nXuuuuuuuuXn..",  # 손(양옆)
    "..XUuuuuuuuuUX..",
    "...XppppppppX...",
    "...XpPPPPPPpX...",
    "...Xpp....ppX...",
    "...Xpp....ppX...",
    "..XssX..XssX....",
    "..XSSX..XSSX....",
]

# 걷기 프레임 A/B: 다리만 살짝 어긋나게
HERO_WALK_A = HERO_IDLE[:20] + [
    "...Xpp....ppX...",
    "..Xpp......ppX..",
    ".XssX......XssX.",
    ".XSSX......XSSX.",
]
HERO_WALK_B = HERO_IDLE[:18] + [
    "...XppppppppX...",
    "...XpPPPPPPpX...",
    "...XppppppppX...",
    "...Xpp....ppX...",
    "...XssX.XssX....",
    "...XSSX.XSSX....",
]

def draw_mop(img):
    """밀대 걸레를 캐릭터 오른쪽에 얹는다 (자루 + 솔)."""
    d = ImageDraw.Draw(img)
    # 자루: col2,row5 ~ col2,row20 사선 살짝
    for i, y in enumerate(range(5, 21)):
        x = 2 - (1 if y > 15 else 0)
        d.point((x, y), fill=PAL["m"])
        d.point((x, y + 0), fill=PAL["m"])
    d.line((2, 5, 2, 16), fill=PAL["m"])
    d.line((1, 16, 1, 20), fill=PAL["M"])
    # 솔(바닥): 1~3 col, 21~23 row
    d.rectangle((0, 20, 3, 22), fill=PAL["w"])
    d.point((0, 22), fill=PAL["W"]); d.point((3, 22), fill=PAL["W"])
    d.line((0, 23, 3, 23), fill=PAL["W"])
    return img

def build_hero():
    frames = {}
    for name, rows in [("idle", HERO_IDLE), ("walk_a", HERO_WALK_A), ("walk_b", HERO_WALK_B)]:
        # 입 자리 'm'은 임시였으니 외곽 다크로 치환
        rows = [r.replace("m", "o") for r in rows]
        img = grid_to_img(rows)
        img = draw_mop(img)
        frames[name] = img
    return frames

# ---------------------------------------------------------------------------
# 고양이 마법사 — 작은 검은 고양이 + 마법 노랑 눈/모자
# ---------------------------------------------------------------------------
CAT = [
    "................",
    ".......yy.......",
    "......yyyy......",
    ".....yyyyyy.....",
    "....XXXXXXXX....",  # 마법사 모자 챙
    "...XcccccccX....",
    "..XccccccccccX..",
    "..XcCcccccCcX...",  # 귀 사이
    ".XccccccccccccX.",
    ".XcyccccccccyX..",  # 눈
    ".XccccffccccX...",  # 코 흰점
    ".XccccccccccX...",
    "..XccccccccX....",
    "..Xcc.cc.ccX....",
    "...f....f.f.....",  # 발
    "................",
]

# ---------------------------------------------------------------------------
# 타일 — 절차적 그라임. 16x16. 내구도별(clean/d1/d2/d3).
# ---------------------------------------------------------------------------
def floor_base(seed):
    """정사각 바닥 타일 — 살짝 베벨 + 미세 노이즈로 '바닥'처럼."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    base = (214, 190, 158)
    for y in range(16):
        for x in range(16):
            n = rnd.randint(-6, 6)
            # 아주 옅은 사선 결
            if (x + y) % 7 == 0:
                n -= 5
            px[x, y] = (max(0, min(255, base[0] + n)),
                        max(0, min(255, base[1] + n)),
                        max(0, min(255, base[2] + n)), 255)
    d = ImageDraw.Draw(img)
    # 베벨: 위/왼쪽 하이라이트, 아래/오른쪽 줄눈(그라우트)
    hi = (232, 212, 184, 150)
    lo = (168, 142, 112, 170)
    d.line((0, 0, 15, 0), fill=hi)
    d.line((0, 0, 0, 15), fill=hi)
    d.line((0, 15, 15, 15), fill=lo)
    d.line((15, 0, 15, 15), fill=lo)
    return img

GRIME = {  # 내구도 -> (틴트, 점밀도, 알파)
    1: ((188, 180, 150), 16, 60),    # 옅은 먼지(밝은 회색, 거의 깨끗)
    2: ((118, 126, 158), 50, 140),   # 중간(푸른 때)
    3: ((86, 68, 52), 95, 205),      # 두꺼운 찌든때(짙은 갈색 슬러지)
}

def make_tile(durability, seed=0):
    img = floor_base(seed)
    if durability == 0:
        # 깨끗 — 살짝 밝게 + 반짝임
        glow = Image.new("RGBA", (16, 16), (255, 250, 235, 34))
        img = Image.alpha_composite(img, glow)
        d = ImageDraw.Draw(img)
        # 작은 반짝이 (+ 모양)
        for (sx, sy) in ((4, 4), (11, 9)):
            d.point((sx, sy), fill=(255, 255, 255, 230))
            d.point((sx - 1, sy), fill=(255, 255, 255, 110))
            d.point((sx + 1, sy), fill=(255, 255, 255, 110))
            d.point((sx, sy - 1), fill=(255, 255, 255, 110))
            d.point((sx, sy + 1), fill=(255, 255, 255, 110))
        return img
    tint, dens, alpha = GRIME[durability]
    rnd = random.Random(seed * 7 + durability)
    overlay = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = overlay.load()
    for _ in range(dens):
        x = rnd.randint(0, 15); y = rnd.randint(0, 15)
        a = alpha + rnd.randint(-30, 30)
        px[x, y] = (tint[0], tint[1], tint[2], max(0, min(255, a)))
        # 덩어리감
        if rnd.random() < 0.4 and x < 15:
            px[x + 1, y] = (tint[0], tint[1], tint[2], max(0, min(255, a - 30)))
    img = Image.alpha_composite(img, overlay)
    return img

# ---------------------------------------------------------------------------
# 집 스테이지 장식물(쓰레기) — 벽/경계용
# ---------------------------------------------------------------------------
TRASHBAG = [
    "................",
    "................",
    "......Xtt X.....",
    ".....XttttX.....",  # 묶은 끈
    "....XXggggXX....",
    "...XgGgggggXX...",
    "..XgGggggggggX..",
    "..XgGgggggggGX..",
    "..XggggggggggX..",
    "..XgggggggggGX..",
    "..XGgggggggggX..",
    "..XgggggggggGX..",
    "...XggggggggX...",
    "....XXXXXXXX....",
    "................",
    "................",
]

def export():
    os.makedirs(OUT, exist_ok=True)
    hero = build_hero()
    for k, v in hero.items():
        v.save(os.path.join(OUT, f"hero_{k}.png"))
    grid_to_img(CAT).save(os.path.join(OUT, "cat.png"))
    grid_to_img(TRASHBAG).save(os.path.join(OUT, "trashbag.png"))
    for dur in (0, 1, 2, 3):
        make_tile(dur, seed=dur + 1).save(os.path.join(OUT, f"tile_{dur}.png"))
    print("assets written to", os.path.abspath(OUT))

def preview():
    scale = 10
    cells = []
    hero = build_hero()
    for k in ("idle", "walk_a", "walk_b"):
        cells.append(("hero_" + k, hero[k]))
    cells.append(("cat", grid_to_img(CAT)))
    cells.append(("trash", grid_to_img(TRASHBAG)))
    for dur in (3, 2, 1, 0):
        cells.append((f"tile{dur}", make_tile(dur, seed=dur + 1)))
    # 타일 보드 샘플
    board = Image.new("RGBA", (16 * 5, 16 * 5), (0, 0, 0, 0))
    sample = [[3, 1, 2, 1, 3], [1, 0, 1, 0, 1], [2, 1, 3, 1, 2], [1, 0, 1, 0, 1], [3, 1, 2, 1, 3]]
    for gy in range(5):
        for gx in range(5):
            board.alpha_composite(make_tile(sample[gy][gx], seed=gx * 9 + gy), (gx * 16, gy * 16))
    cells.append(("board", board))

    pad = 12
    cw = 16 * scale
    montage_w = pad + len(cells) * (cw + pad)
    montage_h = pad + 24 * scale + 80
    m = Image.new("RGBA", (montage_w, montage_h), (40, 36, 48, 255))
    d = ImageDraw.Draw(m)
    x = pad
    for name, img in cells:
        big = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
        m.alpha_composite(big, (x, pad))
        d.text((x, pad + 24 * scale + 8), name, fill=(230, 230, 230, 255))
        x += big.width + pad
    out = os.path.join(TOOLS, "_preview.png")
    m.save(out)
    print("preview written:", out)

if __name__ == "__main__":
    export()
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        preview()
