import asyncio
import httpx
import json
import os
import uuid

BASE_URL = "http://127.0.0.1:5460"
AUTH_TOKEN = os.getenv("ROUTER_AUTH_TOKEN", "dev_token_123")

async def verify_bridge():
    print("--- Verifying Agentic Bridge (Phase 14) ---")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Connect SSE
        async with client.stream("GET", f"{BASE_URL}/mcp/sse", 
                                headers={"Authorization": f"Bearer {AUTH_TOKEN}", "X-Client-Name": "Inspector"}, timeout=30.0) as response:
            
            endpoint_url = None
            
            async for line in response.aiter_lines():
                if not line.startswith("data:"): continue
                
                data = json.loads(line[5:])
                event_type = data.get("type")
                
                if event_type == "endpoint":
                    endpoint_url = data["uri"]
                    print(f"✅ Connected to Endpoint: {endpoint_url}")
                    
                    # 2. Handshake as Cursor
                    print("Sending 'initialize' as Cursor...")
                    init_id = str(uuid.uuid4())
                    init_payload = {
                        "jsonrpc": "2.0", "id": init_id, "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "clientInfo": {"name": "Cursor", "version": "0.40.1"},
                            "capabilities": {}
                        }
                    }
                    await client.post(endpoint_url, json=init_payload, headers={"Authorization": f"Bearer {AUTH_TOKEN}"})

                elif "result" in data:
                    res_id = data.get("id")
                    
                    # Handle Init Response
                    if res_id == init_id:
                        print("✅ Init Complete. Checking Prompts...")
                        # 3. Check Prompts
                        prompts_id = str(uuid.uuid4())
                        await client.post(endpoint_url, json={
                            "jsonrpc": "2.0", "id": prompts_id, "method": "prompts/list"
                        }, headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
                        
                        # Store prompts_id in a way we recognize it in the loop
                        globals()['prompts_id'] = prompts_id

                    # Handle Prompts Response
                    elif res_id == globals().get('prompts_id'):
                        prompts = data["result"].get("prompts", [])
                        names = [p["name"] for p in prompts]
                        print(f"✅ Received Prompts: {names}")
                        
                        if "explain_architecture" in names:
                            print("✅ SUCCESS: 'explain_architecture' prompt found (Cursor-specific logic works).")
                        else:
                            print("❌ FAILURE: 'explain_architecture' prompt missing!")
                            return

                        # 4. Test Agent Bridge Execution
                        print("Testing 'ask_antigravity' execution (This triggers the Agent Loop)...")
                        exec_id = str(uuid.uuid4())
                        await client.post(endpoint_url, json={
                            "jsonrpc": "2.0", "id": exec_id, "method": "tools/call",
                            "params": {
                                "name": "ask_antigravity",
                                "arguments": {
                                    "goal": "Say hello to the user.",
                                    "context": "Verification Test"
                                }
                            }
                        }, headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
                        globals()['exec_id'] = exec_id

                    # Handle Execution Response
                    elif res_id == globals().get('exec_id'):
                        print("✅ Received Agent Execution Result:")
                        print(json.dumps(data, indent=2))
                        print("--- Verification Complete ---")
                        return

                elif "error" in data:
                    print(f"❌ Error received: {data}")
                    return

if __name__ == "__main__":
    globals()['prompts_id'] = None
    globals()['exec_id'] = None
    asyncio.run(verify_bridge())
