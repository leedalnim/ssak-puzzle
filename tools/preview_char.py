#!/usr/bin/env python3
"""달님이 만든 캐릭터(배경제거)를 게임 화면에 올려본 데모."""
import os
from PIL import Image, ImageDraw
ROOT=os.path.join(os.path.dirname(__file__),"..")
A=os.path.join(ROOT,"assets")
VW,VH=216,384
load=lambda n: Image.open(os.path.join(A,n)).convert("RGBA")
TILES=[load(f"tile_{d}.png") for d in range(4)]
char=load("char_store.png")
plant=load("plant.png"); cat=load("cat.png"); fridge=load("fridge.png"); shelf=load("shelf.png")

def hexrgb(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
img=Image.new("RGBA",(VW,VH),(255,255,255,255))
d=ImageDraw.Draw(img)
# 방 배경
wall=hexrgb("#dde9f1"); floor=hexrgb("#ebdab1")
d.rectangle((0,0,VW,96),fill=wall)
d.rectangle((0,96,VW,VH),fill=floor)
d.rectangle((0,90,VW,96),fill=tuple(max(0,c-25) for c in wall))
# 소품(편의점)
for im,(x,y),s in [(fridge,(2,VH-fridge.height*2-4),2),(shelf,(VW-shelf.width*2-2,VH-shelf.height*2-4),2)]:
    img.alpha_composite(im.resize((im.width*s,im.height*s),Image.NEAREST),(x,y))
# 청소 그리드 5x5
cols=rows=5; S=2; tp=16*S
bx=(VW-cols*tp)//2; by=(VH-rows*tp)//2+6
d.rounded_rectangle((bx-6,by-6,bx+cols*tp+6,by+rows*tp+6),8,fill=(255,250,242,255),outline=(120,92,72),width=2)
dirt=[[3,2,1,0,1],[2,1,0,1,2],[1,0,1,2,3],[0,1,2,1,0],[1,2,1,0,1]]
for r in range(rows):
    for c in range(cols):
        v=dirt[r][c]
        img.alpha_composite(TILES[v].resize((tp,tp),Image.NEAREST),(bx+c*tp,by+r*tp))
# 캐릭터: 그리드 중앙 칸에, 약 2.4타일 높이
ch=int(tp*2.6); cw=int(char.width*ch/char.height)
cxp=bx+2*tp+tp//2; foot=by+2*tp+tp
d.ellipse((cxp-tp*0.4,foot-6-tp*0.13,cxp+tp*0.4,foot-6+tp*0.13),fill=(0,0,0,60))
img.alpha_composite(char.resize((cw,ch),Image.LANCZOS),(int(cxp-cw/2),int(foot-ch+4)))
out=img.convert("RGB").resize((VW*3,VH*3),Image.NEAREST)
p=os.path.join(os.path.dirname(__file__),"_char_scene.png")
out.save(p); print("saved",p)
