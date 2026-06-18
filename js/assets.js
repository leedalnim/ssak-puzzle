// 에셋 로더 — PNG 스프라이트를 미리 로드해 캐시한다.
const H = 'assets/home/';
const MANIFEST = {
  // 집청소 테마 — 코지룸 배경 + 가구 소품으로 구성
  store_bg: H + 'room_bg.png',
  obstacle_plant: H + 'furn_plant.png',
  obstacle_boxes: H + 'prop_23.png',
  hint_panel: 'assets/hint_panel.png',
  // 캐릭터: 앞=down, 뒤=up, 좌=side(우측은 좌우반전), 각 3프레임(쪼그려 청소)
  char_down_0: H + 'char_front_0.png', char_down_1: H + 'char_front_1.png', char_down_2: H + 'char_front_2.png',
  char_side_0: H + 'char_left_0.png',  char_side_1: H + 'char_left_1.png',  char_side_2: H + 'char_left_2.png',
  char_up_0:   H + 'char_back_0.png',   char_up_1:   H + 'char_back_1.png',   char_up_2:   H + 'char_back_2.png',
  // 바닥 타일: 0=깨끗(완료), 1~5=더러움 단계
  tile0: H + 'tile_clean.png',
  tile1: H + 'tile_d1.png',
  tile2: H + 'tile_d2.png',
  tile3: H + 'tile_d3.png',
  tile4: H + 'tile_d4.png',
  tile5: H + 'tile_d5.png',
  // 청소 이펙트 스프라이트(반짝임/완료별/먼지)
  fx_sparkle_0: H + 'fx_sparkle_0.png', fx_sparkle_1: H + 'fx_sparkle_1.png', fx_sparkle_2: H + 'fx_sparkle_2.png', fx_sparkle_3: H + 'fx_sparkle_3.png',
  fx_clean_0: H + 'fx_clean_0.png', fx_clean_1: H + 'fx_clean_1.png', fx_clean_2: H + 'fx_clean_2.png', fx_clean_3: H + 'fx_clean_3.png',
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
  const entries = Object.entries(MANIFEST);
  await Promise.all(entries.map(async ([key, src]) => {
    IMG[key] = await loadImage(src);
  }));
  return IMG;
}

export function tileImg(dur) {
  return IMG['tile' + dur];
}
