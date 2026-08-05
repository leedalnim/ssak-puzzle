// 에셋 로더 — 배경/타일/캐릭터/장애물/UI 스프라이트를 미리 로드해 캐시한다.
const R = 'assets/room/';

const MANIFEST = {
  // 배경 (장소별) — 가운데 바닥이 비어 있는 통짜 이미지
  bg_studio: R + 'bg_studio_tall.webp',

  // 바닥 타일: 0=깨끗, 1~5=더러움 단계
  tile0: R + 'tiles/tile_0.png', tile1: R + 'tiles/tile_1.png', tile2: R + 'tiles/tile_2.png',
  tile3: R + 'tiles/tile_3.png', tile4: R + 'tiles/tile_4.png', tile5: R + 'tiles/tile_5.png',

  // 캐릭터: 4방향 × 3프레임 (right는 left 좌우반전본이 파일로 존재)
  char_down_0: R + 'char/char_down_0.png', char_down_1: R + 'char/char_down_1.png', char_down_2: R + 'char/char_down_2.png',
  char_up_0: R + 'char/char_up_0.png', char_up_1: R + 'char/char_up_1.png', char_up_2: R + 'char/char_up_2.png',
  // 측면은 **오른쪽을 보는 3포즈**만 둔다(왼쪽은 코드에서 좌우 반전).
  // 원본 시트의 char_left_*/char_right_* 는 서로 완전한 거울상이라 절반이 중복이었다.
  char_side_0: R + 'char/char_side_0.png',   // 직립(정지)
  char_side_1: R + 'char/char_side_1.png',   // 성큼 A(걷기)
  char_side_2: R + 'char/char_side_2.png',   // 성큼 B(걷기)

  // 장애물
  obs_boxes: R + 'obstacles/obs_boxes.png',
  obs_plant: R + 'obstacles/obs_plant.png',
  obs_basket_rd: R + 'obstacles/obs_basket_rd.png',
  obs_books: R + 'obstacles/obs_books.png',
  obs_stool: R + 'obstacles/obs_stool.png',

  // 바닥에 떨어진 수집품 — 키가 stages.json 의 item.name 과 같아야 한다
  'item_구겨진 잠옷': R + 'ui/kit/it_pajama.png',
  'item_노란 고무장갑': R + 'ui/kit/it_gloves.png',
  'item_작은 화분': R + 'ui/kit/it_plant.png',
  'item_새 운동화': R + 'ui/kit/it_sneakers.png',
  'item_머그컵': R + 'ui/kit/it_mug.png',
  'item_탁상 램프': R + 'ui/kit/it_lamp.png',
  'item_분무기': R + 'ui/kit/it_spray.png',
  'item_물뿌리개': R + 'ui/kit/it_can.png',
  'item_티슈 상자': R + 'ui/kit/it_tissue.png',
  'item_쿠션': R + 'ui/kit/it_cushion.png',
  'item_장바구니': R + 'ui/kit/it_basket.png',   // 모두 무손실 원본 컷
};

// 칸마다 **고르게 보이도록** 맞춘 표시 배율.
// 긴 변만 칸에 맞추면(예전 방식) 납작한 머그컵·티슈는 커 보이고 길쭉한 분무기·램프는
// 작아 보인다. 사람 눈은 '차지하는 면적'으로 크기를 느끼므로,
//   배율 ∝ 긴변 / √(가로×세로)
// 로 계산해 **보이는 면적**을 11종이 같게 맞췄다(원본 에셋은 그대로, 표시 크기만).
// 다만 세로로 길쭉한 물건은 면적이 같아도 '키'가 커서 혼자 튀어 보인다.
// → 계산값을 기본으로 두되 분무기·램프·물뿌리개는 눈으로 보고 더 낮췄다(주석에 계산값 표기).
// 계산값은 tools/calc_item_scale.py 로 다시 뽑을 수 있다.
// 수집함·HUD·클리어 팝업·바닥 렌더가 모두 이 값을 쓴다.
export const ITEM_SCALE = {
  '구겨진 잠옷': 0.99,
  '머그컵': 0.92,
  '티슈 상자': 0.94,
  '노란 고무장갑': 0.99,
  '분무기': 0.88,     // ↓ 계산값 1.14 — 세로로 길어 혼자 우뚝해 보여 손으로 낮춤
  '쿠션': 0.97,
  '탁상 램프': 0.94,  // ↓ 계산값 1.08 — 위와 같은 이유
  '작은 화분': 1.00,
  '물뿌리개': 1.02,   // ↓ 계산값 1.09 — 가로로 길어 살짝 넓어 보여 조금 낮춤
  '장바구니': 0.92,
  '새 운동화': 0.96,
};
export const itemScale = (name) => ITEM_SCALE[name] || 1;

export const IMG = {};

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('이미지 로드 실패: ' + src));
    img.src = src;
  });
}

export async function loadAssets() {
  await Promise.all(Object.entries(MANIFEST).map(async ([key, src]) => {
    IMG[key] = await loadImage(src);
  }));
  return IMG;
}
