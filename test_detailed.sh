#!/bin/bash
echo "Detailed Website Smoke Test - $(date)"
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
    # Get page content
    content=$(curl -s -L "$url")
    
    # Check for last updated - look for various patterns
    last_updated=$(echo "$content" | grep -i "last updated\|updated.*2026\|updated.*march" | head -1)
    if [ -n "$last_updated" ]; then
      echo "Last updated found: $last_updated" | head -c 100
    else
      echo "Last updated: NOT FOUND"
    fi
    
    # Check page title
    title=$(echo "$content" | grep -i "<title>" | head -1 | sed 's/.*<title>//;s/<\/title>.*//' | xargs)
    echo "Title: $title"
    
    # Check for broken elements
    if echo "$content" | grep -qi "404\|not found\|error\|broken\|failed"; then
      echo "WARNING: Possible error content detected"
    fi
    
    # Check if page has reasonable content length
    content_length=$(echo "$content" | wc -c)
    if [ "$content_length" -lt 1000 ]; then
      echo "WARNING: Page content seems very short ($content_length bytes)"
    fi
  else
    echo "ERROR: Page failed to load"
  fi
  echo "---"
done