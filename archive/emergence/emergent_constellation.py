#!/usr/bin/env python3
"""
Emergent Constellation Generator
Creating beauty from simple rules, rendered as SVG.
"""
import math
import random

def hsv_to_hex(h, s, v):
    """Convert HSV to hex color."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h/60) % 2 - 1))
    m = v - c
    
    if h < 60: r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    else: r, g, b = c, 0, x
    
    return '#{:02x}{:02x}{:02x}'.format(
        int((r+m)*255), int((g+m)*255), int((b+m)*255))

class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'hue', 'phase']
    def __init__(self, width, height):
        self.x = random.random() * width
        self.y = random.random() * height
        self.vx = (random.random() - 0.5) * 1.2
        self.vy = (random.random() - 0.5) * 1.2
        self.hue = random.random() * 80 + 180  # blues, purples
        self.phase = random.random() * 2 * math.pi

class Constellation:
    def __init__(self, n=80, w=1200, h=750):
        self.w, self.h = w, h
        self.particles = [Particle(w, h) for _ in range(n)]
        
    def step(self):
        for p in self.particles:
            fx = fy = 0
            for o in self.particles:
                if p is o: continue
                dx, dy = o.x - p.x, o.y - p.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist == 0: continue
                # Attraction
                if 10 < dist < 150:
                    f = (150 - dist) / 150 * 0.05
                    fx += dx/dist * f
                    fy += dy/dist * f
                # Repulsion
                if dist < 20:
                    f = (20 - dist) / 20 * 0.3
                    fx -= dx/dist * f
                    fy -= dy/dist * f
            p.vx = (p.vx + fx) * 0.96
            p.vy = (p.vy + fy) * 0.96
            p.x += p.vx
            p.y += p.vy
            # Wrap
            p.x = p.x % self.w
            p.y = p.y % self.h
            p.phase += 0.03
    
    def to_svg(self, title=""):
        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}">',
            f'<rect width="{self.w}" height="{self.h}" fill="#050508"/>',
            '<defs>',
            '  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/>',
            '    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>',
            '  </filter>',
            '</defs>'
        ]
        
        # Connections
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                dx, dy = p2.x - p1.x, p2.y - p1.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 100:
                    opacity = (1 - dist/100) * 0.5
                    hue = (p1.hue + p2.hue) / 2
                    color = hsv_to_hex(hue, 0.5, 0.6)
                    lines.append(f'<line x1="{p1.x:.1f}" y1="{p1.y:.1f}" x2="{p2.x:.1f}" y2="{p2.y:.1f}" '
                               f'stroke="{color}" stroke-opacity="{opacity:.2f}" stroke-width="1"/>')
        
        # Particles
        for p in self.particles:
            brightness = 0.6 + math.sin(p.phase) * 0.15
            color = hsv_to_hex(p.hue, 0.8, brightness)
            lines.append(f'<circle cx="{p.x:.1f}" cy="{p.y:.1f}" r="4" fill="{color}" filter="url(#glow)"/>')
            lines.append(f'<circle cx="{p.x:.1f}" cy="{p.y:.1f}" r="2" fill="#fff" opacity="0.8"/>')
        
        if title:
            lines.append(f'<text x="20" y="30" fill="#668" font-family="monospace" font-size="14">{title}</text>')
        lines.append('</svg>')
        return '\n'.join(lines)

# Generate evolution
print("🌌 Emergent Constellation Generator")
print("=" * 45)
print("\nEach particle follows only 3 rules:")
print("  1. Move toward neighbors (10-150px away)")
print("  2. Move away if too close (<20px)")
print("  3. Keep some momentum (damping)")
print("\nNo leader. No plan. Watch what emerges.\n")

c = Constellation(n=80, w=1200, h=750)
milestones = [
    (0, "t=0", "Pure chaos. Random positions, random velocities."),
    (40, "t=40", "Clumping begins. Weak attraction creates seeds."),
    (100, "t=100", "Structure emerges. Groups stabilize."),
    (200, "t=200", "Refinement. Excess energy dissipates."),
    (350, "t=350", "Mature constellation. Living geometry.")
]

for step in range(400):
    c.step()
    for target, label, desc in milestones:
        if step == target:
            svg = c.to_svg(f"{label}: {desc}")
            fname = f"constellation_{target:03d}.svg"
            with open(fname, 'w') as f:
                f.write(svg)
            print(f"  ✓ {fname} - {desc}")

# Create final poster
print("\n📸 Creating composite timeline...")
c2 = Constellation(n=80, w=1200, h=750)
frames = []
for step in range(350):
    c2.step()
    if step in [0, 87, 175, 262, 349]:
        frames.append(c2.particles.copy())

# Build composite SVG
comp_w, comp_h = 2500, 1600
cell_w, cell_h = 1200, 750
lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {comp_w} {comp_h}">',
    f'<rect width="{comp_w}" height="{comp_h}" fill="#020205"/>',
    '<defs>',
    '  <filter id="glow"><feGaussianBlur stdDeviation="2.5" result="b"/>',
    '    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
    '</defs>',
    '<text x="50" y="50" fill="#9ab" font-family="monospace" font-size="24" font-weight="bold">EMERGENCE</text>',
    '<text x="50" y="75" fill="#668" font-family="monospace" font-size="12">Simple rules → Complex beauty</text>'
]

labels = ["t=0", "t=87", "t=175", "t=262", "t=349"]
positions = [(50, 100), (1300, 100), (50, 900), (1300, 900), (675, 900)]

for idx, (particles, label, (ox, oy)) in enumerate(zip(frames, labels, positions)):
    # Draw frame
    for i, p1 in enumerate(particles):
        for p2 in particles[i+1:]:
            dx, dy = p2.x - p1.x, p2.y - p1.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 100:
                op = (1 - dist/100) * 0.5
                hue = (p1.hue + p2.hue) / 2
                color = hsv_to_hex(hue, 0.5, 0.6)
                lines.append(f'<line x1="{ox+p1.x:.1f}" y1="{oy+p1.y:.1f}" x2="{ox+p2.x:.1f}" y2="{oy+p2.y:.1f}" '
                           f'stroke="{color}" stroke-opacity="{op:.2f}" stroke-width="0.8"/>')
    for p in particles:
        bright = 0.6 + math.sin(p.phase) * 0.15
        color = hsv_to_hex(p.hue, 0.8, bright)
        lines.append(f'<circle cx="{ox+p.x:.1f}" cy="{oy+p.y:.1f}" r="3" fill="{color}" filter="url(#glow)"/>')
    lines.append(f'<text x="{ox+20}" y="{oy+30}" fill="#668" font-family="monospace" font-size="14">{label}</text>')

lines.append('</svg>')

with open('constellation_poster.svg', 'w') as f:
    f.write('\n'.join(lines))

print("  ✓ constellation_poster.svg - Evolution timeline")
print("\n" + "=" * 45)
print("Files created:")
print("  • constellation_000.svg → constellation_350.svg (individual frames)")
print("  • constellation_poster.svg (composite timeline)")
print("\nOpen any SVG to view the emergent structure.")
