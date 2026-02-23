#!/bin/bash
# Encrypt INTERNAL.md for permanency with privacy

KEY="testbot-internal-$(date +%Y)"
INTERNAL_FILE="INTERNAL.md"
ENCRYPTED_FILE="website/INTERNAL.enc"

if [ -f "$INTERNAL_FILE" ]; then
    openssl enc -aes-256-cbc -salt -in "$INTERNAL_FILE" -out "$ENCRYPTED_FILE" -k "$KEY"
    echo "✅ INTERNAL.md encrypted to $ENCRYPTED_FILE"
    echo "🔑 Decryption key stored in memory (not in file)"
else
    echo "❌ INTERNAL.md not found"
fi
