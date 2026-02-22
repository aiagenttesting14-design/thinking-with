#!/usr/bin/env python3
"""
Enhanced Spawner with Intelligent Rotation - Version 2
Simulated version for testing rotation logic
"""

import sys
import os
import json
from datetime import datetime

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_rotation_system():
    """Load the intelligent rotation system"""
    try:
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "intelligent_rotation", 
            os.path.join(os.path.dirname(__file__), "intelligent-rotation-v1.py")
        )
        intelligent_rotation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(intelligent_rotation)
        
        return intelligent_rotation.IntelligentRotationSystem()
    except Exception as e:
        print(f"⚠️ Failed to load rotation system: {e}")
        return None

def spawn_via_api(task, label=None, model=None):
    """Spawn a subagent via OpenClaw API (simplified version)"""
    
    rotation_system = load_rotation_system()
    
    # If model is specified, use it (override)
    if model:
        print(f"🔧 Using specified model: {model}")
        selected_model = model
    elif rotation_system:
        # Use intelligent rotation to select model
        selected_model = rotation_system.get_best_model(task)
        print(f"🤖 Rotation system selected: {selected_model}")
        
        # Record usage
        rotation_system.record_usage(selected_model, task)
        
        # Show quota info
        quota = rotation_system.get_remaining_quota(selected_model)
        print(f"📊 Quota: {quota['used']}/{quota['limit']} ({quota['percentage_used']:.1f}%)")
    else:
        # Fallback to basic selection
        print("⚠️ Using basic model selection (rotation system unavailable)")
        if "summar" in task.lower() or "brief" in task.lower():
            selected_model = "google/gemini-2.5-flash-lite"
        else:
            selected_model = "moonshot/kimi-k2.5"
    
    print(f"\n🚀 SIMULATED SPAWN:")
    print(f"   Task: {task}")
    print(f"   Model: {selected_model}")
    if label:
        print(f"   Label: {label}")
    
    # Simulate API response
    simulated_response = {
        "status": "accepted",
        "childSessionKey": f"agent:main:subagent:simulated-{datetime.now().timestamp()}",
        "runId": f"simulated-run-{datetime.now().timestamp()}",
        "note": "Simulated spawn for rotation testing"
    }
    
    print(f"\n✅ Simulated spawn successful!")
    print(f"   Session Key: {simulated_response['childSessionKey']}")
    print(f"   Run ID: {simulated_response['runId']}")
    
    # Log the spawn
    log_spawn(task, selected_model, label, "simulated_success")
    
    return simulated_response

def simulate_rate_limit_error(task, model, label=None):
    """Simulate a rate limit error for testing"""
    print(f"\n🧪 SIMULATING RATE LIMIT ERROR for {model}")
    
    rotation_system = load_rotation_system()
    
    if rotation_system:
        # Record the rate limit
        rotation_system.record_rate_limit(model, "Simulated API rate limit reached")
        
        # Get fallback recommendation
        fallback = rotation_system.get_best_model("fallback after simulated rate limit")
        print(f"🔄 Rotation system recommends: {fallback}")
        
        # Show updated quota
        quota = rotation_system.get_remaining_quota(fallback)
        print(f"📊 Fallback quota: {quota['used']}/{quota['limit']}")
        
        # Retry with fallback
        print(f"\n🔄 Retrying with fallback model: {fallback}")
        return spawn_via_api(task, label, fallback)
    else:
        print(f"⚠️ No rotation system available. Basic fallback to Kimi.")
        return spawn_via_api(task, label, "moonshot/kimi-k2.5")

def log_spawn(task, model, label, status, error=None):
    """Log spawn attempt to cost tracker"""
    cost_file = "/Users/aiagentuser/.openclaw/workspace/cost-tracker.json"
    
    try:
        if os.path.exists(cost_file):
            with open(cost_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"spawns": []}
        
        spawn_record = {
            "task": task,
            "model": model,
            "label": label,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            spawn_record["error"] = error[:500]  # Truncate long errors
        
        data.setdefault("spawns", []).append(spawn_record)
        
        with open(cost_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📝 Logged spawn attempt to cost tracker")
        
    except Exception as e:
        print(f"⚠️ Failed to log spawn: {e}")

def test_rotation_scenarios():
    """Test various rotation scenarios"""
    print("🧪 TESTING ROTATION SCENARIOS")
    print("=" * 50)
    
    test_cases = [
        ("Summarize research paper", "Summary-Test", None),
        ("Research AI memory systems", "Research-Test", None),
        ("Complex reasoning analysis", "Reasoning-Test", None),
        ("Heartbeat check", "Heartbeat-Test", None),
    ]
    
    for task, label, model in test_cases:
        print(f"\n{'='*30}")
        print(f"Test: {task}")
        print(f"{'='*30}")
        
        spawn_via_api(task, label, model)
    
    # Test rate limit scenario
    print(f"\n{'='*30}")
    print(f"Test: Rate Limit Simulation")
    print(f"{'='*30}")
    simulate_rate_limit_error("Test after rate limit", "google/gemini-2.5-flash-lite", "RateLimit-Test")

def generate_report():
    """Generate rotation and spawn report"""
    rotation_system = load_rotation_system()
    
    if rotation_system:
        print("\n" + "=" * 60)
        print("INTELLIGENT ROTATION SYSTEM REPORT")
        print("=" * 60)
        print(rotation_system.generate_rotation_report())
    else:
        print("\n⚠️ Rotation system not available for report")

def main():
    if len(sys.argv) < 2:
        print("Enhanced Spawner with Intelligent Rotation - V2")
        print("=" * 50)
        print("Usage: python3 spawn-with-rotation-v2.py '<task>' [label] [model]")
        print("\nExamples:")
        print("  python3 spawn-with-rotation-v2.py 'Research AI systems'")
        print("  python3 spawn-with-rotation-v2.py 'Summarize findings' Research-Summary")
        print("  python3 spawn-with-rotation-v2.py 'Test task' Test-Label google/gemini-2.5-flash-lite")
        print("\nCommands:")
        print("  --test: Run rotation test scenarios")
        print("  --report: Generate rotation system report")
        sys.exit(1)
    
    # Check for commands
    if sys.argv[1] == "--test":
        test_rotation_scenarios()
        return
    elif sys.argv[1] == "--report":
        generate_report()
        return
    
    # Parse arguments
    task = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else None
    model = sys.argv[3] if len(sys.argv) > 3 else None
    
    print("🤖 Enhanced Spawner with Intelligent Rotation - V2")
    print("=" * 50)
    
    # Spawn the subagent
    spawn_via_api(task, label, model)
    
    print("\n" + "=" * 50)
    print("✅ Spawn process complete")

if __name__ == "__main__":
    main()
