#!/usr/bin/env python3
"""
쓱싹퍼즐 픽셀아트 에셋 생성기.

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
    "X": (58, 44, 54, 255),    # 외곽선(밝은 배경용으로 살짝 부드럽게)
    "o": (74, 58, 70, 255),    # 부드러운 외곽선/그림자
    # 머리카락 — 금발 웨이브
    "h": (232, 196, 118, 255),
    "H": (248, 226, 168, 255),
    "d": (198, 158, 90, 255),  # 머리 진한부분
    # 피부
    "k": (250, 208, 166, 255),
    "K": (226, 172, 132, 255),
    "r": (244, 156, 134, 255), # 볼터치
    "e": (64, 96, 150, 255),   # 파란 눈
    "q": (242, 246, 250, 255), # 눈 하이라이트
    # 상의 — 네이비 유니폼 + 흰 카라
    "u": (80, 102, 158, 255),
    "U": (56, 74, 122, 255),
    "L": (238, 242, 248, 255), # 흰 카라
    # 바지 — 네이비
    "p": (58, 72, 116, 255),
    "P": (42, 52, 88, 255),
    # 신발 — 어두운
    "s": (78, 70, 90, 255),
    "S": (54, 48, 64, 255),
    # 손(피부)
    "n": (250, 208, 166, 255),
    # 밀대 자루
    "m": (176, 124, 70, 255),
    "M": (134, 92, 48, 255),
    # 밀대 솔
    "w": (228, 232, 240, 255),
    "W": (178, 186, 200, 255),
    # 고양이
    "c": (60, 54, 72, 255),    # 검은고양이 몸
    "C": (84, 76, 100, 255),   # 고양이 하이라이트
    "y": (240, 214, 110, 255), # 고양이 눈/마법 노랑
    "f": (250, 246, 238, 255), # 흰 포인트
    # 쓰레기봉투 — 부드러운 슬레이트(무겁지 않게)
    "g": (132, 138, 156, 255),
    "G": (164, 170, 186, 255),  # 비닐 하이라이트
    "t": (150, 140, 110, 255),  # 봉투 묶음끈
    # 소품 — 화분
    "a": (118, 176, 96, 255),  # 잎 진한
    "A": (156, 206, 122, 255), # 잎 밝은
    "b": (96, 68, 52, 255),    # 흙
    "z": (206, 124, 86, 255),  # 화분
    "Z": (170, 94, 62, 255),   # 화분 그늘
    # 소품 — 창문
    "F": (242, 244, 250, 255), # 창틀
    "v": (178, 214, 236, 255), # 유리
    "V": (212, 234, 250, 255), # 하늘
    # 가게/가구 공용 색
    "1": (232, 110, 110, 255), # 빨강
    "2": (126, 200, 130, 255), # 초록
    "3": (244, 188, 98, 255),  # 주황/노랑
    "4": (124, 178, 232, 255), # 하늘파랑
    "5": (246, 176, 200, 255), # 핑크
    "6": (210, 156, 100, 255), # 빵 밝은
    "7": (164, 108, 60, 255),  # 빵 진한
    "8": (210, 216, 224, 255), # 크롬/연회색
    "9": (96, 100, 114, 255),  # 진회색
    "i": (250, 250, 252, 255), # 밝은 흰
    "j": (248, 236, 214, 255), # 고양이 크림
    "J": (228, 210, 182, 255), # 고양이 그늘
    "l": (200, 160, 110, 255), # 밝은 우드
    "D": (150, 108, 66, 255),  # 진한 우드
    "N": (122, 82, 54, 255),   # 테이블 브라운
    "E": (238, 242, 248, 255), # 김/하양
    "B": (96, 60, 42, 255),    # 커피
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
    "....XdHHHHdX....",
    "...XdHHHHHHdX...",
    "..XdHHhhhhHHdX..",
    "..XHhkkkkkkhHX..",
    "..XHkkkkkkkkHX..",
    "..XHkeqkkqekHX..",  # 큰 파란 눈 + 하이라이트
    "..XHkeekkeekHX..",
    "..XHkkkkkkkkHX..",
    "..XHkrkkkkrkHX..",  # 볼터치
    "..XHhkkKKkkhHX..",  # 작은 입
    "..XdhkkkkkkhdX..",  # 웨이브 머리 끝 + 턱
    "...XdkkkkkkdX...",
    "....LLLLLLLL....",  # 흰 카라
    "...XuLLLLLLuX...",
    "..nXuuuuuuuuXn..",  # 손(양옆)
    "..XUuuuuuuuuUX..",
    "...XuuuuuuuuX...",
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
    base = (236, 214, 176)
    for y in range(16):
        for x in range(16):
            n = rnd.randint(-5, 5)
            # 아주 옅은 사선 결
            if (x + y) % 7 == 0:
                n -= 4
            px[x, y] = (max(0, min(255, base[0] + n)),
                        max(0, min(255, base[1] + n)),
                        max(0, min(255, base[2] + n)), 255)
    d = ImageDraw.Draw(img)
    # 베벨: 위/왼쪽 하이라이트, 아래/오른쪽 줄눈(그라우트)
    hi = (250, 234, 206, 150)
    lo = (198, 168, 132, 160)
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

PLANT = [
    "................",
    ".....aAa.aAa....",
    "....aAAAaAAAa...",
    "...aAAAAAAAAAa..",
    "...aAAAaAAAaAa..",
    "..aAAAAAAAAAAAa.",
    "...aAAAAAAAAAa..",
    "....aAAAAAAAa...",
    ".....aAAAAAa....",
    "......aAAAa.....",
    ".......aAa......",
    ".......XbX......",
    "......XzzzzX....",
    "......XzzzzX....",
    ".....XZzzzzZX...",
    ".....XZzzzzZX...",
    "......XZZZZX....",
    "................",
    "................",
    "................",
]

WINDOW = [
    "XXXXXXXXXXXXXXXX",
    "XFFFFFFFFFFFFFFX",
    "XFvvvvvFFvvvvvFX",
    "XFvvvvvFFvvvvvFX",
    "XFVVvvvFFvvvVVFX",
    "XFVVvvvFFvvvVVFX",
    "XFvvvvvFFvvvvvFX",
    "XFFFFFFFFFFFFFFX",
    "XFvvvvvFFvvvvvFX",
    "XFVVvvvFFvvvVVFX",
    "XFvvvvvFFvvvvvFX",
    "XFvvvvvFFvvvvvFX",
    "XFFFFFFFFFFFFFFX",
    "XXXXXXXXXXXXXXXX",
]


# ---------------------------------------------------------------------------
# 귀여운 고양이 친구(크림색, 앉은 자세) — 방 친구 NPC
# ---------------------------------------------------------------------------
CATCUTE = [
    "................",
    "...X......X.....",
    "..XjX....XjX....",
    "..X5jX..Xj5X....",
    "..XjjjjjjjjX....",
    ".XjjjjjjjjjjX...",
    ".XjejjjjjjejX...",  # 눈
    ".Xjjjjjjjjjj X..",
    ".Xjj5jEEj5jjX...",  # 코+볼
    ".XjjjjjjjjjjX...",
    ".XjjjjjjjjjjJ7..",  # 꼬리 시작
    "XjjjjjjjjjjjJ77.",
    "XjjjjjjjjjjjjJ7.",
    "XJjjjjjjjjjjjJ..",
    "XJJJ..JJ..JJJX..",  # 앞발
    ".XXX..XX..XXX...",
]

# ---------------------------------------------------------------------------
# 가게/집 가구 소품
# ---------------------------------------------------------------------------
FRIDGE = [  # 음료 냉장고 (편의점)
    "..XXXXXXXXXXX...",
    "..XiiiiiiiiiX...",
    "..Xi8888888iX...",
    "..XivvvvvvviX...",
    "..Xi11223344iX..",
    "..Xi11223344iX..",
    "..XivvvvvvviX...",
    "..Xi33441122iX..",
    "..Xi33441122iX..",
    "..XivvvvvvviX...",
    "..Xi22114433iX..",
    "..Xi22114433iX..",
    "..XiiiiiiiiiX...",
    "..X999999999X...",
    "..X9.......9X...",
    "..XXXXXXXXXXX...",
]

SHELF = [  # 진열대 (편의점/마트)
    "..XllllllllllX..",
    "..Xl11l22l33lX..",
    "..Xl11l22l33lX..",
    "..XDDDDDDDDDDX..",
    "..Xl44l55l11lX..",
    "..Xl44l55l11lX..",
    "..XDDDDDDDDDDX..",
    "..Xl22l33l44lX..",
    "..Xl22l33l44lX..",
    "..XDDDDDDDDDDX..",
    "..XD........DX..",
    "..XXXXXXXXXXXX..",
]

COFFEE = [  # 커피머신 (카페)
    "....EE..EE......",
    "...E..EE..E.....",
    "..XXXXXXXXXX....",
    "..X88888888X....",
    "..X8iiiiii8X....",
    "..X8i1111i8X....",
    "..X88888888X....",
    "..X8.XXXX.8X....",
    "..X8..BB..8X....",
    "..X8.iEEi.8X....",
    "..X8.iBBi.8X....",
    "..X88888888X....",
    "..XXXXXXXXXX....",
    "................",
]

BREADCASE = [  # 빵 진열장 (베이커리)
    "..XXXXXXXXXXX...",
    "..XiiiiiiiiiX...",
    "..XvvvvvvvvvX...",
    "..Xv66X77X6vX...",
    "..Xv667.76.vX...",
    "..XvvvvvvvvvX...",
    "..Xv7X66X77vX...",
    "..Xv.6677.6vX...",
    "..XiiiiiiiiiX...",
    "..XlllllllllX...",
    "..XDDDDDDDDDX...",
    "..XXXXXXXXXXX...",
]

TABLE = [  # 카페 테이블 + 컵
    "................",
    ".....EE.E.......",
    "....XiiiiX......",  # 컵
    "....XiBBiX......",
    "...XNNNNNNNNX...",  # 테이블 상판
    "..XNNNNNNNNNNX..",
    "..XlNNNNNNNNlX..",
    "...XXNN..NNXX...",
    ".....DD..DD.....",  # 다리
    ".....DD..DD.....",
    "................",
    "................",
]

BED = [  # 침대/쿠션 (집)
    "................",
    "..XXXXXXXXXXXX..",
    ".X5iiiii5iiii5X.",  # 베개
    ".X5iiiii5iiii5X.",
    ".XEEEEEEEEEEEEX.",
    ".X44444444444X..",  # 이불
    ".X44224422442X..",
    ".X44444444444X..",
    ".X42244224422X..",
    ".X44444444444X..",
    ".XDDDDDDDDDDDDX.",
    "..XXXXXXXXXXXX..",
]

PROPS = {
    "cat": CATCUTE, "fridge": FRIDGE, "shelf": SHELF, "coffee": COFFEE,
    "breadcase": BREADCASE, "table": TABLE, "bed": BED,
}


def export():
    os.makedirs(OUT, exist_ok=True)
    hero = build_hero()
    for k, v in hero.items():
        v.save(os.path.join(OUT, f"hero_{k}.png"))
    grid_to_img(TRASHBAG).save(os.path.join(OUT, "trashbag.png"))
    grid_to_img(PLANT).save(os.path.join(OUT, "plant.png"))
    grid_to_img(WINDOW).save(os.path.join(OUT, "window.png"))
    for name, grid in PROPS.items():
        grid_to_img(grid).save(os.path.join(OUT, f"{name}.png"))
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
