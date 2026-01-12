#!/usr/bin/env python3
import sys
import os
import yaml

def get_value(data, path):
    """Deep get using dot notation."""
    keys = path.split('.')
    val = data
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return None
    return val

def main():
    if len(sys.argv) < 2:
        print("Usage: get_config.py <key> [default]")
        sys.exit(1)

    key = sys.argv[1]
    default = sys.argv[2] if len(sys.argv) > 2 else ""

    # Locate sovereign.yaml
    # Assuming bin/get_config.py -> parent -> config/sovereign.yaml
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "sovereign.yaml")

    data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            pass # Fail silently to default

    val = get_value(data, key)
    
    if val is None:
        print(default)
    else:
        print(val)

if __name__ == "__main__":
    main()
