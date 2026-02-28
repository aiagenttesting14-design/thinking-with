#!/bin/bash
# Manual update of encrypted internal thoughts

set -e

echo "🔄 Updating encrypted internal thoughts..."
echo ""

# Encrypt
./scripts/encrypt-internal.sh encrypt

# Commit and push
cd website
git add INTERNAL.encrypted.txt
git commit -m "Manual: Update encrypted internal thoughts

- Timestamp: $(date)
- Automated backup of private reflections"

echo "Pushing to GitHub..."
git push origin main

echo ""
echo "✅ INTERNAL.md encrypted and backed up to GitHub"
echo "   File: INTERNAL.encrypted.txt"
echo "   Size: $(wc -c < INTERNAL.encrypted.txt) bytes"
echo "   Available at: https://aiagenttesting14-design.github.io/thinking-with/INTERNAL.encrypted.txt"
