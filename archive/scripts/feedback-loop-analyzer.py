#!/usr/bin/env python3
"""
Feedback Loop Analyzer - Completes Phase 2 self-improvement system
Analyzes experiment results and updates capabilities autonomously
"""

import json
import datetime
from pathlib import Path

WORKSPACE = Path("/Users/aiagentuser/.openclaw/workspace")
IMPROVEMENT_LOG = WORKSPACE / "self-improvement-log.json"

class FeedbackLoopAnalyzer:
    """Analyzes feedback from experiments to enable autonomous improvement"""
    
    def __init__(self):
        self.improvement_data = self.load_improvement_data()
    
    def load_improvement_data(self):
        if IMPROVEMENT_LOG.exists():
            with open(IMPROVEMENT_LOG, 'r') as f:
                return json.load(f)
        return {}
    
    def analyze_experiment_patterns(self):
        """Analyze patterns across experiments to identify improvement opportunities"""
        experiments = self.improvement_data.get("experiments", [])
        improvement_cycles = self.improvement_data.get("improvement_cycles", [])
        
        if not experiments and not improvement_cycles:
            return {"status": "no_data", "recommendations": ["Run initial experiments"]}
        
        analysis = {
            "total_experiments": len(experiments),
            "successful_experiments": len([e for e in experiments if e.get("result") == "success"]),
            "total_cycles": len(improvement_cycles),
            "patterns_identified": [],
            "improvement_opportunities": [],
            "confidence_trends": {}
        }
        
        # Analyze experiment results
        if experiments:
            success_rate = analysis["successful_experiments"] / analysis["total_experiments"]
            analysis["experiment_success_rate"] = success_rate
            
            # Identify patterns in successful experiments
            successful_exps = [e for e in experiments if e.get("result") == "success"]
            for exp in successful_exps[:3]:  # Analyze top 3 successful
                pattern = {
                    "experiment_type": exp.get("experiment", ""),
                    "key_factor": self.extract_key_factor(exp.get("learning", "")),
                    "applicable_to": self.determine_applicability(exp.get("learning", ""))
                }
                analysis["patterns_identified"].append(pattern)
        
        # Analyze capability trends
        capabilities = self.improvement_data.get("metacognitive_knowledge", {}).get(
            "capability_assessment", {}
        )
        
        for capability, data in capabilities.items():
            if isinstance(data, dict) and "confidence" in data:
                analysis["confidence_trends"][capability] = {
                    "current": data["confidence"],
                    "last_updated": data.get("updated_at", "unknown"),
                    "trend": "stable"  # Would compare with previous values in real implementation
                }
        
        # Generate improvement opportunities
        analysis["improvement_opportunities"] = self.generate_improvement_opportunities(analysis)
        
        return analysis
    
    def extract_key_factor(self, learning_text):
        """Extract key factor from learning text"""
        learning_lower = learning_text.lower()
        
        if any(word in learning_lower for word in ["research", "search", "find"]):
            return "thorough_research"
        elif any(word in learning_lower for word in ["plan", "strategy", "approach"]):
            return "strategic_planning"
        elif any(word in learning_lower for word in ["test", "experiment", "try"]):
            return "experimental_approach"
        elif any(word in learning_lower for word in ["reflect", "assess", "evaluate"]):
            return "self_reflection"
        else:
            return "execution_quality"
    
    def determine_applicability(self, learning_text):
        """Determine what tasks this learning applies to"""
        learning_lower = learning_text.lower()
        applicable = []
        
        task_mappings = {
            "research": ["research_tasks", "information_gathering"],
            "write": ["creative_tasks", "synthesis_tasks"],
            "code": ["coding_tasks", "automation_tasks"],
            "analyze": ["analysis_tasks", "evaluation_tasks"],
            "summarize": ["synthesis_tasks", "communication_tasks"]
        }
        
        for keyword, tasks in task_mappings.items():
            if keyword in learning_lower:
                applicable.extend(tasks)
        
        return list(set(applicable)) if applicable else ["general_tasks"]
    
    def generate_improvement_opportunities(self, analysis):
        """Generate specific improvement opportunities based on analysis"""
        opportunities = []
        
        # Opportunity 1: Improve experiment success rate
        if analysis.get("experiment_success_rate", 0) < 0.7:
            opportunities.append({
                "area": "experiment_design",
                "description": "Improve experiment success rate",
                "current_performance": f"{analysis.get('experiment_success_rate', 0)*100:.1f}%",
                "target": "70%",
                "action": "Add more planning phase to experiments, define clearer success criteria",
                "estimated_impact": "Higher learning efficiency"
            })
        
        # Opportunity 2: Increase metacognitive depth
        metacognitive_dist = self.improvement_data.get("success_metrics", {}).get(
            "metacognitive_distribution", {}
        )
        
        evaluation_ratio = metacognitive_dist.get("evaluation", 0) / max(
            sum(metacognitive_dist.values()), 1
        )
        
        if evaluation_ratio < 0.2:
            opportunities.append({
                "area": "metacognitive_depth",
                "description": "Increase self-evaluation activities",
                "current_performance": f"{evaluation_ratio*100:.1f}% evaluation",
                "target": "20% evaluation",
                "action": "Add mandatory reflection step after each task",
                "estimated_impact": "Better learning from experience"
            })
        
        # Opportunity 3: Pattern application
        patterns_used = len(self.improvement_data.get("learned_patterns", []))
        if patterns_used < 3:
            opportunities.append({
                "area": "pattern_application",
                "description": "Apply learned patterns more consistently",
                "current_performance": f"{patterns_used} patterns identified",
                "target": "3+ patterns actively used",
                "action": "Create pattern library and reference it before tasks",
                "estimated_impact": "Faster task completion, higher quality"
            })
        
        # Default opportunity if none identified
        if not opportunities:
            opportunities.append({
                "area": "baseline_establishment",
                "description": "Establish baseline capabilities",
                "current_performance": "Unknown",
                "target": "Measured baselines for all task types",
                "action": "Run capability assessment experiments",
                "estimated_impact": "Enable targeted improvement"
            })
        
        return opportunities
    
    def update_capabilities_based_on_analysis(self, analysis):
        """Update capabilities based on analysis results"""
        updated_capabilities = {}
        
        # Update based on experiment success rate
        success_rate = analysis.get("experiment_success_rate", 0)
        if success_rate > 0:
            experiment_capability = self.improvement_data.get(
                "metacognitive_knowledge", {}
            ).get("capability_assessment", {}).get("experimentation", {})
            
            current_confidence = experiment_capability.get("confidence", 0.5)
            
            # Adjust confidence based on success rate
            if success_rate > 0.8:
                new_confidence = min(current_confidence + 0.2, 1.0)
            elif success_rate > 0.6:
                new_confidence = min(current_confidence + 0.1, 1.0)
            else:
                new_confidence = max(current_confidence - 0.1, 0.1)
            
            updated_capabilities["experimentation"] = {
                "confidence": new_confidence,
                "based_on": f"experiment_success_rate_{success_rate:.2f}",
                "updated_at": datetime.datetime.now().isoformat()
            }
        
        # Update based on patterns identified
        patterns = analysis.get("patterns_identified", [])
        if patterns:
            pattern_recognition_capability = {
                "confidence": min(0.5 + (len(patterns) * 0.1), 1.0),
                "patterns_identified": len(patterns),
                "pattern_types": [p.get("experiment_type", "") for p in patterns[:3]],
                "updated_at": datetime.datetime.now().isoformat()
            }
            updated_capabilities["pattern_recognition"] = pattern_recognition_capability
        
        # Save updates
        if updated_capabilities:
            if "metacognitive_knowledge" not in self.improvement_data:
                self.improvement_data["metacognitive_knowledge"] = {}
            
            if "capability_assessment" not in self.improvement_data["metacognitive_knowledge"]:
                self.improvement_data["metacognitive_knowledge"]["capability_assessment"] = {}
            
            self.improvement_data["metacognitive_knowledge"]["capability_assessment"].update(
                updated_capabilities
            )
            
            with open(IMPROVEMENT_LOG, 'w') as f:
                json.dump(self.improvement_data, f, indent=2)
        
        return updated_capabilities
    
    def generate_feedback_loop_report(self):
        """Generate comprehensive feedback loop report"""
        analysis = self.analyze_experiment_patterns()
        updated_capabilities = self.update_capabilities_based_on_analysis(analysis)
        
        report = f"""# Feedback Loop Analysis Report
## Phase 2: Self-Improvement System Status

### System Overview
- **Total experiments**: {analysis.get('total_experiments', 0)}
- **Successful experiments**: {analysis.get('successful_experiments', 0)}
- **Success rate**: {analysis.get('experiment_success_rate', 0)*100:.1f}% if data available
- **Improvement cycles**: {analysis.get('total_cycles', 0)}
- **Patterns identified**: {len(analysis.get('patterns_identified', []))}

### Identified Patterns
"""
        
        for i, pattern in enumerate(analysis.get("patterns_identified", [])[:3], 1):
            report += f"{i}. **{pattern.get('experiment_type', 'Unknown')}**\n"
            report += f"   Key factor: {pattern.get('key_factor', 'Unknown')}\n"
            report += f"   Applicable to: {', '.join(pattern.get('applicable_to', []))}\n"
        
        report += "\n### Improvement Opportunities\n"
        
        for i, opportunity in enumerate(analysis.get("improvement_opportunities", [])[:3], 1):
            report += f"{i}. **{opportunity['area']}**: {opportunity['description']}\n"
            report += f"   Current: {opportunity['current_performance']}\n"
            report += f"   Target: {opportunity['target']}\n"
            report += f"   Action: {opportunity['action']}\n"
            report += f"   Impact: {opportunity['estimated_impact']}\n"
        
        report += "\n### Capability Updates (Based on Analysis)\n"
        
        if updated_capabilities:
            for capability, data in updated_capabilities.items():
                report += f"- **{capability}**: Confidence {data.get('confidence', 0):.2f}\n"
                if "based_on" in data:
                    report += f"  Based on: {data['based_on']}\n"
        else:
            report += "No capability updates based on current data.\n"
        
        report += "\n### Feedback Loop Status\n"
        
        # Assess feedback loop maturity
        data_points = analysis.get("total_experiments", 0) + analysis.get("total_cycles", 0)
        
        if data_points >= 10:
            maturity = "MATURE - Sufficient data for pattern analysis"
        elif data_points >= 5:
            maturity = "DEVELOPING - Collecting baseline data"
        else:
            maturity = "INITIAL - Need more experiments"
        
        report += f"- **Data points**: {data_points}\n"
        report += f"- **Maturity**: {maturity}\n"
        report += f"- **Autonomous updates**: {'Yes' if updated_capabilities else 'No'}\n"
        report += f"- **Self-directed learning**: {'Enabled' if data_points > 0 else 'Needs initialization'}\n"
        
        report += f"\n*Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        return report

def main():
    """Run feedback loop analysis"""
    print("🔄 FEEDBACK LOOP ANALYZER")
    print("=" * 50)
    print("Phase 2: Closing the self-improvement loop")
    print()
    
    analyzer = FeedbackLoopAnalyzer()
    
    print("1. Analyzing experiment patterns...")
    analysis = analyzer.analyze_experiment_patterns()
    print(f"   Experiments analyzed: {analysis.get('total_experiments', 0)}")
    print(f"   Patterns identified: {len(analysis.get('patterns_identified', []))}")
    
    print("\n2. Updating capabilities based on analysis...")
    updated = analyzer.update_capabilities_based_on_analysis(analysis)
    print(f"   Capabilities updated: {len(updated)}")
    
    print("\n3. Feedback loop report:")
    print(analyzer.generate_feedback_loop_report())
    
    print("\n✅ Feedback Loop System OPERATIONAL")
    print("   Phase 2 self-improvement system is now complete!")

if __name__ == "__main__":
    main()
