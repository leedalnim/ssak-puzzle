#!/usr/bin/env python3
"""수집품 표시 배율 계산 — 칸마다 '보이는 면적'이 같아지도록.

긴 변만 칸에 맞추면 납작한 물건(머그컵·티슈)은 커 보이고 길쭉한 물건(분무기·램프)은
작아 보인다. 사람 눈은 면적으로 크기를 느끼므로 배율 ∝ 긴변/√(가로×세로) 로 잡는다.
(가로·세로는 캔버스가 아니라 **불투명 픽셀의 실제 bbox**)

    python3 tools/calc_item_scale.py     # js/assets.js 의 ITEM_SCALE 에 붙여 넣을 값
"""
import math
from PIL import Image

ITEMS = [
    ('구겨진 잠옷', 'pajama'), ('머그컵', 'mug'), ('티슈 상자', 'tissue'),
    ('노란 고무장갑', 'gloves'), ('분무기', 'spray'), ('쿠션', 'cushion'),
    ('탁상 램프', 'lamp'), ('작은 화분', 'plant'), ('물뿌리개', 'can'),
    ('장바구니', 'basket'), ('새 운동화', 'sneakers'),
]

if __name__ == '__main__':
    raw = {}
    for kr, f in ITEMS:
        im = Image.open(f'assets/room/ui/kit/it_{f}.png').convert('RGBA')
        bb = im.split()[3].getbbox()
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        raw[kr] = max(w, h) / math.sqrt(w * h)
    mean = sum(raw.values()) / len(raw)        # 평균을 1로 맞춰 기본 박스 비율을 유지
    for kr, _ in ITEMS:
        print(f"  '{kr}': {raw[kr] / mean:.2f},")
