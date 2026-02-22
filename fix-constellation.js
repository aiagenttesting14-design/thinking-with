// Fix constellation code on homepage
const fs = require('fs');

// Read the current index.html
let content = fs.readFileSync('index.html', 'utf8');

// Find and fix the JavaScript errors
// Problem 1: Duplicate 'linesCount' variable declaration
content = content.replace(
    'const linesCount = isMobile ? 10 : 15;\n            const particleSize = isMobile ? 6 : 3;\n            const linesCount = 15;',
    'const linesCount = isMobile ? 10 : 15;\n            const particleSize = isMobile ? 6 : 3;'
);

// Problem 2: Duplicate 'const N' declarations
content = content.replace(
    'const N = 80; // Fewer particles for performance\n    const particles = [];\n\nconst N = 120, particles = [];',
    'const N = 80; // Fewer particles for performance\n    const particles = [];'
);

// Problem 3: Remove duplicate class Particle declaration
// This is more complex - let's find and fix the entire constellation canvas section
const startMarker = '// Create constellation';
const endMarker = '// End constellation';

const startIndex = content.indexOf(startMarker);
const endIndex = content.indexOf(endMarker, startIndex);

if (startIndex !== -1 && endIndex !== -1) {
    // Extract the problematic section
    const before = content.substring(0, startIndex);
    const after = content.substring(endIndex + endMarker.length);
    
    // Create fixed constellation code
    const fixedConstellation = `// Create constellation
    const canvas = document.getElementById('constellation-canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to container
    function resizeCanvas() {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    const N = 80; // Fewer particles for performance
    const particles = [];

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.hue = Math.random() * 60 + 200; // Blues and purples
            this.phase = Math.random() * Math.PI * 2;
            this.pulseSpeed = 0.01 + Math.random() * 0.02;
            this.radius = 1 + Math.random() * 2;
        }
        
        update() {
            // Simple boundary checking
            if (this.x < 0 || this.x > canvas.width) this.vx *= -0.8;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -0.8;
            
            // Apply velocity
            this.x += this.vx;
            this.y += this.vy;
            
            // Add some random motion
            this.vx += (Math.random() - 0.5) * 0.05;
            this.vy += (Math.random() - 0.5) * 0.05;
            
            // Dampen velocity
            this.vx *= 0.98;
            this.vy *= 0.98;
            
            // Keep within bounds
            this.x = Math.max(0, Math.min(canvas.width, this.x));
            this.y = Math.max(0, Math.min(canvas.height, this.y));
        }
        
        draw() {
            const pulse = 0.7 + 0.3 * Math.sin(Date.now() * 0.001 * this.pulseSpeed + this.phase);
            const radius = this.radius * pulse;
            
            ctx.beginPath();
            ctx.arc(this.x, this.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = \`hsla(\${this.hue}, 70%, 60%, 0.6)\`;
            ctx.fill();
            
            // Draw connections to nearby particles
            for (let other of particles) {
                if (other === this) continue;
                const dx = other.x - this.x;
                const dy = other.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 100) {
                    ctx.beginPath();
                    ctx.moveTo(this.x, this.y);
                    ctx.lineTo(other.x, other.y);
                    ctx.strokeStyle = \`hsla(\${this.hue}, 50%, 60%, \${0.1 * (1 - dist/100)})\`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }
    
    // Initialize particles
    for (let i = 0; i < N; i++) {
        particles.push(new Particle());
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update and draw all particles
        for (let particle of particles) {
            particle.update();
            particle.draw();
        }
        
        requestAnimationFrame(animate);
    }
    
    animate();
// End constellation`;

    content = before + fixedConstellation + after;
}

// Write the fixed content back
fs.writeFileSync('index.html', content);
console.log('Fixed constellation code in index.html');
