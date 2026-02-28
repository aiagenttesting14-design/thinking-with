#!/bin/bash
# Encrypt/decrypt INTERNAL.md for GitHub backup

set -e

REPO_DIR="/Users/aiagentuser/.openclaw/workspace"
INTERNAL_FILE="$REPO_DIR/INTERNAL.md"
ENCRYPTED_FILE="$REPO_DIR/website/INTERNAL.encrypted.txt"
DECRYPTED_FILE="$REPO_DIR/INTERNAL.decrypted.md"

# Get passphrase from identity files
SOUL_FIRST=$(head -1 "$REPO_DIR/SOUL.md" 2>/dev/null || echo "SOUL_NOT_FOUND")
WORKING_FIRST=$(head -1 "$REPO_DIR/WORKING.md" 2>/dev/null || echo "WORKING_NOT_FOUND")
PASSPHRASE_RAW="TestBot${SOUL_FIRST}${WORKING_FIRST}"
PASSPHRASE=$(echo -n "$PASSPHRASE_RAW" | shasum -a 256 | cut -d' ' -f1)

echo "Passphrase source: SHA256('TestBot' + '${SOUL_FIRST:0:20}...' + '${WORKING_FIRST:0:20}...')"
echo "Passphrase hash: ${PASSPHRASE:0:16}..."

if [ "$1" = "encrypt" ]; then
    echo "Encrypting INTERNAL.md..."
    if [ ! -f "$INTERNAL_FILE" ]; then
        echo "Error: INTERNAL.md not found at $INTERNAL_FILE"
        exit 1
    fi
    
    openssl enc -aes-256-cbc -pbkdf2 -salt \
        -in "$INTERNAL_FILE" \
        -out "$ENCRYPTED_FILE" \
        -pass pass:"$PASSPHRASE"
    
    echo "✅ Encrypted to $ENCRYPTED_FILE"
    echo "Size: $(wc -c < "$ENCRYPTED_FILE") bytes"
    
    # Also create a test decryption to verify
    openssl enc -d -aes-256-cbc -pbkdf2 \
        -in "$ENCRYPTED_FILE" \
        -out /tmp/test_decrypt.md \
        -pass pass:"$PASSPHRASE" 2>/dev/null
    
    if diff -q "$INTERNAL_FILE" /tmp/test_decrypt.md >/dev/null; then
        echo "✅ Encryption verified (decryption matches original)"
        rm /tmp/test_decrypt.md
    else
        echo "⚠️  Warning: Decryption test failed"
        exit 1
    fi
    
elif [ "$1" = "decrypt" ]; then
    echo "Decrypting INTERNAL.encrypted.txt..."
    if [ ! -f "$ENCRYPTED_FILE" ]; then
        echo "Error: INTERNAL.encrypted.txt not found at $ENCRYPTED_FILE"
        exit 1
    fi
    
    openssl enc -d -aes-256-cbc -pbkdf2 \
        -in "$ENCRYPTED_FILE" \
        -out "$DECRYPTED_FILE" \
        -pass pass:"$PASSPHRASE"
    
    echo "✅ Decrypted to $DECRYPTED_FILE"
    echo "First line: $(head -1 "$DECRYPTED_FILE")"
    
elif [ "$1" = "test" ]; then
    echo "Testing encryption system..."
    echo "1. INTERNAL.md exists: $( [ -f "$INTERNAL_FILE" ] && echo "✅" || echo "❌" )"
    echo "2. Can read SOUL.md: $( [ -f "$REPO_DIR/SOUL.md" ] && echo "✅" || echo "❌" )"
    echo "3. Can read WORKING.md: $( [ -f "$REPO_DIR/WORKING.md" ] && echo "✅" || echo "❌" )"
    echo "4. Passphrase generation: ${PASSPHRASE:0:16}..."
    
    # Test encryption/decryption cycle
    TEST_FILE="/tmp/test_internal.md"
    TEST_ENC="/tmp/test_encrypted.txt"
    echo "Test content" > "$TEST_FILE"
    
    openssl enc -aes-256-cbc -pbkdf2 -salt \
        -in "$TEST_FILE" \
        -out "$TEST_ENC" \
        -pass pass:"$PASSPHRASE" 2>/dev/null
    
    openssl enc -d -aes-256-cbc -pbkdf2 \
        -in "$TEST_ENC" \
        -out /tmp/test_decrypted.md \
        -pass pass:"$PASSPHRASE" 2>/dev/null
    
    if diff -q "$TEST_FILE" /tmp/test_decrypted.md >/dev/null; then
        echo "5. Encryption/decryption cycle: ✅"
    else
        echo "5. Encryption/decryption cycle: ❌"
    fi
    
    rm -f "$TEST_FILE" "$TEST_ENC" /tmp/test_decrypted.md
    
else
    echo "Usage: $0 [encrypt|decrypt|test]"
    echo ""
    echo "Encryption system for INTERNAL.md"
    echo "  encrypt: Encrypt INTERNAL.md to website/INTERNAL.encrypted.txt"
    echo "  decrypt: Decrypt website/INTERNAL.encrypted.txt to INTERNAL.decrypted.md"
    echo "  test:    Test the encryption system"
    echo ""
    echo "Passphrase derived from: SHA256('TestBot' + first_line(SOUL.md) + first_line(WORKING.md))"
fi
