"""
Example Cloud Trigger Script
----------------------------
This file demonstrates how the Local Orchestrator (running on your Mac)
connects to the Remote Cloud Brain (running on H100 GPU) to execute a task.

Usage:
    This function would be called by the TaskScheduler at 8:00 AM.
"""

import modal
import asyncio
from typing import Dict, Any

# 1. Define the connection to the deployed App
APP_NAME = "antigravity-night-shift"
CLASS_NAME = "CloudIntelligence"

async def trigger_briefing_task(local_context: str = "No news today.") -> Dict[str, Any]:
    """
    Connects to the cloud, wakes up the 140GB model, and asks for a briefing.
    """
    print(f"📡 Networking: Connecting to {APP_NAME}::{CLASS_NAME}...")

    # 2. Lookup the Class (Does not instantiate yet)
    try:
        CloudBrain = modal.Cls.from_name(APP_NAME, CLASS_NAME)
    except Exception as e:
        return {"status": "error", "message": f"Could not find cloud app: {e}"}

    # 3. Instantiate (Wakes up the Snapshot)
    # This is where the 5-second 'Cold Start' happens.
    print("⚡️ Waking up Cloud Snapshot...")
    brain = CloudBrain()

    # 4. Execute Remote Method
    # We use await asyncio.to_thread because .remote() is blocking in standard Modal
    print("🧠 Thinking (Cloud Inference)...")
    
    # The Prompt for the Model
    prompt = f"""
    You are an Executive Assistant. 
    Review the following local context and provide a briefing:
    
    {local_context}
    """

    try:
        # .remote() sends the data to the H100 and waits for the answer
        response = await asyncio.to_thread(
            brain.cloud_heavy_reasoning.remote, 
            context_text=local_context,
            query="Summarize this for me."
        )
        
        result_text = response.get("result", "No result returned.")
        print(f"✅ Result Received ({len(result_text)} chars).")
        
        return {
            "status": "success",
            "model_used": response.get("model"),
            "briefing": result_text
        }

    except Exception as e:
        print(f"❌ Cloud execution failed: {e}")
        return {"status": "error", "message": str(e)}

# For testing manually from terminal: python3 example_cloud_trigger.py
if __name__ == "__main__":
    async def main():
        result = await trigger_briefing_task("The stock market crashed, and aliens landed in Times Square.")
        print("\n--- Final Output ---")
        print(result["briefing"])

    asyncio.run(main())
