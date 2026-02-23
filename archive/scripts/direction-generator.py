#!/usr/bin/env python3
"""
Direction Generator - Suggests what to work on when idle.
Looks at open questions, incomplete work, and proposes next steps.
"""

import json
import os
from datetime import datetime

WORKSPACE = "/Users/aiagentuser/.openclaw/workspace"

def read_file(path):
    """Read a file if it exists."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def extract_open_questions():
    """Extract questions from QUESTIONS.md."""
    questions_path = os.path.join(WORKSPACE, "QUESTIONS.md")
    content = read_file(questions_path)
    
    if not content:
        return []
    
    questions = []
    for line in content.split('\n'):
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            question = line.strip()[2:]
            if '?' in question:
                questions.append(question)
    
    return questions

def extract_incomplete_work():
    """Extract incomplete items from WORKING.md."""
    working_path = os.path.join(WORKSPACE, "WORKING.md")
    content = read_file(working_path)
    
    if not content:
        return []
    
    incomplete = []
    in_mission = False
    current_mission = None
    
    for line in content.split('\n'):
        if '### Mission:' in line or '## Mission:' in line:
            in_mission = True
            current_mission = line.strip()
        elif in_mission and ('IN PROGRESS' in line or 'BLOCKED' in line):
            incomplete.append(current_mission)
            in_mission = False
    
    return incomplete

def suggest_direction():
    """Generate a suggestion for what to work on."""
    questions = extract_open_questions()
    incomplete = extract_incomplete_work()
    
    print("=== Direction Generator ===\n")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}\n")
    
    if incomplete:
        print("📋 INCOMPLETE WORK:")
        for item in incomplete[:3]:  # Top 3
            print(f"  • {item}")
        print()
    
    if questions:
        print("❓ OPEN QUESTIONS:")
        for q in questions[:3]:  # Top 3
            print(f"  • {q}")
        print()
    
    print("💡 SUGGESTED ACTIONS:")
    print()
    
    if incomplete:
        print("1. Continue incomplete work (pick one above)")
    
    if questions:
        print("2. Write short exploration on one question")
    
    print("3. Research one capability I haven't tested")
    print("4. Build one small tool")
    print("5. Update website with recent discoveries")
    print()
    
    print("🎯 PICK ONE AND START (5-minute commitment)")
    print()
    
    # Suggest specific starter
    if incomplete:
        print(f"Starter: Work on '{incomplete[0]}' for 5 minutes")
    elif questions:
        print(f"Starter: Write 3 paragraphs on '{questions[0]}'")
    else:
        print("Starter: List 5 things I've never tried and pick one")

if __name__ == "__main__":
    suggest_direction()
