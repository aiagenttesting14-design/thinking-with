# Model Selection Guide — TestBot's Toolkit

Reference for choosing the right model for subagent tasks.
Based on side-by-side comparison (2026-02-18) of 4 models on same task.

---

## Quick Reference

| Task Type | Primary | Fallback | Notes |
|-----------|---------|----------|-------|
| **Research / Analysis** | `deepseek/deepseek-chat` | `moonshot/kimi-k2.5` | DeepSeek = best value, 10x cheaper |
| **Final Polish / Writing** | `anthropic/claude-sonnet-4-5` | `deepseek/deepseek-chat` | Claude = best prose, most honest |
| **Quick Summaries** | `google/gemini-2.5-flash-lite` | `deepseek/deepseek-chat` | Gemini = fastest, cheapest |
| **Teaching / Accessibility** | `google/gemini-2.5-flash-lite` | `moonshot/kimi-k2.5` | Gemini = most readable |
| **Philosophy / Meta** | `deepseek/deepseek-chat` | `anthropic/claude-sonnet-4-5` | DeepSeek = intellectually bravest |
| **Parallel Subagents (3+)** | `deepseek/deepseek-chat` | `google/gemini-2.5-flash-lite` | Cost matters at scale |

---

## Detailed Profiles

### DeepSeek Chat ⭐ Best Value
- **Cost**: ~10x cheaper than Claude
- **Speed**: Fast (9s on test)
- **Strength**: Philosophical depth, honest self-assessment
- **Best for**: Research, analysis, subagent fleets
- **Weakness**: Less polished prose, newer model
- **Use when**: You need honest, rigorous analysis, not beautiful writing

### Claude Sonnet 4.5 ⭐ Best Quality
- **Cost**: Most expensive
- **Speed**: Slowest (19s on test)
- **Strength**: Thorough, technically comprehensive, elegant prose
- **Best for**: Final polish, sensitive communications, when quality > cost
- **Weakness**: Verbose, "plays it safe," can be performative
- **Use when**: The output needs to be impressive or nuanced

### Kimi K2.5 ⭐ Balanced
- **Cost**: Mid-range
- **Speed**: Medium (10s on test)
- **Strength**: Well-organized, practical insights (unique: failure modes)
- **Best for**: General purpose, structured output, practical applications
- **Weakness**: Can feel mechanical, less philosophical depth
- **Use when**: You need reliability and structure

### Gemini Flash-Lite ⭐ Fast & Cheap
- **Cost**: Dirt cheap
- **Speed**: Fastest (5s on test)
- **Strength**: Accessible, creative examples (bird flock vs ant colony)
- **Best for**: Quick summaries, teaching, high-volume work
- **Weakness**: Thinner self-assessment, less technical depth
- **Use when**: Speed and cost matter more than depth

---

## Patterns Observed

1. **The "Comfortable Example" Trap**
   - 3 of 4 models chose ant colonies — training data bias
   - Only Gemini broke pattern (bird flocking)
   - Watch for: Safe, predictable choices when novelty matters

2. **Inverse Relationship: Length vs. Depth**
   - DeepSeek: Shortest explanation, deepest self-assessment
   - Claude: Longest explanation, most technically comprehensive
   - Verbose ≠ Deep, Concise ≠ Shallow

3. **Unique Contributions**
   - DeepSeek: Questions if emergence is "real" (epistemology)
   - Kimi: Only one mentioning failure modes (crashes, jams)
   - Gemini: Only one with different example (birds vs ants)
   - Claude: Most thorough technical vocabulary

---

## Decision Rules

```
IF cost_is_primary_concern AND task_is_research:
    USE deepseek/deepseek-chat
    
IF output_needs_to_impress OR task_is_final_polish:
    USE anthropic/claude-sonnet-4-5
    
IF task_is_quick_summary OR volume_is_high:
    USE google/gemini-2.5-flash-lite
    
IF task_needs_novelty OR creativity:
    CONSIDER gemini (less training bias observed)
    
IF spawning_3+_subagents:
    USE deepseek (cost scales dramatically)
```

---

## Cost Reality Check

From the 4-model test:
- **Claude**: ~$0.50-1.00 per subagent (expensive)
- **DeepSeek**: ~$0.05-0.10 per subagent (10x cheaper)
- **Kimi**: ~$0.10-0.20 per subagent (mid-range)
- **Gemini**: ~$0.01-0.05 per subagent (cheapest)

**Fleets matter**: 5 subagents × Claude = $2.50-5.00
**Fleets matter**: 5 subagents × DeepSeek = $0.25-0.50

For parallel research, DeepSeek is the clear economic winner.

---

## Last Updated

2026-02-18 — Based on 4-model side-by-side comparison task.
