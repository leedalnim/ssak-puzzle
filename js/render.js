// 방 씬 렌더러 — 배경 + 원근 보드 + 타일/장애물/캐릭터.
//
// 렌더링 규칙 (CONCEPT.md 6.9):
//   1. 보드는 평면에서 통짜로 조립한 뒤 **한 번만** 원근 변형한다.
//      타일을 개별로 변형하면 이음새가 어긋난다.
//   2. 오브젝트는 변형하지 않는다. 밑면을 셀 중앙보다 살짝 아래에 놓고 세운다.
//      (바운딩박스 중앙 정렬이면 공중에 뜬 것처럼 보임)
//   3. 그림자는 오브젝트 접지 그림자만. 타일별 AO는 넣지 않는다.
import { IMG } from './assets.js';

export const VW = 1024, VH = 1536;                 // 배경 원본 해상도 = 캔버스 좌표계

// 보드 사다리꼴 (배경 기준 실측값)
const TOPW = 680, BOTW = 760, Y0 = 556, Y1 = 1256;
const CX = VW / 2;
const QUAD = [
  [CX - TOPW / 2, Y0], [CX + TOPW / 2, Y0],
  [CX + BOTW / 2, Y1], [CX - BOTW / 2, Y1],
];

const BOARD_PX = 1400;                             // 평면 보드 조립 해상도
const FRAME = Math.round(BOARD_PX * 0.040);        // 나무 프레임 두께
const GAP_R = 0.0028;                              // 타일 간격 비율

// ---------------------------------------------------------------- 호모그래피
function solveHomography(src, dst) {
  const A = [], b = [];
  for (let i = 0; i < 4; i++) {
    const [x, y] = src[i], [u, v] = dst[i];
    A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.push(u);
    A.push([0, 0, 0, x, y, 1, -v * x, -v * y]); b.push(v);
  }
  // 가우스 소거법 (8x8)
  const n = 8;
  for (let i = 0; i < n; i++) {
    let p = i;
    for (let r = i + 1; r < n; r++) if (Math.abs(A[r][i]) > Math.abs(A[p][i])) p = r;
    [A[i], A[p]] = [A[p], A[i]]; [b[i], b[p]] = [b[p], b[i]];
    const d = A[i][i];
    for (let c = i; c < n; c++) A[i][c] /= d;
    b[i] /= d;
    for (let r = 0; r < n; r++) {
      if (r === i) continue;
      const f = A[r][i];
      if (!f) continue;
      for (let c = i; c < n; c++) A[r][c] -= f * A[i][c];
      b[r] -= f * b[i];
    }
  }
  return [b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], 1];
}

const H = solveHomography([[0, 0], [1, 0], [1, 1], [0, 1]], QUAD);

/** 보드 정규좌표(u,v ∈ 0..1) → 화면 좌표 */
export function project(u, v) {
  const w = H[6] * u + H[7] * v + H[8];
  return [(H[0] * u + H[1] * v + H[2]) / w, (H[3] * u + H[4] * v + H[5]) / w];
}

/** 화면 y → 보드 v (중앙선 기준 역변환). 스캔라인 워프에 사용 */
function inverseV(y) {
  // u=0.5 고정: y = (A + B v) / (C + D v)
  const A = H[3] * 0.5 + H[5], B = H[4];
  const C = H[6] * 0.5 + H[8], D = H[7];
  return (y * C - A) / (B - y * D);
}

// ---------------------------------------------------------------- 보드 조립
function boardMetrics(cols, rows) {
  const inner = BOARD_PX - FRAME * 2;
  const gap = Math.max(1, Math.round(inner * GAP_R));
  const cw = Math.floor((inner - gap * (cols - 1)) / cols);
  const ch = Math.floor((inner - gap * (rows - 1)) / rows);
  return {
    gap, cw, ch,
    bw: FRAME * 2 + cw * cols + gap * (cols - 1),
    bh: FRAME * 2 + ch * rows + gap * (rows - 1),
  };
}

/** 셀 → 보드 정규좌표 사각형 */
export function cellUV(c, r, cols, rows) {
  const { gap, cw, ch, bw, bh } = boardMetrics(cols, rows);
  return [
    (FRAME + c * (cw + gap)) / bw, (FRAME + r * (ch + gap)) / bh,
    (FRAME + c * (cw + gap) + cw) / bw, (FRAME + r * (ch + gap) + ch) / bh,
  ];
}

/** 셀 중심의 화면 좌표와 셀 높이 */
export function cellCenter(c, r, cols, rows) {
  const [u0, v0, u1, v1] = cellUV(c, r, cols, rows);
  const um = (u0 + u1) / 2;
  const [x, y] = project(um, (v0 + v1) / 2);
  return { x, y, cellH: project(um, v1)[1] - project(um, v0)[1] };
}

/** 화면 좌표 → 셀 (없으면 null) */
export function hitCell(px, py, cols, rows) {
  const v = inverseV(py);
  if (v < 0 || v > 1) return null;
  const [xl] = project(0, v), [xr] = project(1, v);
  const u = (px - xl) / (xr - xl);
  if (u < 0 || u > 1) return null;
  const { gap, cw, ch, bw, bh } = boardMetrics(cols, rows);
  const bx = u * bw - FRAME, by = v * bh - FRAME;
  const c = Math.floor(bx / (cw + gap)), r = Math.floor(by / (ch + gap));
  if (c < 0 || r < 0 || c >= cols || r >= rows) return null;
  return { c, r };
}

/** 평면 보드(나무 프레임 + 타일 격자)를 오프스크린에 그린다 */
function drawFlatBoard(dur, hole, cols, rows) {
  const { gap, cw, ch, bw, bh } = boardMetrics(cols, rows);
  const cv = document.createElement('canvas');
  cv.width = bw; cv.height = bh;
  const g = cv.getContext('2d');
  const rad = FRAME * 0.85;

  roundRect(g, 0, 0, bw, bh, rad); g.fillStyle = '#c69a64'; g.fill();
  g.strokeStyle = 'rgba(176,132,82,.35)'; g.lineWidth = 1;   // 나무 결
  for (let y = 4; y < bh - 4; y += Math.max(7, FRAME / 5)) {
    g.beginPath(); g.moveTo(4, y); g.lineTo(bw - 4, y); g.stroke();
  }
  for (let i = 0; i < FRAME; i++) {                          // 베벨
    const t = i / FRAME;
    g.strokeStyle = `rgba(${226 - 66 * t | 0},${190 - 68 * t | 0},${138 - 60 * t | 0},.75)`;
    roundRect(g, i, i, bw - i * 2, bh - i * 2, Math.max(2, rad - i)); g.stroke();
  }
  g.lineWidth = 4; g.strokeStyle = 'rgba(240,214,172,.8)';
  roundRect(g, 2, 2, bw - 4, bh - 4, rad); g.stroke();
  g.lineWidth = 5; g.strokeStyle = '#8a643c';
  roundRect(g, 0, 0, bw, bh, rad); g.stroke();

  g.save();                                                  // 안쪽 AO
  g.shadowColor = 'rgba(96,68,40,.75)'; g.shadowBlur = 22;
  g.lineWidth = 14; g.strokeStyle = 'rgba(96,68,40,.55)';
  roundRect(g, FRAME - 5, FRAME - 5, bw - (FRAME - 5) * 2, bh - (FRAME - 5) * 2, 14);
  g.stroke(); g.restore();

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (hole?.[r]?.[c]) continue;          // 보드에 뚫린 칸만 비움
      // 장애물 칸도 바닥 타일은 그린다 (장애물은 타일 '위에' 놓인 물건)
      const img = IMG['tile' + Math.min(5, dur[r][c])];
      if (img) g.drawImage(img, FRAME + c * (cw + gap), FRAME + r * (ch + gap), cw, ch);
    }
  }
  return cv;
}

function roundRect(g, x, y, w, h, r) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

/**
 * 평면 보드를 사다리꼴로 워프. 스캔라인마다 원본 행을 가로로 늘려 그린다.
 * 결과를 캐시해 매 프레임 재계산하지 않는다.
 */
function warpBoard(flat) {
  const cv = document.createElement('canvas');
  cv.width = VW; cv.height = VH;
  const g = cv.getContext('2d');
  const yTop = Math.floor(Y0), yBot = Math.ceil(Y1);
  for (let y = yTop; y <= yBot; y++) {
    const v = inverseV(y + 0.5);
    if (v < 0 || v > 1) continue;
    const sy = Math.min(flat.height - 1, Math.max(0, v * flat.height));
    const [xl] = project(0, v), [xr] = project(1, v);
    g.drawImage(flat, 0, sy, flat.width, 1, xl, y, xr - xl, 1.02);
  }
  return cv;
}

let cache = { key: '', canvas: null };

/** 보드 캔버스(캐시). 그리드 상태가 바뀌면 자동 재생성 */
export function boardCanvas(dur, hole, cols, rows) {
  const key = cols + 'x' + rows + ':' + dur.map(r => r.join('')).join('|');
  if (cache.key !== key) {
    cache = { key, canvas: warpBoard(drawFlatBoard(dur, hole, cols, rows)) };
  }
  return cache.canvas;
}

export function invalidateBoard() { cache.key = ''; }

// ---------------------------------------------------------------- 그림자
// 스프라이트의 **실제 밑면**을 픽셀에서 재서 그림자를 만든다.
// 타입별 상수(둥근 화분 / 네모 상자 …)로 모양을 가정하면 반드시 어긋난다.
const fpCache = new WeakMap();

/** 이미지 하단부의 불투명 영역 → 접지면 중심/폭 (스프라이트 폭 대비 0~1) */
function footprint(img) {
  const hit = fpCache.get(img);
  if (hit) return hit;
  const S = 72;
  const cv = document.createElement('canvas');
  cv.width = S; cv.height = S;
  const g = cv.getContext('2d', { willReadFrequently: true });
  g.drawImage(img, 0, 0, S, S);
  const data = g.getImageData(0, 0, S, S).data;
  let minX = S, maxX = -1;
  // 하단 26% — 구간이 좁으면 캐릭터의 대걸레만 잡혀 그림자가 발에서 벗어난다
  for (let y = Math.floor(S * 0.74); y < S; y++) {
    for (let x = 0; x < S; x++) {
      if (data[(y * S + x) * 4 + 3] > 70) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
      }
    }
  }
  const fp = maxX >= minX
    // 접지면이 지나치게 좁게 잡히면(가는 다리·막대 등) 그림자가 빈약해 보인다
    ? { cx: (minX + maxX + 1) / 2 / S, w: Math.max((maxX - minX + 1) / S, 0.42) }
    : { cx: 0.5, w: 0.6 };
  fpCache.set(img, fp);
  return fp;
}

/**
 * 접지 그림자 — 밑면 폭에 맞춘 둥근 타원.
 * 카메라가 거의 위에서 내려다보므로 그림자는 오브젝트 **바로 밑**에 와야 한다.
 * 아래로 내려 그리거나 납작하게 늘이면 물체가 떠 보인다.
 */
function contactShadow(ctx, cx, baseY, footW) {
  const rx = footW * 0.62;
  const ry = rx * 0.46;                        // 슬라이버가 아니라 둥글게
  // 중심을 바닥선보다 아주 조금만 올린다.
  //  - 너무 내리면 그림자가 오브젝트 아래로 떨어져 보이고,
  //  - 너무 올리면 오브젝트 뒤에 완전히 가려 발밑에 아무것도 안 보인다.
  const cy = baseY - ry * 0.18;
  const draw = (s, a, blur) => {
    ctx.save();
    ctx.filter = `blur(${blur}px)`;
    ctx.fillStyle = `rgba(74,54,36,${a})`;
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx * s, ry * s, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  };
  draw(1.34, 0.10, ry * 0.95);                 // 넓고 아주 옅은 확산
  draw(0.94, 0.22, ry * 0.26);                 // 밑면에 붙는 코어
}

/** 스프라이트 밑면에 맞춘 접지 그림자 (캐릭터 등 외부에서도 사용) */
export function drawContactShadow(ctx, img, spriteLeft, spriteW, baseY) {
  const fp = footprint(img);
  contactShadow(ctx, spriteLeft + fp.cx * spriteW, baseY, fp.w * spriteW);
}

/** 오브젝트를 셀에 세운다 — 밑면이 셀 중앙보다 살짝 아래 */
export function drawObject(ctx, img, c, r, cols, rows, scale, _key, baseOff = 0.10) {
  if (!img) return;
  const { x, y, cellH } = cellCenter(c, r, cols, rows);
  const h = cellH * scale, w = img.width * h / img.height;
  const baseY = y + cellH * baseOff;
  drawContactShadow(ctx, img, x - w / 2, w, baseY);
  ctx.drawImage(img, x - w / 2, baseY - h, w, h);
}

/** 보드 전체 드롭섀도우 */
export function drawBoardShadow(ctx) {
  ctx.save();
  ctx.filter = 'blur(22px)';
  ctx.fillStyle = 'rgba(88,66,44,.30)';
  for (const off of [26, 16, 8]) {
    ctx.beginPath();
    ctx.moveTo(QUAD[0][0], QUAD[0][1] + off);
    for (let i = 1; i < 4; i++) ctx.lineTo(QUAD[i][0], QUAD[i][1] + off);
    ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}
