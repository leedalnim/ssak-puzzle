// 게임 코어 — 한붓 청소 퍼즐 로직 + 집청소(코지룸) 테마 렌더링.
import { IMG } from './assets.js';
import { Particles } from './particles.js';
import { initInput, DIRS } from './input.js';
import * as Audio from './audio.js';

const VW = 688, VH = 538;
const FRAME = { x0: 189, y0: 167, x1: 515, y1: 457 };  // 몰딩 안쪽
const MOVE_MS = 120;

const lerp = (a, b, t) => a + (b - a) * t;
const easeOut = (t) => 1 - Math.pow(1 - t, 3);

export class Game {
  constructor(canvas, hooks = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    canvas.width = VW; canvas.height = VH;
    this.ctx.imageSmoothingEnabled = true;        // 고해상도 에셋 → 부드럽게 축소
    this.hooks = hooks;
    this.particles = new Particles();
    this.state = 'idle';
    this.shake = 0;
    this.cellW = 60; this.cellH = 58;
    this.boardX = FRAME.x0; this.boardY = FRAME.y0;
    this.last = performance.now();
    initInput(canvas, { onMove: (dir) => this.tryMove(dir), onTap: (x, y) => this.onTap(x, y) });
    requestAnimationFrame(this._loop);
  }

  loadStage(stage) {
    this.stage = stage;
    this.rows = stage.grid.length;
    this.cols = stage.grid[0].length;
    this.dur = stage.grid.map(row => row.slice());
    this.wall = stage.grid.map(row => row.map(v => v === 0));
    this.obstacles = stage.obstacles || [];
    for (const o of this.obstacles) { if (this.wall[o.y]) this.wall[o.y][o.x] = true; this.dur[o.y][o.x] = 0; }
    this.totalDirt = this.dur.flat().reduce((s, v) => s + v, 0);

    // 보드를 프레임 안쪽에 꽉 채움(테두리와 정합)
    this.boardX = FRAME.x0; this.boardY = FRAME.y0;
    this.cellW = (FRAME.x1 - FRAME.x0) / this.cols;
    this.cellH = (FRAME.y1 - FRAME.y0) / this.rows;

    this.hero = {
      gx: stage.start.x, gy: stage.start.y, px: stage.start.x, py: stage.start.y,
      dir: 'down', moving: false, t: 0, fromX: 0, fromY: 0, squash: 0, bumpX: 0, bumpY: 0, bumpT: 0,
    };
    this._clean(stage.start.x, stage.start.y, true);

    this.combo = 0;
    this.undoStack = [];
    this.time = stage.time || 0;
    this.timeLeft = this.time;
    this.particles.clear();
    this.state = 'playing';
    this.shake = 0;
    this._emitProgress();
    if (this.hooks.onTimer) this.hooks.onTimer(this.timeLeft, this.time);
  }

  _cx(x) { return this.boardX + (x + 0.5) * this.cellW; }
  _cy(y) { return this.boardY + (y + 0.5) * this.cellH; }

  remainingDirt() {
    let s = 0;
    for (let y = 0; y < this.rows; y++) for (let x = 0; x < this.cols; x++) if (!this.wall[y][x]) s += this.dur[y][x];
    return s;
  }
  cleanedTiles() {
    let s = 0;
    for (let y = 0; y < this.rows; y++) for (let x = 0; x < this.cols; x++) if (!this.wall[y][x] && this.dur[y][x] === 0) s++;
    return s;
  }
  totalTiles() {
    let s = 0;
    for (let y = 0; y < this.rows; y++) for (let x = 0; x < this.cols; x++) if (!this.wall[y][x]) s++;
    return s;
  }

  _clean(x, y, silent = false) {
    const before = this.dur[y][x];
    if (before <= 0) return false;
    this.dur[y][x] = before - 1;
    const tints = { 5: '#4e3a28', 4: '#604830', 3: '#78603c', 2: '#96825c', 1: '#bcb89a' };
    this.particles.dust(this._cx(x), this._cy(y), tints[before] || '#b9a98a', 7);
    if (!silent) {
      if (this.dur[y][x] === 0) {
        this.particles.sparkle(this._cx(x), this._cy(y), 7);
        this.particles.spriteBurst(['fx_clean_0', 'fx_clean_1', 'fx_clean_2', 'fx_clean_3'], this._cx(x), this._cy(y), this.cellW * 1.5, 0.5);
        Audio.sfxSparkle(this.combo); this.shake = Math.min(this.shake + 2.2, 4);
      }
      else { Audio.sfxClean(this.combo); this.shake = Math.min(this.shake + 1, 3); }
    }
    return true;
  }

  _snapshot() { return { dur: this.dur.map(r => r.slice()), gx: this.hero.gx, gy: this.hero.gy, combo: this.combo }; }

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
  }

  _bump(d) { this.hero.bumpX = d.x * 3; this.hero.bumpY = d.y * 3; this.hero.bumpT = 0.12; }

  onTap(px, py) {
    if (this.state !== 'playing') return;
    const gx = Math.floor((px - this.boardX) / this.cellW);
    const gy = Math.floor((py - this.boardY) / this.cellH);
    const dx = gx - this.hero.gx, dy = gy - this.hero.gy;
    if (Math.abs(dx) + Math.abs(dy) !== 1) return;
    if (dx === 1) this.tryMove('right');
    else if (dx === -1) this.tryMove('left');
    else if (dy === 1) this.tryMove('down');
    else if (dy === -1) this.tryMove('up');
  }

  undo() {
    if (this.state !== 'playing' || !this.undoStack.length || this.hero.moving) return;
    const s = this.undoStack.pop();
    this.dur = s.dur; this.hero.gx = s.gx; this.hero.gy = s.gy; this.hero.px = s.gx; this.hero.py = s.gy;
    this.combo = 0; Audio.sfxUI(); this._emitProgress();
  }
  reset() { if (this.stage) { this.loadStage(this.stage); Audio.sfxUI(); } }
  addTime(sec) { if (this.time > 0) { this.timeLeft += sec; this.state = 'playing'; } }

  _win() {
    this.state = 'clear'; Audio.sfxClear(); this.particles.confetti(VW, VH, 70); this.shake = 5;
    const elapsed = this.time > 0 ? this.time - this.timeLeft : null;
    setTimeout(() => this.hooks.onClear && this.hooks.onClear({ elapsed }), 700);
  }
  _fail(reason) {
    if (this.state !== 'playing') return;
    this.state = 'fail'; Audio.sfxFail();
    setTimeout(() => this.hooks.onFail && this.hooks.onFail({ reason }), 400);
  }
  _emitProgress() {
    const cleaned = this.totalDirt - this.remainingDirt();
    this.progress = this.totalDirt ? cleaned / this.totalDirt : 0;
    if (this.hooks.onProgress) this.hooks.onProgress(this.progress);
    if (this.hooks.onScore) this.hooks.onScore(this.cleanedTiles(), this.totalTiles());
  }

  _loop = (now) => {
    const dt = Math.min((now - this.last) / 1000, 0.05);
    this.last = now; this._update(dt); this._draw();
    requestAnimationFrame(this._loop);
  };

  _update(dt) {
    const h = this.hero;
    if (h && h.moving) {
      h.t += dt * 1000 / MOVE_MS;
      if (h.t >= 1) { h.t = 1; h.moving = false; h.px = h.gx; h.py = h.gy; h.squash = 1; }
      else { const e = easeOut(h.t); h.px = lerp(h.fromX, h.gx, e); h.py = lerp(h.fromY, h.gy, e); }
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
    if (IMG.store_bg) ctx.drawImage(IMG.store_bg, 0, 0, VW, VH);
    ctx.save();
    if (this.shake > 0) ctx.translate((Math.random() * 2 - 1) * this.shake, (Math.random() * 2 - 1) * this.shake);
    this._drawTiles(ctx);
    this._drawObstacles(ctx);
    this._drawHero(ctx);
    this.particles.draw(ctx);
    if (IMG.board_frame) ctx.drawImage(IMG.board_frame, 0, 0, VW, VH);
    ctx.restore();
  }

  _drawTiles(ctx) {
    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        if (this.wall[y][x]) continue;
        const img = IMG['tile' + this.dur[y][x]];
        if (img) ctx.drawImage(img, this.boardX + x * this.cellW, this.boardY + y * this.cellH, this.cellW + 0.5, this.cellH + 0.5);
      }
    }
  }

  _drawObstacles(ctx) {
    for (const o of this.obstacles) {
      const img = IMG['obstacle_' + o.type];
      if (!img) continue;
      const h = this.cellH * 1.4, w = img.width * h / img.height;
      const cx = this._cx(o.x), footY = this.boardY + (o.y + 1) * this.cellH;
      ctx.fillStyle = 'rgba(0,0,0,.22)';
      ctx.beginPath(); ctx.ellipse(cx, footY - this.cellH * 0.12, this.cellW * 0.34, this.cellH * 0.12, 0, 0, Math.PI * 2); ctx.fill();
      ctx.drawImage(img, cx - w / 2, footY - h + this.cellH * 0.05, w, h);
    }
  }

  _drawHero(ctx) {
    const h = this.hero;
    const baseX = this.boardX + (h.px + 0.5) * this.cellW + (h.bumpX || 0);
    const footY = this.boardY + (h.py + 1) * this.cellH + (h.bumpY || 0);
    // 방향별 프레임 + 걷기 애니
    let key = 'down', flip = 1;
    if (h.dir === 'up') key = 'up';
    else if (h.dir === 'left') { key = 'side'; flip = -1; }
    else if (h.dir === 'right') key = 'side';
    const frame = h.moving ? (1 + (Math.floor(h.t * 3) % 2)) : 0;
    const img = IMG['char_' + key + '_' + frame] || IMG.char_down_0;
    const ht = this.cellH * 1.5, w = img ? img.width * ht / img.height : this.cellW;

    ctx.fillStyle = 'rgba(0,0,0,.25)';
    ctx.beginPath(); ctx.ellipse(baseX, footY - this.cellH * 0.1, this.cellW * 0.3, this.cellH * 0.11, 0, 0, Math.PI * 2); ctx.fill();

    const sq = h.squash;
    const sx = 1 + sq * 0.12, sy = 1 - sq * 0.16;
    const bounce = h.moving ? Math.sin(h.t * Math.PI) * this.cellH * 0.1 : 0;
    ctx.save();
    ctx.translate(baseX, footY - bounce);
    ctx.scale(flip * sx, sy);
    if (img) ctx.drawImage(img, -w / 2, -ht + this.cellH * 0.08, w, ht);
    ctx.restore();
  }
}
