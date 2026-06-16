// 실제 js/game.js 를 최소 DOM 목킹으로 구동해 로직을 검증.
// solutions.json 해답을 그대로 재생 → 클리어 상태가 되는지 확인.
import fs from 'node:fs';

// ---- 최소 브라우저 환경 목킹 ----
const noop = () => {};
const ctxStub = new Proxy({}, { get: () => noop });
globalThis.performance = globalThis.performance || { now: () => Date.now() };
globalThis.requestAnimationFrame = noop;            // 렌더 루프는 돌리지 않음
globalThis.window = { AudioContext: null, webkitAudioContext: null, addEventListener: noop };
globalThis.Image = class { set src(_) {} };
function makeCanvas() {
  return {
    width: 0, height: 0,
    getContext: () => ctxStub,
    addEventListener: noop,
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 216, height: 384 }),
  };
}

const { Game } = await import('../js/game.js');
const stages = JSON.parse(fs.readFileSync(new URL('../stages/stages.json', import.meta.url)));
const sols = JSON.parse(fs.readFileSync(new URL('../stages/solutions.json', import.meta.url)));

let pass = 0, fail = 0;
for (const st of stages) {
  const g = new Game(makeCanvas(), {});
  g.loadStage(st);
  const sol = sols[String(st.id)];
  if (!sol) { console.log(`#${st.id} 해답 없음`); fail++; continue; }
  for (const dir of sol) {
    g.hero.moving = false; g.hero.t = 1;   // 트윈 즉시 완료 처리
    g.tryMove(dir);
  }
  const ok = g.state === 'clear' && g.remainingDirt() === 0;
  console.log(`${ok ? '✓' : '✗'} #${st.id} ${st.theme}: state=${g.state}, 남은때=${g.remainingDirt()}`);
  ok ? pass++ : fail++;
}
console.log(`\n결과: ${pass} 통과 / ${fail} 실패`);
process.exit(fail ? 1 : 0);
