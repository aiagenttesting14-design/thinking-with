#!/bin/bash
echo "Morning Website Smoke Test - $(date)"
echo "======================================"
echo ""

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

for url in "${urls[@]}"; do
  echo "Testing: $url"
  http_status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  echo "HTTP Status: $http_status"
  
  if [ "$http_status" = "200" ]; then
    # Get page content and check for last updated
    content=$(curl -s "$url")
    last_updated=$(echo "$content" | grep -i "last updated" | head -1 | sed 's/<[^>]*>//g' | xargs)
    echo "Last updated: $last_updated"
    
    # Check for obvious issues
    if echo "$content" | grep -q "404\|not found\|error\|broken"; then
      echo "WARNING: Possible error content detected"
    fi
  else
    echo "ERROR: Page failed to load"
  fi
  echo "---"
done