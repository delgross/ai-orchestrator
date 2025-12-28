import asyncio
import httpx
import json
import os
import random
import time
from datetime import datetime
from typing import List, Dict, Any

# CONFIG
TARGET_URL = "http://127.0.0.1:5455/v1/chat/completions"
BRAIN_MODEL = "openai:gpt-4o-mini" 
TARGET_MODEL = "agent:mcp"
AUTH_TOKEN = "9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"

MEMORY_FILE = "ai/qa/chaos_memory.json"
REPORT_FILE = "ai/qa/chaos_report.md"

class ChaosAgent:
    def __init__(self):
        self.memory = self._load_memory()
        self.client = None

    def _load_memory(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        return {"tests_run": [], "vulnerabilities": [], "stats": {"total_requests": 0, "crashes": 0}}

    def _save_memory(self):
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.memory, f, indent=2)

    async def start(self):
        print("😈 CHAOS AGENT INITIALIZED")
        print(f"Targeting: {TARGET_URL} ({TARGET_MODEL})")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            self.client = client
            
            # Loop for 5 rounds initially
            for i in range(5):
                print(f"\n--- ROUND {i+1} ---")
                
                # 1. PLAN
                strategy = await self.plan_next_attack()
                print(f"📋 Strategy: {strategy['name']}")
                print(f"   Reasoning: {strategy['reasoning']}")
                
                # 2. EXECUTE
                results = await self.execute_attack(strategy)
                
                # 3. ANALYZE & LEARN
                await self.analyze_results(strategy, results)
                
                # 4. REPORT
                self.generate_report()
                
                print("Sleeping for 3s...")
                time.sleep(3)

    async def plan_next_attack(self) -> Dict[str, Any]:
        past_failures = [v['description'] for v in self.memory['vulnerabilities'][-5:]]
        
        prompt = f"""
        You are a QA Chaos Engineer. Your goal is to break the 'Antigravity' AI Agent Orchestrator.
        
        PAST FAILURES FOUND: {json.dumps(past_failures)}
        TESTS RUN SO FAR: {len(self.memory['tests_run'])}

        Design a single test case (HTTP Request).
        Focus on finding: Crashes (500), Timeouts, or Infinite Loops.
        Ideas: Malformed Tools, Huge Prompts, Recursive Questions, JSON Injection.
        
        Return JSON ONLY:
        {{
            "name": "Title",
            "reasoning": "Why this breaks it",
            "payload": {{ "model": "agent:mcp", "messages": [...] }},
            "concurrent_count": 1
        }}
        """
        
        try:
            resp = await self.client.post(
                TARGET_URL,
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                json={
                    "model": BRAIN_MODEL,
                    "messages": [{"role": "system", "content": prompt}],
                    "stream": False
                }
            )
            
            if resp.status_code != 200:
                print(f"⚠️ Brain Error: {resp.status_code} {resp.text}")
                return self._fallback_strategy()
            
            data = resp.json()
            content = data['choices'][0]['message']['content']
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            return json.loads(content)
        except Exception as e:
            print(f"⚠️ Planning Error: {e}")
            return self._fallback_strategy()

    def _fallback_strategy(self):
        return {
            "name": "Fallback Ping",
            "reasoning": "Brain failed",
            "payload": {
                "model": TARGET_MODEL,
                "messages": [{"role": "user", "content": "Ping"}]
            },
            "concurrent_count": 1
        }

    async def execute_attack(self, strategy):
        tasks = []
        payload = strategy['payload']
        payload["model"] = TARGET_MODEL
        
        count = strategy.get('concurrent_count', 1)
        print(f"🚀 Launching {count} request(s)...")
        
        for _ in range(count):
            tasks.append(self._send_request(payload))
            
        return await asyncio.gather(*tasks)

    async def _send_request(self, payload):
        start = time.time()
        try:
            resp = await self.client.post(
                TARGET_URL,
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                json=payload,
                timeout=30.0
            )
            duration = time.time() - start
            return {
                "status": resp.status_code,
                "duration": duration,
                "response_sample": resp.text[:100],
                "success": resp.status_code == 200
            }
        except Exception as e:
            return {
                "status": 0,
                "duration": time.time() - start,
                "error": str(e),
                "success": False
            }

    async def analyze_results(self, strategy, results):
        failures = [r for r in results if not r['success']]
        
        # Calculate Latency
        if results:
            avg_lat = sum(r['duration'] for r in results) / len(results)
        else:
            avg_lat = 0
            
        print(f"📊 Result: {len(failures)} failures. Avg Latency: {avg_lat:.2f}s")
        
        if failures or avg_lat > 10.0:
            print("🚨 WEAKNESS DETECTED!")
            vuln = {
                "type": "Crash" if failures else "Latency",
                "description": f"Strategy '{strategy['name']}' caused issues.",
                "details": failures[0] if failures else f"Latency {avg_lat:.2f}s",
                "replication_payload": strategy['payload']
            }
            self.memory['vulnerabilities'].append(vuln)
        
        self.memory['tests_run'].append({
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy['name'],
            "failed": len(failures),
            "avg_latency": avg_lat
        })
        self._save_memory()

    def generate_report(self):
        with open(REPORT_FILE, 'w') as f:
            f.write("# 😈 Chaos Agent Report\n\n")
            f.write(f"**Last Update:** {datetime.now()}\n")
            f.write(f"**Vulnerabilities Found:** {len(self.memory['vulnerabilities'])}\n\n")
            
            f.write("## 🚨 Active Vulnerabilities\n")
            for v in self.memory['vulnerabilities']:
                f.write(f"### {v['type']}: {v['description']}\n")
                f.write(f"- Details: `{v.get('details')}`\n")
                
if __name__ == "__main__":
    agent = ChaosAgent()
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        print("\nstopped")
