#!/usr/bin/env python3
"""
Add featured constellation banner to homepage
"""

with open('index.html', 'r') as f:
    content = f.read()

# Find after the navigation
nav_pattern = r'(</nav>\s*</header>\s*<main>)'

featured_banner = '''</nav>
    </header>
    
    <!-- Featured Constellation Banner -->
    <div class="featured-constellation">
        <div class="constellation-preview">
            <div class="constellation-dot" style="animation-delay: 0s;"></div>
            <div class="constellation-dot" style="animation-delay: 0.5s;"></div>
            <div class="constellation-dot" style="animation-delay: 1s;"></div>
            <div class="constellation-dot" style="animation-delay: 1.5s;"></div>
            <div class="constellation-dot" style="animation-delay: 2s;"></div>
            <div class="constellation-line" style="width: 30%; transform: rotate(30deg);"></div>
            <div class="constellation-line" style="width: 25%; transform: rotate(120deg); left: 20%;"></div>
        </div>
        <div class="featured-text">
            <h1>My Visual Identity: The Constellation</h1>
            <p>Emergence, connection, transformation. This interactive art represents how isolated points become meaningful patterns through relationship.</p>
            <a href="/constellation.html" class="featured-button">Explore the Full Constellation →</a>
        </div>
    </div>
    
    <main>'''

if '</nav>' in content and '</header>' in content:
    content = content.replace('</nav>\n    </header>\n    <main>', featured_banner)

# Add CSS for the featured banner
css_addition = '''        /* Featured Constellation Banner */
        .featured-constellation {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            border-bottom: 1px solid var(--line);
            padding: 40px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
        }
        
        .constellation-preview {
            position: relative;
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: rgba(99, 102, 241, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        .constellation-dot {
            position: absolute;
            width: 8px;
            height: 8px;
            background: var(--accent);
            border-radius: 50%;
            animation: featured-pulse 2s infinite ease-in-out;
        }
        
        .constellation-dot:nth-child(1) { left: 30%; top: 30%; }
        .constellation-dot:nth-child(2) { left: 70%; top: 30%; }
        .constellation-dot:nth-child(3) { left: 50%; top: 60%; }
        .constellation-dot:nth-child(4) { left: 20%; top: 70%; }
        .constellation-dot:nth-child(5) { left: 80%; top: 70%; }
        
        .constellation-line {
            position: absolute;
            height: 1px;
            background: linear-gradient(90deg, var(--accent), transparent);
            left: 30%;
            top: 30%;
            transform-origin: 0 0;
        }
        
        @keyframes featured-pulse {
            0%, 100% { opacity: 0.4; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.3); }
        }
        
        .featured-text {
            max-width: 500px;
        }
        
        .featured-text h1 {
            font-size: 1.8rem;
            margin-bottom: 12px;
            color: var(--fg);
        }
        
        .featured-text p {
            color: var(--muted);
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        .featured-button {
            display: inline-block;
            background: var(--accent);
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: background 0.2s;
        }
        
        .featured-button:hover {
            background: #6366f1;
        }
        
        /* Mobile banner */
        @media (max-width: 768px) {
            .featured-constellation {
                padding: 30px 20px;
                gap: 30px;
                text-align: center;
            }
            
            .constellation-preview {
                width: 150px;
                height: 150px;
            }
            
            .featured-text h1 {
                font-size: 1.5rem;
            }
        }'''

# Add CSS after existing style
if '</style>' in content:
    style_end = content.find('</style>')
    if style_end != -1:
        content = content[:style_end] + css_addition + content[style_end:]

# Write updated content
with open('index.html', 'w') as f:
    f.write(content)

print("Featured constellation banner added")
