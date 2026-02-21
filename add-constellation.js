// Add constellation background to homepage
document.addEventListener('DOMContentLoaded', function() {
    // Create constellation container
    const constellation = document.createElement('div');
    constellation.className = 'constellation-bg';
    constellation.id = 'constellation-bg';
    
    // Add to body
    document.body.appendChild(constellation);
    
    // Create particles (simplified version)
    const particleCount = 40;
    const linesCount = 15;
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'constellation-particle';
        
        // Random position
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        const size = 1 + Math.random() * 3;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${x}%`;
        particle.style.top = `${y}%`;
        
        // Random animation delay
        particle.style.animationDelay = `${Math.random() * 4}s`;
        
        constellation.appendChild(particle);
    }
    
    // Create some connecting lines
    for (let i = 0; i < linesCount; i++) {
        const line = document.createElement('div');
        line.className = 'constellation-line';
        
        // Random start and end points
        const x1 = Math.random() * 100;
        const y1 = Math.random() * 100;
        const x2 = Math.random() * 100;
        const y2 = Math.random() * 100;
        
        // Calculate distance and angle
        const dx = x2 - x1;
        const dy = y2 - y1;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.atan2(dy, dx) * 180 / Math.PI;
        
        line.style.width = `${distance}%`;
        line.style.height = '1px';
        line.style.left = `${x1}%`;
        line.style.top = `${y1}%`;
        line.style.transform = `rotate(${angle}deg)`;
        line.style.opacity = 0.05 + Math.random() * 0.1;
        
        constellation.appendChild(line);
    }
    
    // Set state based on time of day (simplified)
    const hour = new Date().getHours();
    if (hour >= 9 && hour <= 17) {
        document.body.classList.add('state-active');
    } else if (hour >= 18 && hour <= 22) {
        document.body.classList.add('state-thinking');
    } else {
        document.body.classList.add('state-calm');
    }
    
    console.log('Constellation background added to homepage');
});
