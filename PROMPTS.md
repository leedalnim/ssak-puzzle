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
