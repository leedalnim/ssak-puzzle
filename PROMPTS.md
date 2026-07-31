# 배경 컨셉 이미지 생성 프롬프트 (GPT Image 2)

> 목적: 게임에 바로 끼울 수 있는 **"가운데가 빈" 배경 6장**을 일관된 스타일로 생성.
> 배경 위에 보드/타일/캐릭터/HUD는 **코드가 그림** → 배경에 격자를 그리면 안 됨.

---

## ⚠️ 전달 방법 (중요)

생성한 이미지는 **첨부(📎)로** 주세요. 채팅에 **붙여넣기(Ctrl+V)한 이미지는 파일로 저장되지 않아
제가 픽셀을 열 수 없습니다.** (보이긴 하지만 가공이 불가능)

---

## 🔒 일관성 유지 팁

1. **1장 먼저** 뽑아서 마음에 드는 결과가 나오면
2. 그 이미지를 **참조 이미지로 첨부**하고 나머지 5장 요청
   → `"Same art style, palette, camera angle, and lighting as the reference image."`
3. 6장 모두 **같은 시야각·같은 팔레트**여야 스테이지 전환이 자연스러움

---

## 📐 공통 규칙 (모든 프롬프트에 포함)

- 세로형 (2:3 또는 9:16). 중요한 요소를 **화면 가장자리 끝에 두지 말 것** (기기별 크롭 대비)
- **가운데 빈 바닥 영역 필수** — 폭 80%, 높이 45% 정도
- 그 영역엔 **아무것도 없어야 함**: 가구·러그·소품·격자·타일무늬·그림자 전부 금지
- **캐릭터/사람 없음** (캐릭터는 별도 스프라이트)
- **UI·텍스트·아이콘·테두리 프레임 없음**
- 조명은 균일하게 (빈 바닥에 강한 그림자 지면 타일이 어색해짐)

---

## 🎨 마스터 프롬프트 (영문 — 그대로 붙여넣기)

`{LOCATION}` 부분만 아래 장소별 블록으로 교체하세요.

```
Top-down view of {LOCATION}, cozy pixel art game background, portrait orientation.

STYLE: 16-bit era pixel art, warm wood and cream palette, muted earthy tones,
soft even lighting, no harsh shadows, clean readable shapes, hand-crafted cozy mood.

CRITICAL LAYOUT REQUIREMENT:
Leave a LARGE EMPTY rectangular floor area in the CENTER of the image
(about 80% of the width and 45% of the height). This center area must be
completely empty — plain clean floor only. Absolutely NO furniture, NO props,
NO rugs, NO grid lines, NO tile pattern, NO checkerboard, NO shadows in that area.

Place ALL furniture and props ONLY along the top, left, right, and bottom edges,
framing the empty center.

DO NOT INCLUDE: any characters or people, any UI elements, any text or numbers,
any border frame, any floor grid or tile seams in the center area.
```

---

## 📍 장소별 `{LOCATION}` 블록

### 1. 자취방 (스테이지 1~3)
```
a small cozy studio apartment bedroom with a wooden bed and green checkered pillow,
a nightstand with a lamp, a desk with a laptop and desk lamp, a window with blinds
and a small potted plant, a bookshelf, a mini fridge, a laundry basket, house plants
```

### 2. 부엌 (스테이지 4)
```
a small home kitchen with a sink and faucet, a gas stove, wooden counters,
upper cabinets, a refrigerator, a dish rack, hanging mugs, a small kitchen window
```

### 3. 현관 (스테이지 5)
```
a small apartment entryway with a front door, a wooden shoe rack with sneakers,
coat hooks with a bag and jacket, an umbrella stand, a small doormat, a mirror
```

### 4. 편의점 (스테이지 6)
```
a convenience store interior with tall shelves of snacks and instant noodles,
glass-door drink refrigerators, a checkout counter with a register,
a coffee machine, cardboard boxes stacked at the side
```

### 5. 카페 (스테이지 7)
```
a cozy cafe interior with a wooden counter and espresso machine, a pastry display case,
small round tables with chairs, hanging plants, a chalkboard menu with no readable text,
warm pendant lights
```

### 6. 베이커리 (스테이지 8)
```
a warm bakery interior with bread display cases full of loaves and pastries,
a large oven, a wooden counter, flour sacks, baking trays on racks, a window
letting in morning light
```

---

## ✅ 받은 이미지 체크리스트 (제가 확인할 항목)

- [ ] 가운데 바닥이 **정말 비어 있는가** (소품·러그가 침범하지 않았는지)
- [ ] 바닥에 **격자/타일 이음새가 없는가**
- [ ] 빈 바닥의 **밝기가 균일한가** (강한 그림자/하이라이트 없음)
- [ ] 사람·텍스트·UI가 없는가
- [ ] 시야각·팔레트가 **다른 장과 일치**하는가

문제가 있으면 어느 부분을 어떻게 고쳐 달라고 할지 구체적으로 알려드립니다.

---

## 🔧 자주 필요한 보정 요청문

| 문제 | 추가 지시문 |
|---|---|
| 가운데에 소품이 침범 | `The center floor area must be completely empty — remove all objects from it and move them to the edges.` |
| 바닥에 격자가 생김 | `The center floor must be a smooth plain surface with no grid, no tile seams, no repeating pattern.` |
| 빈 공간이 너무 작음 | `Make the empty center floor area much larger — at least 80% of the image width and 45% of the height.` |
| 그림자가 짐 | `Use flat even lighting on the center floor with no cast shadows.` |
| 시점이 기울어짐 | `Strict top-down camera angle, same as the reference image.` |

---

# 🖼️ 전체 화면 목업 프롬프트 (UI안 B 기준)

> 배경 + 보드 + 타일단계 + 장애물 + 캐릭터 + 상하단 UI를 모두 포함한 **디자인 기준서용** 목업.
> 이걸로 비율·색·스타일을 확정한 뒤, 배경/캐릭터/장애물만 따로 받아 게임에 넣는다.

```
Top-down view of a small cozy studio apartment bedroom — full mobile puzzle game
screen mockup, portrait orientation, 16-bit pixel art.

PALETTE — bright, clean and cheerful: soft cream and ivory base, light natural
wood (beige-toned, NOT orange or amber), sage green and mint accents, bright
natural daylight. NOT dark, NOT gloomy, NOT sepia, NOT muddy.

ROOM (background): a bed with a green checkered blanket, a desk with a laptop,
a bright window with curtains, a nightstand with a lamp, shelves with books,
house plants, a laundry basket. Place all of it ONLY along the top, left, right
and bottom edges, framing the center.

GAME BOARD (center): a 5x5 grid puzzle board with a light wooden frame,
taking about 82% of the screen width, centered.

TILES — 5 dirt levels plus clean:
  clean   : plain cream tile, nothing on it
  level 1 : very faint dust, 1 dot marker
  level 2 : light brown spots, 2 dot markers
  level 3 : medium brown stain, 3 dot markers
  level 4 : dark brown grime, 4 dot markers
  level 5 : nearly black-brown fully covered, 5 dot markers

IMPORTANT: each dirty tile has small round DOT MARKERS drawn on it in a row at
the tile center, showing how many times that tile must be wiped (1 to 5 dots).
Clean tiles have no dots.
Distribute the dirt NATURALLY and RANDOMLY like a real game in progress — most
tiles clean or only lightly dirty, only two or three heavily dirty. Do NOT
arrange them in a neat gradient, ordered rows, or a sample chart.

OBSTACLES: 2 or 3 obstacle objects sitting ON board tiles — a stack of cardboard
boxes, a potted plant, a laundry basket. They block those tiles. Draw them on
the grid itself, not at the room edges.

CHARACTER: a young woman with brown hair seen from behind, crouching and wiping
the floor with a cloth, standing on one of the board tiles. Make her LARGE and
clearly visible — about 1.5 tiles tall. She is the focal point of the screen.

TOP UI (compact and slim): on the left a small cream pill with a clock icon and
"01:45"; on the right a small cream pill with a tile icon and "12"; a small round
pause button in the top-right corner. Keep the top bar slim so the room stays visible.

BOTTOM UI (three controls in a row):
  left   : a round cream button with a "?" help icon
  center : a WIDE prominent button with a back-arrow undo icon — the biggest and
           most eye-catching control on screen
  right  : a round cream button with a circular restart arrow icon
All bright cream panels with light wood borders, crisp and cheerful.

Do not add any legend panel, any border frame around the whole image,
or any text other than the UI labels described above.
```

## UI안 C(아이템 확장형)로 바꾸려면

BOTTOM UI 블록만 아래로 교체:

```
BOTTOM UI (four controls in a row):
  left   : a round cream button with a "?" help icon
  center : a prominent wide button with a back-arrow undo icon
  right  : two square item slots holding cleaning items (a mop and a spray
           bottle), each with a small green count badge
```

## 이 목업에서 뽑아낼 것

| 확정할 값 | 용도 |
|---|---|
| 보드 폭 / 화면 폭 비율 | 코드의 보드 영역 좌표 |
| 셀 크기 대비 캐릭터 높이 | 캐릭터 렌더 스케일 |
| 상단바 / 하단바 높이 | 캔버스 높이 계산 |
| 타일 5단계 색상값 | 코드 타일 팔레트 |
| UI 패널 색 / 테두리 색 | CSS 변수 |

---

# 🧍 캐릭터 스프라이트 시트 프롬프트 (2등신 치비)

> 슬라이싱 실패를 막기 위해 **균일 그리드 · 마젠타 배경 · 텍스트 금지**를 명시.

```
Character sprite sheet for a 2D pixel art puzzle game. Chibi style.

CHARACTER: a cute chibi girl, 2 heads tall (big round head, small compact body),
brown hair tied in a messy bun, wearing a white t-shirt and green overalls,
white sneakers. She is HOLDING A MOP with both hands, standing upright and
walking. Simple cute face with small dot eyes and a tiny smile.

SHEET LAYOUT — follow this EXACTLY:
- A strict uniform grid of 4 rows x 3 columns, evenly spaced.
- Row 1: facing DOWN (toward viewer)
- Row 2: facing UP (back turned)
- Row 3: facing LEFT
- Row 4: facing RIGHT
- Each row shows 3 walking animation frames of that direction.
- Every cell is exactly the same size. The character is centered in her cell
  and drawn at the SAME scale in every cell, with a small margin around her.

BACKGROUND: a single flat solid magenta background (#FF00FF) behind everything.
No shadows on the background.

STRICTLY DO NOT INCLUDE: any text, any labels, any row or column titles,
any numbers, any drawn grid lines or cell borders, any decorations,
any props other than the mop.

STYLE: 16-bit pixel art, bright cream and sage green palette matching a cozy
game, clean readable shapes, crisp outlines.
```

## 통짜 목업용 캐릭터 블록 (교체용)

```
CHARACTER: a cute chibi girl, 2 heads tall (big round head, small body), brown
hair in a messy bun, white t-shirt and green overalls, holding a mop with both
hands, standing and mopping the floor. She stands on one board tile and fits
roughly within a single tile. Cute, charming, clearly visible.
```

---

# 🧊 3D 방향성 목업 프롬프트 (비교용)

> 픽셀아트 대안으로 3D 느낌을 검토하기 위한 목업.
> **카메라 각도에 따라 코드 작업량이 크게 달라짐** — 아래 표 참고.

| 방향 | 보드 모양 | 코드 영향 |
|---|---|---|
| A. 탑다운 3D (약 15° 기울기) | 직사각 격자 | 현재 구조 그대로 사용 가능 |
| B. 아이소메트릭 3D (45°) | 마름모 격자 | 좌표계·클릭판정·깊이정렬 전면 수정 |

## A. 탑다운 3D 디오라마 (구조 호환)

```
A cozy miniature 3D diorama of a small studio apartment bedroom — mobile puzzle
game screen mockup, portrait orientation. 3D rendered, NOT pixel art.

CAMERA: almost directly overhead, tilted only slightly (about 15 degrees) so the
floor reads as a flat rectangle. The grid must stay rectangular, not diamond-shaped.

STYLE: soft 3D render, miniature toy diorama, matte clay-like materials, soft
global illumination with gentle shadows, rounded edges, cute and tactile.
Bright cheerful palette — cream and ivory, light natural wood, sage green and
mint accents. Warm daylight from the window. Clean and inviting, not dark.

ROOM: a bed with a green checkered blanket, a desk with a laptop, a bright window
with curtains, a nightstand with a lamp, shelves, house plants, a laundry basket —
all placed ONLY along the top, left, right and bottom edges, framing the center.

GAME BOARD (center): a 5x5 rectangular grid of floor tiles with a soft wooden
frame, about 82% of screen width, sitting flat on the floor.

TILES — 5 dirt levels plus clean, distributed NATURALLY and randomly like a real
game in progress. Most tiles clean or lightly dirty, only two or three heavily
dirty. Each dirty tile has small round dot markers on it showing how many wipes
it needs (1 to 5 dots). Do NOT arrange the dirt in a neat gradient or chart.

OBSTACLES: 2 or 3 objects sitting ON board tiles — a stack of cardboard boxes,
a potted plant, a laundry basket.

CHARACTER: a cute chibi girl, 2 heads tall (big round head, small body), brown
hair in a messy bun, white t-shirt and green overalls, holding a mop with both
hands, standing on one board tile and fitting within a single tile. Soft rounded
3D toy figure, charming and clearly visible.

TOP UI (slim): a small rounded panel on the left with a clock icon and "01:45";
on the right a small panel with a tile icon and "12"; a round pause button in the
top-right corner.

BOTTOM UI: a round "?" help button on the left, a WIDE prominent undo button with
a back-arrow icon in the center (the biggest control), a round restart button on
the right. Soft rounded 3D UI panels in cream with subtle depth.

No text other than the UI labels. No border frame around the whole image.
```

## B. 아이소메트릭 3D 디오라마 (전체)

```
A cozy miniature 3D diorama of a small studio apartment bedroom — mobile puzzle
game screen mockup, portrait orientation. 3D rendered, NOT pixel art.

CAMERA: isometric 3/4 view at about 45 degrees, like a miniature dollhouse
diorama. The room is a small open-top box with two visible walls (back and left),
floating gently with a soft shadow beneath it.

STYLE: soft 3D render, miniature toy diorama, matte clay-like materials, soft
global illumination with gentle ambient shadows, rounded edges, cute and tactile.
Bright cheerful palette — cream and ivory, light natural wood, sage green and
mint accents. Warm daylight coming through the window. Clean and inviting,
NOT dark, NOT gloomy.

ROOM: a bed with a green checkered blanket, a desk with a laptop, a bright window
with curtains, a nightstand with a lamp, shelves with books, house plants, a
laundry basket. Place all of it ONLY against the two visible walls and along the
outer edges of the floor, keeping the center floor open.

GAME BOARD (center): a 5x5 grid of floor tiles laid out in isometric perspective
(diamond-shaped grid), with a soft wooden border, filling most of the room floor
and clearly readable as the play area.

TILES — 5 dirt levels plus clean:
  clean   : plain cream tile, nothing on it
  level 1 : very faint dust, 1 dot marker
  level 2 : light brown spots, 2 dot markers
  level 3 : medium brown stain, 3 dot markers
  level 4 : dark brown grime, 4 dot markers
  level 5 : nearly black-brown fully covered, 5 dot markers

Each dirty tile has small round DOT MARKERS on its surface showing how many times
it must be wiped (1 to 5 dots), lying flat on the tile and following the isometric
perspective. Clean tiles have no dots.
Distribute the dirt NATURALLY and RANDOMLY like a real game in progress — most
tiles clean or only lightly dirty, only two or three heavily dirty. Do NOT arrange
them in a neat gradient, ordered rows, or a sample chart.

OBSTACLES: 2 or 3 objects sitting ON board tiles — a stack of cardboard boxes,
a potted plant, a laundry basket. Keep them SHORT and low-profile so they do not
hide the tiles behind them. Place them toward the front of the board.

CHARACTER: a cute chibi girl, 2 heads tall (big round head, small compact body),
brown hair in a messy bun, white t-shirt and green overalls, white sneakers,
holding a mop with both hands, standing upright and mopping. She stands on one
board tile and fits within a single tile. Soft rounded 3D toy figure, charming
and clearly visible. Place her near the front of the board so she does not block
other tiles.

UI — drawn as a FLAT 2D overlay on top of the 3D scene, not inside the 3D space:
  TOP (slim): a small rounded cream panel on the left with a clock icon and
  "01:45"; on the right a small panel with a tile icon and "12"; a round pause
  button in the top-right corner.
  BOTTOM: a round "?" help button on the left; a WIDE prominent undo button with
  a back-arrow icon in the center — the biggest, most eye-catching control;
  a round restart button with a circular arrow on the right.
  All soft rounded cream panels with subtle depth and light wood accents.

No text other than the UI labels. No border frame around the whole image.
```

### 아이소메트릭 전용 주의사항
- **장애물은 낮고 앞쪽에** — 뒤 타일을 가리지 않도록
- **캐릭터도 앞쪽 배치** — 같은 이유
- **UI는 평면 2D 오버레이** — 3D 공간에 박히면 실제 구현 불가

## 검토 포인트

- **A**: 격자가 직사각으로 유지되는지 (기울기가 세지면 사다리꼴로 찌그러짐)
- **B**: 캐릭터·장애물이 뒤쪽 타일을 가리지 않는지 (아이소메트릭 특유의 오클루전)
- 공통: 타일 점 마커가 3D에서도 읽히는지

---

# 🧱 실제 에셋 생성 프롬프트 (3D 클레이 확정본)

> 클레이 목업을 **참조 이미지로 첨부**할 것 — 재질·팔레트·캐릭터 얼굴 유지.
> 공통: 마젠타(#FF00FF) 배경 · 균일 격자 · 텍스트/라벨/격자선 금지.

## 1. 타일 시트 (clean + 5단계)

```
Using the attached image as the exact style reference, create a sprite sheet of
floor tiles in the same soft 3D clay material and same cream palette.

LAYOUT: a strict uniform grid, 2 rows x 3 columns, evenly spaced, 6 tiles total.
  Tile 1: perfectly clean, plain cream, no dirt at all
  Tile 2: very faint dust, barely tinted
  Tile 3: light brown spots, clearly dirtier than tile 2
  Tile 4: medium brown stain covering the center
  Tile 5: heavy dark brown grime covering most of it
  Tile 6: almost fully covered in very dark brown dirt

Each tile is a perfect SQUARE seen straight from DIRECTLY ABOVE — completely
flat, no tilt, no perspective, no 3D angle. Soft rounded corners and a slightly
cushioned clay surface, exactly like the tiles in the reference image.
All six tiles are exactly the same size and shape — only the dirt differs.
The six dirt levels must be clearly distinguishable at a glance, in even steps.

BACKGROUND: a single flat solid magenta (#FF00FF) background.

STRICTLY NO text, NO labels, NO numbers, NO dots or markers on the tiles,
NO drawn grid lines or cell borders, NO shadows on the background.
```

⚠️ **타일은 반드시 평면 정사각형** — 원근은 코드가 적용하므로 에셋에 원근이
들어가면 이중으로 기울어져 찌그러진다.

## 2. 캐릭터 시트 (4방향 × 3프레임)

```
Using the attached image as the exact style reference, create a character sprite
sheet of the same chibi girl — same face, same messy brown bun, same white
t-shirt and green overalls, same white sneakers, same soft 3D clay material.
She holds a mop with both hands, standing upright and mopping.

LAYOUT: a strict uniform grid, 4 rows x 3 columns, evenly spaced.
  Row 1: facing DOWN, toward the viewer
  Row 2: facing UP, back turned
  Row 3: facing LEFT
  Row 4: facing RIGHT
Each row is 3 walking animation frames of that direction.

Every cell is exactly the same size. She is centered in her cell and drawn at
the SAME scale in every cell, full body visible with a small margin.

BACKGROUND: a single flat solid magenta (#FF00FF) background.

STRICTLY NO text, NO labels, NO numbers, NO drawn grid lines or cell borders,
NO shadows on the background, NO props other than the mop.
```

## 3. 장애물 3종

```
Using the attached image as the exact style reference, create three obstacle
objects in the same soft 3D clay material and palette.

LAYOUT: a single row of 3 objects, evenly spaced, same scale:
  1. a stack of two cardboard boxes
  2. a small potted green plant in a light ceramic pot
  3. a woven laundry basket with folded towels

Each object is seen from slightly above, sitting flat as if placed on a floor,
exactly matching the obstacles in the reference image. Keep them low-profile.

BACKGROUND: a single flat solid magenta (#FF00FF) background.

STRICTLY NO text, NO labels, NO shadows on the background, NO floor beneath them.
```

## 전달 방법
**zip으로 압축해 첨부** — 이 경로가 검증됨 (배경 전달 성공).

---

# 📱 다음 작업 — 앱 아이콘 & 타이틀 로고

## 1. 앱 아이콘 (모바일 북마크 / favicon)

아이콘은 **48px까지 작아진다.** 배경 일러스트를 그대로 쓰면 뭉개지므로
피사체를 크게, 형태를 단순하게 가야 한다.

### A안 — 캐릭터 얼굴 (브랜드가 됨)
```
Using the attached image as the exact style reference, create a mobile app
icon in the same soft 3D clay style, same cream and sage palette.

SUBJECT: an EXTREME CLOSE-UP of just the chibi girl's head and shoulders,
centered — big round head, brown hair in a messy bun, bright smiling eyes.
She holds the mop head up beside her face, and the black-and-white tuxedo
cat's face peeks in from the lower corner.

COMPOSITION: square 1:1. The character fills MOST of the frame — her head
alone should take up about 60% of the width. Simple flat cream background
with a soft rounded gradient, no room, no furniture, no floor.
Keep a small safe margin around the edges so nothing gets cropped.

CRITICAL: this will be viewed as small as 48x48 pixels. Use BOLD simple
shapes and STRONG contrast. No fine details, no thin lines, no small props,
no busy background.

STRICTLY NO text, NO logo, NO border frame, NO drop shadow outside the subject.
```

### B안 — 대걸레 심볼 (작아도 안 뭉개짐)
위 프롬프트에서 SUBJECT만 교체:
```
SUBJECT: a single cute 3D clay mop standing upright, with two or three
sparkle marks around it, centered on a flat cream background. Bold, simple,
instantly readable at tiny sizes.
```

> 둘 다 뽑아 **48px로 축소해 비교할 것.** 큰 화면에서 예쁜 것이 작을 때도 예쁘진 않다.

### 받은 뒤 Claude가 할 일
`favicon.ico` · `apple-touch-icon`(180px) · PWA 매니페스트(192/512px) 생성 후 연결.

---

## 2. 타이틀 로고 "쓱싹퍼즐"

현재는 웹폰트 텍스트라 밋밋하다. 이미지 로고로 교체 예정.

```
Using the attached image as the exact style reference, create a game logo
in the same soft 3D clay style, same warm cream and sage palette.

TEXT: the Korean word "쓱싹퍼즐" written in chunky rounded 3D clay letters —
soft matte clay material, gently beveled edges, a warm wood-brown color with
a lighter cream highlight on the top of each letter.

The letters sit on a single horizontal line, slightly playful and bouncy in
their baseline. Add two or three small sparkle marks around the letters.

BACKGROUND: a single flat solid magenta (#FF00FF) background.

CRITICAL: the Korean characters must be spelled EXACTLY "쓱싹퍼즐" —
four syllable blocks, in that order. Render them clearly and legibly.

STRICTLY NO other text, NO English, NO border frame, NO shadows on the background.
```

> ⚠️ AI 이미지 모델은 **한글 자소를 자주 틀린다.** 받은 뒤 글자가 정확히
> `쓱 / 싹 / 퍼 / 즐` 인지 반드시 확인할 것. 틀리면 재생성하거나,
> 폰트로 조판한 텍스트를 클레이 스타일로 변환 요청하는 편이 확실하다.


---

# 📦 2차 기능 목업 프롬프트 (첨부 이미지 불필요)

## ① 타이틀 화면 — 보관함·업적 진입점 추가

```
A cozy mobile game title screen mockup, portrait 9:19.5.

STYLE: soft 3D clay-render, miniature toy diorama look. Matte clay materials,
rounded beveled edges, gentle soft shadows, soft global illumination.
PALETTE: cream and ivory base, light natural beige wood (NOT orange), sage green
accents, warm daylight. Cozy and tactile. NOT pixel art, NOT flat vector, NOT dark.

SCENE: a warm cream room wall with a light wooden floor. A cute chibi girl
(2.5 heads tall, brown messy bun, white t-shirt, sage-green overalls, white
sneakers) stands holding a wooden mop. A black-and-white tuxedo cat sits beside
her. A few soft sparkle marks float around.

UI, top to bottom:
- A short Korean tagline in small bold brown text
- A chunky 3D clay Korean logo in warm wood-brown with cream highlights
- A wide CREAM clay pill button (primary)
- A slightly smaller HONEY-BROWN clay pill button (secondary)
- AT THE VERY BOTTOM: TWO small round clay icon buttons side by side, clearly
  smaller than the pills — cream clay circles with a light wood rim.
    left  : a woven basket icon, with a tiny red dot badge on its top-right
    right : a golden trophy icon
  Each has a small Korean caption underneath.

The two pill buttons must still dominate; the round icons are secondary.
No other UI, no extra text.
```

---

## ② 수집품 보관함 ⭐ 가장 중요

```
A cozy mobile game "collection box" screen mockup, portrait 9:19.5.

STYLE: soft 3D clay-render, miniature toy diorama look. Matte clay materials,
rounded beveled edges, gentle soft shadows. PALETTE: cream and ivory, light
natural beige wood (NOT orange), sage green accents, warm daylight.
Cozy and tactile. NOT pixel art, NOT flat vector, NOT dark.

LAYOUT, top to bottom:
- Header row: a small round cream clay button with a back chevron on the left,
  and a wide cream clay pill holding a short Korean title. Both vertically
  centered in the same row.
- A large rounded panel filling most of the screen: cream clay face with a thick
  light-wood frame and a soft drop shadow.
- A small honey-brown pill at the top of the panel showing "4 / 12".
- Inside the panel: a grid of 3 columns x 4 rows of square slots. Each slot is a
  soft cream clay square with a subtle inset shadow and rounded corners.
    - FOUR slots are FILLED with cute 3D clay objects, each with a soft golden
      glow behind it: a crumpled pajama, yellow rubber gloves, a small potted
      plant, a pair of new white sneakers.
    - The REMAINING slots are EMPTY: a faint grey silhouette of an unknown item
      with a small padlock, dimmed and desaturated.
- A black-and-white tuxedo cat sits at the bottom-right corner, looking up at
  the collection, as a small mascot touch.

Warm, cozy, tactile. No other text.
```

---

## ③ 업적 화면

```
A cozy mobile game "achievements" screen mockup, portrait 9:19.5.

STYLE: soft 3D clay-render, miniature toy diorama look. Matte clay materials,
rounded beveled edges, gentle soft shadows. PALETTE: cream and ivory, light
natural beige wood (NOT orange), sage green accents, warm daylight.
Cozy and tactile. NOT pixel art, NOT flat vector, NOT dark, NOT neon.

LAYOUT, top to bottom:
- Header row: a small round cream clay button with a back chevron on the left,
  and a wide cream clay pill holding a short Korean title, vertically centered
  together.
- A large rounded cream panel with a light-wood frame.
- Inside it, a vertical list of FIVE achievement rows. Each row is a rounded
  cream clay bar containing:
    left   : a circular clay medal icon
    middle : a short Korean achievement name, with a thin rounded progress bar
             underneath (sage green fill)
    right  : a small golden star, or a padlock
- The TOP TWO rows are UNLOCKED: gold medal, full progress bar, warm golden glow.
- The BOTTOM THREE are LOCKED: grey medal, partially filled bar, dimmed.

Warm and tactile, not gamey-neon. No other text.
```

---

## ④ 로고 재생성 — 쓱싹퍼즐

```
A chunky 3D clay game logo of the Korean word "쓱싹퍼즐", on a solid magenta
background.

STYLE: soft matte clay letters with gently beveled rounded edges, warm
wood-brown color with a lighter cream highlight along the top of each letter,
soft ambient shadow. Cute, cozy, tactile — like modeling clay.
Add two or three small clay sparkle marks around the letters (cream and sage).

The four letters sit on one horizontal line with a playful, slightly bouncy
baseline.

CRITICAL SPELLING: the text must read EXACTLY "쓱싹퍼즐" — four syllable blocks
in this order: 쓱 / 싹 / 퍼 / 즐. The first two syllables begin with the DOUBLE
consonant ㅆ (ssang-siot), not a single ㅅ. Render the Hangul clearly and correctly.

BACKGROUND: a single flat solid magenta (#FF00FF) background, nothing else.

STRICTLY NO other text, NO English, NO border frame, NO shadows cast on the
background.
```

---

## ✅ 받은 뒤 확인할 것

- **로고**: 첫 두 글자가 **ㅆ(쌍시옷)** 인지 — `쓱싹` ⭕ / `슥삭`·`쑥싹` ❌
- **보관함**: 빈 칸이 흐릿한 잠금 상태로 구분되는지
- 셋 다 **크림 / 라이트우드 / 세이지** 팔레트가 게임과 맞는지

## 📎 전달 방법

zip으로 압축해 첨부해 주세요. ②번(보관함)이 우선순위 1위 —
해금 아이템 4종(구겨진 잠옷·노란 고무장갑·작은 화분·새 운동화)이
이미 `stages.json`에 들어 있어서 목업만 나오면 바로 구현 가능합니다.
