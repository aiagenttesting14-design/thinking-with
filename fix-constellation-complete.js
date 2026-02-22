// Complete fix for constellation visualization
const fs = require('fs');

// Read the current index.html
let content = fs.readFileSync('index.html', 'utf8');

// Find the constellation JavaScript section
const startMarker = '// Create constellation';
const endMarker = '// End constellation';

const startIdx = content.indexOf(startMarker);
const endIdx = content.indexOf(endMarker, startIdx);

if (startIdx !== -1 && endIdx !== -1) {
    // Create clean, working constellation code
    const cleanConstellation = `// Create constellation
    const canvas = document.getElementById('constellation-canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to container
    function resizeCanvas() {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        initParticles(); // Reinitialize particles on resize
    }
    
    // Initialize particles array
    let particles = [];
    const PARTICLE_COUNT = 60; // Reduced for better mobile performance
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.hue = Math.random() * 60 + 200; // Blues and purples
            this.phase = Math.random() * Math.PI * 2;
            this.pulseSpeed = 0.01 + Math.random() * 0.02;
            this.radius = 1 + Math.random() * 2;
        }
        
        update() {
            // Simple boundary checking with bounce
            if (this.x < 0 || this.x > canvas.width) this.vx *= -0.8;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -0.8;
            
            // Apply velocity
            this.x += this.vx;
            this.y += this.vy;
            
            // Add subtle random motion
            this.vx += (Math.random() - 0.5) * 0.02;
            this.vy += (Math.random() - 0.5) * 0.02;
            
            // Dampen velocity
            this.vx *= 0.99;
            this.vy *= 0.99;
            
            // Keep within bounds
            this.x = Math.max(0, Math.min(canvas.width, this.x));
            this.y = Math.max(0, Math.min(canvas.height, this.y));
        }
        
        draw() {
            const pulse = 0.7 + 0.3 * Math.sin(Date.now() * 0.001 * this.pulseSpeed + this.phase);
            const radius = this.radius * pulse;
            
            // Draw particle
            ctx.beginPath();
            ctx.arc(this.x, this.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = \`hsla(\${this.hue}, 70%, 60%, 0.7)\`;
            ctx.fill();
            
            // Draw glow
            ctx.beginPath();
            ctx.arc(this.x, this.y, radius * 2, 0, Math.PI * 2);
            ctx.fillStyle = \`hsla(\${this.hue}, 50%, 60%, 0.2)\`;
            ctx.fill();
        }
        
        drawConnections() {
            // Draw connections to nearby particles
            for (let other of particles) {
                if (other === this) continue;
                const dx = other.x - this.x;
                const dy = other.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 120) { // Connection distance
                    ctx.beginPath();
                    ctx.moveTo(this.x, this.y);
                    ctx.lineTo(other.x, other.y);
                    ctx.strokeStyle = \`hsla(\${this.hue}, 50%, 60%, \${0.15 * (1 - dist/120)})\`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }
    
    function initParticles() {
        particles = [];
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            particles.push(new Particle());
        }
    }
    
    // Animation loop
    function animate() {
        // Clear with slight fade for trail effect
        ctx.fillStyle = 'rgba(5, 5, 8, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Update and draw all particles
        for (let particle of particles) {
            particle.update();
        }
        
        // Draw connections first (behind particles)
        for (let particle of particles) {
            particle.drawConnections();
        }
        
        // Draw particles on top
        for (let particle of particles) {
            particle.draw();
        }
        
        requestAnimationFrame(animate);
    }
    
    // Initialize and start animation
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    animate();
    
    // Add click interaction
    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Add a burst of particles at click location
        for (let i = 0; i < 5; i++) {
            const p = new Particle();
            p.x = x;
            p.y = y;
            p.vx = (Math.random() - 0.5) * 2;
            p.vy = (Math.random() - 0.5) * 2;
            p.radius = 1 + Math.random() * 3;
            particles.push(p);
        }
        
        // Keep particle count manageable
        if (particles.length > 100) {
            particles = particles.slice(-80);
        }
    });
// End constellation`;

    // Replace the problematic section
    content = content.substring(0, startIdx) + cleanConstellation + content.substring(endIdx + endMarker.length);
    
    // Write the fixed content back
    fs.writeFileSync('index.html', content);
    console.log('Completely rewrote constellation JavaScript with clean, working code');
} else {
    console.log('Could not find constellation section markers');
}
