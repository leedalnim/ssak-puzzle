// 부트스트랩 + UI 상태기계.
import { loadAssets } from './assets.js';
import { Game } from './game.js';
import * as Audio from './audio.js';
import { Toss } from './toss-sdk.js';

const $ = (id) => document.getElementById(id);
const PROG_KEY = 'ssak_cleared';
const STAR_KEY = 'ssak_stars';
const ST = 'assets/room/ui/stage/';

// 장소(영역) — 자취방만 실제 콘텐츠, 나머지는 곧 공개
const AREAS = [
  { name: '자취방', act: 1, thumb: ST + 'thumb_studio.png' },
  { name: '편의점', coming: true, thumb: ST + 'thumb_store.png' },
  { name: '카페', coming: true },
  { name: '베이커리', coming: true },
];

let stages = [];
let game = null;
let current = 0;
let clearedMax = 0;
let pendingIntro = null;
let areaIdx = 0;
let stars = {};

function loadStars() { try { stars = JSON.parse(localStorage.getItem(STAR_KEY) || '{}'); } catch { stars = {}; } }
function saveStars() { localStorage.setItem(STAR_KEY, JSON.stringify(stars)); }
/** 클리어 시간 대비 별점(1~3). par = 총 걸레질 횟수(격자 합) 기준 */
function starsFor(st, elapsed) {
  const par = st.grid.reduce((a, row) => a + row.reduce((b, v) => b + v, 0), 0) * 0.8;
  if (!elapsed || elapsed <= par * 0.9) return 3;
  if (elapsed <= par * 1.5) return 2;
  return 1;
}

/** 클리어 팝업 — 별을 하나씩 차례로 '탁' 박아 넣는다 */
let starTimers = [];
function playStars(n) {
  starTimers.forEach(clearTimeout); starTimers = [];
  const imgs = [...$('clearStars').children];
  imgs.forEach(el => { el.classList.remove('on'); el.classList.add('off'); });
  imgs.forEach((el, i) => {
    if (i >= n) return;
    starTimers.push(setTimeout(() => {
      el.classList.remove('off'); el.classList.add('on');
      Audio.sfxStar(i);
    }, 260 + i * 300));
  });
}

const screens = ['screenTitle', 'screenStages', 'screenIntro', 'screenClear',
                 'screenFail', 'screenHelp', 'screenPause', 'screenLoad',
                 'screenCollection', 'screenAchieve'];

const KIT = 'assets/room/ui/kit/';

// 수집품 12종 — 앞 4개는 스테이지 해금 아이템(stages.json의 unlock과 이름이 같다),
// 나머지는 아직 준비 중인 실루엣 자리.
const ITEMS = [
  { name: '구겨진 잠옷', img: 'it_pajama' },
  { name: '노란 고무장갑', img: 'it_gloves' },
  { name: '작은 화분', img: 'it_plant' },
  { name: '새 운동화', img: 'it_sneakers' },
  { name: '머그컵', img: 'sil_mug', sil: true },
  { name: '탁상 램프', img: 'sil_lamp', sil: true },
  { name: '분무기', img: 'sil_spray', sil: true },
  { name: '물뿌리개', img: 'sil_can', sil: true },
  { name: '티슈 상자', img: 'sil_tissue', sil: true },
  { name: '유리병', img: 'sil_cushion', sil: true },
  { name: '쿠션', img: 'sil_cushion', sil: true },
  { name: '장바구니', img: 'sil_tote', sil: true },
];

// 도전과제 — progress(cleared, stars)로 진행도를 계산한다
const ACHIEVEMENTS = [
  { name: '첫걸음',     icon: 'ach_sprout', goal: 1,  get: p => p.cleared },
  { name: '반짝 청소',  icon: 'ach_mop',    goal: 5,  get: p => p.cleared },
  { name: '깔끔한 하루', icon: 'ach_bucket', goal: 10, get: p => p.cleared },
  { name: '청소 달인',  icon: 'ach_vacuum', goal: 20, get: p => p.cleared },
  { name: '완벽한 방',  icon: 'ach_shelf',  goal: 10, get: p => p.threeStars },
];

function loadProgress() { clearedMax = parseInt(localStorage.getItem(PROG_KEY) || '0', 10); }
function saveProgress(id) { if (id > clearedMax) { clearedMax = id; localStorage.setItem(PROG_KEY, String(id)); } }

/** id=null 이면 인게임 화면 */
function show(id) {
  screens.forEach(s => $(s).classList.toggle('hidden', s !== id));
  const inGame = id === null || id === 'screenHelp' || id === 'screenPause';
  $('hud').classList.toggle('hidden', !inGame);
  $('toolbar').classList.toggle('hidden', !inGame);
}

function fmtTime(sec) {
  const m = Math.floor(sec / 60), s = Math.floor(sec % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

/** 캔버스 표시 크기에 맞춰 UI 배율(--k)을 맞춘다 */
function syncScale() {
  const k = $('stage').getBoundingClientRect().width / 1024;
  document.documentElement.style.setProperty('--k', k || 1);
}

// ----------------------------- 게임 훅 -----------------------------
function makeGame() {
  game = new Game($('game'), {
    onTiles: (left) => { $('hudTiles').textContent = String(left); },
    onUndoState: (can) => { $('btnUndo').disabled = !can; },
    onTimer: (left, total, elapsed) => {
      const el = $('hudTimer');
      if (total <= 0) {
        // 제한 시간이 없는 판 — 얼마나 걸렸는지 볼 수 있게 경과 시간을 센다
        el.textContent = fmtTime(elapsed);
        el.classList.remove('warn');
        return;
      }
      el.textContent = fmtTime(left);
      el.classList.toggle('warn', left <= 15);
    },
    onClear: ({ elapsed }) => onStageClear(elapsed),
    onFail: ({ reason }) => onStageFail(reason),
  });
}

// ----------------------------- 흐름 -----------------------------
function startStage(idx) {
  current = idx;
  const st = stages[idx];
  Toss.track('stage_start', { stage: st.id });
  if (st.intro) {
    pendingIntro = idx;
    $('introTitle').textContent = st.theme;
    $('introText').textContent = st.intro;
    show('screenIntro');
  } else {
    beginStage(idx);
  }
}

function beginStage(idx) {
  show(null);
  syncScale();
  game.loadStage(stages[idx]);
}

function onStageClear(elapsed) {
  const st = stages[current];
  saveProgress(st.id);
  const s = starsFor(st, elapsed);
  if (s > (stars[st.id] || 0)) { stars[st.id] = s; saveStars(); }
  Toss.track('stage_clear', { stage: st.id, elapsed, stars: s });
  $('clearStory').textContent = st.clear || '';
  playStars(s);
  $('btnNext').textContent = current + 1 < stages.length ? '다음 스테이지' : '처음으로';
  refreshBadges();
  show('screenClear');
}

function onStageFail(reason) {
  Toss.track('stage_fail', { stage: stages[current].id, reason });
  $('failReason').textContent = reason === 'time'
    ? '시간이 다 됐어요.\n조금만 더 빠르게!'
    : '갈 곳이 없어요.\n처음부터 다시 해볼까요?';
  show('screenFail');
}

function nextUnclearedIndex() {
  const i = stages.findIndex(s => s.id > clearedMax);
  return i < 0 ? 0 : i;
}

// ----------------------------- 스테이지 선택 (페이저) -----------------------------
function el(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}

/** 한 영역(자취방)의 레벨 그리드 페이지 */
function areaPage(area) {
  const page = el('div', 'area-page');
  const header = el('div', 'area-header');
  if (area.thumb) header.appendChild(el('img')).src = area.thumb;
  const list = stages.filter(s => s.act === area.act);
  const clearedCount = list.filter(s => s.id <= clearedMax).length;
  header.appendChild(el('div', 'area-name', area.name));
  header.appendChild(el('div', 'area-progress', `${clearedCount} / ${list.length}`));
  page.appendChild(header);

  const panel = el('div', 'level-panel');
  const grid = el('div', 'level-grid');
  list.forEach(st => {
    const idx = stages.indexOf(st);
    const locked = st.id > clearedMax + 1;
    const cleared = st.id <= clearedMax;
    const state = cleared ? 'clear' : (locked ? 'lock' : 'cur');
    const cell = el('button', `lvl ${state}`);
    let inner = `<span class="n">${st.sub ?? st.id}</span>`;
    if (cleared) {
      const n = stars[st.id] || 1;
      inner += `<span class="stars">${`<img src="${ST}star.png">`.repeat(n)}</span>`;
    } else if (locked) {
      inner += `<img class="lk" src="${ST}lock.png">`;
    }
    cell.innerHTML = inner;
    if (!locked) cell.addEventListener('click', () => { Audio.sfxUI(); startStage(idx); });
    grid.appendChild(cell);
  });
  panel.appendChild(grid);
  page.appendChild(panel);
  return page;
}

/** 곧 공개 영역 페이지 */
function comingPage(area) {
  const page = el('div', 'area-page');
  const box = el('div', 'coming');
  if (area.thumb) box.appendChild(el('img')).src = area.thumb;
  const inner = el('div', 'cm-in');
  const lk = el('img', 'cm-lock'); lk.src = ST + 'lock.png';
  inner.appendChild(lk);
  inner.appendChild(el('div', 'cm-txt', `${area.name} · 준비 중`));
  box.appendChild(inner);
  page.appendChild(box);
  return page;
}

function goArea(i) {
  areaIdx = Math.max(0, Math.min(AREAS.length - 1, i));
  $('areaTrack').style.transform = `translateX(${-areaIdx * 100}%)`;
  [...$('pgDots').children].forEach((d, k) => d.classList.toggle('on', k === areaIdx));
  $('pgPrev').disabled = areaIdx === 0;
  $('pgNext').disabled = areaIdx === AREAS.length - 1;
}

function buildStages() {
  const track = $('areaTrack');
  track.innerHTML = '';
  AREAS.forEach(a => track.appendChild(a.coming ? comingPage(a) : areaPage(a)));
  const dots = $('pgDots');
  dots.innerHTML = '';
  AREAS.forEach(() => dots.appendChild(el('span')));
  // 진행 중인(첫 미클리어) 영역으로 시작
  const cur = stages.find(s => s.id > clearedMax);
  const startArea = cur ? AREAS.findIndex(a => a.act === cur.act) : 0;
  goArea(startArea < 0 ? 0 : startArea);
}

// ----------------------------- 수집함 · 도전과제 -----------------------------
/** 지금까지 얻은 수집품 수 = 클리어한 스테이지의 unlock 개수 */
function ownedCount() {
  return stages.filter(s => s.id <= clearedMax && s.unlock).length;
}
function progressSummary() {
  return {
    cleared: clearedMax,
    threeStars: Object.values(stars).filter(v => v >= 3).length,
  };
}

function buildCollection() {
  const owned = ownedCount();
  $('collCount').textContent = `${owned} / ${ITEMS.length}`;
  const grid = $('collGrid');
  grid.innerHTML = '';
  ITEMS.forEach((it, i) => {
    const got = i < owned;                       // 앞에서부터 순서대로 해금
    const cell = el('div', 'slot ' + (got ? 'got' : 'lock'));
    cell.innerHTML = `<img class="thing" src="${KIT}${it.img}.png" alt="${it.name}">`
      + (got ? '' : `<img class="pad" src="${KIT}lock_item.png" alt="">`);
    cell.title = got ? it.name : '아직 못 얻었어요';
    grid.appendChild(cell);
  });
}

function buildAchievements() {
  const p = progressSummary();
  const list = $('achList');
  list.innerHTML = '';
  ACHIEVEMENTS.forEach(a => {
    const cur = Math.min(a.get(p), a.goal);
    const done = cur >= a.goal;
    // 과제 아이콘 에셋이 이미 '메달' 형태라 그대로 쓰고, 잠금 상태만 CSS로 흐리게 한다
    const row = el('div', 'ach-row ' + (done ? 'done' : 'lock'));
    row.innerHTML =
      `<img class="ach-medal" src="${KIT}${a.icon}.png" alt="">`
      + `<div class="ach-mid"><div class="ach-name">${a.name}</div>`
      + `<div class="ach-bar"><i style="width:${Math.round(cur / a.goal * 100)}%"></i></div></div>`
      + `<img class="ach-st" src="${KIT}${done ? 'st_star' : 'st_lock'}.png" alt="">`;
    list.appendChild(row);
  });
}

/** 새로 얻은 게 있으면 타이틀 아이콘에 빨간 점 */
function refreshBadges() {
  const seenItems = parseInt(localStorage.getItem('ssak_seen_items') || '0', 10);
  $('badgeCollection').classList.toggle('hidden', ownedCount() <= seenItems);
  const p = progressSummary();
  const doneNow = ACHIEVEMENTS.filter(a => a.get(p) >= a.goal).length;
  const seenAch = parseInt(localStorage.getItem('ssak_seen_ach') || '0', 10);
  $('badgeAchieve').classList.toggle('hidden', doneNow <= seenAch);
}

// ----------------------------- 도움말 범례 -----------------------------
function buildLegend() {
  const el = $('legend');
  if (el.childElementCount) return;
  const labels = ['깨끗', '1번', '2번', '3번', '4번', '5번'];
  el.innerHTML = labels.map((t, i) =>
    `<div class="legend-item"><img src="assets/room/tiles/tile_${i}.png" alt=""><span>${t}</span></div>`
  ).join('');
}

// ----------------------------- 버튼 배선 -----------------------------
function wireUI() {
  $('btnStart').addEventListener('click', () => {
    Audio.unlockAudio(); Audio.sfxUI(); startStage(nextUnclearedIndex());
  });
  $('btnStages').addEventListener('click', () => { Audio.sfxUI(); buildStages(); show('screenStages'); });
  // 클리어/실패/일시정지의 '스테이지 목록' → 스테이지 화면으로
  document.querySelectorAll('[data-back]').forEach(b =>
    b.addEventListener('click', () => { Audio.sfxUI(); buildStages(); show('screenStages'); }));
  // 스테이지 화면의 '뒤로' → 타이틀로
  $('btnStagesBack').addEventListener('click', () => { Audio.sfxUI(); show('screenTitle'); });
  // 영역 페이저
  $('pgPrev').addEventListener('click', () => { Audio.sfxUI(); goArea(areaIdx - 1); });
  $('pgNext').addEventListener('click', () => { Audio.sfxUI(); goArea(areaIdx + 1); });

  // 수집함 · 도전과제
  $('btnCollection').addEventListener('click', () => {
    Audio.sfxUI(); buildCollection();
    localStorage.setItem('ssak_seen_items', String(ownedCount()));   // 확인했으니 뱃지 해제
    show('screenCollection');
  });
  $('btnAchieve').addEventListener('click', () => {
    Audio.sfxUI(); buildAchievements();
    const p = progressSummary();
    localStorage.setItem('ssak_seen_ach',
      String(ACHIEVEMENTS.filter(a => a.get(p) >= a.goal).length));
    show('screenAchieve');
  });
  $('btnCollBack').addEventListener('click', () => { Audio.sfxUI(); refreshBadges(); show('screenTitle'); });
  $('btnAchBack').addEventListener('click', () => { Audio.sfxUI(); refreshBadges(); show('screenTitle'); });

  $('btnIntroNext').addEventListener('click', () => {
    Audio.sfxUI(); if (pendingIntro != null) beginStage(pendingIntro);
  });

  $('btnNext').addEventListener('click', () => {
    Audio.sfxUI();
    if (current + 1 < stages.length) startStage(current + 1); else show('screenTitle');
  });
  $('btnRetry').addEventListener('click', () => { Audio.sfxUI(); show(null); game.reset(); });
  // 클리어 팝업의 원형 '다시 하기'
  $('btnRetryClear').addEventListener('click', () => { Audio.sfxUI(); show(null); game.reset(); });

  // 인게임 컨트롤
  $('btnUndo').addEventListener('click', () => game.undo());
  $('btnRestart').addEventListener('click', () => game.reset());
  $('btnHelp').addEventListener('click', () => { Audio.sfxUI(); buildLegend(); game.pause(); show('screenHelp'); });
  $('btnHelpClose').addEventListener('click', () => { Audio.sfxUI(); show(null); game.resume(); });
  $('btnPause').addEventListener('click', () => { Audio.sfxUI(); game.pause(); show('screenPause'); });
  $('btnResume').addEventListener('click', () => { Audio.sfxUI(); show(null); game.resume(); });
  $('btnPauseRestart').addEventListener('click', () => { Audio.sfxUI(); show(null); game.reset(); });

  Toss.onClose = () => show('screenTitle');
  window.addEventListener('resize', syncScale);
  window.addEventListener('pointerdown', () => Audio.unlockAudio(), { once: true });
}

// ----------------------------- 시작 -----------------------------
async function boot() {
  show('screenLoad');
  syncScale();
  loadProgress();
  loadStars();
  await Toss.init();
  await loadAssets();
  stages = await (await fetch('stages/stages.json')).json();
  makeGame();
  window.__game = game;  // 디버그
  wireUI();
  refreshBadges();
  show('screenTitle');
}

boot().catch(err => {
  console.error(err);
  $('screenLoad').innerHTML = `<div class="loader">로드 실패 😢<br><small>${err.message}</small></div>`;
});
