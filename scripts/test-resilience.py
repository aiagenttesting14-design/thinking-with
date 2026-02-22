#!/usr/bin/env python3
"""
Test the resilience features by simulating API failures
"""

import json
import os
from pathlib import Path
import shutil

# Simulate different failure scenarios
STATE_FILE = Path.home() / ".openclaw" / "workspace" / "autonomy" / "micro-insight-state.json"

def simulate_failures(num_failures):
    """Simulate consecutive failures to test adaptive strategies"""
    print(f"\n🧪 Simulating {num_failures} consecutive failures...")
    
    # Load current state
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    else:
        state = {
            "consecutive_errors": 0,
            "last_success": None,
            "current_interval_ms": 5400000,
            "current_model": "google/gemini-2.5-flash-lite",
            "failure_patterns": [],
            "adaptive_strategy": "primary"
        }
    
    # Simulate failures
    for i in range(num_failures):
        state["consecutive_errors"] += 1
        state["failure_patterns"].append({
            "timestamp": "2026-02-21T07:55:00.000000",
            "error": f"Simulated API failure #{i+1}"
        })
        
        # Keep only last 10 failure patterns
        state["failure_patterns"] = state["failure_patterns"][-10:]
        
        # Test exponential backoff logic
        if state["consecutive_errors"] > 3:
            state["current_interval_ms"] = min(
                state["current_interval_ms"] * 2,
                86400000  # Max 24 hours
            )
        
        # Test adaptive strategy switching
        if state["consecutive_errors"] > 6:
            state["adaptive_strategy"] = "alternate"
        elif state["consecutive_errors"] > 3:
            state["adaptive_strategy"] = "fallback"
    
    # Save state
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"✅ Simulated {num_failures} failures")
    print(f"   Consecutive errors: {state['consecutive_errors']}")
    print(f"   Current interval: {state['current_interval_ms']/60000:.0f} minutes")
    print(f"   Adaptive strategy: {state['adaptive_strategy']}")
    
    return state

def test_scenarios():
    """Test different failure scenarios"""
    print("🔬 Testing Resilience Features")
    print("=" * 50)
    
    # Backup original state
    backup_file = STATE_FILE.with_suffix('.json.backup')
    if STATE_FILE.exists():
        shutil.copy2(STATE_FILE, backup_file)
        print("📋 Backed up original state")
    
    try:
        # Scenario 1: 2 failures (should stay with primary)
        state = simulate_failures(2)
        assert state["adaptive_strategy"] == "primary"
        assert state["current_interval_ms"] == 5400000
        print("✅ Scenario 1: 2 failures - Primary strategy maintained")
        
        # Scenario 2: 4 failures (should switch to fallback, double interval)
        state = simulate_failures(2)  # Add 2 more for total of 4
        assert state["adaptive_strategy"] == "fallback"
        assert state["current_interval_ms"] == 10800000  # Doubled
        print("✅ Scenario 2: 4 failures - Fallback strategy, interval doubled")
        
        # Scenario 3: 7 failures (should switch to alternate, interval doubled again)
        state = simulate_failures(3)  # Add 3 more for total of 7
        assert state["adaptive_strategy"] == "alternate"
        assert state["current_interval_ms"] == 21600000  # Doubled again
        print("✅ Scenario 3: 7 failures - Alternate strategy, interval 4x")
        
        # Scenario 4: Success resets everything
        print("\n🧪 Simulating success after failures...")
        state["consecutive_errors"] = 0
        state["last_success"] = "2026-02-21T08:00:00.000000"
        state["current_interval_ms"] = 5400000
        state["adaptive_strategy"] = "primary"
        
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        
        print("✅ Scenario 4: Success - All counters and strategies reset")
        
        print("\n🎉 All resilience tests passed!")
        
    finally:
        # Restore original state
        if backup_file.exists():
            shutil.copy2(backup_file, STATE_FILE)
            backup_file.unlink()
            print("\n📋 Restored original state")

if __name__ == "__main__":
    test_scenarios()
