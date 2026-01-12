import subprocess
import json
import os
import sys

cmd = ["npx", "-y", "sonos-ts-mcp@latest"]
env = os.environ.copy()

print(f"Starting {cmd}")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

def send(data):
    s = json.dumps(data)
    # print(f"-> {s}")
    proc.stdin.write(s + "\n")
    proc.stdin.flush()

# 1. Initialize
send({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "debugger", "version": "1.0"}
    }
})

# Read loop
while True:
    line = proc.stdout.readline()
    if not line:
        break
    # print(f"<- {line.strip()}")
    try:
        msg = json.loads(line)
        if msg.get("result") and "protocolVersion" in msg["result"]:
            # Initialized. Now send initialized notification + tools/list
            send({
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            send({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            })
        
        elif msg.get("id") == 2:
            # Tool list
            tools = msg.get("result", {}).get("tools", [])
            print(f"Got {len(tools)} tools.")
            names = [t['name'] for t in tools]
            
            # Check for duplicates
            from collections import Counter
            c = Counter(names)
            dupes = [n for n, count in c.items() if count > 1]
            if dupes:
                print(f"DUPLICATES FOUND IN SERVER RESPONSE: {dupes}")
            else:
                print("NO DUPLICATES in server response.")
                
            print(f"Sample names: {names[:5]}")
            break
    except Exception as e:
        pass

proc.terminate()
