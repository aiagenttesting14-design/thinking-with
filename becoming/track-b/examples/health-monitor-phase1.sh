#!/bin/bash

# Health Monitoring System - Phase 1 Example
# Simple script to collect basic system metrics for AI agent

LOG_DIR="/Users/aiagentuser/.openclaw/workspace/logs"
METRICS_LOG="$LOG_DIR/health-metrics.log"
ERROR_LOG="$LOG_DIR/error-log.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to get current timestamp in ISO format
get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Function to log metrics in JSON format
log_metric() {
    local metric_type=$1
    local value=$2
    local unit=$3
    local tags=$4
    
    local timestamp=$(get_timestamp)
    
    cat >> "$METRICS_LOG" << METRIC_ENTRY
{
  "timestamp": "$timestamp",
  "metric_type": "$metric_type",
  "value": $value,
  "unit": "$unit",
  "tags": $tags
}
METRIC_ENTRY
}

# Function to log errors
log_error() {
    local error_type=$1
    local message=$2
    local context=$3
    
    local timestamp=$(get_timestamp)
    
    cat >> "$ERROR_LOG" << ERROR_ENTRY
{
  "timestamp": "$timestamp",
  "error_type": "$error_type",
  "message": "$message",
  "context": "$context",
  "severity": "warning"
}
ERROR_ENTRY
}

# Function to check CPU usage
check_cpu() {
    local cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    local tags='{"component": "system", "host": "MacBookPro"}'
    
    log_metric "system_cpu" "$cpu_usage" "percent" "$tags"
    
    # Check alert condition
    if (( $(echo "$cpu_usage > 90" | bc -l) )); then
        log_error "high_cpu" "CPU usage exceeded 90%" "{\"cpu_usage\": $cpu_usage}"
        echo "ALERT: High CPU usage detected: ${cpu_usage}%"
    elif (( $(echo "$cpu_usage > 70" | bc -l) )); then
        echo "WARNING: Elevated CPU usage: ${cpu_usage}%"
    fi
}

# Function to check memory usage
check_memory() {
    # Get agent process ID (simplified example)
    local agent_pid=$(pgrep -f "agent:main" 2>/dev/null | head -1)
    
    if [ -n "$agent_pid" ]; then
        local memory_mb=$(ps -p "$agent_pid" -o rss= | awk '{print $1/1024}')
        local tags="{\"component\": \"agent\", \"pid\": $agent_pid, \"host\": \"MacBookPro\"}"
        
        log_metric "agent_memory" "$memory_mb" "MB" "$tags"
        
        # Check alert condition (simplified - would need total RAM for percentage)
        if (( $(echo "$memory_mb > 1000" | bc -l) )); then
            echo "WARNING: Agent using ${memory_mb} MB of memory"
        fi
    else
        log_error "agent_not_found" "Could not find agent process" "{\"check\": \"memory\"}"
    fi
}

# Function to check disk space
check_disk() {
    local disk_usage=$(df -h /Users/aiagentuser/.openclaw/workspace | tail -1 | awk '{print $5}' | sed 's/%//')
    local tags='{"component": "storage", "mount_point": "/Users/aiagentuser/.openclaw/workspace"}'
    
    log_metric "disk_usage" "$disk_usage" "percent" "$tags"
    
    # Check alert condition
    if (( disk_usage > 90 )); then
        log_error "low_disk_space" "Disk usage exceeded 90%" "{\"disk_usage\": $disk_usage}"
        echo "ALERT: Low disk space: ${disk_usage}% used"
    elif (( disk_usage > 70 )); then
        echo "WARNING: Elevated disk usage: ${disk_usage}%"
    fi
}

# Function to check if agent is responsive
check_agent_health() {
    # Simplified check - in reality would check agent API or heartbeat
    local last_log=$(find "$LOG_DIR" -name "*.log" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
    
    if [ -n "$last_log" ]; then
        local last_modified=$(stat -f "%m" "$last_log")
        local now=$(date +%s)
        local minutes_since=$(( (now - last_modified) / 60 ))
        
        if (( minutes_since > 15 )); then
            log_error "agent_unresponsive" "No activity detected in $minutes_since minutes" "{\"last_log\": \"$last_log\"}"
            echo "ALERT: No agent activity detected for ${minutes_since} minutes"
        fi
    fi
}

# Main monitoring function
run_monitoring() {
    echo "Starting health monitoring check at $(date)"
    
    check_cpu
    check_memory
    check_disk
    check_agent_health
    
    echo "Health monitoring check completed at $(date)"
    echo "Metrics logged to: $METRICS_LOG"
    echo "Errors logged to: $ERROR_LOG"
    echo ""
}

# Run monitoring
run_monitoring

# Example of how to run this periodically:
# while true; do ./health-monitor-phase1.sh; sleep 300; done
