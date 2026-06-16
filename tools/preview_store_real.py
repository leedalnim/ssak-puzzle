#!/usr/bin/env python3
"""목업(달님 완성 디자인)을 충실히 재현 — 실제 추출한 HUD 명패/소품/캐릭터 사용."""
import os
from PIL import Image, ImageDraw
A=os.path.join(os.path.dirname(__file__),"..","assets")
L=lambda n: Image.open(os.path.join(A,n)).convert("RGBA")
char=L("char_store.png"); fridge=L("store_fridgewall.png"); coffee=L("store_coffeerow.png")
score=L("hud_score.png"); stage=L("hud_stage.png"); timer=L("hud_timer.png")
TILES={0:L("tile_clean.png"),1:L("tile_d1.png"),2:L("tile_d2.png"),
       3:L("tile_d3.png"),4:L("tile_d4.png"),5:L("tile_d5.png")}

W,H=360,640
img=Image.new("RGBA",(W,H),(228,216,194,255)); d=ImageDraw.Draw(img)

# 바닥 타일 — 실제 추출한 깨끗한 타일로 타일링
TS=30
floor=TILES[0].resize((TS,TS),Image.NEAREST)
for y in range(0,H,TS):
    for x in range(0,W,TS): img.alpha_composite(floor,(x,y))

def place(im,x,y,h):
    w=int(im.width*h/im.height); img.alpha_composite(im.resize((w,h),Image.LANCZOS),(int(x),int(y))); return w

# === 상단 HUD 바 (실제 명패) ===
hb=46
d.rectangle((0,0,W,hb),fill=(74,54,42,255))
d.rectangle((0,hb-3,W,hb),fill=(50,36,28,255))
ph=30; ty=(hb-ph)//2
sw=int(score.width*ph/score.height); tw=int(timer.width*ph/timer.height); stw=int(stage.width*ph/stage.height)
place(score,8,ty,ph)
place(timer,W-8-tw,ty,ph)
place(stage,(W-stw)//2,ty,ph)

# === 매장 소품(가장자리 프레임) ===
fw=W; fh=int(fridge.height*fw/fridge.width)
img.alpha_composite(fridge.resize((fw,fh),Image.LANCZOS),(0,hb))
d.rectangle((0,hb+fh,W,hb+fh+3),fill=(0,0,0,45))
# 하단 카운터/커피
cw=int(W*0.7); ch2=int(coffee.height*cw/coffee.width)
img.alpha_composite(coffee.resize((cw,ch2),Image.LANCZOS),((W-cw)//2,H-ch2-4))

# === 플레이 영역 (몰딩 프레임 + 5x5 그리드) ===
cols=rows=5; cell=48
gx=(W-cols*cell)//2; gy=hb+fh+24
# 몰딩
d.rounded_rectangle((gx-12,gy-12,gx+cols*cell+12,gy+rows*cell+12),12,
                    fill=(206,184,150,255),outline=(150,118,82),width=4)
d.rounded_rectangle((gx-5,gy-5,gx+cols*cell+5,gy+rows*cell+5),8,fill=(236,226,202,255))
dirt=[[5,3,1,0,2],[3,1,0,2,4],[1,0,2,4,1],[0,2,1,0,1],[2,1,0,1,0]]
for r in range(rows):
    for c in range(cols):
        x=gx+c*cell; y=gy+r*cell
        v=dirt[r][c]
        img.alpha_composite(TILES[v].resize((cell,cell),Image.NEAREST),(x,y))
        d.rectangle((x,y,x+cell-1,y+cell-1),outline=(150,120,86,90),width=1)
# 캐릭터
chh=int(cell*2.4); cwd=int(char.width*chh/char.height)
cxp=gx+2*cell+cell//2; foot=gy+2*cell+cell
d.ellipse((cxp-cell*0.38,foot-8-cell*0.11,cxp+cell*0.38,foot-8+cell*0.11),fill=(0,0,0,55))
img.alpha_composite(char.resize((cwd,chh),Image.LANCZOS),(int(cxp-cwd/2),int(foot-chh+6)))

img.convert("RGB").save(os.path.join(os.path.dirname(__file__),"_store_faithful.png"))
print("saved _store_faithful.png")
