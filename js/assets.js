// 에셋 로더 — PNG 스프라이트를 미리 로드해 캐시한다.
// 에셋 원본은 tools/gen_assets.py 가 생성한 assets/*.png.

const MANIFEST = {
  hero_idle: 'assets/hero_idle.png',
  hero_walk_a: 'assets/hero_walk_a.png',
  hero_walk_b: 'assets/hero_walk_b.png',
  cat: 'assets/cat.png',
  trashbag: 'assets/trashbag.png',
  plant: 'assets/plant.png',
  window: 'assets/window.png',
  tile0: 'assets/tile_0.png',
  tile1: 'assets/tile_1.png',
  tile2: 'assets/tile_2.png',
  tile3: 'assets/tile_3.png',
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
