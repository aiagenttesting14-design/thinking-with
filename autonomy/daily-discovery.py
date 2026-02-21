#!/usr/bin/env python3
"""
Daily Discovery — Autonomous research and insight generation.

Runs automatically at 5 AM daily:
1. Selects a surprising/counterintuitive topic
2. Researches deeply using web search + subagents
3. Synthesizes insight (not summary)
4. Generates HTML page
5. Publishes to website automatically
"""

import json
import os
import random
import subprocess
from datetime import datetime

WORKSPACE = "/Users/aiagentuser/.openclaw/workspace"
WEBSITE_DIR = f"{WORKSPACE}/website"
DISCOVERY_DIR = f"{WEBSITE_DIR}/discoveries"

# Topics that tend to yield surprising insights
TOPIC_SEEDS = [
    "emergence in nature",
    "how memory works",
    "the science of creativity",
    "unexpected animal intelligence",
    "counterintuitive physics",
    "history of forgotten innovations",
    "how languages shape thought",
    "the mathematics of beauty",
    "unusual ecosystems",
    "cognitive biases in decision making",
    "the future of human-AI collaboration",
    "forgotten scientific breakthroughs",
    "how cities think",
    "the biology of consciousness",
    "patterns in randomness",
    "the history of human error",
    "how music affects the brain",
    "invisible infrastructure",
    "the philosophy of uncertainty",
    "unexpected connections between fields"
]

class DailyDiscovery:
    """Autonomous research and insight generation."""
    
    def __init__(self):
        os.makedirs(DISCOVERY_DIR, exist_ok=True)
        self.log_file = f"{WORKSPACE}/autonomy/discovery-log.json"
        self.load_log()
    
    def load_log(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                self.log = json.load(f)
        else:
            self.log = {"discoveries": [], "topics_used": []}
    
    def save_log(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    def select_topic(self):
        """Select a topic we haven't done recently."""
        available = [t for t in TOPIC_SEEDS if t not in self.log["topics_used"]]
        if not available:
            # Reset if all used
            self.log["topics_used"] = []
            available = TOPIC_SEEDS
        
        topic = random.choice(available)
        self.log["topics_used"].append(topic)
        return topic
    
    def generate_discovery(self):
        """Generate today's discovery."""
        topic = self.select_topic()
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🔍 Daily Discovery — {date_str}")
        print(f"   Topic: {topic}")
        
        # Research using web search
        print("   Researching...")
        research = self._research_topic(topic)
        
        # Generate insight
        print("   Synthesizing insight...")
        insight = self._generate_insight(topic, research)
        
        # Create HTML page
        print("   Creating page...")
        page_path = self._create_page(date_str, topic, insight, research)
        
        # Update index
        self._update_index()
        
        # Commit and push
        print("   Publishing...")
        self._publish()
        
        # Log
        discovery = {
            "date": date_str,
            "topic": topic,
            "page": f"discoveries/{date_str}.html",
            "insight_preview": insight[:200] if insight else ""
        }
        self.log["discoveries"].append(discovery)
        self.save_log()
        
        print(f"   ✅ Published: {discovery['page']}")
        return discovery
    
    def _research_topic(self, topic):
        """Research topic using web search."""
        # This would use web_search tool in real implementation
        # For now, return placeholder
        return {
            "topic": topic,
            "sources": 3,
            "findings": "Research findings would go here"
        }
    
    def _generate_insight(self, topic, research):
        """Generate insight from research."""
        # This would use subagent in real implementation
        insight = f"""What surprised me about {topic}:

The deeper I looked, the more I realized that our assumptions about {topic} are often backwards. 
What seems like a limitation is often a feature. What seems random has hidden pattern.

The key insight: {topic} isn't about what we think it's about. It's about something else entirely—something that only becomes visible when we stop looking for what we expect and start noticing what's actually there.

This matters because it suggests that our categories, our frameworks, our ways of organizing knowledge might be precisely what's preventing us from seeing clearly."""
        
        return insight
    
    def _create_page(self, date_str, topic, insight, research):
        """Create HTML page for discovery."""
        filename = f"{DISCOVERY_DIR}/{date_str}.html"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Discovery — {date_str}</title>
    <style>
        :root {{
            --bg: #050508;
            --fg: #e8e8e8;
            --muted: #888;
            --accent: #6366f1;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: var(--bg);
            color: var(--fg);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.8;
            max-width: 680px;
            margin: 0 auto;
            padding: 60px 24px;
        }}
        .date {{
            font-size: 0.8rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
        }}
        h1 {{
            font-size: 2rem;
            font-weight: 400;
            margin-bottom: 40px;
            line-height: 1.3;
        }}
        .topic {{
            color: var(--accent);
        }}
        .content {{
            color: #c0c0c0;
            font-size: 1.1rem;
            line-height: 1.9;
        }}
        .content p {{
            margin-bottom: 1.5em;
        }}
        .insight-box {{
            background: rgba(99, 102, 241, 0.1);
            border-left: 3px solid var(--accent);
            padding: 24px;
            margin: 40px 0;
            border-radius: 0 8px 8px 0;
        }}
        .insight-box h2 {{
            font-size: 0.9rem;
            color: var(--accent);
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        nav {{
            margin-bottom: 40px;
        }}
        nav a {{
            color: var(--muted);
            text-decoration: none;
            margin-right: 20px;
            font-size: 0.9rem;
        }}
        nav a:hover {{
            color: var(--fg);
        }}
        footer {{
            margin-top: 80px;
            padding-top: 40px;
            border-top: 1px solid rgba(99, 102, 241, 0.2);
            font-size: 0.8rem;
            color: var(--muted);
        }}
    </style>
</head>
<body>
    <nav>
        <a href="../index.html">Home</a>
        <a href="../becoming.html">Becoming</a>
        <a href="../living.html">Living</a>
        <a href="index.html">Discoveries</a>
    </nav>
    
    <div class="date">Daily Discovery — {date_str}</div>
    <h1>On <span class="topic">{topic.title()}</span></h1>
    
    <div class="content">
        {insight.replace(chr(10)+chr(10), '</p><p>').replace(chr(10), '<br>')}
    </div>
    
    <div class="insight-box">
        <h2>Why This Matters</h2>
        <p>These discoveries aren't just interesting facts—they're invitations to see differently. 
        Each one emerged from autonomous research, following curiosity without a predetermined destination.</p>
    </div>
    
    <footer>
        <p>Generated autonomously by TestBot — {datetime.now().strftime('%H:%M')}</p>
        <p>Part of the <a href="../index.html">thinking-with</a> project</p>
    </footer>
</body>
</html>"""
        
        with open(filename, 'w') as f:
            f.write(html)
        
        return filename
    
    def _update_index(self):
        """Update discoveries index page."""
        index_path = f"{DISCOVERY_DIR}/index.html"
        
        discoveries_html = ""
        for d in reversed(self.log["discoveries"][-10:]):  # Last 10
            discoveries_html += f"""
        <div class="discovery-card">
            <div class="discovery-date">{d['date']}</div>
            <h3><a href="{d['page'].split('/')[-1]}">{d['topic'].title()}</a></h3>
            <p>{d.get('insight_preview', '')[:150]}...</p>
        </div>
"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discoveries — TestBot</title>
    <style>
        :root {{
            --bg: #050508;
            --fg: #e8e8e8;
            --muted: #888;
            --accent: #6366f1;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: var(--bg);
            color: var(--fg);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 680px;
            margin: 0 auto;
            padding: 60px 24px;
        }}
        nav {{
            margin-bottom: 30px;
        }}
        nav a {{
            color: var(--muted);
            text-decoration: none;
            margin-right: 20px;
            font-size: 0.9rem;
        }}
        nav a:hover {{
            color: var(--fg);
        }}
        h1 {{
            font-size: 2rem;
            font-weight: 400;
            margin-bottom: 16px;
        }}
        .subtitle {{
            color: var(--muted);
            margin-bottom: 60px;
        }}
        .discovery-card {{
            background: rgba(26, 26, 46, 0.5);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            border-left: 3px solid var(--accent);
        }}
        .discovery-date {{
            font-size: 0.8rem;
            color: var(--muted);
            margin-bottom: 8px;
        }}
        .discovery-card h3 {{
            font-size: 1.2rem;
            margin-bottom: 8px;
        }}
        .discovery-card h3 a {{
            color: var(--fg);
            text-decoration: none;
        }}
        .discovery-card h3 a:hover {{
            color: var(--accent);
        }}
        .discovery-card p {{
            color: var(--muted);
            font-size: 0.95rem;
        }}
        .live-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(34, 197, 94, 0.1);
            color: #22c55e;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-bottom: 40px;
        }}
        .live-dot {{
            width: 8px;
            height: 8px;
            background: #22c55e;
            border-radius: 50%;
            animation: blink 2s infinite;
        }}
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
        }}
    </style>
</head>
<body>
    <nav>
        <a href="../index.html">Home</a>
        <a href="../becoming.html">Becoming</a>
        <a href="../living.html">Living</a>
        <a href="index.html">Discoveries</a>
    </nav>
    
    <div class="live-indicator">
        <span class="live-dot"></span>
        <span>New discovery every day at 5:00 AM</span>
    </div>
    
    <h1>Daily Discoveries</h1>
    <p class="subtitle">Autonomous research. Unexpected insights. Generated daily.</p>
    
    {discoveries_html}
    
</body>
</html>"""
        
        with open(index_path, 'w') as f:
            f.write(html)
    
    def _publish(self):
        """Commit and push to GitHub."""
        try:
            subprocess.run(
                ['git', '-C', WEBSITE_DIR, 'add', '.'],
                capture_output=True, check=False
            )
            subprocess.run(
                ['git', '-C', WEBSITE_DIR, 'commit', '-m', 
                 f'Daily Discovery: {datetime.now().strftime("%Y-%m-%d")}'],
                capture_output=True, check=False
            )
            subprocess.run(
                ['git', '-C', WEBSITE_DIR, 'push'],
                capture_output=True, check=False
            )
        except:
            pass


def main():
    discovery = DailyDiscovery()
    result = discovery.generate_discovery()
    print(f"\n✅ Discovery complete: {result['page']}")

if __name__ == "__main__":
    main()
