# OpenClaw Improvements and Best Practices Research

**Compiled:** February 19, 2026  
**Purpose:** Comprehensive guide for OpenClaw self-improvement covering advanced features, optimization, security, and community best practices.

---

## Table of Contents

1. [Core Architecture & Advanced Features](#1-core-architecture--advanced-features)
2. [Configuration Best Practices](#2-configuration-best-practices)
3. [Performance & Cost Optimization](#3-performance--cost-optimization)
4. [Security & Sandboxing](#4-security--sandboxing)
5. [Multi-Agent & Sub-Agent Orchestration](#5-multi-agent--sub-agent-orchestration)
6. [Memory Management](#6-memory-management)
7. [Skills, Plugins & Extensions](#7-skills-plugins--extensions)
8. [Automation Patterns](#8-automation-patterns)
9. [Deployment Strategies](#9-deployment-strategies)
10. [Community Resources](#10-community-resources)

---

## 1. Core Architecture & Advanced Features

### Multi-Agent Routing System
OpenClaw supports **fully isolated agents** with separate:
- Workspaces (files, AGENTS.md/SOUL.md/USER.md)
- State directories (`agentDir`) for auth profiles and model registry
- Session stores under `~/.openclaw/agents/<agentId>/sessions`
- Auth profiles (per-agent, not shared automatically)

**Key Insight:** Each agent is a "fully scoped brain" - this allows multiple people to share one Gateway while keeping AI "brains" and data separate.

### Thinking Levels / Reasoning Configuration

Adjustable reasoning depth via:
- **Config default:** `agents.defaults.thinkingDefault` (off | low | medium | high)
- **Per-message:** `/reasoning <level>` or `/think <level>`
- **Session override:** Persistent for that session only

**Best Practice:** Higher levels use more tokens but improve complex problem-solving. Use `low` for routine tasks, `high` for deep analysis.

**Important Note:** New sessions default to `off` unless configured globally. Set `agents.defaults.thinkingDefault: low` for reasoning-capable models to ensure consistent behavior.

### Model Failover System

Configure deliberate cascades for reliability:
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: [
          "anthropic/claude-sonnet-4-5",  // Same model, different key
          "openai/gpt-4o",                // Different provider
          "google/gemini-2.5-flash-preview"
        ]
      }
    }
  }
}
```

---

## 2. Configuration Best Practices

### Context Window Management

**Skill Quantity Impact:**
- Each skill adds 200-500 tokens to system prompts
- 10 skills ≈ 2,000-5,000 tokens consumed
- Less space left for actual dialogue

**Model-Specific Strategies:**

| Model Type | Context Window | Recommended Skills | Strategy |
|------------|---------------|-------------------|----------|
| Large (Claude) | 200K tokens | 10-20 common skills | Impact negligible |
| Medium (Local 13B-30B) | 8K-32K tokens | 5-10 essential skills | Balance functionality |
| Small (Local 7B) | 4K-8K tokens | 2-5 minimal skills | Prioritize critical only |

### Configuration Editing Methods

1. **Interactive wizard:** `openclaw onboard` or `openclaw configure`
2. **CLI one-liners:** `openclaw config set agents.defaults.heartbeat.every "2h"`
3. **Control UI:** http://127.0.0.1:18789 (Config tab)
4. **Direct edit:** `~/.openclaw/openclaw.json` (auto-reload)

### Validation & Safety

- OpenClaw **refuses to start** with invalid configs
- Run `openclaw doctor` to diagnose issues
- Run `openclaw doctor --fix` for automatic repairs
- Use `openclaw status` for health checks

### AGENTS.md & SOUL.md Best Practices

- **SOUL.md:** Root personality - add high-priority directives at the top
- **AGENTS.md:** Instructions for sub-agents
- **Keep SKILL.md files under ~500 lines** to prevent context bloat
- Use `references/` folder for detailed documentation
- Move non-essential content out of main skill files

---

## 3. Performance & Cost Optimization

### API Cost Reduction Strategies

**Reported Savings:**
- 50-95% cost reduction possible through smart routing
- Users achieving $5-10/day with zero rate limits
- 80-90% savings by balancing Claude Max subscription with Kimi K2.5 API overflow

**Key Techniques:**

1. **Model Scoping:** Match model capability to task complexity
   - Heavy/repetitive tasks → Cheaper models for sub-agents
   - Main agent → Higher-quality model for orchestration

2. **Subscription Strategy:**
   - Claude Max subscription + API overflow for rate limit protection
   - Local models for background tasks
   - OpenRouter for unified access with price optimization

3. **Concurrency Caps:** Prevent runaway costs with limits

4. **Output Token Reduction:**
   - Request unified diffs instead of complete files
   - 90% reduction possible (500-2000 tokens → 50-200 tokens)

### Rate Limit & Quota Management

**Understanding Provider Limits:**
- OAuth tokens (ChatGPT Plus) often have lower rate limits than direct API keys
- Set up fallback models to continue working when rate-limited
- Use `/usage` commands to monitor consumption:
  - `/usage full` - Shows estimated cost footer
  - `/usage tokens` - Shows tokens only

### Smart Model Manager Pattern

```json5
{
  agents: {
    defaults: {
      subagents: {
        model: "openai/gpt-4o-mini",  // Cheaper for sub-tasks
      }
    }
  }
}
```

**Cost Note:** Each sub-agent has its own context and token usage. Configure cheaper models for sub-agents to optimize costs.

---

## 4. Security & Sandboxing

### Core Security Principles

> "You cannot secure the reasoning layer; you must sandbox the execution layer. Assume the agent will eventually be tricked. Design systems where that doesn't matter."

**Treat OpenClaw as a new security principal** - a non-human identity that can take actions, touch data, and move across systems.

### Sandboxing Configuration

**Default Recommendation:** Enable sandboxing for non-main sessions

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",  // or "all" for maximum security
        docker: {
          enabled: true,
          readOnlyWorkspace: true
        }
      }
    }
  }
}
```

**Sandbox Modes:**
- `disabled` - No isolation (not recommended for production)
- `non-main` - Sandboxed sessions for groups (recommended default)
- `all` - All sessions sandboxed (maximum security)

### DM Policy Configuration

**Default: Pairing Mode** (most secure)
```json5
{
  channels: {
    telegram: {
      dmPolicy: "pairing",  // Requires explicit approval
      // allowlist - Only specific IDs
      // open - Any user (not recommended)
      // disabled - DMs blocked
    }
  }
}
```

**Security Checklist:**
- [ ] Enable sandboxing for agents touching untrusted input
- [ ] Use strict tool allowlists
- [ ] Keep secrets out of prompts (use env/config)
- [ ] Bind Gateway to localhost (127.0.0.1) only when possible
- [ ] Use `openclaw doctor` to surface risky DM policies
- [ ] Review skills before installation

### Network Security

**For Production:**
- Bind Gateway to specific interfaces, not 0.0.0.0
- Use `?token=...` authentication or `allowInsecureAuth: true` only in LAN
- Internet-connected gateways appear on Shodan - secure them properly
- Use Tailscale or VPN for remote access instead of public exposure

---

## 5. Multi-Agent & Sub-Agent Orchestration

### Sub-Agent Patterns

**Configuration:**
```json5
{
  agents: {
    defaults: {
      subagents: {
        enabled: true,
        allowSpawn: true,      // Allow spawning sub-agents
        maxDepth: 2,           // Prevent runaway spawning
        model: "cheaper-model" // Cost optimization
      }
    }
  }
}
```

**Orchestrator Pattern:**
```json5
{
  tools: {
    agentToAgent: {
      enabled: true,
      allow: ["researcher", "coder", "writer"]
    }
  }
}
```

### Best Practices for Sub-Agents

1. **Set cheaper models** for sub-agents, keep main agent on high-quality model
2. **Use configurable nesting depth** for orchestrator patterns (maxDepth: 2-3)
3. **Spawn background tasks** with `sessions_spawn` for independent work
4. **Track conversation chains** between agents to prevent infinite loops

### Inter-Agent Communication

**Methods:**
- Shared memory files (careful with collisions)
- Agent-to-agent tool calls
- Webhook delivery between agents
- Shared workspace directories (with appropriate locking)

### Session Management

**Types:**
- **Main session:** System events, heartbeat processing
- **Isolated session:** Dedicated agent turn with separate context
- **Background work:** Runs independently, reports back when done

---

## 6. Memory Management

### Memory Architecture

OpenClaw uses a **local-first, transparent** memory system:
- **Vector Search:** SQLite with sqlite-vec for semantic recall
- **Keyword Matching:** SQLite FTS5 for precision
- **Hybrid Search:** BM25 + vector (70/30 blend, 4x candidate pool)

**Storage:**
- `~/.openclaw/memory/` - Persistent storage
- Graceful degradation if vector extensions unavailable
- Smart syncing: File monitor triggers index updates immediately

### Search Backend Options

1. **SQLite + sqlite-vec** (default, local)
   - Pros: Privacy, no API costs, offline operation
   - Cons: ~1GB disk space, slower than cloud APIs

2. **QMD (Query Metadata Database)**
   - Higher accuracy with re-ranking
   - Trade-off: Takes a few seconds vs instant
   - Better for complex queries requiring semantic + keyword matching

### Optimization Strategies

**Hybrid Search Configuration:**
```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            enabled: true,
            vectorWeight: 0.7,
            textWeight: 0.3,
            candidateMultiplier: 4
          }
        },
        cache: {
          enabled: true  // Avoid re-embedding unchanged chunks
        }
      }
    }
  }
}
```

**Batch Processing:**
- Large memory files use batch processing with caching
- Embedding cache stored in `embedding_cache` table
- Reduces costs for large backfills

### Memory File Structure

**Best Practice Organization:**
```
~/.openclaw/workspace/
├── MEMORY.md          # Core facts, preferences
├── HEARTBEAT.md       # Scheduled task context
├── NOTES/
│   ├── 2026-02/
│   └── projects/
└── REFERENCES/        # External documentation
```

**Avoid:** Flat markdown files that collapse after 10+ days of use

---

## 7. Skills, Plugins & Extensions

### Skills Ecosystem

**Available Resources:**
- Official skills repository: `github.com/openclaw/skills`
- Community directory: `openclawskills.dev` (3000+ skills)
- Awesome list: `github.com/VoltAgent/awesome-openclaw-skills`
- LobeHub marketplace: `lobehub.com/skills`

### Skill Structure Best Practices

**File Organization:**
```
skills/my-skill/
├── SKILL.md           # Main definition (keep < 500 lines)
└── references/
    ├── api-docs.md
    └── examples.md
```

**Creating Effective Skills:**
1. Follow AgentSkills best practices
2. Keep core workflow in SKILL.md
3. Move details to `references/`
4. Validate structure using AgentSkills validator
5. Use specific constraints to prevent bloated files

### Plugins vs Skills

| Feature | Skills | Plugins |
|---------|--------|---------|
| Language | Markdown specs | TypeScript/JavaScript |
| Use Case | Natural language APIs | Deep Gateway extensions |
| Installation | Copy to `skills/` folder | NPM packages |
| Examples | Web search, API calls | Voice calls, custom protocols |

**Plugin Installation:**
```bash
# NPM specs only (registry-only)
# Configure under plugins.entries.<id>.config
# Restart Gateway after installation
```

### Per-Agent vs Shared Skills

- **Shared:** `~/.openclaw/skills/` - Available to all agents
- **Per-Agent:** `~/.openclaw/agents/<agentId>/workspace/skills/` - Agent-specific

---

## 8. Automation Patterns

### Cron Jobs

**Storage:** `~/.openclaw/cron/` (persists across restarts)

**Execution Contexts:**
1. **Main session:** System event → runs on next heartbeat
2. **Isolated:** Dedicated agent turn in `cron:<jobId>` session
3. **Webhook:** POST to external URL instead of chat delivery

**Schedule Format:** Standard cron `minute hour day month weekday`

**CLI Commands:**
```bash
openclaw cron list          # List all jobs
openclaw cron remove <name> # Remove a job
openclaw cron pause <name>  # Pause without removing
openclaw cron resume <name> # Resume paused job
```

**Best Practices:**
- Set `enabled: false` to disable without deleting
- Use webhook delivery for external integrations
- Request "wake now" vs "next heartbeat" for urgent jobs
- Be careful with scheduled tasks - costs can increase unexpectedly

### Webhooks

**Receiving Webhooks:**
```json5
{
  webhooks: {
    github: {
      path: "/webhook/github",
      command: "agent --message 'Process GitHub webhook: {payload}'"
    }
  }
}
```

**Sending Webhooks:**
Configure `delivery.mode: "webhook"` with `delivery.to: "<url>"`

### Hooks System

Event-driven automation triggered by:
- Session start/end
- Message received
- Tool execution
- Custom events

---

## 9. Deployment Strategies

### Local Development

**Quick Start:**
```bash
openclaw onboard  # Interactive setup wizard
openclaw gateway start
```

### Docker Deployment

**Production Considerations:**
- Use Docker secrets instead of environment variables
- Enable read-only workspace access for sandboxes
- Disable external network access for sandboxed tasks unless required
- Use `docker compose` for orchestration

**Security Hardening:**
```yaml
# docker-compose.yml additions
services:
  openclaw-gateway:
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
```

### Cloud Deployment Options

**DigitalOcean 1-Click:**
- Includes TLS via Let's Encrypt (even with IP addresses)
- Pre-hardened security configuration
- Caddy reverse proxy with automatic certificates

**VPS Setup (Hostinger, etc.):**
- Dedicated machine behind firewall recommended
- Doesn't work as well on shared VPS (firewall issues)
- Fresh install preferred

### Gateway Binding Options

| Mode | Use Case |
|------|----------|
| `127.0.0.1` | Local development only |
| `lan` | Home/office network (use with token auth) |
| `0.0.0.0` | Public deployment (requires additional security) |

**Warning:** `gateway.bind: lan` shows warning about insecure context. Use `?token=...` or `allowInsecureAuth: true` with caution.

---

## 10. Community Resources

### Official Resources

- **Documentation:** `docs.openclaw.ai`
- **GitHub:** `github.com/openclaw/openclaw`
- **Changelog:** Track latest features and fixes
- **Issues:** Active development with community feedback

### Community Sites

| Resource | URL | Description |
|----------|-----|-------------|
| CoClaw | `github.com/lansespirit/coclaw` | Community guides and troubleshooting |
| OpenClaw Skills | `openclawskills.dev` | 3000+ community skills |
| OpenClaw Directory | `openclawdir.com` | Skills, plugins, and jobs |
| DeepWiki | `deepwiki.com/openclaw` | Detailed technical documentation |

### Reddit Communities

- r/openclaw - Main community
- r/AI_Agents - General AI agent discussion
- r/AiForSmallBusiness - Business use cases

### Notable GitHub Issues & Discussions

**Active Feature Requests:**
- Auto-adaptive thinking level (`thinkingDefault: auto`)
- Nested sub-agent spawning ( Issue #17511)
- Cost-optimized LLM Gateway (Issue #9244)
- Memory optimization onboarding wizard (Discussion #6038)

**Security Improvements:**
- Default safety posture: sandbox & session isolation (Issue #7827)
- DX improvements for Windows/WSL2 onboarding (Issue #7122)
- Security warnings for misconfigured DM policies

### Cost Optimization Resources

- "Running OpenClaw Without Burning Money" (GitHub gist - digitalknk)
- OpenClaw API Cost Optimization Guide (zenvanriel.nl)
- Rate Limits & Quota Management Guide

### Notable Community Tools

- **Clawtick CLI:** Cloud-powered scheduling with reliable cron
- **TinyFish web agent:** Bot-protected site handling
- **AgentSkills validator:** Validate skill structure

---

## Quick Reference: Key Commands

```bash
# Setup & Configuration
openclaw onboard                    # Interactive setup
openclaw config wizard              # Config editor
openclaw doctor                     # Health check
openclaw doctor --fix               # Auto-repair issues

# Agent Management
openclaw agents add <name>          # Create new agent
openclaw agents list --bindings     # Show agents and routing

# Session & Status
openclaw status                     # Gateway status
openclaw session_status             # Current session info
/reasoning <level>                  # Set thinking level

# Cron Jobs
openclaw cron list                  # List scheduled jobs
openclaw cron pause <name>          # Pause a job

# Gateway Control
openclaw gateway start              # Start Gateway
openclaw gateway restart            # Restart Gateway
openclaw gateway stop               # Stop Gateway

# Skills
openclaw skills list                # List installed skills
openclaw skills install <name>      # Install a skill
```

---

## Summary: Top Recommendations

### Immediate Improvements

1. **Set thinking default** in config to ensure consistent reasoning
2. **Enable sandboxing** for non-main sessions
3. **Configure model fallbacks** for reliability
4. **Use cheaper models for sub-agents** to reduce costs
5. **Set up hybrid memory search** for better recall

### Configuration Priorities

1. **Security:** Sandboxing + DM pairing policy
2. **Cost:** Model routing + subscription strategy
3. **Performance:** Skill optimization + memory caching
4. **Reliability:** Fallback chains + webhook backups

### Long-Term Architecture

- Separate agents by concern (work, personal, coding)
- Use sub-agents for parallel task execution
- Implement cron jobs for proactive automation
- Maintain organized memory structure
- Regular security audits with `openclaw doctor`

---

*This research compiled from OpenClaw documentation, GitHub issues, community guides, and best practice articles. For the latest information, always refer to the official documentation at docs.openclaw.ai.*
