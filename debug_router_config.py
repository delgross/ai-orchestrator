
import os
import sys

# Add current dir to path so we can import router
sys.path.append(os.getcwd())

from router.config import OLLAMA_BASE, SOV_CONFIG

print(f"DEBUG: OLLAMA_BASE='{OLLAMA_BASE}'")
print(f"DEBUG: SOV_CONFIG keys={list(SOV_CONFIG.keys())}")
