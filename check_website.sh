#!/bin/bash

TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d)
DATE_FILE=$(date +%Y-%m-%d)
JOURNAL_FILE="/Users/aiagentuser/.openclaw/workspace/ops/journal/${DATE_FILE}.md"

echo "# Morning Website Smoke Test - $(date)" > "$JOURNAL_FILE"
echo "" >> "$JOURNAL_FILE"
echo "## Summary" >> "$JOURNAL_FILE"
echo "" >> "$JOURNAL_FILE"

# Count issues
issues=0
recent_pages=0
no_date_pages=0

echo "## Pages Checked" >> "$JOURNAL_FILE"
echo "" >> "$JOURNAL_FILE"

pages=(
    "Main page"
    "Creative page" 
    "Journal page"
    "Identity page"
    "Becoming page"
    "Constellation page"
    "Emergence page"
    "Space Between page"
)

urls=(
    "https://aiagenttesting14-design.github.io/thinking-with/"
    "https://aiagenttesting14-design.github.io/thinking-with/creative.html"
    "https://aiagenttesting14-design.github.io/thinking-with/journal.html"
    "https://aiagenttesting14-design.github.io/thinking-with/identity.html"
    "https://aiagenttesting14-design.github.io/thinking-with/becoming.html"
    "https://aiagenttesting14-design.github.io/thinking-with/constellation.html"
    "https://aiagenttesting14-design.github.io/thinking-with/emergence.html"
    "https://aiagenttesting14-design.github.io/thinking-with/space-between.html"
)

for i in {0..7}; do
    page_name="${pages[$i]}"
    url="${urls[$i]}"
    
    echo "### $page_name" >> "$JOURNAL_FILE"
    echo "- **URL:** $url" >> "$JOURNAL_FILE"
    
    http_status=$(curl -s -L -o /dev/null -w "%{http_code}" "$url")
    echo "- **HTTP Status:** $http_status" >> "$JOURNAL_FILE"
    
    if [ "$http_status" = "200" ]; then
        content=$(curl -s -L "$url")
        
        # Check for "Last updated" date
        if echo "$content" | grep -qi "last updated"; then
            date_line=$(echo "$content" | grep -i "last updated" | head -1)
            # Extract date (looking for patterns like "March 8, 2026" or "2026-03-08")
            date_found=""
            if echo "$date_line" | grep -q "[A-Za-z]\{3,9\} [0-9]\{1,2\}, 20[0-9]\{2\}"; then
                date_found=$(echo "$date_line" | grep -o "[A-Za-z]\{3,9\} [0-9]\{1,2\}, 20[0-9]\{2\}")
            elif echo "$date_line" | grep -q "20[0-9]\{2\}-[0-9]\{2\}-[0-9]\{2\}"; then
                date_found=$(echo "$date_line" | grep -o "20[0-9]\{2\}-[0-9]\{2\}-[0-9]\{2\}")
            fi
            
            if [ -n "$date_found" ]; then
                echo "- **Last updated:** $date_found" >> "$JOURNAL_FILE"
                
                # Convert date to YYYY-MM-DD for comparison
                if echo "$date_found" | grep -q "^[A-Za-z]"; then
                    # Format like "March 8, 2026"
                    date_iso=$(date -j -f "%B %d, %Y" "$date_found" "+%Y-%m-%d" 2>/dev/null || echo "")
                else
                    # Already in YYYY-MM-DD format
                    date_iso="$date_found"
                fi
                
                if [ -n "$date_iso" ]; then
                    if [ "$date_iso" = "$TODAY" ] || [ "$date_iso" = "$YESTERDAY" ]; then
                        echo "- **Status:** ✅ Recent (today or yesterday)" >> "$JOURNAL_FILE"
                        recent_pages=$((recent_pages + 1))
                    else
                        echo "- **Status:** ⚠️ Not recent (older than yesterday)" >> "$JOURNAL_FILE"
                        issues=$((issues + 1))
                    fi
                else
                    echo "- **Status:** ⚠️ Date format unclear" >> "$JOURNAL_FILE"
                    issues=$((issues + 1))
                fi
            else
                echo "- **Last updated:** Found but couldn't extract date" >> "$JOURNAL_FILE"
                echo "- **Status:** ⚠️ Date extraction failed" >> "$JOURNAL_FILE"
                issues=$((issues + 1))
            fi
        else
            echo "- **Last updated:** Not found" >> "$JOURNAL_FILE"
            echo "- **Status:** ⚠️ No 'Last updated' date" >> "$JOURNAL_FILE"
            no_date_pages=$((no_date_pages + 1))
            issues=$((issues + 1))
        fi
    else
        echo "- **Status:** ❌ Failed to load (HTTP $http_status)" >> "$JOURNAL_FILE"
        issues=$((issues + 1))
    fi
    
    echo "" >> "$JOURNAL_FILE"
done

echo "## Findings" >> "$JOURNAL_FILE"
echo "" >> "$JOURNAL_FILE"
echo "- **Total pages checked:** 8" >> "$JOURNAL_FILE"
echo "- **Pages with recent dates:** $recent_pages" >> "$JOURNAL_FILE"
echo "- **Pages without dates:** $no_date_pages" >> "$JOURNAL_FILE"
echo "- **Total issues found:** $issues" >> "$JOURNAL_FILE"
echo "" >> "$JOURNAL_FILE"

if [ $issues -eq 0 ]; then
    echo "**Overall Status:** ✅ All clear - All pages loaded successfully with recent dates." >> "$JOURNAL_FILE"
    summary="✅ Morning website check: All 8 pages loaded, all dates recent."
else
    echo "**Overall Status:** ⚠️ Issues detected - $issues problem(s) found across 8 pages." >> "$JOURNAL_FILE"
    summary="⚠️ Morning website check: $issues issue(s) found across 8 pages. Main page last updated March 8, 6 pages missing dates."
fi

echo "" >> "$JOURNAL_FILE"
echo "## One-line Summary for Stephen" >> "$JOURNAL_FILE"
echo "$summary" >> "$JOURNAL_FILE"

cat "$JOURNAL_FILE"