
import requests
import json
import time

URL = "http://127.0.0.1:5460/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer ant1grav1ty_s3cr3t_t0k3n_42"
}

def force_healer():
    print("🧪 Starting Healer Verification Test...")
    print("🎯 Strategy: Trigger 3 parallel failures to hit the 2-strike limit immediately.")
    
    # We ask for something that will definitely cause failures
    # "read_file" on non-existent files is a good candidate
    payload = {
        "model": "agent:latest",
        "messages": [
            {"role": "user", "content": "I need you to check three files immediately. Read 'ghost_file_1.txt', 'ghost_file_2.txt', and 'ghost_file_3.txt'. Do it in parallel."}
        ],
        "stream": True 
    }
    
    print("🚀 Sending Request...")
    start_time = time.time()
    
    try:
        response = requests.post(URL, headers=HEADERS, json=payload, stream=True)
        response.raise_for_status()
        
        print("📨 Receiving Stream...")
        
        healer_seen = False
        full_content = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        # Check for System Status Events (Nexus Injection)
                        if data.get("type") == "system_status":
                            content = data.get("content", "")
                            print(f"\n🔔 [SYSTEM ALERT] {content}")
                            if "Healer" in content or "QwQ" in content:
                                healer_seen = True
                        
                        # Check for content
                        choice = data.get("choices", [{}])[0]
                        delta = choice.get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_content += content
                            print(content, end="", flush=True)
                            
                    except json.JSONDecodeError:
                        pass
                        
        print(f"\n\n⏱️ Total Time: {time.time() - start_time:.2f}s")
        
        if healer_seen:
            print("\n✅ SUCCESS: Healer Escalation was detected via System Alert!")
        else:
            print("\n❌ FAILURE: Healer was NOT detected.")
            print("(Note: It might be that the Agent didn't run tools in parallel, or didn't fail twice?)")

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    force_healer()
