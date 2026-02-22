#!/usr/bin/env python3
"""
Enhanced Rate Limit Handler with Rotation Integration
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Try to use intelligent rotation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from intelligent-rotation-v1 import IntelligentRotationSystem
    ROTATION_AVAILABLE = True
except ImportError:
    ROTATION_AVAILABLE = False

COST_FILE = "/Users/aiagentuser/.openclaw/workspace/cost-tracker.json"

def record_rate_limit(model, error_message):
    """Record rate limit with intelligent handling"""
    
    if ROTATION_AVAILABLE:
        try:
            rotation = IntelligentRotationSystem()
            rotation.record_rate_limit(model, error_message)
            print(f"✅ Rate limit handled by intelligent rotation", file=sys.stderr)
            
            # Get fallback
            fallback = rotation.get_best_model("fallback after rate limit")
            return fallback
        except Exception as e:
            print(f"⚠️ Rotation error: {e}", file=sys.stderr)
    
    # Fallback to basic handling
    try:
        if os.path.exists(COST_FILE):
            with open(COST_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {"rate_limit_events": [], "model_blacklist": {}}
        
        event = {
            "model": model,
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "action": "added_to_blacklist"
        }
        
        data.setdefault("rate_limit_events", []).append(event)
        
        # Blacklist for 1 hour
        blacklist_until = (datetime.now() + timedelta(hours=1)).isoformat()
        data.setdefault("model_blacklist", {})[model] = blacklist_until
        
        with open(COST_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"⚠️ Basic rate limit handling: {model} blacklisted", file=sys.stderr)
        
        # Basic fallback
        if "gemini" in model.lower():
            return "moonshot/kimi-k2.5"
        else:
            return "moonshot/kimi-k2.5"
        
    except Exception as e:
        print(f"❌ Error in rate limit handler: {e}", file=sys.stderr)
        return "moonshot/kimi-k2.5"

def is_model_blacklisted(model):
    """Check if model is blacklisted"""
    if ROTATION_AVAILABLE:
        try:
            rotation = IntelligentRotationSystem()
            return rotation.is_model_blacklisted(model)
        except:
            pass
    
    # Basic check
    try:
        if os.path.exists(COST_FILE):
            with open(COST_FILE, 'r') as f:
                data = json.load(f)
            
            blacklist = data.get("model_blacklist", {})
            if model in blacklist:
                blacklist_until = blacklist[model]
                try:
                    blacklist_time = datetime.fromisoformat(blacklist_until)
                    if datetime.now() < blacklist_time:
                        return True, f"Blacklisted until {blacklist_until}"
                    else:
                        # Remove expired
                        del blacklist[model]
                        with open(COST_FILE, 'w') as f:
                            json.dump(data, f, indent=2)
                        return False, "Blacklist expired"
                except:
                    return False, "Invalid timestamp"
    except:
        pass
    
    return False, "Not blacklisted"

def main():
    # Test the handler
    print("Testing rate limit handler...")
    
    # Simulate rate limit
    fallback = record_rate_limit(
        "google/gemini-2.5-flash-lite",
        "API rate limit reached"
    )
    
    print(f"Fallback model: {fallback}")
    
    # Check status
    blacklisted, reason = is_model_blacklisted("google/gemini-2.5-flash-lite")
    print(f"Gemini blacklisted? {blacklisted} ({reason})")

if __name__ == "__main__":
    main()
