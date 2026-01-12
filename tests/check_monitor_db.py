
import asyncio
import json
import httpx

async def check():
    url = "http://localhost:8000/sql"
    headers = {"NS": "orchestrator", "DB": "memory", "Accept": "application/json"}
    auth = ("root", "root")
    
    q = "USE NS orchestrator DB memory; SELECT * FROM system_state WHERE item = 'dashboard_monitor'"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=q, headers=headers, auth=auth)
            print(f"Status: {resp.status_code}")
            print(f"Raw Text: {resp.text}")
            data = resp.json()
            print(f"Parsed JSON: {data}")
            if data and isinstance(data, list) and data[0].get('result'):
                record = data[0]['result'][0]
                print(f"DEBUG Record: {record}")
                details = record.get('details', {})
                if isinstance(details, str):
                    print("⚠️ 'details' is a string, parsing...")
                    details = json.loads(details)
                
                ts = details.get('timestamp', 0)
                import time
                age = time.time() - ts
                print(f"✅ Monitor Record Found!")
                print(f"   Timestamp: {ts}")
                print(f"   Age: {age:.2f}s")
                print(f"   Latency in DB: {details.get('latency')}")
                print(f"   RAG Online: {details.get('rag_online')}")
            else:
                print("❌ No monitor record found.")
                print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
