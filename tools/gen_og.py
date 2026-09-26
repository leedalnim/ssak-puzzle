#!/usr/bin/env python3
"""카카오톡·트위터 등에 링크를 붙였을 때 뜨는 공유 카드(og:image) 를 만든다.

og:image 가 없으면 공유 앱이 페이지 안의 이미지를 아무거나 집어간다(장바구니 에셋이
썸네일로 나오던 이유). 타이틀 아트에서 캐릭터·고양이를 잘라 오른쪽에 두고,
왼쪽에 로고와 한 줄 소개를 얹어 1200×630 카드를 만든다.

    python3 tools/gen_og.py        # → assets/share/og.png
"""
import io, os
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
OUT = 'assets/share/og.jpg'   # 공유 카드는 사진형이라 JPEG 가 훨씬 가볍다
TAGLINE = '무기력한 방 한 칸에서, 다시 세상 밖으로'
SUB = '한 붓 그리기로 방을 쓱— 싹—'


def load_font(weight, size):
    """게임과 같은 나눔스퀘어라운드를 쓴다(woff2 → ttf 로 메모리에서 변환)."""
    f = TTFont(f'assets/fonts/NanumSquareRound{weight}.woff2')
    f.flavor = None
    buf = io.BytesIO()
    f.save(buf)
    buf.seek(0)
    return ImageFont.truetype(buf, size)


def build():
    art = Image.open('assets/room/screens/title.webp').convert('RGB')
    logo = Image.open('assets/room/screens/logo.webp').convert('RGBA')

    # --- 오른쪽: 캐릭터+고양이 ---
    pw = 560
    cx, cy, ch = 550, 1010, 760                 # 타이틀 아트에서 인물이 있는 자리
    cw = int(ch * pw / H)
    panel = art.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)) \
               .resize((pw, H), Image.LANCZOS)

    # --- 왼쪽: 같은 방의 벽을 늘려 이어지게 ---
    card = Image.new('RGB', (W, H), (246, 236, 214))
    card.paste(art.crop((60, 200, 960, 560)).resize((W - pw + 40, H), Image.LANCZOS), (0, 0))
    card.paste(panel, (W - pw, 0))

    # 이음매를 그라데이션으로 섞어 자른 티가 안 나게
    blend = 70
    mask = Image.linear_gradient('L').rotate(-90, expand=True).resize((blend, H))
    card.paste(Image.composite(panel.crop((0, 0, blend, H)),
                               card.crop((W - pw - blend, 0, W - pw, H)), mask),
               (W - pw - blend, 0))

    # --- 로고 + 문구 ---
    lw = 450
    lg = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    lx, ly = 74, 176
    card.paste(lg, (lx, ly), lg)

    d = ImageDraw.Draw(card)
    y = ly + lg.height + 26
    d.text((lx + 14, y), TAGLINE, font=load_font('EB', 31), fill=(120, 88, 50))
    d.text((lx + 14, y + 46), SUB, font=load_font('B', 26), fill=(160, 130, 92))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    card.save(OUT, quality=90, optimize=True, progressive=True)
    print(f'{OUT} — {card.size[0]}x{card.size[1]}, {os.path.getsize(OUT) // 1024}KB')


if __name__ == '__main__':
    build()
