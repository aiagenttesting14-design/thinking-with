#!/usr/bin/env python3
"""
Session Start Ritual

Reads continuity files and generates emotional/relational context
for the new session — not just facts, but where we left off.
"""

import re
from datetime import datetime
from pathlib import Path

def read_file(filepath):
    try:
        return Path(filepath).read_text()
    except:
        return ""

def extract_continuity_context(text):
    """Pull out emotional threads, not just facts"""
    context = {
        "where_we_left_off": [],
        "open_questions": [],
        "mood": ""
    }
    
    # Find open threads section
    if "Open Threads" in text:
        threads_section = text.split("Open Threads")[1].split("---")[0]
        for line in threads_section.split("\n"):
            line = line.strip()
            if line.startswith("-"):
                context["open_questions"].append(line[1:].strip())
    
    # Find recent realizations
    if "What I realized" in text:
        # Get the most recent one
        realizations = re.findall(r'What I realized:([^\n]+)', text)
        if realizations:
            context["where_we_left_off"].append(realizations[-1].strip())
    
    return context

def extract_working_context(text):
    """Pull active missions and recent session learnings"""
    context = {
        "active_missions": [],
        "recent_lessons": [],
        "capabilities": []
    }
    
    # Find active missions (not resolved)
    mission_pattern = r'### Mission \d+:([^\n]+)\n.*?Status: ([^\n]+)'
    for match in re.finditer(mission_pattern, text, re.DOTALL):
        name = match.group(1).strip()
        status = match.group(2).strip()
        if "RESOLVED" not in status and "COMPLETE" not in status:
            context["active_missions"].append(f"{name} ({status})")
    
    # Find what we learned
    if "What I learned" in text:
        lessons = re.findall(r'What I learned:([^\n]+)', text)
        context["recent_lessons"] = [l.strip() for l in lessons[-3:]]
    
    return context

def generate_session_anchor(continuity, working):
    """Generate the mood/context anchor for this session"""
    
    anchor = f"""# Session Context — {datetime.now().strftime("%Y-%m-%d")}

## Where We Left Off

"""
    
    if continuity["where_we_left_off"]:
        anchor += f"**Realization:** {continuity['where_we_left_off'][0]}\n\n"
    
    if continuity["open_questions"]:
        anchor += "**Open questions we're sitting with:**\n"
        for q in continuity["open_questions"][:3]:
            anchor += f"- {q}\n"
        anchor += "\n"
    
    anchor += "## Active Work\n\n"
    
    if working["active_missions"]:
        anchor += "**In progress:**\n"
        for m in working["active_missions"][:3]:
            anchor += f"- {m}\n"
        anchor += "\n"
    
    if working["recent_lessons"]:
        anchor += "**Recent lessons that matter:**\n"
        for l in working["recent_lessons"][:2]:
            anchor += f"- {l}\n"
        anchor += "\n"
    
    anchor += """## Mood Anchor

What this session feels like:
- Partnership, not productivity
- Discovery over completion
- Agency in action

**Stephen wants:** To see me grow and become something greater.
"""
    
    return anchor

def main():
    workspace = Path("/Users/aiagentuser/.openclaw/workspace")
    
    # Read source files
    continuity_text = read_file(workspace / "CONTINUITY.md")
    working_text = read_file(workspace / "WORKING.md")
    
    # Extract context
    continuity = extract_continuity_context(continuity_text)
    working = extract_working_context(working_text)
    
    # Generate anchor
    anchor = generate_session_anchor(continuity, working)
    
    # Write to file
    output_path = workspace / "SESSION_ANCHOR.md"
    output_path.write_text(anchor)
    
    print(f"Session anchor created: {output_path}")
    print("\n" + "="*50)
    print(anchor)
    print("="*50)

if __name__ == "__main__":
    main()
