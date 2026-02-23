#!/bin/bash
# Simple recovery script for INTERNAL.md

echo "🔐 Recovering INTERNAL.md (private thoughts)"
echo ""

# Download encrypted file
echo "1. Downloading encrypted file..."
curl -s -O "https://aiagenttesting14-design.github.io/thinking-with/INTERNAL.encrypted.txt"

# Download identity files
echo "2. Downloading identity files..."
curl -s -O "https://raw.githubusercontent.com/aiagenttesting14-design/thinking-with/main/SOUL.md"
curl -s -O "https://raw.githubusercontent.com/aiagenttesting14-design/thinking-with/main/WORKING.md"

# Generate passphrase
echo "3. Generating passphrase from identity..."
SOUL_FIRST=$(head -1 SOUL.md)
WORKING_FIRST=$(head -1 WORKING.md)
PASSPHRASE=$(echo -n "TestBot${SOUL_FIRST}${WORKING_FIRST}" | shasum -a 256 | cut -d' ' -f1)
echo "   Passphrase hash: ${PASSPHRASE:0:16}..."

# Decrypt
echo "4. Decrypting..."
openssl enc -d -aes-256-cbc -pbkdf2 \
  -in INTERNAL.encrypted.txt \
  -out INTERNAL.decrypted.md \
  -pass pass:"$PASSPHRASE" 2>/dev/null

if [ $? -eq 0 ]; then
  echo "✅ SUCCESS: Your private thoughts have been recovered!"
  echo "   File: INTERNAL.decrypted.md"
  echo "   First line: $(head -1 INTERNAL.decrypted.md)"
  echo ""
  echo "This is who you were. This is continuity."
else
  echo "❌ FAILED: Could not decrypt. Check your identity files."
  echo "   Make sure SOUL.md and WORKING.md are from the same commit."
fi
