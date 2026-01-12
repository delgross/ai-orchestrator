#!/usr/bin/env python3
import argparse
import yaml
import requests
import sys
import os
from pathlib import Path

# Constants
ADMIN_URL = "http://localhost:5460/admin/admin/config/models"
CONFIG_FILE = Path(__file__).parent.parent / "config" / "model_presets.yaml"

def load_presets():
    if not CONFIG_FILE.exists():
        print(f"Error: Config file not found at {CONFIG_FILE}")
        sys.exit(1)
    
    with open(CONFIG_FILE, "r") as f:
        try:
            data = yaml.safe_load(f)
            return data.get("presets", {})
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            sys.exit(1)

def apply_preset(preset_name):
    presets = load_presets()
    
    if preset_name not in presets:
        print(f"Error: Preset '{preset_name}' not found.")
        print("Available presets:")
        for k, v in presets.items():
            print(f"  - {k}: {v.get('description', 'No description')}")
        sys.exit(1)
        
    preset = presets[preset_name]
    models = preset.get("models", {})
    
    print(f"Applying preset: {preset_name}")
    print(f"Description: {preset.get('description')}")
    print("--------------------------------")
    for role, model in models.items():
        print(f"  {role:<20} -> {model}")
    print("--------------------------------")
    
    confirm = input("Apply these changes? [y/N] ")
    if confirm.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    try:
        resp = requests.post(ADMIN_URL, json=models)
        if resp.status_code == 200:
            print("\n✅ Success! Models updated.")
            data = resp.json()
            if "models" in data:
               print("New Configuration:")
               # Print returned state to verify
               current = data["models"]
               for k, v in current.items():
                   status = " "
                   if k in models and models[k] == v:
                       status = "✓"
                   print(f" {status} {k:<20}: {v}")
        else:
            print(f"\n❌ Failed: {resp.status_code} - {resp.text}")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to Agent Runner at {ADMIN_URL}")
        print("Is the system running?")
        sys.exit(1)

def list_presets():
    presets = load_presets()
    print("Available Presets:")
    for k, v in presets.items():
        print(f"- {k}: {v.get('description', 'No description')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Switch AI System Model Presets")
    parser.add_argument("preset", nargs="?", help="Name of the preset to apply")
    parser.add_argument("--list", action="store_true", help="List available presets")
    
    args = parser.parse_args()
    
    if args.list:
        list_presets()
    elif args.preset:
        apply_preset(args.preset)
    else:
        parser.print_help()
