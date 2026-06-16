#!/usr/bin/env python3
"""달님이 만든 에셋(추출한 냉장고 벽 + 캐릭터)으로 편의점 화면 조립 데모."""
import os
from PIL import Image, ImageDraw
ROOT=os.path.dirname(__file__)
char=Image.open(os.path.join(ROOT,"..","assets","char_store.png")).convert("RGBA")
fridgewall=Image.open("/tmp/objs/0.png").convert("RGBA")   # 냉장고 벽
coffeerow=Image.open("/tmp/objs/2.png").convert("RGBA")    # 정수기/커피머신/캐비닛 줄

W,H=432,768
img=Image.new("RGBA",(W,H),(238,228,210,255))
d=ImageDraw.Draw(img)

# 바닥(깨끗한 베이지 타일) 32px
TS=36; base=(232,222,198); grout=(208,196,170)
floor=Image.new("RGBA",(TS,TS),base+(255,))
fd=ImageDraw.Draw(floor)
fd.line((0,0,TS,0),fill=grout+(255,)); fd.line((0,0,0,TS),fill=grout+(255,))
for y in range(0,H,TS):
    for x in range(0,W,TS):
        img.alpha_composite(floor,(x,y))

# 상단: 냉장고 벽(가로로 꽉 채움)
fw=W; fh=int(fridgewall.height*fw/fridgewall.width)
img.alpha_composite(fridgewall.resize((fw,fh),Image.LANCZOS),(0,0))
# 그림자
d.rectangle((0,fh,W,fh+4),fill=(0,0,0,40))

# 좌측: 커피/캐비닛 줄 세로 배치(회전 없이 그냥 측면 소품으로 하단)
cr_w=int(W*0.62); cr_h=int(coffeerow.height*cr_w/coffeerow.width)
img.alpha_composite(coffeerow.resize((cr_w,cr_h),Image.LANCZOS),(W-cr_w-4,H-cr_h-6))

# 플레이 그리드 5x5
cols=rows=5; cell=58
gx=(W-cols*cell)//2; gy=fh+40
# 몰딩 테두리
d.rounded_rectangle((gx-10,gy-10,gx+cols*cell+10,gy+rows*cell+10),12,
                    fill=(214,196,168,255),outline=(150,120,86),width=4)
d.rounded_rectangle((gx-4,gy-4,gx+cols*cell+4,gy+rows*cell+4),8,fill=(236,226,202,255))
dirt=[[5,3,1,0,2],[3,1,0,2,4],[1,0,2,4,1],[0,2,1,0,1],[2,1,0,1,0]]
tint={5:(78,58,40,210),4:(96,72,48,180),3:(120,96,64,150),2:(150,128,92,110),1:(186,170,134,70)}
for r in range(rows):
    for c in range(cols):
        x=gx+c*cell; y=gy+r*cell
        img.alpha_composite(floor.resize((cell,cell),Image.NEAREST),(x,y))
        d.rectangle((x,y,x+cell-1,y+cell-1),outline=(150,120,86,120),width=1)
        v=dirt[r][c]
        if v>0:
            ov=Image.new("RGBA",(cell,cell),tint[v]); img.alpha_composite(ov,(x,y))

# 캐릭터(가운데 칸), 약 2.4칸 높이
ch=int(cell*2.5); cw=int(char.width*ch/char.height)
cxp=gx+2*cell+cell//2; foot=gy+2*cell+cell
d.ellipse((cxp-cell*0.4,foot-8-cell*0.12,cxp+cell*0.4,foot-8+cell*0.12),fill=(0,0,0,55))
img.alpha_composite(char.resize((cw,ch),Image.LANCZOS),(int(cxp-cw/2),int(foot-ch+6)))

# 간단 HUD
d.rounded_rectangle((12,fh+6,150,fh+34),8,fill=(60,46,38,230))
d.text((24,fh+13),"✦ 12/49",fill=(244,220,120))
d.rounded_rectangle((W-150,fh+6,W-12,fh+34),8,fill=(60,46,38,230))
d.text((W-138,fh+13),"⏱ 0:45   ⟳",fill=(240,236,228))

img.convert("RGB").save(os.path.join(ROOT,"_store_real.png"))
print("saved", os.path.join(ROOT,"_store_real.png"))
