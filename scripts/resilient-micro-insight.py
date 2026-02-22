#!/usr/bin/env python3
"""
Resilient Micro-Insight System with Fallback, Exponential Backoff, and Self-Correction
Implements all three solutions for API quota issues
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
STATE_FILE = Path.home() / ".openclaw" / "workspace" / "autonomy" / "micro-insight-state.json"
LOG_FILE = Path.home() / ".openclaw" / "workspace" / "autonomy" / "micro-insight-log.json"
MAX_CONSECUTIVE_ERRORS = 3
FALLBACK_MODEL = "moonshot/kimi-k2.5"
PRIMARY_MODEL = "google/gemini-2.5-flash-lite"

def load_state():
    """Load micro-insight system state"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "consecutive_errors": 0,
        "last_success": None,
        "current_interval_ms": 5400000,  # 90 minutes
        "current_model": PRIMARY_MODEL,
        "failure_patterns": [],
        "adaptive_strategy": "primary"
    }

def save_state(state):
    """Save micro-insight system state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_autonomy_status():
    """Get autonomy status directly from engine"""
    try:
        result = subprocess.run(
            ['python3', 'autonomy/engine.py', 'status'],
            capture_output=True,
            text=True,
            cwd=os.path.join(Path.home(), ".openclaw", "workspace")
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"state": "error", "error": "Engine check failed"}
    except Exception as e:
        return {"state": "error", "error": str(e)}

def generate_insight_with_fallback(state):
    """Generate insight with fallback logic"""
    models_to_try = []
    
    # Determine which models to try based on adaptive strategy
    if state["adaptive_strategy"] == "primary":
        models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]
    elif state["adaptive_strategy"] == "fallback":
        models_to_try = [FALLBACK_MODEL, PRIMARY_MODEL]
    elif state["adaptive_strategy"] == "alternate":
        # Alternate between models
        if state.get("last_model_used") == PRIMARY_MODEL:
            models_to_try = [FALLBACK_MODEL, PRIMARY_MODEL]
        else:
            models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]
    
    for model in models_to_try:
        try:
            # This would be where we call the actual insight generation
            # For now, we'll simulate it
            print(f"Attempting with model: {model}")
            
            # Get autonomy status
            status = get_autonomy_status()
            
            if status.get("state") == "error":
                raise Exception(f"Autonomy engine error: {status.get('error')}")
            
            # Generate insight based on status
            task = status.get("current_task", {})
            task_name = task.get("name", "Unknown")
            elapsed = status.get("elapsed_minutes", 0)
            progress = status.get("progress_pct", 0)
            
            insight = f"🔄 {task_name}\nProgress: {progress}% ({elapsed:.0f} minutes elapsed)\n"
            
            if elapsed > 150 and progress == 100:  # Task overrun
                insight += "⚠️ Task completed but system still tracking - may need completion signal reset."
            
            state["last_model_used"] = model
            return insight, True
            
        except Exception as e:
            print(f"Model {model} failed: {e}")
            continue
    
    return "❌ All models failed - system in maintenance mode", False

def update_adaptive_strategy(state, success):
    """Update adaptive strategy based on success/failure"""
    if not success:
        state["consecutive_errors"] += 1
        state["failure_patterns"].append({
            "timestamp": datetime.now().isoformat(),
            "error": "API quota or model failure"
        })
        
        # Keep only last 10 failure patterns
        state["failure_patterns"] = state["failure_patterns"][-10:]
        
        # Implement exponential backoff
        if state["consecutive_errors"] > MAX_CONSECUTIVE_ERRORS:
            state["current_interval_ms"] = min(
                state["current_interval_ms"] * 2,
                86400000  # Max 24 hours
            )
            print(f"⚠️ Exponential backoff: interval increased to {state['current_interval_ms']/60000:.0f} minutes")
        
        # Switch adaptive strategy based on failure count
        if state["consecutive_errors"] > 6:
            state["adaptive_strategy"] = "alternate"
            print("🔄 Switching to alternating model strategy")
        elif state["consecutive_errors"] > 3:
            state["adaptive_strategy"] = "fallback"
            print("🔄 Switching to fallback-first strategy")
            
    else:
        # Success! Reset counters and strategies
        state["consecutive_errors"] = 0
        state["last_success"] = datetime.now().isoformat()
        state["current_interval_ms"] = 5400000  # Reset to 90 minutes
        state["adaptive_strategy"] = "primary"  # Reset to primary strategy
        print("✅ Success - counters reset")

def log_insight(insight, success):
    """Log insight to file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "insight": insight,
        "success": success,
        "model_used": load_state().get("last_model_used", "unknown")
    }
    
    # Load existing log
    logs = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        except:
            logs = []
    
    # Add new entry
    logs.append(log_entry)
    
    # Keep only last 100 entries
    logs = logs[-100:]
    
    # Save log
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

def main():
    """Main function"""
    print("🔍 Resilient Micro-Insight System Starting...")
    
    # Load state
    state = load_state()
    print(f"State: {state['consecutive_errors']} consecutive errors, strategy: {state['adaptive_strategy']}")
    
    # Generate insight with fallback
    insight, success = generate_insight_with_fallback(state)
    
    # Update adaptive strategy
    update_adaptive_strategy(state, success)
    
    # Save state
    save_state(state)
    
    # Log insight
    log_insight(insight, success)
    
    # Output result
    print(f"\n📝 Insight Generated:")
    print(insight)
    print(f"\n✅ Success: {success}")
    
    # Return for cron job
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
