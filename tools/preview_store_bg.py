#!/usr/bin/env python3
"""달님 제공 '배경(한 판)' + 32x32 타일 + HUD 명패 + 캐릭터로 충실 재현."""
import os
from PIL import Image, ImageDraw
A=os.path.join(os.path.dirname(__file__),"..","assets")
L=lambda n: Image.open(os.path.join(A,n)).convert("RGBA")
bg=L("store_bg.png"); char=L("char_store.png")
score=L("hud_score.png"); stage=L("hud_stage.png"); timer=L("hud_timer.png")
TILES={0:L("tile_clean.png"),1:L("tile_d1.png"),2:L("tile_d2.png"),
       3:L("tile_d3.png"),4:L("tile_d4.png"),5:L("tile_d5.png")}

HUD=54
W=bg.width; H=HUD+bg.height
img=Image.new("RGBA",(W,H),(60,46,38,255)); d=ImageDraw.Draw(img)
img.alpha_composite(bg,(0,HUD))

# HUD 바
d.rectangle((0,0,W,HUD),fill=(74,54,42,255)); d.rectangle((0,HUD-4,W,HUD),fill=(48,34,26,255))
ph=34; ty=(HUD-ph)//2
def place(im,x,y,h):
    w=int(im.width*h/im.height); img.alpha_composite(im.resize((w,h),Image.LANCZOS),(int(x),int(y))); return w
sw=int(score.width*ph/score.height); tw=int(timer.width*ph/timer.height); stw=int(stage.width*ph/stage.height)
place(score,10,ty,ph); place(timer,W-10-tw,ty,ph); place(stage,(W-stw)//2,ty,ph)

# 플레이 영역 5x5 (배경 몰딩 안쪽)
gx0,gy0,gx1,gy1=152,105,496,446
cols=rows=5
cw=(gx1-gx0)/cols; ch=(gy1-gy0)/rows
dirt=[[5,3,1,0,2],[3,1,0,2,4],[1,0,2,4,1],[0,2,1,0,1],[2,1,0,1,0]]
for r in range(rows):
    for c in range(cols):
        x=gx0+c*cw; y=HUD+gy0+r*ch
        v=dirt[r][c]
        if v>0:  # 깨끗한 칸은 배경 바닥 그대로
            img.alpha_composite(TILES[v].resize((int(cw)+1,int(ch)+1),Image.LANCZOS),(int(x),int(y)))
        d.rectangle((int(x),int(y),int(x+cw),int(y+ch)),outline=(150,120,86,70),width=1)

# 캐릭터(가운데 칸)
chh=int(ch*2.3); cwd=int(char.width*chh/char.height)
cxp=gx0+2.5*cw; foot=HUD+gy0+3*ch
d.ellipse((cxp-cw*0.34,foot-7-ch*0.1,cxp+cw*0.34,foot-7+ch*0.1),fill=(0,0,0,55))
img.alpha_composite(char.resize((cwd,chh),Image.LANCZOS),(int(cxp-cwd/2),int(foot-chh+5)))

img.convert("RGB").save(os.path.join(os.path.dirname(__file__),"_store_bg.png"))
print("saved _store_bg.png", (W,H))
