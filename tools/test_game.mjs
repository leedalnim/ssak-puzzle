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
  // 실제 게임은 js/main.js 가 자리(spots) 중 필요한 만큼만 골라 넣는다.
  // 여기서는 **모든 자리**에 조각을 놓고, 하나도 안 놓치는지 본다.
  g.loadStage({ ...st, items: (st.spots || []).map((sp, k) => ({ ...sp, name: '조각' + k })) });
  const sol = sols[String(st.id)];
  if (!sol) { console.log(`#${st.id} 해답 없음`); fail++; continue; }
  // solutions.json 은 '밟는 칸 좌표'의 나열이라 이웃 간 차이를 방향으로 바꿔 재생한다
  for (let i = 1; i < sol.length; i++) {
    const [px, py] = sol[i - 1], [x, y] = sol[i];
    g.hero.moving = false; g.hero.t = 1;   // 트윈 즉시 완료 처리
    g.tryMove(x > px ? 'right' : x < px ? 'left' : y > py ? 'down' : 'up');
  }
  // 클리어 + **조각을 하나도 놓치지 않았는지**까지 본다.
  // 한붓그리기라 모든 칸을 밟으므로 원래 놓칠 수 없지만, 배치가 벽 위로 가면 깨진다.
  const missed = g.items.filter(it => !it.got).map(it => it.name);
  const ok = g.state === 'clear' && g.remainingDirt() === 0 && !missed.length;
  console.log(`${ok ? '✓' : '✗'} #${st.id} ${st.theme}: state=${g.state}, 남은때=${g.remainingDirt()}`
    + `, 조각 ${g.items.length - missed.length}/${g.items.length}${missed.length ? ' ← 못 주움: ' + missed : ''}`);
  ok ? pass++ : fail++;
}
console.log(`\n결과: ${pass} 통과 / ${fail} 실패`);
process.exit(fail ? 1 : 0);
