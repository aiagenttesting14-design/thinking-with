// Constellation Particle Simulation
(function() {
  const canvas = document.getElementById('constellation');
  const ctx = canvas.getContext('2d');
  const container = canvas.parentElement;
  
  // Set initial dimensions
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
  
  const N = 120;
  const particles = [];
  
  class Particle {
    constructor() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.vx = (Math.random() - 0.5) * 0.8;
      this.vy = (Math.random() - 0.5) * 0.8;
      this.hue = Math.random() * 80 + 180; // blues, purples, teals
      this.phase = Math.random() * Math.PI * 2;
      this.pulseSpeed = 0.02 + Math.random() * 0.03;
    }
    
    update() {
      let fx = 0, fy = 0;
      
      // Forces from other particles
      for (let other of particles) {
        if (other === this) continue;
        let dx = other.x - this.x;
        let dy = other.y - this.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        
        // Attraction at medium distances (creates clusters)
        if (dist < 180 && dist > 8) {
          let force = (180 - dist) / 180;
          fx += (dx/dist) * force * 0.025;
          fy += (dy/dist) * force * 0.025;
        }
        // Repulsion at close distances (prevents collapse)
        if (dist < 25) {
          let force = (25 - dist) / 25;
          fx -= (dx/dist) * force * 0.15;
          fy -= (dy/dist) * force * 0.15;
        }
      }
      
      // Damping
      this.vx = this.vx * 0.98 + fx;
      this.vy = this.vy * 0.98 + fy;
      
      // Update position
      this.x += this.vx;
      this.y += this.vy;
      
      // Wrap edges
      if (this.x < 0) this.x += canvas.width;
      if (this.x > canvas.width) this.x -= canvas.width;
      if (this.y < 0) this.y += canvas.height;
      if (this.y > canvas.height) this.y -= canvas.height;
      
      this.phase += this.pulseSpeed;
    }
    
    draw() {
      const radius = 1.8 + Math.sin(this.phase) * 0.6;
      ctx.beginPath();
      ctx.arc(this.x, this.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${this.hue}, 70%, 60%, 0.7)`;
      ctx.fill();
      
      // Draw connections to nearby particles
      for (let other of particles) {
        if (other === this) continue;
        let dx = other.x - this.x;
        let dy = other.y - this.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 80) {
          ctx.beginPath();
          ctx.moveTo(this.x, this.y);
          ctx.lineTo(other.x, other.y);
          ctx.strokeStyle = `hsla(${this.hue}, 50%, 60%, ${0.15 * (1 - dist/80)})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }
  }
  
  // Initialize particles
  for (let i = 0; i < N; i++) particles.push(new Particle());
  
  function animate() {
    ctx.fillStyle = 'rgba(5, 5, 8, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    for (let p of particles) p.update();
    for (let p of particles) p.draw();
    
    requestAnimationFrame(animate);
  }
  
  // Handle resize
  window.addEventListener('resize', () => {
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
    for (let p of particles) {
      p.x = Math.random() * canvas.width;
      p.y = Math.random() * canvas.height;
    }
  });
  
  animate();
})();
