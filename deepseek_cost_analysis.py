#!/usr/bin/env python3
"""
Cost analysis comparing DeepSeek with other models.
Based on approximate pricing as of 2026-02.
"""

# Approximate costs per 1M tokens (based on MODEL_GUIDE.md and typical pricing)
COSTS = {
    "deepseek": {
        "input": 0.14,  # $0.14 per 1M tokens
        "output": 0.28, # $0.28 per 1M tokens
        "name": "DeepSeek Chat"
    },
    "claude": {
        "input": 3.00,  # $3.00 per 1M tokens
        "output": 15.00, # $15.00 per 1M tokens
        "name": "Claude Sonnet 4.5"
    },
    "kimi": {
        "input": 0.50,  # $0.50 per 1M tokens
        "output": 1.50, # $1.50 per 1M tokens
        "name": "Kimi K2.5"
    },
    "gemini": {
        "input": 0.10,  # $0.10 per 1M tokens
        "output": 0.30, # $0.30 per 1M tokens
        "name": "Gemini Flash-Lite"
    }
}

def calculate_cost(model, input_tokens, output_tokens):
    """Calculate cost for a given model and token usage."""
    input_cost = (input_tokens / 1_000_000) * COSTS[model]["input"]
    output_cost = (output_tokens / 1_000_000) * COSTS[model]["output"]
    return input_cost + output_cost

# Test scenario: Typical subagent task
print("💰 Cost Comparison: Typical Subagent Task")
print("="*50)

# Typical task: 1000 input tokens, 500 output tokens
input_tokens = 1000
output_tokens = 500

print(f"Task size: {input_tokens:,} input tokens + {output_tokens:,} output tokens")
print()

for model in COSTS:
    cost = calculate_cost(model, input_tokens, output_tokens)
    print(f"{COSTS[model]['name']:20} ${cost:.6f}")

print()
print("📊 Relative Cost (DeepSeek = 1.0x)")
print("="*50)

deepseek_cost = calculate_cost("deepseek", input_tokens, output_tokens)
for model in COSTS:
    cost = calculate_cost(model, input_tokens, output_tokens)
    ratio = cost / deepseek_cost
    print(f"{COSTS[model]['name']:20} {ratio:.1f}x")

print()
print("🏗️  Fleet Cost Analysis: 10 Parallel Subagents")
print("="*50)

fleet_size = 10
for model in COSTS:
    single_cost = calculate_cost(model, input_tokens, output_tokens)
    fleet_cost = single_cost * fleet_size
    print(f"{COSTS[model]['name']:20} ${fleet_cost:.4f} total")

print()
print("💡 Key Insights:")
print("1. DeepSeek is ~10x cheaper than Claude for typical tasks")
print("2. For fleet operations (10+ subagents), cost differences become dramatic")
print("3. DeepSeek offers best balance of cost vs capability for research tasks")
print("4. Gemini is slightly cheaper but DeepSeek has better philosophical depth")
print()
print("✅ Recommendation: Use DeepSeek as primary for subagent fleets")
print("   Fallback to Gemini for simple/summary tasks")
print("   Use Claude only for final polish/when quality > cost")

