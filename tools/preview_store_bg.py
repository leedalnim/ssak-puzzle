#!/usr/bin/env python3
"""달님 '배경(한 판)' + 32x32 타일 + 장애물 + HUD 명패 + 캐릭터 — 정렬 교정판."""
import os
from PIL import Image, ImageDraw
A=os.path.join(os.path.dirname(__file__),"..","assets")
L=lambda n: Image.open(os.path.join(A,n)).convert("RGBA")
bg=L("store_bg.png"); char=L("char_store.png")
score=L("hud_score.png"); stage=L("hud_stage.png"); timer=L("hud_timer.png")
plant=L("obstacle_plant.png"); boxes=L("obstacle_boxes.png")
TILES={0:L("tile_clean.png"),1:L("tile_d1.png"),2:L("tile_d2.png"),
       3:L("tile_d3.png"),4:L("tile_d4.png"),5:L("tile_d5.png")}

HUD=50
W=bg.width; H=HUD+bg.height
img=Image.new("RGBA",(W,H),(0,0,0,255)); d=ImageDraw.Draw(img)
img.alpha_composite(bg,(0,HUD))

# === HUD 바: 목업처럼 3등분 균등 배치 ===
d.rectangle((0,0,W,HUD),fill=(214,198,170,255))
d.rectangle((0,HUD-3,W,HUD),fill=(150,120,86,255))
ph=40; ty=(HUD-ph)//2
def W_of(im): return int(im.width*ph/im.height)
def place_center(im,cx): img.alpha_composite(im.resize((W_of(im),ph),Image.LANCZOS),(int(cx-W_of(im)/2),ty))
third=W/3
place_center(score, third*0.5)
place_center(stage, third*1.5)
place_center(timer, third*2.5)

# === 플레이 영역 (몰딩 안쪽, 픽셀검출 좌표) ===
gx0,gy0,gx1,gy1=187,160,514,455
cols=rows=5
cw=(gx1-gx0)/cols; ch=(gy1-gy0)/rows
# 레이아웃: O=장애물 화분, B=박스, 숫자=더러움, .=깨끗
layout=[
 [3,1,0,2,5],
 [1,0,'B',0,2],
 [0,2,4,1,0],
 [2,'O',1,0,3],
 [1,0,2,3,1],
]
for r in range(rows):
    for c in range(cols):
        x=gx0+c*cw; y=HUD+gy0+r*ch
        v=layout[r][c]
        lvl=v if isinstance(v,int) else 0   # 장애물 칸 바닥은 깨끗 타일
        # 모든 칸에 타일 배치(기본 타일 포함)
        img.alpha_composite(TILES[lvl].resize((int(cw)+1,int(ch)+1),Image.LANCZOS),(int(x),int(y)))
# 장애물(셀 위에 얹기, 발밑 정렬)
def put_obstacle(im,r,c,scale=1.15):
    x=gx0+c*cw; y=HUD+gy0+r*ch
    ih=int(ch*scale); iw=int(im.width*ih/im.height)
    px=int(x+cw/2-iw/2); py=int(y+ch-ih+ch*0.05)
    d.ellipse((x+cw/2-cw*0.32,y+ch-7-ch*0.1,x+cw/2+cw*0.32,y+ch-7+ch*0.1),fill=(0,0,0,55))
    img.alpha_composite(im.resize((iw,ih),Image.LANCZOS),(px,py))
for r in range(rows):
    for c in range(cols):
        if layout[r][c]=='O': put_obstacle(plant,r,c,1.4)
        if layout[r][c]=='B': put_obstacle(boxes,r,c,1.25)

# === 캐릭터 ===
pr,pc=2,2
chh=int(ch*2.2); cwd=int(char.width*chh/char.height)
cxp=gx0+(pc+0.5)*cw; foot=HUD+gy0+(pr+1)*ch
d.ellipse((cxp-cw*0.32,foot-7-ch*0.1,cxp+cw*0.32,foot-7+ch*0.1),fill=(0,0,0,55))
img.alpha_composite(char.resize((cwd,chh),Image.LANCZOS),(int(cxp-cwd/2),int(foot-chh+4)))

img.convert("RGB").save(os.path.join(os.path.dirname(__file__),"_store_bg.png"))
print("saved", (W,H))
