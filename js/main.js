// 부트스트랩 + UI 상태기계.
import { loadAssets } from './assets.js';
import { Game } from './game.js';
import * as Audio from './audio.js';
import { Toss } from './toss-sdk.js';

const $ = (id) => document.getElementById(id);
const PROG_KEY = 'ssak_cleared';

let stages = [];
let game = null;
let current = 0;
let clearedMax = 0;
let pendingIntro = null;

const screens = ['screenTitle', 'screenStages', 'screenIntro', 'screenClear',
                 'screenFail', 'screenHelp', 'screenPause', 'screenLoad'];

function loadProgress() { clearedMax = parseInt(localStorage.getItem(PROG_KEY) || '0', 10); }
function saveProgress(id) { if (id > clearedMax) { clearedMax = id; localStorage.setItem(PROG_KEY, String(id)); } }

/** id=null 이면 인게임 화면 */
function show(id) {
  screens.forEach(s => $(s).classList.toggle('hidden', s !== id));
  const inGame = id === null || id === 'screenHelp' || id === 'screenPause';
  $('hud').classList.toggle('hidden', !inGame);
  $('toolbar').classList.toggle('hidden', !inGame);
  $('progressWrap').classList.toggle('hidden', !inGame);
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
    onProgress: (p) => { $('progressBar').style.width = `${Math.round(p * 100)}%`; },
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
    $('introAct').textContent = `${st.act}막`;
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
  Toss.track('stage_clear', { stage: st.id, elapsed });
  $('clearStory').textContent = st.clear || '';
  $('clearTime').textContent = elapsed != null ? `⏱ ${fmtTime(elapsed)}` : '';
  $('clearUnlock').textContent = st.unlock ? `🎁 ${st.unlock} 해금!` : '';
  $('btnNext').textContent = current + 1 < stages.length ? '다음 스테이지' : '처음으로';
  show('screenClear');
}

function onStageFail(reason) {
  Toss.track('stage_fail', { stage: stages[current].id, reason });
  $('failReason').textContent = reason === 'time'
    ? '시간이 다 됐어요.\n조금만 더 빠르게!'
    : '갈 곳이 없어요.\n한 수 무르거나 처음부터 해볼까요?';
  $('btnUndoFromFail').classList.toggle('hidden', !game.canUndo());
  show('screenFail');
}

function nextUnclearedIndex() {
  const i = stages.findIndex(s => s.id > clearedMax);
  return i < 0 ? 0 : i;
}

// ----------------------------- 스테이지 선택 -----------------------------
function buildStageGrid() {
  const grid = $('stageGrid');
  grid.innerHTML = '';
  stages.forEach((st, idx) => {
    const locked = st.id > clearedMax + 1;
    const cleared = st.id <= clearedMax;
    const cell = document.createElement('button');
    cell.className = 'stage-cell' + (locked ? ' locked' : '') + (cleared ? ' cleared' : '');
    cell.innerHTML = `<span class="num">${locked ? '🔒' : st.id}</span>`
      + `<span class="thm">${st.theme}</span>`
      + `<span class="star">${cleared ? '★' : ''}</span>`;
    if (!locked) cell.addEventListener('click', () => { Audio.sfxUI(); startStage(idx); });
    grid.appendChild(cell);
  });
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
  $('btnStages').addEventListener('click', () => { Audio.sfxUI(); buildStageGrid(); show('screenStages'); });
  document.querySelectorAll('[data-back]').forEach(b =>
    b.addEventListener('click', () => { Audio.sfxUI(); buildStageGrid(); show('screenStages'); }));

  $('btnIntroNext').addEventListener('click', () => {
    Audio.sfxUI(); if (pendingIntro != null) beginStage(pendingIntro);
  });

  $('btnNext').addEventListener('click', () => {
    Audio.sfxUI();
    if (current + 1 < stages.length) startStage(current + 1); else show('screenTitle');
  });
  $('btnRetry').addEventListener('click', () => { Audio.sfxUI(); show(null); game.reset(); });
  $('btnUndoFromFail').addEventListener('click', () => { Audio.sfxUI(); show(null); game.undo(); });

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
  await Toss.init();
  await loadAssets();
  stages = await (await fetch('stages/stages.json')).json();
  makeGame();
  wireUI();
  show('screenTitle');
}

boot().catch(err => {
  console.error(err);
  $('screenLoad').innerHTML = `<div class="loader">로드 실패 😢<br><small>${err.message}</small></div>`;
});
