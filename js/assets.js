// 에셋 로더 — PNG 스프라이트를 미리 로드해 캐시한다.
const MANIFEST = {
  // 편의점 테마(달님 제작 에셋)
  store_bg: 'assets/store_bg.png',
  obstacle_plant: 'assets/obstacle_plant.png',
  obstacle_boxes: 'assets/obstacle_boxes.png',
  hint_panel: 'assets/hint_panel.png',
  // 캐릭터: 방향별 idle+걷기 프레임
  char_down_0: 'assets/char_down_0.png', char_down_1: 'assets/char_down_1.png', char_down_2: 'assets/char_down_2.png',
  char_side_0: 'assets/char_side_0.png', char_side_1: 'assets/char_side_1.png', char_side_2: 'assets/char_side_2.png',
  char_up_0: 'assets/char_up_0.png', char_up_1: 'assets/char_up_1.png', char_up_2: 'assets/char_up_2.png',
  // 바닥 타일: 0=깨끗(완료), 1~5=더러움 단계
  tile0: 'assets/tile_clean.png',
  tile1: 'assets/tile_d1.png',
  tile2: 'assets/tile_d2.png',
  tile3: 'assets/tile_d3.png',
  tile4: 'assets/tile_d4.png',
  tile5: 'assets/tile_d5.png',
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
