// 입력 — WASD/방향키 + 스와이프 + 인접 타일 터치.
// 모바일 스크롤/줌 방지를 위해 모든 터치 기본동작 차단(touch-action:none + preventDefault).

const DIRS = {
  up: { x: 0, y: -1 }, down: { x: 0, y: 1 },
  left: { x: -1, y: 0 }, right: { x: 1, y: 0 },
};

export function initInput(canvas, { onMove, onTap }) {
  // ----- 키보드 -----
  window.addEventListener('keydown', (e) => {
    let dir = null;
    switch (e.key) {
      case 'ArrowUp': case 'w': case 'W': case 'ㅈ': dir = 'up'; break;
      case 'ArrowDown': case 's': case 'S': case 'ㄴ': dir = 'down'; break;
      case 'ArrowLeft': case 'a': case 'A': case 'ㅁ': dir = 'left'; break;
      case 'ArrowRight': case 'd': case 'D': case 'ㅇ': dir = 'right'; break;
    }
    if (dir) { e.preventDefault(); onMove(dir, DIRS[dir]); }
  });

  // ----- 터치/스와이프 -----
  let sx = 0, sy = 0, st = 0, moved = false, active = false;
  const SWIPE_MIN = 22;   // px: 이 이상 움직이면 스와이프
  const TAP_MAX = 14;     // px: 이 이하면 탭

  function rel(touch) {
    const r = canvas.getBoundingClientRect();
    return {
      x: (touch.clientX - r.left) * (canvas.width / r.width),
      y: (touch.clientY - r.top) * (canvas.height / r.height),
    };
  }

  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    const t = e.changedTouches[0];
    sx = t.clientX; sy = t.clientY; st = performance.now();
    moved = false; active = true;
  }, { passive: false });

  canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    if (!active) return;
    const t = e.changedTouches[0];
    const dx = t.clientX - sx, dy = t.clientY - sy;
    if (!moved && Math.hypot(dx, dy) >= SWIPE_MIN) {
      moved = true;
      const dir = Math.abs(dx) > Math.abs(dy)
        ? (dx > 0 ? 'right' : 'left')
        : (dy > 0 ? 'down' : 'up');
      onMove(dir, DIRS[dir]);
      active = false; // 한 스와이프 = 한 이동
    }
  }, { passive: false });

  canvas.addEventListener('touchend', (e) => {
    e.preventDefault();
    if (!active) return;
    active = false;
    const t = e.changedTouches[0];
    const dx = t.clientX - sx, dy = t.clientY - sy;
    if (Math.hypot(dx, dy) <= TAP_MAX) {
      const p = rel(t);
      onTap(p.x, p.y);
    }
  }, { passive: false });

  // 마우스(데스크톱 테스트용) — 클릭=탭
  canvas.addEventListener('mousedown', (e) => {
    const r = canvas.getBoundingClientRect();
    const x = (e.clientX - r.left) * (canvas.width / r.width);
    const y = (e.clientY - r.top) * (canvas.height / r.height);
    onTap(x, y);
  });
}

export { DIRS };
