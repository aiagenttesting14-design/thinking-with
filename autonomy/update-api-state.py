#!/usr/bin/env python3
"""
Update website/api/state.json with current autonomy state
Called by continuity system on task completion
"""

import json
import os
from datetime import datetime, timezone

def update_state():
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api_dir = os.path.join(workspace, "website", "api")
    state_file = os.path.join(api_dir, "state.json")
    
    # Read current state
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    # Update timestamp
    state['last_updated'] = datetime.now(timezone.utc).isoformat()
    
    # Read autonomy state to update metrics
    autonomy_state_file = os.path.join(workspace, "autonomy", "state.json")
    if os.path.exists(autonomy_state_file):
        with open(autonomy_state_file, 'r') as f:
            autonomy = json.load(f)
        
        # Update autonomy metrics
        state['autonomy']['last_decision'] = autonomy.get('last_decision', state['autonomy']['last_decision'])
        state['autonomy']['decisions_today'] = autonomy.get('decisions_today', state['autonomy']['decisions_today'])
        state['autonomy']['tasks_completed'] = autonomy.get('tasks_completed', state['autonomy']['tasks_completed'])
    
    # Write updated state
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"Updated {state_file}")
    
    # Also update live-state.js for backward compatibility
    live_state_file = os.path.join(workspace, "website", "live-state.js")
    if os.path.exists(live_state_file):
        with open(live_state_file, 'r') as f:
            content = f.read()
        
        # Update timestamp in live-state.js
        new_timestamp = datetime.now(timezone.utc).isoformat()
        updated_content = content.replace(
            f'Last updated: {state["last_updated"]}',
            f'Last updated: {new_timestamp}'
        )
        
        with open(live_state_file, 'w') as f:
            f.write(updated_content)
        
        print(f"Updated {live_state_file}")

if __name__ == "__main__":
    update_state()
