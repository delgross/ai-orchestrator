import subprocess
import time
import os
import signal
import sys

PORTS = [5455, 5460]

def get_pids(port):
    try:
        cmd = f"lsof -ti :{port}"
        pid_str = subprocess.check_output(cmd, shell=True).decode().strip()
        if not pid_str: return []
        return [int(p) for p in pid_str.split('\n') if p]
    except subprocess.CalledProcessError:
        return []

def kill_port_exhaustively(port):
    print(f"Ensuring port {port} is free...")
    attempts = 0
    while attempts < 5:
        pids = get_pids(port)
        if not pids:
            print(f"Port {port} is free.")
            return True
        
        for pid in pids:
            print(f"Killing PID {pid} on port {port}")
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        
        time.sleep(1)
        attempts += 1
    
    # Final check
    if get_pids(port):
        print(f"ERROR: Could not free port {port}")
        return False
    return True

def start_services():
    # Load env vars from .env manually to be sure
    env = os.environ.copy()
    try:
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env[k] = v
    except Exception as e:
        print(f"Warning: could not parse .env: {e}")

    # Force correct token
    env["ROUTER_AUTH_TOKEN"] = "antigravity_router_token_2025"
    
    print("Starting Router...")
    subprocess.Popen([sys.executable, "-m", "uvicorn", "router.main:app", "--host", "127.0.0.1", "--port", "5455"], env=env, stdout=open("router.log", "w"), stderr=subprocess.STDOUT, cwd=os.getcwd())
    
    print("Starting Agent Runner...")
    subprocess.Popen([sys.executable, "-m", "uvicorn", "agent_runner.main:app", "--host", "127.0.0.1", "--port", "5460"], env=env, stdout=open("agent_runner.log", "w"), stderr=subprocess.STDOUT, cwd=os.getcwd())

if __name__ == "__main__":
    print("Stopping Services...")
    
    # Kill by name first
    subprocess.run("pkill -9 -f router.main", shell=True)
    subprocess.run("pkill -9 -f agent_runner.main", shell=True)
    
    # Kill by port
    for p in PORTS:
        if not kill_port_exhaustively(p):
            print("Aborting restart due to stuck ports.")
            sys.exit(1)
            
    time.sleep(2)
    start_services()
    print("Services Restarted. Giving them 10s to boot...")
    time.sleep(10)
    
    # Verify they are running
    for p in PORTS:
        pids = get_pids(p)
        if pids:
            print(f"Port {p} is active (PID {pids})")
        else:
            print(f"WARNING: Port {p} failed to start!")
