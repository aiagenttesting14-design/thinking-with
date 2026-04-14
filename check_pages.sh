#!/bin/bash
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d)
echo "Morning Website Smoke Test - $(date)"
echo "======================================"
echo ""

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

names=(
  "Main/Index"
  "Creative"
  "Journal"
  "Identity"
  "Becoming"
  "Constellation"
  "Emergence"
  "Space Between"
)

issues=0
for i in "${!pages[@]}"; do
  url="${pages[$i]}"
  name="${names[$i]}"
  
  echo "Page $((i+1)): $name"
  echo "URL: $url"
  
  # Check HTTP status
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$status" = "200" ]; then
    echo "✓ HTTP Status: 200 OK"
  else
    echo "✗ HTTP Status: $status"
    ((issues++))
  fi
  
  # Fetch page and check for "Last updated"
  content=$(curl -s "$url")
  last_updated=$(echo "$content" | grep -i "last updated" | head -1)
  
  if [ -n "$last_updated" ]; then
    echo "✓ Found: $last_updated"
    
    # Check if date is today or yesterday
    if echo "$last_updated" | grep -q "March 6, 2026" || echo "$last_updated" | grep -q "March 7, 2026"; then
      echo "✓ Date is recent (March 6-7, 2026)"
    else
      echo "⚠ Date may be older than yesterday"
      ((issues++))
    fi
  else
    echo "⚠ No 'Last updated' found"
    ((issues++))
  fi
  
  # Quick check for obvious issues
  if echo "$content" | grep -q "404\|not found\|error\|broken"; then
    echo "⚠ Possible content issues detected"
    ((issues++))
  fi
  
  echo ""
done

echo "======================================"
echo "Summary: Checked ${#pages[@]} pages"
echo "Issues found: $issues"
