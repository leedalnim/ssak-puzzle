#!/usr/bin/env python3
"""소프트 일러스트(벡터) 스타일 시안 — 픽셀 버리고 파스텔 코지룸 톤.
PIL 슈퍼샘플링(x3 후 축소)으로 매끈한 외곽선/곡선. 게임에선 Canvas 벡터로 이식 가능."""
import os, math
from PIL import Image, ImageDraw, ImageFilter

SS = 3                      # 슈퍼샘플 배율
W, H = 480, 854             # 최종 캔버스(9:16 근사)
CW, CH = W * SS, H * SS

# ---- 파스텔 팔레트 (레퍼런스 #8 톤) ----
C = dict(
    wall=(247, 230, 226), wall2=(238, 214, 209),
    floor=(236, 206, 160), floor2=(225, 190, 138),
    ink=(120, 92, 72),           # 따뜻한 갈색 외곽선
    white=(252, 246, 238), whiteS=(232, 222, 210),
    pink=(243, 201, 196), pinkD=(231, 174, 168),
    sage=(186, 213, 162), sageD=(150, 186, 122),
    pot=(206, 138, 96), potD=(176, 108, 72),
    blue=(200, 220, 238), blueD=(150, 186, 220),
    skin=(248, 211, 174), skinS=(232, 184, 142),
    hair=(242, 206, 130), hairD=(214, 170, 92), hairL=(250, 228, 174),
    navy=(86, 110, 168), navyD=(64, 84, 134),
    catC=(247, 236, 216), catS=(228, 212, 186),
    eye=(74, 92, 120), blush=(244, 170, 158),
    tileClean=(244, 224, 186), tileDirt=(196, 170, 126), tileDirt2=(176, 148, 104),
    rug=(240, 214, 210), rugIn=(250, 242, 236), rugLine=(228, 190, 184),
)

def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def shadow_layer():
    return Image.new("RGBA", (CW, CH), (0,0,0,0))

def soft_shadow(img, cx, cy, rw, rh, alpha=60):
    lay = Image.new("RGBA", (CW, CH), (0,0,0,0))
    d = ImageDraw.Draw(lay)
    d.ellipse((cx-rw, cy-rh, cx+rw, cy+rh), fill=(70,54,44,alpha))
    lay = lay.filter(ImageFilter.GaussianBlur(6*SS))
    img.alpha_composite(lay)

def rr(d, box, r, fill=None, outline=None, w=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)

def ellipse(d, cx, cy, rx, ry, fill=None, outline=None, w=0):
    d.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), fill=fill, outline=outline, width=w)

INK_W = 2*SS  # 외곽선 두께

def draw_window(img, d, cx, top):
    w, h = 120*SS, 96*SS
    x0, y0 = cx-w//2, top
    rr(d, (x0, y0, x0+w, y0+h), 12*SS, fill=C['white'], outline=C['ink'], w=INK_W)
    # 하늘 유리
    inset = 10*SS
    rr(d, (x0+inset, y0+inset, x0+w-inset, y0+h-inset), 8*SS, fill=C['blue'])
    # 살(창틀 십자)
    d.line((cx, y0+inset, cx, y0+h-inset), fill=C['white'], width=6*SS)
    d.line((x0+inset, y0+h//2, x0+w-inset, y0+h//2), fill=C['white'], width=6*SS)
    # 커튼 살짝
    rr(d, (x0-6*SS, y0-4*SS, x0+22*SS, y0+h+4*SS), 8*SS, fill=C['pink'], outline=C['ink'], w=INK_W)
    rr(d, (x0+w-22*SS, y0-4*SS, x0+w+6*SS, y0+h+4*SS), 8*SS, fill=C['pink'], outline=C['ink'], w=INK_W)

def draw_plant(img, d, cx, base):
    soft_shadow(img, cx, base+6*SS, 28*SS, 9*SS)
    # 화분
    rr(d, (cx-22*SS, base-26*SS, cx+22*SS, base+10*SS), 8*SS, fill=C['pot'], outline=C['ink'], w=INK_W)
    d.line((cx-22*SS, base-14*SS, cx+22*SS, base-14*SS), fill=C['potD'], width=3*SS)
    # 잎 뭉치(둥근 원들)
    for (dx,dy,r,col) in [(-18,-52,20,C['sageD']),(16,-50,20,C['sageD']),
                          (0,-68,24,C['sage']),(-22,-40,16,C['sage']),(22,-42,16,C['sageD'])]:
        ellipse(d, cx+dx*SS, base+dy*SS, r*SS, r*SS, fill=col, outline=C['ink'], w=INK_W)
    ellipse(d, cx, base-66*SS, 22*SS, 22*SS, fill=C['sage'])

def draw_bed(img, d, cx, cy):
    w, h = 150*SS, 96*SS
    x0, y0 = cx-w//2, cy-h//2
    soft_shadow(img, cx, y0+h, w//2-6*SS, 12*SS)
    rr(d, (x0, y0, x0+w, y0+h), 16*SS, fill=C['white'], outline=C['ink'], w=INK_W)
    # 이불
    rr(d, (x0, y0+34*SS, x0+w, y0+h), 16*SS, fill=C['blue'], outline=C['ink'], w=INK_W)
    rr(d, (x0+8*SS, y0+40*SS, x0+w-8*SS, y0+h-8*SS), 10*SS, fill=C['blueD'])
    # 베개 2개
    rr(d, (x0+12*SS, y0+10*SS, x0+w//2-6*SS, y0+34*SS), 10*SS, fill=C['pink'], outline=C['ink'], w=INK_W)
    rr(d, (x0+w//2+6*SS, y0+10*SS, x0+w-12*SS, y0+34*SS), 10*SS, fill=C['white'], outline=C['ink'], w=INK_W)

def draw_cat(img, d, cx, base):
    soft_shadow(img, cx, base+4*SS, 26*SS, 8*SS)
    body = C['catC']
    # 몸
    ellipse(d, cx, base-18*SS, 26*SS, 24*SS, fill=body, outline=C['ink'], w=INK_W)
    # 머리
    ellipse(d, cx, base-44*SS, 22*SS, 20*SS, fill=body, outline=C['ink'], w=INK_W)
    # 귀
    d.polygon([(cx-20*SS, base-56*SS),(cx-8*SS, base-44*SS),(cx-22*SS, base-40*SS)], fill=body, outline=C['ink'])
    d.polygon([(cx+20*SS, base-56*SS),(cx+8*SS, base-44*SS),(cx+22*SS, base-40*SS)], fill=body, outline=C['ink'])
    # 눈/볼/코
    ellipse(d, cx-8*SS, base-46*SS, 2*SS, 3*SS, fill=C['eye'])
    ellipse(d, cx+8*SS, base-46*SS, 2*SS, 3*SS, fill=C['eye'])
    ellipse(d, cx-12*SS, base-40*SS, 4*SS, 3*SS, fill=C['blush'])
    ellipse(d, cx+12*SS, base-40*SS, 4*SS, 3*SS, fill=C['blush'])
    d.polygon([(cx-3*SS, base-41*SS),(cx+3*SS, base-41*SS),(cx, base-38*SS)], fill=C['pinkD'])
    # 꼬리
    d.arc((cx+12*SS, base-26*SS, cx+44*SS, base+6*SS), 270, 90, fill=C['ink'], width=INK_W)

def draw_rug(d, cx, cy, rw, rh):
    ellipse(d, cx, cy, rw, rh, fill=C['rug'], outline=C['rugLine'], w=3*SS)
    ellipse(d, cx, cy, rw-10*SS, rh-10*SS, fill=C['rugIn'], outline=C['rugLine'], w=2*SS)

def draw_grid(img, d, cx, cy, cols, rows, cell, dirt):
    gw, gh = cols*cell, rows*cell
    x0, y0 = cx-gw//2, cy-gh//2
    for r in range(rows):
        for c in range(cols):
            x, y = x0+c*cell, y0+r*cell
            v = dirt[r][c]
            col = C['tileClean'] if v==0 else (C['tileDirt'] if v==1 else C['tileDirt2'])
            rr(d, (x+2*SS, y+2*SS, x+cell-2*SS, y+cell-2*SS), 7*SS, fill=col,
               outline=C['ink'], w=2*SS)
            if v>=1:
                # 얼룩 느낌(부드러운 점들)
                for (dx,dy) in [(0.3,0.4),(0.6,0.65),(0.45,0.25)]:
                    ellipse(d, x+cell*dx, y+cell*dy, cell*0.13, cell*0.1, fill=lerp(col,C['ink'],0.18))
            if v>=2:
                ellipse(d, x+cell*0.7, y+cell*0.5, cell*0.12, cell*0.1, fill=lerp(col,C['ink'],0.25))

def draw_character(img, d, cx, base, s=1.0):
    u = lambda v: int(v*SS*s)
    soft_shadow(img, cx, base+u(2), u(26), u(9))
    # 다리
    rr(d, (cx-u(16), base-u(20), cx-u(3), base), u(6), fill=C['navy'], outline=C['ink'], w=INK_W)
    rr(d, (cx+u(3), base-u(20), cx+u(16), base), u(6), fill=C['navy'], outline=C['ink'], w=INK_W)
    # 몸(유니폼)
    rr(d, (cx-u(24), base-u(60), cx+u(24), base-u(14)), u(16), fill=C['navy'], outline=C['ink'], w=INK_W)
    # 카라(흰)
    d.polygon([(cx-u(10),base-u(60)),(cx+u(10),base-u(60)),(cx,base-u(48))], fill=C['white'], outline=C['ink'])
    # 팔
    rr(d, (cx-u(30), base-u(54), cx-u(16), base-u(24)), u(7), fill=C['navy'], outline=C['ink'], w=INK_W)
    rr(d, (cx+u(16), base-u(54), cx+u(30), base-u(24)), u(7), fill=C['navy'], outline=C['ink'], w=INK_W)
    # 손
    ellipse(d, cx-u(30), base-u(24), u(7), u(7), fill=C['skin'], outline=C['ink'], w=INK_W)
    ellipse(d, cx+u(30), base-u(24), u(7), u(7), fill=C['skin'], outline=C['ink'], w=INK_W)
    # 밀대 (대각선 자루 + 솔)
    d.line((cx+u(30), base-u(24), cx+u(54), base+u(8)), fill=C['potD'], width=u(5))
    rr(d, (cx+u(44), base+u(6), cx+u(66), base+u(20)), u(6), fill=C['whiteS'], outline=C['ink'], w=INK_W)
    # 머리(둥근 금발)
    ellipse(d, cx, base-u(82), u(30), u(30), fill=C['hair'], outline=C['ink'], w=INK_W)   # 헤어 베이스
    # 얼굴
    ellipse(d, cx, base-u(78), u(20), u(21), fill=C['skin'], outline=C['ink'], w=INK_W)
    # 앞머리
    d.pieslice((cx-u(22), base-u(104), cx+u(22), base-u(64)), 180, 360, fill=C['hair'], outline=C['ink'], width=INK_W)
    ellipse(d, cx-u(26), base-u(74), u(10), u(20), fill=C['hair'], outline=C['ink'], w=INK_W)  # 옆머리
    ellipse(d, cx+u(26), base-u(74), u(10), u(20), fill=C['hair'], outline=C['ink'], w=INK_W)
    # 눈/볼/입
    ellipse(d, cx-u(8), base-u(76), u(3.0), u(4.0), fill=C['eye'])
    ellipse(d, cx+u(8), base-u(76), u(3.0), u(4.0), fill=C['eye'])
    ellipse(d, cx-u(7.2), base-u(77.5), u(1.1), u(1.4), fill=C['white'])
    ellipse(d, cx+u(8.8), base-u(77.5), u(1.1), u(1.4), fill=C['white'])
    ellipse(d, cx-u(13), base-u(70), u(4), u(3), fill=C['blush'])
    ellipse(d, cx+u(13), base-u(70), u(4), u(3), fill=C['blush'])
    d.arc((cx-u(4), base-u(72), cx+u(4), base-u(67)), 20, 160, fill=C['ink'], width=int(1.6*SS))

def render():
    img = Image.new("RGBA", (CW, CH), (0,0,0,0))
    d = ImageDraw.Draw(img)
    WALL_H = 250*SS
    # 벽 (위→아래 옅은 그라데이션)
    for y in range(WALL_H):
        t = y/WALL_H
        d.line((0,y,CW,y), fill=lerp(C['wall'], C['wall2'], t*0.5))
    # 바닥
    for y in range(WALL_H, CH):
        t = (y-WALL_H)/(CH-WALL_H)
        d.line((0,y,CW,y), fill=lerp(C['floor'], C['floor2'], t))
    # 바닥 마루 라인(부드럽게)
    for x in range(0, CW, 80*SS):
        d.line((x, WALL_H, x, CH), fill=(*C['floor2'], ), width=2*SS)
    # 베이스보드
    d.rectangle((0, WALL_H-10*SS, CW, WALL_H), fill=C['white'])
    d.line((0, WALL_H-10*SS, CW, WALL_H-10*SS), fill=C['ink'], width=INK_W)
    d.line((0, WALL_H, CW, WALL_H), fill=lerp(C['floor2'],C['ink'],0.3), width=2*SS)

    draw_window(img, d, CW//2, 40*SS)
    # 창에서 들어오는 햇살(부드럽게)
    sun = Image.new("RGBA", (CW, CH), (0,0,0,0))
    sd = ImageDraw.Draw(sun)
    sd.polygon([(CW//2-70*SS, 140*SS),(CW//2+70*SS,140*SS),(CW//2+150*SS,CH),(CW//2-150*SS,CH)], fill=(255,244,206,46))
    sun = sun.filter(ImageFilter.GaussianBlur(10*SS))
    img.alpha_composite(sun)

    # 가구
    draw_bed(img, d, 120*SS, 360*SS)
    draw_plant(img, d, 410*SS, 360*SS)
    draw_cat(img, d, 405*SS, 560*SS)

    # 러그 + 청소 그리드
    cx, cy = CW//2, 540*SS
    draw_rug(d, cx, cy, 150*SS, 150*SS)
    dirt = [[0,1,1],[1,2,1],[1,1,0]]
    draw_grid(img, d, cx, cy, 3, 3, 78*SS, dirt)

    # 캐릭터
    draw_character(img, d, cx-40*SS, cy-6*SS, s=1.0)

    out = img.convert("RGB").resize((W, H), Image.LANCZOS)
    p = os.path.join(os.path.dirname(__file__), "_vector.png")
    out.save(p); print("vector mockup:", p)

if __name__ == "__main__":
    render()
