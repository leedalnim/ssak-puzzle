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
};

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
