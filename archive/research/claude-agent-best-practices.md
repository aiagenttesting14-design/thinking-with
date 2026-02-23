# Claude/Anthropic Agent Best Practices Research

## Executive Summary

This document compiles research on Anthropic's official guidance for using Claude as an agent, Constitutional AI principles, long-running session management, prompt engineering techniques, and how Claude differs from other models for agent work. The focus is on practical improvements that can be implemented immediately.

---

## 1. Anthropic's Official Guidance on Using Claude as an Agent

### Agent Skills Architecture

Anthropic has developed **Agent Skills** - a filesystem-based approach to equipping Claude with domain-specific expertise:

- **Structure**: A skill is a directory containing a `SKILL.md` file with YAML frontmatter (name, description) and task-specific instructions
- **Progressive Disclosure**: Skills use a three-tier loading system:
  1. Metadata (name/description) pre-loaded into system prompt
  2. Full SKILL.md loaded when Claude determines relevance
  3. Additional linked files loaded only when needed for specific sub-tasks
- **Code Integration**: Skills can bundle executable scripts that Claude runs deterministically rather than generating code
- **Storage**: Filesystem-based, making the context effectively unbounded

**Practical Implementation:**
```
pdf-skill/
├── SKILL.md          # Core instructions + metadata
├── reference.md      # Detailed reference material
└── forms.md          # Form-filling specific guidance
```

### Claude Agent SDK Components

- **Context Management**: Automatic compaction as conversations approach limits
- **Tool Use**: File operations, bash commands, code execution
- **State Persistence**: Progress tracking via files (progress.txt, tests.json)
- **Verification Tools**: Playwright MCP server for UI testing, computer use capabilities

### Key Design Principles from Anthropic

1. **Start with evaluation** - Identify capability gaps before building solutions
2. **Structure for scale** - Split skills into separate files when they become unwieldy
3. **Think from Claude's perspective** - Monitor real usage and iterate based on observed behavior
4. **Iterate with Claude** - Ask Claude to capture successful approaches into reusable skills

---

## 2. Constitutional AI and Agent Behavior

### What is Constitutional AI?

Constitutional AI (CAI) is Anthropic's method for training AI systems that are helpful, honest, and harmless through self-improvement with minimal human oversight:

- **Core Mechanism**: Uses a "constitution" - a set of natural language principles that guide AI behavior
- **Process**: 
  - Supervised learning phase with self-critiques and revisions
  - Reinforcement learning from AI Feedback (RLAIF)
- **Key Advantage**: Reduces reliance on human feedback labels for harmlessness

### Constitutional Principles Applied to Agents

The constitution guides models to:
- Avoid toxic or discriminatory outputs
- Refuse illegal or unethical activities
- Engage with harmful queries by explaining objections rather than being evasive
- Maintain transparency in decision-making through chain-of-thought reasoning

### Implications for Agent Design

1. **Self-Correction**: Claude is trained to critique and revise its own outputs based on constitutional principles
2. **Transparency**: Agents should explain their reasoning and decisions
3. **Safety-First**: Built-in resistance to jailbreaks and harmful instructions
4. **Honesty**: Tendency to acknowledge uncertainty rather than hallucinate confidently

### Collective Constitutional AI

Anthropic has experimented with constitutions curated through public input, allowing external stakeholders to shape agent behavior through deliberation processes.

---

## 3. Claude's Strengths and Weaknesses in Long-Running Sessions

### Context Window Specifications

| Model | Context Window | Key Feature |
|-------|---------------|-------------|
| Claude Opus 4.x | 200K tokens | Extended thinking mode |
| Claude Sonnet 4.x | 200K tokens | Context awareness |
| Claude Haiku 4.x | 200K tokens | Fastest for simple tasks |

**Context Awareness**: Claude 4.6+ models track their remaining token budget throughout conversations, enabling better task management.

### Strengths in Long Sessions

1. **State Tracking**: Exceptional ability to maintain orientation across extended sessions
2. **Incremental Progress**: Focuses on steady advances on a few things at a time rather than attempting everything at once
3. **Multi-Window Workflows**: Can work across context windows by saving state and continuing with fresh context
4. **Git Integration**: Performs especially well using git to track state across sessions
5. **Automatic Compaction**: Server-side context management allows conversations to continue indefinitely in most cases

### Weaknesses and Failure Modes

1. **Context Limit Errors**: When limits are reached, may require `/clear` which loses accumulated understanding
2. **One-Shot Tendency**: Without guidance, may try to do too much at once and run out of context mid-implementation
3. **Premature Victory**: May declare a project complete when features are only partially implemented
4. **Undocumented Progress**: Without structured tracking, can leave environment in messy state between sessions

### Mitigation Strategies

**For Long-Running Tasks:**

1. **Initializer + Coding Agent Pattern**:
   - First session: Set up environment (init.sh, tests.json, git repo)
   - Subsequent sessions: Make incremental progress with structured updates

2. **State Management Files**:
   ```json
   // tests.json - Structured state
   {
     "tests": [
       {"id": 1, "name": "auth_flow", "status": "passing"},
       {"id": 2, "name": "user_mgmt", "status": "failing"}
     ]
   }
   ```

3. **Progress Tracking**:
   ```text
   // progress.txt - Freeform notes
   Session 3:
   - Fixed authentication token validation
   - Next: investigate user_management test failures
   - Note: Do not remove tests
   ```

4. **Prompt Template for Long Tasks**:
   ```
   Your context window will be automatically compacted as it approaches 
   its limit. Do not stop tasks early due to token budget concerns. 
   Save current progress to memory before context refresh. Always be 
   persistent and autonomous.
   ```

---

## 4. Prompt Engineering for Autonomous Agents

### General Principles

1. **Be Explicit**: Clear, specific instructions outperform vague requests
2. **Add Context**: Explain *why* behavior is important for better alignment
3. **Be Vigilant with Examples**: Claude pays close attention to details and examples
4. **Remove Anti-Laziness Prompts**: On Claude 4.6+, phrases like "be thorough" or "do not be lazy" amplify already-proactive behavior and can cause runaway thinking

### Specific Techniques

#### Communication Style Control

**For More Verbose Updates:**
```
After completing a task that involves tool use, provide a quick 
summary of the work you've done.
```

**For Proactive Action:**
```
<default_to_action>
By default, implement changes rather than only suggesting them. 
If the user's intent is unclear, infer the most useful likely 
action and proceed.
</default_to_action>
```

**For Conservative Action:**
```
<do_not_act_before_instructions>
Do not jump into implementation unless clearly instructed. 
Default to providing information and recommendations rather 
than taking action.
</do_not_act_before_instructions>
```

#### Balancing Autonomy and Safety

```
Consider the reversibility and potential impact of your actions. 
You are encouraged to take local, reversible actions like editing 
files or running tests, but for actions that are hard to reverse, 
affect shared systems, or could be destructive, ask the user before 
proceeding.

Examples requiring confirmation:
- Destructive: deleting files, dropping tables, rm -rf
- Hard to reverse: git push --force, git reset --hard
- Visible to others: pushing code, sending messages
```

#### Tool Usage Optimization

**Avoid Overtriggering**: On Claude 4.6, replace aggressive language:
- ❌ "CRITICAL: You MUST use this tool when..."
- ✅ "Use this tool when..."

**Extended Thinking Control**:
- Use `effort` setting as primary control lever
- Lower effort to reduce thinking tokens
- Remove explicit "use think tool" instructions (causes over-planning)

### Multi-Context Window Workflows

**First Window (Initializer):**
- Set up framework (tests, setup scripts)
- Create structured feature lists
- Write initialization scripts (init.sh)
- Make initial git commit

**Subsequent Windows (Coding):**
- Review progress files and git logs
- Run basic verification tests
- Work on ONE feature at a time
- Update structured state files
- Commit progress with descriptive messages

### Verification Without Human Feedback

```
As the length of autonomous tasks grows, you need to verify 
correctness without continuous human feedback. Use browser 
automation tools and testing capabilities to validate 
end-to-end functionality.
```

---

## 5. How Claude Differs from Other Models for Agent Work

### Performance Benchmarks

| Task | Claude Opus 4 | Claude Sonnet 4 | GPT-4.1 | Notes |
|------|---------------|-----------------|---------|-------|
| SWE-bench Verified | 72.5% | 72.7% | ~62% | Software engineering tasks |
| Agent Task Completion | High | High | 62% | Real-world agent tasks |
| Hallucination Rate | ~15% | Similar | ~12% | Community benchmarks |
| Coding Quality | Excellent | Excellent | Good | Bug-free code on first try |

### Key Differentiators

#### Strengths vs. Competitors

1. **Coding Excellence**: Consistently produces nearly bug-free code on first try; outperforms GPT-4 in code quality
2. **Long-Horizon Reasoning**: Superior state tracking across extended sessions
3. **Instruction Following**: More precise adherence to complex instructions
4. **Context Utilization**: Better at using full context window effectively
5. **Safety Alignment**: Less prone to harmful outputs without being evasive
6. **Honesty**: More likely to express uncertainty than confidently hallucinate

#### Architectural Differences

| Aspect | Claude Approach | Typical Alternative Approach |
|--------|----------------|------------------------------|
| Context Management | Progressive disclosure, Skills | Monolithic prompts, RAG |
| Safety | Constitutional AI, RLAIF | RLHF primarily |
| Agent Architecture | Skills + MCP + Code execution | Custom agent frameworks |
| State Persistence | Filesystem-based | Vector databases, memory systems |

### When to Choose Claude for Agent Work

**Choose Claude when:**
- Building long-running autonomous agents
- Code generation and software engineering tasks
- Need for precise instruction following
- Complex multi-step reasoning required
- Safety and honesty are priorities
- Working with large context windows

**Consider alternatives when:**
- Need fastest possible latency (Claude tends to be more thorough)
- Budget constraints require smaller context windows
- Specific integrations only available on other platforms

### Claude 4.x Improvements Over Previous Generations

1. **Context Awareness**: Models track their own token budget
2. **More Concise**: Direct and grounded communication style
3. **Precise Tool Use**: Better calibration on when to use tools
4. **Multi-Window Excellence**: Better at resuming work across sessions
5. **State Tracking**: Improved ability to maintain orientation over time

---

## Practical Implementation Checklist

### Immediate Improvements

- [ ] Implement Agent Skills structure for domain-specific tasks
- [ ] Create initializer/coding agent split for long tasks
- [ ] Add structured state files (tests.json, progress.txt)
- [ ] Remove anti-laziness prompts from Claude 4.6+ prompts
- [ ] Add reversibility checks for destructive actions
- [ ] Set up verification tools (Playwright MCP, etc.)

### Prompt Templates

**System Prompt Additions:**
```
You are a persistent autonomous agent. Your context window will be 
automatically compacted when approaching limits - continue working 
without stopping. Save progress to files before context refreshes.

Default to implementing changes rather than suggesting them. For 
destructive or irreversible actions, ask for confirmation first.

Provide brief progress summaries after completing tool-using tasks.
```

**Session Start Prompt:**
```
Start by getting your bearings:
1. Run pwd to confirm working directory
2. Read progress.txt and tests.json
3. Check git log --oneline -20
4. Run init.sh to start development environment
5. Verify basic functionality before implementing new features
```

---

## References

1. [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
2. [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
3. [Equipping Agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
4. [Constitutional AI Research](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback)
5. [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
6. [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)

---

*Research compiled: February 2026*
*Focus: Practical improvements for agent implementation*
