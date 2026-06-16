// 부트스트랩 + UI 상태기계.
import { loadAssets } from './assets.js';
import { Game } from './game.js';
import * as Audio from './audio.js';
import { Toss } from './toss-sdk.js';

const $ = (id) => document.getElementById(id);
const PROG_KEY = 'ssak_cleared'; // 클리어한 최고 스테이지 id

let stages = [];
let game = null;
let current = 0;            // 현재 스테이지 인덱스
let clearedMax = 0;
let pendingStartFromIntro = null;

function loadProgress() { clearedMax = parseInt(localStorage.getItem(PROG_KEY) || '0', 10); }
function saveProgress(id) { if (id > clearedMax) { clearedMax = id; localStorage.setItem(PROG_KEY, String(id)); } }

const screens = ['screenTitle', 'screenStages', 'screenIntro', 'screenClear', 'screenFail', 'screenLoad'];
function show(id) {
  screens.forEach(s => $(s).classList.toggle('hidden', s !== id));
  // 게임 HUD/캔버스 표시 여부
  const inGame = id === null;
  $('hud').classList.toggle('hidden', !inGame);
  $('btnClose').classList.toggle('hidden', false);
  $('progressWrap').classList.toggle('hidden', !inGame);
}

function fmtTime(sec) {
  const m = Math.floor(sec / 60), s = Math.floor(sec % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

// ----------------------------- 게임 훅 -----------------------------
function makeGame() {
  game = new Game($('game'), {
    onProgress: (p) => { $('progressBar').style.width = `${Math.round(p * 100)}%`; },
    onTimer: (left, total) => {
      const el = $('hudTimer');
      if (total <= 0) { el.textContent = '∞'; el.classList.remove('warn'); return; }
      el.textContent = fmtTime(left);
      el.classList.toggle('warn', left <= 15);
    },
    onCombo: (c) => {
      const el = $('hudCombo');
      el.textContent = c >= 3 ? `${c} 콤보!` : '';
      el.style.transform = c >= 3 ? 'scale(1.15)' : 'scale(1)';
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
    pendingStartFromIntro = idx;
    $('introText').textContent = st.intro;
    show('screenIntro');
  } else {
    beginStage(idx);
  }
}

function beginStage(idx) {
  const st = stages[idx];
  $('hudStage').textContent = st.id;
  $('hudTheme').textContent = st.theme;
  show(null);
  game.loadStage(st);
}

function onStageClear(elapsed) {
  const st = stages[current];
  saveProgress(st.id);
  Toss.track('stage_clear', { stage: st.id, elapsed });
  $('clearStory').textContent = st.clear || '';
  $('clearTime').textContent = elapsed != null ? `⏱ ${fmtTime(elapsed)}` : '';
  $('clearUnlock').textContent = st.unlock ? `🎁 ${st.unlock} 해금!` : '';
  const hasNext = current + 1 < stages.length;
  $('btnNext').textContent = hasNext ? '다음 스테이지' : '처음으로';
  show('screenClear');
}

function onStageFail(reason) {
  Toss.track('stage_fail', { stage: stages[current].id, reason });
  $('failReason').textContent = reason === 'time' ? '시간이 다 됐어요.\n조금만 더 빠르게!' : '막혀버렸어요.';
  $('btnAdRevive').classList.toggle('hidden', reason !== 'time' || stages[current].time <= 0);
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
    cell.innerHTML = `<span class="num">${locked ? '🔒' : st.id}</span>` +
      `<span class="thm">${st.theme}</span>` +
      `<span class="star">${cleared ? '★' : ''}</span>`;
    if (!locked) cell.addEventListener('click', () => { Audio.sfxUI(); startStage(idx); });
    grid.appendChild(cell);
  });
}

// ----------------------------- 버튼 배선 -----------------------------
function wireUI() {
  $('btnStart').addEventListener('click', () => { Audio.unlockAudio(); Audio.sfxUI(); startStage(nextUnclearedIndex()); });
  $('btnStages').addEventListener('click', () => { Audio.sfxUI(); buildStageGrid(); show('screenStages'); });
  document.querySelectorAll('[data-back]').forEach(b => b.addEventListener('click', () => { Audio.sfxUI(); buildStageGrid(); show('screenStages'); }));

  $('btnIntroNext').addEventListener('click', () => { Audio.sfxUI(); if (pendingStartFromIntro != null) beginStage(pendingStartFromIntro); });

  $('btnNext').addEventListener('click', () => {
    Audio.sfxUI();
    if (current + 1 < stages.length) startStage(current + 1);
    else show('screenTitle');
  });
  $('btnRetry').addEventListener('click', () => { Audio.sfxUI(); show(null); game.reset(); });
  $('btnAdRevive').addEventListener('click', async () => {
    Audio.sfxUI();
    const ok = await Toss.showRewardedAd();
    if (ok) { Toss.track('ad_watched', { stage: stages[current].id }); show(null); game.addTime(30); }
  });

  $('btnUndo').addEventListener('click', () => game.undo());
  $('btnReset').addEventListener('click', () => game.reset());
  $('btnClose').addEventListener('click', () => { Audio.sfxUI(); show('screenTitle'); });

  Toss.onClose = () => show('screenTitle');

  // 첫 입력에서 오디오 언락(모바일)
  window.addEventListener('pointerdown', () => Audio.unlockAudio(), { once: true });
}

// ----------------------------- 시작 -----------------------------
async function boot() {
  show('screenLoad');
  loadProgress();
  await Toss.init();
  await loadAssets();
  const res = await fetch('stages/stages.json');
  stages = await res.json();
  makeGame();
  wireUI();
  show('screenTitle');
}

boot().catch(err => {
  console.error(err);
  $('screenLoad').innerHTML = `<div class="loader">로드 실패 😢<br><small>${err.message}</small></div>`;
});
