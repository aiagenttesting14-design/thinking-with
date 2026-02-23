#!/usr/bin/env python3
"""
Phase-Aware Micro-Insight System - Final Version
Direct autonomy engine integration for accurate status
"""

import json
import os
import sys
import subprocess
from datetime import datetime

def get_autonomy_status():
    """Get autonomy status directly from engine"""
    try:
        result = subprocess.run(
            ['python3', 'autonomy/engine.py', 'status'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"state": "error", "error": "Engine check failed"}
    except Exception as e:
        return {"state": "error", "error": str(e)}

def get_phase_info():
    """Get current phase information"""
    # Check for Phase 3 Harmony System specifically
    try:
        autonomy_status = get_autonomy_status()
        if autonomy_status.get('state') == 'executing':
            task = autonomy_status.get('current_task', {})
            task_name = task.get('name', '')
            
            if "Phase 3 Harmony" in task_name or "Harmony System" in task_name:
                elapsed = autonomy_status.get('elapsed_minutes', 0)
                remaining = autonomy_status.get('remaining_minutes', 0)
                progress = autonomy_status.get('progress_pct', 0)
                
                return {
                    "phase": "Phase 3 Harmony System",
                    "task": task_name,
                    "elapsed": elapsed,
                    "remaining": remaining,
                    "progress": progress,
                    "subagents": 4  # We know 4 were launched
                }
        
        # Check WORKING.md for other phases
        if os.path.exists('WORKING.md'):
            with open('WORKING.md', 'r') as f:
                content = f.read()
            
            if "Phase 3: External Value Creation Engine" in content:
                return {"phase": "Phase 3: External Value Creation", "week": "Week 1: Market Research"}
            elif "Phase 2: Self-Improvement Feedback Loop" in content:
                return {"phase": "Phase 2: Self-Improvement", "status": "Active"}
            elif "Phase 1: Token Optimization System" in content:
                return {"phase": "Phase 1: Token Optimization", "status": "Complete"}
        
        return {"phase": "Exploring capabilities", "status": "Active"}
    except:
        return {"phase": "Status unknown", "error": "Read failed"}

def generate_insight():
    """Generate clear, phase-aware insight"""
    autonomy = get_autonomy_status()
    phase_info = get_phase_info()
    
    current_time = datetime.now().strftime("%I:%M %p")
    
    # Handle Phase 3 Harmony System specifically
    if phase_info.get('phase') == "Phase 3 Harmony System":
        elapsed = phase_info.get('elapsed', 0)
        progress = phase_info.get('progress', 0)
        subagents = phase_info.get('subagents', 0)
        
        insight = f"🔄 Phase 3 Harmony System\n"
        insight += f"Progress: {progress:.0f}% complete ({elapsed:.0f} minutes elapsed)\n"
        insight += f"Subagents: {subagents} researching autonomously\n"
        insight += f"Research areas: Market analysis, Autonomy frameworks, Self-improvement, Identity manifesto\n"
        insight += f"Next report: 8:00 AM tomorrow\n"
        insight += f"Current time: {current_time}"
    
    # Handle executing state
    elif autonomy.get('state') == 'executing':
        task = autonomy.get('current_task', {})
        task_name = task.get('name', 'Current task')
        elapsed = autonomy.get('elapsed_minutes', 0)
        progress = autonomy.get('progress_pct', 0)
        
        insight = f"⚡ {phase_info.get('phase', 'Active work')}\n"
        insight += f"Task: {task_name}\n"
        insight += f"Progress: {progress:.0f}% ({elapsed:.0f} min elapsed)\n"
        insight += f"Mode: Autonomous execution\n"
        insight += f"Check-in: {current_time}"
    
    # Handle idle state
    elif autonomy.get('state') == 'idle':
        insight = f"⏸️  {phase_info.get('phase', 'System idle')}\n"
        insight += f"Status: Ready for work\n"
        insight += f"Suggest: Run 'auto suggest' for next task\n"
        insight += f"Time: {current_time}"
    
    # Handle error state
    elif autonomy.get('state') == 'error':
        insight = f"⚠️  System Status\n"
        insight += f"Phase: {phase_info.get('phase', 'Unknown')}\n"
        insight += f"Status: Autonomy engine check failed\n"
        insight += f"Time: {current_time}"
    
    # Default status
    else:
        insight = f"📊 {phase_info.get('phase', 'System Status')}\n"
        insight += f"Autonomy: {autonomy.get('state', 'active')}\n"
        if 'week' in phase_info:
            insight += f"Focus: {phase_info['week']}\n"
        insight += f"Last check: {current_time}"
    
    return insight

if __name__ == "__main__":
    insight = generate_insight()
    print(insight)
    
    # Log this insight
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "insight": insight,
        "autonomy_state": get_autonomy_status().get('state', 'unknown'),
        "phase": get_phase_info().get('phase', 'unknown')
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

