#!/usr/bin/env python3
"""
Self-Improvement Engine - Phase 2
Implements intrinsic metacognition based on research findings
"""

import json
import os
import datetime
from pathlib import Path

WORKSPACE = Path("/Users/aiagentuser/.openclaw/workspace")
IMPROVEMENT_LOG = WORKSPACE / "self-improvement-log.json"
RESEARCH_FILE = WORKSPACE / "research/agent-self-improvement.md"

class SelfImprovementEngine:
    """Implements intrinsic metacognition for autonomous learning"""
    
    def __init__(self):
        self.improvement_data = self.load_improvement_data()
        self.research_insights = self.load_research_insights()
        
    def load_improvement_data(self):
        """Load or initialize self-improvement tracking"""
        if IMPROVEMENT_LOG.exists():
            with open(IMPROVEMENT_LOG, 'r') as f:
                return json.load(f)
        
        return {
            "metacognitive_knowledge": {
                "capability_assessment": {},
                "task_understanding": {},
                "learning_strategies": []
            },
            "improvement_cycles": [],
            "learned_patterns": [],
            "success_metrics": {},
            "created_at": datetime.datetime.now().isoformat()
        }
    
    def load_research_insights(self):
        """Load research insights about self-improvement"""
        insights = {
            "levels_of_autonomy": [
                "Stateless/Deterministic",
                "Context-Aware", 
                "Goal-Directed",
                "Fully Autonomous"
            ],
            "metacognitive_framework": {
                "knowledge": "Self-assessment of capabilities, task understanding, learning strategy inventory",
                "planning": "Deciding what to learn, selecting learning strategies, resource allocation",
                "evaluation": "Reflecting on learning experiences, adapting strategies, continuous self-assessment"
            },
            "self_improvement_patterns": [
                "Feedback Loops",
                "Example Accumulation", 
                "Prompt Evolution",
                "Strategy Selection"
            ]
        }
        
        return insights
    
    def assess_capabilities(self, task_type, outcome):
        """Self-assessment of capabilities based on task outcomes"""
        assessment = {
            "task_type": task_type,
            "outcome": outcome,
            "timestamp": datetime.datetime.now().isoformat(),
            "confidence_change": 0,
            "learned_skill": ""
        }
        
        # Simple assessment logic
        if outcome == "success":
            assessment["confidence_change"] = 0.1
            assessment["learned_skill"] = f"Successfully completed {task_type}"
        elif outcome == "partial":
            assessment["confidence_change"] = 0.05
            assessment["learned_skill"] = f"Partially completed {task_type}, needs refinement"
        else:
            assessment["confidence_change"] = -0.1
            assessment["learned_skill"] = f"Failed at {task_type}, need to learn alternative approach"
        
        # Store assessment
        self.improvement_data["metacognitive_knowledge"].setdefault(
            "capability_assessment", {}
        )[task_type] = assessment
        
        self.save_data()
        return assessment
    
    def record_improvement_cycle(self, task, approach, result, learning):
        """Record a complete improvement cycle"""
        cycle = {
            "task": task,
            "approach": approach,
            "result": result,
            "learning": learning,
            "timestamp": datetime.datetime.now().isoformat(),
            "metacognitive_level": self.determine_metacognitive_level(task, approach)
        }
        
        self.improvement_data["improvement_cycles"].append(cycle)
        
        # Extract patterns if successful
        if result in ["success", "partial"]:
            pattern = {
                "task_pattern": task,
                "effective_approach": approach,
                "key_learning": learning,
                "first_observed": datetime.datetime.now().isoformat()
            }
            self.improvement_data["learned_patterns"].append(pattern)
        
        self.save_data()
        return cycle
    
    def determine_metacognitive_level(self, task, approach):
        """Determine level of metacognition used"""
        approach_lower = approach.lower()
        
        if "self-assess" in approach_lower or "reflect" in approach_lower:
            return "evaluation"
        elif "plan" in approach_lower or "strategy" in approach_lower:
            return "planning"
        elif "learn" in approach_lower or "research" in approach_lower:
            return "knowledge"
        else:
            return "execution"
    
    def generate_learning_plan(self):
        """Generate autonomous learning plan based on gaps"""
        gaps = self.identify_capability_gaps()
        
        plan = {
            "generated_at": datetime.datetime.now().isoformat(),
            "learning_priorities": [],
            "experiments_to_run": [],
            "resources_needed": [],
            "success_metrics": {}
        }
        
        for gap in gaps[:3]:  # Top 3 gaps
            experiment = {
                "gap": gap["description"],
                "experiment": f"Test alternative approach for {gap['task_type']}",
                "budget": "Use Phase 1 savings (cheap models)",
                "success_criteria": f"Complete {gap['task_type']} with improved outcome"
            }
            plan["experiments_to_run"].append(experiment)
            
            plan["learning_priorities"].append({
                "priority": f"Improve {gap['task_type']} capability",
                "current_confidence": gap.get("confidence", 0.5),
                "target_confidence": 0.8
            })
        
        # Add meta-learning experiment
        plan["experiments_to_run"].append({
            "gap": "Limited self-improvement capability",
            "experiment": "Test recursive self-improvement loop",
            "budget": "0.10 (Kimi model for self-reflection)",
            "success_criteria": "Successfully modify own approach based on reflection"
        })
        
        self.improvement_data["current_learning_plan"] = plan
        self.save_data()
        
        return plan
    
    def identify_capability_gaps(self):
        """Identify gaps in capabilities based on past performance"""
        gaps = []
        
        # Analyze capability assessments
        assessments = self.improvement_data["metacognitive_knowledge"].get(
            "capability_assessment", {}
        )
        
        for task_type, assessment in assessments.items():
            confidence = 0.5 + assessment.get("confidence_change", 0)
            
            if confidence < 0.7:  # Below threshold
                gaps.append({
                    "task_type": task_type,
                    "description": f"Low confidence in {task_type}",
                    "confidence": confidence,
                    "last_attempt": assessment.get("timestamp"),
                    "suggested_approach": "Research alternative methods, practice with variations"
                })
        
        # If no assessments yet, suggest baseline experiments
        if not gaps:
            gaps = [
                {
                    "task_type": "research_tasks",
                    "description": "No baseline established for research tasks",
                    "confidence": 0.5,
                    "suggested_approach": "Run controlled research experiments"
                },
                {
                    "task_type": "synthesis_tasks", 
                    "description": "No baseline established for synthesis tasks",
                    "confidence": 0.5,
                    "suggested_approach": "Test different synthesis approaches"
                }
            ]
        
        return gaps
    
    def calculate_success_metrics(self):
        """Calculate improvement success metrics"""
        cycles = self.improvement_data.get("improvement_cycles", [])
        
        if not cycles:
            return {"status": "No cycles recorded yet"}
        
        successful = len([c for c in cycles if c.get("result") == "success"])
        partial = len([c for c in cycles if c.get("result") == "partial"])
        failed = len([c for c in cycles if c.get("result") == "failed"])
        
        total = len(cycles)
        success_rate = (successful + (partial * 0.5)) / total if total > 0 else 0
        
        metrics = {
            "total_cycles": total,
            "successful": successful,
            "partial": partial,
            "failed": failed,
            "success_rate": round(success_rate, 3),
            "learned_patterns": len(self.improvement_data.get("learned_patterns", [])),
            "metacognitive_distribution": self.analyze_metacognitive_distribution()
        }
        
        self.improvement_data["success_metrics"] = metrics
        self.save_data()
        
        return metrics
    
    def analyze_metacognitive_distribution(self):
        """Analyze distribution of metacognitive levels"""
        cycles = self.improvement_data.get("improvement_cycles", [])
        
        distribution = {
            "execution": 0,
            "knowledge": 0,
            "planning": 0,
            "evaluation": 0
        }
        
        for cycle in cycles:
            level = cycle.get("metacognitive_level", "execution")
            distribution[level] = distribution.get(level, 0) + 1
        
        return distribution
    
    def save_data(self):
        """Save improvement data"""
        with open(IMPROVEMENT_LOG, 'w') as f:
            json.dump(self.improvement_data, f, indent=2)
    
    def generate_improvement_report(self):
        """Generate self-improvement progress report"""
        metrics = self.calculate_success_metrics()
        gaps = self.identify_capability_gaps()
        
        report = f"""# Self-Improvement Engine Report
## Phase 2: Intrinsic Metacognition Implementation

### Current Status
- **Improvement cycles**: {metrics.get('total_cycles', 0)}
- **Success rate**: {metrics.get('success_rate', 0)*100:.1f}%
- **Learned patterns**: {metrics.get('learned_patterns', 0)}
- **Metacognitive distribution**: {json.dumps(metrics.get('metacognitive_distribution', {}), indent=2)}

### Capability Gaps Identified
"""
        
        for i, gap in enumerate(gaps[:5], 1):
            report += f"{i}. **{gap['task_type']}**: {gap['description']}\n"
            report += f"   Confidence: {gap.get('confidence', 0.5):.2f}\n"
            report += f"   Suggested: {gap.get('suggested_approach', 'No suggestion')}\n"
        
        # Learning plan
        if "current_learning_plan" in self.improvement_data:
            plan = self.improvement_data["current_learning_plan"]
            report += f"\n### Active Learning Plan (Generated: {plan.get('generated_at', 'Unknown')})\n"
            
            report += "\n**Experiments to Run:**\n"
            for exp in plan.get("experiments_to_run", [])[:3]:
                report += f"- {exp.get('experiment', 'Unknown')}\n"
                report += f"  Budget: {exp.get('budget', 'Unknown')}\n"
        
        # Research insights applied
        report += "\n### Research Insights Applied\n"
        report += "1. **Intrinsic Metacognition**: Self-assessment → Planning → Evaluation loop\n"
        report += "2. **Feedback Loops**: Recording outcomes to adjust future behavior\n"
        report += "3. **Pattern Recognition**: Extracting successful approaches for reuse\n"
        report += "4. **Autonomous Learning**: Self-directed capability improvement\n"
        
        report += f"\n*Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        return report

def main():
    """Test the self-improvement engine"""
    engine = SelfImprovementEngine()
    
    print("🧠 Self-Improvement Engine - Phase 2")
    print("=" * 50)
    
    # Test capability assessment
    print("\n1. Testing capability assessment...")
    assessment = engine.assess_capabilities("research_tasks", "success")
    print(f"   Research tasks: {assessment['outcome']} (confidence: {assessment['confidence_change']:+})")
    
    # Test improvement cycle recording
    print("\n2. Recording improvement cycle...")
    cycle = engine.record_improvement_cycle(
        task="Build token optimization system",
        approach="Research-based design with iterative testing",
        result="success",
        learning="Task-based model routing saves 83-92% costs"
    )
    print(f"   Recorded: {cycle['task'][:50]}...")
    print(f"   Metacognitive level: {cycle['metacognitive_level']}")
    
    # Generate learning plan
    print("\n3. Generating autonomous learning plan...")
    plan = engine.generate_learning_plan()
    print(f"   Learning priorities: {len(plan['learning_priorities'])}")
    print(f"   Experiments to run: {len(plan['experiments_to_run'])}")
    
    # Generate report
    print("\n4. Self-improvement report:")
    print(engine.generate_improvement_report())
    
    print("\n✅ Self-Improvement Engine initialized and ready!")
    print("   Using Phase 1 savings to fund autonomous learning experiments")

if __name__ == "__main__":
    main()
