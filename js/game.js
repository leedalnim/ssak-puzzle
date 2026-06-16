// 게임 코어 — 한붓 청소 퍼즐 로직 + 렌더링.
// 손맛: 이동 트윈/스쿼시, 먼지·반짝임 파티클, 콤보 사운드, 성장 그라데이션.

import { IMG } from './assets.js';
import { Particles } from './particles.js';
import { initInput, DIRS } from './input.js';
import * as Audio from './audio.js';

const VW = 216, VH = 384;     // 가상 캔버스(9:16). CSS가 화면 높이에 맞춰 확대.
const TILE = 16;              // 스프라이트 네이티브 타일 크기
const MOVE_MS = 110;          // 한 칸 이동 시간

const lerp = (a, b, t) => a + (b - a) * t;
const easeOut = (t) => 1 - Math.pow(1 - t, 3);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

function hexLerp(h1, h2, t) {
  const p = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const a = p(h1), b = p(h2);
  const c = a.map((v, i) => Math.round(lerp(v, b[i], t)));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}

export class Game {
  constructor(canvas, hooks = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    canvas.width = VW; canvas.height = VH;
    this.ctx.imageSmoothingEnabled = false;
    this.hooks = hooks;          // { onProgress, onClear, onFail, onTimer, onCombo }
    this.particles = new Particles();
    this.state = 'idle';
    this.shake = 0;
    this.tilePx = 32;
    this.boardX = 0; this.boardY = 0;
    this.last = performance.now();

    initInput(canvas, {
      onMove: (dir) => this.tryMove(dir),
      onTap: (x, y) => this.onTap(x, y),
    });

    requestAnimationFrame(this._loop);
  }

  loadStage(stage) {
    this.stage = stage;
    this.rows = stage.grid.length;
    this.cols = stage.grid[0].length;
    // 보드 상태: dur(현재 내구도), wall(벽 여부)
    this.dur = stage.grid.map(row => row.slice());
    this.wall = stage.grid.map(row => row.map(v => v === 0));
    this.totalDirt = stage.grid.flat().reduce((s, v) => s + v, 0);

    // 레이아웃: 보드를 화면 중앙에. 스프라이트는 정수배(S)로 그려 픽셀 균일.
    const availW = VW - 24, availH = VH - 96;
    const S = clamp(Math.floor(Math.min(availW / (this.cols * TILE), availH / (this.rows * TILE))), 2, 6);
    this.tilePx = TILE * S;
    this.scale = S;
    this.boardX = Math.round((VW - this.cols * this.tilePx) / 2);
    this.boardY = Math.round((VH - this.rows * this.tilePx) / 2) + 8;

    // 히어로 배치 + 시작칸 청소
    this.hero = {
      gx: stage.start.x, gy: stage.start.y,
      px: stage.start.x, py: stage.start.y, // 셀 단위(트윈용)
      facing: 1, moving: false, t: 0,
      fromX: 0, fromY: 0, frame: 0, frameT: 0, squash: 0,
    };
    this._clean(stage.start.x, stage.start.y, true);

    this.combo = 0;
    this.cleanedCount = (this.totalDirt - this.remainingDirt());
    this.undoStack = [];
    this.time = stage.time || 0;
    this.timeLeft = this.time;
    this.particles.clear();
    this.state = 'playing';
    this.shake = 0;
    this._emitProgress();
    if (this.hooks.onTimer) this.hooks.onTimer(this.timeLeft, this.time);
    if (this.hooks.onCombo) this.hooks.onCombo(0);
  }

  remainingDirt() {
    let s = 0;
    for (let y = 0; y < this.rows; y++)
      for (let x = 0; x < this.cols; x++)
        if (!this.wall[y][x]) s += this.dur[y][x];
    return s;
  }

  _clean(x, y, silent = false) {
    // 한 번 닦기: 내구도 -1. 0 도달 시 반짝.
    const before = this.dur[y][x];
    if (before <= 0) return false;
    this.dur[y][x] = before - 1;
    const cx = this.boardX + x * this.tilePx + this.tilePx / 2;
    const cy = this.boardY + y * this.tilePx + this.tilePx / 2;
    const tints = { 3: '#6a5238', 2: '#76829e', 1: '#bcb89a' };
    this.particles.dust(cx, cy, tints[before] || '#b9a98a', 7);
    if (!silent) {
      if (this.dur[y][x] === 0) {
        this.particles.sparkle(cx, cy, 7);
        Audio.sfxSparkle(this.combo);
        this.shake = Math.min(this.shake + 2.2, 4);
      } else {
        Audio.sfxClean(this.combo);
        this.shake = Math.min(this.shake + 1, 3);
      }
    }
    return true;
  }

  _snapshot() {
    return {
      dur: this.dur.map(r => r.slice()),
      gx: this.hero.gx, gy: this.hero.gy, combo: this.combo,
    };
  }

  tryMove(dir) {
    if (this.state !== 'playing' || this.hero.moving) return;
    const d = DIRS[dir];
    const nx = this.hero.gx + d.x, ny = this.hero.gy + d.y;
    if (nx < 0 || ny < 0 || nx >= this.cols || ny >= this.rows) { Audio.sfxMoveBlocked(); return; }
    if (this.wall[ny][nx] || this.dur[ny][nx] <= 0) { Audio.sfxMoveBlocked(); this._bump(d); return; }

    this.undoStack.push(this._snapshot());
    if (d.x !== 0) this.hero.facing = d.x > 0 ? 1 : -1;

    // 이동 트윈 시작
    this.hero.fromX = this.hero.gx; this.hero.fromY = this.hero.gy;
    this.hero.gx = nx; this.hero.gy = ny;
    this.hero.moving = true; this.hero.t = 0;

    // 진입 = 청소
    this.combo += 1;
    this._clean(nx, ny);
    if (this.hooks.onCombo) this.hooks.onCombo(this.combo);
    this._emitProgress();

    if (this.remainingDirt() === 0) this._win();
  }

  _bump(d) {
    // 막힌 방향으로 살짝 들썩(피드백)
    this.hero.bumpX = d.x * 3; this.hero.bumpY = d.y * 3; this.hero.bumpT = 0.12;
  }

  onTap(px, py) {
    if (this.state !== 'playing') return;
    const gx = Math.floor((px - this.boardX) / this.tilePx);
    const gy = Math.floor((py - this.boardY) / this.tilePx);
    const dx = gx - this.hero.gx, dy = gy - this.hero.gy;
    if (Math.abs(dx) + Math.abs(dy) !== 1) return; // 인접만
    if (dx === 1) this.tryMove('right');
    else if (dx === -1) this.tryMove('left');
    else if (dy === 1) this.tryMove('down');
    else if (dy === -1) this.tryMove('up');
  }

  undo() {
    if (this.state !== 'playing' || !this.undoStack.length || this.hero.moving) return;
    const s = this.undoStack.pop();
    this.dur = s.dur; this.hero.gx = s.gx; this.hero.gy = s.gy;
    this.hero.px = s.gx; this.hero.py = s.gy;
    this.combo = 0;
    if (this.hooks.onCombo) this.hooks.onCombo(0);
    Audio.sfxUI();
    this._emitProgress();
  }

  reset() {
    if (!this.stage) return;
    this.loadStage(this.stage);
    Audio.sfxUI();
  }

  addTime(sec) {
    if (this.time > 0) { this.timeLeft += sec; this.state = 'playing'; }
  }

  _win() {
    this.state = 'clear';
    Audio.sfxClear();
    this.particles.confetti(VW, VH, 70);
    this.shake = 5;
    const elapsed = this.time > 0 ? this.time - this.timeLeft : null;
    setTimeout(() => this.hooks.onClear && this.hooks.onClear({ elapsed }), 700);
  }

  _fail(reason) {
    if (this.state !== 'playing') return;
    this.state = 'fail';
    Audio.sfxFail();
    setTimeout(() => this.hooks.onFail && this.hooks.onFail({ reason }), 400);
  }

  _emitProgress() {
    const cleaned = this.totalDirt - this.remainingDirt();
    this.progress = this.totalDirt ? cleaned / this.totalDirt : 0;
    if (this.hooks.onProgress) this.hooks.onProgress(this.progress);
  }

  // ----------------------------- 렌더 루프 -----------------------------
  _loop = (now) => {
    const dt = Math.min((now - this.last) / 1000, 0.05);
    this.last = now;
    this._update(dt);
    this._draw();
    requestAnimationFrame(this._loop);
  };

  _update(dt) {
    const h = this.hero;
    if (h && h.moving) {
      h.t += dt * 1000 / MOVE_MS;
      if (h.t >= 1) {
        h.t = 1; h.moving = false;
        h.px = h.gx; h.py = h.gy;
        h.squash = 1; // 착지 스쿼시
      } else {
        const e = easeOut(h.t);
        h.px = lerp(h.fromX, h.gx, e);
        h.py = lerp(h.fromY, h.gy, e);
        // 걷기 프레임
        h.frameT += dt;
        if (h.frameT > 0.09) { h.frameT = 0; h.frame ^= 1; }
      }
    }
    if (h) {
      if (h.squash > 0) h.squash = Math.max(0, h.squash - dt * 6);
      if (h.bumpT > 0) { h.bumpT -= dt; if (h.bumpT <= 0) { h.bumpX = h.bumpY = 0; } }
    }
    if (this.shake > 0) this.shake = Math.max(0, this.shake - dt * 16);
    this.particles.update(dt);

    if (this.state === 'playing' && this.time > 0) {
      this.timeLeft -= dt;
      if (this.hooks.onTimer) this.hooks.onTimer(Math.max(0, this.timeLeft), this.time);
      if (this.timeLeft <= 0) { this.timeLeft = 0; this._fail('time'); }
    }
  }

  _draw() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, VW, VH);
    if (!this.stage) return;

    // 성장 그라데이션 배경(무기력→활력)
    const p = this.progress || 0;
    const bg = ctx.createLinearGradient(0, 0, 0, VH);
    bg.addColorStop(0, hexLerp(this.stage.moodFrom, this.stage.moodTo, p * 0.6));
    bg.addColorStop(1, hexLerp('#1a1622', this.stage.moodTo, p));
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, VW, VH);

    ctx.save();
    if (this.shake > 0) {
      ctx.translate((Math.random() * 2 - 1) * this.shake, (Math.random() * 2 - 1) * this.shake);
    }

    this._drawBoardBase(ctx);
    this._drawTiles(ctx);
    this._drawDecor(ctx);
    this._drawHero(ctx);
    this.particles.draw(ctx);

    ctx.restore();
  }

  _drawBoardBase(ctx) {
    // 보드 밑 깔개(고전 게임식 테두리) — 떠 있는 느낌
    const pad = Math.round(this.scale * 2);
    const x = this.boardX - pad, y = this.boardY - pad;
    const w = this.cols * this.tilePx + pad * 2, h = this.rows * this.tilePx + pad * 2;
    ctx.fillStyle = 'rgba(0,0,0,.28)';
    this._roundRect(ctx, x + 2, y + 4, w, h, 6); ctx.fill();
    ctx.fillStyle = '#2c2434';
    this._roundRect(ctx, x, y, w, h, 6); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,.06)';
    ctx.lineWidth = 1;
    this._roundRect(ctx, x + 0.5, y + 0.5, w - 1, h - 1, 6); ctx.stroke();
  }

  _drawTiles(ctx) {
    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        if (this.wall[y][x]) continue;
        const d = this.dur[y][x];
        const img = IMG['tile' + d];
        const dx = this.boardX + x * this.tilePx, dy = this.boardY + y * this.tilePx;
        ctx.drawImage(img, dx, dy, this.tilePx, this.tilePx);
        // 체커 톤: 격자 가독성 + 바닥다움
        if ((x + y) & 1) {
          ctx.fillStyle = 'rgba(60,40,30,.07)';
          ctx.fillRect(dx, dy, this.tilePx, this.tilePx);
        }
        // 남은 횟수 핍 — 여러 번 닦아야 하는 2·3 칸만(가독성)
        if (d >= 2) this._drawPips(ctx, dx, dy, d);
      }
    }
  }

  _drawPips(ctx, dx, dy, n) {
    const s = this.scale;
    const r = Math.max(1.5, s * 0.9);
    const gap = r * 2.4;
    const totalW = (n - 1) * gap;
    const cx = dx + this.tilePx / 2 - totalW / 2;
    const cy = dy + this.tilePx - r * 2.2;
    const colors = { 3: '#f0d66e', 2: '#9fb6e0', 1: '#e7e1d2' };
    for (let i = 0; i < n; i++) {
      ctx.beginPath();
      ctx.arc(cx + i * gap, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0,0,0,.45)'; ctx.fill();
      ctx.beginPath();
      ctx.arc(cx + i * gap, cy - 0.5, r * 0.7, 0, Math.PI * 2);
      ctx.fillStyle = colors[n] || '#fff'; ctx.fill();
    }
  }

  _drawDecor(ctx) {
    if (!this.stage.decor) return;
    for (const d of this.stage.decor) {
      if (d.x >= this.cols || d.y >= this.rows) continue;
      // 해당 칸이 아직 더러우면 쓰레기 표시(닦으면 사라짐)
      if (!this.wall[d.y][d.x] && this.dur[d.y][d.x] <= 0) continue;
      const img = IMG[d.type];
      if (!img) continue;
      const dx = this.boardX + d.x * this.tilePx;
      const dy = this.boardY + d.y * this.tilePx - Math.round(this.scale * 4);
      ctx.drawImage(img, dx, dy, this.tilePx, this.tilePx);
    }
  }

  _drawHero(ctx) {
    const h = this.hero, s = this.scale;
    const baseX = this.boardX + h.px * this.tilePx + this.tilePx / 2 + (h.bumpX || 0) * s / 3;
    const footY = this.boardY + h.py * this.tilePx + this.tilePx + (h.bumpY || 0) * s / 3;
    // 그림자
    ctx.fillStyle = 'rgba(0,0,0,.25)';
    ctx.beginPath();
    ctx.ellipse(baseX, footY - s * 2, this.tilePx * 0.32, this.tilePx * 0.13, 0, 0, Math.PI * 2);
    ctx.fill();

    const img = (h.moving ? (h.frame ? IMG.hero_walk_b : IMG.hero_walk_a) : IMG.hero_idle);
    const w = 16 * s, ht = 24 * s;
    // 착지 스쿼시
    const sq = h.squash;
    const sx = 1 + sq * 0.12, sy = 1 - sq * 0.16;
    // 걷는 동안 살짝 위아래 바운스
    const bounce = h.moving ? Math.sin(h.t * Math.PI) * s * 1.2 : 0;

    ctx.save();
    ctx.translate(baseX, footY - bounce);
    ctx.scale(h.facing * sx, sy);
    ctx.drawImage(img, -w / 2, -ht + s * 2, w, ht);
    ctx.restore();
  }

  _roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
}
