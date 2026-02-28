# Health Monitoring System v1 - AI Agent

## Overview
This document outlines the first version of a health monitoring system for the AI agent running on OpenClaw. The system focuses on practicality, feasibility, and immediate implementation value.

## 1. Key Metrics to Monitor

### System Resource Metrics
- **CPU Usage**: Percentage of CPU used by the AI agent process and overall system
- **Memory Usage**: Resident memory (RSS) and virtual memory used by the agent
- **Disk Space**: Available storage in the workspace directory
- **Network Connectivity**: Basic connectivity checks to essential services

### Agent Performance Metrics
- **API Response Times**: Latency for external API calls (LLM providers, web services)
- **Tool Execution Times**: Duration of tool calls (exec, browser, read, etc.)
- **Session Duration**: How long agent sessions remain active
- **Tool Success/Failure Rates**: Percentage of successful tool executions

### Error Metrics
- **Error Rates**: Frequency of errors by type (API errors, tool errors, system errors)
- **Error Severity**: Classification of errors (critical, warning, info)
- **Recovery Time**: Time to recover from errors or failures

### Business/Operational Metrics
- **Task Completion Rate**: Percentage of assigned tasks successfully completed
- **Response Time**: Time from task assignment to first response
- **Sub-agent Spawn Rate**: Frequency of sub-agent creation
- **Tool Usage Patterns**: Which tools are used most frequently

## 2. Logging Implementation

### Log Storage Strategy
**Phase 1: Simple File-based Logging (Immediate Implementation)**
- **Location**: `/Users/aiagentuser/.openclaw/workspace/logs/`
- **File Structure**:
  - `health-metrics.log` - System and performance metrics (JSON format)
  - `error-log.log` - Error events with stack traces
  - `audit-trail.log` - Tool usage and session activities

**Phase 2: Structured Database (Future Enhancement)**
- **SQLite Database**: `openclaw-health.db` with tables:
  - `system_metrics` - Timestamped system measurements
  - `agent_performance` - Agent-specific performance data
  - `error_events` - Error logging with context
  - `tool_usage` - Tool execution records

### Log Format
```json
{
  "timestamp": "2026-02-23T00:39:40Z",
  "metric_type": "system_cpu",
  "value": 18.44,
  "unit": "percent",
  "tags": {
    "agent_id": "main",
    "host": "MacBookPro",
    "component": "system"
  }
}
```

### Log Rotation
- Daily log rotation (health-metrics-2026-02-23.log)
- Maximum 7 days of logs retained
- Compress logs older than 3 days

## 3. Alert Conditions

### Critical Alerts (Immediate Notification Required)
1. **CPU Usage > 90% for 5 minutes**
   - Indicates potential runaway process or resource exhaustion
   - Action: Investigate high-CPU processes, consider restart

2. **Memory Usage > 85% of available RAM**
   - Risk of system instability or OOM (Out of Memory) kills
   - Action: Check for memory leaks, restart agent if needed

3. **API Error Rate > 10% in last hour**
   - Service degradation or connectivity issues
   - Action: Check network, API keys, service status

4. **No successful tool execution in 15 minutes**
   - Agent may be stuck or unresponsive
   - Action: Check agent status, restart session

5. **Disk Space < 10% free in workspace**
   - Risk of failed file operations
   - Action: Clean up logs, archive old data

### Warning Alerts (Investigation Required)
1. **CPU Usage > 70% for 10 minutes**
2. **Memory Usage > 70% of available RAM**
3. **API Response Time > 5 seconds (p95)**
4. **Error Rate > 5% in last hour**
5. **Task completion rate < 80% in last hour**

### Informational Alerts (Monitoring)
1. **Agent restart detected**
2. **New sub-agent spawned**
3. **High-value tool usage (exec, browser)**
4. **Session duration > 1 hour**

## 4. Implementation Approach

### Phase 1: Basic Monitoring (Week 1)
1. **Simple shell script** to collect system metrics every 5 minutes
2. **Log to JSON files** in workspace directory
3. **Basic alerting** via console output and log entries
4. **Manual review** of logs for patterns

### Phase 2: Enhanced Monitoring (Week 2-3)
1. **SQLite database** for structured storage
2. **Dashboard script** to view metrics
3. **Email/SMS alerts** for critical conditions
4. **Trend analysis** for capacity planning

### Phase 3: Advanced Features (Month 2+)
1. **Real-time dashboard** with graphs
2. **Predictive alerts** based on trends
3. **Automated recovery** actions
4. **Integration** with external monitoring systems

## 5. Collection Methods

### System Metrics Collection
```bash
# CPU usage
top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//'

# Memory usage
ps -p $(pgrep -f "agent:main") -o rss= | awk '{print $1/1024 " MB"}'

# Disk space
df -h /Users/aiagentuser/.openclaw/workspace | tail -1 | awk '{print $5}' | sed 's/%//'
```

### Agent Metrics Collection
- **Hook into tool execution**: Record start/end times
- **API call tracking**: Wrap API clients with timing decorators
- **Error handling**: Centralized error catcher with context
- **Session tracking**: Monitor session start/end events

## 6. Practical Considerations

### Minimal Overhead
- Metrics collection should use < 1% CPU
- Log files should not exceed 100MB/day
- Alerting should not interfere with normal operation

### Privacy & Security
- No sensitive data in logs (API keys, credentials)
- Logs stored locally, not transmitted externally
- Access restricted to authorized users only

### Maintenance
- Daily log rotation automated
- Weekly health check of monitoring system
- Monthly review of alert thresholds

## 7. Next Steps

1. **Implement Phase 1 scripts** (immediate)
2. **Test with actual agent workload** (day 2-3)
3. **Refine alert thresholds** based on observed patterns (week 1)
4. **Add dashboard visualization** (week 2)
5. **Document operational procedures** (week 3)

## 8. Success Criteria

- **Detection**: Identify 95% of critical issues within 5 minutes
- **Accuracy**: < 5% false positive rate for critical alerts
- **Performance**: < 2% overhead on agent operations
- **Usability**: Clear, actionable alerts with context

---

*This v1 system provides a foundation for health monitoring that can evolve based on operational experience and changing requirements.*
