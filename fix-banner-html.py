#!/usr/bin/env python3
"""
Fix missing banner HTML
"""

with open('index.html', 'r') as f:
    content = f.read()

# Find the exact location where banner should go
# After </header> and before <main>
header_end = content.find('</header>')
if header_end != -1:
    # Find the next <main> tag
    main_start = content.find('<main>', header_end)
    
    if main_start != -1:
        # Insert banner HTML
        banner_html = '''
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
    
    '''
        
        content = content[:main_start] + banner_html + content[main_start:]

# Write updated content
with open('index.html', 'w') as f:
    f.write(content)

print("Banner HTML added")
