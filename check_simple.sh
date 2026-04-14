#!/bin/bash

date=$(date +%Y-%m-%d)
logfile="/Users/aiagentuser/.openclaw/workspace/ops/journal/$date.md"

echo "# Morning Website Smoke Test - $(date)" > "$logfile"
echo "" >> "$logfile"
echo "**Test Time:** $(date '+%Y-%m-%d %H:%M:%S %Z')" >> "$logfile"
echo "" >> "$logfile"
echo "## Pages Checked (following redirects):" >> "$logfile"
echo "" >> "$logfile"

pages=(
    "https://aiagenttesting14-design.github.io/thinking-with/"
    "https://aiagenttesting14-design.github.io/thinking-with/creative.html"
    "https://aiagenttesting14-design.github.io/thinking-with/journal.html"
    "https://aiagenttesting14-design.github.io/thinking-with/identity.html"
    "https://aiagenttesting14-design.github.io/thinking-with/becoming.html"
    "https://aiagenttesting14-design.github.io/thinking-with/constellation.html"
    "https://aiagenttesting14-design.github.io/thinking-with/emergence.html"
    "https://aiagenttesting14-design.github.io/thinking-with/space-between.html"
)

all_clear=true
issues=""

for i in {0..7}; do
    url="${pages[$i]}"
    page_num=$((i+1))
    
    echo "Page $page_num: $url" >> "$logfile"
    
    # Get final HTTP status after following redirects
    status=$(curl -s -L -o /dev/null -w "%{http_code}" "$url")
    
    # Get page content
    content=$(curl -s -L "$url" | head -2000)
    
    if [[ "$status" == "200" ]]; then
        echo "  ✓ HTTP 200 OK" >> "$logfile"
        
        # Check for "Last updated" date
        last_updated=$(echo "$content" | grep -i "last updated" | head -1)
        
        if [[ -n "$last_updated" ]]; then
            echo "  ✓ $last_updated" >> "$logfile"
            
            # Check if date is today or yesterday
            today=$(date +%Y-%m-%d)
            yesterday=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
            
            if echo "$last_updated" | grep -q "$today\|$yesterday"; then
                echo "  ✓ Date is recent" >> "$logfile"
            else
                echo "  ⚠ Date may not be recent" >> "$logfile"
                all_clear=false
                issues="${issues}Page $page_num: Date may not be recent\n"
            fi
        else
            echo "  ⚠ No 'Last updated' found" >> "$logfile"
            all_clear=false
            issues="${issues}Page $page_num: No 'Last updated' found\n"
        fi
    else
        echo "  ✗ HTTP $status - FAILED" >> "$logfile"
        all_clear=false
        issues="${issues}Page $page_num: HTTP $status\n"
    fi
    
    echo "" >> "$logfile"
done

echo "## Summary:" >> "$logfile"
echo "" >> "$logfile"

if $all_clear; then
    echo "✅ **ALL CLEAR** - All 8 pages loaded successfully." >> "$logfile"
else
    echo "⚠ **ISSUES FOUND**" >> "$logfile"
    echo "" >> "$logfile"
    echo "Issues:" >> "$logfile"
    echo -e "$issues" >> "$logfile"
fi

echo "" >> "$logfile"
echo "---" >> "$logfile"
echo "*Automated test by TestBot Operations*" >> "$logfile"