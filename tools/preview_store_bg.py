#!/usr/bin/env python3
"""달님 에셋 통합: 중앙정렬 배경 + 코드 HUD(통일명패+픽셀폰트=동적텍스트) + 타일 + 장애물 + 캐릭터 + 힌트 모달."""
import os, math
from PIL import Image, ImageDraw, ImageFont
A=os.path.join(os.path.dirname(__file__),"..","assets")
L=lambda n: Image.open(os.path.join(A,n)).convert("RGBA")
bg=L("store_bg.png"); char=L("char_player.png")
plant=L("obstacle_plant.png"); boxes=L("obstacle_boxes.png")
hint=L("hint_panel.png"); close=L("btn_close.png")
PLATE={"score":L("plate_score.png"),"stage":L("plate_stage.png"),"timer":L("plate_timer.png")}
TILES={0:L("tile_clean.png"),1:L("tile_d1.png"),2:L("tile_d2.png"),
       3:L("tile_d3.png"),4:L("tile_d4.png"),5:L("tile_d5.png")}
FONT="/mnt/skills/examples/canvas-design/canvas-fonts/PixelifySans-Medium.ttf"

# ---------- HUD: 달님 명패(아이콘 유지) + 텍스트 얹기(동적) ----------
def build_hud(W,Hh, sval, stval, tval, SS=3):
    F=lambda p: ImageFont.truetype(FONT,p*SS)
    img=Image.new("RGBA",(W*SS,Hh*SS),(0,0,0,0)); d=ImageDraw.Draw(img)
    ph=Hh-8; INK=(92,60,38)
    items=[(PLATE["score"],(45,173),sval,16),(PLATE["stage"],(7,167),"STAGE "+stval,15),
           (PLATE["timer"],(46,117),tval,16)]
    pw=int(W*0.30); gap=(W-3*pw)/4
    for i,(plate,reg,text,fpx) in enumerate(items):
        x=int((gap*(i+1)+pw*i))*SS
        img.alpha_composite(plate.resize((pw*SS,ph*SS),Image.LANCZOS),(x,4*SS))
        sx=pw/plate.width*SS
        cxr=x+(reg[0]+reg[1])/2*sx
        f=F(fpx); b=d.textbbox((0,0),text,font=f)
        d.text((cxr-(b[2]-b[0])/2,4*SS+ph*SS/2-(b[3]-b[1])/2-b[1]),text,font=f,fill=INK)
    return img.resize((W,Hh),Image.LANCZOS)

HUD=52
W=bg.width; H=HUD+bg.height
img=Image.new("RGBA",(W,H),(0,0,0,255)); d=ImageDraw.Draw(img)
img.alpha_composite(bg,(0,HUD))
# HUD 바 배경 + 코드 HUD(동적 텍스트)
d.rectangle((0,0,W,HUD),fill=(150,120,86,255)); d.rectangle((0,HUD-3,W,HUD),fill=(96,70,50,255))
img.alpha_composite(build_hud(W,HUD, "12/49", "3", "0:38"),(0,0))

# === 플레이 영역(중앙정렬) ===
gx0,gy0,gx1,gy1=189,167,515,457
cols=rows=5
cw=(gx1-gx0)/cols; ch=(gy1-gy0)/rows
layout=[[3,1,0,2,5],[1,0,'B',0,2],[0,2,4,1,0],[2,'O',1,0,3],[1,0,2,3,1]]
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

# === ? 버튼 ===
def wood_btn(cx,cy,w,h,txt):
    d.rounded_rectangle((cx-w/2,cy-h/2,cx+w/2,cy+h/2),6,fill=(222,206,178),outline=(120,92,66),width=3)
    f=ImageFont.truetype(FONT,18); b=d.textbbox((0,0),txt,font=f)
    d.text((cx-(b[2]-b[0])/2,cy-(b[3]-b[1])/2-b[1]),txt,font=f,fill=(120,80,50))
wood_btn(W/2, HUD+gy1+18, 30,26, "?")

def render(save_name, show_hint):
    base=img.copy()
    if show_hint:
        base.alpha_composite(Image.new("RGBA",(W,H),(30,20,14,120)))
        pw=int(W*0.82); ph2=int(hint.height*pw/hint.width)
        px=(W-pw)//2; py=H-ph2-70
        base.alpha_composite(hint.resize((pw,ph2),Image.LANCZOS),(px,py))
        cw2=int(W*0.22); ch2=int(close.height*cw2/close.width)
        base.alpha_composite(close.resize((cw2,ch2),Image.LANCZOS),((W-cw2)//2,py+ph2+10))
    base.convert("RGB").save(os.path.join(os.path.dirname(__file__),save_name)); print("saved",save_name)

render("_store_bg.png", False)
render("_store_hint.png", True)
