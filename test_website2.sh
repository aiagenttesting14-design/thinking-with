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
  # Follow redirects with -L
  http_status=$(curl -s -L -o /dev/null -w "%{http_code}" "$url")
  echo "HTTP Status: $http_status"
  
  if [ "$http_status" = "200" ]; then
    # Get page content and check for last updated
    content=$(curl -s -L "$url")
    last_updated=$(echo "$content" | grep -i "last updated" | head -1 | sed 's/<[^>]*>//g' | xargs)
    if [ -n "$last_updated" ]; then
      echo "Last updated: $last_updated"
    else
      echo "Last updated: NOT FOUND"
    fi
    
    # Check for obvious issues
    if echo "$content" | grep -qi "404\|not found\|error\|broken"; then
      echo "WARNING: Possible error content detected"
    fi
    
    # Check page title
    title=$(echo "$content" | grep -i "<title>" | head -1 | sed 's/<[^>]*>//g' | xargs)
    echo "Title: $title"
  else
    echo "ERROR: Page failed to load"
  fi
  echo "---"
done