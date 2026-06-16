// 절차적 사운드 — 오디오 파일 없이 WebAudio로 "손맛" 효과음 생성.
// 한 칸 청소할 때의 찰진 "슥-", 콤보로 음정이 살짝 올라감.
// (앱인토스 이식 시 ElevenLabs 등 실제 음원으로 교체 가능한 구조)

let ctx = null;
let master = null;
let muted = false;

function ensure() {
  if (ctx) return ctx;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return null;
  ctx = new AC();
  master = ctx.createGain();
  master.gain.value = 0.5;
  master.connect(ctx.destination);
  return ctx;
}

// 모바일: 첫 터치에서 오디오 컨텍스트 활성화
export function unlockAudio() {
  const c = ensure();
  if (c && c.state === 'suspended') c.resume();
}

export function setMuted(m) { muted = m; if (master) master.gain.value = m ? 0 : 0.5; }
export function isMuted() { return muted; }

// 짧은 노이즈 버스트 = 걸레가 바닥 쓰는 "슥" 소리
function swipeNoise(pitch = 1, dur = 0.13, vol = 0.35) {
  const c = ensure(); if (!c || muted) return;
  const n = Math.floor(c.sampleRate * dur);
  const buf = c.createBuffer(1, n, c.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < n; i++) {
    const env = Math.pow(1 - i / n, 1.6);      // 감쇠
    const grit = (Math.random() * 2 - 1);
    data[i] = grit * env;
  }
  const src = c.createBufferSource();
  src.buffer = buf;
  // 밴드패스로 '쓱'스러운 마찰음 질감
  const bp = c.createBiquadFilter();
  bp.type = 'bandpass';
  bp.frequency.value = 1600 * pitch;
  bp.Q.value = 0.8;
  const g = c.createGain();
  g.gain.value = vol;
  src.connect(bp); bp.connect(g); g.connect(master);
  src.start();
}

function tone(freq, dur, type = 'sine', vol = 0.3, slideTo = null) {
  const c = ensure(); if (!c || muted) return;
  const osc = c.createOscillator();
  const g = c.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, c.currentTime);
  if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, c.currentTime + dur);
  g.gain.setValueAtTime(0.0001, c.currentTime);
  g.gain.exponentialRampToValueAtTime(vol, c.currentTime + 0.01);
  g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + dur);
  osc.connect(g); g.connect(master);
  osc.start(); osc.stop(c.currentTime + dur + 0.02);
}

// 한 칸 청소 — combo가 올라갈수록 피치 상승(쾌감)
export function sfxClean(combo = 0) {
  const pitch = 1 + Math.min(combo, 12) * 0.05;
  swipeNoise(pitch, 0.12, 0.3);
  tone(420 * pitch, 0.08, 'triangle', 0.08);
}

// 때가 완전히 벗겨져 반짝! (타일이 깨끗해짐)
export function sfxSparkle(combo = 0) {
  const base = 880 * (1 + Math.min(combo, 12) * 0.04);
  tone(base, 0.12, 'sine', 0.12);
  setTimeout(() => tone(base * 1.5, 0.12, 'sine', 0.1), 50);
}

export function sfxMoveBlocked() { tone(160, 0.08, 'square', 0.12, 120); }

export function sfxClear() {
  const notes = [523, 659, 784, 1046];
  notes.forEach((f, i) => setTimeout(() => tone(f, 0.22, 'triangle', 0.18), i * 110));
}

export function sfxFail() {
  tone(330, 0.3, 'sawtooth', 0.14, 120);
}

export function sfxUI() { tone(660, 0.06, 'sine', 0.1); }
