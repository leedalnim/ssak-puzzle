#!/usr/bin/env python3
"""달님 에셋 통합: 중앙정렬 배경 + 비율유지 HUD + 정렬 타일 + 장애물 + 캐릭터 + 힌트 범례 모달."""
import os
from PIL import Image, ImageDraw
A=os.path.join(os.path.dirname(__file__),"..","assets")
L=lambda n: Image.open(os.path.join(A,n)).convert("RGBA")
bg=L("store_bg.png"); char=L("char_player.png")
score=L("hud_score.png"); stage=L("hud_stage.png"); timer=L("hud_timer.png")
plant=L("obstacle_plant.png"); boxes=L("obstacle_boxes.png")
hint=L("hint_panel.png"); close=L("btn_close.png")
TILES={0:L("tile_clean.png"),1:L("tile_d1.png"),2:L("tile_d2.png"),
       3:L("tile_d3.png"),4:L("tile_d4.png"),5:L("tile_d5.png")}

HUD=50
W=bg.width; H=HUD+bg.height
img=Image.new("RGBA",(W,H),(0,0,0,255)); d=ImageDraw.Draw(img)
img.alpha_composite(bg,(0,HUD))

# === HUD 바: 비율 유지(찌그러짐 X), 3등분 균등 ===
d.rectangle((0,0,W,HUD),fill=(214,198,170,255))
d.rectangle((0,HUD-3,W,HUD),fill=(150,120,86,255))
ph=38; ty=(HUD-ph)//2
def Wof(im): return int(im.width*ph/im.height)
def place_center(im,cx): img.alpha_composite(im.resize((Wof(im),ph),Image.LANCZOS),(int(cx-Wof(im)/2),ty))
third=W/3
place_center(score, third*0.5)
place_center(stage, third*1.5)
place_center(timer, third*2.5)

# === 플레이 영역(중앙정렬 배경의 몰딩 안쪽) ===
gx0,gy0,gx1,gy1=189,167,515,457
cols=rows=5
cw=(gx1-gx0)/cols; ch=(gy1-gy0)/rows
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
        v=layout[r][c]; lvl=v if isinstance(v,int) else 0
        img.alpha_composite(TILES[lvl].resize((int(cw)+1,int(ch)+1),Image.LANCZOS),(int(x),int(y)))
def put_obstacle(im,r,c,scale):
    x=gx0+c*cw; y=HUD+gy0+r*ch
    ih=int(ch*scale); iw=int(im.width*ih/im.height)
    d.ellipse((x+cw/2-cw*0.32,y+ch-7-ch*0.1,x+cw/2+cw*0.32,y+ch-7+ch*0.1),fill=(0,0,0,55))
    img.alpha_composite(im.resize((iw,ih),Image.LANCZOS),(int(x+cw/2-iw/2),int(y+ch-ih+ch*0.05)))
for r in range(rows):
    for c in range(cols):
        if layout[r][c]=='O': put_obstacle(plant,r,c,1.4)
        if layout[r][c]=='B': put_obstacle(boxes,r,c,1.25)

# === 캐릭터 ===
pr,pc=2,2
chh=int(ch*1.5); cwd=int(char.width*chh/char.height)
cxp=gx0+(pc+0.5)*cw; foot=HUD+gy0+(pr+1)*ch
d.ellipse((cxp-cw*0.32,foot-7-ch*0.1,cxp+cw*0.32,foot-7+ch*0.1),fill=(0,0,0,55))
img.alpha_composite(char.resize((cwd,chh),Image.LANCZOS),(int(cxp-cwd/2),int(foot-chh+4)))

# === ? 버튼(범례 열기) — 보드 하단 중앙 ===
def wood_btn(cx,cy,w,h,txt):
    d.rounded_rectangle((cx-w/2,cy-h/2,cx+w/2,cy+h/2),6,fill=(222,206,178),outline=(120,92,66),width=3)
    d.text((cx-4,cy-7),txt,fill=(120,80,50))
wood_btn(W/2, HUD+gy1+18, 30,26, "?")

def render(save_name, show_hint):
    base=img.copy(); dd=ImageDraw.Draw(base)
    if show_hint:
        # 모달 백드롭
        ov=Image.new("RGBA",(W,H),(30,20,14,120)); base.alpha_composite(ov)
        # 범례 패널(하단 중앙)
        pw=int(W*0.82); ph2=int(hint.height*pw/hint.width)
        px=(W-pw)//2; py=H-ph2-70
        base.alpha_composite(hint.resize((pw,ph2),Image.LANCZOS),(px,py))
        # Close 버튼
        cw2=int(W*0.22); ch2=int(close.height*cw2/close.width)
        base.alpha_composite(close.resize((cw2,ch2),Image.LANCZOS),((W-cw2)//2, py+ph2+10))
    base.convert("RGB").save(os.path.join(os.path.dirname(__file__),save_name))
    print("saved",save_name)

render("_store_bg.png", False)        # 평소(? 버튼)
render("_store_hint.png", True)       # 범례 열림
