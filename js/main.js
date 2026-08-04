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

/** 클리어 팝업 — 처음 깬 판에 해금 아이템이 있으면 "얻었다"를 보여준다.
 *  물건은 조각을 need 개 모아야 열리므로, 아직이면 실루엣 + 진행 상황을 보여준다.
 *  (이름은 stages.json 의 unlock 과 ITEMS 의 name 이 같아야 매칭된다) */
let rewardTimer = null;
function showReward(name) {
  const box = $('clearReward');
  clearTimeout(rewardTimer);
  const item = name && ITEMS.find(i => i.name === name);
  if (!item) { box.classList.add('hidden'); return; }
  const have = Math.min(ownedTally()[item.name] || 0, item.need);
  const done = have >= item.need;
  $('rewardImg').src = `${KIT}${done ? 'it' : 'sil'}_${item.img}.png`;
  $('rewardName').textContent = done ? item.name : `${item.name} 조각`;
  $('rewardSub').textContent = done
    ? '수집함에 담겼어요'
    : `조각 ${have}/${item.need} — 다 모으면 열려요`;
  box.classList.add('hidden');
  // 별이 다 박힌 뒤에 등장시켜 연출이 겹치지 않게 한다
  rewardTimer = setTimeout(() => { box.classList.remove('hidden'); Audio.sfxSparkle(6); }, 1150);
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

// 수집품 — 아이템마다 컬러(it_*)와 회색(sil_*) 두 벌이 있다.
// 얻으면 컬러, 아직이면 회색 실루엣으로 보여준다.
// 앞 4개는 스테이지 해금 아이템(stages.json 의 unlock 과 이름이 같아야 매칭된다).
// area = 어느 장소에서 나오는 물건인지(수집함 탭 분류). desc = 얻었을 때 읽는 한 줄.
// need = 해금에 필요한 조각 수. 20판에서 조각이 20개 나오므로
// 9종×2 + 2종×1 = 20 으로 맞춰, 20판을 다 깨면 11종이 정확히 전부 열린다.
const ITEMS = [
  { name: '구겨진 잠옷', img: 'pajama', area: 1, need: 1, desc: '며칠을 입고 잔 잠옷이다냥. 드디어 벗어 던졌다냥!' },
  { name: '노란 고무장갑', img: 'gloves', area: 1, need: 2, desc: '찌든 얼룩과 맞설 첫 장비다냥.' },
  { name: '작은 화분', img: 'plant', area: 1, need: 2, desc: '창가에 두니 방이 좀 살아났다냥.' },
  { name: '새 운동화', img: 'sneakers', area: 1, need: 1, desc: '이제 밖으로 나갈 준비 완료다냥!' },
  { name: '머그컵', img: 'mug', area: 1, need: 2, desc: '씻어 두니 커피가 당긴다냥.' },
  { name: '탁상 램프', img: 'lamp', area: 1, need: 2, desc: '밤에도 방이 아늑해졌다냥.' },
  { name: '분무기', img: 'spray', area: 1, need: 2, desc: '한 번 뿌리면 얼룩이 쓱 진다냥.' },
  { name: '물뿌리개', img: 'can', area: 1, need: 2, desc: '물 주는 게 하루 일과가 됐다냥.' },
  { name: '티슈 상자', img: 'tissue', area: 1, need: 2, desc: '손 닿는 곳에 두니 편하다냥.' },
  { name: '쿠션', img: 'cushion', area: 1, need: 2, desc: '앉을 자리가 생겼다는 뜻이다냥.' },
  { name: '장바구니', img: 'basket', area: 1, need: 2, desc: '장 보러 나갈 결심이다냥!' },
];

// 도전과제 — progress(cleared, stars)로 진행도를 계산한다
const ACHIEVEMENTS = [
  { name: '첫걸음',     icon: 'ach_sprout', goal: 1,  unit: '판', how: '스테이지 1판 클리어',   get: p => p.cleared },
  { name: '반짝 청소',  icon: 'ach_mop',    goal: 5,  unit: '판', how: '스테이지 5판 클리어',   get: p => p.cleared },
  { name: '깔끔한 하루', icon: 'ach_bucket', goal: 10, unit: '판', how: '스테이지 10판 클리어',  get: p => p.cleared },
  { name: '청소 달인',  icon: 'ach_vacuum', goal: 20, unit: '판', how: '스테이지 20판 모두 클리어', get: p => p.cleared },
  { name: '완벽한 방',  icon: 'ach_shelf',  goal: 10, unit: '판', how: '별 3개로 10판 클리어',  get: p => p.threeStars },
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

/** 주운 물건이 바닥에서 상단 수집 표시로 날아간다 */
let flyTimer = null;
function flyToHud(item, from, done) {
  const el = $('flyItem');
  const target = $('hudItem').getBoundingClientRect();
  clearTimeout(flyTimer);
  el.src = `${KIT}it_${item.img}.png`;
  el.className = 'fly-item';                        // hidden 해제
  // 시작 위치(바닥) — transition 없이 먼저 배치
  el.style.transition = 'none';
  el.style.opacity = '1';
  const s = 120 * parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--k') || 1);
  el.style.width = el.style.height = `${s}px`;
  el.style.left = `${from.x - s / 2}px`;
  el.style.top = `${from.y - s / 2}px`;
  // 다음 프레임에 목적지로
  requestAnimationFrame(() => requestAnimationFrame(() => {
    el.style.transition = '';
    const ts = target.width * 0.62;
    el.style.width = el.style.height = `${ts}px`;
    el.style.left = `${target.left + target.width / 2 - ts / 2}px`;
    el.style.top = `${target.top + target.height / 2 - ts / 2}px`;
    el.style.opacity = '0';
  }));
  flyTimer = setTimeout(() => { el.classList.add('hidden'); done?.(); }, 560);
}

// ----------------------------- 게임 훅 -----------------------------
function makeGame() {
  game = new Game($('game'), {
    onTiles: (left) => { $('hudTiles').textContent = String(left); },
    // got === null 이면 이 판엔 수집품이 없다
    onItem: (got, from) => {
      const box = $('hudItem');
      const st = stages[current];
      const item = st?.item && ITEMS.find(i => i.name === st.item.name);
      box.classList.toggle('hidden', got === null || !item);
      if (!item) return;
      if (got && from) {
        // 바닥 → HUD 로 날아간 뒤에 표시가 컬러로 바뀐다
        flyToHud(item, from, () => {
          box.querySelector('img').src = `${KIT}it_${item.img}.png`;
          box.classList.add('got');
        });
        return;
      }
      box.querySelector('img').src = `${KIT}${got ? 'it' : 'sil'}_${item.img}.png`;
      box.classList.toggle('got', !!got);
    },
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
  const isFirstClear = st.id > clearedMax;      // saveProgress 전에 판정해야 한다
  saveProgress(st.id);
  const s = starsFor(st, elapsed);
  if (s > (stars[st.id] || 0)) { stars[st.id] = s; saveStars(); }
  Toss.track('stage_clear', { stage: st.id, elapsed, stars: s });
  $('clearStory').textContent = st.clear || '';
  showReward(isFirstClear ? st.unlock : null);
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
/** 클리어한 판들의 unlock 을 모아 물건별 **조각 수**를 센다 (need 개를 채우면 해금) */
function ownedTally() {
  const t = {};
  stages.filter(s => s.id <= clearedMax && s.unlock)
        .forEach(s => { t[s.unlock] = (t[s.unlock] || 0) + 1; });
  return t;
}
function progressSummary() {
  return {
    cleared: clearedMax,
    threeStars: Object.values(stars).filter(v => v >= 3).length,
  };
}

let collTab = 0;                                 // 0 = 전체, 그 외 = AREAS 인덱스+1

/** 수집함 — 장소별 탭(전체/자취방/편의점…)으로 걸러 보여준다.
 *  나중에 장소가 늘어도 AREAS 만 늘리면 탭이 따라 생긴다. */
function buildCollection() {
  const owned = ownedCount();
  // ---- 탭 ----
  const tabs = $('collTabs');
  tabs.innerHTML = '';
  const defs = [{ label: '전체', area: 0 },
                ...AREAS.map((a, i) => ({ label: a.name, area: i + 1, coming: a.coming }))];
  defs.forEach(d => {
    const b = el('button', 'coll-tab' + (collTab === d.area ? ' on' : ''), d.label);
    b.addEventListener('click', () => { Audio.sfxUI(); collTab = d.area; buildCollection(); });
    tabs.appendChild(b);
  });

  // ---- 목록 ----
  const tally = ownedTally();
  const list = ITEMS.map(it => {
    const count = Math.min(tally[it.name] || 0, it.need);
    return { ...it, count, done: count >= it.need };
  }).filter(it => collTab === 0 || it.area === collTab);
  const gotN = list.filter(i => i.done).length;
  $('collCount').textContent = `${gotN} / ${list.length}`;

  const grid = $('collGrid');
  grid.innerHTML = '';
  if (!list.length) {
    grid.appendChild(el('div', 'coll-empty', '이 장소는 준비 중이다냥'));
  }
  list.forEach(it => {
    // 조각을 다 모아야 컬러로 해금된다. 그 전에는 회색 + 진행바(n/필요)
    const cell = el('button', 'slot ' + (it.done ? 'got' : 'lock'));
    cell.innerHTML = `<img class="thing" src="${KIT}${it.done ? 'it' : 'sil'}_${it.img}.png" alt="${it.name}">`
      + (it.done ? ''
                 : `<span class="pcs"><i style="width:${Math.round(it.count / it.need * 100)}%"></i>`
                   + `<b>${it.count}/${it.need}</b></span>`);
    cell.addEventListener('click', () => { Audio.sfxUI(); showItemInfo(it); });
    grid.appendChild(cell);
  });
  // 첫 진입엔 가장 최근에 해금한 물건을 보여준다
  const last = [...list].reverse().find(i => i.done);
  showItemInfo(last || null);
}

function showItemInfo(it) {
  if (!it) {
    $('itemName').textContent = '물건을 눌러보라냥';
    $('itemDesc').textContent = '뭘 모았는지 알려주겠다냥.';
    return;
  }
  if (it.done) {
    $('itemName').textContent = it.name;
    $('itemDesc').textContent = it.desc;
  } else {
    $('itemName').textContent = '???';
    $('itemDesc').textContent = it.count
      ? `조각을 ${it.need - it.count}개 더 모으면 열린다냥. (${it.count}/${it.need})`
      : '청소하다 보면 나온다냥.';
  }
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
      + `<div class="ach-mid">`
      +   `<div class="ach-top"><span class="ach-name">${a.name}</span>`
      +     `<span class="ach-num">${cur} / ${a.goal}${a.unit}</span></div>`
      +   `<div class="ach-how">${done ? '달성했어요!' : a.how}</div>`
      +   `<div class="ach-bar"><i style="width:${Math.round(cur / a.goal * 100)}%"></i></div>`
      + `</div>`
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
