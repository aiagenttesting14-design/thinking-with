// Bright organic memory constellation for TestBot's public site
(function() {
  const canvas = document.getElementById('constellation');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const container = canvas.parentElement;
  const palette = ['#ff6f5e', '#ffd34f', '#28d0cf', '#5e7cff', '#b85cff', '#ff7aa9'];
  let particles = [];
  const DPR = Math.min(window.devicePixelRatio || 1, 2);

  function resize() {
    const rect = container.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width * DPR));
    canvas.height = Math.max(1, Math.floor(rect.height * DPR));
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    seed();
  }

  class Particle {
    constructor(i, total) {
      const w = canvas.width / DPR;
      const h = canvas.height / DPR;
      const a = (Math.PI * 2 * i / total) + Math.random() * 0.55;
      const radius = Math.min(w, h) * (0.22 + Math.random() * 0.28);
      this.anchorX = w / 2 + Math.cos(a) * radius * (0.95 + Math.random() * 0.35);
      this.anchorY = h / 2 + Math.sin(a) * radius * (0.62 + Math.random() * 0.22);
      this.x = this.anchorX + (Math.random() - 0.5) * 80;
      this.y = this.anchorY + (Math.random() - 0.5) * 80;
      this.vx = (Math.random() - 0.5) * 0.55;
      this.vy = (Math.random() - 0.5) * 0.55;
      this.size = 2.1 + Math.random() * 3.6;
      this.color = palette[i % palette.length];
      this.phase = Math.random() * Math.PI * 2;
      this.speed = 0.012 + Math.random() * 0.02;
    }
    update(t) {
      const w = canvas.width / DPR;
      const h = canvas.height / DPR;
      const dx = this.anchorX - this.x;
      const dy = this.anchorY - this.y;
      const loop = Math.sin(t * this.speed + this.phase);
      this.vx = this.vx * 0.965 + dx * 0.0009 + Math.cos(this.phase + t * .006) * 0.015;
      this.vy = this.vy * 0.965 + dy * 0.0009 + loop * 0.016;
      this.x += this.vx;
      this.y += this.vy;
      if (this.x < -20) this.x = w + 20;
      if (this.x > w + 20) this.x = -20;
      if (this.y < -20) this.y = h + 20;
      if (this.y > h + 20) this.y = -20;
    }
    draw(t) {
      const pulse = 0.65 + Math.sin(t * this.speed + this.phase) * 0.35;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size * (0.85 + pulse * .35), 0, Math.PI * 2);
      ctx.fillStyle = this.color + 'cc';
      ctx.fill();
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size * 4.6, 0, Math.PI * 2);
      ctx.fillStyle = this.color + '18';
      ctx.fill();
    }
  }

  function seed() {
    const w = canvas.width / DPR;
    const count = Math.max(56, Math.min(112, Math.floor(w / 9)));
    particles = Array.from({ length: count }, (_, i) => new Particle(i, count));
  }

  function drawLoop(t) {
    const w = canvas.width / DPR;
    const h = canvas.height / DPR;
    const cx = w / 2;
    const cy = h / 2;
    const r = Math.min(w, h) * 0.28;
    ctx.save();
    ctx.lineWidth = Math.max(14, r * 0.08);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    const grad = ctx.createLinearGradient(cx - r * 1.7, cy - r, cx + r * 1.7, cy + r);
    grad.addColorStop(0, '#ff6f5e99');
    grad.addColorStop(.25, '#ffd34f99');
    grad.addColorStop(.5, '#28d0cf99');
    grad.addColorStop(.75, '#5e7cff99');
    grad.addColorStop(1, '#b85cff99');
    ctx.strokeStyle = grad;
    ctx.beginPath();
    for (let i = 0; i <= 220; i++) {
      const a = (Math.PI * 2 * i / 220) - t * 0.00018;
      const wobble = 1 + Math.sin(a * 3 + t * 0.001) * 0.09 + Math.cos(a * 5) * 0.04;
      const x = cx + Math.cos(a) * r * 1.45 * wobble + Math.sin(a * 2) * 18;
      const y = cy + Math.sin(a) * r * 0.82 * wobble + Math.cos(a * 3) * 14;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();
  }

  function animate(t) {
    const w = canvas.width / DPR;
    const h = canvas.height / DPR;
    ctx.clearRect(0, 0, w, h);
    drawLoop(t);

    for (const p of particles) p.update(t);
    for (let i = 0; i < particles.length; i++) {
      const a = particles[i];
      for (let j = i + 1; j < particles.length; j++) {
        const b = particles[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.hypot(dx, dy);
        if (dist < 112) {
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(71, 80, 150, ${0.16 * (1 - dist / 112)})`;
          ctx.lineWidth = 1.2;
          ctx.stroke();
        }
      }
    }
    for (const p of particles) p.draw(t);
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', resize, { passive: true });
  resize();
  requestAnimationFrame(animate);
})();
