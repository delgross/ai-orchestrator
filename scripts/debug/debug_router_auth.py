#!/usr/bin/env python3
"""Check router authentication configuration"""
import sys
import os

# Simulate router loading
sys.path.insert(0, '/Users/bee/Sync/Antigravity/ai')

# Load env
from dotenv import load_dotenv
load_dotenv("providers.env")
load_dotenv()
load_dotenv("router.env")

# Check what gets loaded
print("=== Router Auth Debug ===\n")
print(f"1. ROUTER_AUTH_TOKEN from env: {os.getenv('ROUTER_AUTH_TOKEN')}")
print(f"2. pytest in sys.modules: {'pytest' in sys.modules}")
print(f"3. PYTEST_CURRENT_TEST: {os.getenv('PYTEST_CURRENT_TEST')}")

# Import router config
from router import config

print(f"\n4. config.ROUTER_AUTH_TOKEN value: '{config.ROUTER_AUTH_TOKEN}'")
print(f"5. Length: {len(config.ROUTER_AUTH_TOKEN)}")
print(f"6. Is empty: {not config.ROUTER_AUTH_TOKEN}")

# Check if pytest gets imported somewhere
print(f"\n7. All pytest-related modules in sys.modules:")
for mod in sys.modules:
    if 'pytest' in mod.lower():
        print(f"   - {mod}")
