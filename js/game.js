// 게임 코어 — 한붓 청소 퍼즐 로직 + 코지룸(3D 클레이) 렌더링.
import { IMG } from './assets.js';
import { Particles } from './particles.js';
import { initInput, DIRS } from './input.js';
import * as Audio from './audio.js';
import {
  VW, VH, boardCanvas, invalidateBoard, cellCenter, hitCell,
  drawObject, drawBoardShadow,
} from './render.js';

const MOVE_MS = 130;
const CHAR_SCALE = 1.55;      // 셀 높이 대비 캐릭터 크기 (이웃 칸을 과하게 가리지 않는 선)
const OBST_SCALE = 1.05;

const lerp = (a, b, t) => a + (b - a) * t;
const easeOut = (t) => 1 - Math.pow(1 - t, 3);

export class Game {
  constructor(canvas, hooks = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    canvas.width = VW; canvas.height = VH;
    this.ctx.imageSmoothingEnabled = true;
    this.ctx.imageSmoothingQuality = 'high';
    this.hooks = hooks;
    this.particles = new Particles();
    this.state = 'idle';
    this.shake = 0;
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
    this.dur = stage.grid.map(row => row.slice());
    this.hole = stage.grid.map(row => row.map(v => v === 0));   // 보드에 뚫린 칸
    this.wall = stage.grid.map(row => row.map(v => v === 0));   // 지나갈 수 없는 칸
    this.obstacles = stage.obstacles || [];
    for (const o of this.obstacles) {
      if (this.wall[o.y]) this.wall[o.y][o.x] = true;
      this.dur[o.y][o.x] = 0;
    }
    this.totalDirt = this.dur.flat().reduce((s, v) => s + v, 0);

    this.hero = {
      gx: stage.start.x, gy: stage.start.y, px: stage.start.x, py: stage.start.y,
      dir: 'down', moving: false, t: 0, fromX: 0, fromY: 0, bumpX: 0, bumpY: 0, bumpT: 0,
    };
    this._clean(stage.start.x, stage.start.y, true);

    this.combo = 0;
    this.undoStack = [];
    this.time = stage.time || 0;
    this.timeLeft = this.time;
    this.particles.clear();
    this.state = 'playing';
    this.shake = 0;
    invalidateBoard();
    this._emitProgress();
    if (this.hooks.onTimer) this.hooks.onTimer(this.timeLeft, this.time);
  }

  // ------------------------------------------------------------- 상태 조회
  remainingDirt() {
    let s = 0;
    for (let y = 0; y < this.rows; y++)
      for (let x = 0; x < this.cols; x++) if (!this.wall[y][x]) s += this.dur[y][x];
    return s;
  }
  remainingTiles() {
    let s = 0;
    for (let y = 0; y < this.rows; y++)
      for (let x = 0; x < this.cols; x++) if (!this.wall[y][x] && this.dur[y][x] > 0) s++;
    return s;
  }
  canUndo() { return this.undoStack.length > 0; }

  // ------------------------------------------------------------- 조작
  _clean(x, y, silent = false) {
    const before = this.dur[y][x];
    if (before <= 0) return false;
    this.dur[y][x] = before - 1;
    invalidateBoard();
    const { x: cx, y: cy } = cellCenter(x, y, this.cols, this.rows);
    const tints = { 5: '#5a4028', 4: '#6f5233', 3: '#8a6a44', 2: '#a8865c', 1: '#c9ab80' };
    this.particles.dust(cx, cy, tints[before] || '#c9ab80', 8);
    if (!silent) {
      if (this.dur[y][x] === 0) {
        this.particles.sparkle(cx, cy, 8);
        Audio.sfxSparkle(this.combo);
        this.shake = Math.min(this.shake + 3, 6);
      } else {
        Audio.sfxClean(this.combo);
        this.shake = Math.min(this.shake + 1.5, 4);
      }
    }
    return true;
  }

  _snapshot() {
    return { dur: this.dur.map(r => r.slice()), gx: this.hero.gx, gy: this.hero.gy, combo: this.combo };
  }

  tryMove(dir) {
    if (this.state !== 'playing' || this.hero.moving) return;
    const d = DIRS[dir];
    const nx = this.hero.gx + d.x, ny = this.hero.gy + d.y;
    this.hero.dir = dir;
    if (nx < 0 || ny < 0 || nx >= this.cols || ny >= this.rows) { Audio.sfxMoveBlocked(); return; }
    if (this.wall[ny][nx] || this.dur[ny][nx] <= 0) { Audio.sfxMoveBlocked(); this._bump(d); return; }
    this.undoStack.push(this._snapshot());
    this.hero.fromX = this.hero.gx; this.hero.fromY = this.hero.gy;
    this.hero.gx = nx; this.hero.gy = ny; this.hero.moving = true; this.hero.t = 0;
    this.combo += 1;
    this._clean(nx, ny);
    this._emitProgress();
    if (this.remainingDirt() === 0) this._win();
    else if (this._stuck()) this._fail('stuck');
  }

  /** 갈 곳이 없으면 막힌 것 */
  _stuck() {
    for (const d of Object.values(DIRS)) {
      const nx = this.hero.gx + d.x, ny = this.hero.gy + d.y;
      if (nx < 0 || ny < 0 || nx >= this.cols || ny >= this.rows) continue;
      if (!this.wall[ny][nx] && this.dur[ny][nx] > 0) return false;
    }
    return true;
  }

  _bump(d) { this.hero.bumpX = d.x * 6; this.hero.bumpY = d.y * 6; this.hero.bumpT = 0.12; }

  onTap(px, py) {
    if (this.state !== 'playing') return;
    const hit = hitCell(px, py, this.cols, this.rows);
    if (!hit) return;
    const dx = hit.c - this.hero.gx, dy = hit.r - this.hero.gy;
    if (Math.abs(dx) + Math.abs(dy) !== 1) return;
    if (dx === 1) this.tryMove('right');
    else if (dx === -1) this.tryMove('left');
    else if (dy === 1) this.tryMove('down');
    else if (dy === -1) this.tryMove('up');
  }

  undo() {
    if (this.state === 'fail') this.state = 'playing';
    if (this.state !== 'playing' || !this.undoStack.length || this.hero.moving) return;
    const s = this.undoStack.pop();
    this.dur = s.dur;
    this.hero.gx = s.gx; this.hero.gy = s.gy; this.hero.px = s.gx; this.hero.py = s.gy;
    this.combo = 0;
    invalidateBoard();
    Audio.sfxUI();
    this._emitProgress();
  }
  reset() { if (this.stage) { this.loadStage(this.stage); Audio.sfxUI(); } }
  addTime(sec) { if (this.time > 0) { this.timeLeft += sec; this.state = 'playing'; } }

  // ------------------------------------------------------------- 종료 처리
  _win() {
    this.state = 'clear';
    Audio.sfxClear();
    this.particles.confetti(VW, VH, 90);
    this.shake = 7;
    const elapsed = this.time > 0 ? this.time - this.timeLeft : null;
    setTimeout(() => this.hooks.onClear && this.hooks.onClear({ elapsed }), 800);
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
    this.hooks.onProgress?.(this.progress);
    this.hooks.onTiles?.(this.remainingTiles());
    this.hooks.onUndoState?.(this.canUndo());
  }

  // ------------------------------------------------------------- 루프
  _loop = (now) => {
    const dt = Math.min((now - this.last) / 1000, 0.05);
    this.last = now;
    this._update(dt);
    this._draw();
    requestAnimationFrame(this._loop);
  };

  _update(dt) {
    const h = this.hero;
    if (h?.moving) {
      h.t += dt * 1000 / MOVE_MS;
      if (h.t >= 1) { h.t = 1; h.moving = false; h.px = h.gx; h.py = h.gy; }
      else { const e = easeOut(h.t); h.px = lerp(h.fromX, h.gx, e); h.py = lerp(h.fromY, h.gy, e); }
    }
    if (h?.bumpT > 0) { h.bumpT -= dt; if (h.bumpT <= 0) h.bumpX = h.bumpY = 0; }
    if (this.shake > 0) this.shake = Math.max(0, this.shake - dt * 22);
    this.particles.update(dt);
    if (this.state === 'playing' && this.time > 0) {
      this.timeLeft -= dt;
      this.hooks.onTimer?.(Math.max(0, this.timeLeft), this.time);
      if (this.timeLeft <= 0) { this.timeLeft = 0; this._fail('time'); }
    }
  }

  _draw() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, VW, VH);
    if (IMG.bg_studio) ctx.drawImage(IMG.bg_studio, 0, 0, VW, VH);
    if (!this.stage) return;

    ctx.save();
    if (this.shake > 0) {
      ctx.translate((Math.random() * 2 - 1) * this.shake, (Math.random() * 2 - 1) * this.shake);
    }
    drawBoardShadow(ctx);
    ctx.drawImage(boardCanvas(this.dur, this.hole, this.cols, this.rows), 0, 0);

    // 뒤쪽(위쪽) 오브젝트부터 그려야 앞이 뒤를 가린다
    const drawables = this.obstacles.map(o => ({ r: o.y, draw: () => this._drawObstacle(ctx, o) }));
    drawables.push({ r: this.hero.py, draw: () => this._drawHero(ctx) });
    drawables.sort((a, b) => a.r - b.r).forEach(d => d.draw());

    this.particles.draw(ctx);
    ctx.restore();
  }

  _drawObstacle(ctx, o) {
    drawObject(ctx, IMG['obs_' + o.type], o.x, o.y, this.cols, this.rows, OBST_SCALE, o.type);
  }

  _drawHero(ctx) {
    const h = this.hero;
    const frame = h.moving ? 1 + (Math.floor(h.t * 3) % 2) : 0;
    const img = IMG[`char_${h.dir}_${frame}`] || IMG.char_down_0;
    if (!img) return;
    // 이동 중에는 셀 사이를 보간 — 정수 셀이 아니므로 좌표를 직접 계산
    const a = cellCenter(Math.floor(h.px), Math.floor(h.py), this.cols, this.rows);
    const b = cellCenter(Math.ceil(h.px), Math.ceil(h.py), this.cols, this.rows);
    const fx = h.px - Math.floor(h.px), fy = h.py - Math.floor(h.py);
    const cx = lerp(a.x, b.x, Math.max(fx, fy)) + h.bumpX;
    const cy = lerp(a.y, b.y, Math.max(fx, fy)) + h.bumpY;
    const cellH = a.cellH;
    const hop = h.moving ? Math.sin(h.t * Math.PI) * cellH * 0.08 : 0;

    const ht = cellH * CHAR_SCALE, w = img.width * ht / img.height;
    const baseY = cy + cellH * 0.16;
    ctx.save();
    ctx.filter = 'blur(6px)';
    ctx.fillStyle = 'rgba(58,40,26,.5)';
    ctx.beginPath();
    ctx.ellipse(cx, baseY, w * 0.20, cellH * 0.06, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    ctx.drawImage(img, cx - w / 2, baseY - ht - hop, w, ht);
  }
}
