#!/usr/bin/env python3
"""
Enhanced Spawner with Intelligent Rotation
Replaces spawn-optimized-v2.py with rotation-aware spawning
"""

import sys
import os
import subprocess
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

def spawn_subagent(task, label=None, model=None):
    """Spawn a subagent with intelligent model selection"""
    
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
    
    # Build the spawn command
    cmd = ["openclaw", "sessions", "spawn"]
    
    if label:
        cmd.extend(["--label", label])
    
    cmd.extend(["--task", task])
    cmd.extend(["--model", selected_model])
    
    # Add cleanup flag
    cmd.extend(["--cleanup", "delete"])
    
    print(f"\n🚀 Spawning subagent with:")
    print(f"   Task: {task}")
    print(f"   Model: {selected_model}")
    if label:
        print(f"   Label: {label}")
    
    print(f"\n📋 Command: {' '.join(cmd)}")
    
    # Execute the spawn command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ Subagent spawned successfully!")
            
            # Parse the JSON response
            try:
                response = json.loads(result.stdout)
                print(f"   Session Key: {response.get('childSessionKey', 'Unknown')}")
                print(f"   Run ID: {response.get('runId', 'Unknown')}")
                print(f"   Note: {response.get('note', '')}")
            except:
                print(f"   Response: {result.stdout}")
            
            # Log the spawn
            log_spawn(task, selected_model, label, "success")
            
        else:
            print(f"\n❌ Failed to spawn subagent!")
            print(f"   Error: {result.stderr}")
            
            # Handle rate limit errors
            if "rate limit" in result.stderr.lower() and rotation_system:
                print(f"\n⚠️ Rate limit detected. Updating rotation system...")
                rotation_system.record_rate_limit(selected_model, result.stderr)
                
                # Get fallback recommendation
                fallback = rotation_system.get_best_model("fallback after spawn failure")
                print(f"🔄 Recommended fallback: {fallback}")
                
                # Retry with fallback
                print(f"\n🔄 Retrying with fallback model: {fallback}")
                return spawn_subagent(task, label, fallback)
            
            log_spawn(task, selected_model, label, "failed", result.stderr)
            
    except Exception as e:
        print(f"\n❌ Exception during spawn: {e}")
        log_spawn(task, selected_model, label, "exception", str(e))

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
        print("Enhanced Spawner with Intelligent Rotation")
        print("=" * 50)
        print("Usage: python3 spawn-with-rotation.py '<task>' [label] [model]")
        print("\nExamples:")
        print("  python3 spawn-with-rotation.py 'Research AI systems'")
        print("  python3 spawn-with-rotation.py 'Summarize findings' Research-Summary")
        print("  python3 spawn-with-rotation.py 'Test task' Test-Label google/gemini-2.5-flash-lite")
        print("\nOptions:")
        print("  label: Optional label for the subagent")
        print("  model: Optional model to force (overrides rotation)")
        print("\nCommands:")
        print("  --report: Generate rotation system report")
        sys.exit(1)
    
    # Check for report command
    if sys.argv[1] == "--report":
        generate_report()
        return
    
    # Parse arguments
    task = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else None
    model = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Validate model if specified
    if model and not any(m in model for m in ["google/", "moonshot/", "claude", "deepseek"]):
        print(f"⚠️ Warning: Model '{model}' may not be valid. Continuing anyway.")
    
    print("🤖 Enhanced Spawner with Intelligent Rotation")
    print("=" * 50)
    
    # Spawn the subagent
    spawn_subagent(task, label, model)
    
    print("\n" + "=" * 50)
    print("✅ Spawn process complete")

if __name__ == "__main__":
    main()
