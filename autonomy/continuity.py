#!/usr/bin/env python3
"""
Continuity System — The connective tissue between all systems.

Makes the whole ecosystem work together:
- WORKING.md missions → Autonomy goals
- Autonomy state → Website live display
- Session end → Auto-consolidation
- Task completion → Auto-documentation
"""

import json
import os
import re
import subprocess
from datetime import datetime

WORKSPACE = "/Users/aiagentuser/.openclaw/workspace"

class ContinuitySystem:
    """Connects all systems into a breathing whole."""
    
    def __init__(self):
        self.state_file = f"{WORKSPACE}/autonomy/continuity-state.json"
        self.load_state()
    
    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "last_session_end": None,
                "last_consolidation": None,
                "connected_systems": [],
                "auto_updates": 0
            }
    
    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def on_session_start(self):
        """Run when a new session begins."""
        print("🌅 Session start continuity check...")
        
        # Generate briefing
        result = subprocess.run(
            ['python3', f'{WORKSPACE}/autonomy/session-prep.py', 'generate'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("   ✅ Session briefing generated")
        
        # Sync goals from WORKING.md
        result = subprocess.run(
            ['python3', f'{WORKSPACE}/autonomy/goals.py', 'sync'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("   ✅ Goals synced from WORKING.md")
        
        # Generate fresh website state
        result = subprocess.run(
            ['python3', f'{WORKSPACE}/autonomy/generate_state.py', 'js'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("   ✅ Website state refreshed")
        
        return True
    
    def on_task_complete(self, task_name, outcome):
        """Run when a task completes."""
        print("🔄 Continuity update...")
        
        updates = []
        
        # 1. Update website state
        result = subprocess.run(
            ['python3', f'{WORKSPACE}/autonomy/generate_state.py', 'js'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            updates.append("Website state")
        
        # 2. Check if WORKING.md needs update
        if self._should_update_working_md(task_name):
            self._prompt_working_update(task_name, outcome)
            updates.append("WORKING.md prompt")
        
        # 3. Commit website changes if significant
        if outcome and len(outcome) > 10:
            self._commit_website_changes(task_name, outcome)
            updates.append("Website commit")
        
        self.state["auto_updates"] += 1
        self.save_state()
        
        print(f"   ✅ Continuity maintained: {', '.join(updates)}")
        return updates
    
    def on_session_end(self):
        """Run when session ends."""
        print("🌙 Session end consolidation...")
        
        # 1. Final state generation
        subprocess.run(
            ['python3', f'{WORKSPACE}/autonomy/generate_state.py', 'js'],
            capture_output=True
        )
        
        # 2. Commit final state
        self._commit_website_changes("session-end", "Final state update")
        
        # 3. Record timestamp
        self.state["last_session_end"] = datetime.now().isoformat()
        self.save_state()
        
        print("   ✅ Session continuity preserved")
        return True
    
    def _should_update_working_md(self, task_name):
        """Check if this task relates to a WORKING.md mission."""
        working_path = f"{WORKSPACE}/WORKING.md"
        if not os.path.exists(working_path):
            return False
        
        with open(working_path, 'r') as f:
            content = f.read().lower()
        
        # Check if task keywords appear in missions
        task_keywords = set(task_name.lower().split())
        mission_section = content.split('## active missions')[1] if '## active missions' in content else content
        
        return any(keyword in mission_section for keyword in task_keywords if len(keyword) > 3)
    
    def _prompt_working_update(self, task_name, outcome):
        """Create prompt for WORKING.md update."""
        prompt_path = f"{WORKSPACE}/.working-update-prompt"
        with open(prompt_path, 'w') as f:
            f.write(f"""# WORKING.md Update Suggested

Task completed: {task_name}
Outcome: {outcome}
Time: {datetime.now().isoformat()}

Consider updating WORKING.md:
- Mark mission as complete if applicable
- Add session log entry
- Update mission status
""")
    
    def _commit_website_changes(self, task_name, outcome):
        """Auto-commit website changes."""
        try:
            # Add live-state.js
            subprocess.run(
                ['git', '-C', f'{WORKSPACE}/website', 'add', 'live-state.js'],
                capture_output=True, check=False
            )
            
            # Commit with meaningful message
            msg = f"Auto: {task_name[:40]}..." if len(task_name) > 40 else f"Auto: {task_name}"
            subprocess.run(
                ['git', '-C', f'{WORKSPACE}/website', 'commit', '-m', msg],
                capture_output=True, check=False
            )
            
            # Push
            subprocess.run(
                ['git', '-C', f'{WORKSPACE}/website', 'push'],
                capture_output=True, check=False
            )
        except:
            pass  # Silent fail - continuity shouldn't block
    
    def check_health(self):
        """Check if all systems are connected."""
        checks = {
            "autonomy_state": os.path.exists(f"{WORKSPACE}/autonomy/state.json"),
            "website_state": os.path.exists(f"{WORKSPACE}/website/live-state.js"),
            "goals_synced": os.path.exists(f"{WORKSPACE}/autonomy/goals.json"),
            "session_prep": os.path.exists(f"{WORKSPACE}/autonomy/session-prep.py"),
            "working_md": os.path.exists(f"{WORKSPACE}/WORKING.md")
        }
        
        return checks
    
    def get_status(self):
        """Get continuity system status."""
        health = self.check_health()
        return {
            "systems_connected": sum(health.values()),
            "total_systems": len(health),
            "auto_updates_today": self.state["auto_updates"],
            "last_session_end": self.state["last_session_end"],
            "all_systems_healthy": all(health.values())
        }


def main():
    """CLI for continuity system."""
    import sys
    
    continuity = ContinuitySystem()
    
    if len(sys.argv) < 2:
        print("Continuity System — Usage:")
        print("  continuity.py start    # Session start routine")
        print("  continuity.py end      # Session end routine")
        print("  continuity.py status   # Check system health")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "start":
        continuity.on_session_start()
    elif cmd == "end":
        continuity.on_session_end()
    elif cmd == "status":
        status = continuity.get_status()
        print(json.dumps(status, indent=2))
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
