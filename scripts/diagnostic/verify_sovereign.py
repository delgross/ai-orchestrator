
import sys
import os
import asyncio

# Ensure project root is in path
sys.path.append(os.getcwd())

from common.sovereign import get_sovereign_model, get_sovereign_port, get_sovereign_policy
from common.sovereign import SOVEREIGN_CONFIG

def main():
    print("=== Sovereign Registry Verification ===")
    
    # 1. Config Loading
    if not SOVEREIGN_CONFIG:
        print("❌ FAILED: SOVEREIGN_CONFIG is empty.")
        sys.exit(1)
    print("✅ SOVEREIGN_CONFIG loaded successfully.")
    
    # 2. Network Ports
    ports = {
        "router": get_sovereign_port("router"),
        "agent": get_sovereign_port("agent"),
        "rag": get_sovereign_port("rag"),
        "ollama": get_sovereign_port("ollama"),
        "surreal": get_sovereign_port("surreal")
    }
    
    print("\n[Network]")
    for k, v in ports.items():
        if v:
            print(f"  ✅ {k}: {v}")
        else:
            print(f"  ❌ {k}: MISSING")

    # 3. Models
    models = {
        "agent": get_sovereign_model("agent"),
        "router": get_sovereign_model("router"),
        "healer": get_sovereign_model("healer"),
        "summarizer": get_sovereign_model("summarizer"),
        "auditor": get_sovereign_model("auditor"),
        "cloud_vision": get_sovereign_model("cloud_vision"),
        "stt": get_sovereign_model("stt"),
    }

    print("\n[Models]")
    for k, v in models.items():
        if v:
            print(f"  ✅ {k}: {v}")
        else:
            print(f"  ❌ {k}: MISSING")

    # 4. Policies
    policies = {
        "internet": get_sovereign_policy("internet"),
        "safety": get_sovereign_policy("safety"),
    }
    print("\n[Policies]")
    for k, v in policies.items():
        if v:
            print(f"  ✅ {k}: {v}")
        else:
             print(f"  ❌ {k}: MISSING")

    # 5. Check Ingestor Logic (Static Check)
    # We can't run ingestor without full environment, but we can check if file exists
    from agent_runner.system_ingestor import SystemIngestor
    if hasattr(SystemIngestor, "ingest_registry"):
         print("\n✅ SystemIngestor.ingest_registry method exists.")
    else:
         print("\n❌ SystemIngestor.ingest_registry method MISSING.")
         
    # 6. Check Tool Logic
    from agent_runner.tools.registry_tool import tool_registry_manage
    if tool_registry_manage:
        print("✅ tool_registry_manage imported successfully.")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    main()
