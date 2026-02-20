#!/usr/bin/env python3
"""
Predictor — Pattern recognition and proactive suggestions.

Analyzes work patterns to:
- Predict when tasks will overrun
- Identify likely blockers
- Suggest optimal work times
- Detect productivity patterns
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

WORKSPACE = "/Users/aiagentuser/.openclaw/workspace"
PREDICTOR_FILE = f"{WORKSPACE}/autonomy/predictor.json"

class Predictor:
    """Analyzes patterns and makes predictions."""
    
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load prediction data."""
        if os.path.exists(PREDICTOR_FILE):
            with open(PREDICTOR_FILE, 'r') as f:
                return json.load(f)
        return {
            "task_patterns": {},
            "hourly_productivity": defaultdict(int),
            "blocker_keywords": defaultdict(int),
            "completion_times": [],
            "predictions_made": [],
            "accuracy_log": []
        }
    
    def _save_data(self):
        """Persist prediction data."""
        os.makedirs(os.path.dirname(PREDICTOR_FILE), exist_ok=True)
        # Convert defaultdict to dict for JSON serialization
        data = dict(self.data)
        data["hourly_productivity"] = dict(self.data["hourly_productivity"])
        data["blocker_keywords"] = dict(self.data["blocker_keywords"])
        with open(PREDICTOR_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_task_start(self, task_name: str, estimated_minutes: int):
        """Record task start for pattern analysis."""
        # Categorize task by keywords
        categories = self._categorize_task(task_name)
        
        for category in categories:
            if category not in self.data["task_patterns"]:
                self.data["task_patterns"][category] = {
                    "count": 0,
                    "avg_estimate": 0,
                    "avg_actual": 0,
                    "overrun_rate": 0
                }
            
            pattern = self.data["task_patterns"][category]
            pattern["count"] += 1
            # Update rolling average
            pattern["avg_estimate"] = (pattern["avg_estimate"] * (pattern["count"] - 1) + estimated_minutes) / pattern["count"]
        
        self._save_data()
    
    def record_task_complete(self, task_name: str, estimated: int, actual: int, 
                            outcome: str = ""):
        """Record completion for learning."""
        categories = self._categorize_task(task_name)
        overrun = actual > estimated * 1.25  # 25% threshold
        
        for category in categories:
            if category in self.data["task_patterns"]:
                pattern = self.data["task_patterns"][category]
                # Update actual average
                pattern["avg_actual"] = (pattern["avg_actual"] * (pattern["count"] - 1) + actual) / pattern["count"]
                # Update overrun rate
                current_overrun = pattern["overrun_rate"] * (pattern["count"] - 1)
                pattern["overrun_rate"] = (current_overrun + (1 if overrun else 0)) / pattern["count"]
        
        # Record time of completion for hourly patterns
        hour = datetime.now().hour
        self.data["hourly_productivity"][str(hour)] += 1
        
        # Record completion time
        self.data["completion_times"].append({
            "task": task_name,
            "estimated": estimated,
            "actual": actual,
            "variance_pct": ((actual - estimated) / estimated * 100) if estimated else 0,
            "hour": hour,
            "date": datetime.now().isoformat()
        })
        
        # Keep last 100
        self.data["completion_times"] = self.data["completion_times"][-100:]
        
        self._save_data()
    
    def record_blocker(self, task_name: str, reason: str):
        """Record blocker for pattern analysis."""
        # Extract keywords from reason
        keywords = self._extract_keywords(reason)
        for kw in keywords:
            self.data["blocker_keywords"][kw] += 1
        
        self._save_data()
    
    def predict_task_outcome(self, task_name: str, estimated_minutes: int) -> Dict:
        """Predict outcome for a new task."""
        categories = self._categorize_task(task_name)
        
        # Find most relevant pattern
        relevant_patterns = []
        for cat in categories:
            if cat in self.data["task_patterns"]:
                relevant_patterns.append(self.data["task_patterns"][cat])
        
        if not relevant_patterns:
            return {
                "confidence": "low",
                "prediction": "insufficient_data",
                "message": "No historical data for this task type.",
                "suggested_estimate": int(estimated_minutes * 1.25),  # Default buffer
                "risk_factors": []
            }
        
        # Aggregate patterns
        avg_overrun = sum(p["overrun_rate"] for p in relevant_patterns) / len(relevant_patterns)
        avg_actual = sum(p["avg_actual"] for p in relevant_patterns) / len(relevant_patterns)
        avg_estimate = sum(p["avg_estimate"] for p in relevant_patterns) / len(relevant_patterns)
        
        # Predict
        risk_factors = []
        
        if avg_overrun > 0.5:
            risk_factors.append(f"High overrun rate ({avg_overrun*100:.0f}%)")
        
        if estimated_minutes < avg_estimate * 0.5:
            risk_factors.append("Estimate seems low for this task type")
        
        # Check current hour productivity
        current_hour = datetime.now().hour
        current_productivity = self.data["hourly_productivity"].get(str(current_hour), 0)
        avg_productivity = sum(self.data["hourly_productivity"].values()) / 24 if self.data["hourly_productivity"] else 0
        
        if current_productivity < avg_productivity * 0.5:
            risk_factors.append(f"Low historical productivity at {current_hour}:00")
        
        # Suggested estimate
        if avg_overrun > 0.3:
            suggested = int(estimated_minutes * (1 + avg_overrun))
        else:
            suggested = estimated_minutes
        
        return {
            "confidence": "medium" if len(relevant_patterns) > 2 else "low",
            "prediction": "overrun" if avg_overrun > 0.3 else "on_track",
            "message": f"Similar tasks overrun {avg_overrun*100:.0f}% of the time",
            "suggested_estimate": suggested,
            "risk_factors": risk_factors,
            "based_on": f"{sum(p['count'] for p in relevant_patterns)} similar tasks"
        }
    
    def get_productivity_insights(self) -> Dict:
        """Get insights about productive hours and patterns."""
        if not self.data["hourly_productivity"]:
            return {"message": "Not enough data yet"}
        
        hours = self.data["hourly_productivity"]
        sorted_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)
        
        peak_hours = [int(h[0]) for h in sorted_hours[:3]]
        low_hours = [int(h[0]) for h in sorted_hours[-3:]]
        
        return {
            "peak_hours": sorted(peak_hours),
            "avoid_hours": sorted(low_hours),
            "total_tasks": sum(hours.values()),
            "message": f"Most productive hours: {', '.join(f'{h}:00' for h in sorted(peak_hours))}"
        }
    
    def get_common_blockers(self) -> List[Dict]:
        """Get most common blocker keywords."""
        keywords = self.data["blocker_keywords"]
        if not keywords:
            return []
        
        sorted_kw = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [{"keyword": k, "count": v} for k, v in sorted_kw[:5]]
    
    def _categorize_task(self, task_name: str) -> List[str]:
        """Extract categories from task name."""
        categories = []
        task_lower = task_name.lower()
        
        # Define category keywords
        category_map = {
            "research": ["research", "search", "find", "learn", "study"],
            "build": ["build", "create", "make", "implement", "develop"],
            "write": ["write", "draft", "document", "essay", "blog"],
            "fix": ["fix", "debug", "repair", "solve", "resolve"],
            "design": ["design", "plan", "architect", "structure"],
            "refactor": ["refactor", "improve", "enhance", "optimize", "clean"],
            "test": ["test", "verify", "check", "validate"],
            "deploy": ["deploy", "publish", "release", "push", "ship"]
        }
        
        for category, keywords in category_map.items():
            if any(kw in task_lower for kw in keywords):
                categories.append(category)
        
        if not categories:
            categories.append("general")
        
        return categories
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = text.lower().split()
        keywords = [w.strip(".,!?;:") for w in words if len(w) > 3 and w not in stop_words]
        return keywords[:5]  # Top 5 keywords
    
    def generate_insights_report(self) -> str:
        """Generate a comprehensive insights report."""
        lines = ["📊 Autonomy Insights Report", "=" * 40, ""]
        
        # Productivity insights
        prod = self.get_productivity_insights()
        lines.append("🕐 Productivity Patterns:")
        lines.append(f"   {prod.get('message', 'No data')}")
        lines.append("")
        
        # Common blockers
        blockers = self.get_common_blockers()
        if blockers:
            lines.append("🚫 Common Blockers:")
            for b in blockers:
                lines.append(f"   • {b['keyword']}: {b['count']} times")
            lines.append("")
        
        # Task patterns
        if self.data["task_patterns"]:
            lines.append("📈 Task Type Patterns:")
            for category, pattern in sorted(self.data["task_patterns"].items(), 
                                           key=lambda x: x[1]["count"], reverse=True)[:5]:
                lines.append(f"   {category}: {pattern['count']} tasks, "
                           f"{pattern['overrun_rate']*100:.0f}% overrun rate")
            lines.append("")
        
        return "\n".join(lines)


def main():
    """CLI for predictor."""
    import sys
    
    predictor = Predictor()
    
    if len(sys.argv) < 2:
        print("Predictor — Usage:")
        print("  predictor.py predict 'task' minutes  # Predict outcome")
        print("  predictor.py insights                # Show insights")
        print("  predictor.py report                  # Full report")
        print("  predictor.py blockers                # Common blockers")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "predict" and len(sys.argv) >= 4:
        task = sys.argv[2]
        minutes = int(sys.argv[3])
        result = predictor.predict_task_outcome(task, minutes)
        print(json.dumps(result, indent=2))
    
    elif cmd == "insights":
        insights = predictor.get_productivity_insights()
        print(json.dumps(insights, indent=2))
    
    elif cmd == "report":
        print(predictor.generate_insights_report())
    
    elif cmd == "blockers":
        blockers = predictor.get_common_blockers()
        for b in blockers:
            print(f"{b['keyword']}: {b['count']}")
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
