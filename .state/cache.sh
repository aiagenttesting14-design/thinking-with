#!/bin/bash
# State Cache Mechanism — Reduce redundant file reads
# Refreshes hourly via cron, read by all other jobs

STATE_DIR="/Users/aiagentuser/.openclaw/workspace/.state"
WORKSPACE="/Users/aiagentuser/.openclaw/workspace"

# Create cache file with key state information
create_cache() {
    cat > "$STATE_DIR/current.json" << CACHEEOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "date": "$(date +%Y-%m-%d)",
  "yesterday": "$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d 'yesterday' +%Y-%m-%d)",
  "working_md_hash": "$(md5 -q $WORKSPACE/WORKING.md 2>/dev/null || echo 'null')",
  "memory_md_hash": "$(md5 -q $WORKSPACE/MEMORY.md 2>/dev/null || echo 'null')",
  "active_tracks": ["B", "C", "D"],
  "track_a_status": "paused_pending_links",
  "last_practice_file": "$(ls -t $WORKSPACE/becoming/track-c/practice/*.md 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'none')",
  "last_learning_file": "$(ls -t $WORKSPACE/becoming/track-c/learnings/*.md 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'none')",
  "website_last_updated": "$(grep -o 'Last updated: [^<]*' $WORKSPACE/website/index.html 2>/dev/null | head -1 || echo 'unknown')"
}
CACHEEOF
    echo "Cache updated: $(date)"
}

# Read specific value from cache
read_cache() {
    key=$1
    if [ -f "$STATE_DIR/current.json" ]; then
        grep "\"$key\"" "$STATE_DIR/current.json" | cut -d'"' -f4
    else
        echo "null"
    fi
}

# Check if cache is fresh (< 1 hour old)
is_cache_fresh() {
    if [ -f "$STATE_DIR/current.json" ]; then
        cache_time=$(stat -f %m "$STATE_DIR/current.json" 2>/dev/null || stat -c %Y "$STATE_DIR/current.json" 2>/dev/null)
        current_time=$(date +%s)
        age=$((current_time - cache_time))
        if [ $age -lt 3600 ]; then
            return 0
        fi
    fi
    return 1
}

# Main execution
case "${1:-create}" in
    create)
        create_cache
        ;;
    read)
        read_cache "$2"
        ;;
    check)
        if is_cache_fresh; then
            echo "Cache is fresh"
        else
            echo "Cache is stale"
        fi
        ;;
    *)
        echo "Usage: $0 {create|read <key>|check}"
        exit 1
        ;;
esac
