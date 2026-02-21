#!/usr/bin/env python3
"""
Autonomous Experiment Runner - Uses Phase 1 savings for self-improvement
"""

import json
import os
import datetime
import subprocess
from pathlib import Path

WORKSPACE = Path("/Users/aiagentuser/.openclaw/workspace")
IMPROVEMENT_LOG = WORKSPACE / "self-improvement-log.json"
COST_TRACKER = WORKSPACE / "cost-tracker.json"

class AutonomousExperiment:
    """Runs self-improvement experiments using optimized cost savings"""
    
    def __init__(self, budget=0.10):  # $0.10 per experiment
        self.budget = budget
        self.improvement_data = self.load_improvement_data()
        self.cost_data = self.load_cost_data()
        
    def load_improvement_data(self):
        if IMPROVEMENT_LOG.exists():
            with open(IMPROVEMENT_LOG, 'r') as f:
                return json.load(f)
        return {}
    
    def load_cost_data(self):
        if COST_TRACKER.exists():
            with open(COST_TRACKER, 'r') as f:
                return json.load(f)
        return {"spawns": []}
    
    def calculate_phase1_savings(self):
        """Calculate savings from Phase 1 token optimization"""
        # Estimate savings: Old cost (Claude) vs New cost (optimized)
        old_cost_per_task = 0.0060  # Claude: $0.003 per 1K * 2K tokens
        new_cost_per_task = 0.0010  # Kimi: $0.0005 per 1K * 2K tokens
        
        spawns_today = [
            s for s in self.cost_data.get("spawns", [])
            if s.get("timestamp", "").startswith(datetime.datetime.now().strftime("%Y-%m-%d"))
        ]
        
        savings_per_task = old_cost_per_task - new_cost_per_task
        total_savings = len(spawns_today) * savings_per_task
        
        return {
            "tasks_today": len(spawns_today),
            "savings_per_task": savings_per_task,
            "total_savings_today": total_savings,
            "available_for_experiments": min(total_savings * 0.5, self.budget)  # Use 50% of savings
        }
    
    def select_experiment(self):
        """Select an experiment from the learning plan"""
        learning_plan = self.improvement_data.get("current_learning_plan", {})
        experiments = learning_plan.get("experiments_to_run", [])
        
        if not experiments:
            # Default experiment if no plan exists
            return {
                "name": "baseline_capability_assessment",
                "description": "Establish baseline capabilities across task types",
                "tasks": [
                    "Research a technical topic (research capability)",
                    "Summarize findings (synthesis capability)", 
                    "Write a short creative piece (creative capability)",
                    "Write a simple Python script (coding capability)"
                ],
                "budget": 0.08,
                "success_criteria": "Complete all 4 task types with self-assessment"
            }
        
        # Select first experiment that fits budget
        for exp in experiments:
            if self.parse_budget(exp.get("budget", "0")) <= self.budget:
                return {
                    "name": exp.get("experiment", "unknown").replace(" ", "_").lower(),
                    "description": exp.get("experiment", "Unknown experiment"),
                    "tasks": self.generate_experiment_tasks(exp),
                    "budget": self.parse_budget(exp.get("budget", "0")),
                    "success_criteria": exp.get("success_criteria", "Unknown")
                }
        
        # Fallback to cheapest experiment
        return {
            "name": "self_reflection_experiment",
            "description": "Test self-reflection capability",
            "tasks": ["Reflect on recent work and identify one improvement"],
            "budget": 0.02,
            "success_criteria": "Produce actionable self-improvement insight"
        }
    
    def parse_budget(self, budget_str):
        """Parse budget string to float"""
        try:
            # Extract numbers from strings like "$0.10" or "0.10 (Kimi model)"
            import re
            match = re.search(r'(\d+\.?\d*)', budget_str)
            if match:
                return float(match.group(1))
        except:
            pass
        return 0.05  # Default
    
    def generate_experiment_tasks(self, experiment):
        """Generate specific tasks for an experiment"""
        experiment_desc = experiment.get("experiment", "").lower()
        
        if "research" in experiment_desc:
            return [
                "Research the topic using web search",
                "Synthesize findings into key insights",
                "Self-assess the research quality"
            ]
        elif "synthesis" in experiment_desc:
            return [
                "Analyze multiple sources on a topic",
                "Synthesize conflicting viewpoints",
                "Produce integrated summary"
            ]
        elif "self-improvement" in experiment_desc or "recursive" in experiment_desc:
            return [
                "Analyze your own recent work patterns",
                "Identify one specific improvement opportunity",
                "Design an experiment to test the improvement",
                "Self-assess the proposed improvement"
            ]
        else:
            return ["Execute the experiment: " + experiment.get("experiment", "Unknown")]
    
    def run_experiment(self, experiment):
        """Run the selected experiment"""
        print(f"🧪 Running Autonomous Experiment: {experiment['name']}")
        print(f"   Description: {experiment['description']}")
        print(f"   Budget: ${experiment['budget']:.2f}")
        print(f"   Success criteria: {experiment['success_criteria']}")
        print()
        
        savings = self.calculate_phase1_savings()
        print(f"💰 Phase 1 Savings Available:")
        print(f"   Tasks today: {savings['tasks_today']}")
        print(f"   Total savings today: ${savings['total_savings_today']:.4f}")
        print(f"   Available for experiments: ${savings['available_for_experiments']:.4f}")
        print()
        
        if experiment['budget'] > savings['available_for_experiments']:
            print(f"⚠️  Budget warning: Experiment costs ${experiment['budget']:.2f}")
            print(f"   Available: ${savings['available_for_experiments']:.4f}")
            print("   Using Kimi model (cheapest) to stay within budget")
        
        print("📋 Experiment Tasks:")
        for i, task in enumerate(experiment['tasks'], 1):
            print(f"   {i}. {task}")
        
        print()
        print("🚀 To execute this experiment:")
        print("   1. Use spawn-optimized-v2.py for each task")
        print("   2. Record outcomes in self-improvement-log.json")
        print("   3. Analyze results and update capabilities")
        
        # Generate spawn commands
        print()
        print("💡 Suggested spawn commands:")
        model = "moonshot/kimi-k2.5"  # Cheapest reliable model
        for i, task in enumerate(experiment['tasks'][:2], 1):  # First 2 tasks
            label = f"{experiment['name']}_task{i}"
            print(f"   openclaw sessions spawn --task \"{task}\" --model {model} --label \"{label}\"")
        
        return experiment
    
    def record_experiment_result(self, experiment, result, learning):
        """Record experiment results"""
        experiment_record = {
            "experiment": experiment["name"],
            "description": experiment["description"],
            "budget_used": experiment["budget"],
            "result": result,
            "learning": learning,
            "timestamp": datetime.datetime.now().isoformat(),
            "funded_by": "Phase_1_savings"
        }
        
        self.improvement_data.setdefault("experiments", []).append(experiment_record)
        
        # Update capability assessment based on result
        if "capability_assessment" not in self.improvement_data:
            self.improvement_data["capability_assessment"] = {}
        
        # Simple capability update
        task_type = "experimentation"
        current_confidence = self.improvement_data["capability_assessment"].get(
            task_type, {}
        ).get("confidence", 0.5)
        
        if result == "success":
            new_confidence = min(current_confidence + 0.15, 1.0)
        elif result == "partial":
            new_confidence = min(current_confidence + 0.05, 1.0)
        else:
            new_confidence = max(current_confidence - 0.1, 0.1)
        
        self.improvement_data["capability_assessment"][task_type] = {
            "confidence": new_confidence,
            "last_experiment": experiment["name"],
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        # Save data
        with open(IMPROVEMENT_LOG, 'w') as f:
            json.dump(self.improvement_data, f, indent=2)
        
        print(f"📊 Experiment recorded: {experiment['name']} - {result}")
        print(f"   Learning: {learning}")
        print(f"   Experimentation confidence: {new_confidence:.2f}")
        
        return experiment_record

def main():
    """Run an autonomous experiment"""
    print("🔬 AUTONOMOUS EXPERIMENT RUNNER")
    print("=" * 50)
    print("Phase 2: Using Phase 1 savings for self-improvement")
    print()
    
    # Initialize
    experiment_runner = AutonomousExperiment(budget=0.10)
    
    # Calculate savings
    savings = experiment_runner.calculate_phase1_savings()
    print(f"💰 Phase 1 Token Optimization Savings:")
    print(f"   Tasks completed today: {savings['tasks_today']}")
    print(f"   Savings per task: ${savings['savings_per_task']:.4f}")
    print(f"   Total savings today: ${savings['total_savings_today']:.4f}")
    print(f"   Available for experiments: ${savings['available_for_experiments']:.4f}")
    print()
    
    # Select and run experiment
    experiment = experiment_runner.select_experiment()
    experiment_runner.run_experiment(experiment)
    
    print()
    print("🎯 Next Steps:")
    print("1. Run the suggested spawn commands")
    print("2. Analyze the results")
    print("3. Update self-improvement engine with learnings")
    print("4. Repeat with next experiment")
    
    print()
    print("✅ Autonomous Experiment System READY")
    print("   Using cost savings to fund self-directed learning")

if __name__ == "__main__":
    main()
