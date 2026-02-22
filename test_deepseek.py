#!/usr/bin/env python3
import os
import json
import requests
import sys

# Read the OpenClaw config to get DeepSeek API key
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r') as f:
    config = json.load(f)

# Get DeepSeek API key
api_key = config['models']['providers']['deepseek']['apiKey']
base_url = config['models']['providers']['deepseek']['baseUrl']

print(f"Testing DeepSeek API...")
print(f"Base URL: {base_url}")
print(f"API Key: {api_key[:10]}...")

# Make a simple test request
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "Hello! Please respond with a short test message to confirm the API is working."}
    ],
    "max_tokens": 50,
    "temperature": 0.7
}

try:
    response = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    
    result = response.json()
    print("\n✅ DeepSeek API test successful!")
    print(f"Response: {result['choices'][0]['message']['content']}")
    print(f"Model: {result.get('model', 'N/A')}")
    print(f"Usage: {result.get('usage', {})}")
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ DeepSeek API test failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)

print("\n🎉 DeepSeek model functionality test completed successfully!")
