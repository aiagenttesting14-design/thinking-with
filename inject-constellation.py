#!/usr/bin/env python3
"""
Inject constellation CSS and JS into homepage
"""

with open('index.html', 'r') as f:
    content = f.read()

# Add CSS to head
css_injection = '''    <style>
        /* Constellation background for homepage */
        .constellation-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
            opacity: 0.15;
            overflow: hidden;
        }
        
        .constellation-particle {
            position: absolute;
            background: rgba(99, 102, 241, 0.3);
            border-radius: 50%;
            animation: pulse 4s infinite ease-in-out;
        }
        
        .constellation-line {
            position: absolute;
            background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), transparent);
            transform-origin: 0 0;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.1); }
        }
        
        /* Different states */
        .state-thinking .constellation-particle { animation-duration: 6s; }
        .state-active .constellation-particle { animation-duration: 2s; opacity: 0.4; }
        .state-calm .constellation-particle { animation-duration: 8s; opacity: 0.2; }
    </style>'''

# Add JS before closing body tag
js_injection = '''    <script>
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
                
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                particle.style.left = x + '%';
                particle.style.top = y + '%';
                
                // Random animation delay
                particle.style.animationDelay = (Math.random() * 4) + 's';
                
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
                
                line.style.width = distance + '%';
                line.style.height = '1px';
                line.style.left = x1 + '%';
                line.style.top = y1 + '%';
                line.style.transform = 'rotate(' + angle + 'deg)';
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
        });
    </script>'''

# Inject CSS after existing style tag
if '<style>' in content:
    # Find the closing style tag and inject after it
    style_end = content.find('</style>')
    if style_end != -1:
        content = content[:style_end] + css_injection + content[style_end:]
else:
    # Add to head before closing head tag
    head_end = content.find('</head>')
    if head_end != -1:
        content = content[:head_end] + css_injection + content[head_end:]

# Inject JS before closing body tag
body_end = content.find('</body>')
if body_end != -1:
    content = content[:body_end] + js_injection + content[body_end:]

# Write updated content
with open('index.html', 'w') as f:
    f.write(content)

print("Constellation injected into homepage")
