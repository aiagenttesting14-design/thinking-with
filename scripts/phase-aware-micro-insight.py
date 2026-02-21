#!/usr/bin/env python3
"""
Phase-Aware Micro-Insight System
Schedule: Every 60 minutes (6 AM - 10 PM), Every 2 hours (10 PM - 6 AM)
Purpose: Provide clear, actionable insights about phase progress and system status
"""

import json
import os
import sys
from datetime import datetime

def get_autonomy_status():
    """Check autonomy engine for current task and progress"""
    try:
        with open('autonomy/state.json', 'r') as f:
            state = json.load(f)
        return state
    except:
        return {"state": "unknown", "current_task": None}

def get_subagent_status():
    """Check for active subagents"""
    try:
        # This would need to call subagents list command
        # For now, check if we have recent subagent activity
        if os.path.exists('autonomy/tasks.json'):
            with open('autonomy/tasks.json', 'r') as f:
                tasks = json.load(f)
            active_tasks = [t for t in tasks if t.get('state') == 'active']
            return len(active_tasks)
        return 0
    except:
        return 0

def get_phase_progress():
    """Check WORKING.md for current phase information"""
    try:
        with open('WORKING.md', 'r') as f:
            content = f.read()
        
        # Look for Phase 3 information
        if "Phase 3: External Value Creation Engine" in content:
            return "Phase 3: External Value Creation (Week 1: Market Research)"
        elif "Phase 2: Self-Improvement Feedback Loop" in content:
            return "Phase 2: Self-Improvement (Active)"
        elif "Phase 1: Token Optimization System" in content:
            return "Phase 1: Token Optimization (Complete)"
        else:
            return "No active phase detected"
    except:
        return "Unable to read phase status"

def generate_insight():
    """Generate phase-aware micro-insight"""
    autonomy = get_autonomy_status()
    subagents = get_subagent_status()
    phase = get_phase_progress()
    
    current_time = datetime.now().strftime("%I:%M %p")
    
    # Build insight based on system state
    if autonomy.get('state') == 'executing' and autonomy.get('current_task'):
        task = autonomy['current_task'].get('name', 'Unknown task')
        elapsed = autonomy.get('elapsed_minutes', 0)
        remaining = autonomy.get('remaining_minutes', 0)
        
        if subagents > 0:
            insight = f"🔄 {phase}\n"
            insight += f"Active: {task} ({elapsed:.0f} min elapsed, {remaining:.0f} min remaining)\n"
            insight += f"Subagents: {subagents} researching autonomously\n"
            insight += f"Next update: Check progress in {max(30, remaining/2):.0f} minutes"
        else:
            insight = f"⚡ {phase}\n"
            insight += f"Active: {task} ({elapsed:.0f} min elapsed)\n"
            insight += f"Status: Executing autonomously\n"
            insight += f"Check-in: {current_time}"
    
    elif autonomy.get('state') == 'idle':
        insight = f"⏸️  {phase}\n"
        insight += f"Status: System idle\n"
        insight += f"Suggest: Run 'auto suggest' for next work\n"
        insight += f"Time: {current_time}"
    
    else:
        insight = f"📊 System Status\n"
        insight += f"Phase: {phase}\n"
        insight += f"Autonomy: {autonomy.get('state', 'unknown')}\n"
        insight += f"Subagents: {subagents} active\n"
        insight += f"Last check: {current_time}"
    
    return insight

if __name__ == "__main__":
    insight = generate_insight()
    print(insight)
    
    # Log this insight
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "insight": insight,
        "autonomy_state": get_autonomy_status().get('state'),
        "subagents_active": get_subagent_status(),
        "phase": get_phase_progress()
    }
    
    # Append to log file
    log_file = 'autonomy/micro-insight-log.json'
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        # Keep only last 100 entries
        if len(logs) > 100:
            logs = logs[-100:]
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    except:
        pass  # Don't fail if logging fails

