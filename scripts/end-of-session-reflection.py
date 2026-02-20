#!/usr/bin/env python3
"""
End-of-session reflection script.
Generates structured reflection and appends to daily log.
"""

import json
import os
from datetime import datetime

REFLECTION_LOG = "/Users/aiagentuser/.openclaw/workspace/memory/reflections.json"

def reflect():
    """Generate reflection template and guidance."""
    
    reflection = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "questions": {
            "what_worked": "What went well today? What am I proud of?",
            "what_didnt": "What didn't work? Where did I get stuck?",
            "surprises": "What surprised me?",
            "changes": "What would I do differently?",
            "next": "What should I focus on next?"
        },
        "prompts": [
            "Review today's progress.txt entries",
            "Check git commits for work completed",
            "Review any blockers or failures",
            "Note patterns in my behavior",
            "Identify one thing to improve tomorrow"
        ]
    }
    
    print("=== End-of-Session Reflection ===\n")
    print(f"Date: {reflection['date']}")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}\n")
    
    print("Answer these questions:\n")
    for key, question in reflection['questions'].items():
        print(f"  • {question}")
    
    print("\nGuidance:")
    for prompt in reflection['prompts']:
        print(f"  → {prompt}")
    
    print("\n" + "="*40)
    print("Save your answers to memory/YYYY-MM-DD.md")
    print("Or append to this log with: end-of-session-reflection.py save")

def save_reflection(what_worked, what_didnt, surprises, changes, next_focus):
    """Save reflection to log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "what_worked": what_worked,
        "what_didnt": what_didnt,
        "surprises": surprises,
        "changes": changes,
        "next_focus": next_focus
    }
    
    # Load existing or create new
    try:
        with open(REFLECTION_LOG, 'r') as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = {"reflections": []}
    
    log["reflections"].append(entry)
    
    with open(REFLECTION_LOG, 'w') as f:
        json.dump(log, f, indent=2)
    
    print("✅ Reflection saved")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        reflect()
    elif sys.argv[1] == "save" and len(sys.argv) >= 7:
        save_reflection(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    else:
        print("Usage:")
        print("  end-of-session-reflection.py           # Show reflection guide")
        print("  end-of-session-reflection.py save 'worked' 'didnt' 'surprises' 'changes' 'next'")
