import os
import sys
import time
import subprocess
import plistlib
from pathlib import Path

# Constants
HOME = Path.home()
# We get the user ID dynamically
DOMAIN = f"gui/{os.getuid()}"
LAUNCH_AGENTS = HOME / "Library/LaunchAgents"

ROUTER_PLIST = LAUNCH_AGENTS / "local.ai.router.plist"
AGENT_PLIST = LAUNCH_AGENTS / "local.ai.agent_runner.plist"

# RELATIVE PATH FIX:
# We determine the project root based on where THIS script is running from.
# refactor_wrappers.py is in .../ai/
# scripts are in .../ai/bin/
PROJECT_ROOT = Path(__file__).resolve().parent
ROUTER_WRAPPER = PROJECT_ROOT / "bin/run_router.sh"
AGENT_WRAPPER = PROJECT_ROOT / "bin/run_agent_runner.sh"

def run_cmd(cmd, check=True):
    """Helper to run shell commands with logging"""
    print(f"Exec: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=check)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if check:
            sys.exit(1)

def patch_plist(plist_path: Path, script_path: Path):
    """Reads a plist, updates the ProgramArguments, and saves it."""
    if not plist_path.exists():
        print(f"Skipping missing plist: {plist_path}")
        return
    
    print(f"Patching {plist_path.name}...")
    try:
        with open(plist_path, 'rb') as f:
            data = plistlib.load(f)
        
        # KEY CHANGE: Updating the arguments list
        data["ProgramArguments"] = ["/bin/bash", str(script_path)]
        
        with open(plist_path, 'wb') as f:
            plistlib.dump(data, f)
            
    except Exception as e:
        print(f"Failed to patch plist: {e}")
        sys.exit(1)

def main():
    print("--- Starting Python Refactor Script ---")

    # 1. Validation
    # In bash this was: [ -x "$RS" ] || exit 1
    for wrapper in [ROUTER_WRAPPER, AGENT_WRAPPER]:
        if not wrapper.exists():
            print(f"Error: Wrapper not found: {wrapper}")
            sys.exit(1)
        if not os.access(wrapper, os.X_OK):
            print(f"Error: Wrapper not executable: {wrapper}")
            sys.exit(1)

    # 2. Patch logic
    patch_plist(ROUTER_PLIST, ROUTER_WRAPPER)
    patch_plist(AGENT_PLIST, AGENT_WRAPPER)

    # 3. Linting (calling system tools)
    run_cmd(["plutil", "-lint", str(ROUTER_PLIST)], check=False)
    run_cmd(["plutil", "-lint", str(AGENT_PLIST)], check=False)

    # 4. Stop Services
    print("Stopping services (ignore errors)...")
    run_cmd(["launchctl", "bootout", DOMAIN, str(ROUTER_PLIST)], check=False)
    run_cmd(["launchctl", "bootout", DOMAIN, str(AGENT_PLIST)], check=False)

    # 5. Kill Ports
    # subprocess.run with shell=True allows using pipes like |
    print("Ensuring ports are free...")
    subprocess.run("lsof -ti tcp:5455 | xargs -r kill -9", shell=True)
    subprocess.run("lsof -ti tcp:5460 | xargs -r kill -9", shell=True)
    time.sleep(1)

    # 6. Start Services
    print("Starting services...")
    run_cmd(["launchctl", "bootstrap", DOMAIN, str(ROUTER_PLIST)])
    run_cmd(["launchctl", "bootstrap", DOMAIN, str(AGENT_PLIST)])
    
    run_cmd(["launchctl", "kickstart", "-k", f"{DOMAIN}/local.ai.router"])
    run_cmd(["launchctl", "kickstart", "-k", f"{DOMAIN}/local.ai.agent_runner"])

    print("--- Done! ---")

if __name__ == "__main__":
    main()
