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

// 한 칸 청소 — '쓱' 마찰음만. (예전엔 삼각파 톤이 겹쳐 '픽' 소리가 났다)
export function sfxClean(combo = 0) {
  const pitch = 1 + Math.min(combo, 12) * 0.04;
  swipeNoise(pitch, 0.14, 0.28);
}

// 때가 완전히 벗겨져 반짝! — 짧고 날카로운 '픽' 대신 부드러운 종소리
export function sfxSparkle(combo = 0) {
  const base = 1046 * (1 + Math.min(combo, 12) * 0.03);   // C6
  bell(base, 0.34, 0.075);
  setTimeout(() => bell(base * 1.5, 0.40, 0.055), 70);    // 완전5도 — 듣기 편한 화음
}

/** 부드러운 종소리 — 천천히 붙었다 길게 사라진다 */
function bell(freq, dur, vol) {
  const c = ensure(); if (!c || muted) return;
  const osc = c.createOscillator(); const g = c.createGain();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(freq, c.currentTime);
  g.gain.setValueAtTime(0.0001, c.currentTime);
  g.gain.exponentialRampToValueAtTime(vol, c.currentTime + 0.035);   // 부드러운 어택
  g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + dur);  // 긴 여운
  osc.connect(g); g.connect(master);
  osc.start(); osc.stop(c.currentTime + dur + 0.02);
}

/** 클리어 팝업에서 별이 하나씩 박힐 때 — 음이 올라가며 상쾌하게 */
export function sfxStar(i = 0) {
  const scale = [1318, 1568, 2093];            // E6 · G6 · C7
  bell(scale[Math.min(i, 2)], 0.45, 0.09);
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
