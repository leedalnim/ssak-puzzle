// 파티클 — 청소할 때 먼지가 흩어지고 반짝이는 연출.
// 게임의 '손맛'과 시각적 만족감을 담당.
import { IMG } from './assets.js';

export class Particles {
  constructor() { this.list = []; this.anims = []; }

  // 스프라이트 이펙트 버스트(프레임 시퀀스를 한 번 재생)
  spriteBurst(keys, x, y, size, dur = 0.45) {
    const frames = keys.map(k => IMG[k]).filter(Boolean);
    if (!frames.length) return;
    this.anims.push({ frames, x, y, size, dur, t: 0 });
  }

  // 먼지 버스트 (한 칸 닦을 때)
  dust(x, y, tint = '#b9a98a', amount = 8) {
    for (let i = 0; i < amount; i++) {
      const a = Math.random() * Math.PI * 2;
      const sp = 12 + Math.random() * 34;
      this.list.push({
        x, y,
        vx: Math.cos(a) * sp,
        vy: Math.sin(a) * sp - 14,
        g: 60,
        life: 0.4 + Math.random() * 0.3,
        t: 0,
        size: 1 + Math.random() * 2,
        color: tint,
        kind: 'dust',
      });
    }
  }

  // 반짝이 (타일이 완전히 깨끗해질 때)
  sparkle(x, y, amount = 6) {
    for (let i = 0; i < amount; i++) {
      const a = Math.random() * Math.PI * 2;
      const sp = 18 + Math.random() * 30;
      this.list.push({
        x, y,
        vx: Math.cos(a) * sp,
        vy: Math.sin(a) * sp - 20,
        g: 24,
        life: 0.5 + Math.random() * 0.4,
        t: 0,
        size: 1.5 + Math.random() * 1.5,
        color: Math.random() < 0.5 ? '#fff7d6' : '#ffe9a8',
        kind: 'star',
      });
    }
  }

  // 클리어 시 화면 전체 색종이
  confetti(w, h, amount = 60) {
    const colors = ['#f0d66e', '#7eb0aa', '#f4c79b', '#e8a07a', '#fff7d6'];
    for (let i = 0; i < amount; i++) {
      this.list.push({
        x: Math.random() * w,
        y: -10 - Math.random() * h * 0.3,
        vx: (Math.random() * 2 - 1) * 30,
        vy: 40 + Math.random() * 60,
        g: 40,
        life: 1.6 + Math.random() * 1.2,
        t: 0,
        size: 2 + Math.random() * 3,
        color: colors[(Math.random() * colors.length) | 0],
        kind: 'confetti',
        rot: Math.random() * Math.PI,
        vr: (Math.random() * 2 - 1) * 6,
      });
    }
  }

  update(dt) {
    for (let i = this.list.length - 1; i >= 0; i--) {
      const p = this.list[i];
      p.t += dt;
      if (p.t >= p.life) { this.list.splice(i, 1); continue; }
      p.vy += p.g * dt;
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      if (p.kind === 'confetti') p.rot += p.vr * dt;
    }
    for (let i = this.anims.length - 1; i >= 0; i--) {
      const a = this.anims[i];
      a.t += dt;
      if (a.t >= a.dur) this.anims.splice(i, 1);
    }
  }

  draw(ctx) {
    for (const p of this.list) {
      const k = 1 - p.t / p.life;
      ctx.globalAlpha = Math.max(0, k);
      ctx.fillStyle = p.color;
      if (p.kind === 'confetti') {
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.fillRect(-p.size, -p.size * 0.5, p.size * 2, p.size);
        ctx.restore();
      } else if (p.kind === 'star') {
        const s = p.size * (0.6 + 0.4 * Math.sin(p.t * 30));
        ctx.fillRect(p.x - s, p.y - 0.5, s * 2, 1);
        ctx.fillRect(p.x - 0.5, p.y - s, 1, s * 2);
      } else {
        ctx.fillRect(p.x - p.size / 2, p.y - p.size / 2, p.size, p.size);
      }
    }
    ctx.globalAlpha = 1;
    // 스프라이트 이펙트
    for (const a of this.anims) {
      const k = a.t / a.dur;
      const fi = Math.min(a.frames.length - 1, Math.floor(k * a.frames.length));
      const img = a.frames[fi];
      const w = a.size, h = img.height * w / img.width;
      ctx.globalAlpha = Math.max(0, 1 - Math.pow(k, 2.2));
      ctx.drawImage(img, a.x - w / 2, a.y - h / 2, w, h);
    }
    ctx.globalAlpha = 1;
  }

  clear() { this.list.length = 0; this.anims.length = 0; }
}
