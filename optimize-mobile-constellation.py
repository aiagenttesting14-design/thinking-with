#!/usr/bin/env python3
"""
Optimize constellation for mobile screens
"""

with open('index.html', 'r') as f:
    content = f.read()

# Find the constellation CSS and add mobile optimizations
css_pattern = r'(@keyframes pulse \{[\s\S]*?\})'

mobile_css = '''        /* Mobile optimization */
        @media (max-width: 768px) {
            .constellation-bg {
                opacity: 0.25 !important;
            }
            
            .constellation-particle {
                width: 6px !important;
                height: 6px !important;
                background: rgba(99, 102, 241, 0.4) !important;
                animation-duration: 3s !important;
            }
            
            .constellation-line {
                height: 2px !important;
                opacity: 0.15 !important;
            }
            
            /* Mobile always shows active state */
            .state-thinking .constellation-particle,
            .state-active .constellation-particle,
            .state-calm .constellation-particle {
                animation-duration: 3s !important;
                opacity: 0.4 !important;
            }
        }
        
        /* Desktop stays subtle */
        @media (min-width: 769px) {
            .constellation-bg {
                opacity: 0.15;
            }
            
            .constellation-particle {
                width: 3px;
                height: 3px;
            }
        }'''

# Add mobile CSS after the existing constellation CSS
if '@keyframes pulse' in content:
    # Find where to insert (after the closing brace of @keyframes)
    pulse_end = content.find('@keyframes pulse')
    if pulse_end != -1:
        # Find the closing brace
        brace_count = 0
        insert_pos = pulse_end
        for i in range(pulse_end, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    insert_pos = i + 1
                    break
        
        content = content[:insert_pos] + '\n' + mobile_css + content[insert_pos:]

# Also update the JS to create fewer particles on mobile
js_pattern = r'(const particleCount = 40;)'

mobile_js = '''            // Adjust for mobile
            const isMobile = window.innerWidth <= 768;
            const particleCount = isMobile ? 25 : 40;
            const linesCount = isMobile ? 10 : 15;
            const particleSize = isMobile ? 6 : 3;'''

if 'const particleCount = 40;' in content:
    content = content.replace('const particleCount = 40;', mobile_js)

# Write updated content
with open('index.html', 'w') as f:
    f.write(content)

print("Mobile optimization added to constellation")
