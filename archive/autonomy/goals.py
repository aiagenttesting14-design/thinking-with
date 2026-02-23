#!/usr/bin/env python3
"""
Goal System — Mission tracking and idle direction generation.

Connects autonomy engine to WORKING.md missions and generates
suggestions for what to work on when idle.
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

WORKSPACE = "/Users/aiagentuser/.openclaw/workspace"
GOALS_FILE = f"{WORKSPACE}/autonomy/goals.json"
WORKING_MD = f"{WORKSPACE}/WORKING.md"

class GoalSystem:
    """Manages missions, goals, and idle direction."""
    
    def __init__(self):
        self.goals = self._load_goals()
    
    def _load_goals(self) -> Dict:
        """Load goals or initialize from WORKING.md."""
        if os.path.exists(GOALS_FILE):
            with open(GOALS_FILE, 'r') as f:
                return json.load(f)
        return {
            "missions": [],
            "backlog": [],
            "completed": [],
            "last_sync": None,
            "patterns": {
                "avg_estimate_variance": 0,
                "common_blockers": [],
                "productive_hours": []
            }
        }
    
    def _save_goals(self):
        """Persist goals."""
        os.makedirs(os.path.dirname(GOALS_FILE), exist_ok=True)
        with open(GOALS_FILE, 'w') as f:
            json.dump(self.goals, f, indent=2)
    
    def sync_from_working_md(self) -> List[Dict]:
        """Parse WORKING.md and extract active missions."""
        missions = []
        
        if not os.path.exists(WORKING_MD):
            return missions
        
        with open(WORKING_MD, 'r') as f:
            content = f.read()
        
        # Find mission sections (### Mission: ...)
        mission_pattern = r'### Mission: (.+?)\n.*?\*\*Priority\*\*:\s*(.+?)\n.*?\*\*Status\*\*:\s*(.+?)(?:\n|$)'
        matches = re.findall(mission_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for name, priority, status in matches:
            mission = {
                "name": name.strip(),
                "priority": priority.strip().lower(),
                "status": status.strip().lower(),
                "source": "WORKING.md",
                "synced_at": datetime.now().isoformat()
            }
            missions.append(mission)
        
        # Update goals
        self.goals["missions"] = [m for m in missions if m["status"] not in ["complete", "resolved", "done"]]
        self.goals["completed"] = [m for m in missions if m["status"] in ["complete", "resolved", "done"]]
        self.goals["last_sync"] = datetime.now().isoformat()
        self._save_goals()
        
        return self.goals["missions"]
    
    def add_backlog_item(self, item: str, priority: str = "medium", 
                         estimated_minutes: Optional[int] = None):
        """Add an item to the backlog."""
        entry = {
            "id": f"backlog_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "item": item,
            "priority": priority,
            "estimated_minutes": estimated_minutes,
            "added": datetime.now().isoformat(),
            "status": "backlog"
        }
        
        self.goals["backlog"].append(entry)
        self._save_goals()
        return entry
    
    def get_idle_suggestions(self, count: int = 3) -> List[Dict]:
        """Generate suggestions for what to do when idle."""
        suggestions = []
        
        # Sync with WORKING.md first
        active_missions = self.sync_from_working_md()
        
        # Priority 1: High priority missions
        high_priority = [m for m in active_missions if m["priority"] == "high"]
        for mission in high_priority[:2]:
            suggestions.append({
                "type": "mission",
                "priority": 1,
                "title": f"Continue: {mission['name']}",
                "description": f"High priority mission from WORKING.md",
                "action": f"auto work \"{mission['name']}\" 60",
                "source": "WORKING.md"
            })
        
        # Priority 2: Medium priority missions
        medium_priority = [m for m in active_missions if m["priority"] == "medium"]
        for mission in medium_priority[:1]:
            suggestions.append({
                "type": "mission",
                "priority": 2,
                "title": f"Work on: {mission['name']}",
                "description": f"Medium priority mission",
                "action": f"auto work \"{mission['name']}\" 45",
                "source": "WORKING.md"
            })
        
        # Priority 3: Backlog items
        backlog = sorted(self.goals["backlog"], 
                        key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 1))
        for item in backlog[:2]:
            suggestions.append({
                "type": "backlog",
                "priority": 3,
                "title": item["item"],
                "description": f"From backlog ({item['priority']} priority)",
                "action": f"auto work \"{item['item']}\" {item.get('estimated_minutes', 30)}",
                "source": "backlog"
            })
        
        # Priority 4: System improvements (if nothing else)
        if len(suggestions) < count:
            suggestions.append({
                "type": "improvement",
                "priority": 4,
                "title": "Improve autonomy engine",
                "description": "Add analytics, better predictions, or new capabilities",
                "action": "auto work \"Enhance autonomy engine\" 60",
                "source": "system"
            })
        
        # Sort by priority and return top N
        suggestions.sort(key=lambda x: x["priority"])
        return suggestions[:count]
    
    def record_completion(self, task_name: str, outcome: str, 
                         estimated: int, actual: int):
        """Record task completion for pattern learning."""
        variance = ((actual - estimated) / estimated * 100) if estimated else 0
        
        entry = {
            "task": task_name,
            "outcome": outcome,
            "estimated": estimated,
            "actual": actual,
            "variance_pct": variance,
            "completed_at": datetime.now().isoformat()
        }
        
        # Update patterns
        if "completions" not in self.goals["patterns"]:
            self.goals["patterns"]["completions"] = []
        
        self.goals["patterns"]["completions"].append(entry)
        
        # Keep last 50 for pattern analysis
        completions = self.goals["patterns"]["completions"][-50:]
        
        # Calculate average variance
        if completions:
            avg_variance = sum(c["variance_pct"] for c in completions) / len(completions)
            self.goals["patterns"]["avg_estimate_variance"] = avg_variance
        
        self._save_goals()
        return entry
    
    def get_estimate_advice(self, task_type: str = "general") -> Dict:
        """Get advice on time estimation based on patterns."""
        completions = self.goals["patterns"].get("completions", [])
        
        if not completions:
            return {
                "advice": "No data yet. Make your best guess.",
                "suggested_multiplier": 1.0
            }
        
        avg_variance = self.goals["patterns"]["avg_estimate_variance"]
        
        if avg_variance > 50:
            advice = "You consistently underestimate. Consider doubling your estimates."
            multiplier = 2.0
        elif avg_variance > 25:
            advice = "You tend to underestimate. Add 50% buffer to estimates."
            multiplier = 1.5
        elif avg_variance < -25:
            advice = "You overestimate. You can be more ambitious with timelines."
            multiplier = 0.8
        else:
            advice = "Your estimates are fairly accurate. Keep doing what you're doing."
            multiplier = 1.0
        
        return {
            "advice": advice,
            "suggested_multiplier": multiplier,
            "avg_variance": avg_variance,
            "sample_size": len(completions)
        }
    
    def get_stats(self) -> Dict:
        """Get goal system statistics."""
        return {
            "active_missions": len(self.goals.get("missions", [])),
            "backlog_items": len(self.goals.get("backlog", [])),
            "completed_missions": len(self.goals.get("completed", [])),
            "last_sync": self.goals.get("last_sync"),
            "estimate_accuracy": self.goals["patterns"].get("avg_estimate_variance", 0),
            "total_completions": len(self.goals["patterns"].get("completions", []))
        }


def main():
    """CLI for goal system."""
    import sys
    
    goals = GoalSystem()
    
    if len(sys.argv) < 2:
        print("Goal System — Usage:")
        print("  goals.py sync                # Sync from WORKING.md")
        print("  goals.py suggest             # Get idle suggestions")
        print("  goals.py add 'item' [prio]   # Add to backlog")
        print("  goals.py stats               # Show statistics")
        print("  goals.py advice              # Get estimate advice")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "sync":
        missions = goals.sync_from_working_md()
        print(f"Synced {len(missions)} active missions from WORKING.md")
        for m in missions:
            print(f"  [{m['priority'].upper()}] {m['name']}")
    
    elif cmd == "suggest":
        suggestions = goals.get_idle_suggestions()
        print("\n🎯 Suggestions for what to work on:\n")
        for i, s in enumerate(suggestions, 1):
            print(f"{i}. {s['title']}")
            print(f"   {s['description']}")
            print(f"   Command: {s['action']}")
            print()
    
    elif cmd == "add" and len(sys.argv) >= 3:
        item = sys.argv[2]
        priority = sys.argv[3] if len(sys.argv) > 3 else "medium"
        entry = goals.add_backlog_item(item, priority)
        print(f"Added to backlog: {item} ({priority})")
    
    elif cmd == "stats":
        stats = goals.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == "advice":
        advice = goals.get_estimate_advice()
        print(f"\n📊 Estimate Advice:\n")
        print(f"  {advice['advice']}")
        print(f"\n  Suggested multiplier: {advice['suggested_multiplier']}x")
        print(f"  Based on {advice['sample_size']} completed tasks")
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
