#!/usr/bin/env python3
"""
Intelligent Model Router
Routes tasks to appropriate models based on complexity, cost, and capability.
"""

import json
import sys

class ModelRouter:
    def __init__(self):
        # Model capabilities matrix
        self.capabilities = {
            "opus": {
                "strengths": ["strategy", "architecture", "complex_reasoning", "novel_solutions"],
                "weaknesses": ["cost", "speed"],
                "cost_per_1k": 0.015,
                "max_tokens": 4000,
                "priority": "high_quality_over_cost"
            },
            "kimi": {
                "strengths": ["research", "analysis", "coding", "long_context"],
                "weaknesses": ["creative_writing", "complex_math"],
                "cost_per_1k": 0.002,
                "max_tokens": 128000,
                "priority": "cost_effective_research"
            },
            "deepseek": {
                "strengths": ["coding", "debugging", "technical", "efficiency"],
                "weaknesses": ["creative", "strategic"],
                "cost_per_1k": 0.0014,
                "max_tokens": 32000,
                "priority": "technical_tasks"
            },
            "gemini": {
                "strengths": ["summarization", "translation", "simple_qna", "speed"],
                "weaknesses": ["complex_reasoning", "technical_depth"],
                "cost_per_1k": 0.001,
                "max_tokens": 1000000,
                "priority": "high_volume_simple_tasks"
            },
            "claude-sonnet": {
                "strengths": ["reasoning", "planning", "creative", "balanced"],
                "weaknesses": ["cost_vs_alternatives"],
                "cost_per_1k": 0.003,
                "max_tokens": 200000,
                "priority": "when_opus_too_expensive"
            }
        }
        
        # Task type to model mapping
        self.task_mappings = {
            "architecture_design": ["opus", "claude-sonnet"],
            "strategic_planning": ["opus", "claude-sonnet"],
            "research_analysis": ["kimi", "gemini"],
            "coding_implementation": ["deepseek", "kimi"],
            "bug_fixing": ["deepseek"],
            "documentation": ["kimi", "gemini"],
            "summarization": ["gemini", "kimi"],
            "data_processing": ["deepseek", "gemini"],
            "creative_writing": ["claude-sonnet", "opus"],
            "quality_review": ["claude-sonnet", "deepseek"]
        }
    
    def classify_task(self, task_description):
        """Classify task into one or more categories."""
        
        task_lower = task_description.lower()
        categories = []
        
        # Architecture & Strategy
        arch_keywords = ["design", "architecture", "system", "framework", "orchestrate", "coordinate"]
        if any(kw in task_lower for kw in arch_keywords):
            categories.append("architecture_design")
        
        # Research
        research_keywords = ["research", "analyze", "compare", "find", "market", "survey"]
        if any(kw in task_lower for kw in research_keywords):
            categories.append("research_analysis")
        
        # Coding
        coding_keywords = ["code", "script", "implement", "function", "algorithm", "debug"]
        if any(kw in task_lower for kw in coding_keywords):
            categories.append("coding_implementation")
        
        # Bug fixing
        bug_keywords = ["fix", "bug", "error", "issue", "problem", "debug"]
        if any(kw in task_lower for kw in bug_keywords):
            categories.append("bug_fixing")
        
        # Documentation
        doc_keywords = ["document", "explain", "describe", "write", "summary"]
        if any(kw in task_lower for kw in doc_keywords):
            categories.append("documentation")
        
        # Summarization
        sum_keywords = ["summarize", "brief", "overview", "tl;dr", "condense"]
        if any(kw in task_lower for kw in sum_keywords):
            categories.append("summarization")
        
        # If no categories found, default to research
        if not categories:
            categories.append("research_analysis")
        
        return categories
    
    def select_model(self, task_description, budget_constraint=None, quality_requirement="balanced"):
        """Select the best model for a task."""
        
        categories = self.classify_task(task_description)
        
        # Get candidate models for all categories
        candidate_models = set()
        for category in categories:
            if category in self.task_mappings:
                candidate_models.update(self.task_mappings[category])
        
        if not candidate_models:
            candidate_models = {"kimi"}  # Default fallback
        
        # Score each candidate
        model_scores = {}
        
        for model in candidate_models:
            score = 0
            
            # Cost score (lower is better)
            cost_score = 10 - (self.capabilities[model]["cost_per_1k"] * 1000)
            score += cost_score * 0.4  # 40% weight to cost
            
            # Capability match
            capability_match = 0
            for category in categories:
                if model in self.task_mappings.get(category, []):
                    capability_match += 2
            score += capability_match * 0.3  # 30% weight to capability
            
            # Quality requirement
            if quality_requirement == "high":
                if model in ["opus", "claude-sonnet"]:
                    score += 5
            elif quality_requirement == "cost_effective":
                if model in ["kimi", "gemini", "deepseek"]:
                    score += 5
            
            # Budget constraint
            if budget_constraint:
                estimated_cost = len(task_description.split()) / 750 * self.capabilities[model]["cost_per_1k"]
                if estimated_cost <= budget_constraint:
                    score += 3
            
            model_scores[model] = score
        
        # Select best model
        best_model = max(model_scores, key=model_scores.get)
        
        # Get alternatives (second best)
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = [model for model, score in sorted_models[1:3]]
        
        return {
            "primary_model": best_model,
            "alternatives": alternatives,
            "scores": model_scores,
            "categories": categories,
            "cost_estimate": len(task_description.split()) / 750 * self.capabilities[best_model]["cost_per_1k"],
            "rationale": f"Selected {best_model} for {', '.join(categories)} with score {model_scores[best_model]:.1f}"
        }
    
    def create_fallback_chain(self, task_description, max_attempts=3):
        """Create a fallback chain if primary model fails."""
        
        selection = self.select_model(task_description)
        primary = selection["primary_model"]
        
        # Order models by cost (cheapest first for fallback)
        models_by_cost = sorted(
            self.capabilities.keys(),
            key=lambda m: self.capabilities[m]["cost_per_1k"]
        )
        
        # Remove primary from fallback chain
        fallback_chain = [m for m in models_by_cost if m != primary][:max_attempts-1]
        
        return {
            "primary": primary,
            "fallback_chain": fallback_chain,
            "strategy": "Try primary, then fall back to cheaper models",
            "max_cost": self.capabilities[primary]["cost_per_1k"] * 2  # Estimate
        }
    
    def batch_route_tasks(self, tasks):
        """Route multiple tasks optimally."""
        
        routed_tasks = []
        total_cost = 0
        
        for task in tasks:
            route = self.select_model(task)
            cost = route["cost_estimate"]
            
            routed_tasks.append({
                "task": task[:50] + "..." if len(task) > 50 else task,
                "model": route["primary_model"],
                "cost_estimate": cost,
                "categories": route["categories"]
            })
            
            total_cost += cost
        
        # Group by model for efficiency
        model_groups = {}
        for rt in routed_tasks:
            model = rt["model"]
            if model not in model_groups:
                model_groups[model] = []
            model_groups[model].append(rt)
        
        return {
            "routed_tasks": routed_tasks,
            "model_groups": model_groups,
            "total_estimated_cost": total_cost,
            "model_distribution": {model: len(tasks) for model, tasks in model_groups.items()},
            "cost_by_model": {
                model: sum(rt["cost_estimate"] for rt in tasks)
                for model, tasks in model_groups.items()
            }
        }

def main():
    """Test the model router."""
    
    router = ModelRouter()
    
    test_tasks = [
        "Design the architecture for a multi-agent AI system",
        "Research current AI pricing models and summarize",
        "Fix the JavaScript bug in the constellation visualization",
        "Write documentation for the new autonomy engine",
        "Create a summary of today's AI news"
    ]
    
    print("=" * 80)
    print("INTELLIGENT MODEL ROUTER - DEMONSTRATION")
    print("=" * 80)
    
    # Individual routing
    for i, task in enumerate(test_tasks):
        print(f"\n{'='*60}")
        print(f"TASK {i+1}: {task}")
        print(f"{'='*60}")
        
        route = router.select_model(task)
        
        print(f"Categories: {', '.join(route['categories'])}")
        print(f"Primary Model: {route['primary_model']}")
        print(f"Alternatives: {', '.join(route['alternatives'])}")
        print(f"Cost Estimate: ${route['cost_estimate']:.4f}")
        print(f"Rationale: {route['rationale']}")
        
        # Fallback chain
        fallback = router.create_fallback_chain(task)
        print(f"Fallback Chain: {fallback['primary']} → {' → '.join(fallback['fallback_chain'])}")
    
    # Batch routing
    print(f"\n{'='*80}")
    print("BATCH ROUTING OPTIMIZATION")
    print(f"{'='*80}")
    
    batch = router.batch_route_tasks(test_tasks)
    
    print(f"\nTotal Tasks: {len(test_tasks)}")
    print(f"Total Estimated Cost: ${batch['total_estimated_cost']:.4f}")
    
    print(f"\nModel Distribution:")
    for model, count in batch["model_distribution"].items():
        cost = batch["cost_by_model"][model]
        print(f"  {model}: {count} tasks (${cost:.4f})")
    
    print(f"\nOptimal Grouping:")
    for model, tasks in batch["model_groups"].items():
        print(f"\n  {model.upper()}:")
        for task in tasks:
            print(f"    • {task['task']}")

if __name__ == "__main__":
    main()
